# EL-NF1 — scientific architecture

```mermaid
flowchart TD
 S["Same source, measured source position"] --> G["G0 SOFA metadata, IR and delay audit"]
 H["Measured artificial head L/R HRIR"] --> G
 G --> D["Unique direction groups; F30 / F40 heldout split"]
 D --> B["B: 0.5m HRIR with 1/r and travel-time"]
 D --> C0["C0: ordinary HRIR interpolation"]
 D --> C1["C1: arrival-align HRIR interpolation, delay restored"]
 B --> E["Bandwise ILD and ITD vs unseen measured truth"]
 C0 --> E
 C1 --> E
 E --> P["Direction-cluster bootstrap, preregistered verdict"]
 P -. "independent science audit and separate adoption PR" .-> A["future Core receiver contract"]
 A -. "opt-in versioned capability" .-> X["future optional ASMR/Studio use"]
```

Only measurement-specific left/right **relative transfer** is investigated; SOFA HRIR is not calibrated Pa-per-source-Q. The ear canal/blocked-open reference plane and absolute scale are unresolved. `Data.Delay` is applied **once** as additional sample delay. B is 0.5m near-field fixed-reference, **not** a genuine far-field HRTF. C1 per-ear maximum-arrival alignment is an algorithmic hypothesis and can fail versus C0; it is not a biological ear model. No output loudness normalization, source impedance, room, head motion, contact or neural residual.
