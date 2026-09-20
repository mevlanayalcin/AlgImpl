# Fixed 50/50 radial-orthogonal sampling and covariance propagation

**Technical-note draft, 21 September 2026.** This repository document is not an AIcrowd write-up submission, a leaderboard ranking, or an award claim. The code-upload attempt and its platform receipt are tracked separately.

## Scope and provenance

The submitted entrypoint is assembled by `submission-work/arc/build_and_check.py`. Its expected SHA-256 is `2a6745a94ee403b0e49c2372a95dea7c9a7b4684aaafdc7b7953ff57471154a7`.

The implementation is AI-assisted under the account owner's authorization. No independent human code review is claimed. The covariance component comes from the AIcrowd starter kit at commit `5eb9aa1455fcb3216af55994bdf25dc242b95797`, `examples/03_covariance_propagation.py`; its MIT license notice is retained in the assembled source. We do not claim that component, antithetic sampling, Gaussian QR, radial integration, or convex averaging as novel inventions.

## Problem

For a bias-free ReLU network and a standard Gaussian input, estimate every layer's per-neuron mean. The implementation uses the contract's row-vector convention, `x @ weight`, followed by ReLU. It returns an array of shape `(depth, width)`.

## Sampling component

A standard Gaussian vector can be decomposed as `X = R U`, where `U` is uniform on the unit sphere, `R` is chi-distributed, and radius and direction are independent. A bias-free ReLU network is positively homogeneous: `f(r u) = r f(u)` for `r >= 0`. Therefore:

`E[f(X)] = E[R] E[f(U)]`.

The radial mean is a distributional constant, `sqrt(2) Gamma((n+1)/2) / Gamma(n/2)`, not a prediction for a particular evaluation network. Values for supported widths are stored in the source.

We draw Gaussian matrices through `flopscope.numpy`, obtain orthogonal directions with metered QR, and evaluate both signs of each direction. Antithetic evaluation removes sensitivity to QR sign conventions and cancels odd contributions within a pair. Directions in a block are dependent; this is not a claim of independence or a universal variance advantage for every deep network.

The number of pairs is `max(1, min(3*n, budget // (50*depth*n*n)))`. At each layer the code sums post-ReLU activations in float64 and returns float32 means. The first layer is replaced by its analytic Gaussian mean: each column norm of the first weight matrix divided by `sqrt(2*pi)`.

The RNG is seeded with the public `MLP.seed` interface used in the official starter examples. It is used for sampling reproducibility, not to reconstruct private datasets or look up target activations. The code does not inspect grader internals, files, hidden seeds or network-specific answer tables.

## Covariance component

The starter's analytical approximation propagates the full mean and covariance through linear layers. Under a Gaussian marginal approximation, it applies the Gaussian ReLU formulas to the mean and diagonal variance. Off-diagonal covariance uses the starter's gain approximation based on Gaussian CDF values. This approximation can introduce bias, especially as depth increases; it is not exact deep-network inference.

The supported flopscope symmetry validation and retagging are preserved. We do not modify operation prices, counters or bookkeeping and do not pack independent values into machine elements to obtain a cheaper bill.

## Fixed hybrid

The exported estimator computes both components and returns their arithmetic average:

`estimate = 0.5 * sampling_estimate + 0.5 * covariance_estimate`.

The mixture weight is fixed, not selected from private evaluation outputs. A simple bias/variance motivation is that an approximately unbiased sampling estimator can be blended with a low-variance but biased analytical approximation. This motivation does not prove that a 50/50 blend beats both components on every network. No general optimality claim is made.

## Accounting and limitations

Prediction array operations use the public flopscope APIs. Integer shape/budget bookkeeping and ordinary control flow are separate from array computation. The covariance code is mechanically adapted from the attributed upstream source, not rewritten as an unmetered numerical library.

The pair-count rule budgets the sampler conservatively at the tested competition configuration. It is not a proof of a valid total budget for every possible width, depth or user-supplied budget: the covariance component also consumes work. Unsupported widths raise explicitly. The platform grader remains authoritative about limits, residual wall time and fallback predictions.

The local build compares the assembled entrypoint bitwise with the earlier two-component composition on synthetic `(width, depth)` configurations `(4, 2)`, `(64, 3)` and `(1024, 16)`. It also checks matching FLOP counts, finite outputs and expected shapes. These are equivalence and contract checks, **not** an independent broad accuracy benchmark or a leaderboard result. The workflow separately runs the official validator and packager.

Further scientific work should test more independent public networks, alternative fixed mixture weights, and sampler/covariance ablations without tuning to private leaderboard cases. Any future numerical claims need the exact dataset version, code revision, budget and observed outputs.

## Delivery separation

- A repository note is not the required competition write-up upload.
- A valid package is not proof that AIcrowd accepted it.
- A platform submission ID is not a graded score.
- A score is not a final rank, prize, invoice or payment.

No customer, paid job, award or payment is asserted in this note.

## Primary references

- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/examples/03_covariance_propagation.py
- https://github.com/AIcrowd/whest-starterkit/blob/5eb9aa1455fcb3216af55994bdf25dc242b95797/docs/getting-started/stage-5-package.md
- https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026
