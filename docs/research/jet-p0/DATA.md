# JET-P0 — DATA

Units and authority (each is a distinct type of fact):

| Field | Unit | Role |
|---|---|---|
| delta_pressure_pa | Pa | prescribed respiratory-pressure intervention, NOT measured lung pressure |
| leak_area_m2 / max_aperture_m2 | m² | prescribed glottal kinematics, NOT solved tissue |
| aperture_phase / glottal_area_m2(t) | dimensionless / m² | explicit prescribed physical-state input |
| jet_velocity_m_s, Reynolds | m/s, dimensionless | derived Bernoulli / fluid properties |
| flow_m3_s(t) | m³/s | derived mean volume velocity |
| aspiration_m3_s(t) | m³/s | *hypothesized* stochastic source perturbation (record seed) |
| source_m3_s(t) | m³/s | complete physical input to acoustic solver |
| pressure_pa(t) | Pa | Core acoustics result; waveform observed, not internally specified |
| wav PCM16 | samples | separate *playback-scaled* observation only |
| listener notes | text | perception; no physical truth assumed |

P0 fixed sample rate 48000 Hz, 24000 samples, F0 100 Hz, 0.6 open-phase fraction, 10 ms shared file fade; fixed reference body M0@1 from SV-1. Air rho 1.2 kg/m³, viscosity 1.8e-5 Pa s, discharge coefficient 0.6, jet width 1 mm, correlation length 2 mm, phenomenological Re onset 1000. Noise ratio 0.02 is specified relative to *computed jet flow*, **not a claim of 2% audible aspiration**. These are uncalibrated research assumptions.

Conditions: modal (800 Pa, 0 leak, noise 0.02); breathy_gap (800 Pa, leak 0.15 mm², noise 0.02); pressure_x2 (1600 Pa, 0 leak, noise 0.02); noise_off (800 Pa, 0 leak, noise 0). Null zero-pressure tested mathematically and intentionally **not** passed to the nonzero-audio renderer.

Output on explicit `--out` (must not exist): `manifest.json`, and for each non-null case `*_source.npy`, `*_pressure_pa.npy`, `*.wav`. Manifest stores seed, backend/body description, fixed numerical assumptions, physical input values, source/raw-pressure/WAV SHA256, Reynolds, source and rendered >2 kHz fractions, pressure RMS and one common listening gain. **Hash is an integrity checksum, not a third-party signature.** CI run and source SHA must be bound externally before scientific citation; the initial emitted `source_head` placeholder MUST NOT be presented as an attested provenance receipt.

No neural latent, speaker embedding, free-text motor inference, visual body, microphone SPL calibration, nearfield ear, or verified human listening data is present.
