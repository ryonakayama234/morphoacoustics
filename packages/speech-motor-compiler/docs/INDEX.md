# SMC-3 Research Index / decision provenance

**State:** GATE_B_EXPLORATORY_SOFTWARE_PASS / INDEPENDENT_REVIEW_PENDING / RESEARCH_ONLY / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE.

## Navigation
- [SYSTEM.md](SYSTEM.md): architecture, hypotheses, falsifiers and prohibited scope.
- [DATA.md](DATA.md): independent MotorTaskNode, associations and event coupling candidate schema.
- [EXPERIMENTS.md](EXPERIMENTS.md): prospective fixtures, mathematical oracles, software/physical boundaries.
- [README.md](../README.md): import boundary and future Studio route.

## Prior records / historical research
- [SMC-1 #139](https://github.com/ryonakayama234/morphoacoustics/issues/139): exploratory, closed/unmerged.
- [SMC-2 #146](https://github.com/ryonakayama234/morphoacoustics/issues/146): experimental symbolic planning.
- [Draft PR #147](https://github.com/ryonakayama234/morphoacoustics/pull/147): HEAD d12bddbbce2c5571f384217feec98bad3e487771, NOT merged.
- [SMC Gate C #148](https://github.com/ryonakayama234/morphoacoustics/issues/148): preliminary F1–F4 plus Wolfram expressivity witness; third-party review pending.
- [SMC-3 package issue #162](https://github.com/ryonakayama234/morphoacoustics/issues/162): current work, synthetic independent package.
- [Experiment011](https://github.com/ryonakayama234/morphoacoustics/tree/main/experiments/011_gesture_coordination_overlap): bounded physical overlap phenomenon. Its acoustic waveform change does not validate SMC phonetic planning.

## Decision log
- 2026-10-22 Gate A: use a standalone package within Core repository, not a separate repository yet; keep explicit boundary, no root Python package import.
- 2026-10-22 Gate A: select mathematical many-to-many and rational coupling tests before implementing. These are synthetic expressiveness checks, not phonetic data.
- 2026-10-22 Gate A: keep SMC-1/2 original branches unchanged and PR #147 Draft. No third-party reviewer or adoption is claimed.

- 2026-10-22 Gate B code commit: `6b31e77365cf965931cb895286727bf75eaa9b57` after prior Gate A doc commit `4f7bef4a9709c96efaa80d8070a2d8b352d9b1d8`.
- Note: this is self-proposed design and self-authored test suite; no independent acceptance. All claims remain symbolic and synthetic. Cross-body physics, Studio, pronunciation and acoustics excluded.

- 2026-10-22 CI attempt `233bdbac...` exposed strict mypy failure despite 21 pytest passes; source now corrected in a separate follow-up commit, new CI pending. [Failing CI run](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777021246).

## 2026-10-22 verified software Gate B receipt (not research adoption)
Exact source HEAD **`9c9ac9539ae1798ed27ef5cd751562e4b2c9b469`**: GitHub API reported **16/16 completed check runs SUCCESS** (some duplicate push/PR runs), including isolated Python 3.11/3.12/3.13 package import/install + 21 synthetic pytest cases per run + strict package mypy, existing Core root test matrix/typecheck, and bounded SV1 regression. Evidence: [isolated package run](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258873), [root tests](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258910), [SV1](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258867). An earlier failing mypy run is preserved in EXPERIMENTS. Individual OG3 and OG4 were not separately confirmed for this SHA. No independent reviewer, phonetic fixture, body adapter, wav or Studio integration. Disposition: **EXPLORATORY_SOFTWARE_PASS / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**.

## 2026-10-23 Gate C audit tracking
- [Frozen Gate C protocol](GATE_C_PROTOCOL.md): preregistered falsifiers, fixed SHA, deterministic generator seeds, acceptance vs independent-review requirements. Protocol commit `7705ebd752e191a545506c0a2a79d56a40efc6bf` **precedes** all Gate C test code.
- [Adversarial Python tests](../tests/test_gate_c_adversarial.py): 100 synthetic cases, metamorphic invariants, contradiction and malformed-input probes.
- [Wolfram mathematical oracle](../wolfram/gate_c_oracle.wl): independent exact rational witness; no CI execution inferred.
- Audit branch: [research/smc3-gate-c-audit-20261023](https://github.com/ryonakayama234/morphoacoustics/tree/research/smc3-gate-c-audit-20261023), forked from PR #164 HEAD `7d5c405fee1b2469b11bbe6d68b9e0d18e4dab05`.
- Review/state **GATE_C_AUDIT_IN_PROGRESS / ORIGINAL_CANDIDATE_UNCHANGED / INDEPENDENT_HUMAN_REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**. Gate B records above are historical, not Gate C verdicts.

## 2026-10-23 Gate C first failure and targeted revision

- [First failing exact-SHA CI receipt](https://github.com/ryonakayama234/morphoacoustics/pull/169#issuecomment-6367686236): `2a3a038c342150b37323a6c4b24cc846954d1c42`. One runtime malformed source crashes on `len(None)` instead of reporting `INVALID`. Category **BUG**; no timing solver conflict shown.
- [Targeted validator correction](https://github.com/ryonakayama234/morphoacoustics/commit/2de422883e544c1dff5ec12121a1f033a2f3afc5) **subsequent** to the recorded red run; frozen protocol and 100 synthetic test cases unchanged.
- Current stage **REVISE_IN_PROGRESS / POST_FIX_CI_PENDING / HUMAN_REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**. The earlier historical Gate B status must not substitute for this Gate C result.

## 2026-10-23 Gate C — verified exact-source-SHA repair CI

- **Fixed-source commit `2de422883e544c1dff5ec12121a1f033a2f3afc5`** is **16/16 completed SUCCESS**, zero failure/pending in GitHub check-runs API (two push/PR job sets): isolated package Python 3.11, 3.12, 3.13 pytest with 127 synthetic tests per interpreter, package strict mypy, existing root test matrix/typecheck, and bounded SV1. [Python 3.12 job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39973099897/job/120480625178). This is independent of the earlier red SHA `2a3a038c342150b37323a6c4b24cc846954d1c42`.
- Initial red failure **PRESERVED**, caused by `source_text=None` and unguarded `len(None)`; minimal source guard fixed the runtime fail-closed behavior with unchanged frozen test fixtures.
- All verified outcomes above refer to the **code-bearing SHA `2de422883e544c1dff5ec12121a1f033a2f3afc5`**, not automatically to later documentation-only commits. Document-only final branch HEAD checks require their own confirmation. OG3 and OG4 were not run as separate exact-SHA science gates by these package-scoped actions; do not claim them.
- Disposition: **GATE_C_IMPLEMENTER_ORIGIN_SOFTWARE_PASS / HUMAN_INDEPENDENT_REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**. This is not a physical or phonetic validation.

## 2026-10-24 Codex P2 software review extension

- [Codex P2 review/evidence ledger](GATE_C_CODEX_REVIEW.md): exact reviewed implementation SHA, two P2 findings, red CI and controlled fix, AI-vs-human provenance, limited symbolic research gate.
- [Unchanged original Gate C audit tests](../tests/test_gate_c_adversarial.py), plus [post-review regression tests](../tests/test_codex_p2_regression.py). Test-only SHA `08e2a47c8fd34017b6a52cacaef3485779515617` was red (7 Unicode cases + 1 contradiction-permutation case); repair-code SHA `a3f876fcaef3b63e2612807fab288a7e36e7e54a` had **16/16** completed success checks.
- **Current status:** corrected code validated; exact latest amended-head independent Codex re-review pending, final docs HEAD CI separately pending. Scientific/physical claims not adopted; research Draft only; **NO_MAIN_MERGE**.

## 2026-10-24 SMC-4 Gate A — prospective Task semantics and limited lexicon design

This is a **new, design-only, stacked research effort** tracked in [Issue #174](https://github.com/ryonakayama234/morphoacoustics/issues/174), based on SMC-3 research commit `f36bfd5620268f07d5136d101303bcdc0afc0e7b`, not `main`. It does not supersede or re-label the historical Gate B/C records above.

- [SMC4_GATE_A_PROTOCOL.md](SMC4_GATE_A_PROTOCOL.md): goal semantics, TaskDefinition vs TaskTemplate vs MotorTask identity, explicit sharing, versioned pronunciation-to-task mapping, diagnostic/failure and preregistered falsifiers. Original protocol-first (no mapping code) SHA: `cc626535cc32b56f13edbb4349f39e7cf5926e6d`.
- [SMC4_EVIDENCE_REGISTER.md](SMC4_EVIDENCE_REGISTER.md): original literature and project evidence boundaries, synthetic 2-phoneme/3-task graph, measurement and body-realization ownership.
- Gate A has **no implemented new Task lexicon / planner**, no empirically accepted Japanese mapping, no body capability or WAV output. `SMC4_GATE_A_DESIGN_ONLY / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE`. SMC-3 PR #164 remains Draft.

## 2026-10-24 SMC-4 Gate A — separate P2 correction addendum

The **original frozen [SMC4_GATE_A_PROTOCOL.md](SMC4_GATE_A_PROTOCOL.md)** remains unchanged at protocol-first SHA `cc626535cc32b56f13edbb4349f39e7cf5926e6d`.

GitHub Codex's manual **design review of initial docs SHA `44d21d1118ff8994af430e2abd4484030f60f3a2`** found four P2 specification defects: combining alternative pronunciation readings, missing context predicate semantics, incompatible shared goals, and F12's non-falsifiable alternative outcomes. See the separately committed [SMC4_GATE_A_AMENDMENT_01.md](SMC4_GATE_A_AMENDMENT_01.md), origin commit `4686726b2b588e8b2350462750fe095319c43202`, for **normative supersession of only those ambiguous clauses** and explicit F12a/b/c + F16–F22 negative fixtures. No mapping source, physical/audio code or scientific adoption; new exact-SHA CI and Codex re-review required.

## 2026-10-24 SMC-4 Gate A — second review finding and additive/exclusive bundle amendment

Second Codex review of `947805bca9ea4615c1027db0745fab4eaddf8c95` found an additional P2: multiple *required* Task templates for one pronunciation cannot be handled by unique per-unit candidate choice, while unioning all matches would combine mutually exclusive alternatives. Historical frozen protocol and Amendment 01 remain unchanged.

[SMC4_GATE_A_AMENDMENT_02.md](SMC4_GATE_A_AMENDMENT_02.md), initial commit `da0fb2f93d8921effc20c03cb6c90ff0ee89c3c8`, defines versioned `TemplateBundle` of **additive REQUIRED GoalSlots**, **exclusive alternatives within each slot and between bundles**, tri-valued eligibility, explicit priority and no partial plans, with F23–F27 prospective oracles and an unambiguous F01 3-task/4-link witness. A fresh exact-SHA CI and Codex re-review are needed for any `GO_DESIGN_ONLY`; no new executable SMC-4 code.

## 2026-10-24 SMC-4 Gate A — third review scope amendment

Third Codex review of second-amended `36737a0f9fe7537a735586759ccbee23d2c0337a` found another P2: simultaneous per-unit and multi-unit TemplateBundles could overlap selected pronunciation units without a defined coverage/exclusivity rule. **Original Gate A protocol and Amendments 01/02 are preserved unchanged.**

[SMC4_GATE_A_AMENDMENT_03.md](SMC4_GATE_A_AMENDMENT_03.md) at initial commit `7a80f8b0b016cb51ad5b9c3225cd919acc2cbfbc` narrows first Gate B mapping scope to exactly one selected pronunciation unit per TemplateBundle; multi-unit/overlapping bundles in the requested profile are rejected as `UNSUPPORTED_MAPPING_SCOPE`, not silently accepted or discarded. Context predicates may inspect neighbors without owning their mapping scope. F28–F32 prospective fixtures specify covered/overlapping/missing/ambiguous cases. No SMC-4 code, no scientific adoption or main merge.

## SMC-4 Gate B-R canonical ingress — proposed design only (2026-10-25)

- [SMC4 Gate B-R CanonicalRequestBoundary design candidate](SMC4_GATE_BR_CANONICAL_REQUEST_DESIGN.md) — finite UTF-8 JSON wire ingress, typed acyclic validated request snapshot, independent raw-submission vs canonical-experiment hashes, malformed-input rejection semantics, resource ceilings and BR01–BR14 prospective falsifiers.
- [Design Issue #185](https://github.com/ryonakayama234/morphoacoustics/issues/185) and [stopped Gate B Draft #180](https://github.com/ryonakayama234/morphoacoustics/pull/180). This is a **prospective semantic-contract amendment**, not a retroactive cure or adoption of the intentionally RED Gate B software branch.
- **Status:** `PROPOSED / DESIGN_ONLY / NO_EXECUTABLE_CODE / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE`. Requires independent GitHub Codex design review and a recorded design verdict before implementation.

## SMC-4 Gate B-R implementation research (2026-10-25)

- [Frozen ingress-only test protocol](SMC4_GATE_BR_PROTOCOL.md): exact typed UTF-8 JSON wire schema, finite resource ceilings, raw vs canonical SHA, prospective BR01–BR14 fixtures.
- [Design-only proposal](SMC4_GATE_BR_CANONICAL_REQUEST_DESIGN.md) from stacked [design PR #186](https://github.com/ryonakayama234/morphoacoustics/pull/186).
- [Research PR #189](https://github.com/ryonakayama234/morphoacoustics/pull/189) and [test-only RED PR #190](https://github.com/ryonakayama234/morphoacoustics/pull/190). Source `../src/morphoacoustics_smc/canonical_ingress.py`; prereg and Codex tests in `../tests/test_smc4_br_*.py`.
- [SYSTEM ingress-only boundary](SYSTEM.md), [DATA receipt/typed shape](DATA.md), [EXPERIMENTS negative vs green exact-SHA evidence](EXPERIMENTS.md).
- **`REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE`**. Historical [Gate B REVISE](https://github.com/ryonakayama234/morphoacoustics/pull/180) intact; no TaskLexicon plan compiler bridge, Studio or physical audio.

### Independent review round two

Second GitHub AI software review found typed rational timing sort-key P2; `../tests/test_smc4_br_codex_round2.py` was added test-first and `../src/morphoacoustics_smc/canonical_ingress.py` fixed separately. [EXPERIMENTS evidence](EXPERIMENTS.md), [DATA exact key semantics](DATA.md). The design #186 reviewer status and exact fixed docs HEAD CI remain open; **NO_MAIN_MERGE**.

## SMC-5 synthetic canonical-to-symbolic research bridge (2026-10-26)

- [SMC5_GATE_A_PROTOCOL.md](SMC5_GATE_A_PROTOCOL.md): frozen S01–S12 research hypotheses, falsifiers and code/test order (pre-source SHA `0cbd9171b53c16402644750018858cc8967b1377`).
- [SMC5_SYSTEM.md](SMC5_SYSTEM.md): request → finite Task selection → SMC-3 graph validation → candidate, without Core/Studio execution.
- [SMC5_DATA.md](SMC5_DATA.md): typed TaskGoal interval metadata distinct from frozen SMC-3 plan graph, exact digests and selection provenance.
- [SMC5_EXPERIMENT.md](SMC5_EXPERIMENT.md): artificial fixtures, test-first RED and exact-SHA CI plan.
- [SMC5_RESULTS.md](SMC5_RESULTS.md): append-only execution evidence and explicit MORE_DATA until independent review.
- [SMC5_DECISIONS.md](SMC5_DECISIONS.md): bounded adoption and STOP/owner-agreement conditions.
- Research Issue [#210](https://github.com/ryonakayama234/morphoacoustics/issues/210) / stacked [Draft PR #211](https://github.com/ryonakayama234/morphoacoustics/pull/211). Inherited Draft #189/#186/#175/#164 remain unmerged; historical Draft #180 remains REVISE/RED. **No accepted phonetic, physics, audio or production API claim.**


## SMC-6 Gate A0 — 2026-10-27 DESIGN ONLY (next proposed research; not adopted)
- [Issue #219](https://github.com/ryonakayama234/morphoacoustics/issues/219): scientific measurands, explicit falsifiers and two-lane coordination boundary. **Design refinement only**, no code, no Gate A freeze, no Core/Studio/ABI.
- [SMC6_A0_SYSTEM.md](SMC6_A0_SYSTEM.md): system architecture and exact-SMC5 versus experimental timing lanes, diagrams.
- [SMC6_A0_DATA.md](SMC6_A0_DATA.md): proposed private sidecar data, identity/provenance and entity diagram.
- [SMC6_A0_METROLOGY.md](SMC6_A0_METROLOGY.md): L0-L3 evidence taxonomy; formal measures M01-M12, error/uncertainty and independent oracle.
- [SMC6_A0_EXPERIMENT.md](SMC6_A0_EXPERIMENT.md): H0-H6 falsifiers, T01-T15 candidate fixtures, controls and unresolved design choices.
- [SMC6_A0_DECISIONS.md](SMC6_A0_DECISIONS.md): provisional decisions D01-D09 and explicit STOP/approval boundaries.
- SMC5 [Draft #211](https://github.com/ryonakayama234/morphoacoustics/pull/211), source SHA `894d2f0d68169e7f794d78be729057b3b31d6017`, is only `GO_LIMITED_SYMBOLIC` synthetic software; SMC6 design is **not** a new scientific adoption or main merge.


## SMC-6 Gate B — bounded exact temporal-reasoning research, test-first (2026-10-27)
- [Owner Issue #219](https://github.com/ryonakayama234/morphoacoustics/issues/219), design-only [Draft #221](https://github.com/ryonakayama234/morphoacoustics/pull/221) and separate implementation research [Draft #225](https://github.com/ryonakayama234/morphoacoustics/pull/225). Implementation stacks on design A0 → verified SMC5 SHA `894d2f0d...` → unmerged SMC4-BR; **not main-ready**.
- [Protocol first, exact frozen T01–T15](SMC6_GATE_A_PROTOCOL.md) precedes tests/code; [as-built SYSTEM / DATA / metrology](SMC6_GATE_B_IMPLEMENTATION.md) has Mermaid charts and L0–L3 meaning separation.
- [Append-only RESULTS](SMC6_GATE_B_RESULTS.md) records actual test-only RED `7084b339`, first mypy RED `28b996c2`, repair `21ef0748`, independent exact grid oracle `a2622da1`, exact-sha green CI and review/adoption limitations.
- Private `../src/morphoacoustics_smc/temporal_stn.py`, test-first `../tests/test_smc6_stn_preregistered.py`, independent reference `../tests/test_smc6_independent_oracle.py`. SMC-3/5 and `__init__.py` untouched. Hard STN and mathematical witness **do not** imply phonetic/natural/body/acoustic correctness; **NO_PUBLIC_MOTORSCORE_ABI / NO_STUDIO_UI / NO_CORE_PHYSICS / NO_MAIN_MERGE**.

## SMC-7 Gate A0 — linguistic-to-motor evidence / design refinement (2026-10-27)
- [Design Issue #229](https://github.com/ryonakayama234/morphoacoustics/issues/229): new measured hypotheses, data separation and refusal/acceptance boundary; **DESIGN_ONLY / NOT_PREREG_FROZEN / NO_CODE / NO_MAIN_MERGE**.
- [SMC7_A0_SYSTEM.md](SMC7_A0_SYSTEM.md): two front-end lanes, authenticated SMC5/6 legacy bridge, Core/Studio authority; system Mermaid.
- [SMC7_A0_DATA.md](SMC7_A0_DATA.md): original source spans, whole-utterance reading paths, selections, evidence, digests, staged refusal, ER diagram.
- [SMC7_A0_METROLOGY.md](SMC7_A0_METROLOGY.md): L0/L1/L2/L3 evidence taxonomy, L01–L16 proposed measures, independent corpus/oracles, candidate recall vs burden and selective risk.
- [SMC7_A0_EXPERIMENT.md](SMC7_A0_EXPERIMENT.md): prospective H0–H8 / F01–F16, comparative baselines and negative experiments, **not frozen and not executed**.
- [SMC7_A0_DECISIONS.md](SMC7_A0_DECISIONS.md): D01–D11 provisional decisions, open design questions, prerequisites for future separate Gate A and testing.
- Stack directly upon exact SMC6 research Draft #225 head 0caa70f6; **NOT upon CVI experiment #226**, which remains independent Core research with an actual semantic STOP. No source/test/public schema, Core, Studio or ASMR changes.

## SMC-7 A0 design-review amendment (2026-10-28)
- [SMC7_A0_REVIEW_AMENDMENT_01.md](SMC7_A0_REVIEW_AMENDMENT_01.md): Codex P2 exact temporal-scenario input and stage-specific SMC5 digest retention on SMC6 UNSAT. Supersedes only conflicting A0 clauses; review required.

## SMC-7 L0 preregistered execution evidence (2026-10-28)
- [Gate A frozen protocol](SMC7_GATE_A_PROTOCOL.md), prior to test-only RED 1579f332 and source e5b9985.
- [SMC7_GATE_B_RESULTS.md](SMC7_GATE_B_RESULTS.md): exact source and CI, root pytest nested-approx blocker, independent review state and stage-wise limits.
- [SMC7_GATE_B_DECISIONS.md](SMC7_GATE_B_DECISIONS.md): HOLD_FULL_GATE / MORE_DATA, no main merge; L1/physical/audio not claimed.

## SMC-7 L0 Gate B-R trust repair — 2026-10-28
- [SMC7_GATE_B_REPAIR_PROTOCOL.md](SMC7_GATE_B_REPAIR_PROTOCOL.md): frozen repair protocol; P1 forged proposal / P2 size ordering / merged main #234 test-only backport.
- [Gate B RESULTS](SMC7_GATE_B_RESULTS.md) and [DECISIONS](SMC7_GATE_B_DECISIONS.md): append-only original STOP plus new RED, 17/17 exact code-SHA CI, independent review pending.
- Research repair [Draft PR #236](https://github.com/ryonakayama234/morphoacoustics/pull/236); original stopped Draft #232 remains unmerged.

## SMC-7 L1-R methodological research / evidence software (2026-10-29; append-only latest)
- [Owner Issue #242](https://github.com/ryonakayama234/morphoacoustics/issues/242), new stacked [Draft PR #243](https://github.com/ryonakayama234/morphoacoustics/pull/243) on unmerged accepted L0 repair #236; **NO MAIN MERGE**.
- [SMC7_L1R_GATE_A_PROTOCOL.md](SMC7_L1R_GATE_A_PROTOCOL.md): method preregistered before tests/source at SHA `2dfb61d`; proposed 880 held-out and 120 pilot **NOT yet gathered/frozen**.
- [SMC7_L1R_GATE_B_AMENDMENT_01.md](SMC7_L1R_GATE_B_AMENDMENT_01.md): independent first-review P2 pair, frozen before review-regression tests and repair.
- [SMC7_L1R_IMPLEMENTATION.md](SMC7_L1R_IMPLEMENTATION.md): as-built finite evidence/manifest/context/explicit selection + exact software fixture metrics, no automatic G2P or motor plan.
- [SMC7_L1R_GATE_B_RESULTS.md](SMC7_L1R_GATE_B_RESULTS.md): test-only missing-module RED, first 16/16 GREEN but review P2, second 5-failure RED, repaired exact-code SHA `f2ff1e0` 16/16 GREEN + independent re-review no findings.
- [SMC7_L1R_DECISIONS.md](SMC7_L1R_DECISIONS.md): **GO_LIMITED_L1R_EVIDENCE_SOFTWARE** only at `f2ff1e09535fd2578dee4f5a12faca4b228fcdd1`; **MORE_DATA_L1_LINGUISTIC_CORPUS_AND_PROVIDER**, not `GO_LIMITED_L1_READING`. Future corpus/license/annotations [Issue #244](https://github.com/ryonakayama234/morphoacoustics/issues/244).
- No adopted Japanese predictive quality, stress/accent/phonetic score, body/physical Task binding, acoustic quality, public MotorScore ABI or Studio UI. Historic L0 STOP entries above are retained as time-local records, not overwritten by this appended evidence.
