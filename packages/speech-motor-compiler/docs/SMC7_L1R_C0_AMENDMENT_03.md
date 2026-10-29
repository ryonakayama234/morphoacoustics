# SMC-7 L1-R C0 — security review amendment 03 (second independent P2×4)

**2026-10-29 JST | Owner #245 / Draft #246 | review source SHA `9b898152a492e0b57de0509d82b4eade0b6c39ee` | FROZEN BEFORE NEW TESTS / CODE**

## Historical source
Latest exact code SHA had 17/18 GitHub checks success, with the only red job the intentionally isolated Joyo 39-case corpus reconciliation gate. Real private-snapshot B0 executed successfully at [job 123360961050](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40848244585/job/123360961050). Do NOT call this exact SHA accepted software because Codex second review found four new P2. Original first four P2 and all REDs/repairs remain historically preserved in C0 RESULTS.

## Newly independently reported review defects
1. **External user dictionary despite private snapshot:** if snapshotted `dicrc` has active `userdic=...`, MeCab can load external dictionary despite `OpenJTalk(... userdic=b"")`. Source must refuse unsafe active `userdic` directives before engine constructor; no path escaping private snapshots.
2. **Embedded NUL in source:** C backend's `strlen` parses only a prefix of `甲\u0000乙`, while Python source hash covers all. Reject NUL before invoking native code in both fixture and real path; disallow source/C-string aliasing.
3. **FIFO swap before leaf open:** O_NOFOLLOW blocks symlinks but O_RDONLY can block on a substituted FIFO. Add O_NONBLOCK to descriptor-relative leaf opens, then fstat regular and inode identity before reading.
4. **Unbounded corpus read after check:** `Path.read_bytes()` reopens caller-controlled path after symlink/size check, permitting symlink swap and unbounded growth. Use `os.open(O_RDONLY|O_NOFOLLOW|O_NONBLOCK)`, immediate fstat regular + finite size gate, bounded `os.read` <=8MiB+1, fstat after read; reject symlink/special/writer growth, preserve unchanged exact corpus SHA.

## Frozen falsifiers (test-only RED first)
- R201 `read_b0("甲\u0000乙", ...,fixture_reader=spy)` returns `REFUSED/INVALID_SOURCE` and never invokes reader; no native C-string truncation.
- R202 a local tree containing `dicrc` with active `userdic = /tmp/outside-user.dic` rejects prior to constructed real engine, including installed-version stub. Comments such as `# userdic = ...` do not falsely reject.
- R203 a FIFO substituted at leaf after secure inventory triggers a controlled refusal without blocking the process (test uses a monkeypatched `os.open` to assert O_NONBLOCK before replacing). All unknown special files denied.
- R204 corpus JSONL symlink substitution immediately before open raises `INVALID_DATASET_PATH` and never ingests the outside JSONL; corpus FIFO/special paths reject; a file growing over the 8MiB budget after stat cannot allocate beyond `_MAX_CORPUS_BYTES+1`.
- R205 existing real B0 0.4.1 fixture and actual CI must retain exact dictionary bytes digest, no global OpenJTalk cache or user dict, and corpus admission 39 remains `RECONCILIATION_REQUIRED` (not green by suppressing cases). Strict mypy 3.11–3.13, package/root/SV1 CI and independent exact-head re-review.

**STOP / REVISE** on any source-prefix alias, unbounded read/timeout, hidden dictionary dependencies. **NOT** H1–H4 linguistic GO; no main merge, Core, Studio, SM C-4/5/6 or stable API changes.
