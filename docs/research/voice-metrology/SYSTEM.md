# VM0 SYSTEM — causal measurement chain and independent validators

Physical design invariant: morphology M, tissue theta and motor pi(t) drive state x(t) → glottal airflow/acoustic source → tract wave field → radiation + environment → Listener receiver → observed waveform. The spectrum and WAV are downstream measurement, not a substitute latent 'voice' state.

## Signal graph and measurement ownership
- M0: CharacterBodySnapshot owns geometry 1D segment lengths/areas and material assumptions; native sample clock follows c*n/section_length.
- M1: Source owns prescribed U_g(t), phase F0 and envelope; the current SV1 injected volume flow is **not** self-oscillating vocal fold physics. Future moving folds must record effective tissue force, displacement, contact and coupled pressures before source validity is claimed.
- M2: Acoustics owns p_in(t), U_in(t), incident/reflected section waves p+/p-, p_mouth(t), U_mouth(t), energy and boundary impedance. Current bundle records source flow, native mouth p/U and work ledger only; per-section waves and full inlet trace are NOT archived.
- M3: Radiation owns p_ear(t) from geometric Speaker/Listener positions, mouth opening velocity, environment, diffraction/contact and receiver calibration. CURRENTLY UNMODELED. B0 radiation energy dissipation is not equivalent to calibrated p_ear.
- M4: Observation owns FIR/decimation, PCM and fixed monitor scale (currently only **mouth pressure monitor**). Calibration metadata makes a measurement meaningful; no reference receiver invented by WAV playback.
- M5: Instrumentation owns reference measurements, precise spectral window, numerical method, source/geometry hash and uncertainty; it cannot modify original audio. Physically informative reports must refer to the exact source/tract/receiver at which measured.

## Fault localization
Source controls: U_g(t), derivative harmonics, source F0 and true source boundary. Track whether apparent 600Hz is already present at inlet and how much.
Tract controls: acoustic H_pU(f)=P_mouth(f)/U_in(f), also inlet impedance Z_in=P_in/U_in and outlet ratio U_mouth/U_in, measured with SMALL broadband stimulus on a fixed state; explicitly state source impedance and boundary.
Radiation controls: scattering/absorbed B0 energy, complex load, eventually valid radiated pressure at fixed distance; never infer pressure-at-ear from p_mouth.
Sampling controls: physical native pressure and flow first, after FIR/ZOH monitor second, fixed PCM last. First stage of abnormality is a localization clue. Compare power spectra with declared alignment, not equal sample counts alone.

## Independent reference design
Phase 1: Uniform equal-area lossless tube with ideal matched/open/closed ends — analytic delay/scattering and expected resonances under same boundaries. Phase 2: segmented 1D transfer-matrix impedance model, independent code path and numerical reference; include loss/radiation assumptions explicitly. Phase 3: bounded tissue-wall losses and externally validated anatomy/material data before speech claims. Phase 4: coupled glottal and receiver geometry where needed, compared to physical measurements.

Do not treat source/differential code equivalence as independent acoustics. Do not compare CC-A2 dynamic /ai/ to WG2 static /a/ as a matched old/new quality test.

Integration: Core owns physics and metrology, Studio shows only the summary through its Research Drawer under fixed PANEL_REGISTRY. No extra default screen cards, no new sound model in this PR; the creator sees only an explicit, binary GO/NO-GO gate when a specified experimental voice target is scientifically ready.
