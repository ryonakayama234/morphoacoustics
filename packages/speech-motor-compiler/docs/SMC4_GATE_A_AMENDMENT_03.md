# SMC-4 Gate A — Amendment 03: Nonoverlapping Lexical Mapping Scope for Initial Compiler

**Date:** 2026-10-24 JST  
**Status:** THIRD TRANSPARENT POST-FREEZE SPECIFICATION CORRECTION / NO EXECUTABLE COMPILER  
**Review origin:** GitHub Codex's third review of [Draft PR #175](https://github.com/ryonakayama234/morphoacoustics/pull/175), exact prior SHA `36737a0f9fe7537a735586759ccbee23d2c0337a`, P2 **overlapping mapping-scope ambiguity**.  
**Preservation:** Original protocol SHA `cc626535...`, Amendment 01 `4686726...`, Amendment 02 `da0fb2f...` remain intact and historically visible.  
**Normative precedence:** This amendment supersedes **only** the `unit or unit-context span` target-scope allowance in Amendment 02 §2–§3 for **initial Gate B implementation**. It narrows the domain rather than introducing a new overlapping-span selection algorithm. Context may inspect neighboring units; a bundle **always targets one unit occurrence**.

## 1. Problem and minimal-domain choice

Consider selected complete PronunciationPath containing P1 and P2. A lexicon supplies candidate bundles B1(P1), B2(P2), and B12(P1+P2). Amendment 02's "exactly one Bundle for each mapping scope" does not decide whether compiling B12 alone, B1+B2, or all three is intended; all could be accepted by independent per-scope choice, creating contradictory Task graphs.

The first research-only Gate B compiler **will not** implement multi-unit mapping scopes, compositional chunking or span-level recipe precedence. Keep that as a *separate, explicitly preregistered future research gate* after the per-unit semantics are tested.

## 2. Normative selection and coverage contract

- After explicit selection of **one complete PronunciationPath**, create an ordered finite set of distinct `PronunciationUnit` **occurrences** keyed by path-local unit ID. Each valid unit occurrence is a **required mapping target**. Mapping coverage must equal the whole selected set of required unit occurrences; no dropped or duplicate coverage. Source codepoint spans belong to pronunciation provenance and do **not** define independent Task-lexicon mapping scopes.
- Every Gate B v0 TemplateBundle must declare `target_scope_kind=EXACT_ONE_SELECTED_UNIT` and exactly one target `unit_id`. A bundle may have **context predicates referencing adjacent unit IDs or declared utterance facts**, without claiming to map/consume those neighboring units.
- **Before** selecting bundles, validate the finite lexicon in the requested compilation profile. If any potentially applicable bundle advertises multi-unit or overlapping mapping scope for a required unit, emit `UNSUPPORTED_MAPPING_SCOPE` with its IDs, mark selection invalid and **return no mapped plan**. Do not silently ignore B12 and continue with B1+B2. Non-applicable entries in a wholly distinct explicit lexicon profile need not block that other profile; there is no hidden profile fallback.
- For each selected unit occurrence, select **exactly one** applicable `TemplateBundle` according to Amendment 02's `TRUE/FALSE/UNKNOWN` and bundle-scoped explicit priority semantics. If none: `UNMAPPED`. If competing true without priority: `AMBIGUOUS`. If unknown could alter choice: `INSUFFICIENT_CONTEXT`. Stop with no partial mapped plan on any failure.
- Within selected bundle, materialize every REQUIRED additive GoalSlot and exactly one exclusive candidate TaskTemplate per slot. The union across different units' selected slots forms the input for independent `ShareDecision` compatibility (Amendment 01 §A3), not automatic instance deduplication.
- All selected required `unit_id` occurrences **must appear** in at least one TaskAssociation; all emitted tasks linked to at least one selected unit. No plan may contain unselected candidate-path IDs or cover the same unit by two competing TemplateBundles. Canonical ordering ignores input tuple order and relies on stable path-local IDs.

**Why this is limited:** Real fluent speech often has chunk-level/coordinated gesture organizations spanning multiple units; not implementing multi-unit lexical recipes in Gate B does **not** deny such phenomena. It is a deliberately small, testable first representation. Future research may add a segmentation/cover algorithm with explicit exclusivity and overlap semantics, only through a newly preregistered version.

## 3. Frozen prospective oracles (not yet run)

| ID | Fixture | Expected |
| --- | --- | --- |
| **F28** | Selected path P1,P2, B1 targets P1, B2 targets P2, B12 targets both P1+P2 in same requested lexicon profile | **`UNSUPPORTED_MAPPING_SCOPE`**, no mapped plan, preserve B12 ID; never emit B12 or B1+B2 as silent default |
| **F29** | Same selected path with **only** B1(P1) and B2(P2), each containing required additive goal slots | Exactly one selected Bundle per unit and complete coverage. Tasks are union of all required slots, subsequently subject to explicit share compatibility, and associations cover P1/P2 |
| **F30** | One selected P1 has two competing TRUE bundles both exactly one-unit scope, no priority | `AMBIGUOUS`, no plan. Equivalent lexical reordering does not change diagnostics |
| **F31** | Bundle B1 maps P1 but references neighboring P2 only in a fully known context predicate; B2 maps P2 | **Permitted per-unit scope**; if context facts satisfy predicate, both units covered exactly once. If referenced context is UNKNOWN and could alter B1 selection, `INSUFFICIENT_CONTEXT` |
| **F32** | Selected complete path P1,P2 but only a P1 bundle exists | `UNMAPPED` citing P2, **no partial mapped plan** (not 1-task success) |

F01 still means two units, each with one bundle of two required additive slots, and one explicitly shared compatible `source_activity` instance yielding **exactly three** tasks and four associations. No special P1+P2 "bundle" is required to share a task.

## 4. Reviewer and Gate boundaries

- This is an **AI-assisted design correction**, not an actual compiler implementation or source-verified natural language articulatory model.
- No SMC-3 schema/v0 editing; no Core, Studio, performance-contract, body solver or waveform changes.
- Keep this amendment and all prior freeze SHAs; run exact final-head CI and request one distinct Codex review of the **entire** docs design at that SHA.
- `UNSUPPORTED_MAPPING_SCOPE` is a **compile-layer unsupported schema**, not physical `UNSUPPORTED` and not `INFEASIBLE`.
- Gate A remains `DESIGN_REVIEW_PENDING`, with possible `GO_DESIGN_ONLY` (only future Gate B planning) / `REVISE` / `MORE_DATA` / `REJECT`; no science or main merge.
