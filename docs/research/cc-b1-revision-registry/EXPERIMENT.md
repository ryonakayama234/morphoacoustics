# EXPERIMENT — preregistration / risk ledger (before implementation)

Hypothesis H-REG1: with exactly the fixed M0/r1 parent, site08 ratio `0.90` or `1.10`, a **verified real physical archive** yields a deterministic canonical BodyRevision registry entry that is still byte-identical and re-derivable after an entirely fresh Python process reload. Tampering with either stored identity or its data fields fails closed, and duplicates never overwrite.

| Case (planned before code) | Expected | Result |
|---|---|---|
| Two real v1 CLI 48kHz×24000Pa archives (0.90,1.10), one registered each | EXACT_MATCH on restart; distinct revision IDs | NOT_RUN |
| Identical archive re-register; separate genuine Take same revision | ALREADY_REGISTERED, same canonical bytes | NOT_RUN |
| Wrong/nonexistent id or archive missing marker | non-success and no new file | NOT_RUN |
| Record ID/hash/parent/edit/backend/area tamper; even after recomputing storage hash | REVISION_MISMATCH; no reconstructed body from claims | NOT_RUN |
| Extra/duplicate keys, nonfinite data, oversized record, linked registry entry | INVALID; fail-closed | NOT_RUN |
| Existing different bytes at same derived ID | COLLISION/REFUSAL; no overwrite | NOT_RUN |
| Concurrent identical registration | exclusive one winner or exactly one identical idempotent outcome; no partial success | NOT_RUN |
| Process failure mid-publish, disk full, symlink swap / directory hostile mutation | no success; explicit residual risk | NOT_TESTED |
| Python 3.11–3.13, exact HEAD Core tests, OG3/OG4/SV1 and existing v0/v1 CC-A2 | unchanged | NOT_RUN |
| ABX audibility, voice identity, quality, FSI, arbitrary organ graph, Studio UX | outside this Gate | NOT_TESTED |

The numerical Wolfram Gate B and 16-section source physics are **inherited and unchanged**; no new physical law or acoustic oracle is introduced. Existing documented [CLI Gate C records](../cc-b1-cli-gate-c/EXPERIMENT.md) and its artifact proof are prerequisites. Do not turn previous narrow numerical success into perceptual evidence.

Adoption conditions beyond this module: independent critical storage/security audit, exact-head CI with downloadable real audio+registry artifacts, documented limits/risk owner, controlled durable store and follow-on Studio Gate D. A later decision must be `CORE_GO_LIMITED`, `REVISE`, `MORE_DATA`, or `REJECT`, not inferred from author CI alone.

## Executed sequence — evidence after the original preregistration

1. **Initial PR #166 HEAD `8ab0d6cf427f376a06044a03200f813beebeb121`:** dedicated physical/negative/legacy CI [#39794398688](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39794398688) **SUCCESS** (17 new registry tests, genuine 2× 48kHz/24000Pa archives, isolated 0.90/1.10 registered and freshly process-resolved); authentic archive + immutable identity artifact [#12431789640](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39794398688/artifacts/12431789640). OG3/OG4/SV1 SUCCESS. The **general `tests` workflow #39794398680 FAILED** on Python 3.12: dependency resolver installed NumPy 2.5.4 instead of frozen 2.4.6, triggering 16 intentional scientific replay dependency refusals; 784 other tests passed and 13 skipped. This failure is kept as observed; neither physical simulation nor geometry changed to make it pass.
2. **Pinned test matrix HEAD `4a427cef22c23cafd35f8b3d573cd92e498cadc8`:** `.github/workflows/tests.yml` pins and asserts NumPy `2.4.6` after editable project install, as required by fixed Experiment/Gate B numerical oracle. Exact-HEAD Actions [#39894060781](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39894060781) Python 3.11/3.12/3.13 + mypy **SUCCESS**, registry dedicated and OG3/OG4/SV1 also **SUCCESS**. This validates the fixed numeric dependency only; *not* all future NumPy versions.
3. **Critical A2 storage audit found a publication gap:** first implementation used `O_EXCL` to write directly into final revision filename. Concurrent readers/crash could see a partial stable-name record. Repair HEAD `a154e0163771d0c04f180f148fe972473d8c921d` switches to fully fsynced random staging inode, atomic same-directory no-overwrite hard-link, stage removal, directory fsync and full reread; fail-closed orphan stage possible after power loss. Added negative fault-injection tests at HEAD `fcafe8fd05e263dbfc7b36d4c3841dfde7c0ccbc` for link refusal, fsync refusal, two concurrent register calls. **These are not retrospectively passed at earlier HEADs.** Verify exact latest SHA before any new PASS declaration.
4. **Independent Wolfram kernel, 2026-10-23:** [`wolfram_registry_geometry.wl`](wolfram_registry_geometry.wl) result verifies `16×10mm=0.16m`, zero-based site8 alone changes, rest-area edit ratio 9/10 or 11/10, positive edited area given positive baseline; delta rest volume ± A_site08 / 1000 [m³ if area m²]. Independent canonical UTF-8 fixture of 146 bytes produces SHA256 `c461f5f2b9d270562a37ae743f163fd8d0ae4c90fe2110d9947f5e889a0e3625`, equal to a separate Python standard-library calculation. This is **static symbolic/rest-geometry and hash-format sanity**, NOT Core 16-section numerical 1D solver reproduction, physical auditory effect, authenticated source origin or durability proof.

**Unresolved:** concurrent hostile same-UID mutations, ancestor symlink path components, Unix kill -9 / disk full power-loss recovery, Windows-host/remote FS, code signing/source authenticity and independent human security review are NOT_TESTED. Keep Draft, no main merge, no Studio Gate D/E, no false claim of linguistic naturalness or full-body voice range.
