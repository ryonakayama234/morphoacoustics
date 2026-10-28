# RESULTS — EL-R2-S1 Gate B experiment ledger

**2026-10-28: numerical implementation candidate.** Canonical frozen reference: Gate A PR #158 head `489111e19ffa18b21c4c4cadba8ef19f84e11bb4`; JSON blob `f89ccf20cb60019c4487873a13af678e983beb6b`; WL blob `fa8c2112f36f2b7119d40e8125e4d979ba091eef`.

## Evidence categories

- Preliminary offline numerical preflight: tests executed against a **manually reconstructed** 18-row local test fixture, NOT a verified Git-blob-exact copy, so this by itself cannot pass the immutable-oracle gate. This data is developmental, not validation. Exact SHA test intentionally excluded from this early preflight; it must pass in CI with the independently frozen GitHub original.
- Frozen-oracle authentication, GitHub CI 3.11/3.12, exact-head run and repository regression: **PENDING GitHub workflow evidence** as of initial file creation. Do not claim completed until verified against the actual workflow jobs and head SHA.
- Independent science/architecture peer review: **NOT PERFORMED** by own implementation or GitHub CI. Separate review remains necessary for promotion.
- Empirical source/ear acoustics Gate C, ASMR perceptual Gate D, product/Studio: **NOT AUTHORIZED / NOT RUN**.

## Preliminary falsification observations

The synthetic source-match null predicts 2/3 Pa terminal magnitude for all frozen lengths and frequencies; frozen area intervention predicts approximately 0.4492470594476995 Pa at A=6e-5m², L=.025m, 3kHz. These predictions originate in *disclosed, non-blinded* Gate A Wolfram calculations. The implementation suite also injects malformed inputs and mutated source/flow/phasor/loss conditions so they cannot silently pass as legitimate numerical evidence.

## Decision log

Only mark **GATE_B_TESTED_PASS** after both CI versions and the frozen-blob SHA pin pass, with output artifact linking exact head SHA. Even then, use **NUMERICAL_CANDIDATE_PENDING_INDEPENDENT_REVIEW**, not an assertion of physiological or perceptual readiness. Record any failures by case, field, residual, implementation commit and CI link; do not loosen frozen acceptance thresholds retroactively.