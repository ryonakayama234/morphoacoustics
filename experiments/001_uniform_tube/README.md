# 001 — Uniform tube

## Hypothesis

A lossless rigid uniform tube with an acoustically closed inlet and an ideal
pressure-release outlet has quarter-wave resonances at

```text
f_n = (2n - 1)c / (4L).
```

The same resonances should appear as maxima of the inlet-impedance magnitude
computed from the fidelity-0 transfer matrix.

## Intervention

Use a 0.17 m long, 3e-4 m² cross-section uniform tube and compare the first
three analytical resonances with resonance locations found by a dense
frequency scan of the numerical input impedance.

## Controlled variables

- sound speed: 343 m/s,
- air density: 1.21 kg/m³,
- tube area: 3e-4 m²,
- rigid walls,
- lossless one-dimensional propagation,
- ideal pressure-release outlet.

## Expected result

The numerical impedance peaks should coincide with the analytical quarter-wave
frequencies up to the scan-grid resolution.

For the default parameters the analytical values are approximately 504.4 Hz,
1513.2 Hz, and 2522.1 Hz.

## Acceptance criterion

For each of the first three modes:

```text
abs(numerical_hz - analytical_hz) <= frequency_grid_resolution_hz
```

Stable expectations from this experiment are also encoded in
`tests/scientific/test_uniform_tube.py`.

## Run

From an editable development installation of the repository:

```bash
python experiments/001_uniform_tube/run.py
```
