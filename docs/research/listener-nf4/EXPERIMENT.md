# EL-NF4 — EXPERIMENT / controlled execution

1. Freeze D0 commit first. Record immutable SHA and create Draft PR without entering production.
2. G0 inspect **only** original HDF5 metadata + `SourcePosition` (no `Data.IR` scoring, model fitting, onset/magnitude inspection). Audit data rights, microphone plane, source-reference conditions, source L/R channel order and spatial topology. Append an explicit G0 geometry-only `PREREGISTRATION_V1_1.md` with split algorithm, radial folds and exact final query selection BEFORE accessing acoustic response arrays. If metadata cannot support a valid independent holdout, stop.
3. Build a deterministic synthetic oracle (known direction-dependent arrival, ILD and radial trend) and malformed-file, duplicated-coordinate, azimuth seam, unsupported query, refusal-only, leakage and tamper tests, compatible with Python 3.11/3.12.
4. Fit B0/B1/B2/B3, C3 and C4 on training roles only. Select on development and calibrate support on disjoint calibration roles. Freeze model and guard before making final predictions.
5. For true publisher-sourced original measured SOFA, download on controlled GitHub runner (no redistribution); verify source SHA256 and metadata; predict+seal final prediction rows before reading true final HRIR; audit independently and save error summaries (not raw audio). Maintain a scientific verdict separate from CI process status.
6. G5 separate acoustics and code scientific reviewer. If G3 passes, separately propose limited optional `morphoacoustics_asmr` adoption and later separately Studio opt-in. No auto-merge.


## Executed original measured protocol and reproducibility

- D0 frozen prereg at `401089c3`; G0 pre-acoustic geometry refinement frozen `bf8a5119`.
- G0 workflow `.github/workflows/el-nf4-g0.yml` reads **only** position metadata, Data.IR SHAPE, file headers and checksum.
- Synthetic test workflow `.github/workflows/el-nf4-synthetic.yml` on Python 3.11 and 3.12 checks SH basis, coordinate seam, fixed 864-point grid, refusal, raw-model numerical finiteness, signal shift and no fake scientific pass.
- Actual measured workflow `.github/workflows/el-nf4-measured.yml` checks out exact research branch, downloads 10 public original SOFAs into an ephemeral GitHub runner, verifies source rights/metadata/hashes, fits train-only models, freezes 20 pre-truth SHA-256 seal manifests, reads withheld `Data.IR` only afterward, scores, and runs independent-from-predictor evidence arithmetic audit. Runner output is nonreconstructive JSON, never original/derived HRIR arrays.
- Outcome is a **legitimate scientific failure** `REVISE_OR_REJECT`, and workflow process exit success is intentional.

Local WSL2 reproduction for permitted **noncommercial research** with publisher originals acquired separately:

```bash
python -m pip install 'numpy>=1.24,<3' 'scipy>=1.11,<2' 'h5py>=3.8,<4' 'pytest>=8,<10'
python -m pytest -q tests/test_experiment_048_el_nf4.py tests/test_experiment_048_el_nf4_runner.py

# Original SCUT subject0001..0010_measured.sofa must already be
# present within /tmp/scut-original, with rights appropriate to use.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python experiments/048_el_nf4_receiver/run.py \
  --input-dir /tmp/scut-original \
  --output /tmp/el-nf4-repro/evidence.json
python experiments/048_el_nf4_receiver/audit.py \
  --evidence /tmp/el-nf4-repro/evidence.json
```

Do not run the code against synthetic files and label the output as human measured evidence. Never alter model choices/thresholds after seeing final rows. Reproduction of the frozen result is allowed; prospective performance claims need fresh, independent blind data. See [full results](RESULTS.md) and [frozen compact machine-readable summary](MEASURED_SUMMARY_2026_10_31.json).
