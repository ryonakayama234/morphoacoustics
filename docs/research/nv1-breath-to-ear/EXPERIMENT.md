# NV1-EAR / Core — executable work packages (planned)

Status: **no NV1 Core implementation or listening data yet**. Stages below implement existing [#133](https://github.com/ryonakayama234/morphoacoustics/issues/133), in isolation. Acceptance claims are always narrower than the sounds listeners may subjectively infer.

## W0 design/analytic freeze
Read SYSTEM/DATA/PREREGISTRATION, old aspiration #30 and 041 receiver implementation. Pin exact ancestor and dataset provenance. The #129 A/B receiver geometry and measured absolute B scale remain pending review; preserve this fact in all output. Capture independent Wolfram unit and numeric oracles. Review research-only `EXHALE` semantics; no changes to public contracts.

## W1 source: physical-state -> acoustic fluctuation
Implement experiment-local `breath_source.py` (planned):
`validate_scene(scene) -> Outcome`;
`realize_exhale(scene) -> FlowTrace`;
`generate_aperiodic_source(flow, closure, seed) -> AcousticSourceTrace`.
Use fixed Gaussian random stream, physically state-dependent gate and spectral shaping; guard transients, reproducibility, and energy. The user changes **only** pressure/aperture and not direct audio EQ/gain. Write `run.py`, scenario JSON, trace manifest, stereo *A*-only WAV first.

## W2 receiver
Call/reuse the EL-G0a experiment-local `render_a`, `load_sofa`, `select_positions`, `render_b` (or reviewed extraction retaining exactly equivalent semantics). Preserve A model Pa vs B relative signal, sample origin/delay, L/R, raw/playback gain, hash, 0.30m 3-direction only, no double-propagation. Save stereo 48k 24-bit WAV. Use real dataset (not synthetic fixture) for acoustic evidence.

## W3 matrices and nulls
- `P0`: Δp=120 Pa, A=30mm², seed=133041, ideal center.
- `P2`: Δp=240 Pa, A=30mm², identical seed and scene.
- `A2`: Δp=120 Pa, A=60mm², identical seed and scene.
- `Z0`: Δp=0, A=30mm²: exactly zero source/audio before any playback normalizer; no divide-by-zero.
- `NULL-GAIN`: P0 multiplied by a constant only, without recomputing physics; equal-RMS or best-fit gain contrast to P2/A2.
- `NULL-WHITE`: unshaped inlet white noise diagnostic per #30; never silently use as accepted physically conditioned source.
- `RECV-AB`: exact same `q_ac`, source hash, geometry, seed, compare ideal_A vs measured_B for center/left/right.

## W4 numerical, reproducibility, perception gates
Test dimension and sign, analytic mean flow, Re and ΔpQ; deterministic same seed, changed seed only changes stochastic realization; guard source zero energy at zero drive; no nonfinite outputs; at least 2 source variants produce *not byte-identical* freshly rendered WAVs. Compare spectral shape after RMS match and negative controls; **if indistinguishable from mere gain changes, report scientifically uninformative, not pass**. Check high-band (>2 kHz) fraction, spectral flatness, boundary clicks, crest factor, waveform peak. Independent science audit and blind headphone ratings (air-like quality, timbral difference, proximity, naturalness, lateralization) are separate, and not automatically successful on green CI.

## Required artifacts
`evidence.json`, `traces.npz` or deterministic equivalent, plot-ready metrics, hashed raw stereo 48k/24bit WAVs, fixture manifest (SOFA SHA256 and MD5 if used), reproducible command, negative refusal logs, structured STATUS report. Studio uses the **exact code revision** through pinned research runner and verifies it independently. Add final notes to RESULTS without claiming scientific adoption.
