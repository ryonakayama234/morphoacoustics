# SMC-7 C1: DECISIONS — 実装前技術選定・採用境界
2026-10-30 JST | DESIGN RECOMMENDATION FINALIZED / CREATOR SIGN-OFF PENDING.
Documentation only: NOT C1 implementation, heldout preregistration freeze, new data acquisition, linguistic success, public API, Core or Studio change. Original 2026-10-29 H1-H6 method/cohorts/thresholds remain authoritative.

## D01. Chosen capability
C1 shall study **context-aware ranking and bounded complete Japanese katakana reading proposals**, not body movement or waveform synthesis. Its deliverable is a creator-selectable, attributable pronunciation hypothesis and a properly falsified linguistic-science claim. Do not market as free Japanese TTS. Existing SMC4-6 remain symbolic/temporal research, not human pronunciation or biomechanics.

## D02. Technology: hybrid finite alternatives + context ranker
Recommended baseline B0: actual pinned private pyopenjtalk 0.4.1, with already audited dictionary-byte identity 88167f04755fe6f0973f5be05bf839aad53d600e190d7068b29d7af15c594dbd (observed C0; revalidate C1 environment). B0 is NOT context-free and its output is TEXT ONLY with no authenticated source spans.

Recommended candidate producer: deterministically bounded alternatives from a separately licensed/versioned Japanese reading lexicon, stable document/orthography family inventory, and optional provenance-attributed proposals; all candidate utterances must pass syntax/source checks and share complete-path consistency. Do not use heldout gold, public test answer keys or a full-context model's already-preferred answers to prepare the FIXED-POOL RANKING comparison. Target reading alternative membership should be independent of target-external context for a controlled family-level comparison. Outside-target reading hypotheses may require a provisional text-only front end; explicitly measure leakage and do NOT pass these as verified source alignment.

Recommended C: a reproducibly pinned, licensed, Japanese-capable *local open-weight* text ranking model, constrained to select/order members of a candidate pool; it is not trained on the 880 test. Model name/weight/tokenizer/quantization/prompt/decoding will be selected on the separately licensed **120-case pilot only** using predeclared feasibility, Japanese language capability, runtime resources, reproducibility and rights, then locked BEFORE heldout. A model checkpoint is not pre-approved without checking these facts. If no reproducible qualified model is available => MORE_DATA_MODEL / REVISE, NOT a cloud endpoint silently substituted.
Recommended B1 and C-mask: exactly the same candidate pool as C, frozen candidate-ID/member permutation, target reading alternatives presented identically to each ranker. C-mask must conceal all target-external context, INCLUDING information embedded in candidate descriptions, metadata and ordered IDs; the evaluator may recover full paths after ranking. Unmasked C alone receives permitted external sentence context. This is essential to rule out an information leak through the pool or candidate string itself.
A separate full-pipeline C end-to-end discovery report may use context, but must be labeled as proposal-coverage evidence, NOT the same-pool causal ranking experiment.

## D03. Alternatives assessed
- Pure rule/dictionary-only: excellent reproducible baseline and pool source; limited semantic disambiguation under free text, not enough for target contextual claim.
- Smaller supervised heteronym classifier (Japanese BERT/encoder): academically plausible with licensed training labels, but **880 is heldout and 120 is pilot**, not a legitimate model-training corpus. Defer until independent train split exists.
- Cloud LLM as single truth: availability/drift/privacy and training contamination uncertainty; only separately declared exploratory comparator, not the reference C.
- Unconstrained end-to-end generative LLM outputs: can invent candidates/spans, hide proposal explosion, bypass explicit author selection; reject as trusted pipeline.
- Automatic text→gesture/audio: violates existing SMC/physical trust boundaries; defer to independent semantics, body and listening gates.

## D04. Causal/linguistic claim discipline
The observed real B0 output for 人気のない場所 is ニンキノナイバショ; without disambiguating context it is not established wrong. 人の気配 (ヒトケ) and 評判 (ニンキ) are possible senses in different contexts. Allow multiple independently adjudicated acceptable readings. Same-pool context claims require independent candidate source and target-only masked views. Never treat successful string matching, dictionary fingerprint, or text-only benchmark as sound quality or motor-gesture validation.

## D05. Gate order
1. Corpus accession: reconcile 39 C0 internal-format flags as a **separate** publisher-neutral audit (this audit must not masquerade as a primary 880-corpus prerequisite if Joyo is not part of the study); independently acquire licensed text/NOTICE, two blind annotators plus third adjudicator, full-utterance multi-gold 120 pilot and 880 test with split firewall, document/family cluster IDs. If missing => MORE_DATA.
2. Pilot and freeze: preselect finite model/lexicon feasible alternatives; verify context masks, pool independence, normalization and exact provider dependencies; freeze source/dataset/gold/model/tokenizer/prompt/seed/budgets before any holdout metrics. If requirements cannot be pinned => STOP/HOLD.
3. Research implementation: standalone C1 Draft stacked on C0 accepted source (no rewrite), registered protocol then actual test-only RED, code, exact-Python-matrix CI, strict mypy, root/SV1 regressions and independent code/security review. No Studio/Core/SMC5/6 modifications.
4. Gate C science: only after complete accession, one registered 880 run against B0/B1/C-mask/C, family-cluster confidence bounds, candidate burden and all-case refusals. Independent linguistic audit.
5. Decide: GO_LIMITED_L1_READING only on ALL applicable H1–H6 gates and independently evidenced claims; otherwise REVISE/MORE_DATA/STOP. Preserve all failed results. Accepted code+model+dataset+protocol become a FROZEN_REFERENCE_BASELINE (scope LIMITED), successors EXPERIMENTAL_SUCCESSOR. Public STABLE_API, main merge, Core physical and Studio audio require separate authorization.

## D06. Hard holds, failure semantics
Hard STOP if any unselected proposal reaches a trusted SMC task; if B0 kana is falsely assigned authenticated text offsets; if a gold reference is used to generate answers; if unrelated code modifies the old canonical SMC4/5/6 semantics; if rights, model identity or prompt drift are unverifiable; or if >3 path admission gets silently clipped. Gold missing => MORE_DATA, genuine frozen-hypothesis failure => REVISE, dangerous trust boundary violation => STOP. Scientific result and software CI are separate verdicts. Resource/latency and corpus representativeness are measured, not post-hoc success stories.

## D07. Documentation and project scope
Four linked, versioned documents (SYSTEM, DATA, EXPERIMENT, DECISIONS) should be updated together with later code and append-only RESULT records with exact Git SHA. This design branch/PR is stacked on unmerged C0 Draft #246; do not make it Ready or merge into C0/main without creator consent and independent review. Studio V2 Character/Motion/Scene design was accepted but its implementation is held. Core Foundation #199 and vocal-fold physics are separately advancing; only the future versioned service contract may connect them. This PR contains no physics or UI code.

## Final creative value
A writer can ultimately provide an utterance and inspect a small set of **grounded, complete reading possibilities** with explicit uncertainty and selection. The same selected language plan can later compile to reusable body-independent motor goals; only the Core body decides real physical realization and audible outcome. C1 verifies the **linguistic input layer**, not a claim that a character can already speak.
