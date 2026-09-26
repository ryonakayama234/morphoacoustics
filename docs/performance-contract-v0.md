# Performance Contract v0

## Purpose

Performance Contract v0 is a creator-facing contract that sits **above** `morphoacoustics`.

It describes a request in the language of creative work:

```text
CharacterSpec + Script + Direction
                ↓
        PerformanceRequest
                ↓
        backend adapter
                ↓
        PerformanceResult
```

It does **not** make `CharacterSpec`, `Script`, or `Direction` part of the physical simulation kernel. The `morphoacoustics` package remains responsible for morphology, task/gesture realization, physical state, acoustics, and observations.

The contract exists so a future site can ask a character to perform a script without owning solver-specific state or committing the UI to one synthesis backend.

## Design boundary

The creative domain and the physical domain use different vocabularies.

```text
creative domain                  physical domain
---------------                  ---------------
CharacterSpec                    CreatureSpec
Script                           linguistic / pronunciation representation
Direction                        GestureScore / motor control proposals
PerformanceRequest      →        backend-specific compilation / adaptation
PerformanceResult       ←        observations, diagnostics, provenance
```

The translation between these domains is the responsibility of a backend adapter or performance compiler.

A creative control such as `energy=0.8` must therefore **not** be interpreted by the contract as a direct command such as a fixed pressure, F0, muscle activation, or tract parameter. Different backends may realize the same direction differently.

## Versioning

Every top-level object carries:

```json
"schema_version": "performance-contract/v0"
```

Breaking semantic or structural changes require a new contract version. Backend versioning is separate and appears in result provenance.

The JSON Schemas use JSON Schema Draft 2020-12 and live under:

```text
contracts/performance/v0/
```

The schemas are an external integration contract. They are intentionally not imported into `src/morphoacoustics`.

## CharacterSpec

`CharacterSpec` describes the actor as a creative identity, not a solved body.

Required fields:

- `character_id`
- `revision`
- `name`

Optional fields:

- `description`
- `default_controls`

`default_controls` contains creator-facing defaults such as energy or relative pace. It must not contain a `CreatureSpec`, vocal-tract geometry, pressure, vocal-fold parameters, or backend state.

This keeps character identity independent from embodiment. A later adapter may map one character to a human, animal-like, hypothetical, robotic, or other embodiment without changing the character-facing contract.

## Script

A script is segmented from v0 onward.

Each segment has:

- `segment_id`
- `speaker_character_id`
- `text`

The script intentionally does not contain phonemes, gestures, timing solutions, or acoustic features. Those are compiled representations, not authorial source material.

Segment IDs provide a stable target for direction overrides, timing results, diagnostics, and future editing.

## Direction

Direction combines free-form authorial intent with a deliberately small structured control surface.

Top-level fields may include:

- `note`
- `controls`
- `segment_overrides`

The initial structured controls are:

- `energy`: normalized creator-facing intensity in `[0, 1]`
- `pace`: positive relative pace where `1.0` is neutral
- `emotion.label`
- `emotion.intensity`: normalized value in `[0, 1]`

These controls are not physical parameters.

A segment override targets an existing `segment_id` and may override a note and/or structured controls for that segment.

## PerformanceRequest

A `PerformanceRequest` contains snapshots of:

- one `CharacterSpec`
- one `Script`
- one `Direction`
- a deterministic `seed`
- optional requested capabilities

The snapshots are embedded rather than represented only by mutable IDs. This preserves the exact creative input used for a take even if the source character, script, or direction is edited later.

Initial capability names are:

- `audio`
- `timeline`
- `diagnostics`
- `gesture_trace`
- `physical_trace`

A backend may return `UNSUPPORTED` when a requested capability or realization is outside its current implementation.

## PerformanceResult

A result is an envelope, not merely a waveform.

It contains:

- identity: `performance_id`, `request_id`, `take_id`
- job lifecycle: `job_status`
- optional scientific/realization outcome
- artifact references
- optional segment timeline
- diagnostics
- provenance

### Job lifecycle and realization outcome are different

`job_status` is an execution state:

- `QUEUED`
- `RUNNING`
- `SUCCEEDED`
- `FAILED`
- `CANCELLED`

`realization_outcome` is a domain result:

- `FEASIBLE`
- `INFEASIBLE`
- `UNSUPPORTED`
- `INVALID`

A successful job may legitimately produce:

```text
job_status = SUCCEEDED
realization_outcome = INFEASIBLE
```

That means the computation completed and established that the requested performance cannot be physically realized by the selected body under the selected backend contract. It is not an execution failure.

The schema requires a realization outcome whenever the job status is `SUCCEEDED`.

## Artifacts

Large or backend-specific outputs are referenced rather than embedded in the result JSON.

Examples include:

- audio
- spectrograms
- gesture traces
- physical-state traces
- future video or animation products

An artifact contains a `kind` and `ref`, with optional media type and segment association.

The contract deliberately does not prescribe storage transport. A local service, hosted site, content-addressed store, or future asset service may interpret the reference according to deployment context.

## Provenance and reproducibility

A result records at least:

- backend name
- backend version
- contract version
- seed
- deterministic input digest

The exact digest canonicalization algorithm is not frozen by v0; implementations should record the algorithm name in `input_digest_algorithm` and must guarantee that identical normalized requests produce identical digests within that implementation/version.

The request itself remains the authoritative creative snapshot.

## Semantic validation beyond JSON Schema

Some important rules span multiple objects and therefore require application-level validation rather than structural JSON Schema validation.

At minimum:

1. every `Script.segments[].segment_id` must be unique within the script;
2. every `speaker_character_id` used by this single-character v0 request must match `CharacterSpec.character_id`;
3. every `Direction.segment_overrides[].segment_id` must identify a real script segment;
4. segment override IDs must not appear more than once;
5. for each timeline interval, `end_seconds >= start_seconds`;
6. timeline segment IDs must identify real script segments;
7. `FAILED` means execution failure, not physical infeasibility;
8. backend-specific physical parameters must not be inserted into CharacterSpec, Script, or Direction.

These checks belong in the future performance service / adapter layer.

## Mock backend role

The first backend should be deterministic and intentionally non-physical.

Its purpose is to test the contract and the creative workflow before high-cost synthesis exists. Given a request, it may produce deterministic placeholder timing, fixture audio references, diagnostics, and provenance.

The mock backend must use exactly the same request/result envelope intended for later physical or neural backends.

This allows a site to implement:

```text
Character → Script → Direction → Perform → Take
```

before waveform synthesis is ready.

## Relationship to morphoacoustics

`morphoacoustics` remains headless and keeps its current causal contract:

```text
CreatureSpec + PreparedMorphology + GestureScore
                    ↓
             physical realization
                    ↓
                 acoustics
                    ↓
               observation
```

A future adapter may perform transformations such as:

```text
CharacterSpec → embodiment selection / CreatureSpec binding
Script        → linguistic / pronunciation plan → GestureScore proposals
Direction     → modifiers on performance compilation
```

But those transformations are not part of the universal physical kernel.

## Acceptance criteria for v0

The contract is considered usable for the first site/mock integration when:

1. the same normalized request and seed are reproducible by a backend version;
2. editing a source character later does not mutate a stored prior request snapshot;
3. direction can be expressed globally and overridden for an individual script segment;
4. a mock backend and a future morphoacoustics adapter can return the same result envelope;
5. `FAILED` and `INFEASIBLE` remain distinct;
6. an audio-less result remains valid;
7. the JSON fixtures validate against the v0 schemas plus the semantic rules above;
8. no solver-specific parameter leaks into the creative schemas.

## Files

```text
contracts/performance/v0/
  common.schema.json
  character.schema.json
  script.schema.json
  direction.schema.json
  performance-request.schema.json
  performance-result.schema.json
  examples/
    request.json
    result.mock.json
```

This is the first versioned boundary for future Sites / performance-studio work. It is intentionally small: fields should be added only when a real creative workflow or backend requirement demonstrates that they are necessary.
