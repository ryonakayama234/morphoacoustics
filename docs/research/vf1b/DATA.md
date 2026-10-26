# VF-1B DATA — candidate observations/ownership (design only)
**No adopted JSON schema, public ABI or new API.** The fields below are measurement/experimental names, not production objects. Parent [Issue #212](https://github.com/ryonakayama234/morphoacoustics/issues/212).

## Exact reproducibility envelope
```text
ResearchRun
  source: {vf1a_head_sha, stacked_base_sha, evidence_run_id}
  fixture: {tissue_params_digest, tract_preparation_digest, outlet_law_id}
  forcing: {p_sub_t[Pa], t0[s], perturbation, random_seed_if_any}
  solver: {dt[s], duration[s], tolerances, physical_clock, solver_id}
  signals [synchronous t]:
    tissue: x1,x2 [m], v1,v2 [m/s], F_aero1,F_aero2 [N]
    flow: q [m^3/s], A_glottis [m^2], p_sub,p_sup [Pa]
    acoustic: named p [Pa] / U [m^3/s] with port orientation
    ledger: mechanical_stored_E [J], tissue_aero_power [W],
      damping_power [W], other_declared_work [W], closure_error [J]
  analysis:
    equilibrium_estimation_method + validity
    modal_basis_ref + reference_residual
    windows [s], valid_cycle_intervals [s], phase_lag [rad]
    per_cycle_aero_work [J], per_cycle_damping [J],
    modal_energy_change [J], amplitude_envelope [m]
    uncertainty, failure_reason, status
  receipt: {input_hash, trace_hash, test_exit_status,
            independent_reference_id, run_uri, reviewer_status}
```

## Core and Studio ownership
- Core research owns transient states, SI forces/ports, numerical observables and scientific receipts; `src/morphoacoustics_graph/` existing OG3 public fixed2 boundaries stay unchanged.
- `CharacterDefinition.organGraphRef` stays Studio's creative reference to **future** anatomy; no computed p/U/x is persistent anatomy.
- `PerformanceDraft.motionScoreRef` is future task-level intent; no SMC import or user-controllable VF-1B UI.
- `TakeRecord` may only reference a physical artifact **after** separate receiver and creator gates. No new Take here.
- `WorkspaceUiState` stores selection/viewport only; physics may not be authored by pixel layout.

## Distinguish measurement from derived quantity
`W_pressure = ∫∑F_aero_i v_i dt` is full tissue pressure work, not per se positive *oscillatory-mode pumping*. A phase-resolved perturbation diagnostic must define its moving/static equilibrium and independently verify its decomposition against **unmodified** full work and mechanical energy balance. Unresolved equilibrium/cycle identification => INDETERMINATE, not invented per-cycle values. A force/displacement difference is not an audible voice-difference claim.
