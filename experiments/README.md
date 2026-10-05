# Experiments

This directory is for executable research experiments rather than ad-hoc demos.

Current sequence:

1. `001_uniform_tube` — validate simple tube resonances against analytic expectations.
2. `002_vary_tract_length` — hold source fixed and vary tract length.
3. `003_constriction` — map a `CONSTRICT` gesture to a prepared 1D tract state.
4. `004_same_gesture_two_morphologies` — execute one unchanged gesture score on two explicitly prepared bodies and compare physical/acoustic outcomes.
5. `005_infeasible_gesture` — demonstrate that the same valid gesture can be feasible for one body and physically infeasible for another.
6. `006_gesture_timecourse` — compare binary and smooth temporal activation above the existing snapshot primitive before promoting any temporal API into the core package.
7. `007_gesture_sampling_convergence` — test convergence and expose the need for explicit event semantics at discontinuities.
8. `008_event_trajectory` — compare sampled-only timing with explicit events plus sampled continuous trajectories and record the adoption decision.
9. `009_fixed_tract_waveform` — excite fixed prepared tracts with an explicit source and generate the first raw/listening waveforms with independent resonance checks.
10. `010_dynamic_gesture_waveform` — propagate one validated Gesture timecourse through quasi-stationary physical/acoustic rendering and separate motion effects from morphology effects.
11. `011_gesture_coordination_overlap` — compare sequential and overlapping execution of two spatially distinct Gestures before promoting any general coordination or coarticulation API.
12. `012_source_renderer_artifacts` — attribute the blind-listening periodic snap and startup transient to source structure versus short-time renderer edges, then verify coordination effects after objective cleanup.
13. `013_parametric_source_prosody` — isolate LF-family pulse shape, macroprosody, and small microprosody/aspiration before considering a reduced self-oscillating vocal-fold model.
14. `014_structure_aligned_prosody` — anchor matched-range pitch and duration cues to movable semantic boundaries, validate their realization, and prepare blinded early/late boundary listening.
15. `015_embodiment_measurement_calibration` — calibrate the Embodiment measurement harness with an analytical tract-length sensitivity sweep, observer-grid floor, and section-partition control.
16. `016_same_task_morphology_covariance` — apply one unchanged non-empty CONSTRICT task across a preregistered 10% prepared-tract length intervention and test task residuals, body-specific physical scaling, acoustic scale covariance, and preservation of the dimensionless Gesture effect.
17. `017_embodied_infeasibility_boundary` — hold one valid non-empty CONSTRICT task and acoustic geometry fixed while only articulator reach crosses the task boundary; require explicit INFEASIBLE with no physical/acoustic fallback on the unreachable body.
18. `018_local_area_morphology_sensitivity` — sweep one non-self-similar prepared rest-area axis at -10/-5/0/+5/+10% while preserving the same task; measure resolved effects, monotonicity, dimensionless sensitivity, and nonlinear departure against an independent Wolfram oracle.
19. `019_material_conditioned_realization` — compare the production hard-projector null model against an experiment-local quasi-static minimum-energy realizer under one dimensionless stiffness intervention while preserving the exact same task target.
20. `020_stateful_finite_time_realization` — distinguish the Experiment-019 quasi-static equilibrium from an experiment-local critically damped stateful task model using duration, event continuity, post-release memory, and convergence-to-equilibrium gates.

Each experiment should state:

- hypothesis,
- intervention,
- controlled variables,
- expected qualitative/quantitative result,
- backend and parameter provenance,
- acceptance criterion.

An experiment that becomes a stable invariant should be promoted into `tests/scientific/`.
