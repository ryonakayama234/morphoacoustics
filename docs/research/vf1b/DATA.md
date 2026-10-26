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


## Implementation authorization amendment (2026-10-26)
Creator delegated technical experiments and research PR management. This is the **VF-1B1** independent modal-work audit only; underlying VF-1A equations remain byte-for-byte unchanged. The first comparison is the exact symmetric tissue parameters and equal pressure areas of VF-1A; symmetric and antisymmetric modal coordinates use orthonormal unit vectors. Discrete per-step modal work and damping are compared to stored mechanical energy, plus the exact damped midpoint recurrence for the antisymmetric homogeneous mode. Later intraglottal pressure laws remain **outside scope** pending this evidence. New numeric tests/measurements follow this pre-source amendment. Source parent: VF-1A candidate 2b33bc69835170639fb9127c01dab7b523eff4f3; scientific results not yet run.


## Captured physical evidence (2026-10-26)
The implementation serializes 0.5s physical-time traces (NPZ) for 800 Pa uniform at 24k/48k/96k, 800 Pa constricted at 48k and zero-drive uniform at 48k. Each record has SI columns `t_s, x_plus_m, x_minus_m, v_plus_m_s, v_minus_m_s, E_plus_j, E_minus_j, full_work_j_step, full_damping_j_step, oracle_error_step, inlet_pressure_pa, q_valve_m3_s` and a SHA-256 receipt. All raw experiment evidence lives in [CI #40323754160](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40323754160) artifact `vf1b1-modal-evidence` (expires 2027-01-24; permanent archival remains separately unresolved).

Gates: `G0/G1=NUMERICALLY_CONSISTENT_WITH_SYMMETRIC_MODAL_MODEL` in the tested case, `G2=BIOPHYSICAL_MODEL_INDETERMINATE`, `G3=SELF_OSCILLATION_NOT_ESTABLISHED`, `G4=CREATOR_AUDIO_NO_GO`. This record is an experiment-local measurement format; no Core published data schema, biological material, Studio interface or external Take revision is adopted.

### Metric-format correction, current authoritative format (2026-10-26)
The initial recorded NPZ column `oracle_error_step` improperly combined distance [m] and velocity [m/s] within a Euclidean norm. Historical first artifact remains reproducible but that scalar **is not dimensionally valid as a physical measurement**. Corrected schema has **13 columns**, replacing it by `oracle_position_error_m` and `oracle_velocity_error_m_s`; the per-case receipt has corresponding `max_step_oracle_position_error_m`, `max_step_oracle_velocity_error_m_s`, and two distinct full-trajectory oracle error maxima. No physical data is EQ-processed or otherwise modified. Verified CI #40324496663 at exact implementation `2c021b2...`, raw artifact `vf1b1-modal-evidence` id `12650935991`.
