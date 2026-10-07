# Experiment 027 — low-dimensional task-field vowel transition

Issue: #62  
Parent: #33 V3 task-level realization

This experiment is the first V3 decomposition after Experiment 026. It asks whether the calibrated `/a/ -> /i/` transition can be driven by a small task-level command instead of embedding the target area-function vector in the motor representation.

Read [PREREGISTRATION.md](./PREREGISTRATION.md) before interpreting output.

## Run

```bash
python experiments/027_task_field_vowel_transition/run.py \
  --output-dir experiment-027-output
```

The GitHub Actions workflow `.github/workflows/experiment-027.yml` runs the same command and enforces the frozen decision:

```text
ADOPT_TASK_FIELD_CANDIDATE
```

A failed Gate is a scientific result. Do not tune task locations, degrees, kernel widths, or thresholds after looking at Python output.

## Conditions

- **R0** — Experiment-026 prescribed log-area `/a/ -> /i/` trajectory.
- **R1** — the frozen three-task field realized on the same calibrated `/a/` body.
- **R1-ref** — R1 with the Experiment-026 finer temporal control/acoustic cadence.

The canonical task plan contains only task kind, normalized location, dimensionless degree, onset, and offset. Generated section-area vectors are recorded only as realized physical-state diagnostics.

## Main outputs

- `decision.json`
- `provenance.json`
- `task_plan.json`
- `realizer_parameters.json`
- `resonance_trajectory.csv`
- `r0_r1_trajectory_difference.csv`
- `task_section_area_trajectory.csv`
- `signal_metrics.csv`
- raw pressure arrays for R0/R1/R1-ref
- named R0/R1 listening WAVs

## Claim boundary

A passing result supports only a low-dimensional task-field **candidate on one calibrated body**. It does not establish morphology transfer, arbitrary phonology, natural speech, production motor control, or explicit infeasibility on another body.
