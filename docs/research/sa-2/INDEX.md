# SA-2A — coherent circular-aperture radiation research (Gate A)
State: PREREGISTERED / NOT_RUN / NOT_ADOPTED at this design commit.
Tracker: https://github.com/ryonakayama234/morphoacoustics/issues/171
Frozen baseline Core main: 6869cfec04041393eae44485ce2fc91f002114f5.
SA-1 verified experiment source SHA: 5a048551b94b7b3e77c33b37c47d2de814b4c3e6 (not merged main).
SA-1 evidence: https://github.com/ryonakayama234/morphoacoustics/actions/runs/39973210182

Goal: derive mouth load Z_rad and exterior pressure from ONE specified baffled circular piston, test independently against physical reference and SAME-PORT radiated power, then assess a genuine fixed CC-A2 M0 acoustic two-port without generating/adopting a misleading natural-voice WAV.

- SYSTEM.md physical reference and its declared approximation limits.
- DATA.md immutable inputs, units, reference checks and provenance.
- EXPERIMENT.md hypotheses, pre-frozen thresholds, decisions and scoped execution.

Gate B SA-2A: analytic frequency-domain reference and independently checked physics. Gate C SA-2B (SEPARATE future prereg): stable causal positive-real time-domain termination, exact historic JET inputs, 2 authentic bodies if possible, sound traces and VF-1 compatibility. DO NOT infer Gate C from frequency-only success.

No main merge, public API changes, Studio Takes, SMC/ASMR, biologically naturalness or full vocal-fold FSI.

## Post-run status (retrospective, 2026-10-24)
- Gate-A pre-registration: [38f27596](https://github.com/ryonakayama234/morphoacoustics/commit/38f27596b91c47f7307d34af225f8293afb6268a).
- Gate-B analytic radiation oracle and genuine M0 frequency-domain probe: PASS on exact executed [6eca7a25](https://github.com/ryonakayama234/morphoacoustics/commit/6eca7a250e30de8d758087dad83d5f02a1301f38), [Actions #40062355337](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40062355337), [raw data #12548026973](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40062355337/artifacts/12548026973).
- Audit: [RESULTS_20261024.md](RESULTS_20261024.md) including exact numeric results, SHA checks and initially failed run.
- Biological/causal time-domain physics: NOT VERIFIED. SA-2B remains separate; current interface status MODEL_BOUNDARY_HOLD, no VF-1 readiness or main adoption.
