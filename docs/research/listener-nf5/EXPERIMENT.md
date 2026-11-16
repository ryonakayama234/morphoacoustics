# EL-NF5 — EXPERIMENT / future procedure only (NOT_RUN)

**Research implementation, external data downloads and scoring have NOT been authorized. This file does not contain executable code.**

## Prospective ordered stages

### D0 — current documentation phase
- Create isolated branch from `main`, design-only Draft PR linked to #263.
- Check documented hypotheses/requirements are mutually consistent across [SYSTEM](SYSTEM.md), [DATA](DATA.md), [G0](G0_DATA_QUALIFICATION.md), [PREREGISTRATION](PREREGISTRATION.md) and [COMPONENT_FREEZE_POLICY](COMPONENT_FREEZE_POLICY.md).
- Pin D0 documentation commit SHA on Draft PR. No code, datasets, computed scores or model-selection claims.

### G0 — separate later qualification (NOT_RUN)
- Independently check genuine new original measured data, rights, recording plane, source normalization and that it is not a relabelled NF1–NF4 exposed final.
- Metadata-only geometry read; fix deterministic fit/selection/calibration/final block manifests and S1/S2 roles; commit allowed G0 v1.1 refinement *before* final Data.IR inspection.
- Abort/mark BLOCKED if original, rights/permissions, usable relative receiver plane or independent spatial support cannot be established.
- Reserve no commercial rights and distribute no HRIR, audio, train-reconstructive artifacts or legally restricted coefficients.

### G1 — synthetic math and transduction (needs separate authorization)
- Test exact common/ILD algebra: map synthetic bilateral complex spectra to m,ell,arrival,residual-phase and invert; complex-to-real Hermitian checks, DC/Nyquist, 0 lag, known per-ear delays, LF ILD, high-frequency spectral notch, azimuth wrap and symmetric L/R head.
- Demonstrate that a physically plausible magnitude greater than unity is not globally refused, while nonfinite/invalid-source and unexplained uncontrolled amplification are rejected or marked invalid.
- Test multiple samples rates and response lengths including the real source-specific length after G0.
- Declare numerical tolerances, magnitude floors, time window, spectral bins and exact interpolation before model selection.

### G2 — deterministic negative controls, provenance, evaluation independence
- Reject switched-ear labels, wrong units, cartesian–spherical round-trip drift, duplicated/leaking final positions, malformed SOFA, unavailable receiver plane, invalid channel delays, out-of-domain query, missing license evidence for a claimed permission and final-truth access before seal.
- Require model-independent numerical grader to recompute coverage, band-energy ILD, ITD and spectral diagnostics from non-reconstructive manifests and/or guarded evaluation-run data, without using prediction implementation internals.
- Verify seal-manifest tampering, changed model hash, amended threshold and after-final modification all fail.
- Record normal Core CI optional dependency handling in any later code PR; no extra `h5py/scipy` required for main as a side effect of research-only tests.

### G3a — historical original-measured development only
- With separately acquired and license-permitted originals, reproduce NF1–NF4 as known/exposed *history*, never report new blind inference from their already opened targets.
- Evaluate B0/B1/B2/B3 and F1/F2/F3 on explicit split roles; run all ablations; fix primary model selection and B* on development, support threshold on independent calibration.
- One-head-only inference is scoped to that head. Document all risk indicators and refusal distributions, including support vs accuracy and negative results.

### G3b — independent original-measured final
- Refuse to run if G0 source remains blocked; do not replace new data with reused NF4 final queries.
- With one fresh original qualifying corpus, lock query sets and all model versions before any final truth. Save SHA256 source/config/prediction seals; only then reveal final HRIR.
- Calculate primary/secondary gates for *same final accepted positions* for candidate, B0 and B*, plus total coverage and all computable-position errors; block-bootstrap with fixed seed and independent arithmetic audit.
- Every G3b failure must remain append-only `RESULTS` evidence; no retroactive crossover or support tuning.

### G4 / G5 — only if relevant after numeric evidence
- G4 is prospective blinded perceptual study **if claiming listening quality**; reference original HRIR vs B0 vs selected model using same stimulus/headphone and level controls, counterbalanced trials, listener-level units. No claim about ASMR/touch without actual properly designed study.
- G5 independent acoustic-science and code review of original calibration/rights, causality/phase, per-block statistical inference, numerical integrity, true blind separation and source-version hashes. Automated code reviewer or self-conducted arithmetic audit is NOT an independent acoustics sign-off.

## Proposed future paths (not yet created)

Research-only source under a uniquely assigned `experiments/<next-id>_el_nf5_cue_field/`, isolated tests and workflows, with dependency isolation from Core. **Do not preallocate experiment number without checking latest main.**

Review content freeze at exact SHA for candidate, not GitHub action status. Change to Core, `asmr/`, Studio or publication requires a **different authorization**, adoption plan and distinct PR. No import from unmerged NF1–NF4 branches without explicit dependency decision.
