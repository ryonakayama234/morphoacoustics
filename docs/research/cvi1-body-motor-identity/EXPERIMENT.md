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
