# EL-NF3 — EXPERIMENT / executable protocol

Gate D0 already frozen in `PREREGISTRATION.md` at commit `df6addb58296e9945569ff3473aa65039ef959cb`, prior to any NF3 code.

D1: implement measured SOFA scanner/metadata strict validation and coordinate-only region split. Write small deterministic **synthetic physically interpretable** impulse-arrival fixtures and degeneracy/refusal tests, including seam and missing shells. Unit tests MUST pass without downloading a 346.5MB source. Strictly separate test fixture evidence from KEMAR measurements.

D2: B0, B1, B2, C1, C2 candidates and ablations. Model should consume only `training` samples; final-scoring code reads evaluation truth only after predictions generated. Output individual errors (not just summaries), geometry refusals, baseline comparisons on *identical* accepted locations, model versions and source hashes. Runner must not silently reinterpret metadata or fall back to an easier test.

D3: exact original KEMAR measured file. Before scoring, verify publisher MD5, record SHA-256 and metadata report. Run S1 and S2 spatial block holdouts. Block-paired bootstrap, 2000 draws seed 20261030; diagnostic ITD, centered spectral shape and tail. A valid test that fails hypothesis outputs REVISE_OR_REJECT; an incompatible measured data or underpowered block count outputs INDETERMINATE. No committed measured result until run and independently audited.

D4: distinct independent acoustics/code reviewer and optional separate blind headphone audition; owner-gated production adoption later. Preserve failures and evidence; never mutate prior prereg.

### Running (when code lands)
```bash
python -m pip install -e '.[dev]' 'numpy>=1.24' 'scipy>=1.11' 'h5py>=3.8'
python -m pytest -q tests/test_experiment_047_el_nf3.py
python experiments/047_el_nf3_receiver/run.py audit --sofa /absolute/path/KEMAR_NFHRIRmea_1cm.sofa
```

No real-data CI is allowed to claim success unless the genuine publisher file is downloaded, MD5 validated, dataset SHA-256 pinned and full holdout scoring performed. A synthetic CI green is NOT G3 success.
