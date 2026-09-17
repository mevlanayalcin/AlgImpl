"""Build an actual hybrid entrypoint, preserving the upstream MIT notice.
Development/verification tool only. This file is NOT bundled in the submission.
No account credentials, private datasets, or competition internal state are used.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
import flopscope as flops
import flopscope.numpy as fnp
from whestbench import MLP

BUDGET = 2**41


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def component(path: Path, class_name: str) -> str:
    tree = ast.parse(path.read_text())
    kept = []
    renamed = 0
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == '__future__':
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, ast.If) and '__name__' in ast.unparse(node.test):
            continue
        if isinstance(node, ast.ClassDef) and node.name == 'Estimator':
            node.name = class_name
            renamed += 1
        kept.append(node)
    assert renamed == 1, (path, renamed)
    tree.body = kept
    return ast.unparse(ast.fix_missing_locations(tree))


def main():
    root = Path(sys.argv[1]).resolve()
    starter = Path(sys.argv[2]).resolve()
    out = Path(sys.argv[3]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    sampler = root / 'research/arc-whitebox/estimator.py'
    covariance = starter / 'examples/03_covariance_propagation.py'
    license_text = (starter / 'LICENSE').read_text()
    header = '\n'.join('# ' + line for line in license_text.splitlines())
    source = (
        '"""Fixed 50/50 covariance and orthogonal-sphere estimator.\n'
        'AI-assisted contribution authorized by the account owner.\n'
        'The covariance component is adapted mechanically from the AIcrowd\n'
        'starter kit at 5eb9aa1455fcb3216af55994bdf25dc242b95797, not original work.\n'
        'Known statistical ingredients; no novelty or prize claim.\n'
        'No dataset targets or network-specific prediction tables are embedded.\n'
        '"""\nfrom __future__ import annotations\n\n' + header + '\n\n'
        + component(sampler, 'SphereEstimator') + '\n\n'
        + component(covariance, 'CovarianceEstimator') + '\n\n'
        + 'class Estimator(BaseEstimator):\n'
        + '    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:\n'
        + '        sampled = SphereEstimator().predict(mlp, budget)\n'
        + '        analytical = CovarianceEstimator().predict(mlp, budget)\n'
        + '        return (sampled + analytical) * 0.5\n'
    )
    target = out / 'estimator.py'
    target.write_text(source)
    tree = ast.parse(source)
    # Only the documented estimator API, metered computation and future import.
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(a.name.startswith('flopscope') for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module in ('__future__', 'whestbench', 'whestbench.domain')
    merged = load(target, 'assembled_arc_estimator').Estimator
    sphere = load(sampler, 'prior_sphere_component').Estimator
    cov = load(covariance, 'organizer_covariance_component').Estimator
    rng = np.random.default_rng(20260917)
    records = []
    for width, depth in ((4, 2), (64, 3), (1024, 16)):
        weights = [fnp.asarray(rng.normal(0, math.sqrt(2 / width), (width, width)).astype(np.float32)) for _ in range(depth)]
        mlp = MLP(width=width, depth=depth, weights=weights, seed=90210)
        with flops.BudgetContext(flop_budget=BUDGET, wall_time_limit_s=120, quiet=True) as a:
            actual = merged().predict(mlp, BUDGET)
        with flops.BudgetContext(flop_budget=BUDGET, wall_time_limit_s=120, quiet=True) as b:
            reference = (sphere().predict(mlp, BUDGET) + cov().predict(mlp, BUDGET)) * 0.5
        actual_np = np.asarray(actual)
        np.testing.assert_array_equal(actual_np, np.asarray(reference))
        assert actual_np.shape == (depth, width) and np.isfinite(actual_np).all()
        assert a.flops_used == b.flops_used, (a.flops_used, b.flops_used)
        assert a.residual_wall_time_s <= 0.4
        record = {'width': width, 'depth': depth, 'bitwise_equal_to_tested_composition': True,
                  'flops': a.flops_used, 'residual_s': a.residual_wall_time_s}
        records.append(record)
        print('ASSEMBLY_CHECK', json.dumps(record), flush=True)
    report = {
        'official_submission': False,
        'checks': records,
        'entrypoint_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'sampler_sha256': hashlib.sha256(sampler.read_bytes()).hexdigest(),
        'covariance_sha256': hashlib.sha256(covariance.read_bytes()).hexdigest(),
        'scope': 'Packaging equivalence on three synthetic networks, not a new leaderboard evaluation.'
    }
    (out / 'assembly-verification.json').write_text(json.dumps(report, indent=2))
    print('ASSEMBLY_ALL_PASSED', json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
