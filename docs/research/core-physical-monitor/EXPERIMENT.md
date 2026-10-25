# WG2 — Test registration and evidence

## Freeze before code
[Gate A](GATE_A.md) at `e322b8671567160d8b7ec3945c21289e62a3cc9b` preceded the first physical monitor implementation `6034455d0a96340b768fb8f625bea980722521ab`.

## Controls
| Test | Claim scoped to | State |
|---|---|---|
| Zero source, precise PCM format | A new WAV generated from exactly zero pressure; output digest deterministic | CI pending |
| Native impulse causality M0/M1 lengths | No mouth pressure before 16-section finite travel time, no 48k pre-echo | CI pending |
| Causal FIR low 1k / out of band 27k | Physical sample-rate adaptation suppresses Nyquist alias; only filter/group delay | CI pending |
| B0 prescribed 100 Hz flow | Byte-repeatable new audio; SI energy work residual closes, no voice claim | CI pending |
| Invalid input/full scale/clipping | no silent fallback, data corruption or normalization | CI pending |
| Independent Codex review | code/algorithm/claim review under real CI entrypoint | not requested until PR opened |
| CC-A2/SV-1 chosen real prepared body + Studio | Actual user creative Take path | NEXT separate integration / not yet |

## Decision
`PREVIEW_RESEARCH_CANDIDATE`. This is *not* the B2-B moving-wall solver, coupled vocal-fold dynamics, calibrated far-field microphone, general TTS, natural-language creative performance, or full Studio Take. Only label this numerical monitoring utility accepted after exact-HEAD green tests and `@codex review` no unresolved actionable issues.

## Independent Codex round 1, red findings and prospective repair (2026-10-25 JST)
Initial exact candidate HEAD `2339384058c72b4ee873581adc9a7a15fbcbbec0`: [full Core tests / mypy PASS](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40166218445) (all supported Python CI versions); old research differential and related science CI PASS. **Independent `@codex review` reported 3 actionable P2 scientific/software concerns**; therefore no merge from this apparently green candidate:
1. FIR 129 at much faster clock (valid 1mm × n8 = 2.744MHz) insufficient anti-alias (27kHz RMS ≈0.368 vs 1k≈0.706). Correction: **explicitly restrict native clock to 60–75kHz**, 16 sections and n=2 (the supported M0/M1 pilot). Add out-of-band rejection controls at 60/62.36/68.6/75kHz and negative 2.744MHz case. High-rate observer requires different algorithm, not a mere marketing claim.
2. `np.asarray(..., dtype=float64)` accepted complex inputs by silently dropping imaginary components, including NaN imaginary components. Correction: require original dtype kind signed-int, unsigned-int or floating real BEFORE conversion; reject complex/object/bool; add negative controls.
3. Tick-only cap allowed very large section count and O(ticks×sections×cells) copy-on-write runtime. Correction: 16-section × n2 geometry limit **before** session allocation and combined work budget, with huge geometry test.

Code repair `eda03c592cfea6d42de896534d9ed61ebf15228e`, extended falsification tests `d0841a7bedc31754221cbab55809363e19ff97db`. **No new gate success claimed** until exact repaired HEAD CI and fresh Codex review, preserving this previously green-but-invalid wider capability claim.
