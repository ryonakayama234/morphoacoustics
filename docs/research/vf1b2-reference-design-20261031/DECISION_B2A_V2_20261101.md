# VF-1B2a — Design Decision v2 (2026-11-01)
**Status: REVIEWABLE DESIGN FINAL CANDIDATE / OWNER ACCEPTANCE PENDING. NO PHYSICAL IMPLEMENTATION APPROVAL, NO BIOLOGICAL OR VOICE CLAIM, NO MAIN MERGE.**
Primary module: Core experiment-local moving-wall glottal fluid–tissue coupling. This is an additive, prospective amendment to PR #259, not a retrospective rewrite of preregistered PR #262. If inconsistent, this v2 design supersedes PR #259's proposed B2c sequencing and pressure-only global ledger, subject to explicit owner acceptance. Existing frozen references and historical failures remain unchanged.

## Creative purpose and decision
A physically defined respiratory actuator and organ morphology should determine whether an organ oscillates, with what dynamics, and whether it stops; the same motion intent on different organ bodies may yield different states or honest failure. An audible, recognizable character voice remains a separately gated future outcome.

**SELECTED candidate physics family:** two outward-moving lower/upper tissue degrees of freedom, spatially varying moving-area quasi-1D compressible fluid with conservative mass, momentum and *total-energy* transport, and a no-contact fixed downstream reservoir at first. Move to an acoustic tract only after a separately demonstrated conservative mean-flow/acoustic bridge. Do not reuse the old VF-1A scalar valve loss and g·v relation as a conservation proof.
This is a **model-family and interface decision**, not acceptance of any empirical separation/viscosity closure or anatomical voice model.

## Decisions taken (D01–D10)
- D01 — **Preserve authority.** Core owns geometry-to-physical-state preparation, mass/momentum/energy laws, stepping and failure classification. Studio Character/Motion/Scene/Inspector/Take Dock/Research Drawer remain exactly within accepted Workspace V2 slots; no Studio source, Performance Contract, SMC or ASMR edits.
- D02 — **Lower/upper shape coordinates.** Use two outward-moving wall coordinates x_L/x_U with shape functions phi_L=1-z/L and phi_U=z/L; both influence the entire gap, with distinguishable wall-pressure integrals. Use a positive finite initial gap and reject contact; no reflection/clamping.
- D03 — **Use absolute thermodynamic pressure internally.** Declare ambient reference P_atm and external tissue pressure P_ext. Mechanical wall force is from p_abs-P_ext, while fluid energy and convected enthalpy use a consistent absolute EOS. An equivalent relative-energy ledger is permitted only after algebraic derivation of all ambient/reference cancellation terms.
- D04 — **Explicitly conserve moving-volume fluid mass, momentum and energy.** Conservative integral finite-volume fluxes with area evolution; carry separate boundary mass, axial momentum, total enthalpy, moving-wall pressure work and declared dissipative sinks. No pressure-work-only global budget.
- D05 — **Stage downstream coupling.** Stage C1 uses physically declared reservoir state (mean-flow boundary) to qualify moving-wall FSI; this does not test tract feedback. Stage C2 derives a conservative bridge to SFI-2/3's perturbation acoustic port; only after C2 may source–tract feedback or autonomous phonation with tract-load intervention be claimed. A glottal bulk flow cannot simply be identified with the acoustic inlet fluctuation.
- D06 — **Numerics.** Co-solve fluid and tissue unknowns at the same timestep using an implicit residual-based method; energy-consistent midpoint/discrete-gradient or equivalently proved power-preserving integration is a *candidate*, not an assertion that a particular integrator already conserves the discretization. Advance persistent states atomically once; fail rather than clip, silently rescale, or post-correct an unfavorable cycle.
- D07 — **Loss model is evidence-gated.** PR #262 rigid Stokes control is qualified ONLY for its small-pressure low-Re domain. Do not extend it to 400/800/1200 Pa. Start noncontact, explicitly tag inviscid/no-separation mathematical controls as NONPHYSIOLOGICAL. Select high-drive loss/separation closure, or mark EXTERNAL_REFERENCE_UNAVAILABLE and HOLD biological/phonation qualification, before any high-drive claims.
- D08 — **No preferred acoustic result.** No imposed F0/periodic source/negative damping/LF pulse in the claimed phonator. A failure to self-oscillate or to differ across bodies is a legitimate experimental result.
- D09 — **Scientific versus creative gates.** Numerical closure (G1), external pressure/flow validity (G2), sustained source mechanism (G3) and listener/voice quality (G4) never imply one another. Do not create a Studio Take from numeric traces or equate mouth-port pressure with ear pressure.
- D10 — **Reference and adoption.** PR #262 remains REFERENCE_ANALYTIC_CONTROL_V1 (research, Draft). The accepted OG-3 passive fixed2 contract remains unchanged. A new qualified phonator or public OrganGraph ABI needs a separate explicit Gate C / owner approval.

## Technical choices compared
| Candidate | Possible benefit | Blocking weakness | Choice |
|---|---|---|---|
| Reuse VF-1A scalar p·U/geometry law | fastest | scalar flow and spatial work cannot establish moving-wall conservative mass/enthalpy; possible doubled wall work | reject as phonator; keep negative control |
| Pure incompressible moving-volume fluid + prescribed downstream pressure | cheap; useful limits | no compressible energy storage or compatible acoustic port by itself | retain as analytic limit only |
| Compressible quasi-1D moving-area FV + two-mass tissue | explicit density, momentum, convected energy and spatial pressure work | difficult boundary and loss closure; external validity still unknown | **chosen research family** |
| Immediate coupling to existing SFI-3 p' U' port | reuse tested acoustic subsystem | unproven total-flow versus perturbation power interface | **HOLD pending C2 proof** |
| Full 3D FSI | can resolve separation/contact more directly | complexity and independent input data cost | independent discrepancy reference later, not runtime prerequisite |

## Release / stop conditions
**B2a READY_FOR_IMPLEMENTATION** only after: (1) continuous and discrete signs/units/energy derivation independently reviewed; (2) explicit EOS, moving-area flux, boundary characteristic/reservoir treatment and mass/momentum closure; (3) predeclared loss/separation scope or honest external-data blocker; (4) source SHA inventory and standalone analytic/negative controls; (5) thresholds/precision determined without inspecting prospective output; (6) engineering and provenance review. Otherwise B2a DESIGN_HOLD and no source implementation.

Subsequent C1 success means only moving-wall flow–tissue numerical research. It does **not** allow C2 or an acoustic source. Subsequent C2 success means bounded two-way source/tract physical coupling. It does **not** certify natural voice or species physiology.

## Exact known predecessor status (checked 2026-11-01)
- PR #81 SFI-2: unmerged research passive 1D tract @ 6cdd21768fd92167bbc56c57264fc161c35e7dda.
- PR #84 SFI-3: unmerged, stacked on #81 @ 7ab18f25f53bc5f81bcdf5e7697fd11981abe6dd.
- PR #209 VF-1A: unmerged, stacked on #84 @ 2b33bc69835170639fb9127c01dab7b523eff4f3.
- PR #214 VF-1B1: unmerged, stacked on #209 @ fc9c98c59c02b38aa28b16e50e8da4e0cb2a67d3.
- PR #262 rigid low-Re control: Draft research HEAD @ 83c699a5c2c891fd45d9536616d7c09f1a5164ca, 7 tests and 48-case exact-code CI. Does not include a moving-wall solver or biophysical validation.
- Studio V2 accepted layout: Studio docs/product/STUDIO_WORKSPACE_V2_DECISION.md, design Draft #33; panel edits prohibited before separate creator authorization.

## Research anchors and provenance
- Energy-based fluid–structure model of the vocal folds, 2021, DOI 10.1093/imamci/dnaa031 (port-Hamiltonian model-class precedent).
- Li et al. momentum-based reduced flow model, J Biomech Eng, DOI 10.1115/1.4044033 (bounded 3D FSI comparison).
- Stanford compressible-flow course notes, Cantwell, Chapter 9 (control-volume total enthalpy accounting).
- Internal: Core #199/#215, research design PR #259, rigid reference PR #262, SFI-2 #81, SFI-3 #84, VF-1A #209, VF-1B1 #214.
**Scientific literature informs the model choice; no article is evidence that this particular implementation exists or is validated.**
