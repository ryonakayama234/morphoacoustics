# EL-NF2 — physical/software architecture

Source event / propagation -> measured artificial-head relative transfer -> L/R observation. This work owns only *interpolating experimentally observed bilateral receiver response in a bounded coordinate domain*. It does not model neural listening, actual eardrum pressure, cartilage transmission, wet contact or the Core Speaker/SMC pipeline.

Standalone experiment functions: `load_sofa` (strict measurement contract), `match_directions` (coordinates only), `split_coordinates` (entire direction groups held out), `predict_B0`, `predict_B1`, `predict_C1`, `assess` (independent test), `audit_evidence` (summary/data-leakage checks). Prediction logical contract: `{position_xyz_m, left_hrir, right_hrir, delay_samples, sample_rate_hz, normalization, receiver_reference_plane, domain_state, dataset_digest, predictor_digest}`. These are **research records**, not public SDK types.

C1 mathematical hypothesis: H_e(f,r) = A_e(f,r) exp(-2πifτ_e(r)). Estimate τ from training-only ear response maximum as an initial baseline; shift training HRIR to common anchor, blend in geometry/distance, restore predicted τ. Peak arrival is a *proxy*, not guaranteed direct physical path and not a neural auditory latent. Frequency-band / phase continuity require separate evaluation.

Design invariants: no source/receiver physical claim leakage, no uncalibrated absolute Pa; no direct import from unmerged predecessor PR, no production Core contract modification, no ASMR runtime entrypoints, no automatic Studio plugin. Static tests first. Time-varying filters require independent dynamic/retarded-time validation and must not be inferred from static held-out measurements.

Result is research-only until independently verified and separately adopted through optional version-pinned package.
