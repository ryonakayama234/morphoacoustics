# Experiment 031 — exploratory local test report

**Executed:** 2026-10-10, Linux Python 3.13.5, Python standard library. Tests executed locally on the implementation matching this Draft PR. GitHub CI and independent review are separate gates. Research-only toy physics, not natural human phonation.

## Frozen input and interventions

48 kHz, 0.24 s, Psub 800 Pa, f0 100 Hz, 65%-open Amax=3e-5 m², I=1200 Pa s²/m³, Rg=1.5e6 Pa s/m³, C=3.5e-10 m³/Pa, Cd=0.7, rho=1.21 kg/m³, zero initial U and p. Outlet low/high resistance 2e6 / 8e6 Pa s/m³. A(t), Psub and valve coefficients are identical in all four conditions.

## G1: Relative RMS difference in upstream U(t)

| Comparison | RMS(Ucandidate - Ureference)/RMS(Ureference) |
|---|---:|
| C0 low versus C0 high (negative control) | **0.000000** |
| C0 low versus C1 low (feedback intervention) | **0.382479** |
| C1 low versus C1 high (passive load intervention) | **0.482597** |

Eligible G1 thresholds pass locally. These are **differences in flow time series**, not output sound pressure, mean-flow percentage change, human perceptual improvement, or calibrated physiological coupling magnitudes.

## G0: Independent numeric and algebraic checks

- All **10** experiment-local unittest tests pass (independent Wolfram steady and single-step numbers, sign symmetry, closed-valve energy budget, negative drive, parameter rejections, causal isolation and convergence).
- Convergence at aligned time samples for C1-high over 0.08 s: 24 to 48 kHz normalized flow discrepancy **0.00575486**; 48 to 96 kHz **0.00294996**. This is a measured first-order trend in this fixture, not a general solver theorem.
- Maximum per-step energy residual normalized by cumulative absolute driving work: C1-low **1.71e-18**, C1-high **5.45e-18**; all loss terms nonnegative. Backward-Euler numerical dissipation and exact valve-closure projection loss reported separately.
- Independent Wolfram symbolic coupled backward-Euler energy residual: **0**. Exact ideal closure energy residual: **0**.
- Local CSV traces (4 conditions) and summary.json emitted outside Git checkout, intentionally not committed. SHA-256 of the local summary JSON: e1632b7ce5ac24e4028e2b3d11c9909ddcc8a320e9f4fe98814095824fa95dbe.

## Strict scientific limitations

1. The intervention is valid only for a **passive lumped chamber**. No real time-domain tract geometry, segment wave reflection, inlet impedance derived from body geometry, vowel or phonetic result was calculated (**G2 UNSUPPORTED**).
2. C0 is intentionally **nonreciprocal**; its missing pressure-work feedback is an explicit nonreciprocal energy ledger term. No global passivity claim for C0.
3. Exact ideal closure is a dissipative reset and not a contact-mechanics model; area is prescribed, not an LF flow pulse or a simulated moving tissue.
4. No naturalness, buzziness, listening, perceptual or waveform output (**G3 NOT_TESTED**). Not fit for production.
5. Before further promotion: independent review, CI integration if desired, convergence/robustness probes, and a distinct physically grounded time-domain tract model.

## Provenance and sources

- Wolfram analytic and symbolic oracle: wolfram/independent_oracle.wl and wolfram/oracle.json.
- Preregistration-only first commit precedes implementation on this branch.
- Titze (2008), Nonlinear source–filter coupling in phonation: theory: https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/ .
