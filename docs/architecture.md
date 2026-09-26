# Architecture

## Causal contract

`morphoacoustics` is organized around a causal simulation path rather than around audio features:

```text
CreatureSpec + backend-specific rest state
          ↓
 preparation / explicit binding
          ↓
 PreparedMorphology[T]
          +
 GestureScore
          ↓
 morphology-specific realization
          ↓
 backend-specific physical state
          ↓
 acoustic backend
          ↓
 acoustic observation / later waveform output
          ↓
 analysis
```

Waveforms and spectrograms are observations. They are not allowed to become the internal motor representation.

## Representation layers

1. **Morphology** — cavities, source organs, articulators, materials, and constraints.
2. **Preparation** — an explicit, provenance-carrying binding between universal morphology semantics and a backend-specific numerical rest state.
3. **Task / motor program** — morphology-independent gestures such as constriction, opening, phonation, and pressurization.
4. **Physical state** — morphology-specific positions, deformation, contact, pressure, flow, or a backend-specific approximation of them.
5. **Acoustic field** — source generation, propagation, resonances, losses, radiation, and eventually source-filter coupling.
6. **Observation** — waveform and derived analyses.

## Boundary rule

The domain schema should be able to represent more than any one backend can solve.

For example, `CreatureSpec` may represent branching cavities while Fidelity 0 supports only one isolated serial 1D tract. A backend must return `UNSUPPORTED` for a morphology or task outside its capability rather than silently deleting unsupported structure or narrowing the universal domain schema.

Backend-specific rest-state and physical-state types therefore live outside `domain`. Fidelity 0 uses `Tract1DGeometry`; higher-fidelity realizers may use entirely different state types.

## Preparation boundary

A solver-specific numerical body must not be an implicit property of a realizer instance. `PreparedMorphology[T]` explicitly binds:

- one `CreatureSpec`,
- one backend-specific rest state `T`,
- a backend identifier,
- preparation provenance.

For Fidelity 0, `prepare_tract1d()` currently binds a manually supplied `Tract1DGeometry` to a creature after validating that the geometry targets a cavity that exists in that creature. This is **binding**, not anatomical derivation: the current `CreatureSpec` does not yet contain enough metric information to derive a complete tract geometry.

Preparation also does not consume solver capability failures. A branched creature can be coherently bound to a serial prepared cavity and later receive `UNSUPPORTED` from the Fidelity-0 realizer. This preserves the meaning of failure classes.

## Realization outcomes

Realization failures are classified by meaning:

- `FEASIBLE` — the request was realized.
- `INFEASIBLE` — the request is valid and supported, but this morphology cannot physically realize it.
- `UNSUPPORTED` — the request or morphology requires capability this backend does not implement.
- `INVALID` — the request or prepared backend state violates the simulation contract.

This distinction is important for morphology-transfer experiments and future inverse inference. `INFEASIBLE` is evidence about the body; `UNSUPPORTED` is evidence about the solver; `INVALID` is evidence about the request/configuration.

## Backend strategy

Backends are interchangeable behind common realization and acoustic contracts.

`simulate_snapshot()` is the application-level façade. It receives a prepared morphology and asks a `Realizer[TPrepared, TState]` for a physical state. Only on successful realization does it pass that state plus an opaque backend-specific request to a compatible acoustic backend.

```text
simulate_snapshot
      │
      ├── PreparedMorphology[TPrepared]
      │
      ├── Realizer[TPrepared, TState]
      │       ↓
      │      TState
      │
      └── AcousticBackend[TState, TRequest, TObservation]
              ↑                    ↓
           TRequest            TObservation
```

The façade does not know whether an acoustic request means a frequency grid, field probe, modal query, or another future observation request. It also does not require every backend to return input impedance. Fidelity 0 concretizes this boundary as `ImpedanceRequest -> ImpedanceResponse`.

- **Fidelity 0:** static prepared 1D tract state + lossless segmented transmission-line acoustics.
- **Fidelity 1:** time-varying tract, losses, noise sources, side branches, source-filter coupling.
- **Higher fidelity:** multimodal / 3D acoustics and short validation runs with FEM or stronger coupled models.

The same `CreatureSpec` and `GestureScore` should remain meaningful across fidelity levels.

## Morphology-transfer experiment contract

A central scientific intervention is to hold `GestureScore` fixed while changing `PreparedMorphology`.

Expected outcomes are deliberately not acoustic invariance. Instead:

- the task-level gesture retains the same meaning,
- each body realizes that task in its own physical coordinates,
- acoustic observations may differ,
- a valid task may be `INFEASIBLE` for one morphology and `FEASIBLE` for another.

This makes morphology transfer an experimental test of whether the canonical task representation is truly less body-specific than actuator or joint coordinates.

## Public API boundary

The package root exports domain contracts, generic preparation contracts, and stable orchestration. Concrete Fidelity-0 state, preparation helper, request/response, realizer, and acoustic solver types live in their respective subpackages so experimental backend details do not accidentally become the permanent top-level API.

## UI boundary

This repository is headless. A future site should call a stable simulation API and must not become the owner of physical state, gesture semantics, preparation provenance, or scientific assumptions.
