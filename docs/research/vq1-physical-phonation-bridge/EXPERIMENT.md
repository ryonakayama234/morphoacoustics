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
