---
id: EL-G0A-RESULTS
status: LOCAL_SYNTHETIC_TESTED_REAL_DATA_PENDING
adoption: NOT_ADOPTED
---
# Results / decision log

## 2026-10-20 — implementation audit phase

- Research-only branch stacked above PR #114. Existing Experiment 040 unchanged.
- Source volume-velocity Q(t), free-field time-domain propagation, SOFA HRIR / complex-HRTF support, conditional recorded-source selection, stereo WAV and static listening UI implemented.
- **Local synthetic-SOFA fixture:** new tests passed; generates six WAV with 48kHz stereo and provenance. Synthetic fixture verifies processing logic **only**; it cannot prove the measured SOFA's compatibility, real head reception, or ASMR/externalization.
- **Real measured Marschall SOFA:** to be verified by CI; do not retroactively change this field to PASS without actual run and six audio artifacts.
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

Append verified CI run URLs, artifact ID and commits here in later evidence update; never claim checks without observed results.
