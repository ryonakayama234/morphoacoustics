---
id: EL-G0A-SYSTEM
status: RESEARCH_IMPLEMENTATION_DRAFT
---
# System / ownership

```mermaid
flowchart TD
    Q["Deterministic source: Q(t) [m³/s]"] --> D["Time derivative dQ/dt"]
    X["Frozen scene source positions, coordinates"] --> A
    X --> B
    D --> A["A: causal free-space Green function\nideal left/right pressure probes"]
    D --> B["B: measured artificial-head SOFA HRIR\nhead + pinna embedded in measured transfer"]
    A --> W["Physical or model output record\nexplicit units and amplitude limits"]
    B --> W
    W --> P["Explicit playback-wide gain\n48 kHz stereo audio files"]
    P --> U["Research-only static UI\nfront/left/right, A/B, blinded toggle"]
    U --> E["Optional human listening notes\nseparate from physics validation"]
```

- **Core/research:** volume-velocity source, free-field pressure solver, measured SOFA adapter, validation, SI/provenance outputs.
- **Studio:** unchanged. The HTML is a standalone experimental presentation only, not a new physics engine or feature promotion.
- **Source:** deterministic research fixture; no actual `CreatureSpec` or gesture simulation in this task.
- **Receiver B:** real measured head/pinna *transfer*, no geometry/material solver, user-specific hearing, ear mechanical vibration or contact.
- **Physical limits:** no listener movement, rooms, binaural head tracking, contact, cartilage conduction, wet sounds or psychophysical guarantee.
- **Comparison validity:** model-B amplitude/reference calibration unknown; matching loudness across A/B is a playback intervention. A/B directional/tonal comparisons are exploratory, not fully calibrated absolute-pressure testing.

The future speaker body -> spatial field -> anatomically grounded receiver pipeline remains PR #83's *research target*, not implemented here.
