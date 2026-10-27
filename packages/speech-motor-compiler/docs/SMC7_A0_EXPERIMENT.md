# SMC-7 Gate A0 — prospective hypotheses, falsifiers, experiments (NOT preregistered / NOT run)

**2026-10-27 / Issue #229 / HYPOTHESIS_UNVERIFIED / NO_CODE / NO_MAIN_MERGE.** This is the design-before-prereg phase; **none of H0–H8 or F01–F16 is frozen as an executable protocol**. Later Gate A must freeze actual stimuli, gold data, metrics, thresholds, seeds, provider/policy versions, reviewer and negative-case oracle BEFORE test/source implementation.

## Hypotheses with explicit competing explanations / falsifiers

| ID | Investigable hypothesis | Null / alternative explanation | Falsifier or STOP |
| --- | --- | --- | --- |
| H0 compatibility | A correctly selected path projected to the existing schema yields exactly the same SMC5 plan/goals and SMC6 COMPATIBILITY as a direct, semantically equal canonical request | Adapter mutates semantics or times while appearing to succeed | any differing goal, share, event, relevant hash or status |
| H1 alignment | Valid complete paths and declared boundary/silent intervals account for the original source without invented/deleted characters | Provider's concatenated kana hides span loss | any accepted path with invalid source mapping |
| H2 candidate utility | A bounded candidate set can improve gold-path coverage over single deterministic G2P baseline at an explicitly limited candidate burden | Recall can rise trivially by enumerating many garbage readings | no gain at predeclared cap, or burden/false-unique over budget; avoid post-hoc metric selection |
| H3 uncertainty honesty | Heteronyms, OOV and insufficient context can stay unresolved or require explicit actor selection | Hidden top-1 decision creates false certainty | confident unique selection without required evidence/policy, or silent guess on annotated ambiguous case |
| H4 separation | Proposal-only, unselected or unsupported candidate yields no MotorTask plan | SMC5 inadvertently compiles mixed alternatives | any plan or candidate digest from an unselected/rejected path |
| H5 lexical/semantic STOP | Qualified reading can still be rejected at SMC5 TaskLexicon or future Core mapping without synthetic→physical relabeling | lexical labels falsely equated to organs | any Core gesture/physics/audio result from unsupported synthetic meaning |
| H6 version identity | Pinning exact versions/provenance yields deterministic results and semantic changes alter correct identity | mutable dictionary/state leaks into outputs | mismatch on exact rerun or false identity preservation after changed reading |
| H7 resource bounding | Candidate growth and invalid/mixed-script requests fail closed under finite input/candidate budgets | combinatorial explosion / partial output | nondeterministic truncation or usable partial plan after limit |
| H8 timing boundary | Compatibility preserves exact SMC5 constraint equality; arbitrary natural phase/overlap inference is not asserted | generic schedule witness mistaken for natural utterance | silent override, preferred timing claims, unsat displayed as feasible |

## Prospective fixture families (design proposals, *not observed outcomes*)

| ID | Input / intervention | Expected type of evidence, not expected measured success |
| --- | --- | --- |
| F01 | kana-led 'ありがとう' and script revision ID | full path/span and selected-path replay |
| F02 | ambiguous '生物を運ぶ' with differing readings | two distinct path identities, no union of readings/tasks |
| F03 | '今日は……ありがとう' punctuation and pauses | distinguish non-spoken boundary vs actual lexical units |
| F04 | proper name not covered by frozen dictionary | UNKNOWN/abstain trace, no invented reading |
| F05 | 'ありがとう🙂' / mixed Latin or numerals | explicit normalization/unsupported policy and original-span preservation |
| F06 | decomposed dakuten vs composed Unicode, half-width kana, CRLF | exact original source preservation, no silently aliased digests |
| F07 | same text, revised context or dialect profile | independent candidate/evidence identity with unchanged source |
| F08 | multiple proposed complete paths but no selection | PROPOSE_ONLY never compiles mixed candidate |
| F09 | manually selected valid path vs equivalent direct SMC5 wire | exact SMC5/6 compatibility equality |
| F10 | TaskLexicon coverage absent for valid reading | UNMAPPED_TASK refusal, no partial MotorProgramCandidate |
| F11 | SMC5 exact timing contradictory or SMC6 UNSAT | no admissible timeline, no forced fit |
| F12 | same shared task referenced by two selected units | one occurrence, independent graph/receipt audit |
| F13 | change candidate goal or chosen reading while other plan parts constant | digest sensitivity, no silently reused Take/plan |
| F14 | artificially many homographs / many readings | hard bounded candidate count, deterministic refusal/truncation flag (policy to decide) |
| F15 | malformed Unicode/forged canonical request/stale source span | explicit rejection with evidence, no trusted plan |
| F16 | any proposed field including organ position, F0, SPL, neural waveform or Core success | forbidden-output audit (no body leakage) |

F01 is not a proof of natural /aɾigatoː/ articulation; F02 is not a word-sense-disambiguation benchmark without annotated context/reference, and illustrative readings are **not a dataset**.

## Independent evaluation and controlled comparisons

1. Gate A design freeze: select sources with stated license and version; define small audited orthography/reading gold sets with multiple correct readings where legitimate; blind adjudication of ambiguous cases; split by source/document to reduce leakage.
2. Construct a **manual-selected** path oracle for exact downstream SMC5/6 nonregression, using a frozen synthetic TaskLexicon known to be supported. This is software compatibility only.
3. Compare pinned deterministic G2P single path to bounded candidate proposal under the **same** held-out cases: candidate recall @k, candidate burden, selected accuracy and selective risk, false-unique rate, alignment correctness. Do not import gold reading into generator; choose model versions before holdout evaluation.
4. Independent implementation or manually audited reference checks Unicode source spans, entire-path set membership, normalized kana error, selected-path provenance, and SMC5/6 exact event arithmetic. A checker must not call the algorithm it checks.
5. Red-before-green sequencing after authorization: preregister; test-only missing module RED; source; exact-head isolated Python 3.11–3.13 pytest and mypy; Core regression as interface nonregression (not voice-quality evidence); independent Codex software review (not scientific peer review); preserve all receipts.
6. Later L2/L3 gates require separately approved Core physical binding and scientifically controlled actual sound/creator listening. Studio's rejected WG2 quality is a warning: math success alone does not authorize creator-facing speech.

## Gate rules (to finalize **later**, before code)

- **A0 DONE** means a reviewable design and open decisions, NOT a frozen test protocol or scientific adoption.
- **Gate A FROZEN** only when gold set, corpus terms, sample sizes, k/budgets, expected failure classes, analysis code independence, acceptance/error thresholds and target exact parent SHAs are approved. All actual tests are subsequent.
- **L0 GO_LIMITED_SOFTWARE** (future) could accept exact compatibility/replay/refusal under frozen fixtures and review, explicitly *not* Japanese quality.
- **L1 GO_LIMITED_LINGUISTIC** (future) additionally requires independently annotated, held-out reading metrics and predeclared acceptable risk/burden thresholds.
- **MORE_DATA / REVISE / STOP** if unreliable oracle, invalid licensing, candidate-evaluation gaming, failures of stage separation, or unmet gates. **NO_PUBLIC_MOTORSCORE / NO_BODY / NO_STUDIO_UI / NO_MAIN_MERGE** remain separate constraints.

## Evidence sources
- SMC4 Gate A and amendments, SMC5 Gate A, SMC6 Gate B RESULTS, https://github.com/ryonakayama234/morphoacoustics/pull/225 .
- Natural speech gestural score methodology is not equivalent to symbolic time windows: https://pmc.ncbi.nlm.nih.gov/articles/PMC3528686/
- Japanese heteronym corpus methodology: https://aclanthology.org/2022.lrec-1.770/ . Test set candidates are NOT downloaded or accepted at this design stage.
