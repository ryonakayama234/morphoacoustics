# SMC-7 Gate A frozen protocol — L0 bounded reading-path sidecar
**2026-10-28 JST | Issue #231 | GATE_A_FROZEN_BEFORE_TESTS / NO_IMPL / NO_MAIN_MERGE**.
**Parent:** reviewed A0 design #230, corrected P2 via SMC7_A0_REVIEW_AMENDMENT_01.md; exact parent HEAD ebd13629dfd8c43aa60e3bd4ea101d8054bfc3b5; SMC6 inherited exact code head 0caa70f6bb8333f60fbcc2f29ea57578c998033c. No accepted Japanese phonetic/real motion/voice claim.

## L0 only: questions and negative controls
Implement isolated new `morphoacoustics_smc.reading_paths` research module only, no changes to inherited SMC3/4/5/6 types, package __init__, Core, Studio, or Public Performance/MotorScore contracts. Expose small frozen-by-tests *research API*:
- `ReadingUnit(unit_id, symbol, start_offset, end_offset)`; `ReadingPath(path_id, units, evidence_id)` with immutable tuples.
- `ReadingProposal(source_text, source_revision, source_digest, paths, status, code, proposal_digest)` and `ReadingExecution(status, stage, code, smc5, smc6)`.
- `propose_kana(source_text, source_revision)`: **orthographic-character passthrough ONLY**, exactly one path labelled source-evidence `ORTHOGRAPHIC_ONLY`, only Hiragana U+3041..3096 or Katakana U+30A1..30FA and a finite, explicit silent separator set [space, newline, tab, 、 。 ！ ？ …]; each supported character an independent source interval, NOT linguistic segment/phoneme/gesture. Reject unknown kanji, emoji, digits, combining mark, mixed Latin as UNKNOWN_READING with zero paths. No auto pronunciation inference of kanji, long vowels or phonetic processing; U+30FC long mark unsupported for this first slice.
- `make_proposal(source_text, source_revision, paths)`: accept caller-supplied **complete** hypotheses only, with provenance label evidence_id; no claim of pronunciation truth. All non-silent original codepoint positions covered exactly once per entire selected path; unit spans sorted/nonoverlapping; multiple paths preserved, **no union of alternatives**. A path with a multi-character span allowed in explicit mode; no normalization.
- `compile_selected(proposal, selected_path_id, canonical_wire, temporal_scenario)`: selection actor explicitly passes existing path ID (no implicit selection). Revalidate canonical SMC4-BR wire through `parse_canonical_request`; require exact original text, revision, language=ja, selected path ID, unit IDs/symbols/spans and completeness; never generate TaskLexicon, timing or capability from text. Recompile exact bytes with SMC5 `compile_wire`; if RESOLVED analyze exact SAME bytes and explicit external SMC6 TemporalScenario in COMPATIBILITY lane. If SMC5 rejects, do not call temporal. If SMC6 UNSAT/REJECTED retain authenticated SMC5 result and SMC6 diagnostic, but NO scheduled candidate. If success return stage-labelled SYMBOLIC_READY: only symbolic synthetic research, NOT a published MotorScore or physical quality claim.
- Input caps before work: source codepoints 1..256; UTF-8 source <=2048 bytes; paths 1..8; units each path 1..32; unit_id, path_id, evidence_id nonempty ASCII printable <=80 chars; symbol nonempty <=32 codepoints, no surrogates; revision ASCII printable <=80. Never accept arbitrary Python graphs as canonical wire. Limit proposal budget strictly; no silent candidate truncation. Optional argument that does not have correct Python type returns explicit rejection rather than uncontrolled exception.

## Frozen Gate B falsifiers (actual tests only AFTER this protocol commit)
F01 kana-only 'ありがとう' emits 5 exact source-span labels; pronunciation truth unclaimed.
F02 '生物を運ぶ' and mixed unknown produce UNKNOWN_READING / no paths; zero implicit candidate.
F03 explicit two complete alternative paths for '甲乙' retain independent identities; absent path selection produces SELECTION_REQUIRED and no SMC5 result.
F04 duplicate/out-of-order/overlapping/gapped spans are rejected; silent punctuation allowed only in designated set; no silent normalization or text loss.
F05 NFC/decomposed/source revision/difference in symbols change relevant identity; invalid surrogate and unsupported Unicode fail closed.
F06 candidate budget overflow, overlong source and invalid types fail predictably with no SMC5/6.
F07 valid manual hypothesis matching authenticated `test_smc5_preregistered.valid()` `p1` selected path yields EXACT SAME SMC5 plan/candidate digest and SMC6 result as direct legacy `compile_wire(encoded(valid()))`; scenario explicitly `TemporalScenario("smc7-compat","COMPATIBILITY", Fraction(2),Fraction(1,100),())`.
F08 temporal scenario with same wire but horizon Fraction(1,10) leads SMC6 UNSAT; preserve original SMC5 successful candidate digest and SMC6 source candidate digest; return no SYMBOLIC_READY, no witness/events.
F09 canonical wire with same source but changed selected path or symbol/offset/revision rejects BEFORE SMC5/6; do not reconstruct a new lexicon to make it pass.
F10 SMC5 deliberate UNMAPPED result preserved as mapping refusal; no temporal output; no guessed Task from Japanese characters.
F11 unknown SMC6 lane override rejected by wrapper, even when known SMC5 wire; no timing mutation.
F12 two deterministic executions of exact inputs return equal receipts; different original codepoint strings distinguish identities.
F13 silent/prohibited physical fields absent; neither module provides native audio, organ geometry, motor commands or real speech quality.
F14 independent checker reconstructs source coverage and SMC5/SMC6 comparison without calling under-test proposal builder/validator.

## Evidence and thresholds
All F01–F14 exact semantic invariants required 100% (no tuning), Python 3.11/3.12/3.13 package pytest, strict mypy, existing root test and bounded SV1 regression, third-party Codex AI software review of code-bearing exact HEAD; preserve RED→GREEN and source SHA. Independently compare SMC5/6 results at EXACT matched scenario; no quality score shortcut. Gate classification `GO_LIMITED_L0_SOFTWARE` only, conditional on actual passing external CI and review; `MORE_DATA` if review/CI unavailable, `REVISE` on defects, `STOP` on trust-boundary violation.

**Explicitly out of scope:** L1 real Japanese homograph G2P accuracy, external corpus download, learned model/dictionary dependency, accent/devoicing, speech timing preference, body execution, wav/ASMR, stable public MotorScore and Studio UI. A0 L01-L16 remain future multi-layer plans; do NOT call L1 GO without held-out licensed annotated data and separate preregistration. See CORE #227 for model-physical binding. No main merge.
