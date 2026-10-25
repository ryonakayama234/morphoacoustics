# CORE-WG-2 / Gate A — reproducible 48 kHz mouth-port preview (PRE-CODE)

Date: 2026-10-25 JST. Narrow step toward [Core #191](https://github.com/ryonakayama234/morphoacoustics/issues/191), after opt-in Core companion [PR #187](https://github.com/ryonakayama234/morphoacoustics/pull/187) merge `f122b7553270c9a8dd9c7edb63b65467c28559c6`.

## One chosen hypothesis
A prescribed sampled source **volume flow** (m³/s) may drive the unchanged validated `PassiveWaveguideSession` at the prepared geometry's **own** physical clock. Its **signed mouth-port pressure** (Pa) may be rendered as a bounded, anti-aliased 48 kHz PCM16 audition **monitor**, without claiming a calibrated external microphone, physiologic self-oscillating source, natural speech or production adoption.

## Scientific constraints
- No edit to frozen `morphoacoustics` package, historical experiment code/manifests/tests, or existing Core default paths. Implement in opt-in `morphoacoustics_waveguide` only.
- Physical tick `h=L_section/(c*cells_per_section)` from actual body. Geometry must satisfy the accepted static equal-section-length capability.
- Source `U_48(t)` is an externally prescribed **piecewise-linear** signal between known 48k samples. Do not treat the interpolation as coupled source–tract feedback.
- For this first consumer output, require `f_physical > 48k`; no implicit clock rounding. 48k receiver applies **causal** lowpass FIR (Kaiser-windowed sinc; declared coefficients/cutoff/group latency) before **past-sample (zero-order hold)** output sampling. This never injects pre-arrival pressure. Fixed playback Pa/full-scale, no audio file-specific normalization, EQ, pitch-shift, compression, or arbitrary waveform re-coloring.
- Output is called `mouth_port_pressure_monitor_pa` and is **NOT** `far_field_microphone_pa`. The physical duct's B0 radiation loss is computed by solver; no assertion that mouth-port pressure equals ear pressure.

## Controls and falsifiers
1. Zero source -> byte-exact signed-zero physical/monitor signal and silent PCM.
2. Source pulse -> no pre-arrival pressure before (L/c), including 48k monitoring; same 16-section geometry with 10mm vs 11mm sections yields physical clocks and first-arrival times in 1.1 ratio (allow observation filter latency).
3. A 1 kHz native physical pressure sinusoid survives antialias/48k transfer with bounded gain error; a >24 kHz tone is strongly suppressed instead of aliasing. Causal lowpass adds no pre-echo.
4. Nonfinite source, empty arrays, unsupported physics clock, boolean/nonfinite scale, and clipping must fail explicitly; no WAV silently clipped. No implicit sample-count changes.
5. Source trace, native mouth pressure, optional mouth volume flow, 48k monitor, fixed PCM16, exact physics and observation parameters and signed summed energy ledger are separate outputs with reproducible digests. Exposure to Studio requires body ID/revision validation in a **separate adapter** before claiming creator Take.
6. Project CI, focused numeric checks and **`@codex review`** must pass before opt-in merge. A pass proves a scientifically interpretable **monitor transform**, not perceptual voice quality or Studio readiness.

## Decision point
If the monitor is reproducible and causality-preserving, **accept as an opt-in physical-preview building block**, not a default audio generator. Next physically meaningful integration connects pinned CC-A2/SV-1 M0/M1 body/source and Studio Take, then B2-B moving wall and source–tract feedback.
