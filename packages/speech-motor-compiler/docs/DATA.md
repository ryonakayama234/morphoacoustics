# SMC-3 DATA — candidate contract (Gate A)

## Canonical symbol-level vocabulary
- `PronunciationUnit(unit_id, symbol, start_offset, end_offset)` identifies a **candidate** phoneme for a source codepoint span. Different unit IDs may refer to the same source span.
- `MotorTask(task_id, goal_kind, capability_requirements)` identifies one body-neutral symbolic motor goal. No organ coordinates.
- `TaskAssociation(unit_id, task_id)` is a many-to-many link. Repeated references to one task ID do **not** duplicate the task.
- `EventAnchor(task_id, event, time_s)` optionally sets a synthetic absolute event time (relative to a local zero); necessary to resolve all times rather than just differences.
- `CouplingConstraint(source_task_id, source_event, target_task_id, target_event, lag)` describes equality `target_event_time = source_event_time + lag`. Events are ONSET/OFFSET and lag is an exact `fractions.Fraction` of seconds in this synthetic fixture only.
- `SymbolicPlan` aggregates source/units/tasks/associations/couplings, without physical fields.
- `ValidationReport` has STRUCTURALLY_VALID or INVALID and deterministic diagnostics. Neither state represents body feasibility or natural articulation.

## Invariants
- Unique nonblank source unit/task IDs; Unicode Python codepoint span [start,end) within original unchanged text.
- TaskAssociation endpoints must exist; duplicate associations rejected. Reject unit with no task and orphan task; do not fabricate associations.
- Coupling endpoints must exist; event names must be ONSET/OFFSET; lag must be exact Fraction. Contradictory graph equalities and nonpositive determined task duration fail closed.
- Plan fields must not include `CreatureSpec`, `GestureScore`, organ positions, F0, pressure, audio, waveform, body realization, or solver state.
- Canonical receipt should sort order-insensitive collections, preserve the exact Unicode script, and encode Fraction as [numerator,denominator]. Schema is provisional research-only.

## Synthetic many-to-many witness
```text
        G1 G2 G3
P1       1  1  0
P2       0  1  1
```
A single shared G2 node must be preserved across P1/P2. Wolfram proves that strict exactly-one Task per phoneme cannot cover all three task columns in this two-row abstract witness. This does not assert actual phonetic gestures.

## Existing integration boundary
Existing SMC-2 imports `morphoacoustics.integration.shared_timeline`. This sibling package will not; future Core integration belongs to a separate adapter and review.

## 2026-10-22 v0 candidate implementation
`Event` is ONSET/OFFSET, `lag_s` and `time_s` use exact `Fraction`. `validate_plan` checks symbolic references, duplicate links and internally inconsistent equalities; its success is only `STRUCTURALLY_VALID` (never capability or physical clearance). `resolve_timing` additionally requires every onset and offset connected to at least one common anchored origin and returns synthetic `TimingReport` only. A plan with valid associations but no anchors is structurally valid and has an explicitly invalid/unresolved timing report. There is no automatic phoneme-to-task inference.

### Implementation receipt
Type-check invariants include no accidental aliasing of `TaskAssociation` iteration variable and `EventAnchor` iteration variable; the first CI mypy gate correctly caught this and requires a new validated HEAD. Runtime pytest alone was insufficient proof.

## 2026-10-22 verified software Gate B receipt (not research adoption)
Exact source HEAD **`9c9ac9539ae1798ed27ef5cd751562e4b2c9b469`**: GitHub API reported **16/16 completed check runs SUCCESS** (some duplicate push/PR runs), including isolated Python 3.11/3.12/3.13 package import/install + 21 synthetic pytest cases per run + strict package mypy, existing Core root test matrix/typecheck, and bounded SV1 regression. Evidence: [isolated package run](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258873), [root tests](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258910), [SV1](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258867). An earlier failing mypy run is preserved in EXPERIMENTS. Individual OG3 and OG4 were not separately confirmed for this SHA. No independent reviewer, phonetic fixture, body adapter, wav or Studio integration. Disposition: **EXPLORATORY_SOFTWARE_PASS / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**.

## 2026-10-23 Gate C — audit data and independent oracle
- Preregistered audit protocol: [GATE_C_PROTOCOL.md](GATE_C_PROTOCOL.md), commit `7705ebd752e191a545506c0a2a79d56a40efc6bf`, fixed candidate HEAD `7d5c405fee1b2469b11bbe6d68b9e0d18e4dab05`.
- `tests/test_gate_c_adversarial.py` creates **100 deterministic artificial plans** from 5 fixed seeds times 20 indexed cases, each with 3–8 tasks; pairs of onset/offset values are constructed first using `Fraction`, then encoded as event equalities; every association is explicit and task IDs are unique. Expected timestamps are stored outside the SMC solver.
- Metamorphic relations: collection permutation preserves `canonical_plan_json`/`plan_digest` and event table; positive absolute-anchor translation shifts all resolved event timestamps; contradictory extra anchor fails with no partial time series.
- Distinguish `STRUCTURALLY_VALID` vs fully `RESOLVED`: an unanchored component may have valid graph syntax but has no executable/fully-resolved timing. Even RESOLVED is neither capability validation nor physical speech.
- Adversarial malformed runtime input (`source_text=None`) tests whether a type-annotated frozen dataclass is actually validated fail-closed; this is an audit probe, not an adopted public `None` contract. Any crash must be preserved as a counterexample pending disposition.
- Source character offsets count Python Unicode codepoints, **not** grapheme clusters; synthetic complex-emoji fixture documents this distinction.
- Independent exact-math script: [../wolfram/gate_c_oracle.wl](../wolfram/gate_c_oracle.wl). Script existence is not evidence of execution. No semantic-equivalence hashing beyond tuple-order normalization is promised.

## 2026-10-23 Gate C failure-mode correction

At first audited SHA `2a3a038c342150b37323a6c4b24cc846954d1c42`, a runtime malformed `SymbolicPlan(source_text=None)` elicited a Python `TypeError` in a source-span bound check after `EMPTY_SOURCE` was already diagnosed. This is a **runtime type-enforcement failure** in a typed dataclass, not a time solver inconsistency. See [first red-run receipt](https://github.com/ryonakayama234/morphoacoustics/pull/169#issuecomment-6367686236).

`validation.py` fix `2de422883e544c1dff5ec12121a1f033a2f3afc5` computes `source_length = len(source_text)` only when it is a `str`, else 0. The preregistered malformed runtime case must now return `INVALID` and never reach event resolution. This does not imply complete validation of all arbitrarily malformed runtime object graphs; other inputs remain future audit scope.

## 2026-10-23 Gate C — verified exact-source-SHA repair CI

- **Fixed-source commit `2de422883e544c1dff5ec12121a1f033a2f3afc5`** is **16/16 completed SUCCESS**, zero failure/pending in GitHub check-runs API (two push/PR job sets): isolated package Python 3.11, 3.12, 3.13 pytest with 127 synthetic tests per interpreter, package strict mypy, existing root test matrix/typecheck, and bounded SV1. [Python 3.12 job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39973099897/job/120480625178). This is independent of the earlier red SHA `2a3a038c342150b37323a6c4b24cc846954d1c42`.
- Initial red failure **PRESERVED**, caused by `source_text=None` and unguarded `len(None)`; minimal source guard fixed the runtime fail-closed behavior with unchanged frozen test fixtures.
- All verified outcomes above refer to the **code-bearing SHA `2de422883e544c1dff5ec12121a1f033a2f3afc5`**, not automatically to later documentation-only commits. Document-only final branch HEAD checks require their own confirmation. OG3 and OG4 were not run as separate exact-SHA science gates by these package-scoped actions; do not claim them.
- Disposition: **GATE_C_IMPLEMENTER_ORIGIN_SOFTWARE_PASS / HUMAN_INDEPENDENT_REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**. This is not a physical or phonetic validation.

## 2026-10-24 Unicode scalar boundary and contradiction semantics (Codex P2)

[Codex P2 ledger](GATE_C_CODEX_REVIEW.md) records the review provenance, first red CI, and separate correction. Python `str` can contain unpaired surrogate code points U+D800–U+DFFF even though strict UTF-8 encoding cannot represent them. Since the research digest uses strict `encode("utf-8")`, validator must return `INVALID_UNICODE_SCALAR` before treating such string fields as accepted. This guard checks the input source, IDs, hypothesis symbols, goal kinds, capability tokens and symbolic edge reference strings. It does **not** prohibit legitimate supplementary-plane Unicode or valid ZWJ sequences.

For exact contradictory temporal equalities, the global `CONTRADICTORY_TIMING` diagnostic takes precedence over numerical duration or pre-zero diagnostics derived from BFS traversal potentials; such potentials are arbitrary after a conflict. For otherwise consistent components the existing `NONPOSITIVE_DURATION` and `NEGATIVE_ANCHORED_TIME` behavior remains. This is not a physical gesture-duration claim.


## SMC-4 Gate B — separate typed mapping layer (2026-10-24)

**Location:** `src/morphoacoustics_smc/smc4_types.py`, `smc4_lexicon.py`. Research-only API; existing SMC-3 v0 `SymbolicPlan` schema and digest are unchanged.

- `PronunciationPath(path_id, units, required_spans, complete)`: one complete, explicitly selected reading interpretation. No orthography-to-pronunciation inference.
- `Predicate(op, key, expected, operands)`: TRUE/FALSE/EQ/NOT/AND/OR using strong Kleene TRUE/FALSE/UNKNOWN; context is caller-supplied and never guessed.
- `TaskDefinition(definition_id, semantic_revision, variable, value_domain, goal_kind, applicability_domain, capabilities, algebra)`: versioned functional goal-variable declaration, not a physical coordinate.
- `SlotCandidate(template_id, definition_id, semantic_revision, lower, upper, context, priority, evidence_id, status)`: exact-Fraction synthetic scalar bounded target and source of mapping. No claim of phonetic calibration.
- `TemplateBundle(bundle_id, unit_id, symbol, slots, context, priority, profile, target_scope_kind, target_unit_ids)`: initially one selected occurrence only. All `GoalSlot`s REQUIRED; exactly one alternative chosen per slot.
- `ShareDecision(episode_id, members)`: explicit *proposed* shared episode; compatibility checks include definition/revision, variable/domain/algebra and exact target interval intersection. Neither automatic same-kind deduplication nor silent fallback split.
- `TimeAnchor`, `TimeRelation`: occurrence-keyed exact event equality requests. Unsupported phase-oscillator requests explicitly refused.
- `CompileResult(plan|None, receipt)`: successful mapped symbolic graph plus a **separate** `CompileReceipt`. Receipt includes readable chosen (unit, slot, bundle, template, definition/revision, scalar target/evidence), exact `task_targets`, revision/path metadata and deterministic digest; failures return `plan=None`.
- `compile_lexicon(...)`: finite, selected-path-only research function. Status `MAPPED_SYMBOLIC` has `body_status=UNVERIFIED`; rejection codes distinguish incomplete path, UNKNOWN context, ambiguous candidates, unmapped unit, unsupported scope, sharing conflict, semantic goal conflict, invalid graph, unsupported timing and absent empirical confirmation.

**Exactness:** bounded target intervals and temporal anchors use `Fraction`; stable instance IDs are deterministic digest-derived tokens scoped by selected path, occurrence or explicit episode. Unanchored timing stays unresolved; provably overlapping exact windows with disjoint scalar targets are rejected without any body-infeasibility assertion.

**Evidence boundary:** original Gate A protocol + Amendments 01/02/03 and [Gate B frozen protocol](SMC4_GATE_B_PROTOCOL.md) provide the normative oracle. No human Japanese gesture table, morphology fit, animation, waveforms or industrial public API has been adopted.

## SMC-4 Gate B research data contract and input integrity (2026-10-25)

`PronunciationPath` is explicitly selected and complete; `TaskLexicon(revision, rule_revision, definitions, bundles)` has single-unit `TemplateBundle` coverage and additive required `GoalSlot` with exclusive `SlotCandidate` selection. A `ShareDecision` has a stable episode identifier plus occurrence-coordinate pairs `(unit_id,slot_id)`; any share is accepted only with proven compatible scalar-interval intersection. Time relationships remain SMC-3 exact event equalities. Result consists of a candidate `SymbolicPlan` (or none) and a **separate** `CompileReceipt` with input fingerprint, mapping provenance and projected rational task targets.

Versioned predicate trees support Strong Kleene `TRUE/FALSE/EQ/NOT/AND/OR`. Caller-built dataclasses do not enforce runtime types: Gate B must reject malformed keys, bool EQ expected values, wrong operand shapes, cycles and surrogate text *before evaluating eligibility*. Share members likewise require a tuple of two valid string coordinates before hashing, sorting or associating. See review 5 [negative and remediation receipt](SMC4_GATE_B_CODEX_REVIEW.md). Such rejections are `INVALID_PLAN` with **no partial executable plan**, never `INFEASIBLE` or automatic phonetic guessing.

### Sixth Codex specification check: predicate topology and canonical diagnostics

Structural equality of predicates, rather than Python object identity, governs compiler eligibility and receipt identity: a shared immutable child in an AND/OR expression is a valid DAG, whereas a cycle in the active path is invalid. The request fingerprint must be constructed before validation but may **never** recursively expand arbitrarily deep/cyclic Predicate dataclass content. An iterative predicate-specific digest represents invalid input without invoking recursive `asdict`; bounded validation then rejects cyclic/excessively deep trees. Multiple malformed bundle/slot rule declarations form one canonically sorted error set; the first declaration encountered must not determine `INVALID_PLAN` details. [Sixth-round test-first evidence](SMC4_GATE_B_CODEX_REVIEW.md).

### Seventh-round bounded DAG conditions and audit receipts (2026-10-25)

Strong Kleene `Predicate` is a *directed acyclic graph* with legal shared immutable subtrees. `valid_predicate` caches subtree height and enforces the maximum effective root-to-leaf depth (128 nodes) **at every attachment**, including previously validated children; true cycles are rejected. `evaluate` memoizes each node for a fixed context, avoiding exponential recomputation of `AND(p,p)` DAGs. The canonical request fingerprint for an invalid cyclic predicate is built by synchronous structural refinement independent of commutative AND/OR child traversal order; valid acyclic predicates retain exact bottom-up structural hashes. These are **synthetic software semantics**, not a validated language-phonetic rule engine. See [seventh Codex review ledger](SMC4_GATE_B_CODEX_REVIEW.md).

### Eighth external software audit: failure-receipt completeness and timing boundary

Malformed caller-supplied `TimeAnchor` or `TimeRelation` declarations are structurally validated before graph-coordinate lookup or hashing: tuple containers, correct dataclass members, string occurrence coordinates, genuine `Event` enums and exact `Fraction` event values are required. Any invalid shape receives `INVALID_PLAN` and **no partial SymbolicPlan**. `TaskDefinition` declaration validation accumulates a canonically sorted invalid-identifier set before refusal, irrespective of the order of equivalent definitions. A rejected cyclic predicate request must also retain full input identity: cyclic fingerprint refinement spans the number of reachable nodes rather than a fixed local radius, and hashes the graph size. See [eighth Codex review and immutable RED-to-repair evidence](SMC4_GATE_B_CODEX_REVIEW.md).
