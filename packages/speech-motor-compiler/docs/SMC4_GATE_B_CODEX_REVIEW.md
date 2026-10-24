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
