# OD-1 DATA v1 — identity, numerical states and provenance
Proposed research typed records; not a released contract or existing SDK type.

~~~mermaid
flowchart LR
 BASE["BaseBodyRef exact revision"] --> EDIT["ShapeEditProposal: family,c,r"]
 EDIT --> C["Core validate / derive"]
 C --> REV["BodyRevision candidate<br/>immutable geometry and digest"]
 REV --> PREP["PreparedMorphology"]
 G["Fixed GestureScore + LF source"] --> SESSION["PhysicalExecutionSession"]
 PREP --> SESSION
 SESSION --> RAW["RawPhysicalTrace: SI arrays"]
 RAW --> RC["IndependentReferenceComparison"]
 RC --> DEC["CapabilityDecision"]
 RAW -. "future" .-> TAKE["Studio immutable TakeRecord"]
~~~

## Data ownership and strict content
| Record | Authority | Required content |
|---|---|---|
| BaseBodyRef | Core | exact M0 body ID/revision, backend, producer SHA, preparation digest, 16 SI areas and lengths, expected orientation |
| ShapeEditProposal | Core interprets, Studio may draft | schema version; parent exact ref; family tract1d.local-log-area-5.v1; integer c=4/8; enum r∈{0.90,1.00,1.10}; rest_cross_section_area, not frequency or F0 |
| ShapeBasis | Core | fixed five weights 1/4,1/2,1,1/2,1/4, ordered center, unit m², exact shape law revision |
| BodyRevision | Core only | parent full digest; canonical edit; resulting 16×(area,length), inherited air medium, backend/capability, unique immutable recipe ID and distinct preparation digest |
| PreparedMorphology | Core | existing semantic CreatureSpec joined to backend-specific rest state and validation provenance |
| ExecutionSession | Core | body snapshot, source/task SHA, seed, 48k/24000, exact source/solver/observation domain and execution status |
| RawPhysicalTrace | Core | actual t, A_i(t), source volume flow if provided in m³/s, output pressure in Pa at specified reference plane, per-file hashes, refusal record |
| ReferenceComparison | separate observer | derived V,dV/dθ, characteristic impedance, actual *load-matched* complex transfer, residuals/uncertainty/floors, observation location |
| TakeRecord | Studio (future approved integration) | immutable historical body/task/source/revision/solver refs, authenticated actual raw/WAV hash and shared listening-gain recipe, no new physical truth |

BodyRevision does NOT store WAV, formants, F0, rendered spectrogram, UI position, perceptual score or arbitrary solver-internal transient state. Script/Direction are creative domain; physical task translation lives in a separately gated adapter.

## Version and hashing
Core authors canonical body identity from exact base revision/digest, accepted family, c, numeric ratio, full derived rest geometry, backend and shape law version. Immutable prepared digest is calculated independently by actual Core preparation. Studio never infers trusted SHA using JS JSON.stringify; numeric 1 and 1.0 spellings, signed zero, boolean-as-int, NaN, Inf and duplicate keys must not create ambiguous identities. Semantic null r=1.00 is a control, not a novel production body; old single-cell site08 BodyRevision remains distinguishable from new five-cell family. One body may be reused in multiple Takes; never lookup mutable latest for an existing historical Take.

## Refusal semantics
INVALID_INPUT: corrupt type/unit, nonfinite or nonpositive geometry, duplicate fields.
UNSUPPORTED_SHAPE_FAMILY / UNSUPPORTED_BACKEND: valid but unsupported center/ratio/body/physical port.
REVISION_MISMATCH: old parent, forged or stale body identity.
INFEASIBLE: valid supported body cannot fulfill a task; never label a missing preset as infeasible.
NUMERICALLY_UNRESOLVED: solver convergence, instability/conditioning, nonfinite output.
FAILED: external IO/runtime failure, not physics.
RESEARCH_RESULT_NOT_A_TAKE: valid experimental pressure file without authorized Studio integration.
All failures produce explicit receipt, never success audio, phantom BodyRevision or partial Take.

## Existing UI panel owners: no schema change
Project.library owns references only. Character.canvas owns organ selection, not physical solver. Selection.inspector shows supported selected organ property. Motion.canvas owns Script/Direction/Gesture intent; Scene.canvas only scene. Take.transport owns immutable sound comparisons, Research.drawer optional inspection. UI edit changes require Studio V2 STOP-AND-PROPOSE gate. Existing studio private #27 is a local feature, not general back-end physical organ graph.

## Provenance honesty
Existing Core #143 site0, #144 sites0/2/4, #149/#150 site08 and Studio #27 are historical, partly post-hoc results. This new five-cell family was chosen *after* seeing site effects. Label a subsequent pre-run frozen experiment as confirmation of this exact new family; never claim unbiased site discovery. Keep research StudyManifest/Fixture/Session/RawTrace/IndependentVerdict and creator Take in separate namespaces and states, with append-only failures and exact SHA.


## Gate B concrete research records (not a product BodyRevision schema)
The implementation supports only c={4,8} × r={0.90,1.00,1.10} with strict numeric type validation, canonical 16×10mm parent and physically positive sections. Null r=1 resolves to the same baseline object and is explicitly NOT minted as a new body. Experiment output is one atomic directory containing six 24000-sample float64 Pa NPY blobs, six 48000Hz mono PCM16 common-gain preview WAV blobs, and final decision.json as a marker. The decision includes source/gesture digests, per-condition original SI areas, volume and volume derivative, actual terminal/rest matched-observer error, measured pressure-relative-L2, null floor, source trace and file hashes. All observations are downstream of a core-created physical waveform and are NOT editable anatomy or certified Studio Takes.

The prototype does not implement a persistent Core BodyRevision registry, external hostile-filesystem authentication, general patch-edit provenance, public schema evolution, or new Studio interface. Existing exact site08 single-cell PR #27 remains separately named/pinned; it must not silently accept the five-cell family as its own. Gates C/D for persistent revision and creator UI still require separately controlled adoption.
