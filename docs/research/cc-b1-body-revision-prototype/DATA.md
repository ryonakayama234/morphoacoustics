# DATA — experimental single-rest-area BodyRevision candidate

**NOT a public performance contract.** All area and lengths are in SI; editor pixels/decoration cannot enter prepared-geometry identity.

```mermaid
flowchart LR
 S[BodyPreset ID@revision with verified digest] --> V[Core guard]
 E[RestAreaEditIntent: cavity ID / zero-based section / area_m2] --> V
 V --> R[BodyRevision: exact parent / edit digest / prepared digest]
 R --> P[PreparedMorphology: CreatureSpec + immutable Tract1DGeometry]
 P -. Future .-> T[Verified physical Take with independent source/task/solver hashes]
```

## Candidate typed fields
`RestAreaEditIntent`: `base_preset_id`, `base_revision` (strict positive integer), `base_preparation_digest`, `cavity_id`, `section_index` (strict 0..15), `area_m2` (finite >0).

`BodyRevision`: `revision_id` (content-derived, not user choice), exact parent ID/revision/digest, edit section/before/after areas, `edit_digest`, `preparation_digest`, and prepared object. `receipt()` serializes only a *proposal receipt*; it is not yet an authenticated persisted artifact or external contract.

`RevisionResult`: `ACCEPTED`, `INVALID`, `UNSUPPORTED`, `REVISION_MISMATCH`; `NUMERICALLY_UNRESOLVED` reserved for a future physical numerical gate and is not emitted without evidence. Physical `INFEASIBLE` applies only after task execution, not during this rest-geometry preparation. Runtime `FAILED` belongs to a later service boundary.

## Safety/capability proposal, NOT certified limits
- Exactly 16 × 0.01m serial sections; one isolated cavity, no cavity branching.
- One exact section's *rest* `area_m2`, prototype trial window 0.90–1.10 × corresponding **parent** section area. Bounds are provisional exploration constraints, **not certified biomechanical safety**.
- Parent is independently content-hashed before derivation. Null edits, malformed, NaN/Inf, nonpositive, wrong section/base/digest, out-of-range and unsupported graph never create new bodies.
- Every acceptance returns a fresh immutable prepared state; original `BodyPreset` and existing audio/creative Character remain unmodified.
- Digests use SHA-256 over sorted compact JSON (edit input domain and existing Core prepared-payload domain). They provide reproducibility and accidental-change detection, not signed/authenticated origin. Trust requires controlled storage/service.
- Exact source, GestureScore, seed, solver SHA, raw-Pa SHA, Studio adapter SHA, playback gain and evaluation data must live in **Take provenance** later, not be hidden inside body identity.

## Schema adoption hold
Before external release, freeze canonical numeric precision/rounding, accepted baseline whitelist, detailed failure transport, collision/reload registry semantics, bounded source capability, and cross-repo version negotiation; never retrofit arbitrary area fields into v0/v1 request or bypass the Core authority.

## Authority of prototype implementation
The prototype is held under `tools/cc_b1_revision.py` to avoid the frozen production source inventory; its `RestAreaEditIntent` and `BodyRevision` are experimental Python records, **not** a published cross-repo JSON schema. No Studio request may assume these classes are already part of an accepted contract.


## CC-B1 performer request candidate (2026-10-22)
Version `cc-b1-core-limited-performer/v1` is a standalone opt-in JSON boundary; request has exactly `schema_version`, `parent`, `edit`. Parent = `{preset_id:v3b-axial-M0, revision:1, preparation_digest:sha256:<64 hex>}`. Edit = `{cavity_id:oral-vowel-a-16x10mm, section_index:8, rest_area_ratio:"0.90"|"1.10"}`. Ratios are canonical **strings** at external interface, and are converted into SI `area_m2` by Core, with no client-supplied arbitrary audio gain/task/source. JSON schema is published as **candidate** `contracts/cc-b1/v1/core-limited-performer-request.schema.json`.
Output is a success `result.json` written last only after new two-body physics, archived `baseline_pa.npy`, `edited_pa.npy`, pair-shared-gain `baseline.wav`, `edited.wav`, two physical geometry traces, per-file SHA256, exact parent+revision+prepared hashes, source/task digest, Core checkout SHA and frozen Gate A/B science pins. Error statuses `INVALID/UNSUPPORTED/REVISION_MISMATCH/INFEASIBLE/NUMERICALLY_UNRESOLVED/FAILED` **never produce a completed Take**. A checksum is not a digital signature or authorization to trust unknown upstream data.

## Gate C v1 extended receipt and readback
Successful manifest now has `edit_intent` as a strictly accepted canonical profile and `body_revision` with exact immutable edit, so stored data can be compared against the verified CC-A2 M0/r1 baseline after restart. `verify_output_archive` rejects missing marker, unexpected file, linked/missing artifact, bytes/length mismatch, nonfinite pressure, wrong quantized oracle, wrong body digest/profile, and mismatched common playback audio. This is read-only checked evidence, NOT cryptographic origin authentication or app persistence.

## Gate C archive receipt authority constraint (2026-10-22, Draft)

On readback, `body_revision` must be an **exact typed JSON serialization match** to `prepare_rest_area_revision(trusted_registry_M0_r1, canonical_site08_edit).revision.receipt()`. This additionally binds `revision_id`, `edit_digest`, `preparation_digest`, `backend_id`, `schema`, complete `parent` and all `edit` fields. Reject unknown keys, omitted keys, changed numbers, changed types (e.g. `true` in place of integer), or nonfinite metadata. A Python mapping `==` is insufficient because `True == 1`.

Archive validation and source trust are separate: this addition does not implement signed provenance, persistent canonical-byte BodyRevision registry, collision protection across hostile stores or path-race-safe file handles. Existing raw Pa quantized checksum and WAV reconstruction guards remain mandatory. The data maturity is **research-only archived receipt**; no general-v1 BodyRevision API is adopted.
