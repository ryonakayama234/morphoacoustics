# BODY-B1 P1 — Core closed OD-2 catalog protocol candidate

**Protocol:** `od2.b1.core-catalog-receipt/1`  
**Catalog:** `od2-b1-core-closed-catalog/1`  
**Status:** **CANDIDATE_UNADOPTED** — P1 code/review evidence only. **No formal Core pin / no Studio / no Take / no v1 change / no quality claim.**  
**Authorization:** [Owner GO Studio #54 comment 6766594718](https://github.com/ryonakayama234/morphoacoustics-studio/issues/54#issuecomment-6766594718). **Audit anchor:** [Muse P0 acceptance comment 6766562565](https://github.com/ryonakayama234/morphoacoustics-studio/issues/54#issuecomment-6766562565), captured in [P0 ledger](P0_AUDIT_CAPTURE_20261110.md).

## Core authority and exactly supported operations

`tools/od2_b1_catalog.py` is a **thin strict candidate product-release boundary** over the already reviewed `tools/od2_body_cli.py`. It does not duplicate physical preparation, revision identity, registry, acoustic implementation, source or task. It asks OD-2 for the six source-pinned `_receipt` results, which prepare nonnull bodies via the current `BodyPresetRegistry`. It accepts only:

- `parent=v3b-axial-M0@1`; `family=tract1d.local-log-area-5.v1`; `backend=fidelity0.tract1d` from Core;
- zero-based center `4` or `8` and exact text ratio `"0.90"`, `"1.00"` or `"1.10"`;
- four distinct nonnull revision IDs recorded in P0; two `1.00` cases are **two requests to the same M0 physical parent**, not minted revisions;
- one inherited sixteen-section 0.160m geometry, only five changed areas for nonnull cases, no changed length, fixed source `lf_fixed` and inherited task.

The versioned immutable JSON `contracts/body/od2-b1/catalog-v1.json` is a *closed authorization list*, not a mutable body database or free-form recipe generator. Its full content is checked against the code-anchored fixed six-case ledger, and each authorized entry is re-derived with OD-2's pinned physics source. The P0 comment published full revision IDs but only short prefixes for two prepared digests; their exact values are recomputed, never guessed or mistaken for a complete SHA.

The legacy OD-2 research protocol `od2.local.revision-replay.v0-research` remains unchanged. This candidate bridge does not extend the existing v1 performance request API; whether it can later carry derived bodies losslessly on v1 is still a **P2 proof obligation**.

## CLI calls (from an exact clean Core checkout)

```bash
python tools/od2_b1_catalog.py catalog
python tools/od2_b1_catalog.py derive --center 4 --ratio 1.10
python tools/od2_b1_catalog.py issue --center 4 --ratio 1.10 --output /tmp/od2-b1-c4-r110.json
python tools/od2_b1_catalog.py resolve --receipt /tmp/od2-b1-c4-r110.json --revision-id od2-7c2663189d907111665544c67def56c885576f5394e4220ec12251e0ca5ebf67

# Inherited six-case real physical study archive, NOT a Studio Take:
python tools/od2_body_cli.py perform-suite --output-dir /tmp/od2-b1-research-evidence
python tools/od2_b1_catalog.py verify-archive --archive /tmp/od2-b1-research-evidence
```

A success receipt contains: `schema`, `catalog_version`, `catalog_manifest_sha256`, `candidate_core_head` (actual clean checked-out SHA, **never hard-coded to 01b2a337**), `core_pin_status=CANDIDATE_UNADOPTED`, audited source blob pins, Python/NumPy environment, source ID, **host-recomputed** float64 source SHA (explicitly NOT an actual performer source attestation), task-plan SHA, and the **complete OD-2 Core body receipt** (parent, exact revision and prepared digest, family/algorithm, center/ratio, backend, 16 SI float.hex areas and lengths; nonnull recipe).

**Persistence/readback:** `issue` writes an exclusively created non-overwritable JSON file with `O_EXCL` / `O_NOFOLLOW` where available. `resolve` runs in a new process if desired, parses strict JSON (duplicate keys and nonfinite values denied), checks exact requested revision, clean Core HEAD, manifest and all resolved physical/revision fields against a **fresh** Core derivation. Any wrong/truncated/changed old-pin receipt is refused. It does not resolve a symbolic `latest`, use only the supplied ID, or produce audio. Null alias `revision_id` alone is insufficient: its original center/ratio and full receipt must also agree. **No generic mutable registry is introduced.**

**Rejected response:** `{"schema":"od2.b1.core-catalog-receipt/1","status":"REFUSED","code":"...","message":"..."}` with exit code 2. The underlying OD-2 `RevisionError` codes remain specific, and generic operational errors refuse; no false `SUCCEEDED` / credible audio artifact is returned.

## Gate evidence: what to audit at the *actual PR head*

| Required proof | Mechanism | Scope of acceptance |
| --- | --- | --- |
| Four revisions + two aliases | Catalog test cross-checks P0 fixed IDs; Core re-derives all six, verifies preparation anchors and parent | No unsupported edit |
| Parent and exact geometry | Frozen source hashes, `BodyPresetRegistry`, full `float.hex` areas/lengths, 5-cell/nonlocal/null tests, inherited OD-1/OD-2 geometry/oracle | Mathematical 1D body, not anatomical validation |
| Restart and immutable readback | Separate Python subprocess tests for nonnull and null; exclusive file creation; exact-receipt structural equality and full re-derivation | Exact Core HEAD only |
| Refusals / tampering | Wrong center/ratio, forged ID/digest/shape/backend/source/task/pin, unexpected and duplicate fields, symlink, changed catalog, dirty checkout | Fail closed; no audio |
| Inherited real source and acoustic physics | Explicit `OD2_REAL_PHYSICS=1`, existing direct replay & coordinated adversarial waveform tests; re-execute full 48k/24000 Pa; independent loaded oracle | Same pinned model only |
| G0 / OD2 / CC-A2 regression | Exact PR head checkout; frozen NumPy 2.4.6; whole Python test suite, dedicated OD-1/OD-2/CC-A2 tests, physical CC-A2 opt-in | Existing physical model not modified |
| Durable receipt | Versioned JSON, trusted source inventory, exact clean candidate head and artifact uploaded from Actions | Candidate provenance, not adopted pin |

Workflow: [`.github/workflows/body-b1-p1-core-catalog.yml`](../../../.github/workflows/body-b1-p1-core-catalog.yml). The job checks out `github.event.pull_request.head.sha`, **not GitHub's synthetic merge commit**. The captured head, runtime, full catalog and separate-process readback become a reviewable evidence artifact. Its success, failures and exact run ID are **not assumed** until Actions actually completes; Muse must inspect the submitted P1 head and independently sign off.

Original OD-2 shape thresholds remain fixed (log-area ≤ 1e-12; volume relative ≤ 1e-12; timed area ≤ 1e-10; loaded complex transfer ≤ 1e-9). For acoustic archive, the existing verifier freshly reexecutes all six model-native Pa waveforms and requires same-runtime relative replay L2 ≤ 1e-12, source/task pins and M0 quantized oracle; it rejects the coordinated `2*p_null - p_variant` adversarial forgery despite consistent SHA updates. These are inherited tests; no new audio quality or human perception inference follows.

## Separation of decisions and rollback

No Studio code or archived Take changes occur. Legacy b569 Takes are not reclassified or migrated; Studio historical queries remain P2/P3 obligations. This PR should remain **Draft/unmerged** for Muse acceptance and separate Owner merge decision; a green CI is not acceptance. To roll back before merge, discard this branch; it changes neither persisted user artifacts nor existing Core physics. The original OD-2 research CLI remains usable.

**Blocking conditions:** Candidate head mismatch; nonclean checkout; P0 ID or digest anchor mismatch; M0 alias not parent; 5-cell or loaded oracle failure; changed source pins; missing/modified receipt or physical archive; failed negative or CC-A2 regression. Any claim requiring v1 schema reinterpretation is a **STOP for separate v2 design GO**. Formal product pin approval, Studio migration, complete source provenance and audio-quality acceptance are explicitly outside P1.

## Source-bit portability qualification (P1 exact-head review)

The original OD-2 final research Actions [run 41324965684](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41324965684) (Python 3.11.17, NumPy 2.4.6) reported recomputed `lf_fixed` f64 bytes SHA `4d075fd89958ff481507661ea43e4602ed5fe72b0104bc897685b1f696abf529`. The first successful P1 Actions [run 42813320779](https://github.com/ryonakayama234/morphoacoustics/actions/runs/42813320779) (Python 3.11.18, NumPy 2.4.6) reported `724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc`; its task-plan SHA and within-model L2 remained consistent with frozen references. The mechanism for raw-bit difference has **not been independently established**; numerical library, math backend or runner changes are possibilities, not adopted causal explanations. The new candidate protocol records the freshly recomputed raw f64 SHA *and exact runtime* but does not claim portable raw-bit equivalence or Studio actual-run source verification. The P1 physical gate uses the original preregistered same-runtime waveform tolerance and quantized M0 oracle. A new source-code/identity or scientific oracle mismatch remains a STOP. Muse should decide whether the observed source-bit mismatch needs additional root-cause inquiry **before formal product pin adoption**.
