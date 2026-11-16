# EXPERIMENT — preregistered Gate A controls, prospective diagnostics

Gate A's [2026-10-22 EXPERIMENT](https://github.com/ryonakayama234/morphoacoustics/blob/489111e19ffa18b21c4c4cadba8ef19f84e11bb4/docs/research/listener-r2-s1/EXPERIMENT.md) is **immutable**. This file is a dated implementation protocol, not a retrospective amendment.

- H_B1: for every one of 18 rows, compare full complex p0,pL components against frozen Wolfram independent traveling-wave values (each component absolute error <=1e-11 Pa) and the three frozen mean powers (<= max(1e-13W,1e-10 x power scale)).
- H_B2: at matched source A=3e-5m², Zs=Zc, Zt=2Zc, |pL/ps|=2/3 across all L,f to 1e-11; phase varies as exp(-ikΔL).
- H_B3: at fixed absolute Zs,Zt, A=6e-5m², L=.025m,f=3000Hz terminal |pL|≈0.4492470594476995 Pa vs 2/3 Pa baseline.
- H_B4: separate source resistor and lossless tube power ledgers, energy tolerance <= max(1e-13W,1e-10 x max(Pdrive,Pterminal,1e-12W)); passive powers >=-1e-13W; |Gamma_in|<1.
- H_B5: separately control ideal source Zs=0 => p0=ps and imposed total pressure with normalized load Zt=R Zc. This is **not** the finite-source fixed-absolute-load primary intervention.
- H_B6 (prospective): H_total=H_drive*H_canal within 1e-11 per real/imag dimensionless component on all nonzero source rows; report A-paired contrasts without overclaiming causal independence.
- H_B7 (prospective): at matched source six adjacent L pairs, H_total(L2)/H_total(L1)=exp(-i2πfΔL/c), complex error <1e-11. No wrapped-angle comparison ambiguity.
- H_B8 (prospective): strict INVALID/UNSUPPORTED/NUMERICALLY_UNRESOLVED taxonomy, zero-drive undefined ratios, deliberate sign, source boundary, absolute impedance, power, volume-flow, port and phasor mutation rejection.

Mutant tests must actually generate changed observations and assert a named audit failure. `run.py` refuses an altered pinned reference; CI runs the full frozen comparison plus existing Core uniform-tube regression on Python 3.11 and 3.12. WolframScript independent regeneration is separately reproducible but not claimed as an installed CI step.

No measured external sound-field equivalence, biological ear calibration, ASMR perceptual validation, 3D near-field, arbitrary dynamic source or WAV. Numerical compliance cannot be promoted to clinical/physiological accuracy. Decision states: PASS/FAIL/INDETERMINATE for evidence; then separately GO_LIMITED_NUMERICAL/REVISE/REJECT subject to independent review. STOP for failures with raw numerical evidence retained.