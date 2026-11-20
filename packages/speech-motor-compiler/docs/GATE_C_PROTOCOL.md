# SMC-3 Gate C — preregistered adversarial audit protocol (FROZEN)

- Protocol date: **2026-10-23 (Asia/Tokyo)**.
- Candidate under test: **PR #164**, exact candidate commit **`7d5c405fee1b2469b11bbe6d68b9e0d18e4dab05`**. Code-bearing commit previously recorded: `9c9ac9539ae1798ed27ef5cd751562e4b2c9b469`.
- Audit branch: `research/smc3-gate-c-audit-20261023`, **forked from the exact candidate commit**, not from `main`.
- Related issues: [#148](https://github.com/ryonakayama234/morphoacoustics/issues/148), [#162](https://github.com/ryonakayama234/morphoacoustics/issues/162).
- This file must be committed **before** any Gate C test implementation. Preserve commit SHA as preregistration evidence. Subsequent changes require an explicit versioned amendment with justification and cannot silently overwrite the initial criteria.
- Research classification: **ADVERSARIAL_IMPLEMENTER_ORIGIN_AUDIT**. No claim of independent human reviewer, physical validation, phonetic plausibility, Japanese pronunciation, or scientific adoption.

## Hypotheses, falsifiers, and outcomes

### C1 — multiplicity and source/task separation
Represent 2–8 source units and 3–12 distinct task IDs with 1-to-many and many-to-one associations. A task shared by multiple units must have **one task object/ID**, not copies. Reject missing references, duplicate IDs, repeated associations, unassociated source units and orphan tasks. Reorder tuples without changing identity. Falsifier: shared tasks duplicated/lost or accepted invalid associations.

### C2 — exact rational scheduling
Absolute and relative event constraints are equations `t(target) = t(source) + Fraction(lag)` over exact rationals. Construct 3–8-task synthetic plans from predetermined rational onset/offsets with positive durations and deliberately overlapping windows; also make alternate paths/cycles. Reconstruct all absolute times without floats. Falsifier: mismatch to constructive source times, order-dependent solution, rejection of a consistent cycle, or acceptance of an inconsistent cycle. Verify known example G1=[2/25,13/50], G2=[1/5,33/100], G3=[29/100,27/50] seconds; overlaps 3/50 and 1/25.

### C3 — satisfiability vs partial observability
A connected, absolutely anchored component with contradictory equalities is **INVALID** with `CONTRADICTORY_TIMING`. A disconnected/unanchored event component can be `STRUCTURALLY_VALID` but must **not** yield resolved timestamps; `resolve_timing` must return `INVALID` with `UNRESOLVED_EVENT` and no events. A duration resolved as <=0 or a resolved anchored event before zero must be rejected. Falsifier: fabricated default timing, arithmetic tolerance hides exact mismatch, or partial output on failure.

### C4 — source integrity, non-inference and boundary
Keep original Unicode text and Python codepoint spans unchanged; no automatic kanji reading, missing motor-task synthesis, body geometry, physical `GestureScore`, waveform or executable-capability assertion. Change source => change `plan_digest`; permute identical tuples => retain canonical JSON/digest. Do **not** assume that differently encoded but logically equivalent constraint sets have equal digests; that is NOT an adopted normalization guarantee.

### C5 — reproducibility, isolation and regressions
Use a **fixed generator seed list** `[0, 7, 23, 148, 164]`, **20 cases per seed**, with explicitly derived, distinct rational source timestamps and exact expected event tables. In addition run hand-designed adversarial fixtures; print/store seed and test id on failure. Python 3.11–3.13 package pytest + mypy; root/core existing tests and bounded SV1; inspect OG3/OG4 **separately** where available. Test standalone package install/import without Core/Studio runtime. Do not change Studio, root public contract or physical-solver code. No forced `main` merge.

## Execution and oracle independence
1. Commit THIS protocol first. Then implement audit fixtures in a separate commit, without modifying the candidate validator on that commit.
2. A constructive oracle supplies independent rational event timestamps before encoding pairwise relations. Verify candidate against those source values; include both consistent redundant cycles and deliberately mutated contradictory anchors/couplings.
3. Separate mathematical cross-check: Wolfram Language `Solve`/`Reduce` for event equalities and inequalities; record code and manual exact output. CI must not claim Wolfram ran unless verified.
4. Transformation tests: reorder units/tasks/links/couplings/anchors; shift all anchored times by a positive rational and expect shifted absolute timestamps and unchanged relative intervals; renaming IDs changes labels but not schedule structure.
5. Test expected explicit rejections, including malformed source spans, missing references, duplicate IDs, wrong rational lag types, zero/negative durations, and missing absolute origin.
6. Track failing evidence first, with candidate exact SHA; classify `BUG`, `UNDER_SPECIFIED`, `TEST_ERROR` or `DOCUMENTATION`; corrections occur only after failure evidence. Re-run checks at new exact SHA.

## Freeze criteria and review gates
- Gate C exploratory software pass: zero unexplained disagreements on predeclared fixtures, independent numeric oracle, property transformations, package checks and relevant regressions; every deviation and skipped check disclosed with SHA.
- `GO_LIMITED_SYMBOLIC`: **additionally requires distinct independent reviewer** with identity, exact audited SHA, independently designed unseen tests and explicit bounded signoff. Automated test success alone never satisfies this gate.
- Otherwise: `REVISE` (bounded fix), `MORE_DATA` (absent reviewer or missing evidence) or `REJECT` (non-repairable representation failure).
- Decision independent of merging PR #164 into `main`; no main merge or physical/adoption APIs under this protocol.
- Outputs: audit tests, independent mathematical oracle, **SYSTEM.md / DATA.md / EXPERIMENTS.md / INDEX.md** updates, draft PR, exact-SHA CI receipts, separate peer-review status.

## Scope stop
This gate only audits **symbolic software expressiveness and exact temporal consistency**. It does not establish physical realizability, natural speech, language-level phoneme inference, prosody, acoustics, Studio UX, or physiological empirical facts.

## Scientific background (context, not test oracle)
Browman & Goldstein (1992), *Articulatory Phonology: An Overview*, https://pubmed.ncbi.nlm.nih.gov/1488456/ ; prior SMC-3 Gate A/B evidence is logged in existing `EXPERIMENTS.md`.
