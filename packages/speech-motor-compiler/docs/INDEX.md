# SMC-3 Research Index / decision provenance

**State:** GATE_B_EXPLORATORY_SOFTWARE_PASS / INDEPENDENT_REVIEW_PENDING / RESEARCH_ONLY / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE.

## Navigation
- [SYSTEM.md](SYSTEM.md): architecture, hypotheses, falsifiers and prohibited scope.
- [DATA.md](DATA.md): independent MotorTaskNode, associations and event coupling candidate schema.
- [EXPERIMENTS.md](EXPERIMENTS.md): prospective fixtures, mathematical oracles, software/physical boundaries.
- [README.md](../README.md): import boundary and future Studio route.

## Prior records / historical research
- [SMC-1 #139](https://github.com/ryonakayama234/morphoacoustics/issues/139): exploratory, closed/unmerged.
- [SMC-2 #146](https://github.com/ryonakayama234/morphoacoustics/issues/146): experimental symbolic planning.
- [Draft PR #147](https://github.com/ryonakayama234/morphoacoustics/pull/147): HEAD d12bddbbce2c5571f384217feec98bad3e487771, NOT merged.
- [SMC Gate C #148](https://github.com/ryonakayama234/morphoacoustics/issues/148): preliminary F1–F4 plus Wolfram expressivity witness; third-party review pending.
- [SMC-3 package issue #162](https://github.com/ryonakayama234/morphoacoustics/issues/162): current work, synthetic independent package.
- [Experiment011](https://github.com/ryonakayama234/morphoacoustics/tree/main/experiments/011_gesture_coordination_overlap): bounded physical overlap phenomenon. Its acoustic waveform change does not validate SMC phonetic planning.

## Decision log
- 2026-10-22 Gate A: use a standalone package within Core repository, not a separate repository yet; keep explicit boundary, no root Python package import.
- 2026-10-22 Gate A: select mathematical many-to-many and rational coupling tests before implementing. These are synthetic expressiveness checks, not phonetic data.
- 2026-10-22 Gate A: keep SMC-1/2 original branches unchanged and PR #147 Draft. No third-party reviewer or adoption is claimed.

- 2026-10-22 Gate B code commit: `6b31e77365cf965931cb895286727bf75eaa9b57` after prior Gate A doc commit `4f7bef4a9709c96efaa80d8070a2d8b352d9b1d8`.
- Note: this is self-proposed design and self-authored test suite; no independent acceptance. All claims remain symbolic and synthetic. Cross-body physics, Studio, pronunciation and acoustics excluded.

- 2026-10-22 CI attempt `233bdbac...` exposed strict mypy failure despite 21 pytest passes; source now corrected in a separate follow-up commit, new CI pending. [Failing CI run](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777021246).

## 2026-10-22 verified software Gate B receipt (not research adoption)
Exact source HEAD **`9c9ac9539ae1798ed27ef5cd751562e4b2c9b469`**: GitHub API reported **16/16 completed check runs SUCCESS** (some duplicate push/PR runs), including isolated Python 3.11/3.12/3.13 package import/install + 21 synthetic pytest cases per run + strict package mypy, existing Core root test matrix/typecheck, and bounded SV1 regression. Evidence: [isolated package run](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258873), [root tests](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258910), [SV1](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258867). An earlier failing mypy run is preserved in EXPERIMENTS. Individual OG3 and OG4 were not separately confirmed for this SHA. No independent reviewer, phonetic fixture, body adapter, wav or Studio integration. Disposition: **EXPLORATORY_SOFTWARE_PASS / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**.

## 2026-10-23 Gate C audit tracking
- [Frozen Gate C protocol](GATE_C_PROTOCOL.md): preregistered falsifiers, fixed SHA, deterministic generator seeds, acceptance vs independent-review requirements. Protocol commit `7705ebd752e191a545506c0a2a79d56a40efc6bf` **precedes** all Gate C test code.
- [Adversarial Python tests](../tests/test_gate_c_adversarial.py): 100 synthetic cases, metamorphic invariants, contradiction and malformed-input probes.
- [Wolfram mathematical oracle](../wolfram/gate_c_oracle.wl): independent exact rational witness; no CI execution inferred.
- Audit branch: [research/smc3-gate-c-audit-20261023](https://github.com/ryonakayama234/morphoacoustics/tree/research/smc3-gate-c-audit-20261023), forked from PR #164 HEAD `7d5c405fee1b2469b11bbe6d68b9e0d18e4dab05`.
- Review/state **GATE_C_AUDIT_IN_PROGRESS / ORIGINAL_CANDIDATE_UNCHANGED / INDEPENDENT_HUMAN_REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**. Gate B records above are historical, not Gate C verdicts.

## 2026-10-23 Gate C first failure and targeted revision

- [First failing exact-SHA CI receipt](https://github.com/ryonakayama234/morphoacoustics/pull/169#issuecomment-6367686236): `2a3a038c342150b37323a6c4b24cc846954d1c42`. One runtime malformed source crashes on `len(None)` instead of reporting `INVALID`. Category **BUG**; no timing solver conflict shown.
- [Targeted validator correction](https://github.com/ryonakayama234/morphoacoustics/commit/2de422883e544c1dff5ec12121a1f033a2f3afc5) **subsequent** to the recorded red run; frozen protocol and 100 synthetic test cases unchanged.
- Current stage **REVISE_IN_PROGRESS / POST_FIX_CI_PENDING / HUMAN_REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**. The earlier historical Gate B status must not substitute for this Gate C result.

## 2026-10-23 Gate C — verified exact-source-SHA repair CI

- **Fixed-source commit `2de422883e544c1dff5ec12121a1f033a2f3afc5`** is **16/16 completed SUCCESS**, zero failure/pending in GitHub check-runs API (two push/PR job sets): isolated package Python 3.11, 3.12, 3.13 pytest with 127 synthetic tests per interpreter, package strict mypy, existing root test matrix/typecheck, and bounded SV1. [Python 3.12 job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39973099897/job/120480625178). This is independent of the earlier red SHA `2a3a038c342150b37323a6c4b24cc846954d1c42`.
- Initial red failure **PRESERVED**, caused by `source_text=None` and unguarded `len(None)`; minimal source guard fixed the runtime fail-closed behavior with unchanged frozen test fixtures.
- All verified outcomes above refer to the **code-bearing SHA `2de422883e544c1dff5ec12121a1f033a2f3afc5`**, not automatically to later documentation-only commits. Document-only final branch HEAD checks require their own confirmation. OG3 and OG4 were not run as separate exact-SHA science gates by these package-scoped actions; do not claim them.
- Disposition: **GATE_C_IMPLEMENTER_ORIGIN_SOFTWARE_PASS / HUMAN_INDEPENDENT_REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**. This is not a physical or phonetic validation.
