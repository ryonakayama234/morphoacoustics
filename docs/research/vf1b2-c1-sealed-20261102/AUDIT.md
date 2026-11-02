# VF-1B2 C1-R0 — AUDIT / failed and corrected test history
2026-11-02 JST. Protocol frozen at commit `7a3d051d0041f79c319a4ac98d48c38ad0bd43ec`, before any new source code. Local prototype ran after freeze and before publication of the code files.

## Initial failed test, preserved honestly
The first local `test_spatial_force_oracle` asserted that a finite-N midpoint quadrature of **quadratic** pressure x shape-basis integrands should equal the analytic integral *exactly to 11 decimal places*. It failed:
N=16: numerical F_L-F_U = -0.0039375000000000035 N at N=8, while continuum exact -0.004 N; raw mismatch 6.25e-5 N.
The interpretation was a faulty **test assertion**, not an unexpected flow physics effect: midpoint quadrature is second-order, not exact on a quadratic integrand. The original prospective EXPERIMENT.md already specified 4x error reduction under N doubling; it did not require finite-N exact equality. We corrected only the test to check |difference from analytic| <= 2 * max individual quadrature error and factor >=3 for each grid refinement, without modifying preregistered hypotheses or numerical thresholds. The second test run passed all six tests. No counterexample is suppressed.
Original failed output and corrected output were captured locally in the conversation execution; because the first failing code was not committed, the first execution does NOT have a GitHub immutable test source SHA. This is an audit limitation, not a claim of fully retained original failed artifact.

## Scope and audit limitations
- The Python observer is separately coded from the solver and uses raw traces, but it is not an independently calibrated biological reference or an independently implemented second simulation.
- Numerical residual is assessed for one short sealed fixture; energy closure does not validate moving-wall momentum flux in a spatially varying open fluid.
- Git SHA/content integrity and fresh recomputation are separate; no claim of cryptographic authentication against a hostile repository editor.
- No human audition. No uploaded sound. No Studio panels or Takes.
- Scientific status must remain C1_R0_G1_PASS_MATHEMATICAL_SEALED_ONLY even if code CI is green.
