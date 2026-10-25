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


## SMC-4 Gate B navigation and scoped decision trail (2026-10-24)

- [Gate A first frozen design](SMC4_GATE_A_PROTOCOL.md); [post-review Amendment 01](SMC4_GATE_A_AMENDMENT_01.md), [Amendment 02](SMC4_GATE_A_AMENDMENT_02.md), [Amendment 03](SMC4_GATE_A_AMENDMENT_03.md) — all preserved.
- [**Gate B frozen test protocol**](SMC4_GATE_B_PROTOCOL.md) — created before executable compiler; its fixture expectations originate in Gate A F01–F32.
- [SMC-4 Gate B source](../src/morphoacoustics_smc/smc4_lexicon.py) and [typed entities](../src/morphoacoustics_smc/smc4_types.py): versioned synthetic TaskLexicon → unchanged SMC-3 symbolic IR + separate mapping receipt.
- [Gate B synthetic adversarial tests](../tests/test_smc4_gate_b_preregistered.py), [Experiment/evidence timeline](EXPERIMENTS.md), [System and causal boundary diagram](SYSTEM.md), [Data contract](DATA.md).
- [Issue #179](https://github.com/ryonakayama234/morphoacoustics/issues/179), [Draft PR #180](https://github.com/ryonakayama234/morphoacoustics/pull/180). Gate A `GO_DESIGN_ONLY`; Gate B outcome pending final exact HEAD checks and `@codex review` at the time of initial docs write. **Not merged to `main`; no Japanese phonetic/physical or waveform evidence.**


**SMC-4 Gate B review ledger:** [SMC4_GATE_B_CODEX_REVIEW.md](SMC4_GATE_B_CODEX_REVIEW.md) — two reviewed exact SHAs, seven P2 GitHub Codex findings, preserved test-only red evidence, repaired exact-source SHA `504e1e4` 16/16 green (184 synthetic cases on Python3.12), final review/CI still pending at document-write time. Scientific/physical/phonetic adoption remains withheld; research Draft only.


**Third SMC-4 Gate B Codex review:** three further P2 at `827c66d3`, 10 total across three AI review rounds, with separate test-only RED at `0b49c5d`, intermediate RED at `cd5b2e1`, corrected source `4a9bfa2` **16/16 green** and 194 synthetic tests. Detailed [review ledger](SMC4_GATE_B_CODEX_REVIEW.md), [experiments](EXPERIMENTS.md). Fresh final-HEAD review remains required; no human linguistic evidence or main merge.


**Fourth Codex Gate B review:** 11 total P2 across four reviews, new capability-declaration failure from SHA `32492597`, test-only RED `e5d5948c`, repaired source SHA `d57cddc1` 16/16 green. [Full review evidence](SMC4_GATE_B_CODEX_REVIEW.md). No code/main/phonetic-science promotion until a fresh final-HEAD independent AI review and explicit limited decision.

## SMC-4 Gate B — active bounded TaskLexicon research

- [Gate A immutable original protocol](SMC4_GATE_A_PROTOCOL.md), [Amendments 01](SMC4_GATE_A_AMENDMENT_01.md), [02](SMC4_GATE_A_AMENDMENT_02.md), [03](SMC4_GATE_A_AMENDMENT_03.md); owner-delegated `GO_DESIGN_ONLY` recorded in [#174](https://github.com/ryonakayama234/morphoacoustics/issues/174).
- [Gate B preregistration](SMC4_GATE_B_PROTOCOL.md), [GitHub Codex five-round review / RED→repair ledger](SMC4_GATE_B_CODEX_REVIEW.md), [Issue #179](https://github.com/ryonakayama234/morphoacoustics/issues/179), [stacked Draft PR #180](https://github.com/ryonakayama234/morphoacoustics/pull/180).
- Code: `../src/morphoacoustics_smc/smc4_types.py`, `../src/morphoacoustics_smc/smc4_lexicon.py`; tests: `../tests/test_smc4_gate_b_preregistered.py` and `../tests/test_smc4_gate_b_codex_p2_round5.py`.
- [SYSTEM architecture diagram](SYSTEM.md), [DATA semantics](DATA.md), [EXPERIMENTS falsifiers/receipts](EXPERIMENTS.md). All synthetic, no Japanese phonetic validation, morphology, physics, Studio, WAV or `main` merge.

### Gate B ongoing adversarial review: sixth round

[Review ledger](SMC4_GATE_B_CODEX_REVIEW.md) now includes six GitHub Codex rounds / 16 material P2s with test-only RED and independent repair commits. New [round-six regression tests](../tests/test_smc4_gate_b_codex_p2_round6.py) prove deep/cyclic fingerprint fail-closed, shared-predicate DAG identity and canonical rejection diagnostics. The corrected research candidate still requires final SHA CI and another exact-HEAD `@codex review`; it is not merged to `main`.

### Seventh independent AI software review — DAG complexity and invalid-input reproducibility

[SMC-4 Gate B Codex review ledger](SMC4_GATE_B_CODEX_REVIEW.md) now retains seven rounds / 19 material P2 findings with immutable test-first RED evidence, code fixes and SHA distinction. [Round-seven tests](../tests/test_smc4_gate_b_codex_p2_round7.py) validate bounded DAG evaluation, subtree-height enforcement and cyclic request fingerprint equivalence. [DATA](DATA.md) describes canonical predicate graph semantics; [EXPERIMENTS](EXPERIMENTS.md) records test-authored corrections separately from compiler repairs. Final exact-SHA verification and next `@codex review` remain adoption prerequisites.

### Eighth Codex review and final research status

[SMC-4 Gate B Codex review ledger](SMC4_GATE_B_CODEX_REVIEW.md): eight completed GitHub AI software review rounds, 22 material P2, all source failures and repairs preserved. [Round-eight regression tests](../tests/test_smc4_gate_b_codex_p2_round8.py) exercise distant cyclic input identity, malformed time declarations and order-independent invalid-definition receipts. [DATA](DATA.md) describes the corrected boundaries. **Gate B disposition remains reviewer/CI pending, scientific phonetics and physical speech not adopted; no main merge.**

### Ninth Codex audit: generalized caller trust boundary

[Complete review ledger](SMC4_GATE_B_CODEX_REVIEW.md): nine GitHub Codex AI software rounds, 26 P2 findings, original RED test evidence and separate repaired research-only commits. [Round-nine regression tests](../tests/test_smc4_gate_b_codex_p2_round9.py), [DATA](DATA.md) for nonrecursive request fingerprint and identifier/timing guards, and [EXPERIMENTS](EXPERIMENTS.md) for per-SHA results. `REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE` until exact-source/doc CI and clean Codex review.
