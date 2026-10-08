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

Every run needs a **fresh, empty output directory**. Reusing an existing
directory with files raises `FileExistsError` before any experiment output is
written. This is intentional: a rejected run must never leave earlier
successful WAV/trace artifacts in the same directory. For a second run use
another path, such as `--output-dir experiment-029-output-2`. The runner never
automatically deletes user files.

The audited numerical stack is **NumPy 2.4.6**. The dedicated workflow installs
that version. The runner also refuses a different NumPy version; feasible
endpoint/waveform SHA-256 hashes are checked against the original audited
Experiment-029 artifact, not just against the other condition from the same
run. These additional audit checks do not change any frozen task, morphology,
or scientific threshold.

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
