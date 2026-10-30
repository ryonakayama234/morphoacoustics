# System / product ownership — Experiment 043

```mermaid
flowchart TD
  subgraph Studio["Studio V2: existing slots, no UI implementation in this PR"]
    C["Character canvas + selection Inspector: proposed body selection"]
    M["Motion canvas + selection Inspector: proposed task timing"]
    D["Take transport: proposed A/B playback of immutable Takes"]
    R["Research drawer: optional receipts"]
  end
  B["Core: exact M0/M1 1D numerical body"] --> X["Core: Experiment027 task-field realizer"]
  G["Same task targets + bounded onset schedule"] --> X
  X --> A["Core: source + time-varying acoustic transfer"]
  S["Same LF source and phase"] --> A
  A --> P["Raw pressure observations (4)"]
  P --> W["Shared-gain audition WAVs (4)"]
  P --> R
  GIT["Exact Git HEAD + tracked dirty status + Python/NumPy"] --> R
  SRCCHK["Frozen source regression: 100 Hz, noise-free, cycle limits"] --> S
  W -. "Future versioned adapter / Take validation only" .-> D
  C -. "Not connected" .-> B
  M -. "Not connected" .-> G
```

**Existing UI contract authority:** Studio
[`STUDIO_WORKSPACE_V2_DECISION.md`](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md).
The closed slots are unchanged: `character.canvas`, `motion.canvas`,
`selection.inspector`, `take.transport`, `research.drawer`.
This Core research PR does not edit Studio. Future UI binding requires a
separate creator-approved proposal (action, slot, domain owner, exact contract,
real backend capability, immutable Take compatibility, and risks).

**Execution authenticity:** the inherited LF source is revalidated with Experiment026 regression before rendering, and each output receipt records its own executing Git HEAD/worktree/runtime. Historic artifacts remain labelled with their original provenance; a new commit requires a fresh CI execution, not inherited audio claims.\n\n**Physical authority:** Existing Core Experiment027 task field computes
section-area state from task activation; Experiment023/012 computes pressure.
The experiment edits only the numerical rest-body section lengths and the
second task's onset time. A phonetic symbol does not specify a WAV.

**Not yet modeled:** self-excited larynx, dynamic tissue inertia, nonlinear
source-filter coupling, per-individual articulatory skill, full organ graph,
binaural listener or arbitrary script. A valid numeric observation is not a
claim of natural voice.
