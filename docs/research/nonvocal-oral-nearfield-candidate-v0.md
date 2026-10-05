# Non-vocal oral acoustics / near-field receiver candidate v0

Issue: #53

## Purpose

This document records a research candidate for extending `morphoacoustics` beyond voiced speech without changing the project's causal contract.

The candidate asks one architectural question:

> Can non-vocal oral sound events and very-near-field receiving be represented as additional physical source / propagation / receiver paths while keeping waveform, binaural presentation, and creative UI downstream from task-level motor intent and physical realization?

The intended extension is:

~~~text
Morphology + task-level motor program
                ↓
        physical realization
                ↓
       physical event / source
                ↓
       acoustic field / propagation
                ↓
          receiver transfer
                ↓
        acoustic observation

parallel physical observables:
airflow / temperature / humidity / contact / wetness
                ↓
       non-acoustic observation
~~~

This is deliberately **not** a production `WET_CONTACT`, HRTF, saliva, or multimodal API.

## Why this belongs in docs/research

The current architecture already treats the domain schema as broader than any one backend and requires unsupported capabilities to remain explicit rather than being silently erased.

This candidate is earlier than a validated backend capability. It therefore belongs in `docs/research/` until at least one narrow experiment establishes a useful, falsifiable model boundary.

The document may evolve, be split, or be rejected without forcing changes to:

- `CreatureSpec`;
- canonical `Gesture` / `GestureScore`;
- `PreparedMorphology`;
- the Performance Contract;
- Studio-facing controls.

## Existing causal contract remains unchanged

The existing five-layer model remains authoritative:

1. morphology;
2. task / motor program;
3. physical state;
4. acoustic field;
5. observation.

This candidate does not add "ASMR" as a sixth causal layer.

Instead, it broadens what may occur inside physical state and acoustic source generation.

~~~text
task intent
   ↓
body-specific physical state
   ├─ vocal-fold oscillation
   ├─ respiratory jet
   ├─ dry contact
   ├─ wet contact
   ├─ suction / release
   └─ other supported physical events
          ↓
   acoustic source(s)
          ↓
   propagation / radiation
          ↓
   receiver
          ↓
   observation
~~~

## Candidate source classes

The following names are **research vocabulary**, not production enum values.

### Phonation source

Existing vocal-source path.

Possible physical causes include:

- vocal-fold oscillation;
- glottal flow modulation;
- source-filter coupling at higher fidelity.

### Turbulent breath source

Aperiodic aerodynamic sound associated with respiratory flow.

This overlaps conceptually with the aspiration / aperiodicity work in #30 and should not create a duplicate production path unless experiments distinguish the required source placement or control semantics.

Candidate state may eventually depend on quantities such as:

~~~text
flow
jet velocity
opening geometry
pressure drop
source location
spectral shaping implied by the physical approximation
~~~

The canonical motor representation must not directly encode a target noise spectrum.

### Dry contact / release source

Transient sound associated with collision, friction, sticking, sliding, or release between oral surfaces.

Candidate examples:

~~~text
tongue ↔ palate
tongue ↔ teeth
lip ↔ lip
lip ↔ skin / external surface
~~~

Research variables may include contact force, relative velocity, effective stiffness, damping, contact area, and surface state.

### Wet contact / suction / release source

A candidate class for liquid-mediated contact phenomena.

Potential explanatory variables include:

~~~text
wetted area
film thickness
effective viscosity
adhesion
surface tension
normal force
tangential velocity
sealed volume
pressure drop
release velocity
~~~

These are **candidate physical variables only**.

This document does not assert that a reduced model containing these variables is sufficient, nor does it select a constitutive law, multiphase-flow model, or CFD method.

### Film / breakup micro-events

Saliva-film stretching, bridge rupture, bubble or microcavity events may contribute stochastic transients.

They should not be represented as arbitrary "wet sound samples" in the canonical motor path.

If a reduced stochastic model is later adopted, it should be conditioned by physical state and remain inspectable as a closure / unresolved-physics model.

## Event semantics versus source semantics

A task-level event is not itself an audio generator.

For example:

~~~text
CONTACT(...)
SLIDE(...)
SUCTION(...)
RELEASE(...)
AIRFLOW(...)
~~~

would describe attempted physical actions or task constraints.

The body / material / fluid approximation determines what physical event actually occurs.

Only then may an acoustic backend construct one or more acoustic sources.

Therefore:

~~~text
Gesture
  !=
sound effect trigger
~~~

and:

~~~text
WET_CONTACT task
  !=
play "wet_contact.wav"
~~~

This preserves the project invariant that the physical causal path cannot be bypassed.

## Propagation remains separate from source generation

Source generation and acoustic propagation must remain separate concerns.

A source may be represented at different fidelity levels as, for example:

- an equivalent monopole / dipole;
- a boundary pressure or normal-velocity source;
- a distributed source patch;
- a local field extracted from a higher-fidelity coupled simulation.

Propagation may independently vary in fidelity:

- reduced cavity / transmission-line model;
- loss / radiation model;
- multimodal or 3D acoustics;
- local near-field model;
- higher-fidelity FEM validation.

This separation is consistent with standard computational-acoustics formulations in which source terms / source boundary conditions and propagation-domain boundary conditions are modeled independently.

Wolfram references:

- Acoustic PDE overview: https://reference.wolfram.com/language/guide/AcousticPDEModels.html
- `AcousticPressureCondition`: https://reference.wolfram.com/language/ref/AcousticPressureCondition.html
- `AcousticNormalVelocityValue`: https://reference.wolfram.com/language/ref/AcousticNormalVelocityValue.html
- `AcousticRadiationValue`: https://reference.wolfram.com/language/ref/AcousticRadiationValue.html
- `AcousticImpedanceValue`: https://reference.wolfram.com/language/ref/AcousticImpedanceValue.html

The purpose of these references is architectural: they support keeping sources, propagation, and boundaries distinct. They do not validate a specific wet-contact model.

## Near-field receiver candidate

The receiver must be modeled separately from the source-producing creature.

Candidate receiver-side concepts include:

~~~text
Receiver
├─ pose
├─ left / right observation positions
├─ head geometry or reduced transfer model
├─ pinna transfer
├─ ear-canal transfer
├─ source distance
└─ receiver / renderer provenance
~~~

A general conceptual transfer is:

~~~text
source field
   ↓
relative source / receiver geometry
   ↓
near-field transfer
   ↓
head / pinna / ear-canal transfer
   ↓
left / right acoustic observation
~~~

A future reduced binaural model may use an HRTF/HRIR-like transfer representation. This document does not yet establish:

- a specific HRTF dataset format;
- far-field versus near-field interpolation rules;
- SOFA as a production dependency;
- personalized versus generic HRTF;
- ear-canal termination details.

Those require separate evidence and implementation work.

## Distributed sources

Very-close oral/contact events should not be assumed to be point sources in the universal model.

A tongue or contact patch may occupy a spatially extended area.

The conceptual receiver observation may therefore be written as a distributed-source integral:

~~~text
p_receiver(t)
  = integral_over_source_surface(
      transfer(source_position, receiver_state)
      * local_source(source_position, t)
    )
~~~

A low-fidelity backend may approximate this with one or several source patches.

The approximation level belongs to the backend, not to the canonical task representation.

## Kernel ownership versus execution location

This boundary is important.

### Kernel / scientific-model ownership

The scientific meaning of:

- source state;
- source geometry;
- propagation assumptions;
- receiver semantics;
- coordinate frames;
- provenance;
- supported / unsupported capability;

must not be redefined by the creative UI.

### Studio / Web execution

A realtime binaural renderer may eventually execute in `morphoacoustics-studio` or another client for latency and interaction reasons.

For example:

~~~text
kernel / backend
   ↓
versioned receiver-ready artifact or source-field representation
   ↓
Studio / Web renderer
   ↓
head-tracked convolution / binaural presentation
~~~

Execution in the Web layer does **not** make the Web layer the owner of the physical semantics.

The site should consume a stable receiver/rendering contract rather than invent its own body or acoustic model.

## Acoustic and non-acoustic observables

"Warm", "wet", or "breath on skin" are not purely acoustic quantities.

The physical simulation may eventually expose multiple observables:

~~~text
EmbodiedObservation
├─ acoustic pressure / waveform
├─ airflow velocity
├─ temperature
├─ humidity
├─ contact pressure
└─ surface wetness
~~~

Only the acoustic branch is directly renderable as audio.

Therefore the system must not claim:

~~~text
temperature == audio parameter
humidity == audio parameter
wetness == HRTF parameter
~~~

A future multimodal application could consume the other observables using separate renderers or hardware.

The immediate value of preserving the distinction is scientific even if no such hardware exists: it prevents an audio renderer from pretending to reproduce a non-acoustic sensation.

## Candidate invariants

This research track should preserve the following invariants.

1. **Motor intent does not directly specify waveform samples.**
2. **A non-vocal task is not an audio sample trigger.**
3. **Wet-contact parameters belong to physical state / material / closure models, not to linguistic or creative labels by default.**
4. **Source generation and propagation remain separable backend responsibilities.**
5. **Receiver semantics are distinct from source morphology.**
6. **Web/Studio may execute rendering but must not silently redefine scientific receiver assumptions.**
7. **Non-acoustic observables are not collapsed into audio parameters.**
8. **Unsupported source or receiver capability remains explicit.**
9. **A neural residual, if later used, must be conditioned by physical state and must not restore events the physical path says did not occur.**
10. **No production schema is promoted solely from this document.**

## Relationship to current work

### #30 — aspiration / aperiodicity

The turbulent-breath branch may reuse or extend #30.

Before creating a new turbulent-noise production path, compare:

- source placement;
- flow gating;
- spectral shaping;
- required physical state;
- downstream radiation behavior.

### #27 — roadmap discipline

This candidate follows the existing rule:

> do not freeze unvalidated downstream capability into a production API.

### #20 / shared timeline

Future non-vocal tasks may require temporal coordination with speech or other gestures.

For example:

~~~text
PHONATE
AIRFLOW
CONTACT
SLIDE
RELEASE
~~~

may overlap on one shared timeline.

This document does not modify `CoordinationPlan` or `GestureScore`; it only keeps that future compatibility open.

### Tissue / material research

Wet and dry contact may eventually require material state beyond geometry.

This is compatible with the broader morphology view in which geometry, material distribution, actuator distribution, and solver fidelity are distinct concerns.

## Proposed downstream research sequence

These are candidate research tracks, not pre-created production issues.

### NV1 — turbulent breath source

Question:

> Can respiratory-flow state generate a controlled aperiodic source whose downstream behavior is distinguishable from arbitrary inlet white noise?

Prefer reuse / extension of #30 if possible.

### NV2 — dry contact / release transient

Question:

> Can a minimal contact state produce a reproducible transient whose timing and magnitude follow physical contact intervention rather than an audio trigger?

### NV3 — reduced wet-contact model

Question:

> Holding geometry and motion fixed, does a reduced liquid/contact state produce falsifiable acoustic differences under controlled parameter intervention?

Do not begin with full saliva CFD unless reduced models fail a concrete gate.

### NV4 — near-field receiver

Question:

> Holding the source event fixed, does changing receiver distance / orientation produce predictable receiver-side acoustic differences without changing source generation?

This is the first place to compare point-source and distributed-source approximations.

### NV5 — Studio binaural renderer

Question:

> Can a versioned receiver-ready output be rendered interactively in Studio/Web without moving scientific source/receiver ownership into the UI?

Only validated receiver semantics should become creator-facing controls.

## What should be measured

Future experiments should prefer intervention-based evidence.

Examples:

~~~text
source intervention:
  same gesture / body
  change contact state
  -> source / acoustic difference

receiver intervention:
  same source event
  change receiver pose / distance
  -> receiver observation difference

modality separation:
  same acoustic output
  change non-acoustic state
  -> audio path must not fabricate a difference unless acoustics actually change
~~~

Useful artifact classes may include:

- physical event trace;
- source-state trace;
- source position / patch trace;
- pressure / flow trace;
- receiver pose;
- transfer / rendering provenance;
- left/right waveform;
- spectral / transient diagnostics;
- explicit unsupported / invalid outcomes.

## Explicit non-goals

This candidate does not implement or establish:

- production `WET_CONTACT` / `SUCTION` / `SALIVA_FILM` enums;
- a saliva constitutive law;
- full multiphase CFD;
- tongue-surface FEM;
- a production near-field HRTF model;
- SOFA integration;
- personalized HRTF capture;
- WebAudio or AudioWorklet implementation;
- haptic / thermal hardware;
- an erotic/ASMR naturalness metric;
- a new Performance Contract field;
- a new Studio control;
- a claim that audio alone reproduces heat, humidity, or physical wetness.

## Promotion gate

No concept in this document should be promoted to a stable universal or creative API merely because it is useful vocabulary.

Promotion requires at least:

1. a narrow preregistered experiment;
2. an explicit null / comparison model;
3. measurable physical or acoustic consequences;
4. failure classes;
5. independent or analytic verification where practical;
6. a bounded statement of what the result supports;
7. evidence that the representation is not experiment-specific.

## Completion claim for R-NV0

If this candidate is accepted, the supported claim is only:

> The existing morphoacoustics causal architecture can be extended coherently to represent future non-vocal oral sources and near-field receiver models while preserving the separation between task intent, physical realization, acoustic propagation, receiver transfer, and observation.

It does **not** establish that:

- wet-contact audio has been reproduced;
- saliva physics is solved;
- near-field HRTF is validated;
- ASMR quality is natural;
- thermal / humidity sensations can be produced by audio.

## Next decision

After review of this candidate, choose **one** narrow next intervention rather than implementing the entire stack.

Current preference:

~~~text
#30-compatible turbulent breath work
        OR
NV2 dry-contact transient
~~~

before wet-contact or near-field binaural production work.

The objective is to add one new physical source mechanism at a time and preserve the project's existing discipline of separating numerical validity, physical interpretation, perception, and creative usefulness.
