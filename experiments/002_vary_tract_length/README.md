# 002 — Vary tract length

## Hypothesis

With a lossless closed-open 1D tract and all other acoustic parameters held fixed, shortening the tract raises its first quarter-wave resonance.

## Intervention

Compare two uniform rest geometries with total lengths 0.17 m and 0.12 m. The gesture score is empty so only morphology changes.

## Controlled variables

- section count: 10
- cross-sectional area: 3e-4 m²
- speed of sound: backend default (343 m/s)
- air density: backend default (1.21 kg/m³)
- outlet load: ideal pressure release

## Expected result

The first input-impedance peak should be close to `c / (4L)`, so the 0.12 m tract should peak at a higher frequency than the 0.17 m tract.

## Acceptance criterion

Both measured peaks are within 1% of the analytic quarter-wave prediction and `peak_0.17m < peak_0.12m`.

This experiment is also encoded as a stable invariant in `tests/scientific/test_vertical_slice.py`.
