# Embodied Voice Lab — future capability ladder (design proposal, 2026-10-23)

**Status:** proposal, NOT adopted API or finished voice generator. Follows [SA-1 #168](https://github.com/ryonakayama234/morphoacoustics/issues/168) and experimental JET-P0 [PR #167](https://github.com/ryonakayama234/morphoacoustics/pull/167). SMC and ASMR remain independent opt-in modules.

## Creator north star
Make a character by constructing vocal biomechanics, then make it act under the laws of its body. Physical incompatibility and instability are part of the possible performance. The creator should discover a recognizable voice and hear what a *specific* structural/habitual control actually changes. No arbitrary waveform beauty filter is Core causal authority.

## Three separately designed entities
1. `BodyRevision`: physical topology, organ geometry, material distribution, actuator attachment, constraints, solver trust domain, parameters/unit provenance. Versioned, immutable once recorded.
2. `MotorHabit` (proposed, not present contract): stable speaker-specific feasible control preferences, not a speaker_embedding, identity label, output EQ or ad-hoc waveform. Calibrate only after there are multiple feasible strategies.
3. `PerformanceDirection`: ephemeral expressive intent (effort, care, speaking style) mapped through a body-specific controller; it does not directly command SPL, waveform F0 or formants.

~~~mermaid
flowchart TD
    ST[Studio Character / Body Atelier] --> BR[Immutable BodyRevision]
    ST --> DIR[Acting Direction]
    SMC[Optional Speech Motor Compiler] -. symbolic tasks .-> CTRL[Body-conditioned controller]
    DIR --> CTRL
    HAB[Candidate MotorHabit] --> CTRL
    BR --> CTRL
    BR --> VF[Source-organ mechanics]
    CTRL --> VF
    BR --> AC[Passive / damped organ graph acoustics]
    VF <-->|p,u acoustic port| AC
    AC --> OBS[Raw Pa, p/U trace, energy, feasibility, solver provenance]
    OBS --> VA[Studio frozen Take & Voice Atlas masked audition]
    VA --> ST
    ASMR[Optional ASMR module] -. separately gated source port .-> AC
~~~

Current Core is **not yet** that coupled system: the feedback arrows are a target for VF-1; present JET-P0 prescribes glottal opening/pressure and forwards flow into the existing static M0 acoustics.

## Milestones, dependencies, and independent acceptance
| Gate | Creator unlock | Core research question | Separate evidence |
|---|---|---|---|
| **SA-1 NOW** | meaningful physical timbre audits instead of fragile source sliders | Why do subpercent flow-noise perturbations dominate high-frequency outlet pressure? | Independent port transfer oracle, null/source decomposition, exact raw Pa, retain JET-P0 FAIL |
| **VF-1** | a small/large creature develops its own pitch and phonation onset from mechanics | Can a reduced self-oscillating (2-mass / body-cover) fold with pressure drive, contact and acoustic loading yield different real regimes? | Minimum pressure threshold, area/flow phase, F0 *emergent*, closure/open quotient, safety/passivity, source-load feedback, no arbitrary pitch remapping |
| **VA-B1** | edit body size/length *and* phonating tissue; same scene, audible A/B with controls | Are vocal-tract resonances and phonation traits independently/ jointly sensitive to materials/geometry? | Body A/B and A/A negative control, criterion distinguishing numerical vs auditory differences; held-out body and physical reproducibility |
| **MP-1** | persistent character "voice habits": gentle, edgy, forceful are motor strategies | Can one body support two feasible control allocation preferences while retaining identity across vowel/effort? | 2 body × 2 habit × multiple conditions; blind discrimination vs recognition/quality, with infeasible regimes preserved |
| **OG-VOICE** | branching/multi-cavity animals with characteristic resonances | Do typed organ ports, valves, nasal routes and separate source placement yield novel acoustic behavior with conservation/passivity? | Independent linear/feedback response tests, route/port identity, perceptual identity and physical-null gates |

## Do NOT conflate fidelity and creativity
A shape or material edit matters acoustically only if it modifies `mass/stiffness/contact/pressure/flow/acoustic impedance/absorption` along a verified physical path. Use multiple fidelity backends under one declared tissue data model: fast kinematic preview, reduced dynamical biomechanics, optional research FEM; choose fidelity per organ, not globally. A short tract affects formants, but **does not by itself dictate F0**. Small creatures can have high resonance and a low or irregular oscillator, or high F0 with dark subglottal coupling; each must be physically realizable.

## Studio UX concept — Voice Organ Workbench
**Edit** anatomy or a control; **watch** pressure, glottal area, air/port flow and tract deformation; **hear** fresh bounded Core take; **compare** blind with original exact-source Take; **save** immutable body and scene. Organ edits may refuse with a meaningful mechanism explanation rather than fabricate a nice voice. Separate quality, distinctiveness, speech intelligibility, identity consistency and artifact, plus free form impressions; creator preference stays optional and is never a scientific physics gate.

## Research and adoption rules
Do numerical and physical gates first, then listening. Improvement of naturalness is a separate hypothesis, not guaranteed by mechanics. A physically useful source can be adopted at limited scientific fidelity without asserting studio-ready voice quality; Creator-ready modules must earn a separate auditory gate. No Core waveform manipulation to force identity or art-directed loudness. Neural closure may only model unresolved declared subsystem dynamics, with physically defined inputs/units/trust region and ablation failures.
