# CVI-1 — DATA / ownership and provenance proposal (Gate A)

2026-10-27 JST · Core #223 · **not a published API, not a Studio panel contract modification**.

## Existing sources of truth to reuse, not copy

- Character/Body: existing frozen `CreatureSpec`, prepared morphology and exact body fixtures; the *creative* CharacterDefinition and BodyRevision remain Studio/application ownership until separately versioned and approved.
- Task: a canonical `GestureScore` / three-task sequence where already supported. The motor strategy is a candidate **controller choice**, not a task rewrite, prescribed waveform, or identity embedding.
- `src/morphoacoustics_graph/`: currently constrained `acoustic.p_u` passive ports. Fixed serial/branching acoustics are **not** the articulating body or a source model. Do not promote suggested OrganGraph extensions to production.
- UI: only selected references and mode/selection state; no canonical physical arrays or pressure signals in UI document.
- Voice observation/Take: immutable downstream evidence only after a real physical run and qualified provenance. Naturalness and speaker identity assessments are annotations, never authoritative morphology.

## Experiment-local candidate record (field names are not a schema adoption)

```json
{
  "schema": "cvi1.experiment.proposal.v0",
  "status": "NOT_RUN",
  "case_id": "M0_H0_T0",
  "body": {
    "fixture_ref": "existing pinned prepared M0",
    "revision": null,
    "preparation_digest": null
  },
  "task": {
    "task_plan_sha256": null,
    "context_id": "T0",
    "direction_ref": null
  },
  "habit": {
    "candidate_id": "H0",
    "controller_ref": null,
    "law": "declared in prospective protocol, not a free style embedding"
  },
  "engine": {
    "backend_id": null,
    "source_commit": null,
    "physics_mode": null,
    "source_state": null,
    "receiver_ref": null,
    "simulation_clock_hz": null
  },
  "outcome": {
    "feasibility": "NOT_RUN",
    "physical_trace_ref": null,
    "acoustic_port_trace_ref": null,
    "numeric_floor_ref": null,
    "measures": {},
    "limitations": ["NO_VOICE_QUALITY_CLAIM"]
  }
}
```

The `null` placeholders are intentional. This is not a result, a permission to accept missing provenance, or an instance of the adopted `Performance Contract v0/v1`.

## Dimensions / direct observables

| Name | SI unit | Provenance/owner | Meaning |
| --- | --- | --- | --- |
| morphology length L | m | prepared physical body | body fixed per row |
| section area A | m² | prepared physical body | rest/deformed geometry, with state distinction |
| gesture time / activation | s / dimensionless | performance and realizer | continuous task execution, not WAV concatenation |
| effort or actuator command u | **declare physical dimension per control** | controller/physical realization | candidate only; no generic 0–1 loudness-to-Pa mapping |
| physical state x and velocity | specific SI units per DOF | physical backend | motor outcome, not audio observation |
| acoustic port p | Pa | solver/observer | location, clock and sign fixed |
| volume flow U | m³/s | solver/observer | signed physical port flow |
| acoustic impedance p/U | Pa·s/m³ | derived observer | include regularity/singularity masks |
| resonance / peak locations | Hz | independent identified estimator | label finite bandwidth/observer floor |
| WAV pressure/calibration | Pa only if calibrated, else declared digital units | Take/observer | never equate PCM gain with vocal effort |
| source and energy/work | W / J per modeled port | source/physics | no invented fluid/tissue energy closure |

Every derived value must record its exact causal signal path and model scope. Full absolute SPL claims require calibrated receiver; no such claim follows from a raw mouth-port pressure array.

## Analysis datasets (factorial but conditional on feasibility)

Initial candidates: M0/M1 × H0/H1 × T0/T1 (held-out compatible task contexts) = 8 records **only after the backend preflight passes**. Repeats and null controls are additional run records, not invented missing combinations. Freeze exact body, task and controller refs before observing results.

A factorial contrast `I_Q` is defined only for a scalar Q that is comparable in all four valid rows of a given task and has specified units, measurement extraction and uncertainty. If one row is infeasible or unsupported, report **NOT_ESTIMABLE**, never substitute silence/zero. Numerical differences alone must not be named perceptual speaker identity.

## Identity and integrity

- Separate hashes: input/body revision, task semantics, controller candidate, runtime/solver, raw trace, rendered waveform when actually present. No shared digest that hides which factor changed.
- Body digest MUST NOT depend on Studio canvas coordinates, label, playback state or theme.
- Task semantic hash must be identical within a task context across body/habit interventions; controller hash changes only for H0/H1.
- Source and receiver hashes must be invariant across physical comparisons.
- Any future UI binding uses stable immutable references and the currently approved Studio panel owners; no copied model state.

## Explicit status vocabulary

`PROPOSED`, `NOT_TESTABLE_BACKEND_CAPABILITY`, `INVALID_INPUT`, `UNSUPPORTED`, `INFEASIBLE`, `NUMERICALLY_UNRESOLVED`, `EXECUTED_NOT_VALIDATED`, `G0_PASS`, `G1_PASS`, `G2_ACOUSTIC_ONLY`, `G3_CREATOR_NO_GO`, `ADOPTION_HOLD`.

These are **experiment log labels**, not new Core public exception codes. Translate only documented native backend failure statuses; do not conflate `INFEASIBLE` body/task with `UNSUPPORTED` implementation.

Reference: [CVI-1 #223](https://github.com/ryonakayama234/morphoacoustics/issues/223).
