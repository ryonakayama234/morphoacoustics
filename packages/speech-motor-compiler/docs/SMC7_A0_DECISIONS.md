# SMC-7 Gate A0 — design decisions, trade-offs, outstanding approval gates

**2026-10-27 | Issue #229 | PROPOSED_DESIGN_ONLY, NOT_PREREG_FROZEN / NO_IMPLEMENTATION / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE.**

## Provisional design decisions (not permanent public API)

| ID | Decision / rationale | Counter-risk and control |
| --- | --- | --- |
| D01 | Treat Script→pronunciation path proposal as a **new upstream stage** of existing SMC5, not a rewrite of existing SMC4-BR wire | independent source revision / selected-path projector, strict legacy schema guard |
| D02 | Whole-utterance pronunciation **paths** are first-class; no cross-mixing word-level alternatives | full-path IDs, explicit selection, bounded lattice |
| D03 | Split kana/reading, phoneme hypotheses, accent/devoicing, functional Task, schedule, physical trajectory and waveform | do not treat katakana output or G2P prediction as anatomical score |
| D04 | PROPOSE_ONLY and EXPLICIT_SELECTED are distinct entry modes; neither a tool nor model is a ground-truth oracle | multiple proposals, selection actor/policy provenance, no silent unique guess |
| D05 | Align every candidate to *original* Unicode-codepoint source spans; original bytes and text immutable | derived normalization only with rule, explicit unknown/punctuation treatment |
| D06 | Preserve SMC5 synthetic TaskGoal/scalar eligibility; SMC6 COMPATIBILITY exact event replay, keeping original timings and digests | no manufactured biological goal/phase, override by separate later experiment only |
| D07 | Physically meaningful task calibration is Core-owned; Exp040 Stage B semantic STOP remains true | synchronize with Core #227, do not equate tract/open_closed with G_area |
| D08 | Measure candidate recall alongside candidate burden, false unique, selective risk, refusals and exact legacy invariants | false wins from unbounded candidate sets or universal abstention blocked |
| D09 | No automatic technology choice: dictionary, Open JTalk, G2P ensembles and optional learned proposals remain alternatives until controlled comparison | record versions, license, data provenance and unseen evaluation |
| D10 | Research acceptance, frozen baseline, stable ABI, Core integration and Studio creative release each require distinct approval evidence | versioned design/experiment receipts, NO_MAIN_MERGE |
| D11 | Documentation lives only in standalone SMC package; no Studio visual edit because ADR layout is frozen | Motion canvas future only after explicit product authorization |

## Open decisions — MUST close before separate frozen Gate A

1. Primary Japanese profile: standard contemporary Japanese only or named dialects; acceptable variant pronunciation sets and treatment of long vowels, devoicing, accent.
2. Exact source-interval annotation and granularity, including punctuation, silent segments, unknown readings, ruby, alternative surface readings and multi-unit mappings.
3. Dataset and license; annotation method, adjudication, train/dev/held-out boundaries and sample-size/power assumptions. Literature corpora do NOT automatically grant redistribution.
4. Max source bytes/codepoints, maximum complete candidate paths k, branching policy, provider runtime cap, deterministic tie-break or refusal on overflow. Match SMC4-BR existing byte limit without presuming arbitrary future requests fit.
5. Which G2P baseline(s) and dictionary versions are legally installable/reproducible in CI; human selection vs pinned algorithm auto-selection; confidence scores default uncalibrated.
6. Quantitative L1 gate thresholds and weighting across homographs, OOV, punctuation and ordinary texts; preregister before held-out evaluation.
7. Exact projector wire mapping and ability to construct eligible SMC5 finite synthetic lexicon fixtures without adding invented Task semantics or retroactively changing previous fixtures.
8. Independent oracle/third-party review identity and gate success/stop decision owner.

## Interfaces and handoff plan

Core #227 defines future physically observable Task target variables, units, admissibility/capability and actual execution independently of language. Once present, a separate semantic-binding gate may connect a named SMC TaskDefinition to a verified Core task; SMC-7 cannot infer this binding from string identity. Studio Motion can eventually show script, competing readings and MotorScore proposal; underlying Studio 3-mode composition and immutable Take / receiver ownership stay frozen. Future audible voice needs Core source/tract/acoustics and creator listening, not fake generated WAV from SMC.

## Next proposed action (requires separate agreement)

Review and amend A0. Only then construct **SMC7_GATE_A_PROTOCOL.md** with frozen exact-parent code SHA, corpus/provenance, expected case table, thresholds and reviewer, commit the protocol before any test or implementation. Any later code path belongs on another stacked research Draft PR; all A0 files remain auditable design history. No merge/publish changes from this Issue itself.

## References
- SMC4 reading vs Task design: SMC4_GATE_A_PROTOCOL.md; SMC5 exact wire mapping: SMC5_GATE_A_PROTOCOL.md; SMC6 temporal science: SMC6_A0_METROLOGY.md.
- Core Stage B STOP: https://github.com/ryonakayama234/morphoacoustics/pull/226 ; Core physical task research https://github.com/ryonakayama234/morphoacoustics/issues/227 .
- Studio frozen ADR: https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md .
- Open JTalk official: https://open-jtalk.sourceforge.net/ ; polyphone corpus https://aclanthology.org/2022.lrec-1.770/ .
