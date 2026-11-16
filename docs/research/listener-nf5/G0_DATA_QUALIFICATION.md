# EL-NF5 — G0 original measured-data qualification and hard STOP

**Status: prospective checklist only / NOT_RUN. G3b is BLOCKED until a qualified, genuinely independent source exists.**

## G0A original-source discovery — no acoustic evaluation

1. For each proposed new dataset identify publisher, original file host, paper and dataset DOI/accession (distinct), original distribution terms, withdrawal/restriction, personal/biometric implications, explicit right to download and analyze for this research. *Publication CC terms do not necessarily grant data rights.*
2. Require a reachable intact **original** near-field measured bilateral HRIR (not only an interpolator, plot, synthetic HRTF or unreleased paper). Obtain original SHA256, published checksum if available, source filename and controlled storage location. Do not put data or raw measured responses in Git.
3. Audit SOFA convention, original metadata, left/right orientation, single vs multiple head identities, sampling rate, FIR length, delay, angular/radial coordinates, units, recording plane, open/blocked/measured ear condition, stimulus and free-field equalization, source direction convention, source-to-head vs source-to-ear distance definition, absolute normalizations and measurement uncertainty.
4. Check external measurement dependency from NF1–NF4. Same original file, duplicated head, derivative/repackaged version, previously inspected final target or unknown shared source provenance fails **fresh independent G3b evidence** even with a different file name or split. If uncertain, record `INDEPENDENCE_UNVERIFIED` and stop G3b.
5. For the NHK 2026 HATS report, treat 27 measured distances × 865 directions as **paper-level report only**. Verify actual original SOFA/IR availability, license, measurement-plane and independent status before naming it a final dataset. No assumption that these files are public.
6. License may permit noncommercial evaluation but prohibit commercial derivative delivery: **research eligibility and Studio adoption eligibility are different fields**. Unclear rights → no distribution, no model weight release, and explicit `RIGHTS_UNVERIFIED`.

## G0B geometry-only feasibility (before new final acoustics)

Given qualified original location metadata *only*, record coordinate transforms with a reference diagram; angular duplicate/missing bins; radii and direction counts; target interior radii with bracketing measured shells; effective coarse angular sectors and deterministic forbidden buffers; subject/head identity; effective independent blocks. The exact data-dependent angular cells and block IDs can be added in a **G0 geometry-only, versioned amendment**, with its own commit SHA, before any new final HRIR truth inspection. Never inspect Data.IR numeric values to tune geometry-only partitions.

- `S1`: spatially withheld angular regions, in-range measured radii eligible for training.
- `S2`: spatially withheld angular regions and an interior test radius with neighboring shorter/longer training radii; remove target-radius data from that head's model fit.
- Split roles on independent heads when available; within one head, block-separate **fit**, **hyperparameter selection**, **support calibration** and **blind final**, with identical final queries for all comparators.
- Require >=8 accepted independent spatial blocks **for EACH S1/S2** and >=80% potential accepted eligible targets per condition; assess feasibility geometrically, not from HRIR accuracy.
- Distances/directions are NOT independent persons; no claim that head-level sampling can be inferred from many spatial positions.
- Record exact partition algorithm/seed/blocked angular extent; forbid train/selection/calibration leakage into final target acoustic responses.

## G0C risk and STOP/GO output

A machine- and human-readable G0 receipt (planned, not created yet) must contain:
```text
source_id, original_url, sha256, acquisition_timestamp
published_license, actual_data_license, redistribution_and_derivative_permissions
SOFA_convention, sampling_rate_hz, Data.Delay policy, coordinate_frame, receiver_plane
head_ids, positions_per_head, directions, radii, effective_independent_blocks
source_stimulus_reference, equalization, gain_normalization, uncertainty
historical_overlap_ledger, split_manifest_hash, final_truth_access_policy
G0_verdict, exact_reason, auditor_identity, review_status
```

Decision: `QUALIFIED_LIMITED` only when the original is auditable, the selected measurand and necessary reference plane are interpretable, independent new final evidence exists, and spatial partitions can support honest evaluation. Any missing critical item → `BLOCKED`, `INDETERMINATE` or `CLAIM_RESTRICTED` with a reason; no silent imputation, source swap or retroactive use of old NF4 final values.

If absolute source gain is unresolved but *relative* L/R HRIR are still valid, it may be qualified **for relative-only** metrics, never absolute pressure. If an ear-microphone location remains unknown, only a clearly limited measured-channel claim may be qualified after explicit reviewer acceptance; no canal/eardrum claim. Missing rights for acquisition/analysis → hard STOP.

## Order constraint

D0 document commit → initial G0 source/metadata-only audit → prospective G0 geometry-only amendment and frozen query roles → separately authorized G1/G2 implementation → G3a development on previously exposed data → seal selected model, calibration and predictions → **first final truth access** → G3b evidence audit → independent review. Keep original final data sealed before prediction; record checkable hashes. Never claim a sealed prediction if execution logs allow pre-seal final truth to enter training.

**No data download, permission acquisition, computation, repository workflow or CI has been performed in this design-only PR.**
