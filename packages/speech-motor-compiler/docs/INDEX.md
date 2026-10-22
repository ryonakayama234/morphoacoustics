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