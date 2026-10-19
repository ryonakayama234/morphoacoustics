# OG-3 Gate B reconciliation work order — 2026-10-15

Scope: [PR #104](https://github.com/ryonakayama234/morphoacoustics/pull/104), following [Gate A #102](https://github.com/ryonakayama234/morphoacoustics/pull/102). Recorded before the next implementation trial. No public release or Gate B merge authorized by this work order.

| Blocker in initial candidate ce6af25a | Required correction and acceptance |
| --- | --- |
| Arbitrary positive geometry/medium with global 4 kHz window | Implement exact two-fixture domain in RFC §11, backend v2; test each parameter and nextafter mismatches, large area, shared medium, path reversal, both accepted fixtures, order/ID independence, snapshot restore and forged-prepared refusal before evaluation. |
| 4097 finite in-band points classified INVALID | UNSUPPORTED/resource-limit, no observation; malformed/type/value errors first, then resource cap, then frequency cap. Test 1/3/7/4096 success, 4097 refusal, order/repeats and mixed error cases. |
| NumPy coercion may hide bool in mixed numeric containers | Inspect original numeric scalar types before coercion; mixed bool/int, string and complex values INVALID. Test native containers, NumPy arrays and nonfinite values. Do not silently convert bool into Hz. |
| Flux test uses 1e-10 instead of explicit supplementary 1e-12 | Every positive frozen frequency: correct defect <=1e-12; wrong-junction defect >1e-3 and abs(defect-0.5)<=1e-12. Read committed analytic result as reference data; retain separate reverse-order matrix negative control. |
| Signed-zero test lacks exact frequency byte assertion | Reconstruct actual complete observation hash payload and verify positive-zero hex `0000000000000000` for ±0; preserve response/digest equivalence and frequency order sensitivity. |
| Stacked branch conflicts and stale in-package descriptions | Merge accepted design/main without discarding either history; keep original src/morphoacoustics and X2a manifest byte-identical. Reconcile living architecture/data/ledger and PR description to sibling paths. Retarget #104 onto main after design merge. |
| Old green trial predates these requirements | Fresh exact-head Python 3.11/3.12/3.13 pytest, mypy covering sibling, original Experiment028/029 decisions, X2a unknown/tampered-file tests and two real 0.5s WAV/pressure/trace Takes under NumPy 2.4.6. Evidence runner twice, fresh outputs, source/oracle/result hashes and wrong/stale HEAD refusals. |

Physics remains fixed rigid lossless ideal 1D. Supplementary analytic flux thresholds were made explicit after the first trial, for future acceptance, not relabeled preregistration. The two frozen numerical configurations are controlled regressions. No new prospective physiological evidence, generic graph solver, voice or Studio capability follows.

Completion requires actual run links and exact SHA-scoped status in the ledger. Keep `PROVISIONAL_NUMERICAL_PASS_REVIEW_PENDING_NOT_ADOPTED` if machine gates pass. Independent review/release adoption remains a separate decision; correlated AI inspection must not be labeled independent human sign-off.
