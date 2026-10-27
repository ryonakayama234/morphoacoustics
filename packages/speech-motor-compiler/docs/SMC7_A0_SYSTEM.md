# SMC-7 Gate A0 — SYSTEM: language evidence → symbolic motor candidate

**2026-10-27 JST / Issue #229 / DESIGN_REFINEMENT_ONLY / NOT_PREREG_FROZEN / NO_SOURCE / NO_TEST / NO_MAIN_MERGE.**
Stacked design base: SMC-6 Draft #225 exact HEAD 0caa70f6bb8333f60fbcc2f29ea57578c998033c (inherits unmerged SMC-5 #211 and SMC-4 BR). A0 is a prospective architecture, NOT running code, adopted natural pronunciation, public API, or body/sound capability.

## Research question and claim ceiling

For bounded Japanese creator scripts, can independently attributed pronunciation hypothesis **paths** be proposed, selected, validated and (only when a complete valid path plus a legitimate finite SMC-5 research lexicon exists) projected to unchanged SMC-5/6 symbolic planning, without treating linguistic, symbolic, temporal, bodily, and acoustic correctness as interchangeable?

Do not confuse four claims: (i) text→reading accuracy; (ii) reading→Task mapping under a particular lexicon; (iii) constraints permit a symbolic schedule; (iv) Core physically realizes tasks and produces intelligible sound. A0 designs evidence for (i–iii) and explicit ignorance of (iv). Japanese phonetic and prosodic processes are not automatically determined by kana reading.

## Proposed system / authority diagram

~~~mermaid
flowchart TD
  Studio["Future Studio Motion: Script + Direction (UI frozen)"] -. "versioned service later" .-> Src
  Src["ScriptRevision: immutable UTF-8 source + codepoint spans"] --> Front["Pronunciation front-end boundary: candidate providers, bounded, attributed"]
  Front --> Paths["PronunciationPathSet: zero / one / many; unresolved alternatives kept"]
  Paths --> Sel{"Explicit selected path & qualified evidence?"}
  Sel -->|no| Hold["PROPOSED_ONLY / AMBIGUOUS / UNKNOWN; NO MOTOR PLAN"]
  Sel -->|yes| Gate["Projection validator: complete coverage, source spans, allowed symbols, versioned mapping contract"]
  Gate -->|unsupported| Stop["REFUSE with stage and evidence; no candidate plan"]
  Gate -->|yes| Canon["Unmodified SMC4-BR canonical-ingress v1 wire contract"]
  Canon --> S5["Unmodified SMC5 symbolic_bridge: bounded TaskLexicon + TaskGoals"]
  S5 -->|refusal| Stop
  S5 -->|RESOLVED| S6["Unmodified SMC6 COMPATIBILITY STN, exact hard constraints"]
  S6 -->|UNSAT/refusal| Stop
  S6 -->|SAT| Out["Research MotorProgramCandidate concept + provenance: NOT MotorScore ABI"]
  Out -. "separate Gate: semantics/units/capability" .-> Core["Core Character: organ nodes/typed edges → realizer → acoustics"]
  Core -. "validated later" .-> Take["Studio immutable Take / perception"]
  Src --> Audit["L0 source/proposal measurement"]
  Paths --> Audit
  Out --> Audit
~~~

The valid selection does not guarantee a valid SMC5 lexicon mapping. SMC5 admits only current SYNTHETIC_ONLY scalar goals, explicit selected units, required slots and EXACT_EVENTS. SMC6 has two research lanes. For A0's baseline replay choose **COMPATIBILITY only**, inheriting all exact SMC5 anchors/couplings. Any future RESEARCH_OVERRIDE is a separately identified experiment retaining original timing digest; do not silently override exact constraints. No selected path → never call SMC5. One candidate is still only a *proposal* until the selection policy and provenance are declared; a deterministic baseline may select only in a separately declared comparison arm.

## Authority and physical semantics

- SMC-7: spelling/script, pronunciation-hypothesis paths, source alignments, evidence references, selection provenance, fail-closed projection. No body actuator, organ ID, physical target, F0, formants, waveforms or user-interface controls.
- SMC-4/5: finite lexicon, symbolic Task IDs and goals, many-to-many associations, sharing and exact legacy timing; SYNTHETIC_ONLY does not become biologically verified by arriving from Japanese text.
- SMC-6: symbolic temporal feasibility/window/overlap; earliest feasible witness is **not** natural speech timing, genuine coupled phase or biomechanical movement.
- Core: prepared morphology, organ/port topology, body-dependent task observation and capability. Exp040 / PR #226 found 0/3 physically evidenced bindings; Core #227 separately proposes G_area SI m², not human tongue millimeters.
- Studio: Character/Motion/Scene frozen 3-mode layout from merged ADR PR #34. A later separately approved Motion canvas may inspect candidate/readings/receipts; no code or layout change here. The actual hearing experience is only available after validated Core acoustic execution and an actual creator audition (Studio #32).

## Two intentional entry modes (prospective)

1. **EXPLICIT_SELECTED**: caller supplies complete pronunciation path and corresponding source spans. Validate and project under inherited canonical contract; must produce identical SMC5/6 output to a direct equivalent legacy request, or reject.
2. **PROPOSE_ONLY**: one or several deterministic or learned G2P providers propose paths with tool/dictionary/model revision and evidence. Return attributed alternatives/unknowns. A candidate may subsequently be selected by a declared actor or validated selection policy, but proposal-only must never silently become an executable plan.

No backend provider is selected as authoritative by A0. Open JTalk / pyopenjtalk is a candidate reference baseline, not a source of automatic truth. Neural candidates, if ever used, merely propose readings and must be independently evaluated. The planned *selected-path projection* should be a new research-only adapter; never mutate SMC4-BR ingress grammar to accept a lattice.

## Why this architecture is testable

The same source can yield two different complete pronunciation paths and thus distinct compile receipts, without merging their tasks. Changing a script revision invalidates old source alignment and cannot silently retain a motor plan. Invalid Unicode, unsupported annotation, insufficient context, candidate-budget exhaustion, missing TaskLexicon mapping, and incompatible timing are distinct refusals. Only true supported work traverses the green path; rejected/hypothetical paths cannot produce physical/audio traces.

## Project/literature evidence
- SMC-4 gate semantic design: docs/SMC4_GATE_A_PROTOCOL.md, amendments 01–03. SMC5 gate: SMC5_SYSTEM.md / SMC5_DATA.md. SMC6 as-built: SMC6_GATE_B_IMPLEMENTATION.md / SMC6_GATE_B_RESULTS.md.
- Core Experiment 040: https://github.com/ryonakayama234/morphoacoustics/pull/226 ; subsequent physical semantics Gate B: https://github.com/ryonakayama234/morphoacoustics/issues/227 .
- Studio approved product ADR: https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md .
- Browman & Goldstein, articulatory gestures, https://www.cambridge.org/core/journals/phonology/article/abs/towards-an-articulatory-phonology/0DD9DFF7A4E34DB2F9DD651F1FD6FDBC ; TaDA score estimation https://pmc.ncbi.nlm.nih.gov/articles/PMC3528686/ (scientific motivation, NOT validation of our mapping).
