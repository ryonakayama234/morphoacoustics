# EL-R1 DATA — experimental schema and units
**Frozen Gate A: 2026-10-22 | el-r1.passive.uniform.v0 | #152**

## Input fixture
Synthetic independent listener fixture (not a human individual):
- length_m: L; 0.01 <= L <= 0.05 m, frozen comparison L={0.02,0.025,0.03}.
- section_area_m2: 1e-5 <= A <= 1e-4 m²; frozen comparison A=3e-5 m².
- air_density_kg_m3: default and frozen 1.21 kg/m³, >0 finite.
- sound_speed_m_s: default and frozen 343 m/s, >0 finite.
- terminal_resistance_ratio_to_zc: 0.25 <= R <= 4, frozen comparison R={0.5,1,2}.
- frequency_hz: nonempty strictly increasing finite list, [0,8000] Hz, max 128 samples; oracle f={0,1000,3000,7000} Hz.
- entrance_pressure_pa: single finite complex peak phasor, default {real:1,imag:0}. Fixed across geometry comparisons; source_fixture_id nonempty provenance.
- excitation_kind exactly PRESCRIBED_TOTAL_ENTRANCE_PRESSURE; reference_plane exactly CANAL_ENTRANCE.
- terminal model exactly PASSIVE_REAL_RESISTANCE; future reactive/frequency-dependent loading is **UNSUPPORTED**, not silently approximated.
The numeric research ranges above prevent unrecorded extrapolation; they do not attest human anatomical correctness. Changing air medium is permitted if valid and recorded, but requires its own verification before scientific comparison.

## Output
~~~text
{
 "schema_version": "el-r1.passive.uniform.v0",
 "status": "RESEARCH_ONLY",
 "drive": { "source_fixture_id": ..., "excitation_kind": ...,
            "reference_plane": "CANAL_ENTRANCE",
            "entrance_pressure_pa": {"real": ..., "imag": ...} },
 "listener": { "length_m": ..., "section_area_m2": ...,
               "air_density_kg_m3": ..., "sound_speed_m_s": ...,
               "terminal_resistance_ratio_to_zc": ...,
               "terminal_load_kind": "PASSIVE_REAL_RESISTANCE" },
 "planes": ["CANAL_ENTRANCE", "TERMINAL_SIDE"],
 "phase_convention": "exp(+i*omega*t)", "phasor_scale": "peak",
 "fixture_sha256": "...",
 "frequencies": [{
   "frequency_hz": ...,
   "entrance": {"pressure_pa": {"real":...,"imag":...},
                "volume_velocity_m3_s":{"real":...,"imag":...},
                "mean_active_power_w":... },
   "terminal": { "pressure_pa":..., "volume_velocity_m3_s":...,
                 "mean_active_power_w":... },
   "characteristic_impedance_pa_s_m3":...,
   "input_impedance_pa_s_m3": {"real":...,"imag":...},
   "transfer_pressure_terminal_per_entrance": {"real":...,"imag":...},
   "entrance_reflection_coefficient": {"real":...,"imag":...},
   "power_residual_w": ...
 }]
}
~~~
The source fixture ID/plane, terminal kind, and exact version are mandatory provenance. Complex arrays must never be serialized as phase-less magnitudes.

## Failure meanings
- INVALID: missing/ill-typed boundary, negative or nonfinite input, nonincreasing/oversized grid, bogus reference plane, zero/negative resistance, empty source ID.
- UNSUPPORTED: otherwise valid domain values outside **declared research scope**, including geometric range, frequencies over 8kHz, out-of-range positive passive load ratio, or physically valid but unsupported reactive terminal law.
- NUMERICALLY_UNRESOLVED: a conditioning/nonfinite computed result; never emit an apparently valid numeric observation.
The experiment will not claim INFEASIBLE, because no body motor realization occurs. Invalid must not masquerade as unsupported.

## Post-audit schema amendment A1 (2026-10-22; NOT original preregistration)
The v0 schema above is historical. A1 **increments** to `el-r1.passive.uniform.v0a1`. Each observation row has `frequency_interpretation` = HARMONIC_AC or ZERO_FREQUENCY_LIMIT. For 0Hz: `mean_active_power_w` at both planes and `power_residual_w` are null; only `formal_phasor_power_limit_w` (entrance/terminal) retains an algebraic limit, **not** an actual DC work rate. For positive frequency, the prior AC mean-power formula holds. Output includes `linear_pressure_perturbation_ratio=|p0|/(rho*c²)`, with conservative research guard `linear_pressure_perturbation_limit=0.001`. This threshold is an engineering constraint, not a universal physiological constant. Large numeric values that cannot be represented as finite floats are INVALID; valid pressure outside this research small-signal envelope is UNSUPPORTED. Full reasoning in [AUDIT-AMENDMENT-A1](./AUDIT-AMENDMENT-A1.md).
