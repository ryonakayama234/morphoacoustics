# VF-1B2 C1-R0 — DATA / strictly named SI records
Research-only dataset; no public Core schema, no Studio Take.
Fixture: {study/schema, L_g_m, ell_m, half_gap_m, m_L_kg, m_U_kg, k_L_N_m, k_U_N_m, k_c_N_m, d_L_Ns_m, d_U_Ns_m, P0_abs_Pa, Pext_abs_Pa, gamma, rho0_kg_m3, x0_m[2], v0_m_s[2], duration_s, dt_s}. Derived g_m2, V0_m3, gas_mass_kg. Reference units explicit.
RawTrace per physical tick: {t_s, x_m[2], v_m_s[2], V_m3, p_abs_Pa, rho_kg_m3}; stored by one-sided initial conditions without regeneration; run metadata includes sha256 input/file, solver source version, Python version, integration dt, timestamp and end status. No audio files.
IndependentObserver: computes V, p, mass, gap, gas/internal/tissue/external-pressure energy and accumulated damping loss *from raw primary state*, not the solver's H helper. Refuse invalid trace length, nonfinite, non-monotonic t, negative effective half-gap, p-law mismatch, altered pressure, altered density, physical nonconvergence.
ScientificVerdict separates code/numeric pass from source, biological, autonomy and creative quality:
C1_R0_G1_PASS_MATHEMATICAL_SEALED_ONLY / G1_FAIL / NUMERICALLY_UNRESOLVED / INVALID / NO_FLOW_OR_PHONATION / NOT_STUDIO_ADOPTED. These statements never imply self-oscillating source or ear-quality speech.
Research digest is tamper detection of saved bytes, not authentication of malicious Git edits. Exact source SHA and environment must be recorded. Cross-environment binary equality of floating-point arrays is not promised; independent numerical floors distinct from archive hashes.
No second BodyRevision registry; no imports into Core main or src/morphoacoustics_graph.

## Review amendment — stricter raw data binding
For this frozen 6ms/4–2–1us study, the saved trace must contain the complete finite timestamps, exact start state from the declared immutable Fixture, SI-valid finite positive physical parameters, and finite pressure/mass/energy. All saved velocities must agree with the independent signed kinematic witness; max derivative discrepancy in m/s is recorded with the audit engineering tolerance. The output receipt includes `max_energy_residual_J`, `max_energy_residual_relative`, `kinematic_velocity_error_max_m_s` and `kinematic_tolerance_m_s`. This is research trace integrity, not a newly published Studio contract.
