# VF-1B2 rigid Gate B0 — local mathematical pilot results (2026-10-31)
**Scope: low-Re fixed-wall analytic control only; no glottal self-oscillation, no human-voice or moving-wall claim.**

## Chronology and verification level
- SYSTEM, DATA, EXPERIMENT preregistration were committed on this branch **before** executable source, through commit `7cd56559b0dd106503980a559daffcf49a9505e7`. All numeric cutoffs and test cases in the registered protocol were fixed before the pilot code.
- Research candidate `experiments/050_vf1b2_rigid_reference/rigid_reference.py` and independent analytic tests were subsequently committed; no code from unmerged SFI-2, SFI-3, VF-1A, VF-1B1 was imported.
- **Local standard-library Python execution:** 7/7 tests passed (H0–H5, rejection, corruption controls). This is not a GitHub Actions/external-review verdict. Workflow is supplied; exact-branch GitHub CI and reviewer outcome must be checked separately.
- The first local test run had 6/7 passing: an **extra, unregistered** intermediate-N 2%-force-error assertion was stronger than the frozen H4 criterion and failed at N=4. It was removed, not used to change the registered H4 criterion (error must decrease with refinement, final N32 relative error <0.001). The discrepancy is preserved here for audit and is **not** evidence of physical model failure.

## Independent analytic reference
For a fixed channel `h(z)=h0[1+s(2z/L-1)]`, the pressure-driven lubrication theory gives `Q_exact=2 w h0^3 (1-s^2)^2 DeltaP/(3 mu L)`. Candidate uses *cell-midpoint integration* of resistance instead of that analytical formula.

At DeltaP = 0.4 Pa, with preregistered geometry and fluid:

| slope s | exact Q [m3/s] | candidate Q (N32) [m3/s] | relative error | max-Re conservative bound |
| --- | ---: | ---: | ---: | ---: |
| -0.2 | 2.34626121547e-8 | 2.34646805105e-8 | 8.81554e-5 | 0.47059 |
| 0 | 2.54585635359e-8 | 2.54585635359e-8 | 2.22e-16 | 0.340385 |
| +0.2 | 2.34626121547e-8 | 2.34646805105e-8 | 8.81554e-5 | 0.47059 |

Taper relative Q error vs N=4/8/16/32: `0.00561630 / 0.00140894 / 0.000352544 / 0.0000881554`. Error contraction approaches fourfold with midpoint refinement; frozen H1 requires >=3.8x. For s=+/-0.2 the *flow is equal within roundoff* but 25%-length pressure differs: 0.248892 vs 0.339172 Pa at N32, proving that orientation changes the local load even when the total Stokes resistance matches.

N32 uniform channel at 0.4 Pa: virtual lower/upper tissue force approximations `2.666015625e-5 / 1.333984375e-5 N`, against analytical `2.666666667e-5 / 1.333333333e-5 N`. **These are static virtual forces, not moving tissue work.**

Discrete input power vs sum of all cell viscous losses is equal to roundoff (maximum reported example `1.65436e-24 W` residual). This equality is partially by construction of the discrete resistance, so it proves algebraic consistency of this restricted control, **not** a general fluid energy law nor empirical pressure realism. Tampered loss/pressure/power receipts are rejected by separately evaluated consistency checks.

At 800 Pa the solver explicitly raises `UnsupportedRegime` (Re/Mach guard). This is a scientifically important negative result: high-pressure glottal flow must **not** be described using this Stokes model. No pressure/force prediction for physiological 400/800/1200 Pa is validated.

## Gate interpretation
- G0 (local evidence + registered assumptions): **LOCAL_PASS / GITHUB_CI_PENDING**.
- G1 (fixed-wall low-Re mathematical control): **LOCAL_PASS_LIMITED**, pending exact-source CI and independent code/science audit. No simulated FSI.
- G2 (published geometry-matched measured pressure/flow): **INDETERMINATE_NOT_VALIDATED**.
- G3 (moving-wall self-oscillation): **NOT_APPLICABLE**.
- G4 (receiver sound / creative quality): **NO_GO_NOT_EVALUATED**.

## Critical STOP before moving-wall VF-1B2
The low-Re fixed-wall pressure law is **not** a valid surrogate for realistic high-pressure glottal force, separation, or tissue-work; its damping and energy identity cannot be carried into moving-wall FSI without new derivation. Before B2c, obtain an independently auditable moving-wall mass/momentum/energy formulation with advective total enthalpy, nonnegative loss constitutive law, signed fluid/structure pressure work, correct mean-vs-acoustic flow port boundary, documented compressibility assumption, and external reference relevance. If unavailable, record HOLD; do not attempt a prettier source signal or merge into Core main.

## Research references
- Li et al., 2020, J Biomech Eng, DOI 10.1115/1.4044033: 1D momentum-based glottal ROM, context-specific 3D comparison.
- Energy-based fluid-structure model of the vocal folds, IMA J Math Control Info (2021), DOI 10.1093/imamci/dnaa031: power-preserving FSI concept.
- M5/M6 source audits PR #222 and PR #217: geometry/instrument mismatches prevent treating them as direct moving-wall reference data.
