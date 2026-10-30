# Gate A accession: independently checked source-publication claims
2026-10-30 JST | #244 #247 | PUBLIC_SOURCES_REVIEWED; NOT GOLD_FROZEN.

This document records observed public **publisher claims**, distinct from independently audited per-sample rights/independence and previously executed C0 hashes. Do not fuse licenses across sources.

## Candidate 1: original Joyo Kanji Yomi Benchmark
Source card https://huggingface.co/datasets/sbintuitions/joyo-kanji-yomi-benchmark/blob/main/README.md
License https://huggingface.co/datasets/sbintuitions/joyo-kanji-yomi-benchmark/blob/main/LICENSE
C0 observed revision 2ae383bcdac88dacf89c9ab84f9990eec55fe5c9; file SHA256 32a843f662c55f1876baf64f8dc3475cc7b777c576a8fea6b43a2343ff46e897. Publisher declares MIT (copyright 2026 SB Intuitions) and 13,095 native-reviewed target-kanji samples. Its normalized_pron has a bracketed *reading* target, not authoritative original Unicode source offsets or multiple acceptable **whole-utterance** gold paths. Two blind SMC annotators and family×4 full-path design not shown. Status: EXTERNAL_DESCRIPTIVE_AUDIT; do not import as the 880 test. Source embedded-text sublicensing requires verification beyond top-level MIT assertion. See DISCREPANCY.md for accepted-software audit count 45 vs earlier 39.

## Candidate 2: Parakeet JKYB Edition
Source https://huggingface.co/datasets/Parakeet-Inc/joyo-kanji-yomi-benchmark-parakeet/blob/main/README.md and published evaluator https://github.com/Parakeet-Inc/Joyo-Kanji-Yomi-Benchmark-Parakeet-Edition/blob/main/docs/METRICS.md
Publisher declares MIT license, original NOTICE attribution, 13,536 sentences, 3,440 modified historical examples, 441 additions, 75 sentences with multiple **natural target readings**, 55 with marginal target readings. Claims native-speaker review for changed or added rows, and describes some LLM-generated replacement sentences. These are publisher claims, **not** our independent per-row validation or a second blindly annotated full-utterance gold. Its reading conventions diverge from original Joyo, which disallows automatic score interchange. Status: INDEPENDENT_TRIANGULATION_CANDIDATE, exact revision and raw JSONL hash NOT YET ACQUIRED. The 75/55 ambiguity labels are informative but not automatically 80 legitimate A-stratum whole-path examples.

## Candidate 3: YOMI-Bench
Source https://github.com/benchmark-release/YOMI-Bench
Publisher declares CC BY-SA 4.0. Focuses on contextual kanji reading prediction/QA, including different context-dependent readings, but does not establish independent complete-utterance acceptable gold, same orthographic-word-family×4 structure, or source interval coverage. Status: SUPPLEMENTARY_HETERONYM_RESEARCH_CANDIDATE. Treat derivative/text redistribution and CC BY-SA obligations separately.

## Candidate 4: Japanese G2P Benchmark
Source https://github.com/o24s/japanese-g2p-benchmark ; README plus NOTICE.
Code Apache-2.0; evaluation dataset CC BY-SA 4.0; underlying datasets have mixed licenses such as CC-BY-SA, CC-BY, MIT and CC0. Suitable exploratory comparison, not unrestricted MIT whole-sentence gold; source/NOTICE must be reviewed case by case. Status: SUPPLEMENTARY_REFERENCE_ONLY.

## Candidate 5: Sato et al. Japanese heteronym prediction
Paper https://aclanthology.org/2022.lrec-1.770/
Scientific background for heteronym annotated corpora. A paper citation does not grant rights to reproduce the underlying source text or provide two new independent blind annotators. Status: METHOD_REFERENCE_ONLY.

## Provider: pyopenjtalk 0.4.1
Source https://github.com/r9y9/pyopenjtalk ; read LICENSE / README. Package MIT, bundled modified OpenJTalk modified BSD, other included assets carry separate terms. C0 actual execution verified real version 0.4.1, Linux/Python 3.11.17, active dictionary digest 88167f04755fe6f0973f5be05bf839aad53d600e190d7068b29d7af15c594dbd. This is HISTORICAL_B0_SOURCE_REPRODUCIBILITY, not current C1 runtime/version freeze and NOT linguistic accuracy or original source span evidence.

## Rights due diligence fields (required for every eligible case)
Rights holder/source URL and revision, verbatim license and derivative-use scope, internal processing permission, publication/redistribution allowance, commercial-use limitations, attribution and NOTICE chain, third-party embedded text origin, privacy/retention/access control, rights-reviewed-by and timestamp, exact text digest. A public MIT/CC BY-SA card is a publisher statement; do not assert each underlying sentence is legally cleared without review. Restricted text never committed into public Git; commit only metadata hashes/aggregates when permissible.

## Contamination and split
Public benchmarks may already be seen by open models in pretraining and may be reused for development; therefore no automatic 880 holdout use. Require separate licensed original sentences with anti-duplication by exact text, document, lexical family and near-duplicates, and unknown-contamination statement where model training data cannot be inspected. No public publisher-verified sample counts may stand in for SMC's own blind independent gold.

## Assessment
Sufficient public evidence to shortlist sources and specify rights review. **Insufficient** to freeze 120 pilot, 880 holdout, three human annotators, exact legal claims, C model weights or independent gold. Status MORE_DATA; no heldout run authorized.
