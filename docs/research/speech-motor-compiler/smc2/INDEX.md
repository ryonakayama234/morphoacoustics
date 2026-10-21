# SMC-2 — research index (2026-10-22 JST)

**Status: PREIMPLEMENTATION_GATE_A_REGISTERED / NOT_INDEPENDENTLY_RATIFIED / NOT_ADOPTED.**
Parent Issue [#11](https://github.com/ryonakayama234/morphoacoustics/issues/11), implementation [#146](https://github.com/ryonakayama234/morphoacoustics/issues/146). Baseline main `6869cfec04041393eae44485ce2fc91f002114f5`. Old SMC-1 closed-unmerged PR [#140](https://github.com/ryonakayama234/morphoacoustics/pull/140), code-bearing SHA `fa98c1ca1f2e73cb14933d023880e7b1fa1a1d31`. Do not merge it as a dependency.

## Research directory
- [SYSTEM.md](SYSTEM.md): causal boundaries, Core↔Studio creator journey and organ-graph seam
- [DATA.md](DATA.md): representation, IDs, Unicode source offsets, diagnostic rules, symbolic timing contract
- [EXPERIMENTS.md](EXPERIMENTS.md): frozen hypotheses, initial fixtures, negative gates and decision ledger
- `src/smc2_research/motor_plan.py`: future *standalone* research package, not public API
- `tests/test_smc2_motor_plan.py`: future isolated symbolic regressions
- `wolfram-oracle.wl`: exact rational comparison, no phonetic validation

## Search terms
SMC-2; SpeechMotorPlan; MotorIntentGraph; PronunciationUnit; A_LIKE_INTENT; I_LIKE_INTENT; CoordPlan; source_offset; partial resolution; fail-closed; NO_AUDIO; NOT_ADOPTED.

## Decision register
- 2026-10-22 Gate A preregistration **authored before code**; self-registered, independent science audit pending.
- Initial output is a proposed symbolic interface, not adopted physics-domain schema, phonetic controller, phonation, waveform, or Studio feature.
- Keep fixed CC-A2 / SV-1 / OG4 inventory intact; no physical package or Performance Contract edits.

## Implementation revision / still unadopted
- `src/smc2_research/motor_plan.py`: only explicit import, no public Core or Studio API.
- `tests/test_smc2_motor_plan.py`: synthetic timing test adapter only; no phonetic execution.
- `.github/workflows/smc2-research.yml`: check code and unchanged Core regressions at exact head.
