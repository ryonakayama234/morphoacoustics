# SMC-7 Gate A0 — METROLOGY: what to measure, how, and what it cannot prove

**Issue #229 | prospective measurement science, no data collected.** Do not convert design metrics into observed success or tune thresholds after looking at outcomes.

## Four independent evidence layers

| Layer | Measurand / instrument | Scientific claim ceiling |
| --- | --- | --- |
| L0 formal/informatics | Unicode/spans, deterministic candidate/policy identity, TaskLexicon contracts, exact STN references and refusal behavior | software/formal consistency only |
| L1 linguistic/phonetic | independent annotated Japanese reading(s), utterance boundaries, variant/context labels, corpus + annotation methodology | pronunciation-hypothesis accuracy under a named dataset; **not** true articulatory motion |
| L2 Core body execution | named task observation h_M(x), SI unit, prepared organ graph, actual states/constraints/capability | model-specific physical task attainment only; NOT measured in SMC-7 |
| L3 acoustic/perceptual | generated/captured waveform, matched receiver, blinded intelligibility/voice-likeness and creative usability | requires later authorized audio gate; NOT measured in A0 |

SMC-6's mathematical earliest/latest bounds are **not statistical confidence intervals**; proposed G2P confidence estimates (if any) are **not** exact timing bounds.

## Proposed measurands and falsification references

| ID | Quantity / denominator | Reference / diagnostic |
| --- | --- | --- |
| L01 | source alignment validity: all projected indices refer exactly to original Unicode-codepoint intervals; offending spans count | independent Unicode fixture and reconstruction |
| L02 | source coverage: proportion of designated pronounceable source intervals accounted for in a *complete* path; separately count punctuation/silent/unknown | double-annotated interval inventory, distinguish silent vs dropped |
| L03 | candidate-set recall @k: fraction of reference utterances for which at least one of <=k offered **complete paths** belongs to acceptable-gold reading set | held-out multi-reference corpus; document k and any clipping |
| L04 | candidate burden: mean/median/p95 distinct complete paths proposed per utterance and proportion hitting limit; guard against 'include every imaginable reading' | fixed same test cases and budget |
| L05 | selected-path exact-match accuracy: among valid gold-known *selected* utterances, fraction with selected path in acceptable-gold set; also unconditional accuracy over all gold-known cases | independent manual annotations; separate selection coverage |
| L06 | kana character error rate (CER): sum edit distance to best applicable acceptable reference / sum gold chars, conditional on selected path, with explicit tokenization; phone-error rate is **separate** | held-out reference, not a synthesized phonetic truth |
| L07 | abstention and selective error: accepted count / eligible count (coverage), error rate among accepted, error and abstention by OOV/homograph/unknown groups | report risk-coverage curve, avoid impressive accuracy by rejecting everything |
| L08 | ambiguity detection: false-unique rate among reference-ambiguous cases; wrongly flagged ambiguous among reference-unambiguous cases | context-specific gold annotations (not dictionary polysemy alone) |
| L09 | reference/evidence completeness: count missing corpus/provider version, source alignment, license, selection actor and mapping revision; target ZERO missing for accepted receipts | receipt field audit |
| L10 | SMC5 admissible handoff: valid projected selected paths that actually pass current canonical wire/finite lexicon; refusals by reason, denominator = all requested projections | canonical parse + existing SMC5 exact status, NOT reading accuracy |
| L11 | SMC3/5 identity invariants: no invented/duplicated shared Task IDs; plan/candidate digests and original source unchanged for equivalent direct selected-path baseline | independent structural checker and existing SMC5 oracles |
| L12 | SMC6 timing replay: SAT/UNSAT and exact event times/constraints in COMPATIBILITY lane match direct legacy request; original digest stable | independent rational reference, no 'natural score' claim |
| L13 | determinism/provenance: identical exact input+dependency versions+declared seed/policy yield byte-identical receipts; semantically changed selected path yields revised identity | two-process rerun, ordered-source sensitivity, unordered fields invariance only where specified |
| L14 | boundedness: candidate explosion, invalid UTF-8, deep input, large contexts, timeout/resource exhaustion yield explicit refusal with no partial motor plan | negative fixtures; pre-frozen caps in separate Gate A |
| L15 | no ungrounded bodily claim: count SMC output fields claiming organ/area/force/muscle/audio or asserting body capability; target ZERO | schema and side-effect audits; physical mapping count stays separate |
| L16 | annotation uncertainty: disagreement among independent annotators and multiple legitimate gold paths by pronunciation context; stratified disagreement/uncertain cases | recorded annotation protocol before evaluation, not artificial ± ranges |

For reference set G_i and top-k proposed complete candidate paths C_i, candidate recall@k = (sum_i 1[G_i intersection C_i ≠ empty]) / N_gold. Burden B = (sum_i |C_i|)/N_gold. Coverage = N_selected_or_autoaccepted/N_eligible; selective error = N_wrong_selected/N_selected (undefined if zero accepted). These are distinct from edit distance and phoneme correctness. **Report all together.** One path correctly selected does not establish any TaskDefinition as a human physical movement.

## Experiment design and controls

- Sample *entire utterance paths*, not isolated kanji tokens alone. Define gold acceptance sets for readings that depend on context, dialect, orthographic conventions and annotation uncertainty.
- Freeze a hand-reviewed held-out evaluation set (or a licensed, reproducibly subsetted published dataset) before model selection; stratify unambiguous, heteronym, proper-name/OOV, punctuation, numeral, mixed script and accent/phonetic-process-dependent cases; publish stratum counts, not pretend representativeness.
- Keep synthetic adversarial fixtures **separate** from linguistic validity tests. Perfect synthetic invariants do not imply empirical Japanese accuracy.
- Independent adjudicators resolve legitimate alternatives blind to provider prediction; retain disagreements. Avoid train/test source overlap and record dataset license. Citation to a corpus is not permission to redistribute its text.
- Baselines: (A) explicit manually supplied path = software preservation oracle; (B) one pinned deterministic G2P/dictionary proposal; (C) optionally bounded multi-candidate front-end; (D) oracle reference path for downstream *feasibility diagnosis only*, not a deployable predictor. Always use same corpus and budgets.
- Time coordinate in SMC5/6 is exact Fraction seconds and Task ONSET/OFFSET means symbolic interval, **not measured acoustic gesture onset**. No L2/L3 claim by extrapolation.

## Uncertainty and threshold discipline

Exact equality/identity/negative controls: no failures permissible in preregistered fixtures. On linguistic quality, record all denominators, per-stratum results, reference disagreements and sampling uncertainty if statistically justified (e.g., preplanned bootstrap clustered by source text/document). No invented accuracy threshold or p-value at A0. **Before frozen Gate A**, choose dataset, sample size, candidate cap k, source normalization policy, quality acceptance thresholds, false-unique/false-accept budget, and decision rule; register before code and hold-out inspection. Never select a new threshold after seeing passing/failing outputs.

## Traceability

Each measurement record: id, claim layer, variable definition and unit, corpus/fixture ID and revision/license, original source digest, candidate/selected-path identity, provider/compiler/lexicon revision, source SHA, oracle/annotator identity, raw observations, denominator, uncertainty method, analysis code version, outcome, and known limitations. Appendix RESULTS is append-only after future actual execution.

## References
- Japanese heteronym pronunciation-annotated corpora: https://aclanthology.org/2022.lrec-1.770/
- Open JTalk official: https://open-jtalk.sourceforge.net/ ; pyopenjtalk G2P provider API: https://github.com/r9y9/pyopenjtalk
- 2026 Japanese G2P benchmarking example (external results, not project evidence): https://arxiv.org/abs/2606.22009
- SMC6 formal measures: SMC6_A0_METROLOGY.md. Core physical semantics STOP: https://github.com/ryonakayama234/morphoacoustics/pull/226 .
