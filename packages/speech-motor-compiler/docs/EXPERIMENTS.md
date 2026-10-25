# SMC-3 EXPERIMENTS — frozen Gate A test plan

Preregistered from [#162](https://github.com/ryonakayama234/morphoacoustics/issues/162), before new package code. Artificial tasks G1–G3 are mathematical probes, NOT observed human motor gestures.

## H1: representational expressivity
Input: P1/P2 + G1/G2/G3; edges {(P1,G1),(P1,G2),(P2,G2),(P2,G3)}.
Expected: 2 units, 3 **distinct** task IDs, 4 associations, no duplicated G2 node, STRUCTURALLY_VALID. Falsifier: shared G2 copied or missing association.

## H2: exact scheduling and lexical independence
Input task windows (seconds) G1 [2/25,13/50], G2 [1/5,33/100], G3 [29/100,27/50]; durations respectively 9/50,13/100,1/4. Event equality edges supply exact start/end and common anchor. Consecutive overlap 3/50 and 1/25. Never enforce phoneme lexical order as nonoverlap. Falsifier: float rounding or forced sequential timing.
Independent Wolfram evaluator check on 2026-10-22: `{{2/25,13/50},{1/5,33/100},{29/100,27/50}}` → overlaps `{3/50,1/25}`.

## H3: contradiction / missing endpoint
Input 1: same event forced to two unequal rational times 29/100 and 8/25 → INVALID, CONTRADICTORY_TIMING.
Input 2: coupling to missing task, invalid event name or invalid lag type → INVALID.
Input 3: OFFSET equal/before ONSET when both resolved → INVALID.
Falsifier: any silently accepted contradictory or unknown reference.

## H4: provenance / no unauthorized synthesis
Input: unknown character and absent pronunciation unit must remain undecoded; invalid source span or source empty → INVALID; unassociated unit/task → INVALID. No physical score, audio or body fields. Changing input source changes digest; reordering equivalent relations should not change canonical digest.

## H5: package and regressions
Run from clean root: editable install in isolated Python environment (3.11+), package pytest, mypy, existing root pytest; static check no imported Core runtime. Inspect exact HEAD GitHub checks including OG3/OG4/SV1 where available. Failures and skipped experiments must be recorded without conflating software with physical/phonetic validation.

## Decision criteria
GO_LIMITED_SYMBOLIC only after clean software checks and independent design reviewer; else REVISE/MORE_DATA/REJECT. Real pronunciation, physiology, perception, and cross-body execution have separate gates. No `main` merge in this work package.

## 2026-10-22 exploratory implementation status
Pre-implementation criteria frozen at commit `4f7bef4a9709c96efaa80d8070a2d8b352d9b1d8`; code-first commit `6b31e77365cf965931cb895286727bf75eaa9b57` followed it. Package fixtures exercise shared Task ID, exact rational event propagation, contradictory anchors, unknown endpoints, nonpositive durations, unanchored events, source and association failures, deterministic receipt and absence of physical fields. Results are **not yet claimed** until exact-HEAD GitHub CI runs are inspected; physical and phonetic verification remain NOT TESTED.

### CI negative evidence (2026-10-22)
At HEAD `233bdbac18227a5b1dc974557b671f6b79578030`, first isolated-package Python 3.12 run [workflow run 39777021246](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777021246) installed the package and **21/21 pytest passed**, but strict mypy **FAILED 3 issues**, validation.py line 174/177, from one reused loop variable inferred as conflicting dataclass types (`TaskAssociation` vs `EventAnchor`). Revisions should be tied to a new exact HEAD; never overwrite history or claim CI pass based on pytest alone.

## 2026-10-22 verified software Gate B receipt (not research adoption)
Exact source HEAD **`9c9ac9539ae1798ed27ef5cd751562e4b2c9b469`**: GitHub API reported **16/16 completed check runs SUCCESS** (some duplicate push/PR runs), including isolated Python 3.11/3.12/3.13 package import/install + 21 synthetic pytest cases per run + strict package mypy, existing Core root test matrix/typecheck, and bounded SV1 regression. Evidence: [isolated package run](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258873), [root tests](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258910), [SV1](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39777258867). An earlier failing mypy run is preserved in EXPERIMENTS. Individual OG3 and OG4 were not separately confirmed for this SHA. No independent reviewer, phonetic fixture, body adapter, wav or Studio integration. Disposition: **EXPLORATORY_SOFTWARE_PASS / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**.

## 2026-10-23 Gate C — adversarial test preregistration and implementation receipt (results pending)
- Audit base **`7d5c405fee1b2469b11bbe6d68b9e0d18e4dab05`**; freeze-first commit **`7705ebd752e191a545506c0a2a79d56a40efc6bf`**, BEFORE test code commit **`e51ea60ad4ac59ebdb426f699aaf370cd574f428`**. This ordering is intentional.
- Full falsifiers, seeds `[0,7,23,148,164]`, 20 fixtures per seed, model boundary, possible outcomes and gate rubric: [GATE_C_PROTOCOL.md](GATE_C_PROTOCOL.md).
- Adversarial tests: [../tests/test_gate_c_adversarial.py](../tests/test_gate_c_adversarial.py); independent mathematical script: [../wolfram/gate_c_oracle.wl](../wolfram/gate_c_oracle.wl). Synthetic tests and their expected results are **implementer-origin**, not blinded external experiments.
- Prior independent Wolfram arithmetic exercise established an internally consistent exact 4-variable system, an extra inconsistent equality with no solutions, and two distinct assignments for a free variable; reference script formalizes these controls. No CI Wolfram execution claimed.
- **Pending exact-audit-SHA CI receipt**: no passing status, bug finding, or new adoption claim should be inferred from the committed test code alone. Inspect first run, retain failures, classify unexpected behavior and report separately before any candidate correction.
- Explicit scope: no changes to the candidate validator in the audit's initial test implementation; no Core physics or Studio modifications, no merging to main, no scientific/phonetic adoption, independent human review still outstanding.

## 2026-10-23 Gate C prospective audit — first falsification and controlled repair

### Initial exact-HEAD negative receipt
- Candidate+audit SHA: **`2a3a038c342150b37323a6c4b24cc846954d1c42`**. This SHA contained ONLY audit tests/docs and the untouched candidate implementation.
- [Python 3.12 standalone job failed](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39966372894/job/120457185392); [Python 3.11 standalone job failed](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39966253851/job/120456777040). One explicit exception probe failed: `test_malformed_runtime_source_does_not_crash_validator` → `TypeError: object of type 'NoneType' has no len()` from `validation.py:134`. Other instances of the isolated matrix were cancelled. All checked root test/typecheck jobs and bounded SV1 passed.
- Classification **BUG / FAIL_CLOSED_RUNTIME_INPUT**, captured [before patch](https://github.com/ryonakayama234/morphoacoustics/pull/169#issuecomment-6367686236). Consistent rational plan fixtures and metamorphic checks were not the failing cases.

### Correction performed ONLY after recording failure
- Patch commit **`2de422883e544c1dff5ec12121a1f033a2f3afc5`** guards `len(source_text)` for non-string data in source range checks; no changes to signed Gate C protocol, adversarial fixtures, timing solver, physical Core or Studio.
- **Post-patch software result: PENDING exact final audit SHA and fresh CI inspection.** First red run remains a permanent negative receipt; do not retroactively relabel or silently overwrite.
- This is implementer-origin adversarial testing and repair, **not** independent design review, mathematical/phonetic scientific adoption, or authorization to merge `main`.

## 2026-10-23 Gate C — verified exact-source-SHA repair CI

- **Fixed-source commit `2de422883e544c1dff5ec12121a1f033a2f3afc5`** is **16/16 completed SUCCESS**, zero failure/pending in GitHub check-runs API (two push/PR job sets): isolated package Python 3.11, 3.12, 3.13 pytest with 127 synthetic tests per interpreter, package strict mypy, existing root test matrix/typecheck, and bounded SV1. [Python 3.12 job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39973099897/job/120480625178). This is independent of the earlier red SHA `2a3a038c342150b37323a6c4b24cc846954d1c42`.
- Initial red failure **PRESERVED**, caused by `source_text=None` and unguarded `len(None)`; minimal source guard fixed the runtime fail-closed behavior with unchanged frozen test fixtures.
- All verified outcomes above refer to the **code-bearing SHA `2de422883e544c1dff5ec12121a1f033a2f3afc5`**, not automatically to later documentation-only commits. Document-only final branch HEAD checks require their own confirmation. OG3 and OG4 were not run as separate exact-SHA science gates by these package-scoped actions; do not claim them.
- Disposition: **GATE_C_IMPLEMENTER_ORIGIN_SOFTWARE_PASS / HUMAN_INDEPENDENT_REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE**. This is not a physical or phonetic validation.

## 2026-10-24 Codex P2 prospective regression — verified red-to-green

- Reviewer provenance: GitHub Codex manually reviewed [implementation PR #164](https://github.com/ryonakayama234/morphoacoustics/pull/164) at fixed candidate SHA `7d5c405fee1b2469b11bbe6d68b9e0d18e4dab05`, leaving two P2 line threads. The separate audit [PR #169](https://github.com/ryonakayama234/morphoacoustics/pull/169) had no new major findings on its prior SHA, which is not a blanket approval of #164.
- **RED:** test-only commit `08e2a47c8fd34017b6a52cacaef3485779515617`, untouched production validator; [job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40049643238/job/120739210866) reproduced 7 invalid-unicode-string acceptances and 1 order-variant contradiction diagnostic (8 test invocations fail). Original 100 synthetic Gate C plan fixtures unchanged.
- **GREEN:** separate validator commit `a3f876fcaef3b63e2612807fab288a7e36e7e54a`; **16/16** exact code-SHA GitHub check-runs completed SUCCESS with package pytest + strict mypy on Python 3.11/3.12/3.13 and existing root tests/typecheck plus bounded SV1. [Python 3.12 job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40049732250/job/120739514305). No change to physics, schema, Studio, or main.
- See [GATE_C_CODEX_REVIEW.md](GATE_C_CODEX_REVIEW.md) for expected diagnostics, limitation of AI reviewer provenance, review gate, and per-SHA receipts. **Re-review of final amended HEAD remains separately required; final docs-HEAD checks must not be inferred from the code SHA.** No physical/phonetic science adoption.


## 2026-10-24 SMC-4 Gate B — tests first, failures preserved

**Branch:** `research/smc4-gate-b-bounded-tasklexicon-20261024`; stacked [Draft PR #180](https://github.com/ryonakayama234/morphoacoustics/pull/180), not `main`. **Initial protocol SHA:** `4a2957d9b10256bcd4354902df1655e3377bbeae`, committed before compiler source. Test-only SHA `8f523589e6c8a3bb91d7ad171d9bb9e6b085fa35` preceded source modules.

- **RED proof:** test-only SHA `8f523589...` failed the isolated package CI because the deliberately absent `smc4_lexicon` import cannot resolve; other root/SV1 checks passed. This is test-first evidence, not an existing-software regression.
- **Initial implementation negative:** SHA `c8818a561fdcf23e59fb94af0df5c951e5eb25b9` failed strict mypy (12 diagnostic entries caused by typed loop-variable collisions), retained in [package job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40103863858/job/120901383796). Do not misreport it as scientific falsification.
- **First verified GREEN:** separate fix SHA `5e0059fa5385cc8a95417be5b68c8cf28d39d394` obtained **16/16 completed successful GitHub check-runs** (duplicate push/PR CI, isolated Python 3.11/3.12/3.13 package pytest+mypy, root regressions and bounded SV1). Later exact-source SHAs need their **own** CI receipts.
- **Falsifier expansion:** original test-only commit has 12 named test functions covering preregistered F01/F02/F04/F05/F09/F10/F16/F17/F18/F21/F23/F24/F28/F30; subsequent `a6c7048...` and `1214d86...` add F03/F06/F07/F08/F12a/b/c/F13/F14/F15/F19/F20/F22/F25/F26/F27/F29/F31/F32 and metamorphic/Unicode checks. `c80e1e9...` plus `3470445...` address partial exact timing: an unrelated unanchored Task must not hide an independently proved overlapping-goal contradiction. Tests are all **synthetic and implementer-origin**.
- **Review / adoption:** exact final implementation+docs SHA CI and GitHub manual `@codex review` remain separate checks; a no-findings review is limited AI code scrutiny. Gate B software result may support `GO_LIMITED_SYMBOLIC` only, **never** human-language phonetic, physical or perceptual validation. `SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE`.


## SMC-4 Gate B — two independent AI software-review loops (2026-10-24)

The [Gate B Codex evidence ledger](SMC4_GATE_B_CODEX_REVIEW.md) records exact review SHAs, seven material P2 findings across **two** GitHub Codex review rounds, separately committed regression failures and corrected candidates. The first code-review findings at `c8818a5` concerned partial-time semantic conflict, missing inspectable sharing evidence and rejection fingerprint collisions. The second at `1be16c5` concerned malformed path-coverage runtime types, identical constraint projection under Task sharing, first-wins unsupported-scope reporting and selected rule content missing from receipt identity.

- Reviewer-driven test-only `6f12d42...` RED; corrected input fingerprint `c74421840...` **16/16 success**.
- Reviewer-driven test-only `dc0b6b9...` RED; corrected source `504e1e4cee5472402062054ec7e493fd4ae85cf8` **16/16 success** across two push/PR workflow sets; package Python3.11/3.12/3.13 pytest plus strict mypy, root and bounded SV1. Python3.12 isolated package run: [job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40104996247/job/120904743276), **184/184 synthetic pytest checks passed**. This is software evidence only.
- Additional final documentation HEAD CI and a **fresh manual `@codex review` at that exact SHA** remain necessary before Gate B disposition. Source result is not a main-merge authorization or scientific adoption.


## 2026-10-24 SMC-4 Gate B — third GitHub Codex re-review evidence

The third GitHub `@codex review` of exact docs+code SHA `827c66d3a47e077e4600218ab600fcda09d28ae6` found **three further P2** (invalid Unicode during refusal serialization; unchecked priority runtime types; capability/scope permutations changing canonical receipt identity). These issues were NOT masked by 16/16 passing CI. See [new dated review evidence and links](SMC4_GATE_B_CODEX_REVIEW.md).

- Test-only source `0b49c5df4eeee06eba9dca26380f59514aa5fdc4` **RED**; first fix `cd5b2e1...` still RED for graph capability ordering.
- Final repair code `4a9bfa29949309defdcf02d54d9341174dccc158`: **16/16 completed successful GitHub checks**, including 194 synthetic pytest cases in Python3.12 and strict mypy, plus Python3.11/3.13, root regressions and bounded SV1. This is exact *code* SHA evidence and **not** phonetic or physical science adoption.
- Await a fresh `@codex review` and exact combined docs-HEAD checks before a Gate B limited adoption verdict; preserve all previous reviews and negative runs.


## SMC-4 Gate B — fourth Codex review, capability-input fail-closed proof

Fourth reviewed SHA `32492597` CI was 16/16 green but Codex found P2: malformed `TaskDefinition.capabilities` strings were tokenized characterwise or raised `TypeError`. The regression suite `test_smc4_gate_b_codex_p2_round4.py` preceded repair: `e5d5948c...` isolated package **RED**. Correction `d57cddc1bb0f9a8b8620039cb695c51e2351d2c8` **16/16 exact-source-SHA SUCCESS** across package/root/SV1 checks. Details and reviewer thread in [SMC4_GATE_B_CODEX_REVIEW.md](SMC4_GATE_B_CODEX_REVIEW.md). A subsequent exact docs HEAD review/CI must be recorded independently. No scientific / body / audio gate was performed.

## SMC-4 Gate B — fifth external AI code-review falsification (2026-10-25)

GitHub Codex reviewed SHA `e321d5b71830aef8a5418496013913569b237333` and identified two P2 software bugs: malformed predicate expression can crash or silently become an ineligible alternative; malformed Task-sharing occurrence coordinates can crash hashing/sorting. **RED test-only** `4c74aa657c50983d4ca23ff9e5e079eb72820295`, independent [Python 3.12 failing CI job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40146239323/job/121028079454) (the original candidate was not modified). **Repair source** `e49ecb1ae1ad0e71ca7704e276fecd0d49191ff0`, after the isolated predicate-validation edit `75b346dc37768b306d99a7a5fc563c05ad7b7c8b`. The tests target fail-closed behavior, not Japanese articulation or body/audio truth.

Exact repaired-source CI and a separate final docs-HEAD CI receipt must be recorded without using ancestor results. Details, negative evidence and next independent `@codex review`: [SMC4_GATE_B_CODEX_REVIEW.md](SMC4_GATE_B_CODEX_REVIEW.md). Decision remains **REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE** until exact-source green checks and fresh reviewer verdict.

## SMC-4 Gate B — sixth Codex audit RED-to-repair (2026-10-25)

Sixth external AI code-review on `034d4efa479c29732f2d3e1578ebd4105792a2a4` found P2 failure to fingerprint cyclic/deep predicates, invalid rejection of legitimately reused predicate DAG subtrees, and declaration-order-dependent `INVALID_PLAN` diagnostics. New test-only SHA `1ce67cb97dd821acd01bb865a26923cb9fd76625` **FAILED** the standalone package CI ([workflow 40146642460](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40146642460)); root and SV1 workflows independently succeeded. Separate code corrections `76b5d87324140c38296e29051b5f877f32d000b9` and `2f0c1aa73641d7f397c07f7bfbd66f0051346c9d` implement iterative fingerprinting, active-path cycle detection / subtree reuse, and canonical diagnostic aggregation. **Final corrected-source exact-SHA CI and fresh Codex re-review are required before adoption**; neither source implementation nor these tests support Japanese articulation, physical feasibility or waveform claims. The frozen Gate B protocol remains unchanged.

## SMC-4 Gate B — seventh Codex review: DAG resource bounds and cyclic receipt reproducibility

At exact audited docs+source SHA `7e93f9c66a7f69ed3f84a2f9cf37caece6d01839`, all three GitHub CI workflow groups succeeded, yet Codex identified **three further P2**: subtree-depth bypass, exponentially expanded immutable DAG evaluation and cycle-dependent canonical fingerprinting under AND operand permutation. Regression file `test_smc4_gate_b_codex_p2_round7.py` was committed BEFORE repair; the bounded test-only `179e543764406ab5e9329305432d679ae33c91ea` produced [RED isolated Python CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40147182380). An extra test-authored status/code mismatch was identified and corrected without changing source. Candidate repair `a5c930ab3c65476a7def666321ab0969bc284434` implements cached subtree heights, linear-per-node Kleene evaluation, deterministic cyclic structural fingerprint. Final correct-assertion SHA `4410d6e84e764fe251eae86f735e2d4a8d9708e5` requires *independent exact-SHA CI receipt* and subsequent fresh Codex review; no human phonetic/physical claim and no `main` adoption. See [complete audit ledger](SMC4_GATE_B_CODEX_REVIEW.md).
