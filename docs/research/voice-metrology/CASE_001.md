# CASE 001 — WG2 CI M0/M1 spectral concentration (fixed measurement, 2026-10-25)

Source artifact: https://github.com/ryonakayama234/morphoacoustics/actions/runs/40181810529/artifacts/12594024942
Archived Core SHA: 8d4a62c6a75394309ef0b18f72cc06f81f265331 (separate frozen research draft, NOT current accepted main).
Source float64 SHA: 15e7309ec7cce300a4d45f0c5149f6b4ac9490fc3ae0625ea4e1825b4834ea9d, same for M0/M1. Source: SV1 Rd1 LF pulse, externally prescribed 100Hz sampled inlet FLOW; no glottal self-oscillation / pressure feedback.

## Exact reproducibility
- Six input files per body: manifest.json; audio.wav; source_flow_48k.npy; mouth_pressure_native_pa.npy; mouth_flow_native_m3_s.npy; mouth_pressure_monitor_48k_pa.npy. Source and PCM bit hashes in manifest.
- Measurement: remove mean from samples 2400..9599 (0.05..0.20s at 48k), DFT, sum |X(100*n Hz)|² over n=1..80, calculate fractions; 15 full source periods, no frequency interpolation. Fixed 8Pa/fullscale, no per-body audio gain.
- Report limited to THIS stimulus, THIS mouth-port observation and this algorithm version. No calibrated listener SPL or true F1/F2 formant inference.

| Quantity | M0 / 0.160m | M1 / 0.176m |
|---|---:|---:|
| Source SHA same? | yes | yes |
| Physics clock | 68,600 Hz | 62,363.636 Hz |
| Source 600Hz energy share in first 80 harmonics | 0.0288461% | 0.0288461% |
| Source 600 vs 100 Hz | -34.910 dB | -34.910 dB |
| Native p mouth RMS, entire 0.25s | 0.095236 Pa | 0.439268 Pa |
| 48k p monitor RMS, entire 0.25s | 0.095209 Pa | 0.438439 Pa |
| Mouth monitor 600Hz energy share in first 80 harmonics | 21.788% | 96.871% |
| Mouth monitor 100Hz energy share | 23.049% | 1.0054% |
| Mouth monitor 600Hz vs 100Hz | -0.2444 dB | +19.8386 dB |
| Relative selectivity change (output 600:100 minus input 600:100) | +34.665 dB | +54.748 dB |
| First 80 harmonics / output AC spectral energy | 99.972% | 99.566% |
| WAV dequantization error RMS, Pa | 0.00007036 | 0.00006991 |
| PCM peak absolute signed integer | 972 | 3339 |
| Wav clipping / overflow | none | none |
| Max signed energy residual (J/tick) | 2.75e-23 | 3.40e-23 |

## Reading the measurements correctly
- Positive evidence: M1 retains around 96.9% of the measured first-80-harmonic energy at 600Hz. Strong concentration already occurs in native p_mouth before PCM/resampling, whose error is small. Thus a bug solely in *the final WAV packer* cannot explain the dominant 600Hz line.
- NONCONCLUSION: no verified formant frequency/Q or excessive loss can be inferred from this single 100Hz-pitched source output. Acoustic resonances preferentially amplify harmonics by design, and the human voice does not have a universal 600Hz fraction. A 600Hz dominance is an informative flag for a signal-like quality, **not causal attribution yet**.
- Next falsifier: measure independently the 16-section system's transfer function H_pU(f), resonance decay and bandwidth using a broadband input and matched receiving port. Compare boundary and physically justified loss model under same geometry/source.
- Independently study missing source-tract feedback, tissue/wall dissipation, and radiated farfield operator. Do not patch by per-file EQ or arbitrary post-WAV harmonic injection.
- Human's user-local UUIDs (05e8d69a... and 9801d385...) remain unidentified with respect to these CI M0/M1 artifacts. Do not assert that the worst local Take was M1.

## Status
TRACEABILITY: PASS for this authenticated CI artifact bundle. PHYSICS: prior finite-speed/energy tests passed, independent resonance/receiver validation NOT DONE. VOICE CANDIDATE: HOLD. CREATOR GO: not requested for this artifact; earlier subjective NO-GO for local Studio sessions is separate.
