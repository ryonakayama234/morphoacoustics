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
that version, and the runner refuses another version. Exact raw float64
waveform and endpoint hashes are recorded as **bitwise diagnostics only**:
GitHub runners can produce different low-order bits even with NumPy 2.4.6.
Instead the scientific gate checks a frozen content signature of the entire
24,000-sample waveform after quantization to a fixed **1e-9 Pa** grid,
with explicit little-endian int64 encoding. Both feasible conditions must
match the original audited output's quantized signature. Exact bitwise
equality between M_plus and M_boundary is still required *within each run*.
This portability hardening does not change the frozen task, morphology,
reachability rule, or original scientific thresholds.

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
