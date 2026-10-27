# CVI-1 — EXPERIMENT / prospective Gate A and falsification

2026-10-27 JST · Issue #223 · Status **RESEARCH DESIGN ONLY / NO RESULT / NO ADOPTION**.

## The single question

Does a lawful recurring controller habit have a repeatable, acoustically observable effect whose size or direction may depend on the Character's prepared morphology, while preserving the intended task? Distinguish this from a one-off direction change, pitch preset, EQ change, source injection, label-only variation or waveform-level splice.

This does **not** ask whether a synthesized voice is already natural. The answer may be NO; null, unmodelable and source-quality failures are first-class outcomes.

## Gate 0 — feasibility BEFORE coding a 2 × 2 result

Inspect the **actual existing source code and pinned contract** for the candidate full path:
1. Can the same task meaning be executed with H0 and H1 (e.g., two nonidentical valid gesture-overlap/coordination controllers) through **one backend and one body representation** without changing the task targets, controller capability policy or solver?
2. Can that backend realize both vetted M0 and M1 body revisions with actual physical traces and acoustic observation under the same sampling clock?
3. Is the source acoustic boundary and receiver observation explicitly declared? Does no-body/no-controller fallback remain disabled?
4. Is the distinction between transient Direction (per-performance) and H (repeated motor strategy) operationally observable?

**STOP** on first incompatibility with `NOT_TESTABLE_BACKEND_CAPABILITY`. In particular, Exp022 (10-section shared-body) and Exp028 (16-section live vowel transfer) are different fixtures, NOT interchangeable modules. There is no accepted production MotorPersona or general OrganGraph source backend.

Document exactly which functions/data already exist; if an adapter is necessary, make a **separate scientific proposal**, do not silently blend experiment sources. No Core public ABI or Studio edits.

## Hypotheses (falsifiable, not frozen numeric acceptance thresholds)

- **H-representation:** within one T, canonical task semantics are bitwise invariant across M/H cases and physically impossible cases do not generate audio.
- **H-habit:** H0 and H1 yield repeatable differences in an already declared feasible physical control/trajectory quantity after independent solver noise is excluded. Null H0/H0 shows no change.
- **H-acoustic:** for at least two task contexts T0/T1, the downstream acoustic port quantity Q changes under a lawful H manipulation and/or differs between M0/M1, beyond an independently estimated numerical/measurement floor.
- **H-interaction:** the prespecified `I_Q = Q(M1,H1)-Q(M1,H0)-Q(M0,H1)+Q(M0,H0)` is potentially nonzero; **zero is accepted without retuning**. It is a test, not a requirement that identity interactions always occur.
- **H-retention (later):** an unseen task or held-out performance shows recognizable Character identity to blinded listeners; this is NOT equivalent to H-acoustic.

## Conditions / controls for a later frozen Gate B

Proposed 8 primary model runs: 2 prepared body revisions M0/M1 × 2 verified motor strategies H0/H1 × 2 legal gesture contexts T0/T1. Exact revisions, controller equations, durations/clock, task targets, baseline source and receiver and physics backend must be written into a frozen future Gate-B protocol **before** executing confirmatory model results.

Required controls:
- Repeat same request and source at unchanged inputs (run-to-run numerical floor, not an arbitrary acoustic significance threshold).
- H0 versus exactly H0 (null), and task only changes if the context T changes.
- Negative infeasible task using documented existing failure law: no waveform, no acoustic invocation.
- Body or habit tamper that changes only a label/Studio viewport/selection: zero physical effect.
- Source/preset tone, playback gain or neural renderer changed: must be classified as wrong manipulation and rejected from H comparison.
- Corrupted unit, NaN, altered body digest, mismatched task version: invalid input, no automatic replacement.
- Negative comparison with an old independently combined gesture overlay only if the current backend actually exposes a comparable lawful null; else mark `NOT_AVAILABLE`, not a made-up control.

## Signals / measurements

1. **Task and motion:** task residual; physical coordinate and velocity time histories (dimensioned); feasible/infeasible counts; if applicable, controller work / force / damping with explicit signed conventions.
2. **Acoustic ports:** physical pressure/volume velocity (Pa / m³/s), transfer/response, peaks or trajectories, with location and clock. Check energy passivity only for a backend whose energy ledger is actually modeled and validated.
3. **Factor effects:** preselected Q (unit, extraction, bandwidth, reference), body effect, H effect, body × H interaction and held-out T consistency. Do not use a tolerance chosen after seeing results.
4. **Evidence:** exact commit, source/body/task/controller/backend hashes, RAW arrays, standalone independent oracle/perturbation floor, negative tests and CI/third-party review outcome.
5. **Product later:** equal-level unedited A/A and blind A/B from actual new physical Takes; creator separately rates identity, distinctness, naturalness and creative usefulness. Do not demand preferences if no intelligible voice exists.

## Evidence and decision gates

| Gate | Possible decision | Excludes |
| --- | --- | --- |
| G0 actual compatibility / provenance | READY_FOR_PREREGISTRATION or NOT_TESTABLE_BACKEND_CAPABILITY | no fictional merged dynamics |
| G1 native physical execution & controls | NUMERICALLY_SUPPORTED / REVISE / NUMERICALLY_UNRESOLVED | no biology or loudness claim |
| G2 acoustic discriminability beyond observer floor | ACOUSTIC_SIGNATURE_SUPPORTED / NO_EFFECT / INDETERMINATE | no speaker identity |
| G3 human-held-out perceptual identity and actual voice quality | CREATOR_GO / CREATOR_NO_GO / NOT_RUN | CI cannot approve |
| G4 product/ABI adoption | pending separate creator approval and contract review | no default Studio UI change |

**Current decision (2026-10-27): G0 NOT EXECUTED; G1–G4 NOT RUN.** The existence of Exp022, Exp028, Exp029 and a motor-persona hypothesis document is *evidence of components*, not proof the full proposed 2×2 experiment is executable.

## Integration dependencies & parallel work

- Physics/quality: VF-1A/B2 moving source work is draft, measured M5 scalar benchmark #222 does not supply spatial pressure. A genuinely voice-like source–filter–radiation path remains a separate critical dependency for eventual G3.
- Core bounded organ graph: OG-3 current adopted-limited; OG-4 and OG-5 scope must not be confused with moving anatomy.
- Studio contract: three fixed modes, only exact slots from accepted ADR; UI edit STOP-AND-PROPOSE before any code. Existing Takes immutable.
- SMC / ASMR: optional separately gated imports at Motion / Scene boundaries; neither is a dependency to determine body × habit causal observability.

## Follow-up artifacts

If creator accepts research framing and G0 identifies a real compatible implementation:
- prospective **frozen** Gate B amendment with numerical floor and independent reference chosen before outcome,
- isolated executable pilot under a numbered `experiments/` directory, no published public schema,
- source/tests + raw result receipt + append-only decision,
- matching edits to SYSTEM / DATA / EXPERIMENT in same PR,
- CI on exact HEAD and independent `@codex` science/code review,
- explicit decision; only then consider a separate Core API and Studio creator proposal.

Reference: [Issue #223](https://github.com/ryonakayama234/morphoacoustics/issues/223), [Exp022](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/022_shared_body_multigesture/RESULTS.md), [Exp028](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/028_task_field_morphology_transfer/RESULTS.md), [Exp025](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/025_smooth_source_spectrum_vowel_cue/RESULTS.md).


## 2026-10-27 Gate 0 source-level compatibility audit receipt

**Decision:** `NOT_TESTABLE_BACKEND_CAPABILITY` for the *currently demonstrated* CVI-1 factorial pipeline; full `G0_READY_FOR_PREREGISTRATION = false`. This updates the earlier “G0 NOT EXECUTED” statement by distinguishing a newly completed **static source preflight** from a **not executed** same-backend experimental run. There are **no new numerical/CI, G1–G4, sound-quality or creator-listening results**.

| Preflight condition | Exact code evidence | Outcome |
| --- | --- | --- |
| Two H policies with invariant goal semantics | Exp027 `CandidateTask` contains onset/offset; `task_activations_at_time` uses fixed `TASKS`; helper takes explicit activations but not validated H | NOT ESTABLISHED |
| M0/M1 on same backend | Exp028 frozen 16-section, 0.160/0.176m task-field transfer | YES for original fixed task, NOT for H0/H1 |
| Shared state interaction reusable on that backend | Exp022 custom 10-section KKT and modal dynamics, not Exp028 16-section realizer | NO VERIFIED BRIDGE |
| Refuse infeasible/no-fallback | Exp029 `LOCATION_UNREACHABLE` with no acoustic call | LIMITED PRECEDENT only |
| Genuine voice and calibrated receiver | Exp028 frame-rendered frequency-domain transfer; sound/perception not qualified | NOT ESTABLISHED |

Audited source links: [Exp022](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/022_shared_body_multigesture/run.py), [Exp027](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/027_task_field_vowel_transition/run.py), [Exp028](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/028_task_field_morphology_transfer/run.py), [Exp029](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/029_task_field_embodied_infeasibility/RESULTS.md).

**Falsifiable next hypothesis, not an approval:** a separately reviewed experiment-local split of goals and lawful activation/controller schedules may permit genuinely nonidentical H0/H1 on both frozen M0/M1 bodies, with goal targets and physical state checks intact. It must not modify the old frozen V3 identity, relabel transient Direction as persistent H, or claim shared-body dynamics merely by adding independent log-area fields.

**Gate B prerequisite proposal — no code yet:**
1. Freeze a new goal-semantic identity and retained historical task+timing hash. Test that tampering with either fails.
2. Register two explicit lawful recurring controller equations H0/H1 with bounds; freeze one independent trial Direction; null H0/H0 must match.
3. Validate *actual* 16-section state, task residual and feasibility on both exact bodies, and a no-fallback impossible-task negative case. Reject any undocumented 10-to-16 conversion.
4. Freeze source, port, units, timebase and independent numeric/observer floor before comparing acoustic metrics; reject gain-only/label-only interventions.
5. If no common physically meaningful realization exists, **STOP** rather than simulate plausible voice.
6. Only then run preregistered acoustic and held-out-context trials. Studio interface changes and creator audition require separate explicit approval for the already frozen V2 slots; preserve immutable Takes.

This audit removes a deceptive shortcut: a selectable “voice personality” that only changes source signal, mixing or labels. It makes the actual missing causal-control seam explicit while leaving VF/VM sound-quality investigations independent.


## 2026-10-27 — SMC-first metrology / hypotheses / ordered integration study (prospective, not preregistration)

**No actual integration execution, numeric result, experimental test source, Core ABI, Studio UI or PR merge in this revision.** The SMC-6 formal-math GO from Draft #225 is a prerequisite **software evidence class**, not evidence that Japanese speech movements, anatomical execution or auditory character identity work.

### Four distinct measurement layers (no false cross-layer promotion)

| Layer / measurand | Measurement definition / instrument | Reference, unit and uncertainty | Can establish / cannot establish |
| --- | --- | --- | --- |
| **L0 SMC syntax and timing** | authenticated SMC5 selected pronunciation coverage; TaskGoal occurrence count; SMC6 SAT/UNSAT, exact \`t_i\`, per-event min/max, witness, jointly feasible \`O_ij=max(0,min(e_i,e_j)-max(s_i,s_j))\`, hard residual | canonical source/goal/timing digests, exact Fraction s, independent small-grid oracle; arithmetic is **exact under assumptions**, not biological measurement | formal soundness; **NOT** feasible muscles, best timing or natural speech |
| **L1 semantic mapping** | required functional TaskGoal count \`N_req\`, explicitly mapped \`N_mapped\`, named typed target variables and capability sets; structural coverage \`N_mapped/N_req\` only when denominator>0, otherwise refuse | separate frozen TaskLexicon and Core mapping reference, explicit dimension and evidence revision; mapping uncertainty/conflict recorded as \`UNMAPPED_SEMANTICS\` not hidden in scores | a stated map for a bounded task subset; **NOT** real-world articulation |
| **L2 Core motor execution** | requested vs achieved functional goal \`g_i(x_M(t))\`, physical coordinates/velocity, onset-to-achievement latency, final/hold task residual, repeatability, divergence of H0/H1, explicit \`INFEASIBLE/UNSUPPORTED/INVALID\` | pinned same realizer/body versions, actual clock and SI units, independent timestep convergence / oracle, feasibility controls; no energy claim unless full physical ledger exists | lawful model response and body dependence, **NOT** voice |
| **L3 Acoustic / later reception** | same-source same-port \`p(t)\` Pa, \`U(t)\` m³/s, spectra/transfer phase, predeclared comparable \`Q\` and body×H interaction; later radiated/receiver pressure with source/geometry identifiers | fixed source, radiation/receiver models, calibration where claimed, numerical floor, common listening gain; no arbitrary Eq/timbre editing | model-acoustic contrast only; **NOT** an identifiable pleasant character voice |
| **L4 Perceptual creator outcome** | held-out matched A/A and A/B, distinctness, same-identity retention, voice-likeness, intelligibility and usability independently | actual verified physical Takes, blinded order, equal-level replay, report listener count/uncertainty and task coverage | only qualified audition may justify creator-facing GO; CI is not a listening test |

Where a proposed Core physical target \`g_i\` has valid lower/upper bounds \`[l_i,u_i]\`, preregister residual \`r_i(t)=max(l_i-g_i(x(t)),0,g_i(x(t))-u_i)\` in its declared units. This is **prospective** and does not presume SMC5's synthetic scalar interval has those physical units. Fix the achievement/hold window and any threshold using independent evidence *before* looking at H0/H1 outcomes. If the physical meaning is uncalibrated, mark \`NOT_MEASURABLE\`, never define a cosmetic normalized error afterward.

### Separable falsifiable research hypotheses (all untested for CVI)

- **H-S0 provenance:** authenticated identical SMC request + COMPATIBILITY timing reproduces identical plan/goal/exact events irrespective of input ordering that is semantically unordered; a forged receipt, unresolved timing or wrong SHA generates no physical request.
- **H-S1 mapping:** a predeclared subset of SMC TaskGoals can be mapped to dimensioned and physically supported Core task variables without reading invention or body-specific target substitution. Competing/ambiguous or missing mappings **refuse**. Counterexample proves the bridge is unsupported, not that SMC's symbolic graph is invalid.
- **H-P0 same-plan habit:** with same *faithful* SMC exact schedule, same body M0, fixed Direction/source/initial state/solver, two genuinely lawful **physical policies** H0/H1 satisfy the same task goals but yield reproducibly distinguishable physical trajectories above predeclared numerical floor. H0/H0 null must not differ. Reparameterized interpolation of a prescribed waveform does **not** count.
- **H-P1 cross-body transfer:** the *same* H0/H1 definitions and SMC task identity can be tested on both prepared M0/M1 and >=2 independently chosen feasible contexts. Any \`UNSUPPORTED\` or \`INFEASIBLE\` case stops the associated contrast; do not impute silence as Q=0. A change in results need not imply a nonzero interaction.
- **H-A0 acoustic mediation:** if physical H contrast exists, it changes a prespecified acoustic observation *because* of executed physical state under identical source/receiver conditions; null gains/labels, source-only or postfilter manipulations must fail. If source is fixed/prescribed, claim only tract-mediated effects, **not different vocal-fold phonation**.
- **H-T0 independent planner timing study (later):** under a **new authorized non-exact timing contract** a documented policy may select different schedules from a feasible SMC timing region, while source identities and hard constraints remain intact. **SMC6 RESEARCH_OVERRIDE is only synthetic sidecar evidence** and cannot fulfill a faithful performance claim.
- **H-L0 voice identity (later):** any listener-recognized individuality must persist on held-out tasks and under controlled level/source conditions, separate from acoustic-only differences and creator preferences. No assertion until L4.

### Decision sequence / dependency and hard stops

**D0 — source/ABI audit (this design, partially complete):** exact SMC5/SMC6 function/signatures, digest and lane semantics versus actual Core body/task APIs documented; **no supported general SMC->Core mapper or H controller found**. Existing verdict \`NOT_TESTABLE_BACKEND_CAPABILITY\` for the full CVI 2×2 stands.

**D1 — future mapping feasibility design, before code:** choose one concrete, fully named SMC TaskDefinition and one *independently supported* Core functional variable. Prove semantic compatibility and units with an auditable mapping table; explicitly distinguish vocabulary/task hypotheses from measured anatomy. If no mapping, \`UNMAPPED_SEMANTICS / STOP\`, not automatic 'CONSTRICT' guess.

**D2 — future body/habit execution design:** show one same-backend physically meaningful controller with two lawful policies and two compatible pinned prepared bodies. Distinguish symbolic schedule, continuous motor command and actual motion; no 10-section Exp022 graft into 16-section Exp028. If no meaningful physical controller, \`NOT_TESTABLE_BACKEND_CAPABILITY / STOP\`. A mere kinematic curve difference is not automatically a habitual skill.

**D3 — separately preregistered experiment and code after approval:** freeze all inputs, task labels, body/SMC/core/adapter SHA, target/clock, reference oracle, predeclared numerical/observer floor, negative controls and exact Gate thresholds **before** implementation. Only then perform H0/H1 and two-body tests, with raw traces and append-only result ledger. SMC6 compatibility candidate must remain exact. If testing override, use a different synthetic-study evidence stream.

**D4 — bounded acoustic/creator adoption:** only after D3 physical support, test real source/tract/acoustic observations and perhaps qualified physical Takes. Creator's blind A/B and actual voice GO/NO-GO are independently required. Product ABI/Studio V2 motion/character parameter bindings need a fresh STOP->present->agree gate. No new panel, no sound EQ, no automatic merge.

### Preregisterable negative-control suite (not executed)

N1 same SMC5 exact bytes/semantic permutation -> unchanged original candidate/timing digest; N2 COMPATIBILITY attempt to move an exact event -> UNSAT/refusal; N3 untrusted \`RESEARCH_OVERRIDE\` displayed as original SMC5 performance -> reject; N4 SMC shared Task appears once even with two pronunciation owners; N5 absent/ambiguous unit / unknown Task mapping -> no Core execution; N6 wrong physical units/capability / unreachable task -> no acoustic fallback; N7 same H0/H0 and label-only/canvas-only -> zero physical contrast; N8 waveform gain/EQ/source-only change -> forbidden as H; N9 distorted source/receiver clocks -> no acoustic contrast; N10 same-step solver refinement or independently measured floor fails -> \`NUMERICALLY_UNRESOLVED\`; N11 inconsistent 10-vs-16 shared-state shapes -> refuse before computation; N12 invalid schedule/constraint digest or changed Code SHA -> fail-closed.

**Owner/process interface:** SMC #219 remains its independent temporal-formal project and may continue without CVI implementation. CVI #223 / Draft #224 owns this *integration* research plan. Core #199 owns physical law and measured feasibility. Studio V2 ADR remains frozen; Studio #32 acoustic creator-quality HOLD remains authoritative. New technical work requires a specifically reviewed integration task, not stacking unmerged SMC research onto Core main by implication.
