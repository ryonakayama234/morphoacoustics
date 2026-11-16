# EL-NF2 | Unknown-direction near-field receiver

**RESEARCH_ONLY; NOT_ADOPTED; STATIC SPATIAL RECEPTION ONLY.** Tracker #254; parents #53 / PR #83; measured predecessor PR #252 (Draft). Standalone branch from main, no dependency on unmerged predecessor code.

## Read order
1. PREREGISTRATION.md — frozen scientific identity, split and decision rules.
2. DATA.md — measurement, hash, axes, units and refusals.
3. SYSTEM.md — predictor ownership and physical claim ceiling.
4. EXPERIMENT.md — reproduction and implementation protocol.
5. RESULTS.md — append-only empirical evidence and failure ledger.
6. DECISIONS.md — reviews and gated outcomes.

## Scope
Original Marschall / Aalto 2023 unextended 48 kHz measured artificial-head SOFA, 49 directions × 4 distances (0.2–0.5 m), left/right relative transfer only. Unlike EL-NF1's same-direction distance folds, NF2 hides *entire directions* across all radii, and evaluates jointly unseen direction and distance under within-domain interpolation. All evaluation uses the original measurement domain, not 1 cm/contact/eardrum/individualized hearing.

## Boundary
Research predictor -> measured-space test -> independent audit -> **separate explicit adoption RFC** -> optional versioned `morphoacoustics_asmr` package -> opted-in Studio. Core never imports ASMR; no unapproved runtime or Studio changes. Moving-source output is a separately gated future experiment.

## References
- https://zenodo.org/records/7316545
- https://doi.org/10.1016/j.apacoust.2022.109173
- https://www.sofaconventions.org/mediawiki/index.php/SimpleFreeFieldHRIR
- https://github.com/ryonakayama234/morphoacoustics/issues/254
