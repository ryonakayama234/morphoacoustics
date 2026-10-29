# SMC-7 L1-R C0 — independent external data admission review amendment 01

**2026-10-29 JST | Owner #245 / PR #246 | preregister amendment BEFORE new tests/code**

## Historical facts — preserve
- First C0 protocol `SMC7_L1R_C0_PROTOCOL.md` source SHA `b1c88e3c` preceded tests/code. Test-only RED `838b01f` had missing `morphoacoustics_smc.l1r_real_g2p`.
- First adapter source `ca8c755`, platform Path repair `6ba78f5`; actual isolated GitHub job at `6ba78f5` failed three corpus Path cases (revised `53c0e1b`). All inherited CI checks at `53c0e1b` passed 16/16.
- Actual pinned-package GitHub workflow [40846865407](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40846865407) at workflow SHA `323bb60`: **real** `pyopenjtalk==0.4.1` executed, Open JTalk dictionary downloaded automatically by upstream provider at runtime, active dictionary directory SHA-256 `88167f04755fe6f0973f5be05bf839aad53d600e190d7068b29d7af15c594dbd`; `read_b0("人気のない場所")` returned `READ / PYOPENJTALK_REAL / ニンキノナイバショ`; exact Python 3.11.17 Ubuntu runner recorded. This is a real provider **observation**, NOT an annotated correct answer or approved scientific baseline.
- Same workflow downloaded exact Hugging Face dataset Git revision `2ae383bcdac88dacf89c9ab84f9990eec55fe5c9`, raw JSONL SHA `32a843f662c55f1876baf64f8dc3475cc7b777c576a8fea6b43a2343ff46e897`, **13,095 rows**. Our **strict internal admission predicate** admitted 13,056; flagged **39** (8 `INVALID_SOURCE`, 31 `INVALID_TARGET_MARKER`), with 11,833 valid rows satisfying existing strict L1 source script policy, 2,129 distinct target kanji among admitted. This is a count of **strict predicate acceptance**, NOT external dataset error proof. Original combined workflow failed on these 39; that failure must remain visible.

## Amendment
C0 distinguishes three statements that are not equivalent:
1. The publisher's claimed 13,095 human-verified kanji reading rows.
2. Our parser's admitted 13,056 rows and 39 **NEEDS_RECONCILIATION** under the *restricted* internal convention.
3. A independently adjudicated set of usable target/whole-utterance references suitable for true language science. #244 has not frozen this.

`INVALID_DATASET` status semantically overstates the evidence when 39 rows might be legal variant marks, unusual legitimate orthography or mismatched acceptance rules. New status for recognized JSONL with row-level failures: **`RECONCILIATION_REQUIRED`** (no H1–H4 inference). Error categories remain raw diagnostics, not accusations. Strict code continues refusing unadmitted rows for predictive testing; no silent drop or rescore.

## Test-first software changes
- AR01 fixture with duplicate key and unaccepted target marker now returns `RECONCILIATION_REQUIRED` but identical count/reason and file SHA; no `AUDITED` false green.
- AR02 all-valid 3-row fixture remains `AUDITED`.
- AR03 no scores, no original source positions or full-sentence acceptable readings inferred, even for admitted rows.
- AR04 dataset SHA mismatch rejects; symlink/oversize/invalid UTF8 continue fail-closed.
- AR05 **independent workflow job statuses:** actual B0 execution can be green despite corpus admission red; corpus admission remains failure with full diagnostics. No green top-level claim for scientific Gate C. The original combined failing workflow preserved as historical.
- Optional diagnostic triage may print flagged **keys and failure categories**, NOT inject reference values into any model or mutate the dataset. Collecting keys is validation only, not quality evidence.
- No modification to original H1/H2/H3/H4, sample counts, model comparison, Core/Studio/SMC5/6 or main. Any later tolerance threshold requires a separate preregistered experiment, not tuning C0 until it passes.
