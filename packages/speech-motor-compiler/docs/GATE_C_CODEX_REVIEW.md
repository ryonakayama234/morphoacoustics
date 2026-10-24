# Gate C — Codex P2 review follow-up (2026-10-24)

**Disposition: corrected software findings, independent Codex re-review PENDING; SCIENCE_NOT_ADOPTED; NO_MAIN_MERGE.**

This is a *post-freeze addendum*. The prospectively frozen [GATE_C_PROTOCOL.md](GATE_C_PROTOCOL.md), commit `7705ebd752e191a545506c0a2a79d56a40efc6bf`, is not rewritten. The 100 seed-indexed original Gate C tests are likewise unchanged.

## Scope and reviewer provenance

- Original research implementation: [Draft PR #164](https://github.com/ryonakayama234/morphoacoustics/pull/164), candidate exact SHA `7d5c405fee1b2469b11bbe6d68b9e0d18e4dab05`.
- GitHub Codex **manual code review completed 2026-10-24** on that exact SHA. It produced two P2 software findings:
  - [Unicode receipt inconsistency](https://github.com/ryonakayama234/morphoacoustics/pull/164#discussion_r4365286361): a Python unpaired-surrogate string could be accepted as `STRUCTURALLY_VALID`, but later UTF-8 digest generation fails.
  - [Contradictory timing potential instability](https://github.com/ryonakayama234/morphoacoustics/pull/164#discussion_r4365286367): the same contradictory anchor equalities could yield different error diagnostics depending on input ordering.
- This Codex run is a **distinct AI review execution**, not third-party human peer review. The earlier Codex review of [Draft PR #169](https://github.com/ryonakayama234/morphoacoustics/pull/169), SHA `52b89ab5d1873ebff74df42f8fcd60e114620113`, had *no new findings on that diff*; that did not negate the two P2 findings on PR #164's original candidate.

## Retained red-first evidence

- Test-only commit [`08e2a47c8fd34017b6a52cacaef3485779515617`](https://github.com/ryonakayama234/morphoacoustics/commit/08e2a47c8fd34017b6a52cacaef3485779515617) added `tests/test_codex_p2_regression.py` without changing the SMC validator.
- [Python 3.11 red CI job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40049643238/job/120739210866) and [3.13 red CI job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40049643238/job/120739210593) reproduced **8 failing test invocations**: seven caller-string-field unpaired-surrogate validation cases, and one six-permutation inconsistent-anchor diagnostic test. Existing cases remained passing. [Full pre-fix receipt](https://github.com/ryonakayama234/morphoacoustics/pull/169#issuecomment-6378136272).
- The contradiction was exact: ONSET=0, OFFSET=1 and OFFSET=-1; diagnoses differed between only `CONTRADICTORY_TIMING` and `CONTRADICTORY_TIMING` plus `NEGATIVE_ANCHORED_TIME` and `NONPOSITIVE_DURATION`.
- A separate ordinary non-BMP/ZWJ source case was already passing and is retained as a positive control.

## Separate controlled correction and CI

- Repair commit: [`a3f876fcaef3b63e2612807fab288a7e36e7e54a`](https://github.com/ryonakayama234/morphoacoustics/commit/a3f876fcaef3b63e2612807fab288a7e36e7e54a). Source change confined to `validation.py`. No solver change, no IR schema change, no Core body or Studio integration.
- A validator helper rejects surrogate codepoints U+D800–U+DFFF in the relevant caller string fields with `INVALID_UNICODE_SCALAR` and a field-name diagnostic subject that can itself be serialized safely. Real UTF-8-encodable non-BMP codepoints and ZWJ sequences remain allowed.
- Once `_components` reports contradictory equalities, validation returns the contradiction without inferring negative times or impossible durations from arbitrary traversal potentials. Noncontradictory negative times and nonpositive durations retain their existing tests.
- **Exact repair-code SHA** `a3f876fcaef3b63e2612807fab288a7e36e7e54a`: GitHub checks **16/16 completed SUCCESS**, 0 failure/cancel/pending across duplicate push and PR matrix runs: standalone isolated-package pytest + strict mypy on Python 3.11/3.12/3.13, root test/typecheck matrix and bounded SV1. [Python 3.12 passing job](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40049732250/job/120739514305). This does not pre-approve later docs commits; confirm CI on final HEAD separately.

## Gate criteria (for solo AI-assisted research)

A separate Codex review of **the latest amended PR head** can serve as an additional adversarial *software engineering review* after CI/negative receipts, provided review trigger, commit SHA, findings, responses, and any repeat-review results are recorded. It is **not** called human-independent scientific peer review.

For **limited exploratory adoption as a symbolic motor-task IR**, require a documented red→green history, green exact-SHA CI, Codex's separate review on amended code, no unresolved material code/representation findings, and an explicit restricted-use decision. A reviewer finding of 'nothing major' is insufficient by itself without the evidence above.

Actual bodily gestural feasibility, Japanese reading/phonetics, acoustic correctness, physical synthesis, speaker characteristics and Studio integration are **out of scope** and remain unverified. Neither current success nor a subsequent Codex approval may authorize physical-science claims. The individual OG3/OG4 experiments were not separately verified at this SHA. Keep PRs Draft and do not merge into `main` under this addendum.

## Handoff

New `@codex review` trigger should be posted on [PR #169](https://github.com/ryonakayama234/morphoacoustics/pull/169) only **after** all evidence/docs commits are finalized; inspect the resulting bot summary and inline threads against that exact final commit. PR #164's two original threads should remain visible and not marked resolved merely because a separate PR has proposed a fix. On successful reviewed integration into its research branch, re-review PR #164 on its new exact HEAD (still no main merge).
