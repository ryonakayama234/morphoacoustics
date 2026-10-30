# EL-NF3 — DECISIONS / adoption boundaries

## D0 — 2026-10-30: OPEN RESEARCH
- User delegated expert execution, but scientific conclusion remains evidence-gated.
- Create independent research branch from main, not stack onto #252/#255 or merge experimental scripts into Core.
- Prior negative result #255 is frozen reference. Hypotheses H1–H4 are unproved; measured/data legality audits are mandatory.
- Use straightforward deterministic geometric / temporal methods first; no neural generator whose error modes obscure inference.
- Prefer B0/B1/B2/C1 if C2 complexity not justified by genuinely independent heldout validation.
- Freeze any successful *limited* model and its evidence as versioned baseline; investigate successors on new branches. Separate owner-reviewed adoption PR required for future `morphoacoustics_asmr` runtime and a still later Studio UI.
- No approval is implied for physical ear contact, absolute eardrum pressure, human individualization, moving-source interpolation, source/load coupling, or ASMR subjective response.

## Pending decisions
- Dataset license and microphone/reference plane; if uncertain, reject claims needing those details.
- Exact original SOFA manifest and spatial topology.
- Model/threshold review, real measured experiment execution and G3.
- Different reviewer G5 and potential adoption decision.


## D1–D3 — 2026-10-30: ACTUAL_MEASURED / G3 INDETERMINATE / NO ADOPTION

Original measured KEMAR data audit ran successfully with exact publisher MD5, observed SHA-256, coordinate-block split; original CI [41058197316](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41058197316) and its [evidence](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41058197316/artifacts/12978281733). Model-selection block error favored B2 (0.7828dB median ILD) as the eligible control; C2 showed 0.7006dB at selection stage, but was **unsupported at every final test point (0/155)** under the preregistered geometric guard. Therefore *no paired final acoustic accuracy is estimable*; G3 is INDETERMINATE, not GO, and not a proof of C2 inferiority. 80% coverage and 8 independent supported blocks per fold both fail.

The first real run's nonfinite JSON serialization bug was fixed without changing model, splits, thresholds, or withheld measurements; synthetic end-to-end regression and exact measured rerun passed, including independent-from-predictor arithmetic audit. Scientific conclusion remains negative **for applicability/coverage**. Retain Draft #257 and immutable negative evidence, do not adopt into optional ASMR runtime, Core, SMC, or Studio; do not re-use these final locations as a new blind test to tune the same model.

**Next scientific work requires a separate prospective study and independent evidence** to isolate angular simplex failure, sparse-support geometry, near-field timing, and microphone-reference/rights uncertainty. An independent scientist/reviewer G5 has NOT signed off and G4 human audition is NOT done. The original source-rights and absolute reference-plane status remain unresolved.
