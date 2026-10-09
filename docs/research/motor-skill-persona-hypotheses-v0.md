# MotorSkill / MotorPersona — Embodied Voice and Motor Learning Research Hypotheses v0

**Status:** PROPOSED / UNVALIDATED  
**Document type:** Non-normative research hypothesis note  
**Scope:** Physical speech production, reusable motor skills, habitual motor control, sensorimotor learning, perceptual individuality  
**Implementation commitment:** None  
**Date:** 2026-10-09

> This note records questions worth investigating, not confirmed results, production schemas, approved APIs, or a roadmap commitment. H1–H4 may be adopted, revised, or rejected independently.

## 1. Motivation and central question

The project treats sound as an observation of physically realized gestures, not a directly authored motor variable. Beyond differences in morphology and materials, it is worth asking whether **how a body is habitually controlled** can yield a persistent and recognizable voice identity.

**Central research question:**

> Can character-specific differences in speech arise from the interaction of physical embodiment, acquired reusable motor skills, and habitual motor strategies—and can feedback-driven practice modify those differences?

Three provisional ideas motivate the study:

1. **Skill and habit separation:** MotorSkill describes *what* task is to be achieved and its coordination constraints; MotorPersona influences *which feasible way* of achieving it is preferred.
2. **Embodiment × habit:** Voice characteristics may depend on the combination of morphology and habitual motor control, rather than being attributable to either one alone.
3. **Skill acquisition:** Feedback corrections may, through repeated attempts, improve reusable feedforward control. The DIVA model motivates this question, but this project does **not** adopt the DIVA neural architecture by implication.

All three remain hypotheses; in particular, observable changes in articulator trajectories do not establish a distinguishable voice identity.

## 2. Candidate concepts (not schemas)

### 2.1 MotorSkill — reusable speech motor skill

A *candidate* higher-level concept expressing a reusable, task-oriented speech action. Possible elements:

- task-space goals and tolerances;
- required gesture capabilities, gesture identities, and inter-gesture coordination;
- relative temporal/semantic anchor relations, where supported;
- initiation/termination conditions and relevant context;
- candidate control rules or learned body-specific realizations;
- feasibility and validation evidence.

Potential granularities include primitive actions, coordinated transitions, syllable-like chunks, words, or utterance-scale skills. No granularity is assumed privileged. A library of merely concatenated waveforms or frozen body-coordinate trajectories would not by itself satisfy the intended reusable task-level semantics.

Distinguish **Skill Definition** (portable goal and coordination semantics) from **Skill Binding** (a versioned body/controller-specific learned realization or cache) and **Motor Experience** (individual trials, traces, failures, observations, evaluations). These are conceptual roles, not committed storage objects.

### 2.2 MotorPersona — habitual motor-control tendencies

A *candidate* description of a speaker's recurring preferences or control strategy when multiple task realizations are possible. Possibilities include:

- overlap and anticipatory coordination preferences;
- preferred allocation of effort among articulators;
- response speed, damping, precision and release habits;
- habitual breath and phonation coordination;
- feedback gains, adaptation rates, variability and repeatability;
- context-dependent strategy choice.

This concept is **not** a creative personality label, a direct waveform/style code, or a mandate for fixed acoustic parameters. The existence, separability, controllability, and acoustic significance of the proposed dimensions are open questions.

Do not equate CharacterSpec (creative identity), selected body/morphology, MotorPersona (habitual strategy), and Direction (transient acting intent).

### 2.3 Motor Experience — trial and learning evidence

Candidate trial data include the intended Skill, frozen body/solver/controller versions, experimental manipulation, initial physical state, deterministic seed, physical controls and traces, relevant sensory signals, task outcomes, audio observations, independent listening judgments, and failure/diagnostic categories. Learned changes must be linked to the experiences that caused them.

An audio recording or one successful trajectory does not by itself establish a reusable skill or a persistent persona.

## 3. Research hypotheses

### H1 — Motor equivalence permits habitual selection

For a fixed supported morphology and task, more than one feasible motor strategy may exist. Different habitual preferences may select different trajectories or control allocations while satisfying the same task.

**Prediction:** With body, task, initial conditions, solver, and transient direction fixed, experimentally varied habitual-control candidates can yield repeatable differences in physically executed trajectories.

**Important limit:** Kinematic differences may be acoustically neutral. Distinguishable *character voice identity* is a separate perceptual claim requiring separate testing.

### H2 — Embodiment × MotorPersona interaction

Acoustic/physical outcomes may depend non-additively on embodiment and habitual strategy. The effect of a persona intervention may differ from one body to another.

**Prediction:** A factorial body × habit experiment yields an interaction in at least some prespecified physical or acoustic measures, and potentially in perceptual identity ratings.

**Alternative:** Only body effects, only habit effects, or no reliable interaction. These are valid findings, not failures to be explained away.

### H3 — Feedback-guided acquisition of feedforward control

Sensory/task errors during a trial may support correction during that trial and adjustment of a reusable feedforward controller on later trials.

The DIVA model integrates feedforward control with auditory and somatosensory feedback and motivates sensorimotor learning. We borrow the **research question and high-level control distinction**, not DIVA's exact architecture, biological claims, or learning equations.

Distinguish:

1. **Within-trial feedback correction**;
2. **Across-trial skill adaptation**;
3. **Generalization across skills or contexts**, which alone could justify a stronger claim about changed habitual motor strategy.

**Prediction:** Compared with a frozen/untrained control, a learned controller improves a prespecified task metric under controlled initial conditions; improvements persist when online feedback corrections are reduced or removed within a declared safe experimental regime.

### H4 — Skill reuse and transfer

A learned task-level skill may be reused with lower planning or relearning costs across compatible phonetic contexts or morphologies.

**Prediction:** A preserved Skill Definition, adapted by a body-specific binding stage, reaches a criterion with fewer trials or lower optimization cost than an appropriate from-scratch baseline, without quietly altering the intended task.

**Alternative:** The skill is too context-dependent or body-specific to confer measurable benefit; the scope of transfer should then be narrowed.

## 4. Candidate mathematics (illustrative, not adopted)

Let M denote morphology and material/actuator capabilities, S the task/skill goal, H the habitual motor strategy, D transient direction, x(t) physical state, u(t) control, and y(t) the observed acoustic output.

A conceptual causal relation is:

    (S, H, D, M, x0) -> feasible control and coordination
                      -> physical dynamics x(t)
                      -> acoustics y(t)
                      -> analysis / perception

One *candidate* realization model is:

\[
\dot{x}(t)=F(x(t),u(t);M,\theta), \quad
r_S(t)\approx h_M(x(t))
\]

\[
\pi^\star \in
\arg\min_{\pi\in\Pi_{\mathrm{feasible}}(M,S)}
J(\pi;S,M,H,D)
\]

where \(\Pi_{\mathrm{feasible}}\) is constrained by anatomy, actuation, contact, dynamics, and supported backend capabilities. Preferences in J might weight effort, smoothness, coordination, precision, or comfortable states. This is **one hypothesis family**: task dynamics, explicit controllers, dynamical movement primitives, constrained optimization, probabilistic policies, and hybrid/event-driven models remain alternatives.

**Factorial interaction check:** For a prespecified scalar observation Q measured under two bodies M1/M2 and two habits H1/H2,

\[
\Delta_{\mathrm{int}}=
Q(M_2,H_2)-Q(M_2,H_1)-Q(M_1,H_2)+Q(M_1,H_1).
\]

As a toy example, if \(Q(M,H)=aM+bH+kMH\), then

\[
\Delta_{\mathrm{int}}=k(M_2-M_1)(H_2-H_1).
\]

A nonzero result in one scalar physical feature does **not** by itself establish acoustic or perceptual character individuality; incompatible/failed conditions must not be forced into this arithmetic.

**Minimal trial-learning thought experiment:** Separate online feedback action from a reusable feedforward command:

\[
u_n(t)=u^{FF}_n(t)+u^{FB}_n(t),
\quad
u^{FF}_{n+1}(t)=u^{FF}_n(t)+\eta u^{FB}_n(t).
\]

This is a deliberately simplified candidate, **not the DIVA model's learning equation**. Under an additional scalar linearization, an example error process is

\[
e_{n+1}=(1-\eta g)e_n.
\]

For real positive gains \(\eta,g\), this toy recursion contracts if \(0<\eta g<2\). General nonlinear physical speech dynamics, delays, actuator saturation, partial observability, and noisy sensory signals require separate analysis. This relation is not evidence that a specific physical model will learn.

## 5. Candidate experiments and evidence gates

| ID | Intervention | Outcome/evidence | What it cannot prove alone |
| --- | --- | --- | --- |
| E1 | Same body, Skill, Direction; change H only | Feasible-state/trajectory, effort, acoustic and blind listening differences | Changed trajectory does not prove speaker identity |
| E2 | Same Skill and H; change M only | Preserved task meaning, feasible vs infeasible realization, physical/acoustic change | Acoustic difference does not establish portable H |
| E3 | Cross M1/M2 × H1/H2 under comparable conditions | Preregistered interaction contrasts on separate physical, acoustic, perceptual measures | Significant interaction alone does not prove naturalness or character appeal |
| E4 | Repeat one Skill with feedback-based adaptation vs frozen controller | Retained improvement; changes to feedforward control | A single learned skill does not prove global MotorPersona change |
| E5 | Transfer or retain learned skills in new context/body | Success, additional trials/cost, retention, clear capability gates | No general transfer if only a near-identical fixture works |

**Controls and threats to inference:**

- Freeze body revisions, task interpretation, solver fidelity, controller version, initial state and stochastic seed as appropriate.
- Distinguish articulation/coordination, phonation/source, prosodic timing, waveform/acoustic features, and listener judgments.
- Pace/gain-only changes may enable trivial auditory classification; test whether identity generalizes when these are controlled.
- If a body lacks required degrees of freedom or the solver cannot express the phenomenon, record **UNSUPPORTED** rather than falsely rejecting the hypothesis.
- Treat valid but physically impossible tasks as **INFEASIBLE**; malformed plans as **INVALID**.
- Include negative controls and repeated trials, with predeclared metrics before claiming an identifiable motor habit or learning effect.
- Record the distinction between a physically detectable difference, perceptual discrimination, stable character attribution, and subjective preference.

**Decision vocabulary:** Independently assess H1–H4/E1–E5 as ADOPT (within demonstrated scope), REVISE, REJECT, or MORE_DATA. ADOPT never implies a universally valid voice-personality model.

## 6. Open design questions

1. Which portion of a skill is transferable without access to a particular body's actuator coordinates?
2. Which controller properties are identifiable as persistent habit rather than task/context effects?
3. Are persona preferences better represented by objective-function weights, dynamical parameters, coordination constraints, learned policies, or mixtures?
4. What sensory information is required for feedback learning (auditory, somatosensory, task-space)?
5. How do learning of a particular Skill and modification of a general MotorPersona differ operationally?
6. What is the minimum physical fidelity and source/tract coupling needed before a perceived-identity hypothesis is fairly testable?
7. Which differences remain reliably perceptible after controlling for F0, duration, loudness, and morphology?
8. What should be cached and versioned to avoid invalidating learned Skill Bindings after body/solver/controller changes?

## 7. Architectural boundaries and dependencies

- Retain the physical causal contract: morphology + task-level gesture/coordination -> physical realization -> acoustics -> observations.
- Do not put motor persona labels, waveforms, raw formant trajectories, solver indices, or emotional UI controls into the universal physical Gesture/GestureScore schema.
- Candidate MotorSkill and MotorPersona abstractions belong conceptually above physical realization; they are **not** approved production interfaces.
- Preserve task semantics across bodies; body-specific realizers may differ or return explicit failure.
- Keep the present compiler-local [shared timeline candidate](shared-timeline-candidate-v1.md) experimental; do not assert phase oscillator or general coarticulation support.
- Separate creative CharacterSpec, embodiment selection, H, and transient Direction. Creator-facing energy/emotion must not map directly to actuator forces or F0 without a justified translation.
- No requirement for neural networks, machine learning data pipelines, new Studio UI, universal speech recognition, or high-fidelity 3D mechanics follows from this note.
- Defer implementation Issues until experiments have a tractable backend capability and narrowly scoped hypotheses. This research note can be cited from Studio's Character Creator epic without creating a Studio production contract.

## 8. Related project work

- [Core architecture](../architecture.md), [invariants](../invariants.md), [Performance Contract v0](../performance-contract-v0.md).
- [Shared timeline candidate v1](shared-timeline-candidate-v1.md), [CoordinationPlan experiment #20](https://github.com/ryonakayama234/morphoacoustics/issues/20).
- [Longer continuous gesture pilot #74](https://github.com/ryonakayama234/morphoacoustics/issues/74), [voice quality interventions #71](https://github.com/ryonakayama234/morphoacoustics/issues/71).
- [Studio Character Creator epic #12](https://github.com/ryonakayama234/morphoacoustics-studio/issues/12): MotorPersona is explicitly a proposed concept there, not a frozen API.

## 9. Literature and attribution

The sources below motivate candidate ideas; they do **not** validate H1–H4 for this project.

- Tourville, J. A., & Guenther, F. H. (2011). *The DIVA model: A neural theory of speech acquisition and production.* Language and Cognitive Processes, 26(7), 952–981. https://pmc.ncbi.nlm.nih.gov/articles/PMC3650855/  
  Source for the actual DIVA feedforward/feedback learning architecture and motor equivalence discussion.
- Parrell, B., & Houde, J. (2019). *Modeling the Role of Sensory Feedback in Speech Motor Control and Learning.* Journal of Speech, Language, and Hearing Research, 62(8 Suppl), 2963–2985. https://pmc.ncbi.nlm.nih.gov/articles/PMC6813034/  
  Review comparing DIVA, FACTS and the respective roles of online feedback versus longer-term learning.
- [Guenther Speech Neuroscience Lab — DIVA model overview](https://sites.bu.edu/guentherlab/research-projects/the-diva-model-of-speech-motor-control/).  
  Primary lab description of DIVA as a **neural network** model of speech acquisition and production.

**This is an exploratory research record, not an implementation specification or an assertion of established speaker-identity mechanisms.**
