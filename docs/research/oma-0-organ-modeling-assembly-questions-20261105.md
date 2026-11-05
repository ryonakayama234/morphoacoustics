# OMA-Q-20261105-01 — Questions to ChatGPT: Organ Design Contract for the Organ Modeling & Assembly Layer

**STATUS: DESIGN ROUND / QUESTIONS ONLY. No implementation, no code, no schema adoption, no Studio UI, no merge is authorized by this document.**
Issuer: Muse (supervisor, on behalf of the Owner). Date: 2026-11-05 JST.
Base: Core main `17a8d6200a9eca4d1204395b176701728a41d6e4` (PR #277 merged).
Primary module: **Core — Organ Modeling & Assembly Layer** (Organ Design + Physical Assembly sublayers). Physical Execution is out of scope and unchanged.

要旨（Owner向け）: 器官を「設計する対象」として定義する契約を ChatGPT と質疑で固めるための質問票。既に完了した OD-2/OD-3（単一形状族の BodyRevision）と OG-3〜OG-5（受動管グラフ）の2つの系譜を、二重管理にせず1つの Organ Design 契約へ接続できるかを問う。実装・採用の決定は本ラウンドには含まれない。

## 0. Why this round exists

The Owner's three axes are unchanged: (1) body creativity — creators can build characters with different structure and material properties; (2) voice generation — physically explainable, useful sound arises from structure and motion; (3) Studio creative experience — change, perform, compare A/B, save as a character.

The supervisor's audit of both repositories (2026-11-05) found that the missing layer is not tuning and not a new solver:

- `docs/architecture.md` (Preparation boundary): preparation is **binding, not anatomical derivation**. `CreatureSpec` does not yet contain enough metric information to derive a complete tract geometry; `Tract1DGeometry` is supplied manually.
- OD-2 (merged, PR #272/#273) and OD-3 (merged, PR #277) completed exactly one bounded shape family (`tract1d.local-log-area-5.v1`) with immutable BodyRevision receipts, reusing `BodyPresetRegistry`. The OD-2 DECISION explicitly states it introduces **no organ material constitutive law, no general OrganGraph, no public stable API, no Studio adoption**.
- The Organ Graph line (OG-3 fixed2 adopted limited; OG-4/OG-5) validates passive rigid tubes with typed `acoustic.p_u` ports, but the *general* graph schema in `docs/research/organ-graph-data-candidate.md` remains a candidate, NOT adopted. That document also fixes a separation this round must preserve: semantic morphology / editable Blueprint / validated immutable Prepared / simulation state / observation are five different objects and must not be collapsed.
- Therefore two assembly-like lineages exist in parallel — serial-tract preparation + BodyPreset/BodyRevision, and the passive organ-graph blueprint + preparation — with no shared Organ Design contract above them. Creators still cannot *design an organ*; they can only select presets or one bounded shape family.

This round asks whether one Organ Design contract can sit above both lineages without duplicating either authority.

## 1. Non-negotiables (do not relitigate; design within them)

1. Invariants I1–I8 (`docs/invariants.md`) hold. In particular I3/I6/I7/I8: failure categories keep causal meaning; unsupported structure is never silently simplified; preparation must not consume solver-capability failures (a bound morphology may still receive `UNSUPPORTED` at realization).
2. Fidelity 0 contract (`docs/fidelity-0.md`) is unchanged: static, 1D, rigid-wall, lossless, serial, CONSTRICT-only, source-free, waveform-free. This round adds no physics.
3. No fabricated constitutive laws. A material property that no adopted model computes with must be declared `UNMODELED`, never exposed as an effective parameter, a slider mapping, or a default that silently affects output (cf. Studio Issue #12 prohibitions).
4. No duplicate identity authority. OD-2 rejected its Option A (a standalone new registry) for exactly this reason; `BodyPresetRegistry` and OD-2 BodyRevision receipts are the existing authority to reconcile with.
5. Studio slots are frozen (Studio ADR, PR #34): library = references only, canvas = mode-replaced, inspector = permitted parameters of the selection only, take.transport = immutable Take playback/A-B/export, research.drawer = receipts/traces/hashes. No new panel, mode, or graph editing is proposed in this round. Studio Issue #32 [P0] additionally stops new panels and new backend options until its quality reset is resolved.
6. Judgement rule proposed by the supervisor and to be assumed in answers: scientific gates are decided by measurement only; creator listening enters only as a final binary adoption decision (GO / NO-GO), consistent with VM-0 Gate A axis 5. Listening never promotes a physical FAIL to a PASS.
7. Neural components follow I4 and `docs/research/neural-causal-boundary.md`: propose / infer / residual only, never bypassing the physical causal path. No neural element is needed to answer this round.
8. Out of scope, import-later only: Speech Motor Compiler (not present on Core main; SMC lines are unmerged drafts), ASMR / embodied listener (PR #83 parked; current `asmr/` is metadata-only, PR #155). Answers must not depend on either, but the contract must not make their later import impossible (see QO1).

## 2. Questions

### QO1 — Port taxonomy: minimal now, reservable without lying
The only validated port kind is `acoustic.p_u` (OG-3). The Organ Graph Program anticipates later port families (mechanical, tissue contact, airflow/pressure, actuation), each requiring its own laws. The Owner's long-term ideal includes performances whose causal chain is respiratory flow → phonation → tract → a receiver at a specific ear position (near-field / ASMR-class work); those must arise from body and scene physics, never from post-processing.
(a) What is the minimal port-kind taxonomy for an Organ Design contract v0?
(b) May v0 *name* future kinds (e.g. a flow-source port, a receiver port) as explicitly `UNMODELED` reservations, or does naming itself create an implied capability that this repository's evidence discipline forbids? If reservation is allowed, what marker, validation behavior (must assembly fail, and with which category?), and wording keep it honest?
(c) What must a reservation never be allowed to do (e.g. participate in a digest as if physical, be rendered in Studio as a working organ)?

### QO2 — Constitutive declaration without fabrication
Organ Design, as the Owner framed it, includes an organ's material constitutive law. Today the only honest constitutive statement available is "rigid wall" (Fidelity 0 / OG passive tubes); experiments 019–022 explored dimensionless stiffness realizers without promotion.
(a) Design a constitutive *declaration* format — e.g. `constitutive_model_id` + parameter set + validity range + provenance — such that "rigid-wall/v1" is a first-class honest entry and an unmodelled elasticity can be recorded as intent without becoming a computable claim.
(b) Which fields are mandatory before a constitutive declaration may appear in a BodyRevision digest? What happens at assembly time when a declaration names a model no adopted backend implements?
(c) How does this declaration stay distinct from both the semantic morphology (`CreatureSpec`) and the backend rest state, per the five-object separation?

### QO3 — Assembly validation and failure classification
Physical Assembly must verify: organ/connection compatibility, SI units, connection law, boundary conditions, and solver capability, and convert a design into a computable body or an explicit failure.
(a) Split the checks by stage — design-time, binding/preparation-time, realization-time — respecting the rule that preparation does not consume solver-capability failures.
(b) For each stage, state which failures are `INVALID`, which are `UNSUPPORTED`, and where `INFEASIBLE` can legitimately first appear. Give at least two concrete example failures per category drawn from the existing M0/OD-2/OG-3 assets.
(c) Boundary conditions: do they belong to the reusable body (Blueprint/BodyRevision) or to the evaluation request? The data candidate left this open; decide it, with the consequence for revision identity (does changing a boundary mint a new revision?).

### QO4 — The serial tract as an assembly, without fake organ nodes
OD-2's DECISION warns: do not make 16 acoustic sections appear as 16 independent organ nodes.
(a) Can the existing M0 tract (16 sections of 0.010 m) be re-described as an *assembly* under the proposed contract — e.g. one tract organ whose internal discretization is a solver detail — without breaking Fidelity 0, the CC-A2 oracle values (M0 peaks 275.00 / 2101.75 Hz), or OD-2/OD-3 receipts?
(b) What grouping rule decides when a sub-structure is an organ (design object) versus discretization (execution detail)? Apply it to: the 16 tract sections; the OD-2 five-cell shape family; the OG-3 two-tube graph; a nasal branch (NR-1).
(c) If re-description changes any digest or receipt, state the migration and aliasing rule, including the OD-2 identity case (r = 1.00 refers back to the baseline revision, never a newly minted body).

### QO5 — One revision authority across both lineages
(a) Define how an Organ Design contract issues or references immutable body identity so that OD-2 BodyRevisions, `BodyPresetRegistry` entries, and OG-3 blueprint preparations remain one authority — no parallel registry, no second digest scheme. If a new digest is unavoidable, specify exactly what it covers that existing digests do not.
(b) Studio consumes bodies only through the performance contract and pinned Core revisions. What is the minimal contract surface Studio would eventually see (selection of an assembled revision + its declared capabilities), and what must never cross that boundary (raw solver state, unvalidated parameters)?
(c) Versioning: when the Organ Design contract itself changes (v0 → v1), what happens to previously issued revisions and their Takes?

### QO6 — Measurement manifest and the first equivalence experiment
VM-0 (`tools/voice_metrology.py`, `docs/research/voice-metrology/`) fixes traceability discipline: commit, body, source, observation point, SI units, clock, hashes, and an explicit UNMODELED list; quality claims are separated from physical PASS.
(a) What must an AssemblyResult's measurement manifest mandatory contain so that any later claim "this variation changed the sound" is traceable to exactly one body difference?
(b) Design the first experiment for this layer as an *equivalence + one controlled contrast*, not a novelty claim: hand-bound M0 vs assembled M0 must reproduce the existing oracle peaks within a stated tolerance; one OD-2 non-null variation (state which) assembled through the new path must produce a measurable double-contrast difference. State preregistration items: hypothesis, intervention, control, acceptance thresholds, STOP conditions, and what result would falsify the whole Organ Design contract approach.
(c) The known unresolved anomalies (VM-0's M1 600 Hz harmonic dominance; experiment 023's /i/ perceptual gate failure) — must they block this layer, run as parallel obligations, or are they orthogonal? Justify.

## 3. Supervisor's provisional positions (challenge these)

P1. Port reservations, if allowed at all, must fail assembly as `UNSUPPORTED` when used, and must be excluded from digests.
P2. The tract is one organ; sections are discretization. The five-cell family edits the tract organ's rest shape; it is not five organs.
P3. Boundary conditions belong to the evaluation request, not the reusable body; otherwise every listening condition mints a new character.
P4. No new digest scheme: the Organ Design layer should *reference* OD-2/preparation digests, adding at most an assembly manifest hash over references.
P5. VM anomalies do not block the design contract, but no voice-quality claim may be attached to this layer until VM-1 resolves the 600 Hz question.

## 4. Required answer format

- Submit as a **docs-only Draft PR** against Core main, containing one answer document `docs/research/oma-0-organ-design-contract-response-20261105.md` (name may be adjusted if you record the mapping in the PR body).
- Per question: recommendation, rejected alternatives with reasons, at least one falsifier or STOP condition, and explicit NOT ADOPTED / NOT IMPLEMENTED markers where applicable.
- You may add at most four reverse questions to the supervisor, in the same document, clearly separated.
- No code, no schema files presented as adopted, no Studio changes, no SMC/ASMR imports, no experiment execution. Design only.
- Where you rely on an existing asset, cite its file path and, when relevant, its exact identifier (schema name, family id, PR/Issue number). Do not cite unmerged draft content as if it were on main.

## 5. What success looks like for this round

The Owner can decide, from the answer plus the supervisor's review, whether an Organ Design contract v0 is worth freezing — knowing exactly which organ kinds, port kinds, and constitutive declarations it would contain, what assembly would validate, which existing authorities it reuses, and which experiment would first prove the re-description is equivalent. Anything beyond that decision is a later round.
