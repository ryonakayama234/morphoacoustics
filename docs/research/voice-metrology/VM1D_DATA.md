# VM-1D DATA — SI and owner boundary
**Not a public schema.** Core owns this isolated research result. Studio Draft #33 `PANEL_REGISTRY.json` / `DATA_MODEL.md` are immutable reference contracts.

| research item | units / representation | authority |
|---|---|---|
| body M0/M1 | 16 × {length_m, area_m2}; derived M1 length explicit; exact source blob SHA-1 | Core frozen experiment-028 (read-only) |
| state-free acoustic source | `p_drive` complex peak Pa and positive `R_s` Pa·s/m³; not tissue actuation | VM-1D research only |
| acoustic ports | `p_in,U_in,p_mouth,U_mouth` complex, SI with shared positive direction; `Zin=p_in/Uin` | Core acoustic analysis |
| mouth load | B0 continuous `Z_L` Pa·s/m³, specified ideal model | research reference |
| observables | `HpU` Pa·s/m³; `Hpd` dimensionless; `H600/H100` dB with same source law per comparison | measurement receipt |
| power | time-average W peak phasor, independent source/duct/termination ledger | numerical energy check |
| provenance | complete exact Git blob identity, executed checkout (or explicit UNVERIFIED), research code hash, body bytes hash | instrument/CI |
| Takes and listener | none, waveform absent, mouth port not receiver | **no Studio emission** |

No `CreatureSpec`, `OrganGraph`, `PerformanceContract`, `BodyRevision`, `TakeRecord`, `src/morphoacoustics/`, `src/morphoacoustics_graph/`, SMC or ASMR API changes.
