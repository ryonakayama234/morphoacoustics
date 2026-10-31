# EL-NF4 — EXPERIMENT / controlled execution

1. Freeze D0 commit first. Record immutable SHA and create Draft PR without entering production.
2. G0 inspect **only** original HDF5 metadata + `SourcePosition` (no `Data.IR` scoring, model fitting, onset/magnitude inspection). Audit data rights, microphone plane, source-reference conditions, source L/R channel order and spatial topology. Append an explicit G0 geometry-only `PREREGISTRATION_V1_1.md` with split algorithm, radial folds and exact final query selection BEFORE accessing acoustic response arrays. If metadata cannot support a valid independent holdout, stop.
3. Build a deterministic synthetic oracle (known direction-dependent arrival, ILD and radial trend) and malformed-file, duplicated-coordinate, azimuth seam, unsupported query, refusal-only, leakage and tamper tests, compatible with Python 3.11/3.12.
4. Fit B0/B1/B2/B3, C3 and C4 on training roles only. Select on development and calibrate support on disjoint calibration roles. Freeze model and guard before making final predictions.
5. For true publisher-sourced original measured SOFA, download on controlled GitHub runner (no redistribution); verify source SHA256 and metadata; predict+seal final prediction rows before reading true final HRIR; audit independently and save error summaries (not raw audio). Maintain a scientific verdict separate from CI process status.
6. G5 separate acoustics and code scientific reviewer. If G3 passes, separately propose limited optional `morphoacoustics_asmr` adoption and later separately Studio opt-in. No auto-merge.
