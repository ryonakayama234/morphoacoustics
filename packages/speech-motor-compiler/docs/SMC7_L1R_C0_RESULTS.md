# SMC-7 L1-R C0 — actual Gate B / preliminary accession results

**2026-10-29 JST | research owner #245 | Draft #246 | no main merge | parent #242, #243, and corpus #244.** This file is a chronological evidence ledger; never retroactively turn failures into passes.

## 1. Method and observed first RED
- Frozen [C0 protocol](SMC7_L1R_C0_PROTOCOL.md) committed before source/test at **`b1c88e3c334ec8b80ee119ecb83d2697895f8f6d`**. Target: real installed G2P **text-only**, dictionary fingerprint and independent kanji benchmark intake, explicitly **NOT** the held-out 880-case linguistic evaluation.
- Test-only commit **`838b01f895c704cbc1196bbdd52a48e7147e3247`**; GitHub isolated Python 3.12 test collection actually failed with `ModuleNotFoundError: morphoacoustics_smc.l1r_real_g2p` ([workflow 40846237491](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40846237491)). This is a genuine RED.
- First source **`ca8c755ad2d150184e9a56bb0a76527c4be9e1a9`** then concrete OS Path subclass repair **`6ba78f5a983e01de08a183f14f84ac763f9c747d`**. The latter exposed **three real failures** in isolated Python 3.11 CI on corpus PosixPath admission ([job 123355345901](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40846551954/job/123355345901)); fixed in **`53c0e1bd1323a100fb5859a78ea03dd256436170`**. A deterministic installed-version negative fixture improved at **`0d105355ce3214f9c4ef7b4d3cd38941dcb5a221`** (test only); no external model trained.
- At first software candidate SHA `53c0e1b` inherited CI **16/16 success**. This did NOT mean exact dictionary execution trusted because Codex then found independent P2 flaws.

## 2. Actual first live provider + corpus audit observed
- Original combined isolated workflow code SHA **`323bb60eaecc7e8fc1ef1778673e10d7e0c8a75a`**, [GitHub Actions run 40846865407](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40846865407), Linux Python 3.11.17:
  - `pyopenjtalk==0.4.1` actually imported, dictionary release `open_jtalk_dic_utf_8-1.11` automatically downloaded by the upstream library on first init, active dictionary bytes fingerprint `88167f04755fe6f0973f5be05bf839aad53d600e190d7068b29d7af15c594dbd`.
  - Actual sample `人気のない場所` -> `ニンキノナイバショ`, status `READ`, mode `PYOPENJTALK_REAL`. This is one observed **library output**, not an independent correct reading or context benefit. No IPA/accent/timing/physics.
  - Exact original Joyo benchmark revision `2ae383bcdac88dacf89c9ab84f9990eec55fe5c9`, file `common_kanji_source.jsonl`, actual downloaded SHA-256 **`32a843f662c55f1876baf64f8dc3475cc7b777c576a8fea6b43a2343ff46e897`**; 13,095 rows. Strict parser admitted 13,056, flagged 8 `INVALID_SOURCE` and 31 `INVALID_TARGET_MARKER` = **39 require manual reconciliation**. In admitted rows, 11,833 fit the current restrictive L1 script repertoire; 2,129 target characters distinct. This is **compatibility of our admission convention** only, not proof the publisher's annotations are defective, not H1/H2.
  - Original combined job **FAILURE** because the explicit all-rows audit admission predicate is not satisfied. Preserve failure, don't report all-green.

## 3. Data-admission terminology correction and job isolation
- [Amendment 01](SMC7_L1R_C0_AMENDMENT_01.md) `09ee76ece0031196c2ebb656d8cf00733c132edf` frozen before tests and code.
- Test-only **`efe8043d33833faebd33b6c8ba91ce3bafaab553`**: actual isolated Python 3.12 RED expected `RECONCILIATION_REQUIRED` vs observed old `INVALID_DATASET`, [job 123358372271](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40847462619/job/123358372271).
- Source repair `8d48d43501269f0c975ed4eb51b920a661658d36`: rejects row admission but uses neutral **`RECONCILIATION_REQUIRED`**, never automatically omits suspect rows. Public benchmark cannot satisfy complete whole-utterance acceptable multi-gold references merely from marked target kanji.
- CI workflow split at `c1d6c05a5ccc64f736e72224f8a2249e4aa0c2af`: independent actual G2P job and *separately failing* data reconciliation job, plus fixed raw dataset content SHA. No accuracy computation on Joyo held-out examples.

## 4. Independent Codex security review — four P2 and repaired exact code
First independent Codex review of `323bb60` reported **four** P2: global cached OpenJTalk/userdic could bypass claimed dictionary identity, symlink swap between stat and open, unbounded sort/rglob tree traversal despite file cap, and non-kanji/empty key reading accepted. The first version therefore had disposition **REVISE_P2_4**, regardless of its main CI success.

- [Amendment 02](SMC7_L1R_C0_AMENDMENT_02.md) **`7263f4cc81aa4bcf4928811dac9f14f5ddcc4a5b`** written before tests/source.
- Test-only **`08d046581533b73e33dcb9928d2c4f2546b35a9f`**; GitHub isolated Python 3.11 [job 123359995906](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40847954226/job/123359995906) observed genuine failures: cached-engine path, symlink swap, unbounded directory entry/depth, malformed target key. Old results preserved.
- Source **`53ffdf1d96ce0f0dd9c52524c20a4ee19d26dae7`** introduced descriptor-relative `O_NOFOLLOW`, bounded 512 total entries and eight levels, stat/identity verified file-byte reads, private snapshot and **new** `OpenJTalk(dn_mecab=<exact snapshot>, userdic=b"")` (no global cache); strict one-kanji nonempty key.
- Follow-up input-contract defect at above source: missing dictionary path leaked FileNotFoundError rather than required controlled ValueError, observed isolated 3.11/3.13 CI. Fixed at frozen **code-bearing SHA `9b898152a492e0b57de0509d82b4eade0b6c39ee`**. The change re-adds missing-dir gate before os.open; not a data-quality adjustment.

## 5. Exact repaired source CI and actual provider replay
At **`9b898152a492e0b57de0509d82b4eade0b6c39ee`** [full check suite](https://github.com/ryonakayama234/morphoacoustics/pull/246/checks): **17/18 GitHub checks success**, the **sole failure** is intentionally separate `independent-Joyo-reconciliation-gate` because 39 source/marker predicate incompatibilities remain. All package tests Python 3.11/3.12/3.13, root tests Python 3.11/3.12/3.13, mypy and bounded SV1 passed. *No claim of 18/18 success.*

Separate [real G2P job 123360961050](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40848244585/job/123360961050) **SUCCESS** on same exact code SHA, now with the private source-dictionary snapshot and no user dictionary. The real fingerprint remained **`88167f04755fe6f0973f5be05bf839aad53d600e190d7068b29d7af15c594dbd`** and actual `人気のない場所` reading remained `ニンキノナイバショ`, mode `PYOPENJTALK_REAL`, version 0.4.1. The identical digest refers to a deterministic hash algorithm over the same original bytes; *new software changes what the engine actually reads*, not the source bytes. Input/source SHA `cd9569c654b13689d55dce177fe8272901a1cb0123e50cc25ce34043ecab8eac`.

As of this ledger creation the independent **exact repaired SHA Codex re-review is REQUESTED/PENDING**. No final software security gate claim before its result.

## 6. Claim limits and unresolved work
- **Measured:** actual optional external `pyopenjtalk==0.4.1` call (not mocks), verified content-bound dictionary snapshot (software semantics), one sample output, external file byte hash, schema admission counts, preserved RED/green code regression.
- **Not measured:** B0 full-corpus baseline target accuracy or sentence CER; B1/C/C-mask context challenger; original H1–H4 target reading accuracy and confidence intervals; 880 independently annotated held-out utterances or 120 pilot; label correctness; model training-data leakage; independent corpus rights attestation beyond publisher MIT metadata.
- **Blocked:** Gate C linguistic evaluation while the 39 rows need independent reconciliation and the original multi-gold 880/full sentence span corpus is missing. Do not train on or cherry-pick these external evaluation references.
- **Non-goals maintained:** no SMC4/5/6 source change, no newly authorized source offset/token alignment, no TaskLexicon/physical organ mapping, Core sound, Studio UI, main merge or public ABI.

Reference: owner #245, corpus #244, original H1–H4 protocol `SMC7_L1R_GATE_A_PROTOCOL.md`.

## 7. Third independent Codex review — further P2×4, another test-first repair (2026-10-29)
Second Codex exact-SHA review at `9b898152a492e0b57de0509d82b4eade0b6c39ee` completed with **four additional P2** and `REVISE`:
- Cached external user dictionary can still be loaded through an active `userdic` directive in snapshotted `dicrc`, even when `OpenJTalk(...,userdic=b"")`. Snapshot must reject external configuration.
- NUL in source can truncate upstream C parser at `strlen`, misrepresenting a prefix as full original text.
- POSIX FIFO leaf replacement can block before fstat when opening O_RDONLY without O_NONBLOCK.
- Corpus `Path.read_bytes` follows newly swapped symlink after initial stat or reads unbounded bytes if file grows.

[Amendment 03](SMC7_L1R_C0_AMENDMENT_03.md) committed **`9cff1e5b9a7d8ec64be7a58e7bb5a55ca861347d` BEFORE regression tests/source**. Test-only commit **`1cefe748d3ed4151e5f396334511949fb1e335a9`** and revised stricter FIFO test-only **`c116b02ab7367db211bbafedc70278fd3e9c440a`**: GitHub isolated 3.11 actual [job 123364658491](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40849353772/job/123364658491) observed NUL false acceptance, external `dicrc` userdic not refused, missing O_NONBLOCK and corpus symlink re-open bypass. This RED is historical and not a current failure claim.

Minimal repaired code **`5087bd5775a148655188df9918d6faaff6a8ea4a`**:
- rejects NUL before native provider invocation;
- hashes `dicrc` as part of bounded source tree then refuses active `userdic` directives before engine construction (no user dictionary silently loaded);
- opens all dictionary leaves with `O_NOFOLLOW|O_NONBLOCK` then checks regular inode, identity, size and mtime;
- opens corpus via `O_NOFOLLOW|O_NONBLOCK`, immediate `fstat`, reads at most 8MiB + 1 bytes and checks descriptor metadata after read. No new source-offset authority or automatic SMC transition.

**Actual exact code SHA `5087bd5775a148655188df9918d6faaff6a8ea4a` GitHub checks: 17/18 success; isolated Joyo reconciliation gate the sole deliberate FAILURE.** Independent actual [real B0 job 123365200272](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40849518746/job/123365200272) succeeded under this revised code. Pin `pyopenjtalk==0.4.1`, Python 3.11.17 Linux; same actual private dictionary bytes identity `88167f04755fe6f0973f5be05bf839aad53d600e190d7068b29d7af15c594dbd`; real `人気のない場所` -> `ニンキノナイバショ`; mode `PYOPENJTALK_REAL`. This is **one real execution**, not a reading-correctness judgment. Data audit remains **`RECONCILIATION_REQUIRED` 39/13,095**; no thresholds changed.

**Independent exact-source Codex re-review at `5087bd5` requested** after these fixes. This ledger states the status at the time of commit; a separate Decision document must refer to the later completed review outcome before accepting software safety claims.

## 8. Third exact-code independent review completed — software-only decision

At code-bearing SHA **`5087bd5775a148655188df9918d6faaff6a8ea4a`**, third independent Codex PR review **completed** with **`has_any_findings=false`** and **`has_unresolved_findings=false`**. All eight historical P2 review threads from two previous rounds were replied to with the frozen test-only RED/fix SHA chain and marked resolved in PR #246; original comments and observed failure history remain public.

The exact-code 18 GitHub checks were **17 passed, 1 failed**, with the **one failure the independent Joyo strict-format reconciliation gate**, correctly refusing to ignore 39/13,095 flagged rows. Package/root Python 3.11–3.13, mypy, SV1 and genuine pinned private-engine B0 all passed. The real C0-only research gate therefore has **`GO_LIMITED_C0_REAL_B0_EXECUTED`**, not all-green and not H1–H4; data and independent whole-utterance Japanese reading study remain **`MORE_DATA`** under #244/#247. See [C0 DECISIONS](SMC7_L1R_C0_DECISIONS.md). No user approval of main merge/public ABI/Studio/Core was sought or implied.
