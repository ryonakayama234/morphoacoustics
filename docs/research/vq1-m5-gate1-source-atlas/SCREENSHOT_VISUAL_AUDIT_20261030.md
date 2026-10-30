# M5 Figure 2B — user-provided screenshot visual evidence receipt (2026-10-30)

**Classification:** SECONDARY_SCREENSHOT_VISUAL_REFERENCE / NOT_ORIGINAL_FIGURE_BYTES / NOT_A_DIGITIZED_PRESSURE_ATLAS.

## Intake facts (bytes examined in current conversation sandbox)
- Supplied by the creator in the 2026-10-30 conversation as a mobile browser screenshot displaying `cdn.ncbi.nlm.nih.gov`.
- Supplied JPEG: `960 × 1536` pixels, `138578` bytes, **SHA256 `acf93c2ad9c3a559c87c2bbf543074a14c241b2efe55d5691b853c43d997ad4d`**. This digest uniquely identifies **the uploaded screenshot**, not PMC's underlying original image, nor the source publication's raw figure.
- Screenshot includes browser controls, blank framing, and a displayed rasterized image containing all three Figure 2 panels. Do **not** store/redistribute the potentially copyrighted image in GitHub; keep only the hash and textual examination notes.
- Publication-side locator previously identified: [Fulcher, Scherer & Powell, JASA 2011, PMC3078031](https://pmc.ncbi.nlm.nih.gov/articles/PMC3078031/), Figure 2 raster `https://cdn.ncbi.nlm.nih.gov/pmc/blobs/b50d/3078031/6d466b56c3c5/JASMAN-000129-001548_1-g002.jpg`. The screenshot visually matches the study's panel labels and source figure description; image-byte equivalence with the original has NOT been cryptographically audited.

## What is independently visible in the supplied screenshot

| Panel | Printed uniform M5 gap | Decision |
| --- | --- | --- |
| (A) | `d=0.005 cm` | DIFFERENT SOURCE CASE, exclude from Gate1 primary |
| **(B)** | **`d=0.02 cm`** | **SELECTED GATE1 PRIMARY PANEL** |
| (C) | `d=0.16 cm` | DIFFERENT CASE, optional separately preregistered side-contrast challenge |

- Horizontal graph title: **AXIAL DISTANCE (cm)**. Vertical title: **PRESSURE DROP (cm H₂O)**. The B-panel printed ordinate runs from zero downward through 5,10,15,20,25,30. The top and right side of B show five separately annotated operating curves `P=3, 5, 10, 15, 25 cm`.
- **Selected curve:** the center **`P=10 cm`** curve in the B panel; do not mistakenly measure the `P=15` or `P=25` curve just below it. The relevant B panel has an entrance guideline near x~0.211 cm and exit guideline near x~0.511 cm (precise original-source tap coordinates require Figure 1B source qualification).
- FW is printed as filled-circle/line; NFW as outline triangle, frequently overlapping in B. Therefore cannot assert two distinct pressure measurements wherever markers coalesce. FW/NFW describe flow-attachment categories, not permanent anatomical left/right.
- **Qualitative ONLY:** along the P=10 curve, the plotted pressure DROP appears to increase from around entrance toward the straight-section end, followed by a small recovery toward exit. This agrees qualitatively with source prose and the prospective H-AXIAL/H-RECOVERY hypotheses, but **NO numeric D6/D11/D13 values were digitized or certified**, no uncertainty interval assigned and no hypothesis deemed experimentally passed.

## What this new user-provided evidence changes

**Resolved at the visual-identification level:** correct panel (B), case `d=.02cm`, selected `P=10cmH₂O` curve, axes, side legend, and visible nonuniform axial shape. The previous blanket phrase "the figure cannot be seen" is now **false**.

**Still blocked scientifically:**
1. Original publisher/PMC **Figure 2 image bytes** not obtained or SHA256-audited. The screenshot SHA is not a substitute. Original image URI's bytes could not be downloaded in the active runtime (DNS restrictions); do not manufacture original image SHA.
2. Screenshot JPEG compression, rendering and resizing may move marker centroids / obscure overlap. It is usable for **first-pass visual inspection**, not automatically the original high-fidelity figure or a full calibrated source.
3. No two truly independent numeric pixel read sessions; the user's screenshot plus one assistant visual read is **one** visual evidence event, not two independent calibrated readings.
4. No completed instrument-error qualification, independent original Figure1B tap map, FW/NFW identification at overlapping marks or real S1 pressure numbers.
5. No backside pressure field, full wetted area, normals, physical wall map or virtual-displacement mode; S2/S3 and moving-wall/audio remain HOLD/NO_GO.

## Next executable step and gate

- Record screenshot as a **secondary evidence intake**, not `source_manifest.json.figure_asset` (that field is reserved for qualified original Figure 2 bytes, which are still absent). Keep current `figure_asset=null`, `reads=[]`, `source_qualified_samples=0` and emitted `S0_SOURCE_UNQUALIFIED` scientifically accurate.
- Obtain full original Figure 2 image bytes through PMC's full-image/download where lawful, hash and inspect the original DPI/axis units; independently audit the source provenance and physical tap coordinates from Fig1B.
- Execute two separate marked-measurement passes, preserving origin/side ambiguity and separate instrument/pixel/physical-z uncertainty. Only then export an S1 candidate and review it independently.
- Until then issue [#249](https://github.com/ryonakayama234/morphoacoustics/issues/249) stays OPEN with the narrower blocker **original source bytes + quantitative independent metrology**, not general image visual unavailability.

**Cross-references:** Gate1 prereg [#220](https://github.com/ryonakayama234/morphoacoustics/pull/220), reviewed architecture [#241](https://github.com/ryonakayama234/morphoacoustics/pull/241), research executor [#248](https://github.com/ryonakayama234/morphoacoustics/pull/248), original study DOI [10.1121/1.3514424](https://doi.org/10.1121/1.3514424).
