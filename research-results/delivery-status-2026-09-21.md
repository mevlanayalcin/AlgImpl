# Delivery status — 21 September 2026 (Europe/Istanbul)

Account-owner-authorized, AI-assisted preparation. This record distinguishes account registration, authentication, packaging, submission, evaluation, prizes and payment.

## User-reported registrations

The account owner reports creating AIcrowd, Sanity and DEV accounts. This is not evidence that this execution environment has authenticated sessions for those accounts, that challenge participation has been completed, or that anything has been submitted. No passwords or API-key values were requested in chat or retrieved.

## New ARC work actually completed

- Repository: `mevlanayalcin/AlgImpl`.
- Separate branch: `work/arc-auth-gated-20260921`, created from `b77704fe6e88538b228f1dd698cdffd63072c340`.
- Tested workflow commit: `89043eeb4c10f329bb613621bc711fe676be01b3`.
- Actual GitHub Actions run: https://github.com/mevlanayalcin/AlgImpl/actions/runs/35540232423
- Actual completed job: https://github.com/mevlanayalcin/AlgImpl/actions/runs/35540232423/job/106156435660
- Job conclusion: success; upload step: **skipped**.

The job rebuilt the earlier full hybrid against pinned starter-kit commit `5eb9aa1455fcb3216af55994bdf25dc242b95797`, using flopscope 0.12.1, whestbench 0.16.1 and numpy 2.4.6. This is a pinned reproduction, not a claim to use every latest dependency. Hardware fallback probes were not disabled in the new workflow.

The actual logs verify bitwise equality on synthetic 4x2, 64x3 and 1024x16 networks. The 1024x16 case used 234652534365 FLOPs. These are packaging-equivalence checks, not new public-dataset scores or a full production-grader eligibility review.

The estimator SHA256 remains `2a6745a94ee403b0e49c2372a95dea7c9a7b4684aaafdc7b7953ff57471154a7`. The explicit checksum step passed. `whest validate` and `whest package` passed. The tarball lists only `estimator.py` and `manifest.json`.

The GitHub artifact is `arc-auth-gated-package`, ID `10614028613`, 12735 bytes for the complete ZIP according to the upload log, with ZIP SHA256 `6311295724d19eb7583ec4cf9f02c66642a83114c7d3e6bdcfabe9597aedb625`. This is the GitHub delivery ZIP, NOT the inner AIcrowd tarball checksum or an AIcrowd upload receipt. Retention is seven days. The artifact bytes have not been independently downloaded in this turn.

## Authentication and upload safeguards

`ARC_UPLOAD_ENABLED` is explicitly `false`. Merely creating an account, storing a secret or re-running this unchanged workflow will NOT submit an entry.

The workflow refers to the repository secret `AICROWD_API_KEY` only inside the gated upload step. Installation, assembly, validation and packaging do not receive that key. If a future separately enabled upload has no key, it fails before invoking the uploader. There is no `continue-on-error` on upload and no automatic upload retry. Timeout outcomes are treated as unknown, not automatically retried. Only allow-listed public AIcrowd submission receipt URLs are retained; raw authentication output is not published. A CLI receipt still requires verification on AIcrowd and does not establish successful grading, prize eligibility, an award or payment.

Five local mocked gateway cases passed: missing key, failed command, zero exit without receipt, public receipt and timeout. These used synthetic test data and no network uploads; they are not five real submissions or an independent human security review.

Before enabling one upload, the owner must confirm participation in the correct challenge under the real account, review/accept its terms personally where required, and save the AIcrowd API key directly into this repository's GitHub Actions Secrets interface. Do not send it in chat, public issues, files, logs or screenshots. Current submission availability and applicable rules still require verification before that real upload. Official guide: https://github.com/AIcrowd/whest-starterkit/blob/main/docs/getting-started/stage-5-package.md

## Other project status

Sanity/DEV publication was not attempted in this turn. The earlier Proof Before Pay / Kanit Defteri archive is still a local prototype: real Sanity project connection, production build, publication and contest entry are not established by the registrations. A local npm connectivity check failed with EAI_AGAIN, so no successful local Astro production build is claimed.

No default-branch changes, third-party PRs, comments, account-permission changes, paid-plan purchases or money transfers were performed. New accepted competition submissions: none. New verified awards or receipts of money: none.
