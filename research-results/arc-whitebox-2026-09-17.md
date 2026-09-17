# ARC White-Box Estimation: bounded experiment, 17 September 2026

## Status

This is an AI-assisted exploratory implementation and independent benchmark, authorized by the account owner. It is NOT an AIcrowd submission, leaderboard score, original-algorithm claim, prize decision, paid contract or payment. No paid compute service was purchased.

The code is isolated on `work/arc-whitebox-probe`. The public standard GitHub Actions runner has no repository write permissions or supplied secrets. No cache, deployment or uploaded Actions artifact is used.

## Reproducible evidence

- Initial sampler run: https://github.com/mevlanayalcin/AlgImpl/actions/runs/35269513994
- Fixed-hybrid validation run: https://github.com/mevlanayalcin/AlgImpl/actions/runs/35269955460
- Hybrid job: `105366481188`, completed successfully.
- Tested code commit: `cbca706de35763b21647771d02fc65a9ee0f6372`
- Organizer starter-kit commit: `AIcrowd/whest-starterkit@5eb9aa1455fcb3216af55994bdf25dc242b95797`
- Public dataset: `aicrowd/arc-whestbench-public-2026`, revision `aa99830fdc09fad15407b10e8e3459d3e18bba0a`, `mini` split.
- Runtime: Python 3.12.3, flopscope 0.12.1, whestbench 0.16.1, NumPy 2.4.6, datasets 5.0.1.

The numeric results below are copied from the actual job logs, not simulated output. Development initially hit an unsupported in-place array operation; this was corrected with out-of-place metered accumulation before the successful runs. The test thresholds were not weakened.

## Method and attribution

For a bias-free ReLU network, positive homogeneity gives `f(r*u)=r*f(u)` for `r>=0`. A standard Gaussian decomposes into independent radius `R` and uniform sphere direction `U`, giving `E[f(X)]=E[R]*E[f(U)]`.

The sampling component uses Gaussian QR columns as random orthogonal axes, evaluates both signs, and uses the known mean chi radius. The first-layer output mean is replaced with the exact Gaussian formula. All prediction arithmetic uses flopscope; ordinary Python is orchestration only.

The final experiment combines this sampler and the **unmodified organizer covariance-propagation example** with a fixed 50/50 average. The covariance method is not my original work. Orthogonal/antithetic sampling and averaging are established ingredients; no novelty claim is made.

Both complete component evaluations and the final averaging occur within one FLOP budget context. Reference means are loaded by the external test harness and are never supplied to `predict()`.

## Why the first candidate was not enough

On public rows 0, 1 and 2, the sampler averaged final-layer MSE `8.378276525858703e-6`, versus `1.4593501932125197e-5` for plain Monte Carlo and `5.1492440799462655e-6` for the organizer covariance baseline. It improved on plain sampling but lost to the stronger reference.

Only after that comparison was the fixed 50/50 hybrid selected. Its test used the next three public rows (indices 3, 4 and 5), which had not been evaluated in the preceding experiment. No mixture-weight sweep was run against these new rows.

## New-row results

Width 1024, depth 16, local estimator seed `17092026 + row_index`. The public row names below are dataset identifiers, not human subjects.

Final-layer mean squared error; smaller is better:

| Public row | Plain Monte Carlo | Organizer covariance | Fixed hybrid |
|---|---:|---:|---:|
| 3: steven-rice | 1.4138911177991132e-5 | 3.6949172581431233e-6 | 2.603427002220036e-6 |
| 4: sarah-kelley | 1.2534396217874163e-5 | 3.3377125035283143e-6 | 2.4924625117970753e-6 |
| 5: christopher-morales | 1.2562105310368843e-5 | 5.201657665656768e-6 | 2.2988147552380935e-6 |
| Mean | 1.3078470902078046e-5 | 4.078095809109402e-6 | 2.4649014230850684e-6 |

The hybrid's mean final-layer MSE was 39.56% lower than the covariance baseline and 81.15% lower than plain MC **on these three rows only**.

### Compute-adjusted comparison and tradeoffs

Using the local expression `final_layer_mse * max(0.1, flops / 2**41)`:

- Covariance mean local score: `4.078095809109402e-7`
- Hybrid mean local score: `2.6302376040203235e-7`
- Reduction: **35.50%** on these three rows.

This is NOT an official leaderboard score. It uses our local seeds and in-process budget context rather than the full competition grading/submission protocol.

The hybrid used `234652534365` FLOPs per network (10.6708% of the 2**41 cap), versus `51709240799` for covariance (2.3515%). It therefore used **4.54 times as many FLOPs** as covariance. The improvement does not mean the method is cheaper. Elapsed prediction times in this runner were approximately 3.0 seconds for the hybrid and 1.55 seconds for covariance; hardware timing is not portable.

The hybrid's measured residual time was at most 0.0238 seconds, below the local 0.4-second check. All nine new-row method runs returned finite arrays with the expected shape and stayed within the local limits.

Importantly, average MSE over **all layers** got worse relative to covariance: `3.423033866375611e-6` versus `2.2664794694674925e-6`. The improvement is in the final-layer metric, not every accuracy measure.

## Other completed checks

The sampling estimator passed shape, deterministic-seed and exact-first-layer checks on synthetic networks of shapes 1x1, 4x2, 16x3 and 64x1, plus a zero-weight 4x2 test. The composite also passed deterministic repetition and the first-layer identity on a fresh 4x2 case.

The separate NumPy development experiment on six 256x16 networks (seeds 200-205, 1536 estimator samples and 262144 independent reference samples each) showed a 52.32% mean MSE reduction for orthogonal spherical sampling versus plain MC. This smaller experiment used finite Monte Carlo references and multiple explored variants; it is not an official evaluation or a generalization guarantee.

## Limits and the next decision gate

Only three new large networks and one local estimator seed per network were used. A wider, multi-seed evaluation, official packaging/admission checks, account/rules acceptance, and a successfully graded submission remain undone. The tested package versions do not by themselves establish identity with every production grader version.

No AIcrowd account was connected, no competition entry was sent, and no income was obtained. A better score than one supplied baseline is not evidence of an award-winning ranking.

The current practical next gate is a wider independent evaluation before treating this as a submission candidate. The separate matchpack #267 US$25 proposal remains unapproved; this experiment does not change that funding status.
