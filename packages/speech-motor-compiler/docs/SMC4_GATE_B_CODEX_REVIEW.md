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
