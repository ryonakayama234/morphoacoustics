# EL-NF4 — SYSTEM / causal and architectural contract

```mermaid
flowchart LR
 S["Calibrated test source\n(Static position, source stimulus)"] --> F["Physical propagation + head scattering\n(observed as measured SOFA HRIR)"]
 F --> M["Left/right measurement plane\nreference unknown until G0"]
 M --> D["G0 SOFA metadata audit"]
 D --> T["Train-only C3/C4 spatial transfer field"]
 D --> C["Separate risk/acceptance calibration"]
 T --> Q["Query: position, head ID, reference frame"]
 C --> Q
 Q --> O["SUPPORTED: relative HRIR + provenance\nor REFUSED with reason"]
```

- Ownership: source is outside receiver, no modification to Core, source/gesture, material, SMC or Studio. This experiment predicts measured static receiver transfer; it is not a source solver.
- The current `asmr/` distribution on main is metadata-only; `require_adopted` continues to refuse all non-adopted models. Research implementation stays in `experiments/048_el_nf4_receiver/` and `tests/`. No production public API.
- Source and receiver frame/unit must be obtained from SOFA. Coordinate operations are explicit; inferred az/el do not imply common microphone/reference plane.
- Magnitude, interaural level, interaural time and optional monaural spectral shapes are **observables**, not listener perception or timbral preference.
- A `SUPPORTED` tag is a research operating point with empirical held-out performance, not a proof of physical accuracy at arbitrary off-grid conditions.
- Provenance includes file SHA-256, training-role manifest and algorithm params. No raw measured IR data committed or distributed.
- No posthoc threshold adjustment against final samples; distinct human independent review G5 before feature adoption.

## Work artifacts
`INDEX.md` AI routing; `DATA.md` source and rights; `PREREGISTRATION.md` immutable D0; prospective `PREREGISTRATION_V1_1.md` G0 geometry-only if required; `EXPERIMENT.md` runnable procedure; `RESULTS.md` dated append-only log; `DECISIONS.md` explicit promotion gate.
