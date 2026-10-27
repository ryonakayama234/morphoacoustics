# SMC-7 Gate A0 — DATA and traceability (conceptual, NOT public JSON schema)

**Issue #229 | DESIGN_ONLY / PROPOSAL, no migration, not a MotorScore asset/ABI.** Previous exact SMC4/5/6 schemas and hashes remain authoritative for their own code and must NOT be silently expanded.

## Distinct objects / source of truth

~~~mermaid
erDiagram
  SCRIPT_REVISION ||--o{ SOURCE_INTERVAL : anchors
  SCRIPT_REVISION ||--o{ PRONUNCIATION_PATH : proposes
  PRONUNCIATION_PATH ||--|{ PRONUNCIATION_UNIT_CANDIDATE : orders
  SOURCE_INTERVAL ||--o{ PRONUNCIATION_UNIT_CANDIDATE : traces
  EVIDENCE_RECORD ||--o{ PRONUNCIATION_UNIT_CANDIDATE : supports
  PRONUNCIATION_PATH ||--o| SELECTED_PATH : may_select
  SELECTED_PATH ||--o| SMC4_CANONICAL_REQUEST : projects_conditionally
  SMC4_CANONICAL_REQUEST ||--o| SMC5_COMPILE_RESULT : authenticates
  SMC5_COMPILE_RESULT ||--o| SMC6_TEMPORAL_ANALYSIS : analyzes
  SELECTED_PATH ||--|| SMC7_RESEARCH_RECEIPT : records
~~~

1. **ScriptRevision**: original Unicode text, immutable UTF-8 submission digest, script revision ID, input locale, exact original character length; no hidden NFKC rewrite. Use explicit half-open Python-Unicode-codepoint indices [start,end) (NOT UTF-8 byte offsets or grapheme cluster counts), plus an optional explicit codepoint→byte mapping if a consumer needs bytes. Invalid Unicode scalar sequences/refused surrogates must be handled at the ingress boundary. Preserve exact source.
2. **SourceInterval**: source revision and [start,end) with annotation role: pronounceable unit, punctuation/boundary, intentionally silent span, or unresolved span. Punctuation is not a fabricated phoneme.
3. **PronunciationPath**: explicit stable path ID, ordered candidate units and occurrence IDs, language/profile/dialect constraints, boundary information, source digest, candidate generation policy and deterministic limit. A path is a *joint sentence-level hypothesis*, not a Cartesian product automatically formed from independently plausible word readings.
4. **PronunciationUnitCandidate**: one or more source intervals as allowed by a separately specified alignment convention, kana-reading representation and (only when evidenced) phonological segments. Keep surface reading, phoneme hypothesis, accent, devoicing and motor task **different tiers**; do NOT treat kana as exact IPA or anatomical commands. Define complete-path coverage vs unresolved span explicitly.
5. **EvidenceRecord**: corpus/dictionary/provider ID, version/commit/digest, language and applicability, provenance method, reference license/restrictions, citation, and status OBSERVED_ANNOTATION | PROVIDER_PROPOSAL | MANUAL_SELECTION | SYNTHETIC_FIXTURE | UNVERIFIED. A provider score is not a calibrated probability without held-out calibration evidence.
6. **SelectedPath**: path ID, selection actor/policy (human, external reference, pinned algorithm), declared context, status and point-in-time decision. Unselected competitors remain recoverable as evidence, but **cannot be mixed** into one SMC5 plan.
7. **ProjectionReceipt** (research only): source/path IDs, projector revision, SMC4 canonical request identity (only on accepted schema), selected unit-to-source alignment, SMC5 result and SMC6 scenario hashes when legitimately available, refusal code/stage, resource-budget trace. No fabricated candidate_digest for a failed mapping.
8. **MotorProgramCandidate** is a conceptual reference to authenticated SMC5 symbolic plan + TaskGoals + SMC6 analysis only. No new public data type, absolute actuator times, physical motion, WAV or character body.

## Identity/immutability and normalization rules

- Exact source UTF-8 bytes and Unicode codepoints are preserved in all cases; any normalization/transliteration is a separate, explicitly reversible or source-aligned derived view, with algorithm revision. NFC vs NFD, long vowels, digits, emojis, ruby, English tokens, punctuation and CRLF require explicit policy or refusal. Never conflate visually similar normalized strings when computing source-revision digest.
- Source annotation spans refer to the *original* unchanged revision. If text changes, old selections need explicit revalidation; offsets/identities are not blindly inherited.
- Candidate-path digest must bind: source identity, ordered unit IDs/symbols and spans, context/profile, provider/dictionary revision, selection policy and evidence reference, using a prospective domain-separated canonical digest. Hash identity is reproducibility, **not validity**.
- If a provider returns a wrong/missing/non-contiguous mapping, fail or mark unresolved with true source spans; never silently guess an offset from concatenated kana. Non-speech intervals and pronunciation-unit spans require an exact disjoint coverage policy to be decided before Gate A freeze.
- Time units remain inherited exact rational seconds in SMC5/6; do not confuse a text span with onset timing. SMC5 TaskGoal numeric goal ranges are NOT time ranges.
- A TaskDefinition must have a verified semantic binding to become a bodily goal. Matching synthetic labels such as tract/open_closed or source/active_inactive do not confer physical target units/actuators.

## Stage-labelled outcome proposal

| Stage | Provisional code | Required behavior |
| --- | --- | --- |
| INPUT | INVALID_SOURCE / UNSUPPORTED_SCRIPT | reject malformed source or unsupported dialect/syntax; record diagnostic |
| PROPOSAL | UNKNOWN_READING / CANDIDATE_LIMIT / AMBIGUOUS_READING | retain alternatives or abstain; no implicit selection |
| ALIGNMENT | ALIGNMENT_INVALID / INCOMPLETE_PATH | zero plans; preserve source/proposal evidence |
| SELECTION | SELECTION_REQUIRED / UNVERIFIED_SELECTION | no hidden best-effort path |
| PROJECTION | UNSUPPORTED_WIRE / UNMAPPED_TASK / INSUFFICIENT_CONTEXT | no SMC candidate digest; do not change SMC4-5 grammar |
| TEMPORAL | TEMPORAL_UNSAT / UNSUPPORTED_POLICY | no valid scheduled candidate; preserve original timing receipt |
| PHYSICAL (future) | UNMAPPED_SEMANTICS / UNSUPPORTED / INFEASIBLE | owned by Core adapter, not falsely emitted as SMC text-processing success |

These names are *conceptual design names*, not assertions about the exact existing code enums. Projectors must use actual legacy refusal codes; any translation layer must be versioned and bijective where required.

## Asset boundary

Long-term goal is a versioned, portable task/gesture command score. A0 does not define one. At most preserve a provenance-rich **research candidate envelope**. A stable MotorScore schema, Studio import/export and user-editable direction require separately validated semantic meaning, versioned compatibility policy and creator approval.
