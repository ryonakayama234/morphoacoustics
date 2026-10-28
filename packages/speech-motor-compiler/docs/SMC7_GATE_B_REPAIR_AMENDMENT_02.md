# SMC7 Gate B-R — second independent-review amendment (2026-10-28 JST)

**Normative preregistration BEFORE next test-only RED / source.**

Original repair code HEAD 3a9b5dae6614de03b54de6d810376ed5dbfbb7ec passed 17 GitHub checks, but Codex returned P2 [untrusted equality in digest fields](https://github.com/ryonakayama234/morphoacoustics/pull/236#discussion_r4397773467). Supplying unittest.mock.ANY for source_digest and proposal_digest in dataclasses.replace(proposal(), ...) causes equality with recomputed digest strings to succeed, resulting in SYMBOLIC_READY even though input metadata is not a SHA-256 string. Exact prior code is **REVISE**, not GO.

## New falsifiers prior to implementation
- R11: explicit unittest.mock.ANY digest fields and a user-controlled __eq__ object in source_digest / proposal_digest refuse at PROPOSAL BEFORE SMC5/6.
- R12: non-plain built-in Python string metadata (e.g., hostile str subclass with overriding __eq__, or int/bool) is refused; digest fields, source text, revision, status and code must be exactly built-in str, not merely comparable to str. The original source digest and proposal digest are independently recomputed and compared with *plain* sha256 strings.
- R13: hostile nested path/unit ID fields and wrapper subclasses with custom __eq__ must not bypass structural validation or direct wire equality; require concrete built-in tuple and exact ReadingPath/ReadingUnit dataclasses and plain str semantic fields. No changed interpretation of ordinary valid dataclass fixtures.
- R14: direct legacy SMC5/SMC6 exact replay and UNSAT preservation remain unchanged. All earlier red fixtures still pass.

## Code strategy
Validate raw inbound scalar/wrapper types before any caller-controlled equality is invoked, then call bounded make_proposal to validate all path contents, and only then compare received canonical *plain* values with recomputed immutable receipt. Explicitly distinguish integrity from authenticity: no HMAC, verified speaker identity or Japanese reading truth. The repair must remain solely package-local with exact-source 3.11–3.13 CI + independent review again. The merged-main pytest PR #234 test-only backport is unchanged.

Status: ADDENDUM_FROZEN_BEFORE_TESTS / NOT_GO / NO_MAIN_MERGE.
