# SA-1 — Source x Acoustic Port Audit

STATUS: GATE_A_DESIGN_ONLY / NOT_RUN / NOT_ADOPTED
Tracker: https://github.com/ryonakayama234/morphoacoustics/issues/168
Frozen Core main: 6869cfec04041393eae44485ce2fc91f002114f5
Frozen prior JET-P0 experiment source: 9a79fa616e280de24daab5bfbe3cce57fda92256
Prior failed physical run: https://github.com/ryonakayama234/morphoacoustics/actions/runs/39951204385

## Single question
Which factor turns a small flow-noise addition into dominant >2kHz observer pressure: the source spectrum, 1D tube transfer, simplified termination, intended monopole radiation weighting, or rendering/windowing errors?

This is a diagnostic enabling VF-1 source–tract interface, not a new natural voice, solver adoption, or an EQ correction.

- SYSTEM.md: actual current acoustic model, physical port graph, oracle definitions
- DATA.md: source/port/output quantities, units, provenance, known uncertainty
- EXPERIMENT.md: predeclared controls, numerical tests, decisions
- Follow-on: physical voice-regime map is future work, not an SA-1 deliverable

Science gate outcomes: DIAGNOSIS_VERIFIED_INTERFACE_READY, DIAGNOSIS_VERIFIED_REPAIR_REQUIRED, or UNRESOLVED_ORACLE_FAIL. Keep previous JET-P0 rejection unchanged. SMC and ASMR remain independent. No changes to Studio or public Core APIs.

## After execution (retrospective, NOT an edit to preregistration)

- **Gate B NUMERIC TESTS PASSED**, exact-branch-head source commit `5a048551b94b7b3e77c33b37c47d2de814b4c3e6`, [push CI run #39973210182](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39973210182).
- The detailed post-run measured diagnosis and 24 hashed raw artifacts are preserved in [RESULTS_20261023.md](RESULTS_20261023.md).
- Decision **DIAGNOSIS_VERIFIED_REPAIR_REQUIRED**: source/tube/monopole frequency weighting is mathematically explained; unified biologically valid lip radiation boundary is not yet available for VF-1. Next bounded study: [SA-2 #171](https://github.com/ryonakayama234/morphoacoustics/issues/171).
- Previous JET-P0 high-band failure and lack of audition remain. No main merge, no public source adoption, no Studio/SMC/ASMR change.
