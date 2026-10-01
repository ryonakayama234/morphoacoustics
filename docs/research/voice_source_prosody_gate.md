# Research Gate — voice source, prosody, and laryngeal coordination

Status: research decision for R1 / issue #23.  This document records a design decision before production implementation.

## Trigger

Experiment 012 separated two audible artifacts:

- frequent pitch-synchronous snap: sharp explicit harmonic source;
- startup transient: renderer edge handling.

After replacing the source with a deliberately smooth periodic surrogate, the artifacts disappeared in listening, but the result became buzzer/alarm-like and lost much of the perceived fluctuation and word-boundary impression.  The smooth surrogate was never intended to be a production vocal-fold model.

The question is therefore not yet whether the 1D tract is too low fidelity.  The immediate question is whether the missing behavior lies in the source/control layers upstream of the tract.

## Repository facts

The canonical `Task` vocabulary already contains `CONSTRICT`, `OPEN`, `PHONATE`, and `PRESSURIZE`.  `Gesture` carries task timing plus explicit parameters, and `GestureScore` is only a temporal collection of gestures.

The current Fidelity-0 `Tract1DRealizer` explicitly supports only active `CONSTRICT` tasks and reports the others as `TASK_UNSUPPORTED`.  Therefore there is no need to redefine `PHONATE` as a waveform or to force source behavior into the tract realizer.

The current voiced source used by Experiments 009–011 is experiment-local: fixed `F0 = 100 Hz`, 40 phase-aligned harmonics with amplitude proportional to `k^-1.2`, plus a file-boundary ramp.  It is not a laryngeal controller.

## Literature findings

### 1. Voice-source behavior can matter more than additional tract-acoustic detail

Birkholz & Drechsel (2021) added several realistic vocal-tract acoustic effects to VocalTractLab but did not obtain improved perceived naturalness; their analysis concluded that voice-source settings played a larger role than the tested additions.

Source: https://doi.org/10.1016/j.specom.2021.06.002

This does not imply that tract fidelity is unimportant.  It does show that increasing tract complexity is not the first justified response to the current buzzer-like result.

### 2. LF-family parametric models are a suitable low-fidelity source layer

The Liljencrants–Fant (LF) family explicitly controls glottal-pulse timing/shape, including open and return phases that determine important source-spectrum properties.  A causal linear implementation (LFLM) has been perceptually compared with LF/LFCALM and found sufficiently consistent, with the authors explicitly encouraging the simpler models for speech synthesis.

Sources:

- https://pubmed.ncbi.nlm.nih.gov/34470270/
- https://pure.tue.nl/ws/portalfiles/portal/2167417/200311316.pdf

The exact LF derivative is defined by an exponentially weighted sinusoidal open phase and an exponential return phase, with cycle length `T0 = 1/F0`.  The return phase affects spectral slope.  This gives us explicit, inspectable controls that are absent from the current smooth surrogate.

### 3. Reduced self-oscillating models are the next physical fidelity, not the first experiment

Self-oscillating two-mass / bar-mass vocal-fold models are used as voice sources in articulatory synthesis.  Their behavior depends on physically meaningful variables including glottal rest opening, vocal-fold stiffness/tension, and subglottal pressure; published evaluations measure phonation threshold, oscillation frequency range, open quotient, spectral slope, H1-H2, and related flow quantities.

Sources:

- https://doi.org/10.1016/j.specom.2019.04.009
- https://pubmed.ncbi.nlm.nih.gov/15807024/

This is a strong Fidelity-1 candidate because oscillation and F0 become outcomes of a dynamical system.  It is deliberately not selected for the first post-R1 experiment because it changes too many mechanisms at once and would make attribution difficult.

### 4. Laryngeal control should be upstream of acoustic outcomes

Human pre-phonatory laryngeal posture differs for modal, breathy, and pressed phonation, and the timing of laryngeal posturing precedes and affects phonation onset.

Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC4916049/

Gestural approaches to laryngeal contrasts likewise treat acoustic outputs such as VOT as consequences of the size and timing of a laryngeal gesture coordinated with an oral closure, rather than as the gesture itself.

Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC6768074/

Therefore canonical `PHONATE` semantics should not be `F0 = 103 Hz`.  F0 is a realized/source-control variable.  `PHONATE` should denote a functional laryngeal task/posture whose body-specific realization can involve adduction/abduction, effective tension/stiffness, and phonation regime.  `PRESSURIZE` should denote respiratory driving/pressure intent, whose physical realization may later expose subglottal pressure.

The exact canonical parameter names remain an implementation question; the architectural boundary is the research decision.

### 5. Prosody must be explicit and time-varying

Fixed F0 is a poor baseline for perceived speech naturalness.  Experimental work on synthetic speech has found F0 variation to increase naturalness ratings compared with fixed F0.  In articulatory synthesis, microprosodic F0 variations can also improve perceived naturalness in some cases even when the changes are barely audible.

Sources:

- https://pubmed.ncbi.nlm.nih.gov/31306599/
- https://pubmed.ncbi.nlm.nih.gov/34470273/

Current VocalTractLab research also treats duration, F0, and voicing as joint prosodic prediction targets, which is consistent with representing them as coordinated time-varying outputs rather than a fixed oscillator setting.

Source: https://www.vocaltractlab.de/index.php?page=birkholz-supplements

For Tokyo Japanese specifically, an accentual-phrase initial pitch rise can provide a useful word-boundary cue, while pre-boundary lengthening is also documented.

Sources:

- https://pubmed.ncbi.nlm.nih.gov/20415004/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC7988283/

This directly supports treating the user's lost "word-boundary impression" as a prosodic-control problem to test, rather than as evidence that the tract model has reached its ceiling.

### 6. Aperiodicity matters, but random jitter/shimmer is not the first control layer

Jitter, shimmer, aspiration/noise, and other deviations from perfect periodicity occur in voices.  However, perceptual work finds that listeners do not reliably isolate jitter and shimmer as independent dimensions, whereas noise/aperiodicity is more robustly perceived.  Separate work shows that combined perturbations can increase the apparent naturalness of synthesized vowels.

Sources:

- https://pubmed.ncbi.nlm.nih.gov/15898661/
- https://pubmed.ncbi.nlm.nih.gov/27777057/

Therefore random jitter/shimmer should not be introduced first as a generic "humanizer".  Macro F0/intensity/voicing trajectories and source pulse shape should be established first; microprosody and aspiration/aperiodicity can then be added as separately attributable interventions.

## Wolfram metric sanity check

A deliberately illustrative calculation compared a fixed 100 Hz sinusoidal source with the same source under a small smooth F0 contour and amplitude modulation.  This was not a physiological parameter choice; it only checked whether proposed metrics distinguish a perfectly periodic buzzer from a controlled nonstationary source.

For the fixed source:

- 10 ms lag correlation: approximately `1.0`;
- 20 ms RMS-envelope coefficient of variation: approximately `0`.

For the illustrative modulated source:

- 10 ms lag correlation: approximately `0.9871`;
- RMS-envelope coefficient of variation: approximately `0.0803`.

This supports using fixed-period lag correlation and envelope variation as auxiliary objective diagnostics in the next experiment.  They are not naturalness scores.

Wolfram's audio analysis stack also provides time-varying F0, RMS amplitude, spectral slope, spectral flux, voice activity, and speech aperiodicity descriptors that can be used as independent analysis/oracle quantities.

## Research decisions

### SOURCE_F0

Adopt an **LF-family parametric source as the first low-fidelity voice-source layer**.

- Preferred implementation direction: LF-compatible source, with LFLM considered where its parameter mapping can be independently reproduced and tested.
- Required derived controls for the experimental layer: `F0(t)`, source pulse-shape / voice-quality trajectory (`Rd` or equivalent LF timing parameters), amplitude/flow scale, voicing gate, and optional aspiration/noise amount.
- These are backend/source-control variables, not the canonical semantics of `PHONATE`.

A reduced self-oscillating two-mass/body-cover style model becomes **Fidelity 1** after the parametric-control experiment identifies which missing dimensions actually matter.

### PROSODY_REP

Use a distinct compiler-side **`ProsodyPlan` concept**, not raw acoustic samples in `GestureScore`.

`ProsodyPlan` should express performance/linguistic intent using event-aligned quantities such as:

- prominence / pitch-accent event;
- phrase/boundary event and strength;
- duration/rate modification;
- voicing intent;
- energy/effort contour intent.

The compiler may derive a backend-specific `SourceControlTrajectory` containing F0/amplitude/Rd/aspiration values.  The derived trajectory is versioned/provenanced and is not the canonical creative representation.

### LARYNGEAL_TASK_SEMANTICS

Keep `PHONATE` and `PRESSURIZE` as causal task-level concepts.

- `PHONATE`: request/initiate/sustain a laryngeal phonation regime or posture; body-specific realization maps this to glottal configuration/tension and, at Fidelity 0, to source-control parameters.
- `PRESSURIZE`: respiratory driving/pressure intent; body-specific realization maps this to subglottal driving conditions.

Do **not** redefine either task as direct waveform, fixed F0, or loudness.

### COORDINATION IMPACT

Revise #20 rather than abandon it.

The event-relation engine should remain task-agnostic.  It must be able to coordinate oral, laryngeal, and respiratory gestures.  `ProsodyPlan` remains logically separate but must share temporal anchors with the coordination compiler so that phrase/accent/boundary events can influence gesture timing and derived source controls.

Conceptually:

```text
Script / PronunciationPlan
        |
        +--> Gesture inventory ------------------+
        |                                        |
        +--> ProsodyPlan --------------------+    |
                                             v    v
                                    Coordination compiler
                                             |
                                             v
                                 task-level PerformanceScore
                          / oral / laryngeal / respiratory \
                                             |
                  +--------------------------+------------------+
                  v                          v                  v
           tract realization          source realization   pressure realization
                  \__________________________|__________________/
                                             v
                                          acoustics
```

`PerformanceScore` is a conceptual placeholder in this research document, not a committed production type name.

## NEXT_EXPERIMENT

Run **Experiment 013 — parametric source and prosody ablation** before implementing a self-oscillating vocal-fold model.

The experiment should be nested so each added layer can be attributed:

1. `smooth_fixed` — Experiment-012 low-artifact smooth periodic baseline, fixed F0.
2. `lf_fixed` — LF-family source shape, fixed F0 / amplitude / voice quality.
3. `lf_macroprosody` — same source plus explicit F0, amplitude/effort, voicing and boundary-aligned trajectories.
4. `lf_macroprosody_micro` — add microprosody and a small explicit aspiration/aperiodic component as a separate intervention.

Do not add two-mass dynamics in Experiment 013.  If conditions 2–4 remain alarm-like despite artifact-free source generation and planned trajectories, then open Experiment 014 comparing the parametric source with a reduced self-oscillating model under matched average F0/energy conditions.

## Experiment 013 measurement families

Scientific / implementation measurements:

- source continuity and derivative sharpness;
- pitch-synchronous transient metric used in Experiment 012;
- local F0 trajectory error against the planned trajectory;
- local RMS-envelope correlation/error against the planned trajectory;
- fixed-period lag correlation / periodicity;
- spectral slope and H1-H2 or equivalent source-shape diagnostics;
- spectral high-frequency/noise ratio and aperiodicity where noise is enabled;
- finite output and discretization sensitivity;
- retention of intended tract/gesture effects.

Perceptual measurements are separate:

- alarm/buzzer-like vs voice-like;
- audible clicks/snaps;
- presence of fluctuation without obvious synthetic wobble;
- detectability of the intended phrase/word-like boundary;
- retention of useful oral-coordination differences.

Do not collapse these into a single "naturalness score".  Naturalness is a broad and underspecified construct, so artifact, voice-likeness, boundary perception, intelligibility and creative usefulness should remain separate observations.

## Decision boundary

R1 is considered complete when this document is merged and Experiment 013 is separately preregistered.  No production source or laryngeal API is promoted by this research gate alone.
