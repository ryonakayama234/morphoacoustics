# EL-R2-S1 Gate B — research-only synthetic acoustic port solver

This directory contains only an **isolated numerical research adapter** around the existing Core `UniformTube.transfer_matrix`, plus an independent *frozen* Wolfram traveling-wave reference. It has no voice/body source, biological ear, actual source calibration, HRIR, ASMR perceptual model, physical contact, audio renderer, or Studio feature.

## Provenance and immutable inputs

- Gate A source: [Draft PR #158](https://github.com/ryonakayama234/morphoacoustics/pull/158), exact head `489111e19ffa18b21c4c4cadba8ef19f84e11bb4`.
- Frozen oracle original `wolfram_oracle_18.json` Git blob `f89ccf20cb60019c4487873a13af678e983beb6b`.
- Frozen Wolfram source `wolfram_oracle_18.wl` Git blob `fa8c2112f36f2b7119d40e8125e4d979ba091eef`.
- Gate B design review: [Draft PR #228](https://github.com/ryonakayama234/morphoacoustics/pull/228), prospective [PROTOCOL-V1](https://github.com/ryonakayama234/morphoacoustics/blob/research/el-r2-s1-gateb-design-20261027/docs/research/listener-r2-s1-gateb/PROTOCOL-V1.md).

**Only use Git-blob-exact copied source files**; do not silently regenerate, alter primary comparison thresholds or relabel results. The original Wolfram predictions were disclosed before this implementation, *not blind empirical evidence*. The regression gate checks 18 full complex pressure points and three powers per row; values absent from the frozen reference are audited by separate boundary equations and power conservation.

## Run (WSL2/Linux, from repository root)

~~~bash
python -m pip install -e '.[dev]'
python -m pytest -q tests/test_experiment_el_r2_s1.py tests/test_acoustics_uniform_tube.py
python experiments/044_el_r2_s1_source_load/run.py --output /tmp/el-r2-s1-gateb-observations.json
~~~

`run.py` generates the full typed, complex SI per-port records, provenance (frozen Git blobs, SHA256 Core primitive, Python version), individual oracle discrepancies, two energy residuals, and a numerical PASS/FAIL summary. If a request is out-of-scope it fails closed with INVALID, UNSUPPORTED or NUMERICALLY_UNRESOLVED; INFEASIBLE is irrelevant. Synthetic ps and Zs are **not** measured/calibrated physical source parameters.

Wolfram reference regeneration is a **separate** scientific operation, not performed by the GitHub CI:

~~~bash
wolframscript -file experiments/044_el_r2_s1_source_load/wolfram_oracle_18.wl > /tmp/el-r2-s1-wolfram-regenerated.json
~~~

Compare numeric fields against pinned JSON rather than raw JSON formatting. The original WL source and original JSON are both SHA-pinned by `audit.py`; CI does not claim Wolfram is installed or execute this regeneration.

## Ownership and promotion

Code in this directory is an experiment, not part of `morphoacoustics` or `morphoacoustics_asmr` public runtime. No Core/SMC/Studio edits. Passing this gate can justify **GO_LIMITED_NUMERICAL**, pending independent science/code review, but does not justify measured acoustics, ear morphology accuracy, time-domain sound, audible ASMR, or production admission. All downstream work requires separately registered Gate C/D and an audited, version-pinned optional ASMR adapter.