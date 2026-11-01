# G0-A — candidate source evidence and exclusion ledger

Desk-reviewed **2026-11-01 JST**. Statements in this file are sourced *public metadata or publisher methods*, not an inspection of the original SOFA signals. Links are to the authoritative publisher, file indexes and journal landing pages. Any item requiring original-file examination is marked **UNVERIFIED**. External scientific and legal review: **NOT_PERFORMED**.

## K1 — TH Köln / Arend–Neidhardt–Pörschmann KU100 near-field

**Evidence anchors**
- K1-E1, original publisher's download listing: https://audiogroup.web.th-koeln.de/ku100nfhrir.html (R16-1118; SOFA and miro; separate gain-instructions document).
- K1-E2, author's 2016 paper: https://audiogroup.web.th-koeln.de/PUBLIKATIONEN/Arend_TMT2016.pdf, *Measurement and Perceptual Evaluation of a Spherical Near-Field HRTF Set* (especially pp. 357–358 for method, p. 362 for explicit dataset license).
- K1-E3, Zenodo distribution record DOI **10.5281/zenodo.4297951**: https://zenodo.org/records/4297951; public SOFA archive `NFHRIR_L2702_SOFA.zip` (Zenodo **MD5** `1310d2b015c82272cc27d10d680b6bb4`), `NFHRIR_CIRC360_SOFA.zip` (Zenodo **MD5** `6380cf3e4592e2adcb8bb01ad79f0679`). These are *publisher-listed MD5 identifiers*, **NOT** locally checked checksums or SHA256 values.
- K1-E4, indexed individual SOFA mirror (file names, not file contents): https://sofacoustics.org/data/database/fhk/ lists `HRIR_L2702_NF050/075/100/150.sofa`, `HRIR_CIRC360_NF025/050/075/100/150.sofa`. Mirror ≠ a different original dataset/head; verify provenance and equality if authorized.
- K1-E5, gain restoration explanation: https://audiogroup.web.th-koeln.de/FILES/NF_Datasets_Gains_infos.pdf, linked by publisher listing. Its publicly indexed text warns that MIRO `normalization` values do not account for varying preamplifier gains and that SOFA has no corresponding normalization entry; **do not treat raw cross-radius SOFA scale as natural attenuation**. PDF screenshot visual verification was attempted but tool timed out; confirm the document in an authorized independent audit before relying on exact correction factors.
- K1-E6, SONICOM THK umbrella catalog: https://ecosystem.sonicom.eu/databases/108, labels aggregate as CC BY-SA 4.0. Do not transfer an umbrella listing to an unverified file version without checking.
- K1-E7, AES 2017 paper: https://aes.org/publications/elibrary/elibrary-page/?id=18697, supporting independent publication of this measured near-field corpus.

**Publisher-supported attributes (not file-audited):**
- One *Neumann KU100 artificial head*, anechoic TH Köln measurement; **post-processed measured** bilateral HRIR, not raw microphone pressure or a numerical head solver.
- Full-sphere Lebedev **2702 directions × four radii**, nominal 0.50 / 0.75 / 1.00 / 1.50 m. Horizontal circular **360 directions × five radii**, 0.25 / 0.50 / 0.75 / 1.00 / 1.50 m. **0.25 m is circular-only**; full-sphere 0.25 m MUST NOT be fabricated. Candidate interior S2 shell could be 0.75 or 1.00 m, but feasibility, buffers, and independent block count have NOT been verified.
- Paper describes **48 kHz** capture and postprocessing to **128-tap** HRIR through loudspeaker/reference magnitude-and-phase compensation, adaptive low-frequency extension (paper's 200 Hz crossover), trimming and peak/dataset leveling. The effective **common absolute arrival delay may have been removed or changed**; the NF5 H1 physical-arrival claim is **not licensed by mere existence of SOFA**. ITD/relative bilateral timing and phase origin require file and algorithm audit.
- Paper describes laser distances between the loudspeaker and **entrance of the dummy head's ear canal** for alignment; this must not be silently interpreted as `SourcePosition` origin or distance to a head center. Exact acoustic source/receiver reference geometry remains UNVERIFIED.
- Author-documented **robot-arm shadowing toward rear angles** for Lebedev measurement and potential loudspeaker/receiver near-field interference. A preregistered geometry-only scope decision is mandatory; do not exclude artifact-heavy positions post hoc using acoustic outcomes.
- The publisher **explicitly states near-field set is available under Creative Commons CC BY-SA 4.0** in K1-E2. This is *direct publisher evidence of the dataset's license*, not merely the paper's license; track citation, attribution, ShareAlike compliance and identity of the actual file/edition. Zenodo web extraction does not display a named right in the Rights field. Individual files/version/possible additional notices were not opened. Do not assert the dataset has no license. Commercial use is **not categorically excluded** by CC BY-SA 4.0; legal analysis of redistribution and what constitutes an adaptation of the original data, including weights and application assets, is not yet complete.
- **Original-data independence vs NF1–NF4 = UNVERIFIED**: this appears a distinct documented TH Köln KU100 acquisition from Aalto, KEMAR and SCUT, but a named repository/corpus and visual inspection are not a proof against identical-source/derivative overlap.

**K1 provisional result: `G0_A_PRIMARY_SOURCE_AND_LICENSE_CLAIM_FOUND`, but `G0_VERDICT=BLOCKED_PENDING_ORIGINAL_AUDIT`.** Need: original SOFA access consent/identity and full-file SHA256, receiver mic plane, absolute/relative time convention, `Data.Delay`, calibration and distance-gain treatment, source/receiver coordinate convention, left/right orientation, and splitability with >=8 truly independent spatial blocks per S1/S2. Neither 2702 positions nor several radial shells means independent *heads*.

## N1 — NHK HATS 2026 paper candidate

**Evidence anchors**
- N1-E1: https://www.jstage.jst.go.jp/article/ast/47/1/47_e25.48/_article/-char/en
- N1-E2: https://doi.org/10.1250/ast.e25.48 (technical report, *Measurement of near-field head-related transfer functions: Dense measurements in the upper hemisphere*, Matsui et al., Acoustical Science and Technology 47(1), 47–55, January 2026).

Publisher's abstract describes a measured NHK Science and Technology Research Laboratories HATS, **865 angular directions × 27 source distances 0.20–1.50 m in steps of 0.05 m**, **upper hemisphere** (not full sphere), and a purpose-built source in anechoic conditions. The J-STAGE landing page shows **Supplementary material (0)**. No accessible publisher-authorized original HRIR/ SOFA data archive, data-file license, mic/reference plane or file-level conditions were verified during this desk audit. The article's **CC BY-ND 4.0** is a copyright statement for the *article*, **not proof of a measured-data license**. Do not infer data is unavailable worldwide from failure to locate it here.

**N1 provisional result: `G0_VERDICT=BLOCKED_NO_VERIFIED_ORIGINAL_DATA`; literature-only.** Contact or locate primary original distribution before reconsidering; no automated scraping, private attachment inference or silent simulation substitution.

## Historical exclusion register (not fresh NF5 truth)

- NF1/NF2: Marschall/Aalto Zenodo 7316545, [PR #252](https://github.com/ryonakayama234/morphoacoustics/pull/252), [#255](https://github.com/ryonakayama234/morphoacoustics/pull/255).
- NF3: KEMAR Zenodo 7626148, [PR #257](https://github.com/ryonakayama234/morphoacoustics/pull/257).
- NF4: SCUT ten measured subjects, [PR #261](https://github.com/ryonakayama234/morphoacoustics/pull/261). **Negative must persist**: C4 only 242/344 supported (70.35%, below 80%); matched ILD median C4 2.34171 vs prereg B3 2.06708 dB; posthoc B0 1.53527 dB; CI crossed zero. No retrospective NF5 rescue.
- The TH Köln KU100 **Zenodo archive**, TH Köln publisher URL and SOFA mirror are **aliases/copies of the same candidate source family**, never three independent final datasets.

## Priority of next audit
1. K1 original file/edition legal and hash verification with permitted controlled access; independent rights reviewer to inspect actual notices. Until then no data access under this milestone.
2. K1 physical measured-plane, timing and leveling audit, including whether onset/common propagation time survives processing and whether first two full-sphere interior shells permit honest prereg splits.
3. K1 geometry-only **future authorized** G0-B evaluation: spatial block independence, angular buffer, S1/S2, receiver reference and final truth separation.
4. N1 original-data discovery through publisher/author and verified license, otherwise remain BLOCKED.
