# Sites Performance Studio v0 — implementation handoff

## Purpose

This document is the implementation handoff for the first creator-facing Sites/Work prototype built on **Performance Contract v0**.

The goal is not to expose `morphoacoustics` as a simulator UI. The goal is to validate the creative workflow:

```text
Character
   +
Script
   +
Direction
   ↓
Perform
   ↓
Take
   ↓
compare / revise / perform again
```

The first implementation uses a deterministic `MockBackend`. Real waveform synthesis and the `morphoacoustics` adapter come later.

## Source of truth

The site must treat these repository files as authoritative:

```text
contracts/performance/v0/common.schema.json
contracts/performance/v0/character.schema.json
contracts/performance/v0/script.schema.json
contracts/performance/v0/direction.schema.json
contracts/performance/v0/performance-request.schema.json
contracts/performance/v0/performance-result.schema.json
docs/performance-contract-v0.md
```

Do not create a second, incompatible contract inside the site.

If TypeScript types are generated, they must be generated from or mechanically checked against these schemas. Runtime request/result validation should use the same Draft 2020-12 schemas.

## Product boundary

The site speaks the **creative domain**:

- character identity and description;
- script text and stable segments;
- free-form acting direction;
- a small set of creator-facing controls;
- performances and takes.

The site must not own or expose the **physical domain** as creator controls:

- `CreatureSpec`;
- `GestureScore`;
- tract geometry;
- prepared morphology;
- physical state;
- glottal pressure;
- vocal-fold tension;
- solver-specific configuration.

Those belong behind a future backend adapter.

## v0 scope

Implement exactly one useful vertical slice:

1. create or edit one `CharacterSpec`;
2. write a `Script` containing one or more segments;
3. write global `Direction`;
4. optionally override direction for an individual segment;
5. press **Perform**;
6. validate and snapshot the creative input into a `PerformanceRequest`;
7. send it to a deterministic `MockBackend`;
8. receive a `PerformanceResult`;
9. show the resulting Take;
10. edit the creative inputs and create another Take;
11. compare at least two Takes without mutating either historical request.

This is a single-character v0. Multi-character scenes are deliberately deferred even though `Script` carries `speaker_character_id`.

## Non-goals for the first site

Do not block the v0 prototype on:

- real speech synthesis;
- phoneme editing;
- gesture editing;
- waveform synthesis from `morphoacoustics`;
- higher-fidelity physics;
- character-body/embodiment editing;
- emotion ontology design;
- collaboration, accounts, or cloud persistence;
- production deployment hardening;
- a full DAW-style timeline.

The prototype must never imply that MockBackend output is real physical or neural voice synthesis.

## Core application model

Keep the site architecture backend-neutral:

```text
UI drafts
  ├─ CharacterSpec
  ├─ Script
  └─ Direction
        ↓ Perform
PerformanceRequest snapshot
        ↓
PerformanceBackend interface
        ├─ MockBackend          ← v0
        └─ MorphoacousticsAdapter ← later
        ↓
PerformanceResult
        ↓
immutable Take record
```

Recommended TypeScript boundary:

```ts
export interface PerformanceBackend {
  perform(request: PerformanceRequest): Promise<PerformanceResult>;
}
```

The UI must depend on this interface, not on MockBackend implementation details.

## Drafts, requests, performances, and takes

Keep these concepts distinct.

### Draft

Editable creator state. A draft may be incomplete and is not historical evidence.

### PerformanceRequest

Created only when the user presses **Perform**. It is an immutable snapshot of the exact `CharacterSpec`, `Script`, `Direction`, and seed used for that attempt.

Editing the draft after Perform must not mutate a stored request.

### PerformanceResult

Backend result envelope containing job lifecycle, optional realization outcome, artifact references, timeline, diagnostics, and provenance.

### Take

A creator-facing record that pairs one immutable request with its result:

```text
Take
  ├─ request snapshot
  └─ result
```

A second performance after editing direction creates a new request and a new Take. Do not rewrite Take 1.

## Direction precedence

For structured controls, use this precedence from weakest to strongest:

```text
CharacterSpec.default_controls
          ↓ overridden by
Direction.controls
          ↓ overridden by
Direction.segment_overrides[].controls
```

Resolve controls per segment only when the backend needs effective controls.

Do not convert these controls into physical values in the site. For example, `energy=0.8` must not become a hard-coded pressure or F0 mapping.

Free-form notes are not numerically merged. Preserve:

- the global `Direction.note`;
- the matching segment override `note`;
- the character description;
- the script text;

as distinct pieces of authorial context.

## UI proposal

Use one studio screen rather than a multi-page wizard so the user can iterate quickly.

### Left — Character

Show/edit:

- name;
- description;
- default energy;
- default pace.

Keep IDs/revision visible only in an advanced/details area.

### Center — Script and Direction

Show:

- ordered script segments;
- add/delete/reorder segment;
- segment text;
- global direction note;
- global energy / pace;
- emotion label / intensity;
- selected-segment direction override.

The main action is **Perform**.

### Right — Takes

Show a chronological take list with:

- take ID;
- mock badge;
- status;
- realization outcome when present;
- duration derived from timeline;
- key direction summary;
- diagnostics count.

Allow selecting two Takes for side-by-side comparison.

### Inspector / details drawer

For the selected Take show:

- request snapshot JSON;
- result JSON;
- provenance;
- diagnostics;
- segment timeline;
- artifact references.

This makes the causal/integration boundary inspectable without turning the main studio into a developer console.

## Job lifecycle

Contract job states are:

```text
QUEUED
RUNNING
SUCCEEDED
FAILED
CANCELLED
```

For the first MockBackend the computation may finish immediately, but keep the UI and backend interface compatible with an asynchronous implementation.

A useful UI state machine is:

```text
EDITING ↔ READY → QUEUED → RUNNING → SUCCEEDED
                           ├────────→ FAILED
                           └────────→ CANCELLED
```

`SUCCEEDED`, `FAILED`, and `CANCELLED` are terminal for that job. Creating another Take starts another performance attempt rather than reviving a terminal job.

Do not confuse `job_status` with `realization_outcome`.

A valid result may be:

```text
job_status = SUCCEEDED
realization_outcome = INFEASIBLE
```

That means the computation succeeded and the requested realization did not.

## Validation boundary

Validate in two layers.

### Layer 1 — JSON Schema

Before calling a backend:

- validate `PerformanceRequest` against Draft 2020-12 schemas;
- reject malformed contract payloads before backend execution.

After backend return:

- validate `PerformanceResult` before the UI accepts it as a Take result.

### Layer 2 — semantic validation

Also enforce the cross-object invariants from `docs/performance-contract-v0.md`, including:

- unique segment IDs;
- speaker ID matches the v0 character;
- segment override IDs exist and are unique;
- timeline segment IDs exist;
- `end_seconds >= start_seconds`;
- solver-specific physical parameters do not leak into creator-facing objects.

A structurally invalid payload should be rejected at the contract boundary. `realization_outcome = INVALID` is a backend/domain result, not a substitute for accepting malformed JSON.

## Deterministic MockBackend

The MockBackend exists to validate workflow and contract behavior, not voice quality.

Requirements:

- implement the same `PerformanceBackend` interface intended for future backends;
- return a schema-valid `PerformanceResult`;
- be deterministic for the same request snapshot and seed;
- return provenance identifying `mock-v0`;
- produce segment timeline entries;
- produce at least one diagnostic identifying the result as mock output;
- support an audio-less result;
- never claim that placeholder audio represents the character's synthesized voice.

### Suggested timing algorithm

Keep it simple and deterministic.

For each script segment:

1. resolve effective creator-facing `pace`;
2. estimate a base duration from text length;
3. scale by inverse pace;
4. add a small deterministic seed-derived variation if desired;
5. insert a fixed or deterministic inter-segment gap;
6. emit monotonically increasing timeline intervals.

Exact timing quality is not important. Stable behavior is.

### Optional placeholder audio

If the site needs to exercise artifact playback, use a clearly labelled fixed placeholder sound or generated tone and return it as an `audio` artifact.

Do not synthesize fake speech and present it as meaningful character performance. An audio-less MockBackend is fully acceptable for v0.

## Deterministic input digest

For the Sites v0 implementation, choose one explicit deterministic JSON canonicalization procedure and record its name in `provenance.input_digest_algorithm`.

A practical implementation is:

1. recursively sort object keys;
2. preserve array order;
3. serialize as UTF-8 JSON without insignificant whitespace;
4. hash the resulting bytes with SHA-256;
5. encode as `sha256:<hex>`.

The implementation-specific algorithm name can be something explicit such as:

```text
sha256-over-recursively-sorted-json-v1
```

Do not silently change that algorithm within the same backend version.

## Seed behavior

Expose a seed in an advanced area, not as a primary creative control.

Default behavior:

- a new draft may receive a random non-negative integer seed;
- re-performing the identical request with the same seed must be deterministic for a backend version;
- a user may duplicate a Take and change only the seed to explore controlled variation later.

For the first MockBackend it is acceptable for seed variation to affect only timing jitter.

## Local persistence

For the first Sites prototype, browser-local persistence is sufficient.

Persist:

- current Character draft;
- Script draft;
- Direction draft;
- Take history.

Do not require accounts or server persistence.

Store immutable request/result snapshots inside each persisted Take. Schema version must be stored with them.

Provide a **Reset demo data** action.

## Demo seed data

Use the repository example as the first demo:

```text
Character: ミオ
Script:
  s1: おはよう。
  s2: 今日も眠いね。
Direction:
  眠そう。でも相手を見つけて少し嬉しくなる。
  s2 override: 語尾で少し笑う。
```

The demo should make it possible to press Perform immediately and then create a second Take by changing only one direction field.

## Take comparison

Comparison is a core v0 feature, not polish.

When two Takes are selected, show differences in:

- character revision;
- script revision/text if changed;
- global direction;
- segment overrides;
- seed;
- result status/outcome;
- timeline duration;
- diagnostics;
- provenance/backend version.

Do not reduce comparison to only audio playback.

## Accessibility and interaction

- keyboard-accessible primary controls;
- explicit labels for sliders and values;
- never rely on color alone for status;
- preserve user-entered Japanese text exactly;
- make Mock status visually obvious;
- confirm before deleting a historical Take;
- editing a draft must never silently mutate a Take.

## Acceptance criteria

The Sites v0 prototype is complete when all of the following are true:

1. The user can edit a Character, Script, and Direction.
2. Script contains stable segment IDs and supports at least two segments.
3. Direction supports global controls and a per-segment override.
4. Perform creates an immutable `PerformanceRequest` snapshot.
5. The request validates against the repository JSON Schemas.
6. MockBackend returns a schema-valid `PerformanceResult`.
7. Result validation happens before the result becomes a stored Take.
8. The site can create at least two Takes from different draft states.
9. Two Takes can be compared side by side.
10. Historical Takes do not change when current drafts are edited.
11. `job_status` and `realization_outcome` are displayed as separate concepts.
12. `SUCCEEDED + INFEASIBLE` can be represented without being shown as a crashed job.
13. An audio-less result renders correctly.
14. Provenance and diagnostics are inspectable.
15. The UI exposes no solver-specific physical controls.
16. Mock output is unmistakably labelled as mock output.
17. Browser reload preserves local drafts and Take history.
18. Reset demo data restores a known usable state.

## Suggested implementation order

Implement in this order:

```text
1. Load / represent Performance Contract v0
2. Character editor
3. Script segment editor
4. Direction editor + segment override
5. Request snapshot builder
6. Request validation
7. deterministic MockBackend
8. Result validation
9. immutable Take store
10. Take list
11. Take comparison
12. local persistence
13. inspector / provenance / diagnostics
14. interaction polish
```

Do not begin with visual polish or audio generation.

## Explicitly deferred decisions

The prototype should gather evidence before deciding:

- a canonical emotion taxonomy;
- whether `energy` and `pace` remain the right creator-facing controls;
- multi-character scene representation;
- embodiment selection UI;
- CharacterSpec-to-CreatureSpec mapping;
- text-to-pronunciation and pronunciation-to-GestureScore compilation;
- network API transport;
- local WSL bridge;
- hosted persistence;
- real waveform artifact transport.

## Work + @Sites prompt

The following can be given directly to Work with `@Sites`:

> @Sites Build the first **Performance Studio v0** for the `ryonakayama234/morphoacoustics` project. Treat `contracts/performance/v0/` and `docs/performance-contract-v0.md` as the source of truth, and follow `docs/sites-performance-studio-v0.md` as the implementation handoff. The product is a creator-facing studio, not a physics simulator UI. Implement the single-character flow `Character → Script → Direction → Perform → Take`, using a deterministic `MockBackend` behind a backend-neutral `PerformanceBackend` interface. Validate requests and results against the repository Draft 2020-12 JSON Schemas, preserve immutable request/result snapshots per Take, support per-segment direction overrides, local browser persistence, provenance/diagnostics inspection, and side-by-side comparison of two Takes. Do not expose CreatureSpec, GestureScore, tract geometry, physical-state parameters, or other solver internals. Mock output must be clearly labelled and may be audio-less. Start from the repository ミオ example so the first Perform works immediately. Do not implement real synthesis yet.

## Handoff rule

If Sites discovers that the contract cannot express a necessary creator workflow, do not silently invent a solver-specific field in the UI.

Record the concrete workflow that is blocked, then revise Performance Contract v0/v1 deliberately in the repository before depending on the new field.
