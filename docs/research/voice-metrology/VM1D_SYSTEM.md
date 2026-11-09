# VM-1D SYSTEM — internal source/duct/load research chain
This is a hypothetical passive acoustic source termination **inside the research runner**, not a new organ module, glottis model or Studio control.

```mermaid
flowchart LR
  P["Source pressure p_drive; research command"] --> R["Passive upstream Rs; Δp=Rs Uin"]
  R --> I["Inlet p_in,U_in"]
  I --> T["Frozen M0/M1 16-section 1D tract; lossless ABCD"]
  T --> L["Continuous B0 passive radiation load (idealized)"]
  L --> O["Mouth p_L,U_L only (NOT listener WAV)"]
  I --> M["Independent SI power & impedance ledger"]
  L --> M
  P --> M
  O --> M
  M --> D["Research receipt (future Studio research.drawer only)"]
```

With `[p_in,U_in]^T=M[p_L,U_L]^T`, `M=[A B; C D]`, `p_L=Z_L U_L`, and `p_drive=p_in+R_s U_in`,
`U_L=p_drive/[A Z_L+B+R_s(C Z_L+D)]`.
Ideal-flow comparator: `U_L=U_command/(C Z_L+D)`.
The passive duct has neither self-oscillation nor a physically realized gesture.

**UI ownership alignment** (Studio Draft #33 PANEL_REGISTRY, read only): `character.canvas` describes possible organ nodes / body refs; `motion.canvas` owns future Script, Direction and Gesture timing; `take.transport` owns verified creator audio (NOT generated in VM-1D); `research.drawer` may later own scientific receipts. No panel change and no new controls. Studio imports only vetted Core capability contracts later.
