# OMA-Q-20261106-01 — Questions to ChatGPT: D1 minimal vocabulary freeze for the Organ Design contract

**STATUS: DESIGN ROUND / QUESTIONS ONLY. No implementation, no machine-readable schema, no experiment, no Studio change, no merge is authorized by this document.**
Issuer: Muse (supervisor, on behalf of the Owner). Date: 2026-11-06 JST.
Base: Core main `34dfcd693bad979590919204ed168a61c77f6e08` (OMA-0 frozen on main). Tracking Issue: **#288**.
Primary module: **Core — Organ Modeling & Assembly Layer** (vocabulary of the Organ Design + Physical Assembly contract adopted at D0).

要旨（Owner向け）: D0 で採用した設計契約に続き、その契約で使ってよい「単語の表」（器官種・ポート種・接続法則・構成則・失敗理由コード・旧資産の読み替え）を固定するための質問票。語彙に入っていないものは存在しないものとして扱えるようにすることが目的。

## 0. Where this round starts

D0 is closed and frozen on main: question OMA-Q-20261105-01 and response OMA-R-20261105-01 (both merged, PR #285/#287), Owner adoption recorded on PR #287, tracking Issue #286 closed. The response's decision ladder defines **D1 = separately freeze a minimal vocabulary and a legacy non-destructive view**. The Owner has authorized opening this D1 round (2026-11-06). Nothing else in the ladder (G0–G4) is authorized.

Frozen at D0, **not open for renegotiation** in this round (flag contradictions as deviation candidates instead):
- Only executable port kind is `acoustic.p_u`; everything else is `UNMODELED` design intent, excluded from physical digests, refused `UNSUPPORTED` at assembly/execution.
- Constitutive honesty: `rigid-wall` is an ideal kinematic boundary assumption; unimplemented material behaviour is declared, never computed or implied.
- The tract is one organ; its sections are discretization but remain in receipt identity; OD-2's family is one edit kernel, not five organs.
- Anatomical interfaces (aperture, port position, topology) belong to the body; imposed loads/excitation/observer belong to the evaluation request. Legacy OG-3 digests are preserved byte-for-byte.
- One identity authority: existing BodyPresetRegistry / PreparedMorphology / OD-2 receipts / OG-3 digests; manifest hashes are audit-only.
- Assembly-stage `UNSUPPORTED` is scoped to "no bindable numerical rest state exists" (D0 REVISE 1); the E1 tolerance ±2e-6 is provisional until frozen at preregistration (D0 REVISE 2).
- Judgement: scientific gates by measurement only; creator listening is a final binary adoption decision only.

Existing identifiers on main that the vocabulary must reconcile with (verify, do not rename): `og3.passive.fixed2.v1` (schema, `src/morphoacoustics_graph/model.py`), connection laws `ideal.series.p_u` and `ideal.branch3.p_u` (same file), OD-2 family `tract1d.local-log-area-5.v1`, body presets `v3b-axial-M0@1` / `v3b-axial-M1@1`, domain specs `CreatureSpec / CavitySpec / CavityConnection / SourceOrganSpec / ArticulatorSpec` (`src/morphoacoustics/domain/creature.py`). Candidate labels proposed in OMA-R-20261105-01 but **not** existing ABIs: `rigid-wall/v1`, reason codes `PORT_LAW_UNMODELED` / `MATERIAL_LAW_UNMODELED` / `RECEIVER_MODEL_UNMODELED`, declaration states `MODELED_LIMITED` / `UNMODELED`.

## 1. Questions

### QD1 — Organ kinds: the minimal list
(a) Propose the exact v0 list of organ kinds, each with: vocabulary id, status (`EXECUTABLE_LIMITED` or `UNMODELED` reservation), the adopted evidence that supports it, and its scope limits. Candidates from D0: a serial tract organ (design view over CC-A2/OD-2 bodies) and a passive tube component (OG-3). Is the tract a *kind*, or a composition of one kind? Decide and justify.
(b) The domain layer already names `SourceOrganSpec` and `ArticulatorSpec` as semantic specs. Does the vocabulary map design organ kinds onto those, exclude them, or keep a two-level rule (semantic spec ≠ design kind)? State the rule so a future source organ cannot sneak in as executable by sharing a name.
(c) Which reservation names, if any, enter v0 for organ kinds (e.g. a branching cavity path per NR-1, a compliant-wall organ)? Apply the D0 honesty test: a reservation is a name for a question, not a capability.

### QD2 — Port kinds and connection laws
(a) Confirm `acoustic.p_u` as the sole executable port kind in v0 and give its frozen definition (variables, units, orientation, phasor convention) by reference to existing adopted material — do not redefine it.
(b) Connection laws: `ideal.series.p_u` clearly belongs (OG-3 fixed2). Does `ideal.branch3.p_u` enter v0 as executable, and if so strictly within which adopted scope (OG-4 evidence), or is it held out of the OMA vocabulary until a later gate? Decide; a law listed without its scope is an implied general capability.
(c) The response proposed reservation port names: `airflow.pressure_flow`, `mechanical.force_velocity`, `tissue.contact`, `actuation.command`, `acoustic.radiation_interface`, `receiver.observation`. Freeze all six, trim, or rename? For each kept name state the future law it names and why it earns a place now; for each dropped name state why not.
(d) Naming grammar: existing executable ids carry versions inside the id (`og3.passive.fixed2.v1`, `tract1d.local-log-area-5.v1`), while reservation names above carry none. Propose one grammar rule that respects existing ABIs and prevents a reservation from looking like a versioned executable contract.

### QD3 — Constitutive vocabulary
(a) Give `rigid-wall` its formal vocabulary entry: id (reconcile the candidate `rigid-wall/v1` spelling with QD2's grammar), status, exact meaning (zero normal wall velocity as an ideal boundary assumption), and the adopted contexts where it is effective.
(b) Freeze the declaration-state vocabulary: are `MODELED_LIMITED` / `UNMODELED` the right two states, or is a third needed (e.g. for a law that is modeled in a different backend than the selected one)? Define each state's effect on assembly and on digest inclusion per D0.
(c) Missing-effects list: propose the closed v0 list of declarable-but-unmodeled effects (starting point: viscothermal loss, wall compliance, wall damping, radiation impedance, turbulence noise, source–tract coupling, tissue stress–strain behaviour). Closed list or governed extension? Each entry names what adopting it would require.

### QD4 — Stage names and failure reason codes
(a) Freeze the stage names (candidate: `design`, `assembly-binding`, `realization`, plus `evaluation` if you argue it is distinct), each with its successful product and its refusal product, consistent with the D0 stage table as revised.
(b) Build the reason-code table: for each stage × category (`INVALID` / `UNSUPPORTED` / `INFEASIBLE`) that can occur there, the stable reason codes. Start from the D0 candidates (`PORT_LAW_UNMODELED`, `MATERIAL_LAW_UNMODELED`, `RECEIVER_MODEL_UNMODELED`) and complete it, including at minimum codes for: malformed design, unit violation, unknown reference, duplicate/conflicting identity, task unsupported by backend, topology unsupported by backend, articulator reach exceeded (the legitimate `INFEASIBLE`), and numerical nonconvergence (which must not be coded as `INFEASIBLE`).
(c) Grammar and stability: propose the code format, what may change in v1, and the separation between stable codes (part of the contract) and free-text diagnostics (never part of identity or digests).

### QD5 — Legacy non-destructive view: the mapping table
For every existing asset below, give its vocabulary description and an explicit "not claimed" line. No digest, byte, ID, or receipt changes.
Assets: (i) presets `v3b-axial-M0@1` / `v3b-axial-M1@1` via `BodyPresetRegistry`; (ii) OD-2 family `tract1d.local-log-area-5.v1` and its BodyRevision receipts (incl. the r=1.00 alias rule); (iii) OG-3 blueprint/preparation under `og3.passive.fixed2.v1`; (iv) Fidelity-0 `PreparedMorphology[Tract1DGeometry]` via `prepare_tract1d()`; (v) OD-3 coordination results as evaluation-side material.
Also: define the mapping record's fields (asset ref, vocabulary description refs, adapter/view version, evidence refs) and where the table lives at D1 (a document; not a registry, not code).

### QD6 — Vocabulary versioning and amendment procedure
(a) What counts as a vocabulary change requiring a new version: adding a reservation, promoting a reservation to executable, adding a reason code, renaming (argue: forbidden, alias-only), deprecating an entry?
(b) Promotion rule: state why promoting an `UNMODELED` name to executable can never be a vocabulary-only edit — which evidence gate and whose decision (supervisor review + Owner decision) it requires, following the OG gate pattern.
(c) Relationship between the vocabulary version, the D0 contract, and existing versioned ids (`og3.passive.fixed2.v1` etc.): which versions move independently, and what a v0→v1 vocabulary change does to previously issued revisions and Takes (expected: nothing; confirm or refute).

### QD7 — Deliverable form: system diagram and data structure
The answer must include, as part of the same document:
(a) An updated **system diagram** (text/ASCII or Mermaid) of the Organ Modeling & Assembly Layer with the frozen vocabulary placed: which layer owns each vocabulary class, how a design flows design → assembly-binding → realization → evaluation/observation, and where the legacy authorities sit. The diagram must remain consistent with the frozen Studio slot contract (no new panels; Studio reads only the future minimal surface defined at D0/QO5).
(b) The **vocabulary table as a data structure**: the field list every vocabulary entry carries (e.g. id, class, status, definition/evidence refs, scope, failure behaviour, aliases, introduced-in version), with the full v0 entries filled in.
(c) A short note on how a future Studio Inspector would *read* this vocabulary (display names and capability availability only), without proposing any UI implementation.

## 2. Supervisor's provisional positions (challenge these)

PV1. `ideal.branch3.p_u` enters v0 only with its OG-4 adopted scope attached; a scope-less listing is a general-capability claim and is forbidden.
PV2. Keep all six reservation port names from the response, add none in v0. Each is cheap as a name and expensive to re-litigate later; the honesty protection is the status marker and the assembly refusal, not scarcity of names.
PV3. Reason codes are two-tier: the I7 category plus a code from a closed table are contract; free-text detail is diagnostics only and never enters identity.
PV4. Grammar: follow the repository's existing convention — version inside the id where an adopted ABI exists; pure vocabulary reservations carry no version suffix, so they can never be mistaken for a released contract.
PV5. Promotion of any reservation to executable is a scientific gate (evidence + supervisor review + Owner decision), never an editorial vocabulary change.
PV6. The vocabulary document itself, once frozen, is amended only by a new versioned document that supersedes it; silent in-place edits to a frozen vocabulary are prohibited, mirroring the preregistration discipline used elsewhere in this repository.

## 3. Required answer format

- Submit as a **docs-only Draft PR** against Core main, containing one answer document `docs/research/oma-1-vocabulary-response-20261106.md` (name may be adjusted if the mapping is recorded in the PR body).
- Per question: recommendation, the filled vocabulary entries or table rows concerned, rejected alternatives with reasons, at least one falsifier or STOP condition, and explicit NOT ADOPTED / NOT IMPLEMENTED markers where applicable.
- At most four reverse questions to the supervisor, clearly separated.
- No code, no JSON Schema or other machine-readable contract presented as adopted, no Studio changes, no SMC/ASMR imports, no experiment execution. Vocabulary design only.
- Cite existing assets by exact identifier and file path. Do not cite unmerged draft content as if it were on main; OMA-R-20261105-01 may be cited as the frozen D0 contract.

## 4. What success looks like for this round

The Owner can freeze, from the answer plus the supervisor's review, a single vocabulary document: the complete v0 list of organ kinds, port kinds, connection laws, constitutive declarations, stage names, and failure reason codes, plus the legacy mapping table — such that any future implementation proposal can be checked mechanically against the question "is every word it uses in the frozen vocabulary, with the right status?" Anything beyond the freeze decision (G0 equivalence verification onward) is a later round.
