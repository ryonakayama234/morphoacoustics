# SMC-7 C1: DATA — 証拠・中間表現・信頼境界
2026-10-30 JST. DESIGN_COMPLETE / CREATOR_APPROVAL_PENDING / NO_NEW_PUBLIC_SCHEMA / NOT CORPUS-FROZEN.

## Conceptual data structure (not a claim of implemented API)
~~~mermaid
erDiagram
 SCRIPT_REVISION ||--o{ LINGUISTIC_CASE : contains
 LINGUISTIC_CASE ||--o{ ACCEPTABLE_GOLD_PATH : adjudicated_independently
 SCRIPT_REVISION ||--o| CANDIDATE_POOL_RECEIPT : produces
 CANDIDATE_POOL_RECEIPT ||--o{ COMPLETE_READING_PATH : contains
 CANDIDATE_POOL_RECEIPT ||--o{ RANKING_RECEIPT : shares_membership
 RANKING_RECEIPT ||--o| SELECTION_RECEIPT : selection_optional
 SELECTION_RECEIPT ||--o| VERIFIED_ALIGNMENT : requires
 VERIFIED_ALIGNMENT ||--o| SMC4_CANONICAL_REQUEST : safely_projects
 SMC4_CANONICAL_REQUEST ||--o| SMC5_6_RECEIPT : replay
 RANKING_RECEIPT ||--|| EVALUATION_RECEIPT : audits
~~~

## Fields, ownership, admissibility
1. ScriptRevision: immutable original UTF-8, Unicode scalar sequence, original codepoint length and half-open codepoint spans, source digest, context digest and separately declared language/profile/permission. No covert NFC/NFKC, byte/token/grapheme offsets substitution or changed text with reused receipt.
2. LinguisticCase: case ID, orthographic-family and document grouping IDs, stratum C/O/U/A, source rights/NOTICE, source/target original spans independently annotated; multiple valid or genuinely unknown readings permitted. Annotator and adjudicator lineage separate from model output.
3. AcceptableGoldPath: 1..n complete utterance katakana alternatives, complete normalized-reading rule revision (long mark, particles, punctuation, small kana, variants and unknowns), target reading, blinded reference provenance, raw interannotator disagreement. Katakana reading does NOT establish IPA, devoicing, accent, anatomical motion or sound quality.
4. ProviderManifest: exact provider/model weights/tokenizer/prompt/decoding/seed and dictionary binaries, package and transitive dependencies, host hardware/Python/OS, available legal use and redistribution constraints, timeouts and resource budget. A caller-supplied version string or hash-shaped text does not authenticate a provider by itself.
5. CandidatePoolReceipt: original case/source identity, producer versions, context-isolation rule, finite deduplicated complete-path membership, pool digest, origin of every candidate, search budget, pruning/discard count and refusal. Pool must not contain inserted heldout gold or C preferred answers for fixed-pool ranking inference; identical membership and canonical identity passed to B1/C-mask/C.
6. RankingReceipt: same pool ID, arm ID, exact context view/masking digest, permutation/rank, uncalibrated scores unless independently calibrated, abstention/refusal/latency, provider ID. No rank automatically selects a path.
7. L1CandidateSet: 0..3 validated full utterance paths for existing L1 wrapper. A proposed ranker may have wider internal search, but search pruning is openly recorded and cannot be misreported as exhaustive enumeration. Existing wrapper refuses >3 supplied paths; do not change that contract. Unknown/OOV may result in no proposal, not invented certainty.
8. AlignmentReceipt: separately verified original source positions and complete pronounceable coverage, explicit silent/unresolved source intervals. B0 G2P output lacks automatic authoritative source spans; tokenizer or substring projection alone never proves alignment.
9. SelectionReceipt: explicit authorized actor, in-set path ID, exact source/context/pool/policy/provider versions. Revalidation on every handoff; no selection receipt when candidate set is empty or source identity changed.
10. EvaluationReceipt: immutable method+code+dataset versions, all-case eligibility and refusal counts, locked acceptable gold lookup restricted to evaluation, arm outputs, paired cluster identifiers, numeric metrics and CI seed, exact byte digest. Never feed reference annotations back into model prompts.
11. MotorBridgeReceipt: optional independently gated old SMC4 canonical wire to existing SMC5 synthetic-only plan and SMC6 COMPATIBILITY. No generic Japanese TaskLexicon fabrication, guaranteed FEASIBLE body result, or new motor timing/physical value.

## Data/firewall contract
A separate 120-case **pilot** may inform normalization instructions, candidate provider selection and evaluator bugs. The 880 **heldout** cases are C 400 (100 families×4 contrastive contexts), O 240, U 160, A 80; no family, document or text overlap with pilot. Two competent independent Japanese annotators, blind to model predictions, and a third adjudicator; preserve original disagreement. Record licensed source provenance, access rights, exact split and corpus digest before any heldout prediction; if unavailable => MORE_DATA, not invented labels.

## Joyo external audit is NOT the primary heldout
Observed C0: source rev 2ae383bcdac88dacf89c9ab84f9990eec55fe5c9, file SHA256 32a843f662c55f1876baf64f8dc3475cc7b777c576a8fea6b43a2343ff46e897; 13,095 rows, 39 flagged by our strict format convention (8 source/key, 31 marker). This does NOT imply publisher errors; Joyo annotates target kanji and marked full-sentence katakana but is not automatically the independent, multi-gold, whole-path corpus required by #244. Do not tune on public benchmark answer keys or silently omit flagged rows.

## Immutable evidence and publication
Git records document versions, scripts, reviews, graphs, source/manifest hashes and permissible aggregates. Restricted material stays in controlled access; metadata and license/NOTICE references remain discoverable. Every result binds exact code SHA + model/dictionary/hash + corpus/split/annotation/manual + normalization + method + actor + result; hash identity is not correctness/rights/authentication. Distinguish MODEL_UNKNOWN, DATA_UNAVAILABLE, UNLICENSED, GOLD_UNRESOLVED, ALIGNMENT_UNVERIFIED, CANDIDATE_LIMIT, NO_SELECTION, TEMPORAL_UNSAT and failed execution; these are design categories, NOT declarations of existing runtime enums.
