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
