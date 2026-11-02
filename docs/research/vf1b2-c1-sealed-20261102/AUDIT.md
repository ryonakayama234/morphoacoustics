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

## 2026-11-02 exact-HEAD independent Codex P2 corrective amendment
The initial 6/6 CI success at `a8034c4f40c53173625356fcb3a705c0e593eee1` was NOT a sufficient audit. Independent Codex review identified two material P2 flaws:
1. An intermediate raw trace velocity could be changed to 100 m/s, injecting approximately 0.5 J of fake kinetic energy, and still pass because only final accumulated energy was checked.
2. A saved 6001-tick trace could be truncated to two ticks, or a static null could be relabeled with nonzero initial fixture metadata, because coverage/fixture initial state were unchecked.

Fixed with no modification to original source generator or original prereg thresholds: independent audit now computes signed energy residual at **every tick** using cumulative damping quadrature, and checks complete duration, sample count, sample time and exact initial-state binding. Added two adversarial tests; local result **8/8 PASS** on Python 3.13.5. Damped 1us maximal trajectory residual (not merely final) = **7.711825241826593e-14 J**, normalized **1.0748189915569494e-6**; lossless maximal = **2.1123438399338974e-15 J**. Both meet the original `3e-10 J` and `5e-4` limits at every tick. Earlier CI evidence remains historical and must not be relabeled as a current-head independent review success. New GitHub exact-head CI and Codex re-review needed.

## 2026-11-02 second Codex P2 corrective cycle
Review of post-first-fix commit `3eaf2c351195e437e8a28950c276feeeb8f2f8be` revealed two more authentic blind spots:
- Signing only one mid-trajectory velocity negative passes energy (kinetic and damping are even in velocity), but contradicts position evolution. Remedy: independently reconstruct signed v from saved 5-point x stencil, compare each tick, reject `KINEMATIC_MISMATCH`.
- NaN raw times passed the old `abs(t-expected)>tolerance` comparison because comparisons with NaN are false. Remedy: explicit `isfinite(t)` before clock comparison.
Additionally audited fixture SI signs/nonfinite parameters, gamma, computed gas and energy finite values. Preserved original `solver.py` bitwise unchanged and underlying raw trace digests. Local test suite now **11/11 PASS** after adding review-negative tests for signed v, NaN t, nonfinite P0 and negative density.

An intermediate local test first expected a 100m/s forged velocity to raise `ENERGY_LEDGER_FAIL`; the new independent kinematic check rejected it earlier with `KINEMATIC_MISMATCH`. Reordered check reporting so gross energy forgery retains the energy classification, whereas a pure signed-velocity flip raises `KINEMATIC_MISMATCH`. This is classification order, not an acceptance-threshold change. Note the kinematic threshold was calibrated on already visible numerical reference, not held out; do not promote this newly added guard as preregistered physics evidence.
