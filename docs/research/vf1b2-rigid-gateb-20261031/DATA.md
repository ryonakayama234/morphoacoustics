# VF-1B2 Gate B0 — data ownership and SI
**Prospective research-only records, NOT public Core/Studio ABI.**

| Record | owner | fields |
| --- | --- | --- |
| FixedGeometry | Core experiment | length_m, width_m, half_gap_m, taper_slope |
| FluidAssumptions | Core experiment | viscosity_pa_s, density_kg_m3, sound_speed_m_s, incompressible/Stokes/lubrication label |
| Boundary | Core experiment | upstream_gauge_pressure_pa, downstream_gauge_pressure_pa=0 |
| CandidateResult | Core experiment | sections, cell resistance, volume_flow_m3_s, face pressures, loss_w, power_residual_w, virtual forces_n, Re/Mach checks |
| OracleResult | independent mathematics | Q_exact_m3_s, integrated resistance and analytic p(x); no candidate functions imported |
| ValidationReceipt | research | source_rev, exact parameters, numeric errors, condition-level G0/G1 states; explicit G2/G3/G4 nonclaims |

Fixed predeclared geometry: L=0.01 m, w=0.01 m, h0=0.00012 m; mu=1.81e-5 Pa s, rho=1.21 kg/m^3, c=343 m/s. Frozen s=-0.2,0,+0.2; upstream pressure=0,0.1,0.2,0.4 Pa, with downstream 0 Pa; sections=4,8,16,32. Slope orientation is recorded and not inferred from audio. Store full face p and per-cell losses. Hash code and immutable stimuli when running in CI.

No measurement of physiological intraglottal p(z) has been performed; all figures here are mathematical computed quantities in a simplified limit. Any later M5/M6 comparison needs geometry/coordinate/uncertainty/rights reconciliation and cannot retroactively promote this model.

Not owned: CharacterSpec, OrganGraph public model, Performance Contract, Studio mode/tab/panel registry, immutable Take. No WAV or neural generation.
