# Experiment 039 — prepared physical graph, OG-2

Issue #96, design-only tracking; this branch is an explicitly isolated executable research specimen.

Two immutable, named rigid tubes + one typed ideal p/U series junction → structural validation → backend capability validation → prepared 2-organ graph with stable topology SHA-256 → complex 2-port acoustics via **adopted** Core UniformTube.

The physical interface conserves **pressure** and **volume velocity**, not particle velocity. No voiced waveform, no FSI, no arbitrary graph solver, no Studio or production `src/` modifications.

## Reproduce locally (WSL2/Linux)

```bash
python -m pip install -e '.[dev]'
python -m pytest tests/test_experiment_039_og2.py -q
python experiments/039_og2_prepared_graph/run.py --output-dir /tmp/og2-fresh-evidence
python -m pytest -q
python -m mypy
```

Use a **new non-existing** output directory each run. Generated artifact `decision.json` includes raw complex matrices and provenance hashes; `evidence_sha256.txt` hashes that exact JSON. The two Wolfram files are a frozen independent oracle (source and numbers). `PREREGISTRATION.md` freezes gates before Python code; `AMENDMENT_001.md` records an openly corrected dimensional-normalization defect discovered after implementation. Do not mislabel the amended run as a new blind prospective validation.

**Decision rule:** green numerical results only mean PROVISIONAL_NUMERICAL_PASS / REVIEW_PENDING / NOT_ADOPTED. Independent numerical physics and code/API reviewers are still mandatory. OG-0 audit #93 and OG-1 #94 remain unsatisfied adoption dependencies.
