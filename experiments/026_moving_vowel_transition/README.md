# Experiment 026 — moving vowel transition

Issue: #32  
Milestone role: C1 physical hard Gate

This experiment tests a prescribed continuous acoustic transition between the calibrated Arai /a/ and /i/ endpoint tracts.

Read [PREREGISTRATION.md](./PREREGISTRATION.md) before interpreting any output. The experiment is intentionally frozen before execution.

## Run

```bash
python experiments/026_moving_vowel_transition/run.py \
  --output-dir experiment-026-output
```

The GitHub Actions workflow `.github/workflows/experiment-026.yml` executes the same command and fails unless `decision.json` reports:

```text
SUPPORT_MOVING_ACOUSTICS
```

A failed Gate is a scientific result and must not be repaired by changing preregistered thresholds after seeing the output.

## Conditions

- **T0** — independently rendered static /a/ and /i/ halves concatenated with no crossfade.
- **T1** — one full-duration render using the primary log-area trajectory.
- **T1-ref** — T1 with finer temporal control/acoustic update cadence.
- **T2** — continuous linear-area interpolation, diagnostic only.
- **S1** — inherited 32x5 mm spatial-regrid trajectory diagnostic.

All primary conditions use the Experiment-013 fixed LF-family source. Experiment-025's cos/n² diagnostic excitation is explicitly excluded.

## Main outputs

- `decision.json`
- `provenance.json`
- `progress_trajectory.csv`
- `section_area_trajectory.csv`
- `resonance_trajectory.csv`
- `spatial_diagnostics.csv`
- `signal_metrics.csv`
- raw pressure arrays for T0/T1/T1-ref/T2
- named listening WAVs
- exploratory blind T0-vs-T1 listening package

## Claim boundary

A passing result supports only prescribed calibrated /a/→/i/ moving acoustics in the current quasi-stationary short-time transfer backend.

It is not evidence of autonomous task-level articulation, natural speech, general coarticulation, moving-boundary FSI, or TTS.
