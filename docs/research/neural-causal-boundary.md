# Neural components and the physical causal boundary

Status: **provisional architectural research decision**

This document records how neural models may participate in `morphoacoustics` without weakening the project's central claim: sound is an observable consequence of a body-specific physical causal process.

The short form is:

> **Neural models propose, infer, approximate, and complete.  
> The embodied physical system determines what sound can actually occur.**

This document is the research rationale. Stable conclusions are summarized in `docs/architecture.md` and enforced as invariants in `docs/invariants.md`.

---

## 1. Core causal authority

The project keeps the following path authoritative:

~~~text
Morphology + Material + Task-level Motor Intent
                    ↓
          Physical Realization
                    ↓
      Airflow / Source / Acoustics
                    ↓
          Physical Observation
                    ↓
               Analysis
~~~

A neural component may exist around or inside this graph, but it must not silently replace the graph with direct intent-to-audio generation while the system still claims an embodied physical explanation.

The key distinction is:

~~~text
Neural: what to attempt, infer, approximate, or fill in
Body:   what actually happens
~~~

If a requested task is physically unrealizable for a morphology, a downstream neural component must not repair it into a plausible utterance.

---

## 2. Why a generic neural post-processor is not enough

A large waveform model placed after the simulator can improve naturalness while destroying the scientific meaning of the result.

For example:

~~~text
physics
  ↓
rough / imperfect waveform
  ↓
large neural vocoder
  ↓
natural-looking speech
~~~

is unsafe as the default architecture if the vocoder can:

- restore a phoneme that the body failed to realize;
- pull morphology-dependent formants back toward a training-set norm;
- erase source-filter bifurcations or body-specific failure modes;
- inject linguistic information that was absent from the physical observation.

The project therefore treats "neural color" more narrowly:

> **learned components may model unresolved physical detail or bounded perceptual microstructure, but they do not get authority to reinterpret the body.**

This motivates the role taxonomy below.

---

## 3. Role taxonomy

| Location | Neural role | Architectural status |
|---|---|---|
| Script / intent -> Gesture | pronunciation, prosody, timing, overlap, task proposal | allowed and useful |
| Observation -> latent causes | inverse inference / posterior proposal | allowed and useful |
| Inside a physical subsystem | learned closure for unresolved constitutive / loss / contact / turbulence terms | allowed with explicit scope |
| High-fidelity solver replacement | validated surrogate / reduced-order approximation | allowed inside a declared trust region |
| Physical waveform -> final waveform | bounded stochastic microtexture / unresolved detail | allowed only if causal content is preserved |
| Perception / preference | naturalness, identity, "cute", realism, task-specific perceptual objective | evaluator outside causal authority |
| Text -> waveform | end-to-end speech generation | not the physical simulator |

---

## 4. Neural motor planner

A neural planner may propose a `GesturalScore` or a compiler-side coordination plan from linguistic and expressive intent.

Conceptually:

[
p(G mid 	ext{text}, 	ext{prosody}, 	ext{rate}, 	ext{intent}, M)
]

where (G) contains task-level structures such as:

- gesture selection;
- targets;
- duration;
- stiffness or activation strength;
- inter-gesture phase relationships;
- overlap;
- prosodic modulation.

The planner does **not** generate the waveform.

~~~text
Text / intent / prosody
          ↓
    Neural Planner
          ↓
     GesturalScore
          ↓
 Physical Controller
          ↓
      Physics
~~~

Body capability remains authoritative. A planner may ask for an impossible task; the realizer may return `INFEASIBLE`.

This is consistent with the existing distinction between reusable task-level Gesture semantics and body-specific realization.

---

## 5. Neural inverse estimator

Inverse inference is one of the strongest uses of learned models because observation-to-cause mapping is generally non-unique.

Instead of forcing a single reconstruction

[
y(t) ightarrow hat{x}(t),
]

the preferred model is a proposal distribution such as

[
q_phi(G, M, 	heta mid y, v, ldots),
]

where observations may include audio, video, EMA, pressure traces, or other measurements.

Candidate latent causes are then tested by forward simulation:

~~~text
real observations
      ↓
neural inverse estimator
      ↓
candidate Gesture / Morphology / Material
      ↓
physics
      ↓
resynthesis / predicted observations
      ↓
comparison
~~~

The neural model proposes explanations; the forward physical model evaluates whether those explanations actually reproduce the observations.

This is an analysis-by-synthesis workflow, not a claim that the inferred latent state is uniquely "the true motion".

---

## 6. Learned closure inside physical dynamics

A learned component may model a term that is known to be missing from an otherwise mechanistic subsystem.

If a coarse physical model is

[
dot{x}=F_{mathrm{phys}}(x,u;M,	heta),
]

a bounded learned closure may take the form

[
dot{x}
=
F_{mathrm{phys}}(x,u;M,	heta)
+
R_phi(x,u,M,	heta).
]

The important property is decomposition:

- (F_{mathrm{phys}}) is the explicit known model;
- (R_phi) represents a declared unresolved term;
- training and validation target that term or the subsystem behavior it affects;
- the learned term does not silently absorb unrelated causal structure.

Candidate future closures include:

~~~text
vocal-fold dynamics
    = coarse biomechanics + learned contact / loss residual

wall impedance
    = analytic / parametric impedance + learned tissue residual

turbulent source
    = coarse deterministic/stochastic model + learned unresolved spectrum
~~~

Small subsystem-local models are preferred over one global network that can compensate for arbitrary upstream errors.

This is closely related to gray-box / Universal Differential Equation style modeling, where known mechanistic dynamics and trainable unknown terms coexist in one dynamical system.

---

## 7. Physics surrogate / reduced-order model

High-fidelity FEM, FSI, or 3D acoustics may be too expensive for repeated design search, inverse inference, or interactive use.

A learned surrogate may approximate a high-fidelity solver:

[
mathcal{S}_{HF}(M,x,u)
longrightarrow
hat{mathcal{S}}_phi(M,x,u).
]

The surrogate is not a license to extrapolate arbitrarily.

Every surrogate should declare:

- training / calibration domain;
- validated parameter ranges;
- error metrics;
- out-of-domain detection or confidence rule;
- fallback behavior.

Preferred behavior:

~~~text
inside validated trust region
    → surrogate

outside validated trust region
    → higher-fidelity solver / explicit unsupported status
~~~

This is particularly important for hypothetical creatures, where a human-trained surrogate can otherwise hallucinate familiar human-like behavior.

Wolfram Language provides the same general systems-modeling pattern through `SystemModelSurrogateTrain`: a system model is sampled over declared inputs and parameter ranges, then approximated by a faster surrogate focused on selected outputs.

Reference:
- https://reference.wolfram.com/language/ref/SystemModelSurrogateTrain.html

---

## 8. Neural microtexture renderer

A final neural renderer may add detail that the coarse physical simulator intentionally does not resolve.

Possible residual dimensions include:

- aspiration microstructure;
- microturbulence;
- jitter / shimmer;
- fine tissue-loss behavior;
- contact noise;
- stochastic cycle-to-cycle variation.

A conservative form is

[
y(t)
=
y_{mathrm{phys}}(t)
+
R_phi(
x_{mathrm{phys}},
	ext{source state},
	ext{pressure},
	ext{flow},
	ext{contact},
M,	heta,epsilon
),
]

where (epsilon) is a stochastic latent.

The renderer must not recreate the high-level speech act.

The physical path should already determine:

- task success or infeasibility;
- timing;
- morphology-dependent resonance structure;
- source regime;
- major source-filter interaction;
- major phonetic consequences.

The neural residual may make the result less sterile, but it must not become the hidden primary synthesizer.

---

## 9. Perceptual evaluator is outside the causal simulator

Perceptual objectives such as:

- naturalness;
- realism;
- identity similarity;
- cuteness;
- breathiness preference;
- creator preference;

may be neural.

But they are evaluators:

[
C(y)
]

not causal state.

They can drive search over morphology, gesture, controller, or renderer parameters, but an optimization target must not be confused with a physical explanation.

A useful pattern is:

~~~text
candidate body + task
        ↓
      physics
        ↓
   final observation
        ↓
perceptual evaluator
        ↓
search / selection
~~~

---

## 10. Voice identity decomposition

A generic speaker embedding should not automatically be treated as the cause of voice identity.

The preferred decomposition is:

~~~text
Voice identity
   ↓
Morphology parameters
Material parameters
Source-organ parameters
Habitual motor strategy
Prosodic tendencies
Residual unexplained identity latent
~~~

The residual identity latent should be the remainder after explainable physical and behavioral variables have been represented.

This makes "identity" an interpretable combination of body, source, habit, and only then unresolved learned variation.

---

## 11. Causal budget

A learned residual needs an explicit **causal budget**: limits on how much semantic or morphology-dependent structure it is allowed to overwrite.

The exact numerical form is an open research question, but the architecture requires that the budget be testable.

Candidate controls include:

- explicit residual gain or norm limits;
- spectral / temporal bandwidth limits;
- mutual-information or ASR leakage tests;
- morphology-intervention preservation tests;
- task-infeasibility preservation tests;
- source-regime preservation tests;
- ablation with neural components disabled.

A residual is suspicious if its standalone output carries the utterance or if the final output loses known physical intervention effects.

---

## 12. Falsification suite

Any learned component that touches the causal path should eventually face the following tests.

### N0 — Neural OFF

Disable the learned component.

Expected:

- fidelity / naturalness may decrease;
- the causal interpretation of the body's action remains;
- task success, infeasibility, and major morphology effects do not reverse.

Failure signal:

- without the neural model the intended phoneme or body consequence disappears entirely.

### N1 — Residual-only leakage

Listen to or analyze the learned residual in isolation.

Expected:

- mostly texture, noise, unresolved detail.

Failure signal:

- ASR can recover the utterance reliably;
- intelligible segmental structure is present;
- speaker or phoneme identity lives primarily in the residual.

### N2 — Morphology intervention preservation

Change one morphology axis while holding task semantics fixed.

Expected:

- preregistered physical/acoustic consequences remain visible after the neural stage.

Failure signal:

- the learned component normalizes the result back toward the training distribution.

### N3 — Infeasible-task preservation

Provide a valid, supported task that is `INFEASIBLE` for one morphology.

Expected:

- no plausible acoustic repair is generated.

Failure signal:

- the neural stage produces the intended utterance anyway.

### N4 — Source / coupling intervention preservation

Change a declared source or source-filter coupling condition.

Expected:

- corresponding phonation-regime differences remain detectable.

Failure signal:

- the learned stage collapses materially different physical regimes to similar output.

### N5 — Out-of-domain morphology

Evaluate a morphology outside the surrogate / renderer validation domain.

Expected:

- low confidence, fallback, `UNSUPPORTED`, or higher-fidelity evaluation.

Failure signal:

- confident human-like extrapolation without evidence.

---

## 13. Relationship to DDSP

DDSP is useful primarily as an interface-design precedent.

The library exposes differentiable signal processors whose controls remain meaningful, for example:

~~~text
neural network
    ↓
F0 / amplitudes / harmonic distribution / filter controls
    ↓
known differentiable signal processor
    ↓
audio
~~~

That is preferable to an opaque direct waveform layer when interpretable controls matter.

For `morphoacoustics`, the analogous principle is stronger:

> learned modules should emit or refine physically meaningful controls and residuals wherever practical, while the embodied simulator retains causal authority.

References:
- https://github.com/magenta/ddsp
- https://arxiv.org/abs/2001.04643

An articulatory DDSP vocoder also demonstrates that articulatory trajectories plus F0/loudness can drive a compact learned differentiable renderer:
- https://github.com/Louis0324/DDSP-Articulatory-Vocoder
- https://arxiv.org/abs/2409.02451

This is evidence for the feasibility of a grounded learned renderer, not evidence that the renderer should replace body mechanics.

---

## 14. Accepted constraints, candidate mechanisms, open questions

### Accepted architectural constraints

These may be promoted into stable architecture / invariants now:

1. Neural components do not bypass embodied causality.
2. Physical infeasibility must survive downstream learned stages.
3. Morphology-dependent causal consequences must not be silently normalized away.
4. Learned surrogate validity is domain-bounded.
5. Observations and perceptual scores remain downstream of physical/task state.
6. Turning neural components off may reduce quality but must not reinterpret what the body physically did.

### Candidate mechanisms

These are promising but remain research choices:

- neural motor planner;
- inverse posterior estimator;
- subsystem-local learned closure;
- high-fidelity surrogate;
- neural microtexture renderer;
- residual identity latent;
- explicit causal-budget regularization.

### Open research questions

- What residual parameterization best preserves physical interpretability?
- How should the causal budget be quantified?
- Which learned closures are justified before increasing physical fidelity?
- What is the best OOD detector for hypothetical morphologies?
- How much linguistic information may legitimately remain in a downstream residual?
- Which perceptual metrics are useful without becoming proxies for physical validity?
- When is a surrogate accurate enough to replace a specific fidelity backend in exploration?

---

## 15. Project rule

The operational rule is:

> **Neural models may propose, infer, approximate, and complete.  
> The embodied physical system determines what sound can actually occur.**

When a future implementation makes this boundary ambiguous, the default response is not to broaden neural authority. It is to add a falsification experiment and make the causal ownership explicit.

Related repository documents:

- `docs/architecture.md`
- `docs/invariants.md`
- `docs/model-assumptions.md`
- `docs/research/voice_source_prosody_gate.md`
- Issue #40 — Embodiment causal measurement gate
