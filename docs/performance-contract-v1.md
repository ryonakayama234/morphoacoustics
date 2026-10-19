# Performance Contract v1 — exact selectable embodiment (CC-A1)

**Status: DRAFT, not published/adopted; not an audio or physics capability.**

Studio X2a is separately adopted on main (Studio PR #15, 2026-10-19). This v1 contract is NOT consumed by the existing fixed-body X2a backend. Implementation PR and tests are independently gated under [Core #72](https://github.com/ryonakayama234/morphoacoustics/issues/72). Upstream Body Binding v0 and Performance Contract v0 remain unchanged.

## Formal composition and ownership

```mermaid
flowchart LR
 R["Request v1\nCharacter/Script/Direction v0 snapshots +\nexact BodySelection"] --> V["Core schema and\nsemantic validator"]
 V --> G["BodyPresetRegistry\nexact ID+revision"]
 G --> P["PreparedMorphology\nbackend ID+digest"]
 P --> O["Result v1\nstatus+resolved embodiment"]
```

- **v1 envelope, v0 creative snapshots.** Top-level `schema_version` is `performance-contract/v1`; embedded `CharacterSpec`, `Script` and `Direction` remain *exact, independent, unchanged* `performance-contract/v0` snapshots referenced via JSON Schema. This avoids duplicating or silently redefining creator-facing semantics. A future version may separately upgrade creative snapshots.
- Request `embodiment = {preset_id, preset_revision}`, exact revision integer `>=1`; never `latest`, no physical geometry or pressure in creator fields.
- Resolution `embodiment.status` is `BOUND`, `MISSING_PRESET`, `REVISION_MISMATCH` or `UNSUPPORTED_BACKEND`. When and only when `BOUND`, result stores exact `preset_id`, `preset_revision`, `backend_id`, `preparation_digest` (actual Core body binding). Status is *not* job lifecycle or physical realization; `job_status=SUCCEEDED` and `realization_outcome=INFEASIBLE` remain valid for a body that **was** successfully bound.
- v1 request+result JSON Schemas are under `contracts/performance/v1`, Draft 2020-12; v0 files are untouched. The source helper `contracts/performance/v1/semantic_validation.py` only resolves exact prevalidated Core presets, never synthesizes a body, waveform, or approximate fallback.
- The v1 fixture uses illustrative `sha256` values and `UNSUPPORTED` with no audio: **not** a claim that a validated live two-body adapter exists or was executed.

## Digest and historical Takes

`input_digest_algorithm=sha256-canonical-json-v1`: SHA-256 over `json.dumps({request: <full validated v1 request>, backend_id: <exact backend>, backend_version: <exact version>}, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)`, UTF-8 encoding. All input snapshots, seed, exact body revision and adapter identity are included. Canonicalization handles JSON types as encoded (it does not normalize 1 vs 1.0); request serialization is included in the contract. This digest describes request+adapter input, **not** prepared physical state.

### Cross-language digest authority

**The trusted Core-side Python adapter is the sole issuer of `input_digest` for `sha256-canonical-json-v1`.** Studio must consume that version-tagged value as opaque evidence, not calculate it from the browser request and assert equality. Python `json.dumps` distinguishes numerical spellings such as `1.0` from `1`, while JavaScript `JSON.stringify` may collapse both to `1`; floating-point exponents and signed zero introduce further divergence. The current contract does not adopt broad Python/JavaScript byte-for-byte canonicalization. If a future JavaScript producer is required, cross-language conformance vectors over the supported numeric/Unicode domain must be independently frozen and passed before it can issue the same algorithm identifier.

On new Take creation, the trusted Core adapter schema-validates the request, resolves the exact preset, authors the digest and verifies ID/seed/backend/version/resolved-body equality before persistence. Studio stores and displays the backend-authored value and verifies independent artifact byte hashes as appropriate. This does not assert cryptographic authenticity against a malicious backend or filesystem. Historical requests/results and their frozen binding receipts must be read without re-resolving against a newer mutable registry. The reference helper's `verify_v1_result_pair` accepts a versioned `V1BindingResolution` receipt containing the exact requested character/preset/revision, backend ID/version and Core physical resolution **for all statuses including refusals**; it is **not** a historical Take rehydration API.

`preparation_digest` is separately created by the authoritative `BodyPresetRegistry` / Core `PreparedMorphology` binding, not calculated from user free-form character text. Saved Takes retain both request and result snapshots. Replacing/upgrading the catalog later must not mutate a historical Take or retarget it to a newer preset revision. Missing/mismatched preset returns a typed status; no implicit substitute.

## Failure cannot produce apparent successful audio

The v1 result schema forbids an `audio` artifact kind or `audio/*` media type (including ASCII case variants of either token) unless `job_status=SUCCEEDED` and `realization_outcome=FEASIBLE`. This covers physical `INFEASIBLE`, unsupported/invalid cases, failed/cancelled/incomplete jobs. Diagnostic non-audio artifacts remain permitted. A schema-valid feasible audio reference alone is NOT evidence of a genuine waveform calculation. This restriction is additive v1-only; existing v0 files remain unchanged.

## Rejection/status taxonomy

Malformed v1 request is **INVALID**, validated request with missing ID is **MISSING_PRESET**, known ID at a missing revision is **REVISION_MISMATCH**, compatible ID/revision at wrong backend is **UNSUPPORTED_BACKEND**. A bound body may still receive realization **UNSUPPORTED**, **INFEASIBLE**, or **FEASIBLE**; task execution can separately be **FAILED**. These states must not be conflated. No unrestricted morphology editing or geometry interpolation exists.

## Acceptance and limits

- Validate v1 request and result fixtures, structural negative controls, missing/latest/bool/zero revision rejection and correct schema registry references.
- Verify unchanged v0 request/result fixtures; input digest varies by selected body exact revision and backend version, while stable repeats match.
- Resolve two extant validated Core `BodyPreset` fixtures; preserve immutable earlier binding and digests across later catalog revision; typed missing, mismatch, incompatible status without fallback.
- For `SUCCEEDED, FEASIBLE/INFEASIBLE`, require `BOUND` with all four physical identity values; prevent false resolved physical digest on unsuccessful binding.
- Run both JSON Schema and runtime semantic tests, mypy and generic CI across supported Python versions and pin results to exact commit SHA.
- This **contract-level pass cannot authorize a Studio two-body physical audio demo**. Studio #14 must show actual backend capability and can use supported trace-only evidence without inventing WAV.

## Files

```text
contracts/performance/v1/
  common.schema.json
  performance-request.schema.json
  performance-result.schema.json
  examples/request.json
  examples/result.fixture.json
  examples/result.revision-mismatch.json
contracts/performance/v1/semantic_validation.py
tests/test_performance_contract_v1.py
docs/performance-contract-v1.md
```

Existing [architecture/data proposal](./research/organ-graph-program.md) and [execution plan](./research/organ-graph-execution-plan.md) track the cross-work-package status; research physics remains independent of this contract.

## Frozen source inventory compatibility

The deployed limited-live experiment deliberately audits the complete existing `src/morphoacoustics` source inventory. Adding a new production module there would invalidate its independently frozen hash manifest. Therefore the v1 binding helper is scoped to `contracts/performance/v1/semantic_validation.py` in this design-and-contract test gate, outside the published Core package; it is *not* an installed runtime API. The production integration boundary must undergo a separate explicit frozen-manifest migration before any promotion to `src/`. Neither the audited manifest nor an old verification baseline has been modified.

## Request-result semantic pair gate

The contract-local `verify_v1_result_pair` helper checks a **new result** against a previously schema-validated request and exact authoritative `V1BindingResolution` receipt: request ID, seed, backend ID/version, v1 canonical input SHA-256, status and the full resolved physical binding must all match. Every resolution, including MISSING_PRESET, REVISION_MISMATCH and UNSUPPORTED_BACKEND, must carry the exact attempted character ID, selected preset ID/revision and backend ID/version in the reference receipt; a BOUND snapshot must additionally match these values; comparing a result only with an unrelated borrowed binding is insufficient. Forged bodies, stale input digests and mismatch of a request to another Take fail closed. It does not re-resolve archived Takes against mutable catalogs; pass their stored immutable resolved snapshot when interpreting history. This is a **reference conformance utility**, not a published backend service or a substitute for authenticated artifact storage.
