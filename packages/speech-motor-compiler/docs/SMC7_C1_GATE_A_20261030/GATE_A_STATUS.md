# Gate A 2026-10-30 — actual accession result and critical path
Owner #244 / successor C1 #247 / design #251. Research-only, NO main, Core or Studio mutation.

## State: MORE_DATA_L1_LINGUISTIC_CORPUS_AND_INDEPENDENT_ANNOTATORS
We completed an **external source/publication audit and machine-checkable structural intake tool**, not the scientific linguistic-gold freeze. No real 120 pilot, 880 heldout multi-gold corpus or three independent blinded reviewers have been acquired or attested. None has been created by an LLM. This is NOT a green Gate A.

## Work completed now
1. Public source/license due diligence: original Joyo, Parakeet JKYB Edition, YOMI-Bench, Japanese G2P Benchmark, Sato 2022 and B0 OpenJTalk. Distinguish publisher claims from original C0 actual executed data SHA. SOURCE_RIGHTS_MATRIX.md.
2. Direct GitHub Actions source-and-log forensic audit uncovered a substantive historic discrepancy: **39** format nonadmissions at earlier SHA vs **45** at the accepted/reviewed C0 code SHA 5087bd5; same data SHA, 6 extra INVALID_KEY and 1 fewer accepted target-family identities. Independent review required, never silently mark 39 as current. DISCREPANCY.md.
3. ANNOTATION_PROTOCOL.md prepared for real 2 blinded Japanese readers and 1 independent adjudicator; raw disagreements, multi-gold, unknown, full-utterance and source-spans, split firewall. Draft requires pilot review before final freeze.
4. A bounded, offline, standard-library **gate_a_manifest_lint.py** structural validation tool created under research/ with synthetic-only self-tests. Run with --self-test (uses no corpus or external provider). It checks 120/880 counts, 100 heteronym families×4 at least 2 reading digests, split contamination via source hash/orthographic family/document, named separate A/B/C attestations, multi-gold, declared rights/status, IDs and hashes. **It NEVER certifies human independence, legality, textual content, biological truth or gold quality.** Even passing output is STRUCTURAL_CHECKS_PASSED_NOT_SCIENTIFICALLY_FROZEN, NOT GO.

## Required gate evidence
| ID | Necessary evidence | Status |
|---|---|---|
| A01 | Licensed 120 development pilot, no heldout overlap | NOT_OBTAINED |
| A02 | 400 C utterances; 100 exact orthographic WORD families x4 contrastive contexts and >=2 readings per family | NOT_OBTAINED |
| A03 | Ordinary 240 utterances (genres/punctuation) | NOT_OBTAINED |
| A04 | Names and OOV 160 (resolvable vs unknowable) | NOT_OBTAINED |
| A05 | Genuine context-underdetermined A80 and acceptable multi-gold | NOT_OBTAINED |
| A06 | Real independent Japanese-proficient blind A/B annotators | NOT_OBTAINED |
| A07 | Third independent human adjudicator; raw disagreements retained | NOT_OBTAINED |
| A08 | Per-case text rights, notices, source SHA, controlled store/retention | NOT_OBTAINED |
| A09 | Annotation normalization policy from pilot, target intervals and full paths | DRAFT |
| A10 | Family/document/text/near-duplicate leakage review | LINTER PREPARED, NO REAL DATA |
| A11 | Model/lexicon/tokenizer/prompt/decoding/seed pin selected solely on lawful pilot | NOT_SELECTED |
| A12 | C1 exact dependency/dictionary/provider re-verification | C0 HISTORICAL B0 ONLY |
| A13 | Public Joyo 6+8+31 row-wise human review | 6 𠮟 U+20B9F rows **SOURCE IDENTIFIED / PARSER REPERTOIRE MISMATCH**; 8+31 still OPEN (not intrinsic new-gold stop) |

## Structural manifest minimal fields
One JSON object {schema: "SMC7_GATE_A_STRUCTURAL_V0", cases: [1000 confidential metadata records]}. Per record: case_id, split pilot/holdout, stratum C/O/U/A, family_id (exact orthographic target family), document_id, source_sha256, context_sha256, rights_id and rights_status CLEARED, annotators {A: id, B: id, C: id}, blind_a_b true, adjudicated true, 1..8 gold_paths_sha256, gold_status (A MULTI or CONTEXT_INSUFFICIENT), and for C target_reading_sha256. Never publicly commit private text, unredacted true reviewer IDs or gold. SHA is a content identity, not a substitute for actual annotations or signature verification. The linter is a minimal screen, not a rights/provenance attestation.

## Critical path / next workers
- Data acquisition lead: lawfully create or find independent utterances for all four strata, avoiding public answer-key tuning, with per-case rights and exact source/doc/family IDs; keep protected gold secret from model development.
- Three independent humans: A/B blinded independent full-utterance annotation, C independent adjudication. Preserve original separate annotations and report agreement.
- Research auditor: audit rights and non-overlap; hard-freeze exact 120 and 880 source/annotation bytes plus acceptable variants and normalization; compare source hash with internal manifests. Treat any missed/unknown contested language case explicitly, not as auto-refused to improve scores.
- Model research: only use the lawful 120 pilot for selecting the local licensed C checkpoint, tokenizer, prompts, dictionary and inference budgets; freeze all BEFORE reading holdout outcomes.
- Separate original Joyo audit: enumerate the 6 new INVALID_KEY rows and 8+31 older failures for manual source/key/marker policy mapping, with earlier code version preserved. Do not claim source publisher errors without adjudication.

## Decision
PREPARATION COMPLETED; **SCIENTIFIC GATE A NOT COMPLETE**. Honest stop is MORE_DATA rather than synthetic gold or invented annotator signoff. Existing H1-H6 and original 880/120 preregistration remain untouched. No implementation of context generator, no blind heldout scoring and no Core/Studio/audio/public API/main merge.

## Executed checks and receipts (not scientific gold)
- GitHub Actions [40988272321](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40988272321): actual pinned public Joyo byte download, source SHA verification and **row-by-row old vs current policy replay** PASS (meaning reproducibility of admission discrepancy, not that public gold is accepted): old 39 vs current 45; all six newly rejected are 𠮟 U+20B9F, Extension B. The 45 keys and line numbers are in that job log. 8 source and 31 target-marker mismatches require expert review; zero pronunciation-accuracy metrics.
- GitHub Actions [40988272343](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40988272343): synthetic-only bounded Gate A structural manifest linter PASS on Python 3.11, 3.12, 3.13, including no-follow input and split/annotator/candidate-contrast adversarial fixtures. **No corpus/gold was provided** in these tests.
- Direct independent public reference for 𠮟 as a real Japanese Joyo ideograph: https://www.kanjipedia.jp/kanji/0002920800 ; independent Unicode U+20B9F registry https://www.cns11643.gov.tw/wordView.jsp?ID=666183 . These do not validate all sentences or override current strict C0 key policy.

To advance to actual scientific freeze, source permission and human annotation are still necessary. Do not represent these tests as Gate A scientific PASS.
