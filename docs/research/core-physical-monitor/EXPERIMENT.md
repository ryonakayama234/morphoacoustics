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
