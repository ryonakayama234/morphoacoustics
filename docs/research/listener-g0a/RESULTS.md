---
id: EL-G0A-RESULTS
status: MEASURED_SOFA_CI_NUMERIC_PASS_PERCEPTUAL_REVIEW_PENDING
adoption: NOT_ADOPTED
---
# Results / decision log

## 2026-10-20 — implementation audit phase

- Research-only branch stacked above PR #114. Existing Experiment 040 unchanged.
- Source volume-velocity Q(t), free-field time-domain propagation, SOFA HRIR / complex-HRTF support, conditional recorded-source selection, stereo WAV and static listening UI implemented.
- **Local synthetic-SOFA fixture:** 12 new tests passed; generates six WAV with 48kHz stereo and provenance. Synthetic fixture verifies processing logic **only**; it cannot prove the measured SOFA's compatibility, real head reception, or ASMR/externalization.
- **Real measured Marschall SOFA:** **PASS** in [CI run 39406560531](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39406560531), source MD5 verified, both parent Experiment 040 (9 tests) and new G0a (12 tests) passed (21 total).
- **Actual audio proof:** GitHub Actions artifact [`EL-G0a-measured-HRTF-listening`, ID 12256912249](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39406560531) includes 6 real-SOFA 48kHz/24-bit PCM stereo WAVs, reproducible `evidence.json` and `index.html`. Artifact expires 2026-11-19.
- **Project-wide normal CI:** [run 39406565506](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39406565506) passed Python 3.11 / 3.12 / 3.13 and mypy. Optional G0a dependencies are installed in the dedicated workflow; normal CI skips that test module when dependencies are absent.
- **Measured source positions:** radius 0.3 m, azimuth center 0°, left +27.69°, right -27.69°, horizontal elevation 0°; indices center 61, left 62, right 73. Positions came from SOFA file and are not interpolated.
- **HRTF actual metadata:** `SimpleFreeFieldHRIR`, `DataType=FIR`, 196 measurements, 2400-tap IR. `ReceiverPosition` declared type `spherical`, units `metre` without angular units. Parser explicitly marks it unsupported and A uses ideal ±0.09 m probes; thus ear-observation planes are not perfectly matched, and **strict one-factor human-ear causal comparison is not yet demonstrated**.
- **WAV observations:** source is the same Q(t). R/L geometric A RMS delta: center 0 dB, right +2.272227 dB, left -2.272227 dB. B playback R/L RMS delta: center -0.703689 dB, right +10.380500 dB, left -12.135290 dB. These are channel-ratio acoustic differences **not** absolute B Pa and not perception measurements. A right-minus-left ideal delay: ±0.235542 ms. B sample timing/phase requires independent reference audit.
- **Browser/headphone audition:** PENDING manual interaction and user assessment.
- **Independent reviewer:** PENDING; implementation author's own checks do not satisfy review gate.
- **Physical SPL calibration for B:** UNVERIFIED. Frequency-domain conversion assumes uniformly sampled complex transfer data and preserves phase; measured reference-plane time origin requires review.
- **Promotion:** NOT_ADOPTED; no production API/Studio main modification.

## Known interpretation risks

Measured HRTF may already embed free-space propagation and is not a calibrated Pa-per-source-Q transfer. The comparison therefore applies a documented shared playback gain and B-wide RMS matching for listening, rather than asserting equal physical source-to-ear loudness. Externalization also depends on subject-specific HRTF, room and head motion. Unknown HRTF recording plane, headphone equalization and 1cm/contact extrapolation remain out of scope. Failure to improve subjective experience is an informative research outcome, not a bug.

## Independent review checklist

- [ ] Independently inspect SOFA convention, `SourcePosition`, receiver mic positioning, channel order, sample rate, HRTF phase/time origin, reference normalization.
- [ ] Verify analytical SI model, fractional-delay filter, resampling, signal derivative, physical pressure vs playback gain.
- [ ] Confirm actual 3 poses are measured, not interpolated or extrapolated, and frequency band is justified.
- [ ] Independently rerun six WAVs and compare hashes/listening UI.
- [ ] Human creator's blinded notes and playback equipment.

Above CI URLs/artifact are verified. Future review results and human listening records must be appended separately rather than guessed.
