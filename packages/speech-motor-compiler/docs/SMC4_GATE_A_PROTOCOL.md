# SMC-4 Gate A — Task Semantics & Bounded Pronunciation-to-Task Lexicon

**Date:** 2026-10-24 JST  
**Status:** PROSPECTIVE DESIGN / IMPLEMENTATION NOT STARTED / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE  
**Owner issue:** [#174](https://github.com/ryonakayama234/morphoacoustics/issues/174)  
**Parent implementation (not merged to main):** SMC-3 [Draft PR #164](https://github.com/ryonakayama234/morphoacoustics/pull/164), **exact base SHA** `f36bfd5620268f07d5136d101303bcdc0afc0e7b`  
**Milestone:** Gate A only; this document and accompanying evidence registry precede any SMC-4 executable mapping implementation. Changes after design freeze must be explicit dated revisions, not retroactive edits to preregistered expectations.

## 1. Research question and claim ceiling

Can a bounded, versioned lexicon select **explicit, interpretable task-goal candidates** from caller-provided pronunciation hypotheses, construct independent MotorTask instances and many-to-many association edges with auditable continuity/sharing decisions, and **reject unknown or contradictory cases** without embedding body coordinates, inventing readings, or implying physical/phonetic validity?

A Gate A pass is a **design-consistency verdict only**. Future Gate B success means *only* deterministic symbolic mapping against preregistered artificial or source-audited fixtures. Acoustic production, correct Japanese articulation, execution in any morphology, phonetic transfer, and creative voice quality require other gates and evidence.

### Supported inherited software facts vs unanswered research

| Inherited from SMC-3 | NOT established by SMC-3 |
| --- | --- |
| Frozen `PronunciationUnit` with codepoint source spans; caller-provided `symbol` | Text-to-reading or verified Japanese pronunciation |
| `MotorTask(task_id,goal_kind,capability_requirements)` | Task-variable semantics or articulatory accuracy |
| Many-to-many `TaskAssociation` with stable IDs | Rule selecting or sharing tasks for actual phonetic targets |
| Exact-`Fraction` ONSET/OFFSET event equalities, structural/temporal rejection | Natural task timing, phase oscillator, coarticulation learned from recordings |
| Standalone Python package with red→green CI and Codex audit evidence | Body-binding feasibility, physics, audio, cross-morphology transfer |

Software provenance: [SMC-3 DATA](DATA.md), [Gate C Codex ledger](GATE_C_CODEX_REVIEW.md), [Issue #162](https://github.com/ryonakayama234/morphoacoustics/issues/162). `STRUCTURALLY_VALID` and `RESOLVED` are *not* phonetic/physical verdicts.

## 2. Scientific motivation and provenance rules

- Browman & Goldstein (1992), [Articulatory Phonology: An Overview](https://pubmed.ncbi.nlm.nih.gov/1488456/): utterances can be represented as **overlapping constellations of gestures**. Motivation for separate task instances and timing, not proof of this project's inventory.
- Saltzman & Munhall (1989), [A Dynamical Approach to Gestural Patterning in Speech Production](https://doi.org/10.1207/s15326969eco0104_2): task-based coordination links abstract control goals with movements; does **not** make all task variables anatomy-invariant.
- [TaDA manual, Haskins Laboratories](https://static1.squarespace.com/static/6463dc0cc0fa823cfe25e5fd/t/647f8ea67dc58526b1a6b0a5/1686081191000/TADA_manual_v091.pdf): precedents for gestural lexicon, coupled-oscillator planning and task dynamics. Do not adopt TaDA implementation, gestural corpus, or timing equations without separate scientific and licensing assessment.
- Shaw & Kawahara (2021), [Japanese devoiced [u] contextual articulation](https://pubmed.ncbi.nlm.nih.gov/34727587/): a phonemic/surface label **does not guarantee** one invariant tongue-body goal. Evidence for explicit language/context/uncertainty in candidate mapping, **not** approval of a special-case implementation for Japanese /u/.
- [VocalTractLab official 2.4 manual](https://vocaltractlab.de/download-vocaltractlab/VTL2.4-manual.pdf): reference for continuous gestural-score engineering, not verified data or code imported into this project.
- Project hypotheses: [MotorSkill/MotorPersona non-normative study](https://github.com/ryonakayama234/morphoacoustics/blob/main/docs/research/motor-skill-persona-hypotheses-v0.md). A stable *task/skill goal*, body-specific binding, and habitual choice of realization are different concerns; all Persona/learning hypotheses remain unvalidated.

**Source discipline:** label every claim `OBSERVED_IN_PROJECT`, `REPORTED_BY_LITERATURE`, `SYNTHETIC_DEFINITION`, or `HYPOTHESIS_UNVERIFIED`, with a resolvable source/revision. A structural test never upgrades a hypothesis into empirically verified speech science.

## 3. Conceptual data model (NOT a production schema)

### 3.1 TaskDefinition — type-level goal semantics

One *versioned, semantic* declaration describing:
- `definition_id` and `semantic_revision`, plus explicit `applicability_domain` (e.g., generic flow-path-equipped body vs human-like tract). **No assumption of a universally identical organ.**
- `task_variable`: named observable/controlled **functional relation** such as degree of constriction of a declared passage, not a phoneme, muscle name or direct waveform target.
- `value_domain`, `goal_region_or_value`, `tolerance_and_measurement_convention`, `temporal_scope_convention`; units or dimensionless normalization explicitly defined where meaningful. Targets never silently use `F1/F2` or anatomy mesh indices as canonical goals.
- `capability_predicates` needed for a body realizer to *attempt* binding, and `evaluability` (unknown/unsupported until a body-specific observation function is supplied).
- `evidence_ids`, `status` and `known_counterexamples`.

A planned semantic relation is `h_M(x_M(t)) ∈ T` on a declared activation interval: `h_M` is **supplied and checked by the body adapter**, not computed by the SMC lexicon. The existence of an `h_M` for arbitrary M must not be assumed. No optimization policy, actuator trajectory, joint coordinate, area-function samples, F0, audio or solver state is permitted in TaskDefinition.

### 3.2 TaskTemplate — context-conditioned proposed use of a definition

A versioned entry binds a **caller-supplied pronunciation pattern**, language/variant profile, phonological and phonetic context predicates, and `TaskDefinition` reference to a **candidate goal parameterization**. It also provides:
- `entry_id`/`lexicon_revision` and stable `evidence_ref`, license/provenance, applicability boundaries;
- explicit `coordination_rule_ref` without copying timing physics into lexical semantics;
- `candidate_status`: `SYNTHETIC_ONLY`, `LITERATURE_PROPOSED`, `PROJECT_MEASURED` (only after applicable project Gate), or `UNSUPPORTED`;
- unresolved alternatives when evidence cannot choose one realization; **no implicit probability that presents a hypothesis as certainty**.

The **Pronunciation Lexicon** (orthography→reading/hypothesis) and the **Task Lexicon** (given hypothesis+context→task templates) are different registries. Gate A and B begin *after* a supplied pronunciation hypothesis; no automatic kana/kanji inference.

### 3.3 MotorTask — occurrence/instance identity

An utterance Task instance has:
- independent stable `task_id`, `definition_id`, chosen `template_id`, `goal_params` and local utterance applicability;
- one or more `TaskAssociation` edges to candidate `PronunciationUnit` IDs;
- selection and any sharing-decision provenance; physical realization status is **not** an SMC-3 `ReportStatus`.

**Identity axioms:**
1. Same `TaskDefinition` or same goal parameters **does not imply** the same instance ID.
2. Multiple pronunciation units share one `task_id` **only with an explicit continuity/shared-occurrence decision** grounded in rule and context. Never deduplicate tasks by kind or label.
3. Repeating a goal in different occurrences yields distinct IDs even if one phonetic symbol is repeated.
4. Realized bodily actions may be coupled or adaptively modified downstream, but that cannot retrospectively alter the original task instance receipt.
5. A task instance can be proposed without an executable body; `UNVERIFIED` stays distinguishable from `INFEASIBLE`.

The existing SMC-3 v0 `MotorTask` and `SymbolicPlan` remain unchanged in Gate A. Consider a separate *mapping receipt* and a gated v1 schema adapter in Gate B; do not change physical/public schemas preemptively.

## 4. Bounded pronunciation-to-Task selection

Input: explicitly supplied hypothesis IDs, symbols, source codepoint spans, language/profile, context boundaries, lexicon revision and optional coordination recipe revision. Multiple readings or phonetic interpretations remain explicit alternatives, not resolved by hidden heuristics.

Proposed operations (all deterministic if inputs/revisions fixed):
1. Validate source/hypothesis and selected profile; reject malformed UTF-8-surrogate data and impossible spans using existing SMC-3 invariants.
2. Query *only* the finite eligible lexicon set, keeping origin and context matches; no best-effort fallbacks to arbitrary phoneme/gesture labels.
3. Resolve a unique explicitly qualified candidate or report `UNMAPPED` / `AMBIGUOUS`.
4. Create task instances and task-to-unit association edges. Apply **explicit instance-sharing rule**, not string equality of `goal_kind`.
5. Apply a separately versioned coordination recipe. Only map timing relations expressible by SMC-3 exact `ONSET`/`OFFSET` equality constraints; otherwise reject `UNSUPPORTED_COORDINATION` rather than invent oscillatory phase dynamics.
6. Run SMC-3 `validate_plan` and, if requested, `resolve_timing` with independent diagnostics. A structurally valid but unanchored timeline remains unresolved; do not synthesize absolute clocks.
7. Emit a normalized **compile receipt**: input hash, source and pronunciation provenance, lexicon/definition/rule revisions, chosen alternatives and Task IDs, sharing justification, rejection trace, SMC-3 canonical IR digest, compiler version. Unmappable or ambiguous candidates produce a receipt of rejection with **no executable plan**.

No phoneme name, section index, target vowel formants or waveform matching may substitute for a TaskDefinition's functional goal semantics. No assertion that any symbolic target can be realized by an arbitrary body.

## 5. Diagnostic ontology (distinguish stage and certainty)

| Stage | Candidate outcome | Meaning |
| --- | --- | --- |
| Input/pronunciation | `INVALID_INPUT` | malformed source/span/symbol; no plan |
| Lexicon resolution | `UNMAPPED` | no eligible entry for supplied pronunciation and context |
| Lexicon resolution | `AMBIGUOUS` | multiple eligible incompatible candidates without explicit selection |
| Task graph / timing | `INVALID_PLAN` / `UNSUPPORTED_COORDINATION` | malformed/contradictory graph, or unsupported coupling semantics |
| Pre-realization | `MAPPED_SYMBOLIC` + `UNVERIFIED` | graph built; no body feasibility claimed |
| Body adapter (future) | `UNSUPPORTED` | absent necessary capability or backend functionality; distinguish these in details |
| Body adapter (future) | `INFEASIBLE` | documented physical impossibility within defined model/constraints, **not merely solver timeout/nonconvergence** |
| Execution (future) | `EXECUTION_FAILED` | attempted realization terminated without desired outcome |

These proposed statuses are **not** replacements for current SMC-3 `ReportStatus`. They represent distinct pipeline stages. `MAPPED_SYMBOLIC` does not mean human phonetic appropriateness, `RESOLVED` does not mean body-feasible.

## 6. Frozen prospective adversarial fixture design

This table specifies **future Gate B expectations now**, before any SMC-4 implementation. Fixture inventory consists of **synthetic definitions and phonetic labels only**, not claimed Japanese observations. Fixtures must be stored with expected outcome independent of the implementation.

| ID | Input setup | Expected / falsifier |
| --- | --- | --- |
| F01 | P1→G1,G_shared; P2→G_shared,G2 with explicit share decision | Exactly 3 distinct tasks, stable shared ID, 4 links |
| F02 | Two P share same template kind with **no** continuity rule | Two separate task IDs; failure if automatically deduplicated |
| F03 | Repeat P symbol in separate occurrence with no rule | Distinct task instances and complete source association |
| F04 | Missing lexicon entry | `UNMAPPED`, no fabricated Task |
| F05 | Two incompatible context-eligible templates; no adjudication | `AMBIGUOUS`, both alternatives retained in diagnostic |
| F06 | Supplied invalid symbol/surrogate/span | `INVALID_INPUT` and fail-closed receipt |
| F07 | Explicitly incompatible Task selectors or dangling task-template ref | No `MAPPED_SYMBOLIC` plan; clear diagnostic |
| F08 | Two contradictory exact anchor/event equalities | `INVALID_PLAN`/`CONTRADICTORY_TIMING`, no resolved times |
| F09 | Reorder semantically unordered declarations and associations | Same normalized plan/receipt digest; no index-based ID semantics |
| F10 | Change lexicon revision or one context rule | Provenance/receipt changes, even when chosen `SymbolicPlan` happens to remain equal |
| F11 | Same TaskDefinition and accepted graph, vary Body M separately | Canonical *semantic* definition and plan unchanged; future body outcome may differ |
| F12 | Contradictory semantic goals within overlapping intervals | Explicit rule for when this is rejected vs deferred to body adapter; **must not claim detection absent defined goal algebra** |
| F13 | Unanchored-but-consistent coupling graph | `STRUCTURALLY_VALID` but temporal `UNRESOLVED`; no invented 0s |
| F14 | Unsupported relative-phase or arbitrary nonlinear coordination | `UNSUPPORTED_COORDINATION`; do not convert to invented exact lag |
| F15 | Missing/inapplicable empirical evidence for Japanese /a/→/i/ entry | `SYNTHETIC_ONLY` candidate may be tested, but **cannot** be exported as a calibrated Japanese articulatory mapping |

**Planned metamorphic/property tests:** input tuple permutations; substitution of same-kind distinct instances; explicit share vs split; provenance revision perturbation; unknown context; seeded adversarial graph arrangements; candidate discontinuity; Unicode codepoint vs grapheme; pass/fail separation of structural validation, temporal resolution, lexicon match and body feasibility. Freeze generators and exact seeds in Gate B *before running any candidate implementation*. Gate A does not purport to have executed them.

## 7. Targeted empirical bridge, not an implicit Gate A pass

Start with a **synthetic** `/a/, /i/, /a i/` label demonstration only to exercise structural mapping. Before any **Japanese phonetic** claim:
1. Audit V1 [#31](https://github.com/ryonakayama234/morphoacoustics/issues/31) and V2 [#32](https://github.com/ryonakayama234/morphoacoustics/issues/32) for *exact-SHA positive phonetic calibration and listening acceptance*; closed issue state alone is not evidence of vowel identification or natural voice.
2. Independently identify human-language TaskDefinition variable/target measurements and body compatibility; published articulatory results constrain hypotheses but do not supply a verified universal creature-space gesture.
3. Send task-annotated plans to **V3 [#33](https://github.com/ryonakayama234/morphoacoustics/issues/33)** for body-realization investigation. Feasibility, phonetic preservation, morphology transfer and sound synthesis are judged by that experiment, not claimed by SMC-4 Gate A/B.
4. A Japanese devoiced /u/ context rule is an **adversarial future research case**, not a default implemented dictionary entry, because reported targetlessness varies by context and speaker.

## 8. Future gates, preconditions and decision rubric

- **Gate A — DESIGN_ONLY** (this PR): domain semantics, registry boundary, provenance, identity/sharing rules, diagnostics, falsifiers and limits reviewed; no executable SMC-4 mapping code. Design can pass with explicitly unresolved physiological questions.
- **Gate B — SYNTHETIC_SYMBOLIC_COMPILER** (new PR only after Gate A review): implement versioned narrow lexicon and graph builder without changing existing v0/physics interfaces, run frozen fixture tests plus package Python 3.11–3.13/myPy and root regressions; preserve red failures at exact commit SHA and request fresh separate Codex AI code review.
- **Gate C — SCIENTIFIC LEXICON EVIDENCE** (separate scope): audit empirical Japanese task targets and contexts against original papers, licensing, speaker effects, project vowel reference measurements. Disallow promoting structurally passing artificial recipes into genuine human pronunciation truth.
- **Gate D — BODY REALIZATION** (V3 owned): bind goals to supported morphology, test feasibility, physical motion and sound identity independently; no body or waveform redefinition of canonical Task definitions.

**Decision vocabulary for Gate A:**
- `GO_DESIGN_ONLY`: terms, owner boundaries, non-goals, falsifiers and source-level epistemic labels explicit; allows Gate B prereg and implementation, **not scientific adoption**.
- `REVISE`: ambiguity in goal identity, link sharing, context disambiguation, impossible status or receipt prevents test oracle.
- `MORE_DATA`: real-language task mappings or body coverage require empirical evidence; retain synthetic design exploration if separately justified.
- `REJECT`: goals only expressible by frozen articulator coordinates or waveform tokens, or missing-data becomes silent fictional executable actions.

## 9. Audit and change control

This is an **implementer/assistant-authored** design, not independently preregistered science. Freeze this protocol in a docs-only exact SHA before any SMC-4 source implementation. Later scientific evidence cannot be claimed by rewriting this file; record dated amendments in separate commits/docs and preserve original SHA.

Open a stacked **Draft PR to `research/smc3-standalone-package-20261022`**, not `main`. At final docs SHA, check GitHub CI and ask Codex `@codex review` for an adversarial *software/design-spec* critique. Document bot completion SHA/finding states and resolve issues transparently. A no-findings code bot is neither human peer review nor proof of task scientific validity. Do not mark PR ready or merge as part of Gate A. The project owner may separately decide whether to open Gate B based on these receipts.

**Out of scope:** automatic Japanese reading, phonetic-feature inference, a universal species-independent tract, a copied TaDA dataset, phase-oscillator model, learned controller, MotorPersona preferences, stable public schema/API, Core or Studio integration, WAV output, neural polish, /u/ deletion modeling, and `main` adoption.
