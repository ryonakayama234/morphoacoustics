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
python -m mypy --follow-imports=skip experiments/039_og2_prepared_graph/og2.py experiments/039_og2_prepared_graph/run.py
# With a Wolfram Engine / wolframscript installed:
wolframscript -file experiments/039_og2_prepared_graph/wolfram/verify_og2_oracle.wl
```

Use a **new non-existing** output directory each run. Generated artifact `decision.json` includes raw complex matrices, provenance hashes, the **actual clean Git checkout HEAD** and GitHub run identity when under Actions; `evidence_sha256.txt` hashes that exact JSON. Pass `--expected-head-sha <SHA>` to reject mismatched source checkouts (the workflow always supplies it). This is an evidence-schema v2 extension only; scientific oracle and thresholds stay frozen. The dedicated Wolfram verifier evaluates the independent `.wl` from scratch and compares all 7x4 complex entries and isolated exact fractions against the immutable checked-in reference (failure exit on mismatch). CI runners may lack `wolframscript`; the external Wolfram evaluation is recorded separately in #98, not deceptively claimed as a GitHub job. The two Wolfram files are a frozen independent oracle (source and numbers). `PREREGISTRATION.md` freezes gates before Python code; `AMENDMENT_001.md` records an openly corrected dimensional-normalization defect discovered after implementation. Do not mislabel the amended run as a new blind prospective validation.

**Decision rule:** green numerical results only mean PROVISIONAL_NUMERICAL_PASS / REVIEW_PENDING / NOT_ADOPTED. Independent **AI critical review plus machine evidence** is mandatory per #98, not unavailable human signatures. The transparent post-implementation amendment remains a controlled regression, not a new prospective blind replication. OG-0 audit #93 and OG-1 #94 remain separate unsatisfied adoption dependencies; fixing OG-2 alone is not automatic permission to merge.
