# SMC-4 Gate A — Amendment 01: Four Codex P2 Design Falsifiers

**Date:** 2026-10-24 JST  
**Status:** POST-FREEZE SPECIFICATION CORRECTION / DESIGN ONLY / NOT SCIENTIFIC ADOPTION  
**Parent frozen protocol:** [SMC4_GATE_A_PROTOCOL.md](SMC4_GATE_A_PROTOCOL.md), original *pre-review* commit [`cc626535cc32b56f13edbb4349f39e7cf5926e6d`](https://github.com/ryonakayama234/morphoacoustics/commit/cc626535cc32b56f13edbb4349f39e7cf5926e6d). **Preserve the original unchanged.**  
**Review origin:** Codex code/design review of [Draft PR #175](https://github.com/ryonakayama234/morphoacoustics/pull/175) at *exact initial review SHA* `44d21d1118ff8994af430e2abd4484030f60f3a2`. It identified four **P2 issues**: pronunciation-path alternatives, unknown-context semantics, incompatible shared-goal parameters, and an unfalsifiable semantic-conflict oracle.  
**Normative precedence:** The four specific clauses and new prospective fixtures here **supersede the corresponding ambiguous Gate A descriptions** in original protocol §§3.3–4 and fixture F12. All other clauses of the frozen protocol remain prospective, with no retroactive PASS and no SMC-4 implementation.

## A1. Mutually exclusive pronunciation paths MUST NOT be combined

### Problem / external finding

Original protocol §4 lists candidate unit IDs and source spans but never specifies which units form **one pronunciation interpretation**. SMC-3 allows multiple candidate units for the same source span; compiling each independently could produce a physically fictional union of mutually exclusive readings.

### New required semantics

- A `PronunciationHypothesisSet` has one `source_revision` and at least one distinct `PronunciationPath` keyed by `path_id`. Each path declares *the complete set of unit IDs for that interpretation* plus `coverage_required` source spans and an explicit completeness flag.
- Task compilation accepts **exactly one explicitly selected complete `path_id`**. Alternatives may be inspected in separate receipts, but tasks from different paths can **never** be combined into one `SymbolicPlan`. The same source span is legal across alternative paths but does not authorize a merged reading.
- If a hypothesis set contains more than one complete eligible path and none is selected, return `AMBIGUOUS_PRONUNCIATION_PATH` at pronunciation-selection stage, with candidate IDs but **no combined executable or mapped plan**. Do not rank alternatives by lexical order.
- If a selected path is incomplete (required source coverage has no resolved pronunciation), return `UNRESOLVED_PRONUNCIATION`. If input spans or identifiers are malformed, return `INVALID_INPUT`. `UNMAPPED` is reserved for a **well-formed, complete, selected pronunciation path** lacking a Task-lexicon entry. This distinguishes missing reading from missing motor knowledge.
- A selected path may retain explicitly documented overlapping unit spans when they describe distinct events in that *same* phonetic interpretation; Gate B initial fixtures use non-overlapping paths and do not infer such overlapping events. `path_id` is a grouping decision outside SMC-3 `PronunciationUnit`; do **not** mutate SMC-3 v0 in Gate A.

### Fixed prospective oracles

- **F16 (alternate readings):** source `"甲"`, two distinct complete paths `R_A` and `R_B` each with one unit covering [0,1], whose templates map respectively to `GA` and `GB`. When neither selected: `AMBIGUOUS_PRONUNCIATION_PATH`, no MotorTask graph. Selecting `R_A` yields only `GA`; selecting `R_B` yields only `GB`; never a graph with both.
- **F17 (partial reading):** source `"甲乙"`, selected path has only [0,1] and declares required coverage [0,2]. Return `UNRESOLVED_PRONUNCIATION`, no task plan even if existing unit matches a valid template. A complete selected path with a valid pronunciation label but absent Task template returns `UNMAPPED` instead.

## A2. Template context is three-valued; unknown is NOT false

### Problem / external finding

Original §4 has context predicates but no formal semantics for absent facts. A generic entry and a context-specific entry could choose different outputs depending on whether `not supplied` is treated as `false` or `unknown`.

### New required semantics

- Context facts have explicit provenance and state `KNOWN(value)`, `KNOWN_NOT_APPLICABLE` (only for fields for which N/A is semantically defined), or `UNKNOWN`. `UNKNOWN` must **not** evaluate as `false`. Values are caller-supplied or sourced from a named approved measurement; no inference from raw kana spelling or silent defaults.
- Predicates are evaluated using `TRUE`, `FALSE`, or `UNKNOWN` with a frozen three-valued AND/OR/NOT semantics (Kleene strong logic for initial Gate B), and typed predicates whose missing dependency yields `UNKNOWN`.
- Collect all `TRUE` eligible templates and all templates whose `UNKNOWN` predicate could become `TRUE`. If **any UNKNOWN competitor could change mapping selection**, return `INSUFFICIENT_CONTEXT` and a diagnostic naming missing typed facts. Do not silently use generic fallback.
- With all relevant facts known and several `TRUE` alternatives, the compiler may choose only if the lexicon contains an explicitly declared and versioned **unambiguous priority rule** for this disjoint candidate group. Missing/tied priority or incompatible equal priority => `AMBIGUOUS`; do not infer priority from apparent linguistic specificity.
- If no template has `TRUE` or `UNKNOWN` eligibility, `UNMAPPED` is correct. A `FALSE` entry is excluded based only on **known** contradictory context.

### Fixed prospective oracles

- **F18 (generic/specific with unknown):** a generic `T_ANY` is TRUE and a specific `T_DEVOICE` requires `devoiced=TRUE`, which is UNKNOWN. Return `INSUFFICIENT_CONTEXT`; no plan. If `devoiced=FALSE` is KNOWN, select generic. If `devoiced=TRUE` KNOWN, resolve via declared priority or return `AMBIGUOUS` when no priority. Do **not** claim this synthetic flag provides empirical Japanese devoicing identification.
- **F19 (no candidates vs missing fact):** one template predicate requires `context_location="X"`; when `context_location` UNKNOWN return `INSUFFICIENT_CONTEXT`; when KNOWN `"Y"`, return `UNMAPPED`; changing input tuple order does not alter outcome.

## A3. Explicit sharing also requires compatible goals and provenance

### Problem / external finding

Original identity axiom only requires an explicit continuous-episode decision. Two templates with same definition and episode may demand disjoint goal regions. A single MotorTask with only `template_id` and `goal_params` cannot represent both; first-wins is order-dependent.

### New required semantics

- A `ShareDecision` is a **proposal**, not permission to merge. It names a shared episode, contributing pronunciation units and **all contributing template IDs** with individual goal parameterizations and revisions.
- Initially, compatible sharing is decidable only when definitions and semantic revisions match, units/target algebra are identical, temporal scope is defined, and their task **goal regions have a nonempty intersection**. For bounded scalar interval goals `T1=[a,b]`, `T2=[c,d]`, combined goal is intersection `[max(a,c), min(b,d)]` if nonempty. Two other goal geometries require a *separately specified proven algebra*; do not assume generic intersection exists.
- The resulting one shared MotorTask is linked to **every contributing unit** and stores *all* template IDs, source facts, parameters and the derived intersection in its **mapping receipt**. Existing SMC-3 `MotorTask` may hold a summary goal_kind; it cannot be used as the only source of task target/provenance in Gate B.
- If goal regions are provably disjoint: return `TASK_SHARE_CONFLICT` / `INVALID_PLAN`, **no selected shared Task**, and do not silently split into two tasks or prefer whichever mapping occurs first. If compatibility is not decidable by the declared algebra, return `UNVERIFIED_SHARE_COMPATIBILITY` / no mapped plan; do not call it physically infeasible.
- If no sharing is requested, create distinct tasks even with equivalent goal regions and identical TaskDefinition. Lexicon tuples and task associations remain ordering-invariant under canonicalization.

### Fixed prospective oracles

- **F20 (compatible shared target):** P1 and P2 propose same single-valued scalar task definition+revision and episode: `T1=[0,2]`, `T2=[1,3]`. Output **one** task goal `[1,2]`, two links, receipt listing both templates and parameters, invariant under input permutation.
- **F21 (incompatible shared target):** same episode+definition, `T1=[0,1]`, `T2=[2,3]`. Return `TASK_SHARE_CONFLICT` (with both provenance refs), no plan; reversing template order must give the identical error.
- **F22 (unknown goal algebra):** same episode but templates use incompatible value domains or unregistered goal-algebra combination. Return `UNVERIFIED_SHARE_COMPATIBILITY` and no plan; not `INFEASIBLE`.

## A4. F12 obtains a falsifiable, two-branch semantic conflict oracle

### Problem / external finding

Original F12 allowed either rejection or deferral, so any implementation could pass. Define a hard synthetic inconsistency independent of anatomy and a separate genuinely body-dependent case.

### New required semantics

- A `TaskDefinition` may declare a **single-valued scalar variable** `q(t)` and a goal region that must hold **throughout** its explicitly known activation interval. Its algebra can detect a contradiction if two independent task instances constrain the same `definition_id`/`semantic_revision`/`q` during **provably overlapping positive-duration intervals** to disjoint target regions.
- Only infer this when activation intervals are established by consistent exact timing; uncertain/unanchored or only possibly overlapping schedules do not establish time overlap. If the goal algebra is not declared, do not label this conflict.
- When disjoint intervals demand conflicting values of the same `q(t)` but do not overlap in time, there is **no intrinsic semantic contradiction**; actual motion between them remains body-realization concern.
- Two different task variables, e.g., one abstract aperture and another source activity, may compete for mechanisms in a particular body; absence of that body interface means **UNVERIFIED physical co-feasibility**, not a symbolic contradiction.

### Fixed prospective oracles

- **F12a (must reject):** `G1` imposes `q(t)∈[0,1]` for `t∈[0,1]`; `G2` imposes `q(t)∈[2,3]` for `t∈[1/2,3/2]`. The two identical task-variable definitions overlap for positive duration; intersection empty. Return `TASK_GOAL_CONFLICT` / `INVALID_PLAN`, with no body claim. Fraction timing inputs are exact.
- **F12b (must defer):** `G1` controls a declared abstract passage-aperture variable, `G2` controls a separate source-state variable over the same interval; no shared goal algebra or body `h_M`. Return **`MAPPED_SYMBOLIC` + `UNVERIFIED`**, not `TASK_GOAL_CONFLICT`, `INFEASIBLE` or an automatically invented physical strategy.
- **F12c (must not reject):** same scalar `q` with disjoint goal regions `[0,1]` and `[2,3]`, assigned respectively to temporal intervals `[0,1]` and `[2,3]` (non-overlapping). No semantic goal contradiction; mobility and transition feasibility remain `UNVERIFIED`.

## A5. New diagnostic stage boundaries

This amendment adds the following *proposed* candidate outcomes to the original ontology (no SMC-3 v0 enum change):

| Stage | New outcome | Precise meaning |
| --- | --- | --- |
| Pronunciation path | `AMBIGUOUS_PRONUNCIATION_PATH` | More than one complete path, none explicitly selected |
| Pronunciation path | `UNRESOLVED_PRONUNCIATION` | Selected path fails declared required coverage/completeness |
| Context resolution | `INSUFFICIENT_CONTEXT` | Unknown predicate could change candidate selection |
| Shared task construction | `TASK_SHARE_CONFLICT` | Proven disjoint goals for an explicitly requested shared task |
| Shared task construction | `UNVERIFIED_SHARE_COMPATIBILITY` | No applicable goal combination algebra; cannot approve sharing |
| Symbolic goal-algebra | `TASK_GOAL_CONFLICT` | Same declared single-valued variable, provable concurrent disjoint constraints |

Precedence for the initial Gate B compiler: invalid input → path selection/completeness → missing context → lexicon match/selection → sharing and goal algebra → SMC-3 structural/timing resolution → separate body status. When multiple defects exist, preserve all reliably detectable stage-local diagnostics in a receipt but **never** emit partial mapped/executable task plans; do not claim a unique global diagnostic priority beyond this pipeline. UNKNOWN, UNSUPPORTED, unverified physical feasibility, and proven symbolic contradiction are distinct.

## A6. Audit trail, new fixture count and Gate disposition

- Prior protocol prospective fixtures **F01–F15** remain unchanged in the original code-free frozen record. F12's exact pass/fail expectation is now explicitly **F12a/b/c** in this amendment, and original F12's vague alternatives must not be used as the Gate B oracle.
- New **F16–F22** fixed prospective fixtures test path selection, unknown context, merging and compatibility. These are **not yet executed**. Do not call them red/green implementation evidence.
- All four P2 findings are design defects caught by Codex review at `44d21d...`; no preregistered code tests failed because SMC-4 has no executable implementation. Record review thread IDs and subsequent changes with exact SHAs.
- A revised design can be reviewed to support `GO_DESIGN_ONLY` but cannot prove real Japanese phonology, body transfer or audio. No main merge or SCIENCE_ADOPTED.
- If implementation finds the chosen limited goal algebra insufficient, record `REVISE`/new revision before seeing test outcome. Do **not** silently generalize to unproven anatomy-specific gesture targets.

**Owner decision pending:** after documentation CI, a fresh Codex review of this exact amended head and explicit outcome report. Draft PR only.
