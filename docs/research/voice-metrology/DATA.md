# VM0 DATA — diagnosis record, status and reproducibility

## Input evidence bundle
source_flow_48k.npy: float64 48kHz [m³/s], externally prescribed LF. mouth_pressure_native_pa.npy: float64 native physics clock [Pa]. mouth_flow_native_m3_s.npy: float64 native clock [m³/s]. mouth_pressure_monitor_48k_pa.npy: float64 output monitor pressure [Pa]. audio.wav: mono signed PCM16 48kHz with fixed scale Pa/fullscale. manifest.json contains exact SHA, byte counts, body revisions, observer version, physics tick length and signed energy.

## Diagnostics schema
- schema_version: voice-metrology/v0, method: fixed-15-cycle-100hz-dft-50to200ms-mouth-port.
- For each body: exact prepared ID/revision and hash; source identity and source SHA; native p hash, monitor p hash, WAV hash; physics clock and receiver location.
- source_harmonics and mouth_monitor_harmonics: 100..8000Hz, 100Hz spacing, AC DFT power for exact 15 cycles. Fields: sixth_fraction, fundamental_fraction, sixth_relative_to_fundamental_db, harmonic_family_ac_fraction, effective_harmonic_count, 10 strongest lines; all normalized by the stated FIRST EIGHTY SOURCE HARMONICS, not broadband recording loudness.
- sixth_vs_fundamental_selectivity_change_db = output relative 600:100 dB - source relative 600:100 dB. It can be large because the tract is a filter; not a pathological threshold.
- wav_quantization_rmse_pa, wav_pcm_peak_abs, native_pressure_rms_pa, native_mouth_flow_rms_m3_s, observer_max_abs_energy_residual_j are lower-level numeric observables.
- Hard statuses: measurement_validity VALID_BYTES_AND_NAMED_PORTS / INVALID; acoustic_reference_validity NOT_TESTED until H(f) reference exists; voice_candidacy HOLD_NO_REFERENCE; creator_acceptance NOT_ASKED_FOR_THIS_FIXTURE.
- CI two-body comparison: same_source_both_bodies is true only if both hashes identical. Still comparator_type ANATOMY_SENSITIVITY_NOT_OLD_NEW_VOICE. A different body is never a matched old/new acoustic-quality control.

## Three non-interchangeable reference types
(a) known mathematical reference validates signal-processing algorithm on sinusoids and silence; (b) independent waveguide/transfer-matrix reference validates acoustic response against physical modeling assumptions; (c) measured phonation and calibrated receiver references eventually validate vocal-sound task. None is implied by a successful NumPy FFT.

## Scientific status and ownership
Metrology never writes back a corrected WAV or new voice. It is readonly offline inspection of immutable artifacts. Numeric thresholds are registered before measurement from model truncation/error, independent fixtures or qualified reference distribution. Unknown means UNKNOWN, not PASS. Simulator-produced narrowband spectra cannot be compared against clinical CPP norms. Studio Research Drawer may display the report; the creator's only required answer remains a binary GO/NO-GO after preregistered target.

## Reproduce fixture
Download GitHub Actions artifact 12594024942 from run 40181810529 as ZIP. Execute: python tools/voice_metrology.py --zip path/to/wg2-prepared-m0-m1-native-physics.zip --output-json vm0.json. If the artifact is unpacked, zip the root M0 and M1 directories to reproduce original root names. Do not trust results if hashes mismatch or a signal is clipped.
