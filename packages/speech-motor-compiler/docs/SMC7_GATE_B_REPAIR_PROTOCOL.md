# SMC-7 L0 Gate B-R repair protocol — trust-boundary and bounded parsing
**Date 2026-10-28 JST / OWNER #231 / parent STOP SHA 57692629011937c475f3d3b10fb21f73c8556afd.**
**Status PROTOCOL_FROZEN_BEFORE_NEW_RED / NO_IMPLEMENTATION_YET / NOT_ADOPTED / NO_MAIN_MERGE.**

## Measured STOP evidence
Code-bearing e5b998565908859612074dbdcf32266ca3edb9a0 passed isolated SMC Python 3.11/3.12/3.13 but failed independent software review: P1 https://github.com/ryonakayama234/morphoacoustics/pull/232#discussion_r4395336542 forged ReadingProposal succeeds without revalidation; P2 https://github.com/ryonakayama234/morphoacoustics/pull/232#discussion_r4395336547 traversal of oversized input before length gate. Full root CI also failed (nested pytest.approx in existing shared timeline assertion).

Independent infrastructure confirmation: upstream https://github.com/ryonakayama234/morphoacoustics/pull/234 is already MERGED to main SHA f1020c568c54615bc9fdc4c9804128ddbcc3ff0d and main test CI passed. It edits **one test file**, no numerical behavior. The unmerged SMC6-parent research stack does not yet include it; copy the exact change with explicit credit in a **separate test-only backport commit**, preserving full expected numerical values/tolerances. Do not cherry-pick whole main branch or overwrite SMC6 stack.

## Narrow hypotheses and explicit falsifiers (R01-R10)
- R01: caller-provided dataclass ReadingProposal is UNTRUSTED at compile_selected entry. A replaced source with extra uncovered character and matching SMC4 wire must be refused BEFORE SMC5, never SYMBOLIC_READY.
- R02: forged source placing a formerly pronounceable unit on a silent punctuation codepoint is refused before SMC5.
- R03: source >256 codepoints (or >2048 UTF-8 bytes) cannot use forged proposal to bypass limits.
- R04: substituted source_digest / proposal_digest (including None), forged status/code or modified paths must not pass without full revalidation. A correctly independently reconstructed identical *valid* proposal with same deterministic digests remains accepted: hashes are *consistency checks*, NOT cryptographic authentication or proven phonetics.
- R05: all candidate paths, not only selected, must be structurally valid and source-aligned; forged unselected path rejects full proposal. New failure code BAD_PROPOSAL_INTEGRITY at stage PROPOSAL; no smc5/smc6 for invalid object.
- R06: source type and length checked before potentially O(N) Unicode scan and before UTF-8 encode; 257 codepoints triggers SOURCE_LIMIT and _scalar is not called.
- R07: symbol type+length<=32 checked before _scalar scan; probe with monkeypatched _scalar or huge string to verify rejected without scanning symbol, but valid source still processed.
- R08: existing direct SMC4/5 and SMC6 COMPATIBILITY equality, SMC6 UNSAT retention of SMC5 candidate digest, no NATURAL audio/physical fields unchanged.
- R09: root pytest 9.2 assertion backport reproduces merged PR #234 *exactly* and root 3.11/3.12/3.13 become independently green; no root production source or evaluation threshold changes.
- R10: hostile nested containers/invalid dataclass field types fail closed with bounded scanning; no unhandled exceptions in proposal revalidation for admissible API object shapes.

## Implementation boundary and sequence
First commit this protocol; second add **test-only RED** on exact stopped implementation; run GitHub CI and preserve the assertion traces from R01-R07. Then only modify reading_paths.py with stage-ordered validation: use make_proposal on every inbound instance and compare recomputed entire immutable record (including metadata/digests) with supplied record; never trust status or a digest alone. Optimization: check type and size before _scalar for source and each symbol. No external library, no G2P model, no Core/Studio changes. Root maintenance backport is a separate commit matching PR #234, not a new fix. Regression and Codex must be on final exact SHA. Record evidence append-only.

## Decision rules
GO_LIMITED_L0_SOFTWARE only if R01-R10 and earlier frozen F01-F14 pass on Python 3.11/3.12/3.13, mypy, exact-source GitHub root/Core regression and independent software review with no unresolved blocking findings. Else MORE_DATA/REVISE/STOP. Do not infer L1 Japanese correctness, body task semantics, speech synthesis, physiological control, Studio UI, public ABI or main merge. Original Gate B STOP and review comments remain immutable.
