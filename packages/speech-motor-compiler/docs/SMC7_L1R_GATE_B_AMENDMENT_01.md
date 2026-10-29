# SMC-7 L1-R Gate B amendment 01 — independent review P2 source repertoire and hostile profile equality

**2026-10-29 JST | Issue #242, Draft #243 | REVIEWED_CODE_REVISE | preregister BEFORE adversarial tests and source repair.**

Original frozen method `SMC7_L1R_GATE_A_PROTOCOL.md` commit `2dfb61dedf9bab1933ac488e3de5a65490d7ff8a`. Test-only RED `5a5b8fd7ffda571a0d4b8d28e79c18de708dd012` from isolated package Python 3.11 [workflow 40817153089](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40817153089), missing module. Implemented first candidate source SHA `38a4c7e84714dadeb0b037127d68a71039d816bf` with 16/16 GitHub check-runs PASS. This is **NOT an accepted software baseline** because independent Codex review reported two real P2 flaws:

1. [P2 source repertoire bypass](https://github.com/ryonakayama234/morphoacoustics/pull/243#discussion_r4408671713): L0 `make_proposal` correctly verifies source spans but does not determine allowable L1 source script. Current L1 accepts `😀`, `甲A`, `ー`, `・` with forged but structurally valid caller reading `ア`, contrary to the preregistered Gate A unsupported-source refusal.
2. [P2 hostile profile equality](https://github.com/ryonakayama234/morphoacoustics/pull/243#discussion_r4408671715): `_context_error` compares `profile != "ja-JP"` before type-checking. Caller-defined `__ne__` can throw or run arbitrarily, bypassing fail-closed `ValueError`.

## Normative bounded repair policy
- Predeclare supported **source** Unicode repertoire on this first gate only: CJK unified base U+4E00..U+9FFF, hiragana U+3041..U+3096, katakana U+30A1..U+30FA, and exactly existing L0 silent punctuation separators `SPACE TAB LF 、 。 ！ ？ …`. This is a **restricted research subset**, *not* full Japanese orthography or a claim that every admitted sequence is linguistically correct. `ー` (U+30FC), middle dot `・`, ASCII, emoji, CJK extension/iteration signs, composed/decomposed combining mark, CR and half-width kana require a later separately preregistered policy. Keep original codepoints and no normalization. Check repertoire after existing O(1) length bound, never scan overlong sources.
- In `context_hash(context, revision, profile)`, reject `type(profile) is not str` **before evaluating any comparisons**. Context input and revision must likewise be typed and length-gated before iteration.
- Do not modify L0 `make_proposal`, SMC4/5/6, Core, Studio or public API. No human phonetic/body/acoustic claims.

## Frozen new falsifiers (must first be failing tests on old code)
- R01 `"😀"` with plausible full span/caller reading, correct matching manifest -> explicit `REJECTED` `UNSUPPORTED_SOURCE`.
- R02 `"甲A"` with matching entire span -> same rejection.
- R03 `"ー"` with matching entire span -> same rejection.
- R04 `"・"` with matching entire span -> same rejection.
- R05 a legitimate Japanese source containing basic kanji/kana and L0 silent punctuation remains `PROPOSED`, with complete source coverage.
- R06 `context_hash(..., profile=HostileProfile())` with `__ne__` raising AssertionError -> **ValueError** `INVALID_PROFILE_OR_REVISION` without invoking the hostile comparison; ordinary `"en-US"` is rejected too.

After tests are committed, observe actual RED via GitHub isolated package workflow (ideally distinct R01-04/R06 failures); then minimal source repair, full exact-SHA 3.11/3.12/3.13 isolated+root+strict mypy+SV1 CI, and a new exact code SHA Codex review. Preserve first source SHA P2, no retroactive GO. Even repaired software cannot validate Japanese predictive H1-H4 without licensed blinded held-out corpus (Gate C Issue #244).
