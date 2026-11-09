# VM-1A Gate A — broadband small-signal transfer of fixed prepared tracts

**Status: PRE-IMPLEMENTATION PREREGISTRATION / research only / NOT adopted.**
Parent: [VM-1 #196](https://github.com/ryonakayama234/morphoacoustics/issues/196); historical 600 Hz observation: [VM-0 CASE_001](CASE_001.md). The original WG2 CI audio, Studio user UUIDs, and Core/Studio production interfaces are unchanged.

## Decision question and falsifiers

H1: A single discrete, volume-normalized flow pulse can expose the *complex* small-signal transfer of a static 1D waveguide without excitation-harmonic aliasing. Uniform matched-tube results must agree with an **independent analytic traveling-wave delay**; otherwise refuse all M0/M1 inferences.

H2: Exact frozen Experiment-028 M0 and M1 /a/ areas, unchanged across bodies, yield measurably different broadband tract response when axial segment length changes 10%. Counterexample: equal transfer magnitude/phase after length scaling across all bins.

H3: Changing ONLY the terminal boundary (`b0` vs `matched`) with the same exact geometry and source changes the measured response. This is a *boundary sensitivity experiment*, not evidence of a more humanlike voice.

H4: The implemented waveguide remains linear in the tested amplitude regime. Doubling the injected volume must double the observed physical p/U traces and leave transfer ratios unchanged. Nonlinearity invalidates impulse-as-transfer inference.

## Frozen stimulus / geometry / clock

- Native discrete-time **single-sample rectangular volume-flow pulse**, tick 0: `U[0] = V/h`, later ticks `U[k>0]=0`. Integrated injected volume `sum(U*h)=V=1e-13 m^3`. No 48 kHz resampling, WAV, speech or synthetic glottal fold; one contiguous physics session per run.
- Source is an *ideal imposed flow boundary*, not a source impedance or vocal-fold oscillator. Excitation amplitude is a **numerical small-signal probe**, not a physiological vocal effort.
- Air `rho=1.21 kg/m^3`, `c=343 m/s`. 16 sections, 2 wave cells/section, areas from immutable Experiment-028 `frozen_reference.json` (Git blob SHA `7810dfbb72cb6c41af007db6e9d51c58cad9a522`), /a/ array only; each M0 section 0.010 m and M1 section 0.011 m.
- Derived physics rate `fs=c*2/section_length`; 0.30 seconds observed, `N=ceil(0.30*fs)` physical ticks. Rectangular fixed signal, no windowing; resolution `df=fs/N`, approximately 3.33 Hz. Frequencies 100 and 600 Hz are **nearest DFT bins**, not asserted to be exact.
- `b0` passive RL termination from Core-WG-1 and ideal `matched` termination are explicitly distinct loads; no wall loss, far-field radiation, scene/receiver or microphone.
- Secondary uniform reference: 16 equal-area sections, area `8e-4 m^2`, 0.010 m, `matched`, pulse as above. A traveling-wave analytic reference predicts `p_out[k]=Zc U[k-32]`, `U_out[k]=U[k-32]`, `p_in[k]=Zc U[k]`, `Zc=rho*c/A`. First nonzero outlet sample is **index 32** under the audited waveguide stepping convention. No B0 reference is claimed by this ideal matched case.

## Measurement equations / units

For the finite rectangular time record, `H_pU(f)=FFT(p_mouth)/FFT(U_in)` [Pa s/m^3], `Z_in(f)=FFT(p_in)/FFT(U_in)` [Pa s/m^3], and `H_U(f)=FFT(U_mouth)/FFT(U_in)` [dimensionless]. Preserve real/imaginary values, magnitude and phase; report clock, tick count, ports and nearest-bin offsets. FFT of a one-sample flow pulse has no zero bins.

The *diagnostic* relative transfer contrast `20 log10(|H_pU(600)|/|H_pU(100)|)` is compared across B0 vs matched and M0 vs M1. For an unloaded ideal pressure-release mouth, p_mouth=0 and this particular ratio would be undefined: **do not** silently substitute another port. No fitted F1/Q, decay constant or physical source-filter feedback is authorized by this tranche.

## Gates fixed before implementation

1. Uniform matched analytic reference: tickwise delay, p_in and outlet p/U agree at relative `1e-11` (absolute `1e-14 Pa` for pressure and `1e-17 m^3/s` for flow), and complex transfer near any non-DC, non-Nyquist FFT bin agrees within `1e-9` relative to `Zc*exp(-i 2pi f 32/fs)` or `exp(-i 2pi f 32/fs)`.
2. Both M0/M1 geometry arrays and blob identity, SI units and derived clocks must match exact frozen inputs; 2x pulse is linear within `1e-10` relative at finite physical output samples. Zero-pulse negative control yields exactly zero pressure/flow. Different body/source/termination names cannot be conflated in JSON.
3. For all runs, energy residual must satisfy Core-WG-1 per-tick published tolerance, and physically measured FFT values must be finite. If either fails, no transfer result may be treated as a valid measurement.
4. Report the complex transfer, nearest frequencies, bin resolution, input digest, frozen geometry digest, named observer, modeled/unmodeled terms. Do not attach `VOICE_PASS`, `natural formant`, `radiated` or `listenable` status. CI and reviewer assess *instrument only*.
5. Any difference from VM-0's historic selective 600 Hz numbers remains **INDETERMINATE** until matching original time-limited source/monitor/receiver and a separately validated independent segmented/B0 transfer reference.

## Explicit next gates

VM-1B: independently assembled *segmented* complex transfer matrix under **same** B0 discrete impedance, frequency-grid convergence n=2/4/8, amplitude and boundary phase; then -3 dB widths and time-domain ringdown with uncertainty if resolvable. VM-1C: physically validated wall loss versus no loss. VM-1D: calibrated source, radiation and Listener. No speculative EQ, neural audio replacement, SMC/ASMR imports or UI expansion.
