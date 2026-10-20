# Experiment 043 / exploratory result record (2026-10-20)

**Run status: COMPLETED WOLFRAM EVALUATION / EXPLORATORY ONLY / NOT CONFIRMATORY GATE B.** Source: [global_oracle.wl](./global_oracle.wl), created on branch `research/og-aud1-gatea-20261020` at [commit df1de285](https://github.com/ryonakayama234/morphoacoustics/commit/df1de285f582a20dcf2ed72f2c04651fa3b88c00). This record transcribes the actual Wolfram Language evaluator's returned numeric association. No exact machine-kernel version, independently signed human review, CI, or logged external artifact SHA is claimed yet.

## Observed scalar-vs-global solution (both matched terminations)

| C area (m²) | f (Hz) | peak p(A.in) (Pa) | scaled matrix 2-norm condition | rel(Zin_global − Zin_scalar) |
| ---: | ---: | ---: | ---: | ---: |
| .00015 | 80 | 0.9973118186 | 12.013812 | 9.43e-17 |
| .00015 | 733 | 1.8287799006 | 16.176473 | 4.34e-16 |
| .00015 | 997 | 2.1927648884 | 18.650167 | 1.43e-16 |
| .00015 | 4000 | 1.1373495938 | 14.568247 | 2.27e-16 |
| .00060 | 80 | 0.5220035930 | 8.049078 | 2.48e-16 |
| .00060 | 733 | 2.3601954197 | 14.968735 | 3.01e-16 |
| .00060 | 997 | 4.2119687892 | 24.911442 | 2.66e-16 |
| .00060 | 4000 | 0.8162777183 | 9.608591 | 0 |

Reported **max scalar/global relative error = 4.3361839e-16**, **max scaled condition number = 24.9114415**, **max `|P_A.in - P_B.out - P_C.out|` = 3.1763736e-22 W**, **max junction complex volume-flow residual magnitude = 9.0471361e-23 m³/s**.

### Falsification checks (actual output, not an acceptance threshold)

- **Wrong-law mutant:** wrong particle-velocity conservation yielded relative input-impedance error vs correct scalar law between approximately **0.243 and 0.477** across the eight condition/frequency pairs. This mutant is therefore distinguishable on the tested anchors.
- **Matched outlet distal-length-only null:** changing B and C tube lengths simultaneously but leaving their outlets matched changed source impedance relatively by about **1.19e-16 to 3.56e-16**, consistent with the analytic invariance. This is a *negative* control, not a claim that all future finite tubes are length-insensitive.
- **Source and observation:** `U_A.in=(1+0.4 i)10^-6 m³/s` is a frequency-domain test phasor. These are peak **source-plane** pressure phasors at eight condition-frequency pairs, **not** audible 48kHz output, mouth radiation, natural voice or calibrated listener SPL.
- **Numerical footnote:** an exploratory earlier unscaled Pa/U global matrix emitted a Wolfram `LinearSolve::luc` condition warning despite small displayed residuals. The executable file **uses pressure-scaled flow variables**, and the subsequent scaled solve returned the numeric values above without the warning. The scaled condition is not a valid reason to silently weaken future solver checks.

## Status boundaries / next scientific gate

This run is mathematically independent of OG-4's public `response` implementation, but scalar/global expressions share the ideal 1D waveguide and matched-load theoretical assumptions. It is **not an independent reviewer signature** or broadband validation. Do not retrofit thresholds to this result and call them preregistered. Gate A must freeze a finite-time source and dimensional reference plane, DC/Nyquist/filter policy, sample rate/length/padding, passivity and error-budget thresholds, hash and failure semantics **before** confirmatory Gate B. Gate C Studio implementation and user listening remain unstarted.
