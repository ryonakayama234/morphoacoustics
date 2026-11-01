# EL-NF5 G0-A2 — decisions (append-only)

## D1 — 2026-11-01 JST: bounded execution authority
- Owner: "実際の専門知識・作業詳細は自由に裁量をもって遂行 ... お任せします" after discussion of G0-A2. This authorizes G0-A2 work, **not** automatic model/Studio/API adoption or raw G3b truth access.
- Branch independent from `main`; keep original D0 PR #264 and G0-A PR #266 unchanged; no automatic merges.
- Archive byte acquisition for integrity is **separate from acoustic-value access**. Original SOFA is never committed/uploaded. Inspect metadata and hashes only, no `Data.IR`, `Data.Delay` values or geometry-split IDs.
- Original publisher dataset CC BY-SA statement permits a scoped research access interpretation. **Independent rights review is not performed**, so commercial-derived assets and redistribution are blocked.
- Gain factors are recorded as publisher-provided with precision caveat, not treated as calibrated Pa or a verified propagation law.
- 128 taps and 1.5-m free-space delay comparison motivates Q1 investigation, but does not logically establish absolute-delay removal. Native 375-Hz bin spacing motivates Q4 investigation, not an automatic failure.
- No model learning in G0-A2. Future model default is transparent classical spatial regression/local interpolation, rather than neural epochs, but that study requires separate authorization.

## D2 — current STOP boundary
**NO G0-B OR G1–G5**, no source-to-ear physical pressure claim, no measured amplitude/time/frequency score, no final blind data, no adopted ASMR runtime. Outcome cannot be declared `QUALIFIED_LIMITED` solely from metadata. Explicit additional review and next-stage decision required.

## D3 — 2026-11-01 JST: observed original CI evidence
- G0-A2 **integrity/source-family identity** is confirmed by successful [run 41307651527](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41307651527). Original archive verified to published MD5 and local SHA256; four SOFAs structurally checked. This is a bounded GO for provenance/format **only**.
- **Rights blocker newly found**: SOFA root `License = CC 3.0 BY-SA`, paper's explicit dataset licence `CC BY-SA 4.0`. Maintain `RIGHTS_CONFLICT_REVIEW_REQUIRED`. Independent file/edition legal review must determine actual governing terms and obligations for derived weights/commercial usage before distribution.
- **Timing blocker refined**: `Data.Delay` shape [1,2] is common to measurement positions in each SOFA. No per-position delay values are in that field. No conclusion on physical absolute TOF until evidence of preprocessing, time origin, Data.IR or independently calibrated arrival is qualified with appropriate blind control.
- No G0-B geometry split, signal sampling/learning, G3b truth or production adoption. **Scientific overall decision: PARTIAL-GO-INTEGRITY / BLOCKED-MEASURAND-QUALIFICATION.**
