# Experiment 029 — phonetic task-field embodied infeasibility

Issue: #67  
Parent: #33

This experiment keeps the audited Experiment-027/028 three-task phonetic plan unchanged and changes only one PreparedMorphology capability limit.

Expected pattern:

```text
M_plus      -> FEASIBLE
M_boundary  -> FEASIBLE
M_minus     -> INFEASIBLE
```

The negative condition must stop before any physical endpoint or acoustic waveform is generated.

Read [PREREGISTRATION.md](./PREREGISTRATION.md) before interpreting results.

## Run

```bash
python experiments/029_task_field_embodied_infeasibility/run.py \
  --output-dir experiment-029-output
```

The dedicated CI workflow enforces:

```text
SUPPORT_PHONETIC_EMBODIED_INFEASIBILITY
```

A failing frozen Gate is a scientific result and must not be rescued by changing the task plan, reach endpoints, assignment policy, oracle, or thresholds after execution.

## Primary outputs

- `decision.json`
- `provenance.json`
- `task_plan.json`
- `morphologies.json`
- `task_reach_trace.csv`
- `oracle_condition_checks.csv`
- feasible raw pressure arrays

## Claim boundary

A pass supports only the calibrated frozen three-task path under this experiment-local reachability fixture. It does not establish biological articulator limits, force/contact mechanics, arbitrary morphology infeasibility, or perceptual phonetic equivalence.
