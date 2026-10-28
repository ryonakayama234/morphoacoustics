# VQ-1 EXPERIMENT — prospective physical-phonation capability gate

2026-10-28 JST. **DESIGN-ONLY / NOT RUN.** This is a decision and test plan that must be agreed and frozen before any new solver source or test-derived threshold is written. It must not be counted as a positive physical finding, Core main adoption, Studio feature, or audible improvement.

## Verified starting evidence (historical, not newly measured)

- Core main `727b11e`: PR #235 merged; post-merge Core tests, OG3, OG4, SV1 Actions success (runs 40649993869, 40649993867, 40649993846, 40649993887).
- Adopted SV1 Experiment042: prescribed 100Hz LF, two sustained durations; creator N=1 considered individual short/long /a/-like samples acceptable; independently concatenated short renders sound bumpy. Not a self-oscillating fold or proof of continuous text reading.
- Creator Studio #32: two *local* Take UUIDs were reported signal-like / barely /a/-like. Those exact WAV/receipts are **not available in GitHub**. Do not label them M0/M1 or infer measured causes from these IDs.
- Voice Metrology CASE_001: one separate authentic CI WG2 M1 mouth-port waveform has 96.871% first-80-harmonic share at 600Hz; source shares 0.0288461%. Measurement proves where spectral concentration appears, not its physical defect.
- Draft VF-1A #209: energy-balanced two-mass coupled pilot but 20–60ms window response decays. Draft VF-1B1 #214: 0.5s symmetric pilot decays and the anti-mode receives zero pressure work. **No self-sustained phonation yet**; both depend on unmerged SFI research.
- VM-1D #206 models a finite source impedance frequency-domain intervention, not moving tissue. VF-1B2 #216/#217/#218/#222 have bounded flow/scalar references, **not** an independently measured full pressure/tissue-force distribution.

## Four candidate directions evaluated (not test results)

| Candidate | Expected creator value | Physics/contract risk | Immediate decision |
|---|---|---|---|
| Studio V2 panel implementation | High long-term creative ergonomics | Explicit UI STOP; voice backend still rejected | HOLD until feature-specific authorization |
| CVI body × MotorPersona 2×2 | Strong character identity and variation | #227: 10/16-section tasks and SMC semantic binding not yet executable together | HOLD until a trustworthy physical task |
| WG2 visco-thermal wall/radiation improvement | Direct possibility of less tonal output | needs validated 1D loss and named receiver; prescribed source persists | Parallel *candidate*, not first source capability |
| **VF-1 physical source: sustain/stop driven by tissue + respiration + tract** | **Source physiology, material variation, credible future voice quality** | hard aero force law, unmerged coupling dependencies | **SELECT one bounded physics hypothesis next** |
| VM-0 further spectral metrology | Essential when a new model needs diagnosis | Does not itself improve sound or character creation | Use as instrument, not default product task |

Selection is a **research priority**, not a claim that self-oscillation automatically sounds natural.

## Hypotheses to preregister before next source implementation

- **H0:** Under constant respiratory drive and a physically declared, independently constrained pressure-to-tissue coupling, oscillatory perturbations decay or the solver refuses. Observed apparently sustained activity may be numerical/reflection artefact.
- **H1:** At least one bounded and interpretable parameter regime shows a *non-imposed*, repeatable sustained oscillation, with reservoir work balancing tissue damping, fluid losses and radiated/absorbed acoustic energy. Drive=0 and changed loading/material produce physically explainable changes.
- **Material sensitivity H2 (conditional):** after H1, holding tract, drive and task fixed, one material parameter intervention predictably affects onset/cessation or source dynamics without artificial waveform recoloring. H2 need not imply better human likeness.

## Ordered work: proof before playable feature

1. **G0 Dependency and semantic audit:** reconcile current `morphoacoustics_waveguide` on main and SFI-2/#81, SFI-3/#84, VF-1A/#209, VF-1B1/#214. Declare whether this can be a standalone main-based research experiment or requires precisely audited stacking. Retain original 0.5s null evidence.
2. **G1 Physical mechanism law (separate approval):** choose at most one justified, explicitly dimensioned modification to existing law. Pressure spatial distribution, force integration, port signs, external reservoir work and independent reference must be specified *before code*. The currently missing M5 pressure taps cannot be invented from k_ex. If evidence insufficient, `STOP_PHYSICAL_REFERENCE`, rather than tuning a fake voice.
3. **G2 Numerical/causal experiment:** frozen 0Pa and positive-pressure cases; exact geometry/material/initial perturbation; two time steps and a longer decay-vs-growth window; independent modal/work oracle, passive-tract and valve energy, solver failure controls; perturbation-refinement and zero-drive falsifiers. Publish signed raw power, displacement, pressure, flow, work and CI identities. A positive total work balance alone is not a self-oscillation proof.
4. **G3 Character variation (only if G2 positive):** fixed tract+drive, one material intervention; fixed tissue+drive, one tract/body intervention. Measure onset, fundamental periodicity if resolvable, change in physically computed source spectrum and port observables. No creative slider yet.
5. **G4 Voice/Studio gate (later):** valid radiation/monitor boundary; new immutable physical Take vs frozen old single-vowel baseline, fixed listening level and blind A/A/A/B; independently judge artifact severity and practical creator value. Core physical success without creator GO **remains a Studio NO-GO**.

## Pre-data decisions / STOP meanings

- **GO_RESEARCH_LAW** only after G0/G1 source audit and frozen independent physical reference.
- **NO_SUSTAINED_PHONATION** for valid dissipating cases, retained as evidence (not patched by imposing F0).
- **NUMERICALLY_UNRESOLVED** for convergence, force/power mismatches, contact without model, sampling or unstable numerics.
- **INDETERMINATE_PHYSIOLOGY** if the reduced model passes arithmetic but lacks pressure/material calibration.
- **NO_GO_CREATOR** until same-task audible improvement and explicit creator acceptance after G4.

No numeric tolerance, source calibration, measured anatomy or false voice-quality benchmark is invented here. Numerical floors must be justified and frozen with the selected law and exact reference **before** running new code. Do not recycle old VF-1A success receipts as a new G2 success.

## Required simultaneous records on each future experimental change

1. Update `SYSTEM.md`: the actual force, flow and graph coupling law, including what remains unmodeled.
2. Update `DATA.md`: physical parameters/units, permanent identity, raw state and refusal status.
3. Append to `EXPERIMENT.md`: preregistration SHA, red/green runs (including failures), independent oracle/reviewer, measured uncertainty, adopted/rejected decision.
4. Link Core #207/#212/#215 and Studio #32, and preserve historical Takes; request external Codex review and exact-head CI before proposing a merge.

**No UI code, physics source, tests, audio or Core API is changed in this design PR.**

## G0 source audit observation — 2026-10-28 (append-only)

**Inspected code, not executed physics.** Current-main `src/morphoacoustics_waveguide/passive_waveguide.py` returns `source_pressure_pa`, `inlet_flow_m3_s`, `source_work_j`, and `energy_residual_j` on each checked single tick. Its first boundary uses `a_new=b_old+Zc*U`, hence `p_in=a_new+b_old=2*b_old+Zc*U`; source work is `dt*p_in*U`. It is promising for a same-tick affine passive boundary in a separate source/flow solve. **No independent energy test or new port-coupled code was run**.

Draft SFI-2 #81 provides an *implicit-midpoint* duct with independently selected dt; Draft SFI-3 #84 and VF-1A #209 are stacked and unmerged. The current-main FIFO port and VF-1A's midpoint source-coupling implementation therefore cannot be joined by import or class substitution. **G0 decision: PARTIAL_CODE_AUDIT_ONLY.** Before GO, freeze a testable research port interface against current main, verify exact inlet affine prediction across nonzero pre-states, same-step p/U and work, B0/reflection controls, invalid inputs, collision/refusal atomicity and time-step stability. Compare an independent wave-scattering oracle, not merely replay the implementation under test. Do not start G1 pressure-law tuning or claim new phonation from this observation.


---

## D1 final pre-implementation experiment design — G0-P / G1-S / G1-D (2026-10-28 JST)

**PROPOSED FROZEN DESIGN — NO NEW SOURCE/TEST EXECUTED.** This is an additional pre-implementation decision gate. It is not an experimental result and cannot amend pre-existing VF-1A/#209 or VF-1B1/#214 outcomes. The current exact tested Core main head at planning time is \`727b11ecf103f5c087cfcb820bdec11f883e7c03\`; re-check before any test-only commit.

### Measurement targets, estimands and falsifiers

| Gate | Measured target (with units) | H0 / what would refute approval | H1 / what would support limited approval |
|---|---|---|---|
| **G0-P1 port prediction** | for native tick \(n\): actual inlet \(p_n\,[Pa]\) versus independent \(2b_n+Z_cU_n\), pressure residual Pa and dimensionless scaled residual | wrong sign, stale reflection, hidden half-tick, stateful peek, inconsistent boundary | same-tick affine relation on nonzero states; exact no-mutation and one-step commit |
| **G0-P2 power & physics** | \(\Delta E\,[J]\), source \(dt\,p_n U_n\,[J]\), outlet loss [J], signed residual [J], latency [s] | energy created from zero work, wrong port direction, boundary mismatch, geometry clock silently changed | bounded residual against independent port/scattering reference, correct first arrival, failure atomicity |
| **G1-S static wall pressure** | paired measured \(Q\,[m^3/s]\), \(p_{\rm wall}(z)\,[Pa]\), FW/NFW if present, geometry [m], pressure error [Pa], uncertainty | only scalar \(k_{\rm ex}\), unqualified digitization, mismatched pressure/diameter, wrong surface orientation | declared M5 **static** experimental reference and physically scoped pressure law agree within independently justified uncertainty |
| **G1-S effective tissue force** | \(\int_{S}p_{\rm wall}\,n\cdot\partial r/\partial x_i\,dS\,[N]\) | no matched wet-surface/material coordinate map; integration/units invented | conditional **static force-map only**, with independently specified surface Jacobian |
| **G1-D moving-wall work** | signed \(F_i v_i\,[W]\), \(P_{\rm sub}q\,[W]\), \(p_{\rm in}U_{\rm in}\,[W]\), dynamic \(p_{\rm wall}(z,t)\) and all state energy [J] | extrapolation of static pressure into dynamic unvalidated, missing \(\dot V\) or contact work, added phase lag to induce sound, work mismatch | separate dynamic model and qualified reference support power/causal closure; still **not yet** sustained-phonation or audible-voice proof |

No overall percentage score can substitute these separately reported endpoints.

### Exact order, to avoid speculative simultaneous implementation

**Stage A — freeze G0-P, independent oracle and fixture (NO solver modifications).**
1. Pin Core main SHA, baseline Python/runtime, true geometry sections, cells-per-section, outlet and physical clock. Reproduce currently adopted WG smoke separately; do not graft SFI-2 classes onto main.
2. Define finite G0 test conditions: one uniform duct (matched), two equal-area serial sections, two unequal-area sections, and two previously prepared verified 16-section M0/M1 body fixtures *if supported without changing original definitions*. Cases with \`b=0\` and genuinely evolved nonzero inlet reflection, \`U=0\`, \(+U\) and \(-U\), plus B0 and at least one distinct built-in termination. *Body A/B are for geometric portability, not audible character improvement.*
3. Independently compute inlet pressure from traveling-wave boundary/reflection law and closed-form uniform matched-tube response. One reference must not call the new adapter, and mutation tests must kill a deliberately wrong reflected-wave sign, wrong \(Z_c\) and off-by-one tick. B0 energy and delay compared to the already validated Core baseline with its exact assumptions.
4. Engineering acceptance target for deliberately **non-negligible, finite** reference cases: \(|p_{\rm actual}-p_{\rm ref}|/\max(|2b|+|Z_cU|,1\,Pa)\le 10^{-10}\), \(|\Delta E-W_{\rm src}+W_{\rm loss}|/\max(|\Delta E|+|W_{\rm src}|+|W_{\rm loss}|,10^{-12}\,J)\le10^{-10}\). These are **pre-data numerical roundoff/discrete-equation checks**, *not* biological accuracy or empirical calibration. For near-zero-work cases additionally check absolute zero-state and exact no-advance behavior; do not treat a tiny normalized ratio alone as pass. Freeze amplitude/energy ranges and independent reference calculation **before test code**; failure to set nontrivial excitation means \`UNINFORMATIVE_FIXTURE\`.
5. Test repeated \`peek\` purity, exact one-tick \`commit\`, stale/duplicate/ref mismatch, nonfinite/unit-type errors, and failure-atomic state. A rejected attempt must not mutate the only live session; a second intentionally fresh valid attempt must match an untouched reference copy.
6. Physical native-clock interpolation is **outside G0**; \(dt\) stays per-body physics. Clock/cell-size comparisons, if added, compare at equal *physical time* and declare the discretization order instead of requiring pointwise bit equality at different clocks.

**G0 decision:** \`GO_PORT_RESEARCH_ONLY\` **iff** genuine source-only/test-only RED evidence where applicable, independent oracle, normal and adversarial tests, exact-head CI and external code review all support the bounded relation. If any physical or atomicity gate fails: \`REVISE\` or \`STOP_INCOMPATIBLE_PORT\`. **G0 passing authorizes no wall-force model, self-oscillating glottis, generic OrganGraph or voice-quality claim.**

**Stage B — freeze G1-S measured static aerodynamic qualification before force solver.**
1. Audit the actual M5 paper source and previous Core #215, #218, #220, #222 fixtures. Pin one preselected target: \(d=0.02\,cm\), \(\Delta P=10\,cmH_2O\), taps 6/11/13 at \(z=0.211/0.413/0.511\,cm\), previously recorded Q 64.7 cm³/s **subject to recheck**. Preserve gauge-pressure reference and 7.5× model/life-size-equivalent scaling from the original paper, NOT mix them.
2. Acquire actual wall-tap data/figure point positions with traceable source and extraction uncertainty; measure FW/NFW as distinct where the paper distinguishes them. Existing 35 table Q and exit-coefficient pairs are scalar reference context, **not pressure taps**. Do not turn calculated pressures from published formulas into "independent measured p(z)".
3. Predefine static candidate(s) without adjusting to the held-out tap data: paper's declared entrance/intraglottal/exit equations as a **published comparator**, and an independently authored spatial law only if it has an explicit valid geometry and source. Fit parameters only on a declared training subset, never on held-out pressure taps; require uncertainty-based comparison and negative wrong-diameter/pressure/reference controls. For any integrated \(F_i\), independently freeze wet-surface geometry/Jacobian.
4. Set reference/tolerance after confirming instrument and extraction uncertainties but **before** calculating candidate-vs-reference residuals. Keep missing data \`REFERENCE_UNQUALIFIED\`; no post-hoc more permissive threshold after failure.

**G1-S decision:** \`GO_STATIC_LAW_RESEARCH_ONLY\` only when spatial pressure/geometry/flow and measured uncertainty independently qualify. If pressure field or surface geometry is missing: \`STOP_PHYSICAL_REFERENCE\` / \`INDETERMINATE_FORCE\`. No automatic onward G1-D.

**Stage C — G1-D moving-wall feasibility (separate prospective go/no-go).**
1. Choose a **single** moving-wall law with explicitly defined fluid control volume and wet surface; write terms for \(\dot V\), \(\mathbf F\cdot\dot{\mathbf x}\), fluid inertance, losses and acoustic inlet/outlet work. No transplant of a static M5 pressure map into a moving geometry without dynamic-validity evidence.
2. Seek independent dynamic reference or demonstrable independent first-principles limiting case. If neither exists, STOP physical adoption and (if scientifically useful) label any toy dynamics \`SYNTHETIC_ONLY\`; do not call a numerically growing oscillator a physiological voice source.
3. Only after qualified force/work can the *different later* VF-1B2/VQ-1 G2 experiment test sustained oscillation: 0 Pa null, positive pressure, paired \(\Delta t\), long observation after transients, spectral and **time-domain** amplitude stationarity, tissue modes and signed cycle work. Check initial perturbation shrinking/growing, zero-pressure decay, changed acoustic load/material intervention, and energy; a static equilibrium or transient cannot pass.
4. Delayed one-tick pressure, periodic externally imposed aperture/F0, negative damping, arbitrary energy/force injection, post-EQ and neural audio overwrite are **prohibited causal shortcuts**. Unknown contact physics refuses rather than clipping an aperture.

### Realistic time and scope limits

- **One core branch and one bounded task** for G0; no recursive absorption of Draft #81/#84/#209/#214 source or PR chain. The current \`src/morphoacoustics_waveguide\` and \`src/morphoacoustics_graph\` APIs remain unchanged during test-first port research.
- If G0 succeeds but G1-S cannot identify actual wall force, report **positive numerical infrastructure + scientific STOP** rather than expanding into arbitrary tissue presets.
- A scientifically valid *static* glottal law is still not a working autonomous voice. A validated self-oscillator is still not known to be humanlike or audition-worthy.
- No Studio code or UI changes. Frozen slots: \`character.canvas\` + Inspector, \`motion.canvas\`, \`scene.canvas\`, \`take.transport\`, \`research.drawer\`. Preserve legacy Takes.
- The earliest actual creator sound trial is a future **separate** task requiring named radiation/receiver or explicitly labeled mouth monitor and an authentic same-task, fixed-level comparison against accepted SV1 and held WG2. N=1 listening has meaning as **creator acceptance only**, not an anatomy experiment.

### Evidence and execution bookkeeping

Before implementation put the exact protocol revision, source heads and independent oracle digest in a **new prospective child experimental record**. For every meaningful work step append alongside the existing three files: *SYSTEM* (causal law / capabilities), *DATA* (units / versioned records), *EXPERIMENT* (pre-data hypothesis, tests, failure history, raw evidence, actual result). All claims cite exact SHA and Action run/artefact and distinguish run status from scientific verdict. Ask Codex review for code/API regressions; separately audit scientific causality. Do not merge merely because CI passes.

### References

- Project: [Core Draft #237](https://github.com/ryonakayama234/morphoacoustics/pull/237), [Core #207](https://github.com/ryonakayama234/morphoacoustics/issues/207), [Core #215](https://github.com/ryonakayama234/morphoacoustics/issues/215), [Core Draft #220](https://github.com/ryonakayama234/morphoacoustics/pull/220), [Core Draft #222](https://github.com/ryonakayama234/morphoacoustics/pull/222), [Studio V2 contract](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md).
- Titze 2008, [DOI 10.1121/1.2832337](https://doi.org/10.1121/1.2832337) — rationale for source–tract loading.
- Fulcher, Scherer & Powell 2011, [DOI 10.1121/1.3514424](https://doi.org/10.1121/1.3514424) — **static M5**, not moving-wall data.
