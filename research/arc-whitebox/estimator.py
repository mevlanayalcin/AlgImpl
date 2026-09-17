"""Experimental ARC estimator; no leaderboard score or originality claim.

For a bias-free ReLU network f, f(r*u)=r*f(u) for r>=0. A Gaussian
input decomposes into independent radius R and uniform direction U, hence
E[f(X)]=E[R]*E[f(U)]. Gaussian QR columns provide random orthogonal axes.
Evaluating both signs removes QR sign conventions and odd sampling noise.
All prediction arithmetic uses the public flopscope API. This is a
sampling-based baseline candidate, not a claim of a novel estimator.
AI-assisted implementation authorized by the account owner.
"""
from __future__ import annotations

import flopscope.numpy as fnp
from whestbench import BaseEstimator, MLP

# Offline constants E[chi_n], not network-specific predictions. Includes the
# official 4x2 contract probe and the 1024x16 Phase 2 shape.
_RADII = {
    1: 0.7978845608028651,
    2: 1.2533141373155,
    4: 1.8799712059732514,
    8: 2.741624675377657,
    16: 3.9380256218873253,
    32: 5.612839389220769,
    64: 7.96881222199864,
    128: 11.291633201545112,
    256: 15.984382666607859,
    512: 22.6163711584994,
    1024: 31.9921884548318,
}
_INV_SQRT_2PI = 0.3989422804014327


class Estimator(BaseEstimator):
    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        width, depth = mlp.width, mlp.depth
        if width not in _RADII:
            raise ValueError("Unsupported width: add its offline chi-mean constant")
        if depth < 1 or budget <= 0:
            raise ValueError("Positive depth and budget required")
        # Integer shape/budget bookkeeping only; no unmetered array arithmetic.
        pairs = max(1, min(3 * width, budget // (50 * depth * width * width)))
        rng = fnp.random.default_rng(mlp.seed)
        totals = fnp.zeros((depth, width), dtype=fnp.float64)
        radius = fnp.asarray(_RADII[width], dtype=fnp.float32)
        for start in range(0, pairs, width):
            block = min(width, pairs - start)
            gaussian = rng.standard_normal((width, block), dtype=fnp.float32)
            q, _ = fnp.linalg.qr(gaussian, mode="reduced")
            x = fnp.concatenate((q.T, -q.T), axis=0) * radius
            for layer, weight in enumerate(mlp.weights):
                x = fnp.maximum(x @ weight, fnp.zeros((), dtype=fnp.float32))
                totals[layer] += fnp.sum(x, axis=0, dtype=fnp.float64)
        result = (totals / (2 * pairs)).astype(fnp.float32)
        # Exact first-layer mean for a centered Gaussian linear form.
        first = mlp.weights[0]
        result[0] = fnp.sqrt(fnp.sum(first * first, axis=0)) * _INV_SQRT_2PI
        return result
