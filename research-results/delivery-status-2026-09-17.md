# Delivery status — 17 September 2026

This is an account-owner-authorized, AI-assisted activity record. It distinguishes code delivery, packaging, platform acceptance, and payment. No award or income is claimed.

## Matchpack

The focused patch and 11 regression tests were delivered to the upstream issue in this comment:
https://github.com/tscircuit/matchpack/issues/267#issuecomment-5720923876

This is an issue comment with reviewable files, NOT an upstream pull request or merge. The US$25 proposal remains unapproved. The production patch targets e0864473414ad1b9b0528afff5bda00c7ce67b86. The existing independent verification run is https://github.com/mevlanayalcin/AlgImpl/actions/runs/35263653930 .

## ARC: actual hybrid packaging

The earlier `research/arc-whitebox/estimator.py` implements the sampling component only; the measured 50/50 hybrid was nested in `verify.py`. Submission preparation therefore assembled both components into a self-contained Estimator, preserving the AIcrowd MIT notice. Sending the old sampler entrypoint would not submit the measured hybrid.

Build script: `submission-work/arc/build_and_check.py`.
Tested commit: 2fb068f62b56cd82a03b39f0dc20b5f2f634a17f.
Actual run: https://github.com/mevlanayalcin/AlgImpl/actions/runs/35272306809
Actual job: 105374397160.

Observed from the completed job logs:
- Bitwise equality to the previously tested composition passed for synthetic 4x2, 64x3, and 1024x16 networks.
- The full 1024x16 composition used 234652534365 FLOPs, equal to the earlier composition.
- `whest validate --estimator dist/estimator.py` passed class resolution, setup, output shape, and finite-value checks.
- `whest package --estimator dist/estimator.py --output dist/submission.tar.gz` succeeded.
- The resulting 3440-byte tarball contains only `estimator.py` and `manifest.json`.

## ARC: upload did NOT complete

The actual command `whest submit dist/submission.tar.gz` exited with code 2:

```
No AIcrowd API key found. Run `whest login` (or set AICROWD_API_KEY).
```

There is NO accepted submission ID, official leaderboard entry, registration confirmation, or prize. The workflow is green because the failed upload step was marked `continue-on-error` so the useful package could be retained. The raw log and `submission-attempt.json` preserve the failure. A successful workflow does NOT establish accepted submission.

The account owner must authenticate through AIcrowd's supported mechanism to submit. Never put credentials in a public issue, source file, or delivery archive.

## Artifact identity

GitHub artifact 10518737099 (`arc-submission-ready`) was downloaded and checked:
- ZIP SHA256: 714ab6e48f2409c0696f4e610091e116d911a0978729970840276a6537f2a861
- submission.tar.gz SHA256: 8a55827cc312da56c6ad205c7d7bd06fda281a4bd5029b341c204d17de90446f
- estimator.py SHA256: 2a6745a94ee403b0e49c2372a95dea7c9a7b4684aaafdc7b7953ff57471154a7

Only separate work branches were used; no default-branch update, paid service purchase, or payment transfer was performed in this turn. These packaging checks are not a larger accuracy study or full production-grader eligibility review.
