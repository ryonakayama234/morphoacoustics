# Experiment 043 — OG-AUD1 preflight: independently assembled global 12-state matrix

**Status: EXPLORATORY ONLY / Gate A candidate; not preregistered, not Gate B, not an adopted broadband solver.** Core [#130](https://github.com/ryonakayama234/morphoacoustics/issues/130), Studio [#20](https://github.com/ryonakayama234/morphoacoustics-studio/issues/20), [SYSTEM](../../docs/research/og-aud1/SYSTEM.md), [DATA](../../docs/research/og-aud1/DATA.md), [EXPERIMENT](../../docs/research/og-aud1/EXPERIMENT.md), [Gate A focused review](../../docs/research/og-aud1/GATE_A_REVIEW.md).

## Purpose

Falsify two particularly easy but destructive assumptions **before** attempting waveform synthesis:
1. `U` at a junction is **volume flow** [m³/s], not particle velocity [m/s]; an invalid junction may look superficially plausible but must disagree with a correctly derived oracle.
2. Naive SI mixed-variable global matrices can appear badly conditioned because the pressure and volume-flow unknowns differ by ~10^6 in characteristic scale. First solve for `p` [Pa] and `q=Z_ref*U` [Pa], with `Z_ref=rho*c/S_A=1,372,000 Pa·s/m³`, then convert back to raw SI for recorded diagnostics. The scaling changes neither the original physical equations nor reported units.

The standalone Wolfram script [global_oracle.wl](./global_oracle.wl) assembles an explicit **12 by 12 complex global matrix** with unknowns `(p_A.in,q_A.in,p_A.out,q_A.out,p_B.in,q_B.in,p_B.out,q_B.out,p_C.in,q_C.in,p_C.out,q_C.out)`, two transfer equations per tube, p continuity at J, **signed** q conservation at J, two matched distal outlet equations, and prescribed U at A.in. A separate scalar branch-input impedance equation acts as a cross-check: neither calculation reads the public eight-point OG-4 response output.

## Model and observational discipline

- Lossless rigid 1D, linear `exp(+i 2π f t)` peak phasors, three fixed tubes and a zero-volume ideal junction. `rho=1.2 kg/m³`, `c=343 m/s`, A=.08m and .0003m², B=.09m and .0003m², C=.06m and C area=.00015 or .0006m².
- B and C are exactly matched to their *own* characteristic impedances. Source fixed `U_A.in=(1+0.4i)*10^-6 m³/s`.
- Fixed probes use **only** OG-4's already validated isolated anchors `{80,733,997,4000} Hz`. Their eight-condition output is a **scientific preflight**, not a 0–4k continuous response or WAV.
- Deliberate false-law mutant uses `U_A/S_A=U_B/S_B+U_C/S_C` in place of correct volume-flow conservation. The counterfactual length-only perturbation changes `L_B=.09 → .13m`, `L_C=.06 → .025m` while retaining matched loads. Correct source input impedance must not change; this model cannot audibly identify those lengths at A.in.
- Independently required at Gate B: full valid frequency-band/source/FFT/time-boundary specification, an independently reviewed cross-language matrix, pre-frozen tolerances, new solver implementation, actual measured raw physical response, passive power and full p/U diagnostics at *all* required samples.

## How to reproduce

Run `global_oracle.wl` in a Wolfram Language kernel (for example `wolframscript -file experiments/043_og_aud1_preflight/global_oracle.wl`). It emits a Wolfram Association with the exact scenario table, maximum relative/global mismatch, norm-scaled condition number, maximum power and junction flow residuals, deliberate false-law mutant deviations and distal-length null deviations. It creates **no** production files, audio, or UI.

See [RESULTS](./RESULTS.md) for the actual 2026-10-20 evaluator output and what it does *not* establish.
