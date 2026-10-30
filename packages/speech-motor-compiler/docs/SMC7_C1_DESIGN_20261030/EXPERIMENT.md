# SMC-7 C1: EXPERIMENT — 計量・反証・対照実験
2026-10-30 JST. DESIGN_COMPLETE / PROTOCOL_AMENDMENT_NOT_FROZEN / NO_HELDOUT_EXECUTION.
This document **does not replace** H1-H6, thresholds, sampling sizes or the 2026-10-29 method freeze in SMC7_L1R_GATE_A_PROTOCOL.md. It makes measurement operators and competing mechanisms explicit before C1 source work.

## Competing hypotheses
H1. C correctly ranks context-appropriate reading more often than actual B0, not merely relying on one appealing example. Null: any apparent improvement is dictionary coverage, priors, contamination, added candidates, annotation mismatch or random fluctuation.
H1b. Holding pool membership exactly constant, full context C improves ranking over B1 and relative context mask C-mask. Null: observed apparent gain follows candidate pool leakage/position bias rather than the ranker using context.
H2. End-to-end C attains useful whole-utterance recall with <=3 complete paths and low creator burden. Null: recall increases trivially with arbitrary alternatives, hidden clipping or refusals excluded from denominator.
H3. In genuine ambiguity, the system refuses to make unsupported unique-certainty claims; abstention/risk must be informative, not rejection of all hard examples.
H4. Ordinary-text correctness does not regress unacceptably.
H5/H6. Exact source, provenance, explicit selection and old compatible symbolic/time results survive adversarial replay. These are software/formal invariants, NOT proof of motor, body, phonation or sound.

## Observable measurements
| ID | Quantity | Independent reference and denominator | Limit |
|---|---|---|---|
| M01 | target heteronym top1 (% and pp delta) | C=400 independent reference target readings, clustered 100 families x4 | H1 |
| M02 | same-pool C versus C-mask / B1 pp | identical pool membership, source and frozen context view, paired C cases | H1b |
| M03 | acceptable complete utterance Recall@1/2/3 | multi-gold independent reference strings, include zero-output failures | H2 |
| M04 | burden: distinct complete paths, mean/median/p95 and cap hit | all eligible, including abstentions and failure status | H2 |
| M05 | unsupported UNIQUE_CONFIRMED and ambiguity detection | A=80 multi-gold/unresolved annotated cases | H3 |
| M06 | ordinary top1 noninferiority, percentage points | O=240 with predeclared family/document clustering | H4 |
| M07 | coverage vs selective error | all eligible versus selected; when no selected predictions, risk is undefined | safety |
| M08 | original span validity and full coverage | independent Unicode/canonical reconstruction oracle | H5 |
| M09 | exact SMC5/6 COMPATIBILITY replay, SAT/UNSAT | same old synthetic wire and independent mathematical reference | H5 |
| M10 | reproducibility, provenance and input-resource budgets | different processes, exact SHA and version swaps, malformed input | H6 |
| M11 | annotation disagreement/adjudication coverage | blinded annotators and raw disagreement, per stratum | reference quality |
| M12 | inference p50/p95 latency, CPU/GPU RAM, failure frequency | pinned hardware/runtime and warm/cold protocol | descriptive |
| M13 | pool oracle ceiling, same-k control and leakage check | heldout reference visible only to post-prediction analyst, never generator | attribution |

Main denominator eligibility, refused cases, unknown cases, excluded cases and reasons must ALL be published. Do not reinterpret a provider error as a correct abstention; do not compute good accuracy by dropping failures. Normalization is a separately versioned exact algorithm, not a silent reconstruction of source text.

## Arms and identifiability
B0: actual pinned pyopenjtalk 0.4.1, private snapshot dictionary, text only, internally sentence-context-capable; baseline is NOT context-free.
B1: frozen candidate pool P(x), no target-external sentence context in ranking.
C-mask: same P(x), target span retained, context outside target syntactically masked by a protocol-frozen rule; masking must not change target content or candidate membership.
C: SAME P(x), full sentence context. Fixed-pool ranking experiment estimates a contextual ranking effect.
C-full discovery: optional separate end-to-end whole-utterance candidate generation arm; membership might use context and is explicitly not interchangeable with the fixed-pool contextual effect. H2 end-to-end comparison must report candidate-discovery gain separately from ranking. The pool must NOT be generated from C's context-conditioned top1 then reused to falsely prove ranking-only context effects.

Counterfactual tests: swap contexts among the same written heteronym, context removal, reversed candidate order, plausible placebo masking, source shift, wrong span, unseen family, synthetic gold injection detection, version mismatch, OOV unresolved, genuinely ambiguous, forced >3 L1 paths, no selection, bad canonical wire and inherited SMC6 UNSAT. Models cannot inspect real heldout gold before prediction.

## Registered existing thresholds — DO NOT RETUNE
- H1: top1 C-B0 >= +5 pp, 95% *clustered* CI lower >0; separately C-C-mask >= +3 pp.
- H2: whole-path C Recall@3 minus B0 whole-path top1 >=+8 pp, 95% clustered CI lower >0; mean candidate count <=2, empirical p95 <=3; no silent clipping.
- H3: unsupported explicit UNIQUE_CONFIRMED <=5% across 80 A cases. If output has no unique-certainty feature, state INVARIANT_ONLY / AMBIGUITY_DISAMBIGUATION_NOT_EVALUATED rather than claiming an empirical success.
- H4: ordinary C-B0 top1 >= -2 pp and 95% lower bound >= -5 pp.
- H5/H6: zero forged selected plans, false alignment, source drift, silent version substitution, incompatible old symbolic replay, and unbounded acceptance.

Compute family-cluster paired bootstrap with 100 families carried intact 4 contexts each, 10,000 replicates seed 20261029 and 2.5/97.5 percentiles; use same resampled clusters for all compared predictions. O clustering must be fixed by document/orthography before the heldout evaluation. A 400-row corpus is NOT 400 independent lexical-family replicates. Show actual eligible denominators and uncertainty; family-level effects and per-case errors separately. H1-H4 are the 2026-10-29 frozen method, not measured findings.

## Execution phases and stop conditions
Gate A data accession: first independently reconcile 39 Joyo internal-format nonadmissions (no silent omission, no scientific blame), and separately secure rights and two-blinded-annotator plus adjudicator whole-path 120 pilot / 880 heldout. Freeze gold policy, copyright NOTICE, split, grouping and leakage audit. If not possible MORE_DATA; synthetic fixtures cannot substitute.
Gate A+ model selection: run pilot-only feasibility of model/lexicon, normalization and context masks; choose exact versioned local model or record MORE_DATA_MODEL. Fix model weights, tokenizer, prompt, decoding, dependency/build, dictionary, time/memory budget, corpus and evaluator SHA before opening heldout.
Gate B: commit preregistration; test-only actual RED, bounded implementation, Python 3.11/3.12/3.13, strict mypy, full root and SV1 regression, independent code/security review. Separate source-alignment certification gate; never assign authenticated spans using text-only B0.
Gate C: ONE frozen heldout evaluation and negative-control audit, preserving every failed sample and reviewer comments; no output-driven changes to model or thresholds. Secondary exploratory diagnosis can follow only in a separately labelled EXPERIMENTAL_SUCCESSOR.
Gate D: GO_LIMITED_L1_READING only with all applicable independent linguistic + safe selection + provenance + CI/review gates; otherwise REVISE, MORE_DATA or STOP. Freeze accepted code/dictionary/model/gold and caveats separately; do not merge or publish stable MotorScore/Studio/physical-quality claims.

## Key falsifiers
If the C-B0 CI includes zero, fail H1 even if a famous phrase reads well. If C-C-mask shows no positive difference on identical pools, do not claim external-context causal improvement (even if end-to-end C gains via pool enlargement). If Recall@3 gains only by offering large alternatives, fail/qualify H2. If independent whole-path gold is unavailable, results are DATA_MISSING not scientifically GO. Matching bytes/green tests are NOT biological pronunciation or listening validation.
