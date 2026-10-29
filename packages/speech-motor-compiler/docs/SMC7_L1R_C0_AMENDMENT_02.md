# SMC-7 L1-R C0 — security review amendment 02 (P2×4)

**2026-10-29 JST | Owner #245 / PR #246 | independent Codex initial review at workflow/code SHA `323bb60eaecc7e8fc1ef1778673e10d7e0c8a75a` | preregister BEFORE adversarial tests and repair.**

## History preserved
- Original C0 code SHA `53c0e1bd1323a100fb5859a78ea03dd256436170`, 16/16 inherited checks green. Real workflow SHA `323bb60` ran genuine pyopenjtalk, recorded original dictionary hash `88167f04755fe6f0973f5be05bf839aad53d600e190d7068b29d7af15c594dbd`, `ニンキノナイバショ` and dataset 39 admission discrepancies. This original SHA is **REVISE_P2_4**, not an accepted software/security implementation.
- Review findings:
  - [P2 cached engine/user dictionary](https://github.com/ryonakayama234/morphoacoustics/pull/246): global `_global_jtalk` can remain bound to changed/externally supplied dictionary even if `OPEN_JTALK_DICT_DIR` equals a claimed path.
  - [P2 symlink substitution](https://github.com/ryonakayama234/morphoacoustics/pull/246): old path-stat then Path.open race follows a forged link.
  - [P2 unbounded traversal](https://github.com/ryonakayama234/morphoacoustics/pull/246): `sorted(root.rglob("*"))` scans entire attacker-supplied tree before count limits; subdirectories are not counted.
  - [P2 invalid kanji key](https://github.com/ryonakayama234/morphoacoustics/pull/246): target `あ__0` could be admitted because target not checked as one CJK base kanji, reading key field allowed empty.

## Normative repair
1. A real G2P execution MUST create its own new **`OpenJTalk(dn_mecab=<private verified snapshot>, userdic=b"")`** rather than `pyopenjtalk.g2p()` using the mutable cached global engine. The temporary snapshot's file bytes and relative names are hashed, then this exact private tree is passed to the engine. Never rely on mutable module `OPEN_JTALK_DICT_DIR` as attestation. Explicit user dictionary is absent and must remain absent.
2. Secure snapshot/hash traversal: open source directory with no-follow flags; bound directory **and** file entries, depth <=8, <=512 total entries and <=512MiB file bytes before sorting the bounded file list. Every file opened with `O_NOFOLLOW` (and parent directories through file-descriptor-relative no-follow opens), verify regular fstat/inode/size before/after stream; read/copy bytes in chunks; throw `DICTIONARY_UNVERIFIED` on substitutions or unsafe platforms. The private newly created snapshot directory is owner-only. Fingerprint the bytes actually handed to the engine, not the directory name. A concurrent writer able to change source input before copy has no access to the private snapshot; changes after copy do not change this engine.
3. Joyo key `<one basic CJK U+4E00..9FFF>_<nonempty Japanese kana reading>_<decimal index>`; do **not** require marked pronunciation segment to equal its key (the dataset demonstrates legitimate orthographic/phonetic notational mismatches). Incompatible keys remain `RECONCILIATION_REQUIRED` rather than silently admitted, without calling whole dataset invalid.
4. Preserve baseline fixture `FIXTURE_ONLY`; actual runtime `PYOPENJTALK_REAL` only after the exact private engine executed successfully, with version `0.4.1`. No G2P-to-L0 source offsets, automatic SMC selection or Core/Studio modifications.
5. Record actual test-only RED before source, exact code-bearing GREEN, new Codex review and inspect re-run real provider/dictionary digest. Old SHA cannot inherit new trust verdict.

## Frozen new falsifiers before code
- S01 spy on `pyopenjtalk.g2p` global callable to raise, while a fake `OpenJTalk` constructed from provided snapshot succeeds; tests prove the global path never executes and explicit `userdic=b""`.
- S02 simulate source file symlink substitution after scan but before open; hash/snapshot fails without opening external file.
- S03 513 empty directory entries (and deep >8 directory tree) fail immediately with `DICTIONARY_LIMIT`; no full traversal of millions of entries.
- S04 original dictionary bytes and filename modifications deterministically change fingerprint, no symlinks/empty/invalid origin.
- S05 `key="あ__0"` or `key="甲__0"` rejected as `RECONCILIATION_REQUIRED` and not included in distinct target kanji; genuine `固_かためる_0` remains accepted.
- S06 same pinned package through actual CI with real private engine and verified snapshot hash, no unpinned user dictionary; independent re-review exact code SHA and inherited root/isolated SV1 checks.

All these are **software properties**; they neither establish the full Japanese 880-item experiment nor correct pronunciation.
