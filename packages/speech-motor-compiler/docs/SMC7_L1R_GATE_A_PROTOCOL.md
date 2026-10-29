# SMC-7 L1-R — method preregistration and evidence-boundary protocol

**2026-10-29 JST | Issue #242 | METHOD_FROZEN_BEFORE_TESTS | LINGUISTIC_DATA_GATE_NOT_FROZEN | RESEARCH_ONLY | NO_MAIN_MERGE**

## 0. Source and scope
- Base research branch `research/smc7-l0-trust-repair-20261028` at `4e6b6530247700d70e3ad319e1d6bd0d20e8b962`; L0 reviewed, accepted code-bearing SHA `5b970ebb1ddfbe08313f72116c39a5875148a78f` (18/18 checks, independent software review no findings). Parent Draft #236 remains unmerged.
- Prior A0 SYSTEM/DATA/METROLOGY/EXPERIMENT, issue #229 and P2 design amendment 01 remain historical documents. L0 is not evidence of Japanese pronunciation truth.
- This first **methodological** freeze precedes L1 code/tests. The proposed 880 utterances, gold readings, provider binaries/dictionary hashes, legal permissions and annotators have **not been acquired or frozen**. No Gate C run, H1-H4 acceptance, or `GO_LIMITED_L1_READING` until a separate timestamped accession freeze before any held-out prediction.
- Keep SMC-4/5/6 source, `__init__`, Core, Studio, public API, organ physics, waveform and main branch untouched. SMC5 task semantics are `SYNTHETIC_ONLY`; SMC6 `COMPATIBILITY` witnesses do not assert natural timing.

## 1. Scientific estimand and competing explanations
For standard contemporary Japanese reading *written as fullwidth katakana* (not IPA, pitch accent, devoicing, timing, physics or voice), measure whether **same orthography in different contexts** yields better correct-reading selection in a held-out test under an upper bound of three complete, ordered utterance paths.

- H1 primary: target heteronym reading top1 accuracy C versus version-pinned single G2P B0, paired delta >=+0.05 AND a word-family cluster bootstrap 95% percentile lower bound >0. Context-masked C ablation delta >=+0.03 (secondary). NULL: context provides no benefit, gains derive solely from large lexicon/frequency memorization.
- H2 whole-utterance candidate recall@3 C minus B0 top1 exact path accuracy >=+0.08 AND cluster-bootstrap lower bound >0; mean distinct complete paths <=2.0; empirical p95 <=3; silent truncation count exactly 0. NULL: enumerate many implausible readings.
- H3 80 context-underdetermined/legitimate alternatives: unsupported UNIQUE_CONFIRMED <=5%. A ranked top1 or singleton **is not** UNIQUE_CONFIRMED; if there is no unique claim feature, call this an invariant not evidence of disambiguation.
- H4 ordinary 240 utterances: whole-path top1 difference C minus B0 >=-0.02 and cluster-bootstrap 95% lower bound >=-0.05; noninferiority guard, not a generalization claim.
- H5 boundary: source Unicode spans all non-silent positions covered exactly once per complete path, no unselected path compiles, no absent evidence accepted, no fresh task semantics; direct and projected SMC5/6 results EXACT equality at *same explicitly pinned* scenario. For UNSAT, maintain original authenticated SMC5 receipt/digest, no SMC6 feasible witness. All cases must pass.
- H6 reproducibility: exact input/context/profile/provider/dictionary/policy/selected path version -> same L1 output in independent processes; semantically changed L1 evidence alters its identity even if inherited SMC5 request is unchanged. Digest is identity/integrity only, never external authorization or linguistic correctness.

## 2. Reference corpus/hold-out plan (not obtained yet)
| Stratum | N | Definition |
| --- | ---: | --- |
| C heteronyms | 400 | 100 distinct orthographic families × four contrasting contexts each; at least two different readings per family |
| O ordinary | 240 | unambiguous utterances spanning scripts/punctuation/genres |
| U names/OOV | 160 | explicitly separate resolvable and unknowable; no guessing counts as safe |
| A underdetermined | 80 | real multiple-gold or insufficient-context cases; false unique |
| Held-out total | 880 | never feed to rules/model tuning/dictionary additions |
| Pilot | 120 | separate text and orthography families for implementation/annotation decisions |

Two native-competent reading annotators must independently annotate original utterance with context, full katakana reference, source intervals, profile, acceptable variants, unknown status **blinded to candidate outputs**. A third independent adjudicator resolves disagreements, without hiding unresolved readings. Retain raw disagreements and rates. If >5% of C cannot be adjudicated, `MORE_DATA_INVALID_GOLD`. Partition by document, orthographic family and context pairs; neither pilot nor provider prompts/dictionaries may include held-out answers. Identify license/terms for every source and provider and distinguish evaluation permission from redistribution permission; published corpus citation is not a license.

**Accession freeze required before Gate C:** exact source/corpus manifest + immutable content digests, source licenses/NOTICE, annotation manual, annotator agreement, gold reference and acceptable-variant policy, pilot/hold-out partition hash, leakage audit, B0/B1/C/C-mask model/dictionary/provider version and seeds, evaluation code SHA. At accession, explicitly state that the held-out readings were not inspected for tuning. Without all these do not use a `GO` verdict.

## 3. Arms, variables, analysis
- B0 single deterministic `pyopenjtalk==0.4.1` candidate baseline, **only if actually installed with exact dictionary SHA and compatible license**. Raw kana string alone has no safe source-span provenance; G2P text metric comparison is not a motor-plan admission.
- B1 bounded same candidate pool as C but context-agnostic ranking; C is context-conditioned bounded generator/ranker; C-mask hides *context outside target span* while preserving the span. Do not let candidate pool or budget differences masquerade as context effects.
- Gold oracle is solely for SMC5/6 invariance with **existing valid synthetic** canonical request/lexicon. Human chooser is optional secondary experiment and **must be blind** to gold.
- Primary denominator: C 400 adjudicable context pairs, with any excluded cases separately accounted; whole-path exact match is not target-token match.
- `Recall@k = mean(1[distinct complete ranked C_i[:k] intersects acceptable complete G_i])` for k=1,2,3. `burden = mean(|C_i|)` over **all eligible inputs**, including zero outputs. Report median/p95, unknown and budget-limit fractions.
- `coverage = n_selected/n_eligible`; `selective_risk = n_wrong_selected/n_selected` (undefined when no selections); report paired risk-coverage, false-unique on A, target top1, contrast-pair both-correct, whole-path top1, corpus-weighted katakana CER (secondary).
- Paired cluster bootstrap: 10,000 draws, seed **20261029**, sample 100 orthography families with replacement, carry their four contexts, percentile [2.5,97.5]; H1/H2 joint gate, no post-hoc threshold optimization. O is clustered by document/orthography units as preregistered at accession and method must be declared before held-out evaluation. Show raw denominators and uncertain references; no false precision.
- Performance/resource report is independent of linguistic accuracy and uses pinned local machine/runtime and budgets. B0 may be unavailable in CI; never silently substitute another provider.

## 4. Stage types, receipts, strict trust
This Gate B software slice is an isolated L1 *proposal-evidence wrapper* around existing L0, not an unlicensed/pretend G2P implementation:
1. `ContextEnvelope`: exact context bytes, source revision, ja-JP profile, bounded input; domain-separated context identity.
2. `EvidenceManifest`: exact provider/version/dictionary/content digest/license/policy and context identity; metadata are **claims**, not truth. Reject absent/malformed version/opaque object/hostile equality and budget exceed before expensive work.
3. `L1CandidateSet`: 0..3 complete `ReadingPath` objects accepted only after full independent revalidation through **existing** `make_proposal` over original text/revision, plus L1 identity binding context, ordered candidates, manifest and policy. Do not inject target reading into generated candidates. 0 paths -> abstain, not selected or compilable; >3 -> `CANDIDATE_LIMIT` refusal (no silent clipping).
4. `SelectionReceipt`: explicit selection actor and in-set path identity; source/context/manifest and candidate-set ID bound at moment of selection. Unselected proposal returns no motor plan. No automatic top1 promotion. Selection consistency rechecked on every handoff; changed source/context/provider/selection invalidates L1 receipt.
5. Projection (later if needed) uses exactly unchanged `compile_selected` with externally provided authentic SMC4 wire and explicit SMC6 `COMPATIBILITY` scenario; **does not construct a new synthetic lexicon from Japanese symbols**, infer schedule or allow `RESEARCH_OVERRIDE`.
6. No field named or implying F0, SPL, formant, actual gesture motor, body displacement, feasibility, WAV, voice quality or Take. Receipts differentiate `L1_PROPOSAL`, `L1_REJECTED`, `L1_SELECTED`; no exposed stable MotorScore ABI.

Exact original Unicode codepoint intervals [start,end), no covert NFKC/NFC conversion. L0 silent set is explicitly space/newline/tab/、。！？… . For other punctuation, mixed Latin, surrogate, long mark, emoji or unsupported source, refuse until a **new preregistered** mapping, rather than fabricate source spans. Max source 256 codepoints / UTF8 2048 bytes and L0 32 units/path are inherited; max candidates here 3; manifest/context fields must themselves be bounded before iteration.

## 5. Gate B software first-slice test-falsifier catalog — freeze before test/source
- T01 valid manually supplied kana path + pinned context and manifest yields L1_PROPOSAL only; never SMC plan, and source revision is intact.
- T02 ranked 2 or 3 complete paths retain order/identity and different candidate-set hash; no Cartesian cross-splicing.
- T03 0 candidates -> explicit abstention and no selection; 4 candidates -> CANDIDATE_LIMIT with no usable candidate.
- T04 wrong context revision/profile/manifest ID/selection actor/path ID -> fail closed and no selected receipt.
- T05 context-only change changes L1 identity, while unchanged SMC5 canonical request is never rewritten.
- T06 incomplete/gapped/overlapped/forged span, silent symbol intrusion, unverified L0 proposal, external `mock.ANY`, custom equality -> reject before selection.
- T07 over-limit original or context strings, invalid Unicode/surrogate, hostile Python types and nested structures -> controlled refusal; length checked before scan.
- T08 no actual G2P inference, accent/phoneme/physical fields; no Core/Studio/file/network side effects; all provider metadata is unverified declaration.
- T09 same input/version yields deterministic output in two independent Python processes; version and dictionary changes change L1 identity.
- T10 existing L0 direct-vs-SMC5/6 compatible selected path replay and UNSAT stage-specific receipt remains unchanged (root/package inherited suite).
- T11 independent evaluator fixture: multiple acceptable complete references, zero candidates, duplicate proposals, target-vs-whole-path contrast; exact numerator/denominator and candidate-burden audit, no gold fed to candidate builder.
- T12 inherited L0 P1 forged ReadingProposal, P2 scan-before-limit and `unittest.mock.ANY` adversarial regressions preserved.
- T13 research package remains dependency-free at runtime; require package pytest Python 3.11/3.12/3.13, strict mypy, full Core/root, bounded SV1, exact-source independent code review. Record actual RED (test-only before module) and actual GREEN, not merely expectation.

All T01-T13 are **software** properties. Passing them never confirms H1-H4, independent linguistic correctness, Core physical semantics or perceptual voice quality.

## 6. Sequencing and outcomes
Method protocol commit -> **test-only RED commit** -> module implementation -> exact-HEAD CI and independent third-party software review -> append-only Results/Decisions. Any actionable review defect gets a new preregistered regression test first. Separate Gate C only after licensed gold/provider accession as defined above. Until then result is `MORE_DATA_L1_LINGUISTIC_CORPUS_AND_PROVIDER`. Explicit `REVISE` when scientific targets fail; `STOP` if unselected text can create a trusted plan or provenance is forged; record all past failures, never rewrite them as passed.

References: #229, #231, #236, #242; SMC7_A0_*; SMC7_GATE_A_PROTOCOL.md; SMC7_GATE_B_DECISIONS.md; SMC5_SYSTEM.md; SMC6_GATE_B_IMPLEMENTATION.md; Core #227; Sato et al. 2022 https://aclanthology.org/2022.lrec-1.770/; pyopenjtalk https://github.com/r9y9/pyopenjtalk .
