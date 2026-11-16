# EL-NF5 G0-A — source qualification desk audit

**Status (2026-11-01 JST): RESEARCH_ONLY / METADATA_AUDIT_COMPLETED / NO_SOURCE_QUALIFIED / G0-B_NOT_RUN / G3b_BLOCKED / NOT_ADOPTED / DO_NOT_MERGE.**

This is the user-authorized **G0-A public-source / source-rights desk-audit checkpoint only**. Tracking issue: [#265](https://github.com/ryonakayama234/morphoacoustics/issues/265). Upstream D0 remains *unmerged* [#263](https://github.com/ryonakayama234/morphoacoustics/issues/263) / [draft #264](https://github.com/ryonakayama234/morphoacoustics/pull/264), design-doc SHA `483f708140899fb16f11eff49d3dde4171e0512c`. This independent branch started from `main` at `727b11ecf103f5c087cfcb820bdec11f883e7c03`.

Scope is a **static, measured, identified listener/head** at known microphone plane, not speaker biomechanics, anatomy solver, pressure at eardrum, contact, absolute loudness, unmeasured heads, motion, or ASMR perceptual quality.

## Route
- [SOURCES.md](SOURCES.md): primary-evidence ledger, candidate-by-candidate provenance, licensing, geometry and measurement-system hazards.
- [ACCESS_POLICY.md](ACCESS_POLICY.md): anti-peeking and mandatory STOP conditions (no source signal accessed).
- [G0A_RECEIPT.json](G0A_RECEIPT.json): machine-readable provisional receipts with explicit unknown/null values; no synthetic SHA.
- [RESULTS.md](RESULTS.md): desk-audit findings; *no* sonic data, measurements or tests.
- [DECISIONS.md](DECISIONS.md): disposition, blocks and owner/review boundaries.

## Interpretation
This is a source-discovery result, **not a dataset admission**. The publisher's KU100 paper explicitly says CC BY-SA 4.0 for *the near-field set*, which strengthens the source-rights evidence; a blank/omitted license on a text extraction of a Zenodo record must not be interpreted as an explicit restriction or proof of no license. Access, exact original file integrity, matching version/attribution, proposed reuse and acoustic measurement metadata still need separate qualification. NHK has a paper but no independently verified distributable original IR.

**No original SOFA/ZIP/IR downloaded or opened**, no SHA256 computed, no geometry manifest fixed, no model built, no experiment scored, no freeze, no merge. The D0 preregistration remains authoritative for thresholds, nulls, S1/S2, B0/B*, F1–F3 and freeze policy until separately amended.
