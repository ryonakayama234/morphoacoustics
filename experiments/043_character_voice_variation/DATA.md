# Data / causal lineage — Experiment 043

| Record | Owner | Shape / unit | Revision semantics |
| --- | --- | --- | --- |
| Body condition | Core experiment | 16 TubeSections, `length_m`, `area_m2` (SI) | Exact M0/M1 research condition |
| Timing condition | Core experiment | 3 CandidateTasks; second onset 0.15 or 0.19 s | Experiment-local, not a MotorPersona contract |
| Physical realized state | Core | 16-section time-dependent `Tract1DGeometry` | Derived; not persisted as Character anatomy |
| Source | Core | 48 kHz, fixed 0.5s LF flow array (m³/s), measured planned-F0 metadata and inherited Exp026 regression receipt | Fail closed if inherited source differs from frozen 100 Hz/noise-free specification; no hardcoded observation F0 |
| Raw observation | Core experiment | 4 × float64 `*_pressure_pa.npy` | Derived acoustic pressure; not physical state |
| Audition | Core experiment | 4 × mono 16-bit PCM, 48 kHz | Shared multiplier from maximum across all pressure buffers |
| Receipt | Core experiment | `receipt.json`, schema `exp043-research-only/v0` | Source/pressure/PCM SHA256, inherited source regression, exact executing Git HEAD, tracked-worktree-dirty flag, Python/NumPy versions |
| Immutable Take | Studio | **None in this experiment** | Future adapter must preserve all previous Take revisions |

```mermaid
flowchart LR
    BODY["Body parameters"] --> GEOM["Rest geometry"]
    TASK["Task targets + timing"] --> REAL["Realized geometry(t)"]
    GEOM --> REAL
    REAL --> ACO["Acoustic response(t)"]
    SOURCE["Source flow (fixed)"] --> ACO
    ACO --> RAW["Raw pressure Pa"]
    RAW --> WAV["Common gain / WAV observation"]
    RAW --> REC["Receipt / objective audit"]
    WAV --> REC
```

Do not identify `M0` or `M1` as a real species or voice actor. The profile
`late_constriction` is a schedule intervention, not an independent speaker
identity. The current audio render is an experiment-local observation bundle
and **must not be presented as a validated creator Take**.

## 2026-10-31 source integrity amendment

Source control records remain SI volume flow (m³/s) sampled at 48 kHz. Before accepting a run, the pilot checks `source_result.cycles` (dimensionless cycles) against a 100 Hz / 48 kHz independently clock-derived trajectory (absolute tolerance 1e-8 cycles), and checks emitted flow against the LF opening × planned-gain control (float tolerance 1e-15 m³/s absolute plus 1e-11 relative). These are experiment-local **source integrity assertions**, not independent physiological validation and not a change in Character/Take data ownership. Original 2026-10-30 audio artifacts are unmodified and must retain their exact historical source SHA and runtime receipt.
