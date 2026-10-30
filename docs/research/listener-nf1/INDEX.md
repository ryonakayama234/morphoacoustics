# EL-NF1 — research-only index

**RESEARCH_ONLY / NOT_ADOPTED / Draft / independent of unmerged PRs #83/#129/#138/#153/#233.**

- [Frozen preregistration](PREREGISTRATION.md): metrology, holdouts, comparators, quantitative gates; committed before implementation or measured evaluation.
- [System](SYSTEM.md): source/receiver separation and model architecture.
- [Data contract](DATA.md): SOFA validity, reference plane, provenance, failure classes.
- [Experiment](EXPERIMENT.md): WSL2 commands and CI reproduction.
- [Results](RESULTS.md): append-only audit ledger (synthetic tests ≠ empirical evidence).
- [Decisions](DECISIONS.md): no premature adoption / independent review policy.

Runnable research-only code: `experiments/045_el_nf1_receiver/run.py`; tests: `tests/test_experiment_045_el_nf1.py`. Not a Core, ASMR runtime or Studio feature.
