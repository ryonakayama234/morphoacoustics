# VM-1C Gate A — SA-2A baffled piston vs native B0 boundary

**2026-10-26 / prospective research comparison before new VM-1C code.** Parent [#203](https://github.com/ryonakayama234/morphoacoustics/issues/203), [Foundation Charter #202](https://github.com/ryonakayama234/morphoacoustics/pull/202). Core main, Studio UI, held research PRs unchanged.

## Independent reference and physical claims

**Reference:** actual unmodified SA-2A `experiments/049_baffled_piston_sa2a/run.py` from [Draft #172](https://github.com/ryonakayama234/morphoacoustics/pull/172), exact source blob SHA-1 `3e7439b426adfd3549586bb43210eec66242606c`; its `radiation_impedance(f,a)` Bessel/Struve analytic oracle is separately checked by disk-overlap quadrature and forward hemispherical power. Do **not** duplicate its reference function, edit SA-2A thresholds, or claim real human lips.

**Hypotheses to test, not presumed true:**
1. Current native B0 shunt R+inertance `Y=1/R + 1/(i ω M)` matches the leading low-ka terms of the *ideal flanged piston* reference, but may differ at finite frequency. Quantify full complex normalized `Z=p/U`, resistance, reactance, phase and relative error.
2. The exact **time-discrete** native B0 `Y=1/R - i dt/(2M) cot(pi f dt)` at its geometry-derived n=2 clock is distinct from continuous B0 and exact piston. Separate **discretization error** from **model law error**.
3. With the same frozen M0/M1 /a/ geometries and ideal fixed **input volume-flow**, independent 16-section lossless 2-port transmission with the loaded end can quantify changes in the three complex port transfers `HpU,HU,Zin`, source power/lip power and 600-to-100Hz pressure selectivity. If selectivity remains high under the piston reference, refuse to attribute all of it to an inaccurate B0 approximation.

## Frozen scope and measurements
- `rho=1.21 kg/m3`, `c=343 m/s`, `U_in=1e-6 m3/s complex peak` for **frequency-domain power calibration only**; `e^(+iωt)` convention. `Zc=rho*c/(pi a²)` [Pa s/m3]. Positive U is outward from the tract. No amplitude envelope, prescribed LF source waveform, self-oscillation or receiver pressure.
- Exact Experiment028 [frozen_reference.json](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/028_task_field_morphology_transfer/frozen_reference.json), Git blob SHA1 `7810dfbb72cb6c41af007db6e9d51c58cad9a522`. 16 /a/ areas unchanged, M0 segments 0.010m, M1 0.011m; lip equivalent radius **16mm**.
- Native B0 parameters for each selected outlet radius `a`: `M=8 rho a/(3 pi S)`, `tau=3 pi a/(16c)`, `R=M/tau`. Continuous `Z_B0=1/(1/R+1/(i 2πf M))`; discrete at `dt=Lsection/(2c)` is exact phasor of native B0.
- Prespecified frequency sample set on each frozen body and matched boundary: **100, 300, 600, 1000, 1600, 2500 Hz**. Geometry controls at radii **5, 10, 16mm**, same frequencies. Enforce `ka=2π f a/c<=0.8` and `f<Nyquist`; out-of-scope case is `UNSUPPORTED_KA` rather than invented values.
- `T=[A,B;C,D]` from sixteen independent `[cosφ, iZj sinφ; i sinφ/Zj, cosφ]`, `Uout/Uin=1/(C ZL+D)`, `Pout/Uin=ZL/(C ZL+D)`, `Zin=(A ZL+B)/(C ZL+D)`. Preserve complex phase, group labels, outlet positivity.

## Prospective gates
- **G0 source/geometry integrity:** Verify exact git blob hashes SA-2A and Experiment028 before calculation; record executed git checkout+tree, source/geometry bytes SHA256; refuse unsupported, invalid and nonfinite.
- **G1 independent oracle:** At `ka = {0.02, 0.10, 0.25, 0.55, 0.80}`, SA-2A analytic reference vs its independent Rayleigh overlap `abs(normalized complex error)<=2e-9`; normalized real impedance >= -1e-12 and passivity. This checks the **ideal baffled piston**, not biology.
- **G2 B0 low-ka leading-order:** `lim_{ka→0} Im(Z_B0/Zc)/(8ka/(3π))=1` and `lim Re(Z_B0/Zc)/(ka²/2)=1`; computational checks at ka=0.001 with **absolute** normalized complex discrepancy vs independent SA-2A <=2e-6. This validates local asymptotic agreement, not full-band validity. More general finite-ka deviations are to be measured, **without a post-hoc go/no-go accuracy threshold**.
- **G3 isolated finite-ka measurements:** All valid 5,10,16mm data stored as complex `Z_exact,Z_B0_cont,Z_B0_disc`, real/imag fractional differences, `|ΔZ|/|Z_exact|`, phase and R>=0. Separate model and timestep discrepancies.
- **G4 loaded M0/M1 effects:** All three complex `HpU,HU,Zin` for all declared valid frequency points, lip and inlet passive power equality for lossless sections rel<=1e-8, nonnegative real total input impedance and no free energy from source. Report B0 vs exact piston **100-to-600Hz selectivity dB** and source-port impedance; do not label musical/voice formant or naturalness GO.
- **G5 negative controls:** SA-2A content/fixture hash mutation rejected, reversed/incorrect load or nonfinite input rejected, 16mm @3000Hz (ka>0.8) refused, no zero/negative flow-power false pass. Full exact-head CI and independent @codex review before research verdict.

**Status decision:** `SA2A_IDEAL_PISTON_COMPARISON_MEASURED` if evidence/references pass, otherwise `REFERENCE_OR_POWER_GATE_FAILED`. Actual human lips, unflanged open pipe and singer voice `INDETERMINATE_REAL_RADIATION`; creator audition `VOICE_NO_GO_UNCHANGED`. The benchmark's 2-port matrix is independent of **native time stepping**, but exact low-ka B0 equation is a shared **assumed** law. Do not mislabel it an empirical cross-validation.