# SMC-1 — SYSTEM architecture and creator consequences

**Hypothesis:** Script intent can be represented independently of a body's current motor/solver capability. A string must never be quietly converted into plausible sound through another path.

```mermaid
flowchart TD
  subgraph Studio["Studio: creative application (NO CHANGES THIS GATE)"]
    X["Character + Script.text + segment_id"] --> Y["Future Performance adapter"]
    Z["Direction / MotorPersona (future)"] -.-> Y
  end
  subgraph Compiler["morphoacoustics.integration: SMC-1 research only"]
    Y --> A["Explicit limited kana decoding"]
    A --> B["PronunciationUnit[] + source offsets"]
    B --> C["MotorIntentSlot[] (symbolic or unresolved)"]
    C --> D{"All intents mapped, no uncertainty?"}
    D -->|yes| E["Candidate CoordinationPlan + semantic start anchor"]
    D -->|no| F["Partial / Invalid diagnostics; NO executable score"]
  end
  subgraph Physics["Core physical causal path (unchanged)"]
    E -. "separate future approved adapter only" .-> G["Calibrated Gesture templates / GestureScore"]
    G --> H["PreparedMorphology + capability gate"]
    H --> I["Physical state → acoustics → audio"]
    H --> J["UNSUPPORTED / INFEASIBLE: no substitute audio"]
  end
  I -. "future versioned result" .-> K["Studio immutable Take / A-B listening"]
  F -. "future inspection UI" .-> K
```

## Current vs future
Current SMC-1 owns *only* pure kana analysis, symbolic A/I-like intents, and a demonstration event-relation plan. It does **not** create `GestureScore`, access body presets or call waveform generation. Import it explicitly from `morphoacoustics.integration.speech_motor_candidate`; it is deliberately absent from `integration.__all__`.

Existing `shared_timeline.compile_shared_timeline` accepts **actual** GestureTemplate instances and a CoordinationPlan. Tests use a **synthetic two-CONSTRICT adapter** solely to compare event arithmetic to Experiment011. This test adapter is not a phonetic mapping for 「あい」; never expose the resulting synthetic score to Studio as speech.

## Creator-facing semantics
The future Studio experience can show an intact typed Script plus unresolved movements. An existing adopted physical adapter may generate a real new Take only when every requested task is validated and feasible. Unimplemented `/h/`, `/g/`, `/ɾ/`, `/t/` and the uncalibrated mapping of whole syllables cannot become audible just because a phoneme string exists.

**Organ graph separation:** no organ nodes, ports, edges, materials, acoustic topology or physical numerical state are modified. Body-specific realization and capabilities remain Core responsibility; Studio owns creative editing, Takes and comparisons.

## Next gates
Gate A independent prospective protocol; Gate B bounded planning semantics and test evidence; Gate C separate physical adapter and real audio; Gate D independent scoped adoption; Gate E Studio product journey. Do not broaden Performance Contract v0/v1 silently.
