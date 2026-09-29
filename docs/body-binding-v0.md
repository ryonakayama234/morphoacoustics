# Body Binding v0 — Character identity ↔ prepared body preset

## Purpose

This integration-layer design binds a creator-facing character identity to an
**exact version of an already prepared physical body** without putting physical
solver state into `CharacterSpec`, `Script`, or `Direction`.

```text
CharacterSpec.character_id
          +
CharacterBodyBinding
          ↓
BodyPresetRegistry
          ↓
BodyPreset(preset_id, revision)
          ↓
PreparedMorphology
  ├─ CreatureSpec
  ├─ backend-specific rest state
  ├─ backend_id
  └─ preparation provenance
```

The mapping is deliberately above the universal physical kernel. It is an
integration concern used by a future `MorphoacousticsAdapter`.

## Why this is not part of CharacterSpec

A creative character can be performed through more than one embodiment. The
name, personality, script and direction should not change merely because the
selected physical body changes.

For example, both bindings below are valid integration choices:

```text
char_mio → human-wide@1
char_mio → human-narrow@1
```

The character identity remains `char_mio`; only the embodiment changes.

## Exact revisions, no mutable `latest`

A `CharacterBodyBinding` stores:

- `character_id`;
- `preset_id`;
- `preset_revision`.

The registry resolves **exact revisions only**. It intentionally provides no
implicit `latest` alias for historical execution. This prevents a later edit to
a preset from changing what an older Take meant.

A successful resolution produces an immutable `BodyBindingSnapshot`:

```text
character_id
preset_id
preset_revision
backend_id
preparation_digest
```

`preparation_digest` is SHA-256 over a deterministic JSON representation of the
prepared CreatureSpec, backend-specific 1D rest geometry, backend ID and
preparation provenance.

## Diagnostic semantics

The initial registry distinguishes:

| status | diagnostic code | meaning |
|---|---|---|
| `BOUND` | — | exact preset revision resolved |
| `MISSING_PRESET` | `BODY_PRESET_MISSING` | preset ID is unknown |
| `REVISION_MISMATCH` | `BODY_PRESET_REVISION_MISMATCH` | preset exists, requested revision does not |
| `UNSUPPORTED_BACKEND` | `BODY_PRESET_BACKEND_UNSUPPORTED` | preset was prepared for another backend |

These are integration diagnostics. They are not physical `INFEASIBLE` outcomes.
A body can resolve successfully and later still prove physically incapable of a
requested Gesture.

## Performance Contract v0 compatibility

Performance Contract v0 keeps `CharacterSpec`, `Script`, and `Direction` free of
solver/body state. This must remain true.

For the **first X1 fixed-body demo**, v0 can still record which body was used by
emitting a result artifact such as:

```json
{
  "kind": "body-binding",
  "ref": "body-binding://mio-demo-body/r1?backend=fidelity0.tract1d&sha256=<digest>"
}
```

This uses the existing generic artifact envelope and gives a Take an immutable,
content-addressed reference to the exact binding used by the backend.

The adapter/backend version must also pin its default `CharacterBodyBinding`, so
an identical request executed by the same backend version cannot silently
change bodies.

## Where Performance Contract v0 is insufficient

v0 has **no creator-facing request field for selecting an embodiment**. It also
has no structured body-binding object in `PerformanceResult.provenance`.

Therefore v0 is sufficient for:

```text
fixed demo binding selected by a versioned adapter
→ execute
→ record exact body-binding artifact in result
```

but it is not sufficient for:

```text
creator selects body preset in Studio
→ body choice becomes part of the immutable request snapshot
```

Do not overload `CharacterSpec.default_controls`, `Direction`, backend version,
or a free-form note to carry that selection.

## Required contract change before body-selection UI

Before Studio exposes an embodiment selector, introduce a deliberately versioned
Performance Contract revision (expected direction: `performance-contract/v1`).
The minimum semantic addition should be equivalent to:

```json
{
  "embodiment": {
    "preset_id": "mio-demo-body",
    "preset_revision": 1
  }
}
```

on `PerformanceRequest`, plus a structured resolved snapshot on the result side:

```json
{
  "embodiment": {
    "preset_id": "mio-demo-body",
    "preset_revision": 1,
    "backend_id": "fidelity0.tract1d",
    "preparation_digest": "sha256:..."
  }
}
```

The exact schema should be introduced only when the X1/body-selection workflow
requires it. The invariant is more important than the field name:

- authorial character identity and physical embodiment remain separate;
- request records the selected preset revision when selection is user-visible;
- result records what was actually resolved;
- the resolved digest is stable historical evidence.

## X1 handoff

The first `MorphoacousticsAdapter` may use one fixed binding such as:

```text
char_mio → mio-demo-body@1
```

and expose the resolved snapshot as a `body-binding` artifact in the existing v0
result. This lets X1 connect Studio to the M2 waveform path without prematurely
adding body editing to S2.

If X1 needs multiple selectable bodies, stop first and version the Performance
Contract as described above.

## Scope boundary

Body Binding v0 does not provide:

- a free-form anatomy editor;
- automatic CreatureSpec → numerical geometry preparation;
- a universal body serialization format;
- physical feasibility prediction;
- body selection inside Performance Contract v0.

It provides only the exact-version integration boundary needed to make body use
reproducible and inspectable.
