# DATA — synthetic source/load boundary and versioned observations

**Gate A research candidate / schema `el-r2-s1.source-load.v0`.**

## Synthetic frozen factorial and units
- Air rho=1.21 kg/m³; c_air=343 m/s, constant across intervention.
- **Absolute** source open-circuit pressure `ps=(1+0i) Pa` peak phasor, at `SOURCE_EQUIVALENT`. `source_fixture_id=thevenin-reference-A`.
- **Absolute** source impedance `Zs=1.21*343/(3e-5)=13834333.333333334 Pa s/m³` and **absolute** terminal impedance `Zt=2*Zs=27668666.666666668 Pa s/m³` remain fixed in the primary comparisons.
- Cross-section `A={3e-5,6e-5}` m²; length `L={0.020,0.025,0.030}`m; frequencies `f={1000,3000,7000}`Hz, 18 primary rows. No 0Hz AC power fields in the primary grid.
- Each row records: `ps`, `p0,U0` at `CANAL_ENTRANCE`, `pL,UL` at `TERMINAL_SIDE`, `Zs,Zt,Zc,Zin`, `Gamma0`, `Psource,Pentrance,Pterminal,Psource_loss`, `frequency_hz`, positive-frequency classification, reference-plane and model version, immutable fixture hash and analysis provenance. Store real+imag, no magnitude-only serialization. Source pressure is *not* entrance pressure. No waveform claim.

## Gate-B implementation-domain proposal (MUST validate)
- Real positive finite air rho/c_air/L/A and terminal real Zt>0 finite; nonnegative finite real Zs>=0. Strictly increasing, nonempty f>0, <=8kHz (research computational scope only).
- Proposed geometric guard 0.01<=L<=0.05m, 1e-5<=A<=1e-4m²; >0 finite impedances, source pressure phasor components finite; dimensionless small-signal guard `max(|ps|,|p0|,|pL|)/(rho*c_air²) <=1e-3` as conservative **engineering cutoff**, not physiological safety limit.
- Clearly distinguish INVALID malformed/nonfinite numeric values from UNSUPPORTED physically meaningful parameter outside this narrow research backend. Out-of-domain complex/reactive Zs/Zt is UNSUPPORTED only if explicitly well formed; missing or ambiguous units INVALID.
- Derived denominator condition, impedance overflow, singularity/ill-conditioning: NUMERICALLY_UNRESOLVED, no damping/automatic plausible fallback. `INFEASIBLE` does not apply: no actuators or physical gestures.
- A new `el-r2-s1.source-load.v0` observation contract does NOT retroactively change EL-R1 `el-r1.passive.uniform.v0a1` fixture digests, and no Core public type or Studio schema may adopt it until later review.
