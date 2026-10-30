# SMC-7 C1: SYSTEM — 実装前アーキテクチャ決定稿（提案）
2026-10-30 JST | Parent #247, #242 | Data #244 | C0 #245 / Draft #246
Status: DESIGN_COMPLETE / CREATOR_APPROVAL_PENDING / NOT_PREREG_FROZEN / NO_IMPLEMENTATION / NO_MAIN_MERGE.

## Mission and scope
Enable 0–3 complete, ranked, independently attributable Japanese katakana readings of a creator script. Proposals never automatically become a selected motor plan. Preserve separate scientific claims: L1a Japanese reading correctness, L1b exact original-text alignment, L0 authenticated symbolic plan, L2 bodily realization, L3 acoustic/perceptual quality. Only L1a is experimentally evaluated in C1; L1b is a separate necessary safety gate.

## Architecture (prospective; C1 predictor not yet built)
~~~mermaid
flowchart TD
  ST["Studio future Motion: Script + Direction"] -. "separately approved API later" .-> IN["Exact source revision / UTF-8 / context ingress"]
  IN --> B0["B0: real pinned private OpenJTalk, TEXT ONLY"]
  IN --> POOL["Finite auditable alternatives / complete path pool"]
  POOL --> P["Pool receipt P(x): no gold, bounded, immutable"]
  P --> B1["B1: context-blind ranker"]
  P --> CM["C-mask: target-external context masked"]
  P --> C["C: full-context ranker"]
  B0 --> EVA["Independent reading evaluator: 880 gold, no motor"]
  B1 --> EVA
  CM --> EVA
  C --> V["Existing L1 proposal / evidence envelope"]
  V --> EVA
  V --> SEL{"Explicit creator selection AND independently verified source spans?"}
  SEL -->|No| HOLD["ABSTAIN / PROPOSAL ONLY / ALIGNMENT UNVERIFIED"]
  SEL -->|Yes| L0["Existing L0 canonical selected-path ingress"]
  L0 --> S56["SMC5 TaskLexicon synthetic plan + SMC6 COMPATIBILITY"]
  S56 -. "future semantic/capability gate" .-> CORE["Core: physical body / organs / acoustics"]
  CORE -. "future creator sound gate" .-> TAKE["Studio immutable Take"]
  IN --> RECEIPT["Attribution / evidence / failure records"]
  P --> RECEIPT
  C --> RECEIPT
  S56 --> RECEIPT
~~~

## Scientific isolation and anti-leak architecture
B0 is NOT context-free: OpenJTalk may use sentence context. For a ranking-only context effect, construct candidate pool P(x) once without reference labels or a full-context ranking model, then pass exactly identical pool membership to B1, C-mask, C. Context-conditioned discovery may be explored separately and explicitly as an end-to-end generator effect. A pool secretly constructed from C preferred predictions cannot support a clean context-effect claim. Report same-pool ablation and candidate-pool ceiling separately.

B0 returns a reading string; it does NOT independently authenticate [start,end) Unicode original source positions. Valid text-only predictions may be scored in L1a without being eligible for a selected motor plan. Source alignment for L0 is an independent verifier responsibility, not a guessed reverse alignment from kana. Unsupported punctuation/long marks may be eligible for linguistic measurement but unsupported for L0; report distinct denominators rather than silently dropping them.

## Authority boundaries
SMC7 C1: proposals, linguistic evaluation, provenance, explicit selection, refusal. SMC5/6: inherited bounded synthetic Task semantics and exact rational temporal constraints; compatible replay only, never automatic lexical inventing. Core: organ graph, material, physical feasibility, actual acoustics. Studio: creator choice, Motion workflow, playback and immutable Takes. Current Studio Workspace V2 is design accepted but UI integration is on hold; no panel or implementation writes here.

## Negative controls and refusal
Counterfactual swapped contexts, masked contexts, reversed candidate order, unknown or ambiguous text, false source offsets, stale source/context/model/dictionary, unlicensed corpus, selection absent, proposal >3, unsupported input and temporal UNSAT. All failures have stage-specific receipts and NO implicit selected plan/audio.

## Baseline and references
Inherit C0 reviewed code-bearing SHA 5087bd5775a148655188df9918d6faaff6a8ea4a and Draft #246 head at design inception 8fb9e5ef4c9ac907148d698142e99eb672c5990b. C0: pyopenjtalk 0.4.1 observed; 17/18 checks with separate Joyo reconciliation failure; not a linguistic accuracy claim.
- https://github.com/ryonakayama234/morphoacoustics/issues/247
- https://github.com/ryonakayama234/morphoacoustics/issues/244
- packages/speech-motor-compiler/docs/SMC7_L1R_GATE_A_PROTOCOL.md
- https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md
- https://github.com/ryonakayama234/morphoacoustics/issues/199
