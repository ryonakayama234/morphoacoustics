# SYSTEM — causal/ownership architecture
## Research-boundary diagram
```mermaid
flowchart TD
  S["Core-owned embodied source & field (out of scope for M1)"] -. "only future typed reference contract" .-> A["Optional ASMR receiver adapter (NOT IMPLEMENTED)"]
  O["Publisher-original KU100 measured SOFA archive"] --> I["G0 integrity, rights and measurand receipts"]
  I --> G["G0-B geometry-only split + final lock"]
  G --> D["fit / selection / calibration / final roles"]
  D --> M["Future B0-B3 / F1-F3 isolated research models"]
  I --> M
  M --> P["Phase-complete bilateral HRIR and support decision"]
  P --> V["Independent frozen numeric evaluation (NOT AUTHORIZED HERE)"]
  V -. "G5 + owner approval, new PR" .-> A
  A -. "separately pinned opt-in" .-> T["Studio immutable Take"]
```
## Ownership invariant
Core owns body morphology, gesture, speaker/source impedance and acoustic ports; ASMR may in future own a qualified measured receiver transfer and its bounded estimation. A measured HRTF is not an ear mechanical load, a physical head-scattering PDE solver, a subjective ASMR variable, or an unqualified absolute-pressure mapping. Studio may select source/listener poses and consume a versioned approved API; no experiment imports.
## Typed future boundary (NOT PUBLIC)
`ReceiverQuery(head_id, position_listener_m, coordinate_frame, source_reference_plane, input_excitation_convention, measurement_edition_sha)` →
`Supported(h_L, h_R, fs, window_origin, channel_plane, normalization, domain, model_hash, evidence_id)` OR `Refused(reason, unverifiable_field)`.
Never multiply a volume velocity derivative Qdot or Core Pa pressure by stored HRIR unless the measured excitation input/reference plane and source normalization make that transfer mathematically compatible. No double-counted free-field 1/r, ear-canal filter or source-to-head propagation. Composite rendering requires a subsequent separately audited source/receiver contract.
## Evidence boundaries
EVIDENCE_FREEZE = immutable positive/negative run; VALIDATED_COMPONENT_FREEZE = scientifically verified bounded estimator with G5 review; ADOPTED_CAPABILITY = separate owner-approved rights-compatible optional package release; Studio adoption is another independent decision. Mathematical C-TRANSFORM verification never implies full HRIR prediction.
