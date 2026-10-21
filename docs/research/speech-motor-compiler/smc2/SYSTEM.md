# SMC-2 SYSTEM — body-independent motor intent planning

## Creator objective and separation
Creators write any Script.text, including unsupported text. Research planner preserves source and offers proposals / exact unresolved diagnostics, never a fake audible Take. Future Core realizer binds a validated task/gesture mapping to a versioned PreparedMorphology; Studio then records immutable physically generated Takes. This work does **not** implement that future link.

```mermaid
flowchart TD
  S[Studio: Character + Script text + segment_id] --> P[Future request adapter]
  P --> A[SMC-2: explicit bounded kana decoding]
  A --> B[PronunciationUnits and source spans]
  B --> C[MotorIntentGraph: phoneme-level nodes]
  C --> D{All intents known; no ambiguity?}
  D -->|yes| E[CoordinationPlan: symbolic onset/offset relations]
  D -->|no| F[PARTIAL/INVALID plus unresolved diagnostics]
  E --> G[Research-ready symbolic result, NOT GestureScore]
  G -. independently verified adapter only .-> H[Core: CapabilityResolver + PreparedMorphology]
  H -.-> I[GestureScore -> physical realization -> acoustics]
  I -.-> T[Studio immutable Take]
  F --> Z[Future Studio inspection UI; no audio]
```

## Strict ownership
- Core `src/morphoacoustics/` physical and existing `integration.shared_timeline`: **unchanged**.
- Research `src/smc2_research/`: provisional immutable plans, no public re-export, no physical solver imports except reuse of `shared_timeline` symbolic constraint types.
- Existing `compile_shared_timeline` emits physical GestureScore and therefore is NOT invoked by runtime SMC-2. A synthetic test fixture may explicitly use it to verify *event arithmetic only* (Exp011), never as evidence of Japanese phonetic mapping.
- Organ graph node/edge (physical acoustics) is NOT the same graph as motor-intent node/time-edge. Intent expresses desired capabilities, not body-specific organ IDs, locations, tissue properties, or numerical state.
- Studio remains untouched in initial Gate B. Its adopted CC-A2 body preset and immutable Take contract are an integration destination, not part of this research result.

## Claim limits
No Japanese general phonology, no physical consonants, no morphology-conditioned actuation, no self-oscillating source, no real-time speech, no neural fallback, no recorded speech/audio input, no wav output, no naturalness claim. Recognition is not execution, and `SYMBOLIC_READY` is explicitly not `FEASIBLE`.

## Implemented research boundary (Gate B submission)
`plan_speech_motor(segment_id, text, pace)` returns immutable phoneme-level nodes, ordering edges, diagnostics and an optional fully mapped synthetic CoordinationPlan. Runtime does not call physical `compile_shared_timeline`, and there is no body adapter or synthesis interface. Test code may use a synthetic CONSTRICT adapter for inherited time arithmetic only.

## Ordering semantics correction
A graph edge now uses `LEXICAL_NEXT`, **not** a temporal PRECEDES constraint. Actual onset/offset overlap is exclusively represented in `CoordinationPlan`; lexical text order need not imply nonoverlapping actuation. This is a research semantic refinement before API adoption.

## B1 capability receipt
On code-bearing `a8e41fb6`, all exact-SHA automated checks passed. Changes relative to main comprise 9 new files exclusively: standalone research package, tests, 4 documents, Wolfram source, CI config. The physical kernel, organ graph, Performance Contracts and Studio remain untouched. A test-only synthetic GestureScore is not a runtime artifact or phonetic capability.
