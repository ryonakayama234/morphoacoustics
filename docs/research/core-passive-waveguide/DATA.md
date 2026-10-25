# CORE-WG-1 — Data model and invariants

## Source of truth and mutability
- `CreatureSpec`, `PreparedMorphology` and immutable `Tract1DGeometry(cavity_id, sections)` remain under established Core domain/preparation/physical ownership. No new "voice color" field.
- `PassiveWaveguideConfig`: frozen geometry, `cells_per_section ∈ {2,4,8}`, `termination ∈ {b0,closed,pressure_release,matched}`, air density and sound speed. Lengths fixed **and equal within a session**; sections may have distinct areas. Derived-only `physics_clock_hz`, `timestep_s`, characteristic impedances (Pa·s/m³).
- `PassiveWaveguideSession`: per-physical-Take mutable forward/backward queues of pressure waves (Pa), B0 inertial flow q (m³/s), tick count. No process-global, per-word reset, implicit resampling or waveform cache.
- `step(inlet_flow_m3_s)` returns `WaveguideStep`: signed source and mouth pressure (Pa), mouth flow (m³/s), stored duct and B0 energy (J), external source work (J per tick), terminal dissipation (J per tick), energy increment (J per tick), signed residual (J).
- Provenance for a future Take MUST also contain prepared-body preset ID/revision/digest, exact code commit, physical clock and observable 48k bridge version (not provided by this module).

## Operational data flow
```text
Prepared body snapshot + motion state    Prescribed source flow (for this stage)
               |                                  |
     tract geometry/areas                          |
               +----------------------------------+
                           |
                config / session state
                           |
                  local scattering + B0
                           |
             per-tick signed WaveguideStep
                 /                   \
       independent physics audit      48k observation bridge [FUTURE]
                 |                             |
          experiment evidence          immutable Studio Take [FUTURE]
```

## Physical constraints
`E=Δt Σ_cells((f²+b²)/Z_section) + M_B0 q²/2`, `ΔE = W_source - D_terminal` at stationary walls. This identity **does not include moving-wall work** and must not be reused for B2-B with time-varying area. An absolute pressure or isolated arbitrary WAV is not an adequate replacement for the paired signed p/U ports.

## Negative controls
- Nonfinite/unsupported inputs rejected; unequal section lengths refused.
- Causality: lip response cannot precede physical length/c.
- Equal-area scattering must reduce to no reflection.
- Junction energy and B0 energy are nonnegative; wrong-sign power audit must fail.
- Moving walls, closed constrictions, nonlinear air jets, flow separation, nasal branches and real microphone model NOT supported.

## Scientific versus perceptual outputs
`STATIC_PHYSICS_PASS` must NOT be converted into `VOICE_LIKE`, `CHARACTER_DISTINCT` or `STUDIO_READY`. Voice Atlas has separate difference / voice-likeness / artifact judgments, and neural microphysics (if ever introduced) cannot repair impossible task outcomes by replacing the physical waveform.
