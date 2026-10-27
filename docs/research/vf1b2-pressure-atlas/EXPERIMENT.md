# VF-1B2 Pressure Atlas / EXPERIMENT — preregistered Gate 0
Date: 2026-10-27. These criteria precede experimental source code.

## Research hypothesis and falsification
Hypothesis H0: the currently identified sources have genuine rigid-glottis measured pressure profiles, but our repository **does not yet possess a complete qualified numeric, spatially registered wall-pressure dataset** appropriate for a geometry-matched simulation comparison. The Gate-0 result is an *availability and qualification audit*, not proof or rejection of any aerodynamic solver.

Falsify H0 only by recovering the full attributable numerical measurements, tap coordinates and sides, pressure sign and reference, model geometry, boundary conditions and uncertainty budget; a plotted model curve or invented taps are insufficient.

## Gate design (fixed before coding)
- G0A SOURCE: valid cited source, distinct M5/M6 geometry and tap-axis semantics. Printed table Q and image-only p(z) are not interchangeable.
- G0B TAP DATA: numeric measured p(tap) and measured tap coordinates available, calibrated, units/sign/reference traceable; source/paper or audited digitization with error ledger. Missing or wrong typed numeric values fail closed.
- G0C COMPARABILITY: same actual geometry, inlet/outlet and wall side as model, including any 3D/side mismatch. Without positive **independent** audit, NO-GO for numeric model comparison.
- G0D UNCERTAINTY: absolute and/or relative pressure measurement uncertainty, digitization and scale error provenance separately qualified. Do not assert probabilistic confidence from reported instrument-accuracy bounds.
- Result `SOURCE_DISCOVERED_NOT_COMPARABLE` or `REFERENCE_READY_FOR_SEPARATE_COMPARISON`; **never** `PHYSICS_VALIDATED`. Initial cases must not be declared ready merely due to published figures/flow or two coordinate anchors.
- G2 external physical agreement INDETERMINATE; G3 moving-wall pressure-work N/A; G4 voice quality NO-GO until separately established.

## Adversarial controls
1. Reject nonexistent article identifier, or falsely label M6 transverse arrays as M5 axial taps.
2. Changing `figure_only` to numeric-ready without actual measured samples must fail.
3. No geometry match, no pressure-reference/sign, no uncertainty specification => not comparable.
4. Nonfinite p values, nonpositive uncertainty bounds, missing/duplicate tap coordinates or invented calibration => reject/quarantine.
5. Control showing perfect mathematical agreement with a toy `p(z)` must still fail G0C when boundaries are mismatched.
6. Source-hash or downstream output tampering must never upgrade a `HOLD` to `PASS`.

## Bounded initial run
Register three named published candidates, review what is actually published, and run fail-closed source/comparability tests. **No fake digitized samples**, no interpolation-as-data, no parameter fit to the outcome. Independent code review and exact tested source revision are required before believing software gate success.

## Later experiment, NOT authorized by this file
Digitize or acquire verified p(tap) with pixel-to-physical-axis calibration and separate uncertainty; preregister matching geometry, fixed flow/pressure cases and held-out cases; only then run an **independent** 1D/2D/3D candidate pressure comparison, never mark moving-wall FSI solved by a static match.

## Interpretation contract
Test PASS => qualification logic behaves as specified, not a validated source. Audio quality is outside this experiment and must ultimately be judged by actual human phoneme clarity, voice-like sound and character distinction after physical gates.
