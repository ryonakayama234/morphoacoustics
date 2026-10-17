# Experiment 032 — local pilot measurement (2026-10-10)

**Status: experimental numeric verification of fixed-geometry linear 1D acoustics only.** The local diagnostic model was run on Python 3.13 + numpy 2.3.5, with 9 independent experiment-local tests passing; an additional Core integration test was added to run in the actual GitHub install/CI environment (local sandbox lacks an installed clone of Core). This report does **not** equate local execution with GitHub Actions or outside scientific review.

## Fixed oracle and physical quantities

- Uniform tract = 10 sections × 0.017m, area 3e-4m²; rho 1.21kg/m³, c 343m/s; implicit midpoint at 48kHz, 4 subdivisions per physical section, total 40 acoustic cells.
- Ideal characteristic impedance **1,383,433.333 Pa·s/m³**; ideal outlet round-trip time **0.991253644ms**.
- Closed/open uniform ideal eigenmodes, **504.411765 / 1513.235294 / 2522.058824 Hz**, from independent Wolfram; these are ideal boundary benchmarks, **not human formant observations**.
- Narrowed tract: one interior section area halved, other geometry and prescribed input fixed.

## Observed transient results

- Ideal pressure-release reflected pulse vs matched outlet: reflected *negative* pressure peak returned after **1.010417ms** relative to a compact input pulse center; absolute error from ideal **0.019163ms** (< preregistered 0.20ms).
- Three matched-outlet complex input impedance probes (magnitude of complex relative error vs Zc):

  | frequency | relative complex error |
  |---|---:|
  | 250 Hz | **0.00665%** |
  | 500 Hz | **0.03790%** |
  | 1000 Hz | **0.00338%** |

- Pressure-release *semi-discrete* modal frequencies converge with subdivision factor 2 / 4 / 8:

  | subdivisions | 1st mode Hz | 2nd mode Hz | 3rd mode Hz |
  |---|---:|---:|---:|
  | 2 | 504.282 | 1509.737 | 2505.884 |
  | 4 | 504.379 | 1512.360 | 2518.009 |
  | 8 | 504.404 | 1513.017 | 2521.046 |

- Maximum per-step discrete energy residual / accumulated absolute injected input work over ~10ms: **7.22e-16** (constricted matched), **7.67e-16** (uniform matched) and **1.18e-15** (uniform pressure release), with nonnegative resistive dissipation. The residual is a numerical energy bookkeeping check, not an empirical calibration.
- One-section constriction changed the *inlet pressure trace* by peak **0.573898 Pa** for an identical injected test pulse. It does not yet demonstrate that the constrained body changes an endogenous glottal flow, because inlet flow is prescribed.

## Independent Wolfram oracle

The 2-cell discrete midpoint energy identity was symbolically simplified to residual **0**, independently of Python. Matched ZL=Zc gives Zin=Zc. Ideal first three quarter-wave eigenmodes and junction A→A/2 pressure reflection coefficient **+1/3** agree with the documented reference script `wolfram/independent_oracle.wl`.

## Explicit unsupported capabilities / review blockers

**G3 UNSUPPORTED:** the tube's measured inlet pressure is *not yet fed back to* Experiment 031's valve-flow equation; no true geometry-conditioned source–filter flow coupling has been claimed.

**G4 NOT_TESTED:** naturalness, listening quality, actual vowels/speech, moving geometry, material-dependent walls, glottal tissue vibration and precise lip radiation are not implemented or tested.

Before promotion: require successful **experiment-specific** GitHub Actions results, critical review of implicit midpoint acoustic physics and reconstructed inlet port power, more realistic dissipative and time-varying tract boundary modeling, and a separately preregistered true glottal-flow coupling experiment. Keep PR Draft.
