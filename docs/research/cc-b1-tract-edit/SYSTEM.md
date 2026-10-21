# CC-B1 — SYSTEM / physical architecture
**DESIGN CANDIDATE; NOT ADOPTED.** Defines one creator-editable **rest morphology** axis, not gesture-time control or acoustic postprocessing.

## Existing live implementation and bounded extension
```mermaid
flowchart TD
  subgraph Studio["Studio — creative authority"]
    UI["Body Atelier: edit single area, see SI and before/after"] --> REQ["Bounded morphology edit proposal"]
    TAKES["A/B immutable physical Takes, source and body diff"]
  end
  subgraph Core["Core — physical authority"]
    REQ --> VALID["Validate unit, index/semantic coordinate, geometry, capability"]
    VALID --> PREP["Prepare immutable BodyRevision and digest (candidate)"]
    PREP --> REAL["Frozen three-task GestureScore + body-specific realization"]
    SOURCE["Frozen LF 100Hz source, source hash"] --> ACOUST["Existing 1D moving acoustic backend"]
    REAL --> ACOUST --> OBS["Raw pressure Pa + geometry/source/solver traces"]
    VALID --> REFUSE["Typed failure: no real Take"]
  end
  OBS --> VERIFY["Trusted Studio verification, exact SHA, bytes"] --> TAKES
```

- Grounded current baseline: [CC-A2](../cc-a2-two-body-live.md) only two 16-section prepared axial bodies, 0.5s 48kHz LF 100Hz / three tasks. New rest-section area is **NOT** currently accepted by the CC-A2 runner.
- First experiment changes only **a single rest-area cell**. All other source, task, timing, base geometry, listener policy and backend inputs must be held fixed. Choose an area section not actively targeted by a frozen exact-area gesture, then independently verify what the realizer does to this morphology perturbation.
- Identity separation: Character is the creative entity; BodyRevision is immutable morphology; GestureScore is the performance intent; physical state and waveform are time-varying derived observations.
- The Core renderer is presently an independently integrated segmented **serial 1D tract**. Do not falsely model it as the separately validated OG-4 branch3 graph, self-oscillating vocal folds or real listener pressure.

## Future typed organ and port mapping (DESIGN ONLY)
```mermaid
flowchart LR
  Lung["Source organ (future)"] -. "candidate airflow/acoustic interface; coupling UNVALIDATED" .-> Tube["Vocal tract organ (current 1D bound)"]
  Tube -. "future typed acoustic.p_u connection" .-> Branch["Nasal/side-cavity organs (future)"]
  Tube -. "future radiation boundary" .-> Ear["Listener organ (future)"]
```

A semantic **organ node** owns stable ID, version, geometry/material capability and typed ports. An **edge** connects validated compatible ports via explicitly chosen physical junction/boundary law. Visual lines do not create legal physical edges. UI node layout never enters physical body hashes. The physical two-port/junction conditions of [OG-4](../og4-branch3-api-v1.md) cannot be retrofitted into the existing live source-filter by UI mapping alone.

## Non-goals
No automatic voice-sex/age identity, no anatomy 3D, no arbitrary graph editing, no moving-wall FSI, no source-filter feedback proof, no source spectrum retuning, no neural voice conversion or post-hoc EQ. Unsupported asks must fail rather than inventing a more human-like sound.

## Implemented research-only physical path (NOT a new public feature)
```mermaid
flowchart LR
  A["Exact Experiment023 /a/ 16x10mm"] --> E["section0 rest area x0.9/1.0/1.1"]
  E --> PREP["Core prepare_tract1d + exp029 capability"]
  PREP --> MOVE["Exact frozen Experiment027 3-task trajectory"]
  SOURCE["Frozen LF source / SHA"] --> RENDER["Current moving 1D acoustic renderer"]
  MOVE --> RENDER --> PA["Raw SI pressure 48kHz x0.5s; hashes"]
  PA --> NOTES["Experimental result; NOT Studio Take"]
```
The conditional output signal is generated through existing physical source/tract path, **not** edited audio amplitude. The measured sound may remain buzzer-like. This code neither implements immutable first-class BodyRevision registry nor character editor; neither permits arbitrary source coupling or branched Port physics.

## Preview renderer is downstream observation only
The subsequent research build optionally exposes `raw Pa -> common fixed listening gain -> PCM16 WAV` for *three* conditions. This stage does not overwrite raw physical pressure, add EQ, generate phantom phonemes, or claim calibrated acoustic SPL. Same gain matters for causal A/B. It is a research listening artifact only; Studio immutable Take and listener/eardrum physics remain separate future boundaries.

## Listening signal path and sensitivity (diagnostic only)
```mermaid
flowchart LR
  USER["Creator reports: section0 not distinguishable"] --> MAP["Wolfram all-16-section sensitivity scan (post-hoc)"]
  MAP --> EDIT["site0,2,4 × rest area .90/1.10 (+ null)"]
  EDIT --> BODY["Exact new prepared bodies, 16x10mm"]
  BODY --> MOTION["Existing frozen 3-task gestural realizer"]
  SOURCE["Same frozen LF F0=100Hz source"] --> PHYS["Existing Core frame-wise physical acoustics"]
  MOTION --> PHYS
  PHYS --> RAW["7 independently rendered raw Pa streams"]
  RAW --> WAV["One common playback gain / 7 WAV previews"]
  RAW --> LOG["Geometry/peaks/hashes/real acoustic calls"]
  WAV --> HEAR["Future human audition: not yet conducted"]
```
Section0 is a 10mm segment at the inlet, and its ±10% area equates to diameter changes roughly −5.13%/+4.88% (circular area equivalence); a single site changes only 1/16 of the axial tract. End-state spectral F2 mode span 15Hz (~0.71% of 2100Hz), F1 nearly invariant. A common-gain WAV should be thought of as a *listening observation* of physical raw pressure, not a human-validated character difference.

## Semantically complete vs incomplete
**Current physical causal loop demonstrator** is implemented for exact 16-section research fixtures: one rest cross-section only; *all* sites are already subject to the same existing task-field motion. The site4 area at terminal state is ~4.640627× its own rest-area under existing Gesture alone, so this is **not activation of a previously static organ**. Numerically distinct waveform is obtained from the same source/filter law, not per-condition EQ or spoofed voice. This satisfies the *bounded causal proof of principle*.

**Not yet implemented:** a creator directly editing the permanent shape through Studio; Core-authoritative immutable saved/versioned BodyRevision; typed refusal, new bound Performance Contract bridge, independently validated physical oracle for output waveform and untrusted inputs, immutable Studio historical Takes and reload. Current physics is frame-wise prescribed area-dependent lossy 1D transfer with explicit resistive outlet and surrogate monopole radiation, **not** validated 3D moving boundary FSI, natural phonation source coupling or organ junction acoustics. Preserve those limits as separate research backlog, never aesthetic voice-quality guarantees.
