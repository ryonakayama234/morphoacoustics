# G0-A2 bounded integrity experiment (execution contract)

## Authorized sequence
0. Record **new** issue #269 owner delegation; do not modify authorization of previous #265.
1. Check publisher's source and source-specific research/redistribution rights; no inference of independent rights review.
2. In ephemeral CI workspace download `NFHRIR_L2702_SOFA.zip` from original Zenodo record (max 50 MB; pin publisher MD5). Publisher mirror can be fallback **only if exact MD5 matches**, never count as independent corpus.
3. Compute archive MD5 and original SHA256, refuse mismatched bytes. Reject ZIP path traversal, encrypted entries, non-SOFA entries for HDF metadata scan, abnormal decompression or unexpectedly large entries.
4. Inspect HDF5 root attrs and **only** datasets' names/shapes/dtypes and coordinate metadata unit/type attributes; read `Data.SamplingRate` scalar only. Never read `Data.IR`, `Data.Delay`, `SourcePosition`, `ReceiverPosition` numerical contents.
5. Emit **non-reconstructive** receipt to CI logs: SHA256, original file names/hashes, SOFA format, scalar sample rate, dimensions, attrs/units and hard-gate observations. Do not upload archive, SOFA or raw output artifacts. Dedicated synthetic tests cover hash failure and missing structural keys.
6. Review source-specific license notices and measurement methodology; document which claims remain unverified. Retain restricted original bytes only in ephemeral CI, not GitHub or project assets.
7. In this PR leave final truth unopened. Results are metadata/rights **qualification**, never acoustic prediction or physical-arrival validation.

## Execution gates
- `ARCHIVE_INTEGRITY_VERIFIED`: publisher MD5 matches archive and computed original SHA256 is recorded.
- `SOFA_STRUCTURE_CHECKED`: HDF5 opens, expected minimal keys and dimensions present; this alone DOES NOT qualify receiver plane, left/right, timing or gain.
- `MEASURAND_LIMITED`: separately justified time/ILD/level/phase claims by original measuring process, not merely HDF attrs.
- `G0B_ELIGIBLE`: only after separate science/right access review confirms rights, exact source plane, uncertainties and independent split feasibility.
- `G3B_BLOCKED`: until G0-B geometry-only split, separate code/measurement authorizations and independent blind final evidence.

## Failure and negative controls
Corrupt publisher MD5 -> hard fail. Missing `Data.IR`/`Data.Delay` -> structural fail. Malware/path traversal/oversized ZIP -> fail. Dataset containing sentinel sample values must not leak values in receipt. Same-Dataset SOFA mirror is not independent data. Archive download 429/network failure -> `SOURCE_NOT_ACQUIRED`, NOT a score and NOT an integrity pass. A safe CI run without original source is ONLY a synthetic test result.

## Reproduction
```bash
python -m pip install h5py pytest
python -m pytest -q experiments/051_el_nf5_g0a2/test_audit.py
python experiments/051_el_nf5_g0a2/audit.py --archive /private/NFHRIR_L2702_SOFA.zip --expected-md5 1310d2b015c82272cc27d10d680b6bb4
```
The second command inspects metadata only and must run in a restricted environment. Complete G0-B and G1–G5 are not part of this authorization.
