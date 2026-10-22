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
