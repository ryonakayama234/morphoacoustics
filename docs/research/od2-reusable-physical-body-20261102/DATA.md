# OD-2 DATA — typed research candidate, identity authority and SI observations

**STATUS: DESIGN CANDIDATE / NOT A RELEASED SCHEMA / NO EXISTING SDK TYPE CLAIMED.** Parent #271. Data types below are *proposed*, not exports available in current main.

## Causal data DAG and immutable ownership
~~~mermaid
flowchart LR
 CHAR["Studio CharacterRef"] --> BR["Core BodyRevisionRef (exact)"]
 BASE["Core BaseBodyRef M0@1"] --> PROP["ShapeEditProposal"]
 PROP --> VALID["Core family + SI validation"]
 BASE --> VALID
 VALID --> RECIPE["Canonical BodyRevisionReceipt"]
 RECIPE --> BR
 RECIPE --> PREP["Core PreparedMorphology / preparation_digest"]
 MOT["Studio Performance / exact GestureScore"] --> EX["Core ExecutionSession"]
 PREP --> EX
 SRC["fixed LF source identity"] --> EX
 EX --> RAW["RawTrace and actual Pa observation"]
 RAW --> MAN["Verified physical artifact manifest"]
 MAN -. "separate Studio integration" .-> TAKE["Immutable Studio Take"]
 TAKE --> DOCK["take.transport"]
 RAW --> RESEARCH["research.drawer"]
 VALID --> FAIL["Typed rejection; no phantom success"]
~~~

## Proposed data objects (semantic shape, no stable wire ABI yet)

### ShapeEditProposal (input intent)
- schema_version: literal od2.shape-proposal.v0-draft (future version negotiated at G3).
- parent: exact Core-owned preset_id, revision, preparation_digest (M0/r1 only).
- organ_ref: the validated serial voice-tract cavity/organ ID; not a UI node coordinate, not section-is-organ identity.
- family: tract1d.local-log-area-5.v1.
- center_index: exactly 4 or 8 (integer, exclude bool), zero-based glottis→mouth.
- rest_area_ratio: *enumeration string* "0.90" | "1.00" | "1.10" at wire boundary; map to approved exact numeric values only within Core to avoid JS/Python numeric spellings.
- no caller-supplied area vector, F0, formant, gain, source settings, materials, waveform, filename or backend override.

### ShapeFamilyDefinition (Core trusted)
- family_version and fixed weights [1/4,1/2,1,1/2,1/4] at c-2..c+2.
- allowed body/backend/source/timing envelope; positive 16×SI geometry and cavity orientation.
- actual numerical model law and preparation validation version; capability declaration, never UI-owned.
- no assumption that the passive OG-3 acoustic.p_u graph executes full active body dynamics.

### BodyRevisionReceipt (Core-only authoritative issuance)
- full exact parent body ref/digest; schema+family version; canonical edit; derived ordered 16×(length_m,area_m2) SI rest state; derived rest volume; prior immutable body lineage and backend identity; authoritative identity algorithm and complete digest.
- revision_id is content-addressed over a versioned Core canonical *recipe with parent lineage and derived geometry*. Canonical encoding must be unambiguous for binary64 (e.g., fixed hexadecimal float encoding or a strict declared canonical byte format); never hash ad-hoc cross-language JSON.stringify. Backend and algorithm changes require new version IDs, not reusing the same digest.
- preparation_digest is issued by existing Core PreparedMorphology preparation independently of the revision/recipe digest. A revision may map to a prepared-state fingerprint; do not replace one with the other.
- same parent+same exact approved edit = idempotent revision ID; c=4 versus c=8 or old single-site family = different recipe identities. If identical physical geometry is reached by different lineages, receipt IDs remain different but preparation fingerprints may coincide, and this is disclosed. Null ratio 1.00 aliases parent and must not mint a new production revision.
- timestamps are audit metadata, not part of physical identity. Character label, UI x/y, preview gain, Take, hearing-score and raw audio are never part of BodyRevision.
- readback re-derives trusted Core geometry/recipe and compares *all* fields, not just manifest hashes.

### PreparedMorphology and Binding
- existing Core PreparedMorphology[Tract1DGeometry] (creature, rest_state, backend_id, preparation provenance).
- existing BodyPresetRegistry is the binding authority. Reconcile proposed derived-body registry with previously researched single-site #166, not a second authoritative competing source.
- CharacterRef holds selected immutable revision ref, not a copied solver state; historic references always resolve exact revision, never mutable "latest".
- G3 must select *one* supported CLI/importable API with typed refusal and format/version agreement. v0/v1 Performance Contracts unchanged; new experimental wire schema cannot be silently branded v1.

### PhysicalExecutionSession (Core)
- exact body revision/preparation IDs; task/gesture/Direction interpretation IDs; solver/code SHA, source identity, seed, 48000 samples/s, 24000 samples, 100Hz fixed LF provenance, declared load and observation plane, execution status.
- recorded physical timecourse of all 16 areas at declared samples, source input flow/pressure as actually available, 1D acoustic outlet/observer result; no invented trace fields.
- audio provenance: raw native float64 Pa NPY and named observation; WAV PCM16 derived with one declared paired common gain solely for playback; paired outputs must retain raw Pa and gain formula, hashes and sizes; a WAV without physical trace and matching receipt is not a valid completed Take.

### ScientificComparison / Studio TakeRecord
- reference comparison includes independent V, dV/dtheta, characteristic Z, complex H(f) at actual termination and distance proxy, temporal invariants, null checks, uncertainty/numerical floor, raw pressure relative L2 and refusal results. One physical metric does not certify audition.
- Studio TakeRecord (only after separate G4) stores immutable body/task/source/scene/solver refs and verified actual artifact IDs, comparisons and optional subjective notes. It is NOT part of body physics and may retain one body across many Takes.
- Research drawer may present exact SHA, model limitations and structured result. Project library holds reference IDs, not a second body clone.

## Error and non-success semantics
| Code | Meaning | Audio success? |
|---|---|---|
| INVALID_INPUT | malformed type, duplicate key, NaN/Inf, nonpositive or mis-unit geometry, unknown fields | NO |
| UNSUPPORTED_SHAPE_FAMILY / UNSUPPORTED_BACKEND | valid request outside supported body/family/port/backend | NO |
| MISSING_PRESET | exact parent not found | NO |
| REVISION_MISMATCH | parent/revision/digest, readback, recipe, or historical binding fails | NO |
| INFEASIBLE | supported valid body cannot physically realize a valid task | NO |
| NUMERICALLY_UNRESOLVED | convergent/finite/conditioned numerical result cannot be established | NO |
| FAILED | runtime/artifact IO interrupted or corrupt, no complete manifest | NO |
| NOT_TESTABLE_BACKEND_CAPABILITY | experiment cannot execute on *same* lawful body/realizer combination | NO |
| RESEARCH_RESULT_NOT_A_TAKE | physical study succeeded but there is no approved Studio creation binding | NO |

Do not use INFEASIBLE as a synonym for missing feature. Fail-closed means no published success marker or credible playable Take, but preserve diagnostic failure record when useful.

## Cross-revision compatibility
Legacy site08 single cell PR #166 is private and pinned, not main. The derived body family identity MUST encode which edit model was applied; any old site08 ID and artifact remain byte-for-byte historical. CC-A2 M0/M1 adopted presets and X2a live path unchanged; old Takes can still be read without moving their original revision/body pointer. No silent solver upgrade of an archived Take. Core source-inventory migration, if needed, must be separate, reviewed and explicit.

## Research-only exemplar (illustrative not released JSON)
~~~json
{
  "schema_version": "od2.shape-proposal.v0-draft",
  "parent": {
    "preset_id": "v3b-axial-M0",
    "revision": 1,
    "preparation_digest": "<Core-authored exact SHA256>"
  },
  "organ_ref": "<Core-validated vocal tract cavity ID>",
  "family": "tract1d.local-log-area-5.v1",
  "center_index": 4,
  "rest_area_ratio": "1.10"
}
~~~
Do not materialize placeholder digest as real data. Actual source body ID and cavity binding must be verified at code-level A0 prior to accepted G3 schema.
