---
id: EL-G0-INDEX
status: EXECUTABLE_RESEARCH_ONLY
parent: "PR #83 / EL-H01, EL-H02 / Issue #113"
production_contract: NONE
---

# EL-G0 — Listener reception baseline (AI / human INDEX)

**Current focus:** 理想3D自由音場で、単一の既知モノポールから二つの理想点受音位置に届く複素音圧・左右伝搬遅延・レベル差の独立基準を作る。人間の耳/ASMRを再現したとは扱わない。

## Search routing
| Need | Read first | Canonical owner |
| --- | --- | --- |
| Why / what is implemented | [SYSTEM.md](SYSTEM.md) | EL-G0 architecture snapshot |
| Variables, units, graph nodes and data trace | [DATA.md](DATA.md) | EL-G0 schema candidate |
| Frozen hypothesis, fixture, thresholds | [PREREGISTRATION.md](PREREGISTRATION.md) | Immutable preregistration |
| How to reproduce numerics | [experiment README](../../../experiments/040_listener_g0/README.md) | Executable research |
| Observed evidence / failures / adoption | [RESULTS.md](RESULTS.md) | Append-only experiment log |
| Full parked Listener & two-body questions | [PR #83 INDEX](https://github.com/ryonakayama234/morphoacoustics/blob/docs/embodied-listener-research-20261011/docs/research/embodied-listener/INDEX.md) | Research hypotheses |
| Non-vocal sources and boundaries | [R-NV0](../nonvocal-oral-nearfield-candidate-v0.md) | Existing parent #53 |

## Immutable project boundaries
1. Core physics owns source/event/propagation, Studio owns creator-facing composition. **No Studio change in this work.**
2. Existing production CreatureSpec/GestureScore/PreparedMorphology/Performance Contract unchanged.
3. ListenerSpec, ListenerPreparedState and InteractionScene remain **research vocabulary**, not publicly adopted types.
4. Ideal probe geometry is not anatomical pinna, HRTF, ear canal or subjective perception.
5. Numerical null success ≠ G1/G2 biological validation; contact and two-body work remain EL-H04/H05 research hypotheses.

## Evolution policy
Every experimental revision updates `SYSTEM.md` (architecture / constraints), `DATA.md` (versioned schema / provenance) and `RESULTS.md` (hypotheses → observed results → decision). Preserve previous gates and failures; amend rather than silently moving thresholds. Merge only after review, never automatic. Speaker core main remains independent.
