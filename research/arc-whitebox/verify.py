"""External verification harness, never included in the estimator submission.
Reads only public data. Reference targets are never passed to predict().
"""
from __future__ import annotations
import gc
import hashlib
import importlib.util
import importlib.metadata
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, MLP
from estimator import Estimator

BUDGET = 2**41


def load_example(path):
    spec = importlib.util.spec_from_file_location("official_covariance", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.Estimator


class PlainMC(BaseEstimator):
    def predict(self, mlp, budget):
        pairs = max(1, min(3*mlp.width, budget//(50*mlp.depth*mlp.width*mlp.width)))
        rng=fnp.random.default_rng(mlp.seed)
        x=rng.standard_normal((2*pairs,mlp.width),dtype=fnp.float32)
        rows=[]
        for w in mlp.weights:
            x=fnp.maximum(x@w,fnp.zeros((),dtype=fnp.float32))
            rows.append(fnp.mean(x,axis=0,dtype=fnp.float64))
        return fnp.stack(rows).astype(fnp.float32)


def measured(estimator, mlp):
    start=time.perf_counter()
    with flops.BudgetContext(flop_budget=BUDGET,wall_time_limit_s=120.0,quiet=True) as ctx:
        pred=estimator.predict(mlp,BUDGET)
    arr=np.asarray(pred,dtype=np.float32)
    if arr.shape!=(mlp.depth,mlp.width) or not np.isfinite(arr).all():
        raise AssertionError("Invalid prediction")
    result={"flops":ctx.flops_used,"budget_fraction":ctx.flops_used/BUDGET,
            "residual_s":ctx.residual_wall_time_s,"elapsed_s":time.perf_counter()-start}
    result["limits_pass"]=(result["budget_fraction"]<=1 and result["residual_s"]<=0.4)
    return arr,result


def contract_tests():
    rng=np.random.default_rng(42)
    for width,depth in [(1,1),(4,2),(16,3),(64,1)]:
        weights=[fnp.asarray(rng.normal(0,math.sqrt(2/width),(width,width)).astype(np.float32)) for _ in range(depth)]
        mlp=MLP(width=width,depth=depth,weights=weights,seed=2468)
        pred,info=measured(Estimator(),mlp)
        repeat,_=measured(Estimator(),mlp)
        np.testing.assert_array_equal(pred,repeat)
        exact=np.linalg.norm(np.asarray(weights[0]),axis=0)/math.sqrt(2*math.pi)
        np.testing.assert_allclose(pred[0],exact,rtol=2e-6,atol=2e-6)
        print("CONTRACT",json.dumps({"width":width,"depth":depth,**info}),flush=True)
    zeros=[fnp.zeros((4,4),dtype=fnp.float32) for _ in range(2)]
    pred,_=measured(Estimator(),MLP(width=4,depth=2,weights=zeros,seed=10))
    np.testing.assert_array_equal(pred,np.zeros((2,4)))
    print("CONTRACT_ALL_PASSED",flush=True)


def public_probe():
    from datasets import load_dataset
    from huggingface_hub import HfApi
    info=HfApi().dataset_info("aicrowd/arc-whestbench-public-2026",revision="v2-phase2")
    revision=info.sha
    print("PUBLIC_DATASET_REVISION",revision,flush=True)
    ds=load_dataset("aicrowd/arc-whestbench-public-2026",revision=revision,split="mini",streaming=True).with_format("numpy")
    covariance=load_example(sys.argv[2])
    rows=[]
    for idx,row in enumerate(ds.take(3)):
        print("PUBLIC_ROW_KEYS",sorted(row.keys()),flush=True)
        weights=np.asarray(row["weights"],dtype=np.float32)
        target=np.asarray(row["all_layer_means"],dtype=np.float32)
        assert weights.shape==(16,1024,1024),weights.shape
        assert target.shape==(16,1024),target.shape
        weight_hash=hashlib.sha256(weights.tobytes()).hexdigest()
        # Local reproducible test seed, NOT the official private rerun protocol.
        mlp=MLP(width=1024,depth=16,weights=[fnp.asarray(w) for w in weights],seed=17092026+idx)
        item={"index":idx,"name":str(row["mlp_name"]),"weights_sha256":weight_hash,"results":{}}
        for name,cls in [("orthogonal_sphere",Estimator),("plain_mc",PlainMC),("official_covariance",covariance)]:
            pred,stats=measured(cls(),mlp)
            stats["final_layer_mse"]=float(np.mean((pred[-1].astype(np.float64)-target[-1])**2))
            stats["all_layer_mse"]=float(np.mean((pred.astype(np.float64)-target)**2))
            stats["local_adjusted_score"]=stats["final_layer_mse"]*max(0.1,stats["budget_fraction"]) if stats["limits_pass"] else float(np.mean(target[-1].astype(np.float64)**2))
            item["results"][name]=stats
            print("MEASURED",json.dumps({"index":idx,"method":name,**stats}),flush=True)
        rows.append(item)
        record={"dataset_revision":revision,"split":"mini","evaluated_count":len(rows),"official_submission":False,"rows":rows}
        Path("public-probe-results.json").write_text(json.dumps(record,indent=2))
        print("ROW_RESULT",json.dumps(item),flush=True)
        del weights,target,mlp,row
        gc.collect()
    assert len(rows)==3
    print("PUBLIC_PROBE_COMPLETE",json.dumps(record),flush=True)


if __name__=="__main__":
    print("VERSIONS",json.dumps({p:importlib.metadata.version(p) for p in ["flopscope","whestbench","numpy","datasets"]}),flush=True)
    if sys.argv[1]=="contract": contract_tests()
    elif sys.argv[1]=="public": public_probe()
    else: raise SystemExit("Expected contract or public")
