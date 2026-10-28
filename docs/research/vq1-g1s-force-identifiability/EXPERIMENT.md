# VQ-1 G1-S — static pressure-force preregistered EXPERIMENT

Date: 2026-10-28. Pre-code prospective protocol. **Hypothesis**: a declared spatial wall pressure field, independent wetted-surface quadrature, and a common-gauge tracheal/exterior pressure reference suffice for *algebraically identifiable* signed static generalized force **within the declared discretization**. They do NOT establish that the field or geometry matches an actual larynx.

## Frozen independent tests
1. H-SIGN: single patch, known p0, exterior and D yields exact analytical force; reversing signed projection reverses force; do not turn drop D into absolute wall pressure.
2. H-WALL: equal-opposite pressure patches cancel the common baseline; unequal measured drops do not. FW/NFW mismatches and duplicate patch keys are rejected.
3. H-GAUGE: adding the same constant gauge offset to p0 and exterior must leave force unchanged. Missing p0/exterior must refuse computation.
4. H-UNC: uncertainty interval contains independently bounded perturbations and computes **common-mode** gauge uncertainty from sum of signed patch weights, not quadrature over taps.
5. H-NEGATIVE: missing/unmatched measurements, wrong wall, negative area, nonfinite/boolean values, negative uncertainty, nonsensical projection and fake dynamic execution are refused before results are reported.
6. H-NO-VOICE: the runner reports only synthetic algebraic results; with NO qualified real source it emits `G1_S_SOURCE_HOLD`, `G1_D_HOLD`, `VOICE_NO_GO`, even when software tests pass. Tests cannot certify force physiology.

## Measurements and stop/go
Keep three distinctions:
- **G1-S algebra**: independent synthetic analytical cases, dimensional checks, negative controls, exact-head CI.
- **G1-S actual force**: STOP until independently digitized M5 wall pressure at actual taps, original figure audit, coordinate uncertainty, independent geometrical area/normal/projection and pressure reference exist. Draft #220 contains the detailed source metrology protocol.
- **G1-D dynamic / G4 voice**: HOLD / NO-GO; static pressure data cannot validate moving-wall work, tissue vibration or audible character voice.

Design is hypothesis-driven, not testing a visually pleasing fabricated voice. Failed tests must not be converted to PASS by an evidence runner. Dedicated CI stores JSON receipt even when tests are RED; source SHA attached. Do not import unmerged SFI/VF/G0-P implementations. Follow with separate actual source-digitization and geometry-qualification task, *not* an oscillator or Studio panel.

When a future valid source profile becomes available, reassess the force interval including geometric uncertainty and independent wet-surface / reference-plane qualification. Admit a Core API only after scientific verification and code review; admit Studio sound only after waveform physics and creator listening independently pass.
