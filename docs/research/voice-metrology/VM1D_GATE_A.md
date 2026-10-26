# VM-1D Gate A — frozen finite-source inlet impedance (preregistration)
**2026-10-26 JST. Pre-implementation research freeze.** Issue [#205](https://github.com/ryonakayama234/morphoacoustics/issues/205); parent #199/#196; VM-1B #201 and VM-1C #204 are unmerged research. This Gate A must be committed before the VM-1D solver/test/CI files.

## Primary question and competing explanations
The unusually high frozen M0/M1 600/100Hz mouth-port pressure transfer under prescribed inlet flow survived B0↔ideal-piston replacement in VM-1C. Ask **whether finite acoustic inlet impedance alters that same frequency selectivity** without any wave-level voice cosmetic processing.
- H0: The finite passive source resistance values leave the 600/100Hz mouth-port response within **0.1dB** of the ideal-volume-flow ratio for each frozen body.
- H1: At least one finite-resistance condition produces >0.1dB change, measured against that body's prescribed-flow ratio. This is a *research sensitivity* delimiter, not a just-noticeable difference or voice-quality threshold. Record signed differences regardless of outcome.
This alone cannot distinguish actual glottal tissue effects, real mouth radiation, wall losses or biological speech. Those remain untested.

## Frozen physical scope
- Frozen fixture: `experiments/028_task_field_morphology_transfer/frozen_reference.json`, exact **Git blob SHA-1 `7810dfbb72cb6c41af007db6e9d51c58cad9a522`**. Validate blob before run. Read M0's sixteen `a_areas_m2`, M0 section lengths 0.010m; M1 defined by the **VM-1B documented 0.011m each** with identical 16 `a_areas_m2`. These are *prepared research geometries*, not general anatomy or material values.
- SI: `rho=1.21 kg/m³`, `c=343 m/s`, `p` in Pa (positive compression), `U` in m³/s (positive toward mouth), `p*U` in W; complex time convention `e^{+i ω t}`. Geometry fixed per condition; rigid, lossless 1D serial tract; B0 **continuous** passive shunt `Y_l=1/R_l+1/(i ω m_l)`, where `m_l=8 rho r/(3 π A_l)`, `R_l=m_l/(3 π r/(16c))`.
- Frequency grid **100, 600, 2500 Hz**. The last is a diagnostic frequency, not a vowel/formant definition. This pilot does not use a discretized native B0 boundary; compare only the continuous reference law.
- Two noninterchangeable driving conditions:
  * prescribed ideal `U_in=1e-6m³/s` at each frequency: `H_pU=p_mouth/U_in` (Pa·s/m³);
  * source `p_drive=1Pa` idealized flat pressure at each frequency in series with **real positive passive** resistance `R_s/Zc,in=0.1,1,10`, `Zc,in=rho*c/A_in`: `H_pd=p_mouth/p_drive` dimensionless. Measure actual `U_in`, **not** pretend the two excitations are the same.
- Power: phasor peak convention `P=0.5Re(p U*)`. `P_drive = P_source_resistor + P_in`, `P_in = P_mouth` for each lossless duct; all physically positive flow and powers in the accepted finite case. Never mix static acoustic reactive energy with dissipated power.

## Independent references and negative controls
1. **Uniform matched tube:** direct propagation `p_out/p_drive=[Zc/(Zc+Rs)]e^{-i 2πf L/c}`, independent of the matrix cascade and B0. Test multiple frequencies and source resistances; relative complex error <=1e-10.
2. 16-segment matrix determinant `AD-BC=1` within 1e-10 and both port/source power identities within relative 1e-9 (double-precision numerical tolerance, not empirical agreement).
3. Wrong-sign negative `R_s<0`, zero/nonfinite source pressure, nonpositive/NaN area and out-of-range frequencies must explicitly refuse; deliberately perturbed source-power ledger must fail its energy gate.
4. Replicated fixture and run file byte-hash provenance in report; report numerical failures, do not convert to PASS because a peak is aesthetic.

## Possible decisions
- `G0_G1_PASS_SOURCE_LOADING_SENSITIVITY`: reference, numerical and negative gates pass, report H0/H1 with actual numbers.
- `NUMERICALLY_UNRESOLVED`: any reference, power, identity, negative or provenance gate fails; preserve evidence.
- G2 **INDETERMINATE_PHYSIOLOGY**, G3 **NOT_RUN_NO_SELF_OSCILLATOR**, G4 **VOICE_NO_GO_UNCHANGED** irrespective of H0/H1. No Studio, Take, SMC/ASMR, public graph API or main merge.
