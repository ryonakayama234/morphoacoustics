# SMC-5 RESULTS — append-only research evidence ledger

2026-10-26 JST, before final exact-HEAD checks and independent audit.
**Current verdict: IN_PROGRESS / MORE_DATA / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE.**

- Creator approved limited technical execution and explicit STOP for public creative/API/physics semantics; requires GitHub `@codex review`.
- Frozen protocol `0cbd9171b53c16402644750018858cc8967b1377`, preregistered test-only `3d836e2b4bffc763da31790019dd50a9a18f0786` (imports absent module), test-only correction `01d1e7c8fb46a1e15ab67806748ca42f1146fccf`, first implementation `47f67ee10c983a346e8fb3fa02d5b9d21cbb06ec`.
- **CI outcomes currently UNVERIFIED**; GitHub Actions runs were queued when inspected. RED intent does not mean observed failure until exact-run logs show it. No assertion of passing tests. Codex review not yet requested at final source SHA.
- Deliberately not rerun historical red Gate B F01–F32 in this limited research slice. Mark as **NOT_RUN / MORE_DATA**. SMC4-BR's earlier BR11–BR12 bridge gap motivated this task, not evidence this task solves all prior falsifiers.
- User-supplied real utterances, natural gesture lexicon, body adapter, real sound, listener quality and human scientific replication: **NOT_RUN / NOT_ESTABLISHED**.

## Gate
Record exact commit SHA, workflow URL, Python matrix checks, mypy/root regression, test fixture identity, Codex review SHA and all P2s before considering `GO_LIMITED_SYMBOLIC`. Keep PR Draft, no main merge. Failure evidence remains searchable.

## Checkpoint — 2026-10-26 JST, later than initial source candidate
- Incremental preregistered negative-stage/strong-Kleene tests SHA `23638c99a953346c6e89e6d4ca0fa7737d29a935`; production correction SHA `2fb620e57a4a9ff96215188e42b2fed9df127d99`.
- Checked GitHub Actions for test-only, code-bearing and docs commits: workflow groups remained **queued**, not completed, at inspection. Consequently **no confirmed RED execution, GREEN execution, mypy, root or SV1 pass**. This is `MORE_DATA_CI`, not a successful outcome and not cause to weaken tests.
- GitHub Codex review was requested on prior code/docs HEAD `0305dd3f865591e0ff1bbd29248823f9897db336`; GitHub response showed **RUNNING**, not completed. Because subsequent corrections advance HEAD, request a fresh review at the new exact HEAD. No review success or waiver claimed.
- No code changes outside standalone package: Core physics/Studio untouched. No main merge. Independent phonetic/physical verification and F01–F32 **NOT_RUN**.

## Checkpoint — completed first full CI + first exact-HEAD Codex review (2026-10-26 JST)
- Exact original reviewed SHA `d88f8a88993904f116e62809518fde245d2b05d4`, Draft #211. Workflow `tests` [40310246219](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40310246219) and SV1 [40310246329](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40310246329) both **SUCCESS**. Isolated SMC matrix [40310246206](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40310246206) **FAILURE** due strict mypy on `symbolic_bridge.py:221-222`: nullable TaskDefinition branch lacked a nonreturning annotation. Synthetic package pytest reached green; this is NOT a green matrix verdict.
- Test-only original SHA `01d1e7c8fb46a1e15ab67806748ca42f1146fccf` completed isolated RED [40309026562](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40309026562): module intentionally not yet implemented. Additional stage-specific test-only SHA `23638c99a953346c6e89e6d4ca0fa7737d29a935` completed isolated RED [40310052956](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40310052956): `MAPPING` incorrectly returned for `TIMING` and `COORDINATION` cases, before separate repair `2fb620e...`. Both negative witnesses are retained.
- The exact `d88f8a8` [GitHub Codex review](https://github.com/ryonakayama234/morphoacoustics/pull/211) **COMPLETED, HAS_TWO_UNRESOLVED_P2**: [P2 mypy nonreturning refusal helper](https://github.com/ryonakayama234/morphoacoustics/pull/211#discussion_r4376398622); [P2 graph-origin stage is misclassified for blank segment ID and whitespace unit ID](https://github.com/ryonakayama234/morphoacoustics/pull/211#discussion_r4376398636).
- Codex regression tests were added **first** at test-only SHA `40a61d4b3289f6789105aec238ff6baebd919e79`. Source repair **later** at `d2d9b5333a1d3ecd2df36cbe0e9ab286d70b03f7`: declare `_fail(...)->NoReturn`; replace fragile diagnostic-code allowlist with explicit MAPPING/COORDINATION/GRAPH/TIMING phase tracking, including structural `INVALID_SEGMENT_ID` and `INVALID_OR_DUPLICATE_UNIT_ID` as GRAPH. Initial source failure and audit findings remain discoverable.
- **Latest correction SHA CI remains PENDING** as of this entry; no pass claim, no Codex re-review verdict for correction yet. Research gate **MORE_DATA_CI_AND_CODEX**, no public ABI, no main merge or Studio/Core physics change. A new final-HEAD Codex review and 3.11/3.12/3.13 package/myPy, root tests, SV1 workflow confirmation are still required.
