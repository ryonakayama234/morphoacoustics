# Experiment 028 — task-field morphology transfer

Issue: #64  
Parent: #33

This experiment reuses the audited Experiment-027 three-task plan and realizer without body-specific retuning, and changes only the prepared tract's axial section length from 10 mm to 11 mm.

Read [PREREGISTRATION.md](./PREREGISTRATION.md) before interpreting output.

## Run

```bash
python experiments/028_task_field_morphology_transfer/run.py \
  --output-dir experiment-028-output
```

The dedicated GitHub Actions workflow fails unless `decision.json` reports:

```text
SUPPORT_TASK_TRANSFER
```

## Conditions

- **T0 / M0** — Experiment-027 calibrated reference body.
- **T1 / M1** — same frozen task plan on the 1.10x axial-length body.
- **T1-ref** — finer M1 temporal/acoustic cadence.

The body-specific /i/ fixtures are observer references only; the realizer receives the /a/ start body plus the canonical task plan.

## Main outputs

- `decision.json`
- `provenance.json`
- `task_plan.json`
- `realizer_parameters.json`
- `morphologies.json`
- `metric_task_coordinates.csv`
- `resonance_trajectory.csv`
- `m0_m1_trajectory_difference.csv`
- `task_section_area_trajectory.csv`
- `signal_metrics.csv`
- raw M0/M1/M1-ref pressure arrays
- named M0/M1 listening WAVs

## Claim boundary

A pass establishes only the frozen V3b 1.10x axial-length TASK_TRANSFER fixture. Explicit INFEASIBLE/no-fallback behavior remains V3c.
