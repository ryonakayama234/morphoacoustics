# Speech Motor Compiler — SMC-1 research index

**2026-10-21 — RESEARCH EXPERIMENT / NOT ADOPTED / NO AUDIO OR STUDIO RELEASE**

Tracking: [SMC-1 #139](https://github.com/ryonakayama234/morphoacoustics/issues/139), parent [M5 #11](https://github.com/ryonakayama234/morphoacoustics/issues/11). Branch: `research/smc1-gate-a-b-20261021`. Do not confuse a Draft PR/CI success with adoption.

## Searchable context
- [SYSTEM.md](SYSTEM.md): creator journey, Core↔Studio boundaries, causal diagram, modules and staged gates.
- [DATA.md](DATA.md): immutable linguistic and symbolic motor records, ID/source-offset mapping, diagnostics and capability limits.
- [EXPERIMENTS.md](EXPERIMENTS.md): falsifiable hypotheses, fixed numerical oracle, controls, experiments, evidence status, decision ledger.
- [wolfram-oracle.wl](wolfram-oracle.wl): independent rational-number timing oracle for inherited Exp011 constraints.
- `src/smc1_research/speech_motor_candidate.py`: bounded exploratory planner; **not exported as public API**.
- `tests/test_speech_motor_candidate.py`: positive, partial, invalid, ambiguity and contradiction tests.

## Distinguish four questions
1. Is the kana orthographically recognized? SMC-1 **yes** for a deliberately tiny explicit mapping.
2. Is context-sensitive Japanese pronunciation validated? **No** (notably よう/とう).
3. Is a symbolic motor-intent target assigned? **Only A/I-like candidates**, without physical gesture calibration.
4. Can a body physically execute it and generate natural speech? **Not shown by SMC-1**. Existing Core limited live waveforms are separate adopted capabilities.

## Prior work and constraints
- [Experiment011 RESULT](../../../experiments/011_gesture_coordination_overlap/RESULTS.md): two CONSTRICT overlap is an observable independent variable, not verified natural Japanese coarticulation.
- [shared timeline candidate](../shared-timeline-candidate-v1.md): deterministic equality-constraint graph, no solver/body state.
- [V3 Experiment027](../../../experiments/027_task_field_vowel_transition/RESULTS.md): frozen 3-task /a/→/i/-like physical realization; not interchangeable with arbitrary syllable templates.
- [V4-A #74](https://github.com/ryonakayama234/morphoacoustics/issues/74), [SV-2 #126](https://github.com/ryonakayama234/morphoacoustics/issues/126): separate physical temporal-coherence branches.
- [Studio CC-A2](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/cc-a2-two-body-studio.md): existing immutable physical Take integration is unchanged.

## Decision states
Exploration ⇒ independently preregister confirmatory hypotheses ⇒ research verification ⇒ separate physical Gate ⇒ external studio adapter Gate ⇒ scoped adoption. **This PR contributes only exploratory SMC-1 representation and tests.** No main merge or API promotion is implicitly authorized.
