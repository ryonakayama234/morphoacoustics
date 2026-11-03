# VF-1B2 DATA — typed scientific observables, owner, units, provenance
**Proposal only / NOT a new Studio contract, public Core type, or Take.**

## Experiment-local entities (read-only records)
| Record | Owner | Required content | Immutable linkage |
|---|---|---|---|
| StudyManifest | Core research | exact Git checkout SHA, parent stack SHAs, python/NumPy, clean status, model family, assumptions, parameter/fixture digest, test status, reference source IDs, external data license/availability | one manifest per scientific run |
| TissueFixture | Core research | m_L,m_U [kg], k_L,k_U,k_c [N/m], d_L,d_U [N s/m], rest gaps [m], depth ell [m], length L_g [m], initial x_i [m],v_i [m/s], no-contact floor [m²] | hash of parameter table; not a Studio Character body |
| GlottalFluidFixture | Core research | fluid reference rho0 [kg/m³], c [m/s], atmospheric reference [Pa], EOS name/version, cell lengths [m], volumes [m³], pressure-loss/separation closure IDs and allowed flow direction | reference derivation + SI provenance |
| AcousticFixture | Core research | exact pinned 10-section tract length [m], area [m²], sample clock [s], inlet/outlet port orientation, passive termination and supported frequency range | no reuse of 16-section Exp043 IDs |
| Stimulus | Core research | Psub(t) [Pa] nonperiodic pressure schedule; initial perturbation and offset, load branch and changing factor | can be later mapped to Motion, but no SMC import |
| DynamicsTrace | Core research | t, x_L/x_U [m], v_L/v_U [m/s], p_wall_lower/upper [Pa], Psub/Ptract [Pa], rho_j [kg/m³], Uin/Uout/Utract [m³/s], cell mass [kg], A_L/A_U/Amin [m²], separation location [m] when supported | raw float64 buffers + column/unit manifest |
| WorkTrace | Core research independent observer | F_L/F_U [N], F_i v_i [W], W_i [J/cycle], mode +/− work [J], E_tissue/fluid/tract [J], source/acoustic port work [J], viscous/separation/tissue/tract/outlet losses [J], residual [J], mass residual [kg] | separate code path + hash |
| ScientificResult | Core research | G0 measurement, G1 physical/numeric, G2 reference/biology, G3 self-oscillation, G4 creator audio; per-case status and explicit exclusions | never infer GO from a valid WAV |
| Creative Take | Studio | NONE at this stage | no fabricated WAV/Take or changed historical take |

## Candidate exchange formats (not API)
- `manifest.json`: machine readable exact code and source trace provenance, units and numerical methods.
- `fixture.json`: all immutable physical assumptions including wall shape functions, flow loss closure, boundary and initial conditions, reference access and capability.
- `trace.npz`: raw float64 arrays, column metadata and failure partial traces; no necessary listening WAV.
- `metrics.json`: independent observer outputs, conservation residuals, convergence, cycle segmentation, intervention contrast and outcome statuses.
- `SYSTEM.md`, `DATA.md`, `EXPERIMENT.md`, append-only `RESULTS.md`: synced per research revision, with amended prereg threshold explicitly marked prospective vs post hoc.

## Units and measurement science
- Primary measured (computed) **measurands**: (1) static p(z), U pressure/flow relation; (2) moving-wall generalized force F_i and signed wall work W_i; (3) mass balance and power ledger; (4) pressure/velocity phase/cycle work; (5) steady-pressure growth/decay, source shutoff and source–tract loading dependence.
- Each observed physical signal records its sensor location and orientation, time standard, sampling step, filter/no filter, window definition, numeric uncertainty and lineage. No port pressure misnamed far-field ear pressure.
- `p × U` = Pa·m³/s = W; `F × v` = N·m/s = W; `dissipation` = J integrated and nonnegative; `mass` = kg; `d rho/dt` = kg m^-3 s^-1.
- Explicit time-step convergence: same physical time horizon, same source drive and body/load; compare 24, 48, 96 kHz where supported. Numerical uncertainty derived from discretization/reference and independent observer, not from historical waveform hash differences.
- Separately retain numerical-vs-biophysical validity. Exact energy closure inside one set of equations does NOT prove pressure law realistic; physiology needs independent external data/uncertainty.
- Distinct `INVALID`, `UNSUPPORTED_CONTACT`, `UNSUPPORTED_FLOW_REGIME`, `NUMERICALLY_UNRESOLVED`, `REFERENCE_UNAVAILABLE`, `NO_SELF_OSCILLATION_FOUND`, and `CREATOR_AUDIO_NOT_EVALUATED` statuses. Distinguish failure vs lack of positive result.

## Studio V2 mapping (NO UI changes)
- `character.canvas`: future immutable Character/OrganGraph revision, only after separately validated domain contract; **not** TissueFixture itself.
- `motion.canvas`: future task-level effort / phonation direction, not Psub waveform pasted as motion.
- `scene.canvas`: stage actors and validated receiver references, not fake ear observations.
- `research.drawer`: scientific receipt/trace with exact physical revision and uncertainty; future data display only upon approval.
- `take.transport`: only *future genuinely executed and qualified* immutable Takes. Never a numeric research trace disguised as a creative audio Take.
- `project.library`, `selection.inspector`, `global.header`: existing accepted ownership; no panel/schema edits.

## Backward-compatible baseline and research lineage
- Core main commit at design time: `727b11ecf103f5c087cfcb820bdec11f883e7c03`.
- SFI-2 Draft #81 HEAD `6cdd21768fd92167bbc56c57264fc161c35e7dda`; SFI-3 Draft #84 HEAD `7ab18f25f53bc5f81bcdf5e7697fd11981abe6dd`.
- VF-1A Draft #209 HEAD `2b33bc69835170639fb9127c01dab7b523eff4f3`; VF-1B1 Draft #214 HEAD `fc9c98c59c02b38aa28b16e50e8da4e0cb2a67d3`.
- These are unmerged research revisions. Never treat the Core main branch as containing those solver implementations.
