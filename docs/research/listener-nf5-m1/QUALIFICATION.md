# QUALIFICATION — M1-A and geometry-only G0-B hard gates
## Gate chronology
- G0-A2 historical: original ZIP MD5/SHA and 4 SOFA structures verified in PR270; file notice vs paper license discrepancy; physical reference plane/TOF/spectral suitability and rights BLOCKED.
- M1-A: review publisher measurement chain, ear recording plane, loudness factors and their precision, 128-tap window/origin, channel-specific postprocessing, sample rate and relative acoustic target. A credible answer must cite edition-specific original author material, not infer physical truth from SOFA field existence.
- M1-B: read **ONLY SourcePosition numeric geometry and HDF5 non-acoustic metadata** from verified original. Do not open Data.IR/Delay numeric values. Geometry audit is NOT performance/truth access.
- M1-C: freeze exact geometry role hashes and full operational candidate/evaluation amendment **before** any NF5 final acoustic samples could be read. Independent reviewer receives an immutable SHA.
## G0-B checks
1. Verify source archive bytes against `1310d2b015c82272cc27d10d680b6bb4` MD5 and `5f3a4c6df0f0c0bbbce6639f41129a20bc03603d19316db74637f70bfa1ff5f9` SHA256. Refuse mismatch.
2. Strict ZIP allowlist for four SOFA members, no duplicate traversal/symlinks/oversized extraction; no upload of original files.
3. Read `SourcePosition` [2702,3] spherical degree,degree,metre. Verify finite az/el and radius against file-specific nominal shell. Match original direction order across four shells by rounded *direction* only and require unique measurements; any mismatch STOP, no guessed assignment.
4. Direction block: az normalized [0,360) and elevation [-90,90], 20° az ×10° elev cells; angle to nearest non-fit direction is great-circle (not raw az difference). 5° prohibited angular adjacency from held-out roles to fit; cannot leak final direction on any shell.
5. Deterministic SHA256 cell-seed mapping to fit, selection, calibration, final roles; same direction/cell role across all shells. Publish only per-role counts, effective angular block counts, hashes of mapping/query IDs, not final measured data.
6. Operational folds: S1 final withheld directions at .75m (distance seen in fit); S2 final withheld directions at **1.0m** while all fit at 1.0m removed for S2. Bracketing training shells include .75m and 1.5m; S1/S2 are separate fitted scenario protocols. Neither can see final direction at any radius. Make S1 and S2 distinct target sets by fold/radius though their final directions may be shared; bootstrap unit is angular block.
7. Require >=8 eligible spatial angular blocks per S1/S2 and >=80% potential geometric support at G0-B; calibrated/model-specific supported coverage and >=8 actually accepted blocks cannot be asserted until G3b. Do not assert angular blocks are iid physical replicates.
8. The scheme can be geometry-amended prospectively (numbered version and new commit) only **before** opening final original Data.IR. Any failure of geometry gate -> INDETERMINATE/BLOCKED, not automatic re-labeling or relaxation.
## Stop conditions
`WRONG_ARCHIVE`, `UNSAFE_ZIP`, `UNSUPPORTED_SOFA`, `COORDINATE_MISMATCH`, `DUPLICATE_DIRECTION`, `LOW_EFFECTIVE_BLOCKS`, `RIGHTS_REVIEW_REQUIRED`, `PLANE_UNVERIFIED`, `TIME_ZERO_UNVERIFIED`, `SPECTRAL_FIDELITY_UNVERIFIED`.
Scientific G0-B geometry feasibility may be recorded while independent legal/metrology review is pending; it must **not** promote overall G0 to QUALIFIED_LIMITED if endpoints are still scientifically ambiguous. No privileged final acoustics in this scope.
