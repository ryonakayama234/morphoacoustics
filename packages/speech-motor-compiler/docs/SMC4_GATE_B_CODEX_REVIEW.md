# SMC-4 Gate B — GitHub Codex adversarial software review ledger

**Date:** 2026-10-24 JST | [Issue #179](https://github.com/ryonakayama234/morphoacoustics/issues/179) | [Draft PR #180](https://github.com/ryonakayama234/morphoacoustics/pull/180)

**Epistemic ceiling:** Codex is the sole available external AI software/design critic per owner direction. **Not** independent human scientific peer review, proof of real Japanese articulatory targets, morphology portability, physical feasibility or acoustic naturalness. SMC-3 and Gate A remain stacked Draft research; never auto-merge to main.

## Frozen test-order evidence

1. Preimplementation Gate B protocol commit `4a2957d9b10256bcd4354902df1655e3377bbeae`.
2. Test-only SHA `8f523589e6c8a3bb91d7ad171d9bb9e6b085fa35` intentionally **RED** in isolated SMC package ([CI job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40103586084/job/120900551010)), with `ModuleNotFoundError: morphoacoustics_smc.smc4_lexicon`, before candidate implementation existed.
3. First implementation `c8818a561fdcf23e59fb94af0df5c951e5eb25b9` **RED** strict mypy (12 errors, loop-local reused inferred type), [CI job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40103863858/job/120901383796). Minimal fix `5e0059fa5385cc8a95417be5b68c8cf28d39d394` then **16/16 completed success**.
4. Expanded F-oracles include goal sharing, alternative readings, context UNKNOWN, exact timing conflict with unrelated unresolved tasks, unsupported scopes, complete coverage, Unicode rejection and deterministic versions; exact code SHA `3470445553f259da5ec65719d9952db4f0be02ef` **16/16 success**.

## First Codex review: SHA c8818a56 (three P2)

- [P2: independently anchored Task goal conflict](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367464088). Previously, a third unanchored Task suppressed F12a contradiction. Fixed with local exact-time proof for each pair `c80e1e93af880beedf0feedfd1c83e0ed1dd55db`; adversarial F12a test `3470445`. No invented absolute time for unrelated tasks.
- [P2: lost shared provenance/target intersection](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367464094). Added inspectable `mapping_provenance`, rational `task_targets` and input revision metadata `0191e073...` + `cee0abe...`; F20 checks combined interval and both template evidence IDs.
- [P2: rejected input fingerprint collision](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367464097). Extra test-only SHA `6f12d42ada22bbefe5853959d5a9f790c621bab4` **RED**: 4 tests failed (missing input_fingerprint); [job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40104709401/job/120903885056). Repaired with `canonical_request_fingerprint` including selected/unselected paths, profile, context, full rule/data declarations, shares, exact timing and source revision; source fixes `d815dbd8...` and `c7442184...`. **16/16 green** on `c74421840c4d3f377cf7e04297c426f58d15870e`. Canonicalization sorts unordered collections but preserves direction-sensitive tuple coordinates.

## Second Codex review: SHA 1be16c5c (four P2)

- [P2: malformed path coverage could crash or accept truthy nonbool](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367493819). Explicit type checking of path completeness and required span shape before iteration.
- [P2: sharing projection caused spurious duplicate exact coupling](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367493828). Identical projected exact rational constraints collapse idempotently; contradictory different constraints are retained for SMC-3 validation.
- [P2: first-wins unsupported-scope diagnostic](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367493832). Collect all applicable unsupported bundle IDs, sort, then reject, independent of lex declaration order.
- [P2: changed context selection rule not reflected in success receipt](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367493835). Already addressed by `c7442184...` full canonical input fingerprint on BOTH mapped and rejected receipts; regression test confirms changing chosen predicate while the plan stays equal alters digest.

New test-only SHA `dc0b6b9f2086c677b599b7d8643a4d5ab9d6ecc3` **RED** in [isolated package CI](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40104927798/job/120904545232). Separate fix SHA `504e1e4cee5472402062054ec7e493fd4ae85cf8` is **16/16 GitHub check runs SUCCESS**, zero failures/pending, including isolated package Python 3.11–3.13 pytest/mypy and existing root regression/SV1. See [Python3.12 isolated job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40104996247/job/120904743276) (184 package pytest cases).

## Decision boundary

All fixes are research-only within new `smc4_*.py` and bounded synthetic tests. The existing SMC-3 v0 IR remains unchanged, and no Core/Studio/waveform code was modified. New review must target exact **final amended HEAD**, not infer passing status from ancestor source. Final `GO_LIMITED_SYMBOLIC/REVISE/MORE_DATA/REJECT` decision is conditional on clean fresh review+CI; do not interpret no Codex findings as phonetic scientific adoption. **NO_MAIN_MERGE**.


## Third Codex review: SHA 827c66d3 (three additional P2)

GitHub manual [third review](https://github.com/ryonakayama234/morphoacoustics/pull/180) audited full docs+code HEAD `827c66d3a47e077e4600218ab600fcda09d28ae6` (**16/16 checks SUCCESS**). It identified three *new* actionable defects:

1. [Reject receipt on illegal surrogate crashed](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367521705) when an invalid share episode / unsupported scope ID crossed JSON→strict UTF-8. Correction: canonical receipt JSON uses `ensure_ascii=True` for unencodable values; invalid IDs still reject.
2. [Malformed priority was accepted or crashed](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367521708): mixed integer/string priority produced TypeError, all-string priority was compared lexicographically. Correction: `type(priority) is int` or `None` at common selector, including boolean rejection, even for one eligible candidate.
3. [Semantic-unordered capability/scope declarations changed fingerprints](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367521709). Correction: `capabilities` and `target_unit_ids` normalized as unordered in full request fingerprint; additionally emitted symbolic `MotorTask.capability_requirements` tuple sorted for full graph equality (not just digest equality).

**Test-before-fix RED:** new `tests/test_smc4_gate_b_codex_p2_round3.py` at SHA `0b49c5df4eeee06eba9dca26380f59514aa5fdc4` failed isolated package CI, e.g. [3.11 job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40105618567/job/120906574327). First repair `cd5b2e1fa20bd2433cdc95f586c08f6874111137` retained a failing graph-equivalence test; [3.12 negative job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40105645918/job/120906657406). Distinct second repair `4a9bfa29949309defdcf02d54d9341174dccc158` yielded **16/16 completed SUCCESS**, zero failed/pending, including standalone package Python3.11–3.13 and strict mypy, root matrix/typecheck, bounded SV1. [Python3.12 package job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40105808997/job/120907135474) exercised **194 synthetic tests** (72+72+50 progress dots), mypy: no issues in 5 source files.

**Cumulative:** 3 GitHub Codex rounds found 10 substantive P2 defects in initial Gate B candidates, with separate test-first failures and repairs. All are software/specification findings, **not scientific validation**. The final documented HEAD requires its own exact CI and a *fresh* Codex review; do not inherit verdict from ancestor SHA. Main remains unmerged.


## Fourth Codex review: SHA 32492597 — one additional P2

Fourth manual GitHub `@codex review` reviewed complete HEAD `3249259704aeebac3b845b62da3d3d41457a314d`, with **16/16 passing CI** but still [found one P2 malformed capability declaration](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367546360): `TaskDefinition.capabilities="capA"` was sorted into four one-letter tokens, while `("capA",1)` raised `TypeError`. The public symbolic Task therefore failed Gate B's fail-closed runtime input requirement even though static mypy and synthetic fixtures were green.

- **RED first:** new `test_smc4_gate_b_codex_p2_round4.py` on isolated test-only SHA `e5d5948cced262f13758803f5e35345e0edb45a5`, confirmed failed package CI, e.g. [Python3.11 job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40106286777/job/120908539516).
- **Separate repair:** source SHA `d57cddc1bb0f9a8b8620039cb695c51e2351d2c8` validates the capability declaration as a tuple of distinct, nonempty, UTF-8-safe string tokens *before* sorting. Reject malformed values `INVALID_PLAN`, never silently split a string. This exact SHA received **16/16 completed SUCCESS** from GitHub check-runs including package Python3.11–3.13 pytest/mypy, root tests/typecheck and bounded SV1. No SMC-3 IR/Core/Studio modification.

**Four external AI software-review rounds produced 11 P2 findings.** No expert human phonetics review, physical listening test or `main` merge. A fresh Codex inspection and final docs-HEAD CI are separate outstanding receipts. The implementation remains research-only until explicitly gated.

## Fifth Codex review: SHA e321d5b — two further P2; regression and repair

The [fifth manual @codex review](https://github.com/ryonakayama234/morphoacoustics/pull/180) inspected exact implementation+docs SHA `e321d5b71830aef8a5418496013913569b237333`, reporting two additional defects. This makes **13 P2 findings over five review rounds**, none of which is empirical phonetic/physical evidence:

1. [P2 malformed predicate trees](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367560227): an EQ list-valued key raised `unhashable type: list`, a malformed NOT/AND operand raised, and a bool-valued EQ could silently be treated as FALSE in a higher-priority competitor. Rejection must occur *before eligibility*, not as a generic fallback.
2. [P2 malformed share-member coordinates](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4367560231): list-valued / irregular coordinates caused a hash/sort exception before a rejected receipt could be produced.

**Test-before-fix:** new `tests/test_smc4_gate_b_codex_p2_round5.py` committed alone at `4c74aa657c50983d4ca23ff9e5e079eb72820295`; [isolated Python 3.12 CI job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40146239323/job/121028079454) was RED with both crash and silent-ineligible failure witnesses. Negative outcome retained.

**Separate remediation:** `75b346dc37768b306d99a7a5fc563c05ad7b7c8b` added a bounded, strictly typed Kleene predicate-tree validator (node/operator/operand/Unicode shape, no cycles). Source SHA `e49ecb1ae1ad0e71ca7704e276fecd0d49191ff0` validates every lexicon rule tree before selection, plus well-formed tuple-of-two-string share coordinates before sort/hash. A nonselected malformed competitor is not treated as false. No frozen Gate A or B preregistered expectation was edited. **Exact repaired-source and final documentation HEAD CI are separate checks; do not extrapolate success from earlier SHAs.**

**Review request:** ask for a *fresh* GitHub `@codex review` at the final documentation HEAD after exact-SHA verification. The code review is the only available external AI adversarial audit, not human scientific peer review. `SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE`.

## Sixth Codex review: SHA 034d4efa — three further P2, post-review code repair

**Review exact SHA:** `034d4efa479c29732f2d3e1578ebd4105792a2a4` ([Draft PR #180](https://github.com/ryonakayama234/morphoacoustics/pull/180)). Sixth GitHub Codex review found **three additional material P2**, cumulative **16 P2s** in six software-review rounds:
1. [P2 deep/cyclic predicate fingerprinting](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369074219): unconditional recursive `dataclasses.asdict` at compiler entry raised `RecursionError` before the validator could return a rejected receipt for a 400-level NOT tree or self-cycle.
2. [P2 valid shared predicate DAG rejected](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369074223): `AND(p,p)` with one reused immutable predicate was rejected while two equal but separately allocated predicates compiled, violating semantic/object-identity invariance.
3. [P2 declaration-order-dependent invalid-rule diagnostics](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369074225): BA/BI invalid-rule iteration order changed the otherwise identical rejection receipt.

**Separate test-only RED:** `tests/test_smc4_gate_b_codex_p2_round6.py` at commit `1ce67cb97dd821acd01bb865a26923cb9fd76625`; [isolated package workflow 40146642460](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40146642460) FAILED, existing root/SV1 passed.

**Separate repairs:** `76b5d87324140c38296e29051b5f877f32d000b9` implements iterative cyclic/deep-safe predicate fingerprinting **before** validation and distinguishes active-path cycles from shared immutable subtrees; `2f0c1aa73641d7f397c07f7bfbd66f0051346c9d` gathers/sorts all invalid-rule diagnostics before returning a no-plan rejection. No preregistration, SMC-3 v0 IR, Core runtime or Studio alteration. **Final exact-SHA CI and fresh seventh GitHub Codex review still need independent evidence; do not inherit ancestor pass.** Research-only `SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE`.

## Seventh GitHub Codex review — three further P2 and bounded test-first repair (2026-10-25)

**Review exact source+docs HEAD:** `7e93f9c66a7f69ed3f84a2f9cf37caece6d01839`, all three previously verified Actions workflows SUCCESS. The seventh [independent GitHub AI review](https://github.com/ryonakayama234/morphoacoustics/pull/180) identified **three additional P2**, bringing the cumulative software-review audit to **19 material P2 findings across seven rounds**.

1. [P2 previously validated DAG subtree bypassed root depth](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369087379): cached subtree acceptance did not include the depth of a new parent path; 1000-node nested NOT and sampled AND could raise `RecursionError` or depend on AND operand order.
2. [P2 repeated immutable subtree caused exponential evaluation](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369087381): 40 layers of `AND(p,p)` expand over a trillion recursive visits instead of the 41 unique nodes.
3. [P2 cyclic-invalid fingerprint depended on AND operand ordering](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369087385): a DFS cycle marker was incorrectly sensitive to which cyclic child had been visited first.

**Test-first negative evidence:** new `test_smc4_gate_b_codex_p2_round7.py` added in `bb02df159e5cdcc89c5db993e870b9ac2fc5c23f`. A direct long-DAG test was immediately bounded from 40 to 8 layers **without touching the candidate source** in `179e543764406ab5e9329305432d679ae33c91ea`. This source-unmodified test-only SHA **FAILED** isolated Python 3.11 CI ([run 40147182380](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40147182380)): reproduced timeout, RecursionError and different cyclic fingerprints; one additional failure was a test-authored mistaken success `receipt.code` expectation. It does not count as a compiler defect; the assertion was corrected separately.

**Candidate repair:** `a5c930ab3c65476a7def666321ab0969bc284434` modifies only `smc4_types.py`: (1) caches subtree heights checked at every DAG attachment, (2) evaluates strong Kleene logic once per distinct immutable node, and (3) uses bottom-up structural digests for acyclic graphs plus fixed-round synchronous, operand-order-insensitive label refinement for cyclic invalid graphs. Source CI exposed the test-authored `receipt.code == "MAPPED_SYMBOLIC"` error on a successful result whose established code is `OK`; corrected test-only assertion at `4410d6e84e764fe251eae86f735e2d4a8d9708e5` without modifying the repair. All red runs and correction SHAs remain audit evidence.

**Research disposition:** new exact test-corrected source SHA must have green CI; current docs final SHA and next `@codex review` are separate outstanding gates. **No main merge; no Japanese phonetic/body/acoustic validation; AI code review is not human scientific peer review.**

## Eighth Codex software audit — three new P2, bounded Gate B repairs (2026-10-25)

The eighth GitHub `@codex review` audited exact code+docs SHA `999a2207148dd675be8ad9da0d6fdcb66286a2a6`, on which all three Actions workflow groups succeeded. It found **three additional material P2** (cumulative **22 P2 over eight reviews**):
1. [Fixed-round cyclic predicate fingerprint collided on distant changes](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369108533). A cyclic invalid condition and a differing leaf more than 64 NOT edges away yielded identical complete rejection receipts. No synthetic input identity may be lost merely due to the presence of a cycle.
2. [Malformed timing declaration crashed before structured refusal](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369108537). Unhashable `TimeAnchor.unit_id` / `TimeRelation.from_unit` or non-TimeAnchor members raised `TypeError`/`AttributeError` instead of `INVALID_PLAN` with a receipt.
3. [Definition-stage invalid diagnostics depended on declaration order](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369108540). Multiple invalid capability declarations with reordered definitions produced different first-error IDs despite semantically equivalent inputs; frozen F09 applies to rejection as well as success.

**Test-before-fix RED:** `tests/test_smc4_gate_b_codex_p2_round8.py`, exact test-only commit `cc002123496528c543be230c275078fed69d750c`; isolated [workflow 40147579064](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40147579064) FAILED before any source modification. See the preserved independent negative receipt.

**Separate repairs:** `3f2d1e812d92e419a1909a08be762fd364b547f7` replaces the fixed 64-round cyclic graph refinement with `reachable node count + 1` synchronous rounds and includes full reachable graph cardinality. This propagates any distinct leaf information through every simple reachable graph path while keeping the AND/OR child order normalization. `6b56698ca4edcf060f0f376d3bf0cdd7375d7d50` validates timing declaration containers, objects, scalar coordinates and rational/event data **before** dictionary lookup, and accumulates/sorts all invalid TaskDefinition diagnostics. Original preregistration, SMC-3 v0, physics, Studio and waveform code remain unchanged.

**Outstanding:** Verify exact source and final docs SHA CI independently and request a fresh **ninth** GitHub Codex AI review; no `GO_LIMITED_SYMBOLIC` is authorized on green CI alone. `SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE`.

## Ninth GitHub Codex review — general runtime trust boundary (2026-10-25)

Ninth GitHub independent AI software review of exact code+docs SHA `15ed2f09c2da008e3d5b8a75e10ed6c204778e69` (all three Actions workflow suites successful) found **four new material P2**, cumulative **26 P2 over nine audit rounds**:

1. [P2 non-Predicate cyclic/deep container fingerprint RecursionError](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369124402): caller context with list containing itself, or deeply nested list, crashed recursive request normalization before receiving a refusal receipt.
2. [P2 path identifiers accessed/hashed before validation](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369124406): `paths=(0,)` and unhashable `PronunciationPath.path_id=[]` caused `AttributeError`/`TypeError`.
3. [P2 unhashable lexicon identifiers used before validation](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369124409): malformed `GoalSlot.slot_id`, `SlotCandidate.definition_id` or `TemplateBundle.target_unit_ids` caused crashes before structured refusal.
4. [P2 first-missing timing reference changed rejected receipt identity](https://github.com/ryonakayama234/morphoacoustics/pull/180#discussion_r4369124414): equivalent permutation of two dangling anchor/constraint references yielded different receipt digests.

**Test-only RED:** `test_smc4_gate_b_codex_p2_round9.py` committed at `d88844fd87509f508e636ca745b1d4d538b8d426`, standalone package [workflow 40148021942](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40148021942) FAILED, while existing root tests and bounded SV1 succeeded. This was prior to code repairs.

**Separate corrective code:** `d258add2d98b8b7c641f8884ebf04319523b5732` rewrites general `canonical_request_fingerprint` as nonrecursive structural child-digest traversal, independently handles Predicate graphs, sort-normalizes semantically unordered declarations and includes cycle back-edge markers without any recursive `asdict`. `a35f6bba1865f255dca87dbf3bf2a27bdbb7f1b4` validates caller lexicon/path/bundle/slot/candidate identifiers before hash/dictionary operations and canonically collects all missing time references before rejection. An old round-three test required malformed surrogate bundle IDs to remain `INVALID_INPUT` (not `INVALID_PLAN`): corrected with `881f96735cb2b4435aa19b1dc0532cfad5b1ade7`, keeping legacy diagnostic contract without changing the original test.

**Evidence limit:** ninth-round fixes remain research-only, preserving SMC-3 v0, Core, Studio, real phonetics and audio boundaries. Exact source and docs SHA green checks plus a **tenth exact-SHA external GitHub Codex AI software review** are required for a Gate B decision. Given persistent material external findings, absence of a clean review means `REVISE / REVIEW_PENDING / SCIENCE_NOT_ADOPTED / NO_MAIN_MERGE`. No claim of external human scientific peer review.
