# Architecture

## Causal contract

`morphoacoustics` is organized around a causal simulation path rather than around audio features:

```text
CreatureSpec + GestureScore
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
2. **Task / motor program** — morphology-independent gestures such as constriction, opening, phonation, and pressurization.
3. **Physical state** — morphology-specific positions, deformation, contact, pressure, flow, or a backend-specific approximation of them.
4. **Acoustic field** — source generation, propagation, resonances, losses, radiation, and eventually source-filter coupling.
5. **Observation** — waveform and derived analyses.

## Boundary rule

The domain schema should be able to represent more than any one backend can solve.

For example, `CreatureSpec` may represent branching cavities while Fidelity 0 supports only one isolated serial 1D tract. A backend must return `UNSUPPORTED` for a morphology or task outside its capability rather than silently deleting unsupported structure or narrowing the universal domain schema.

Backend-specific physical-state types therefore live outside `domain`. Fidelity 0 uses `Tract1DGeometry`; higher-fidelity realizers may return entirely different state types.

## Realization outcomes

Realization failures are classified by meaning:

- `FEASIBLE` — the request was realized.
- `INFEASIBLE` — the request is valid and supported, but this morphology cannot physically realize it.
- `UNSUPPORTED` — the request or morphology requires capability this backend does not implement.
- `INVALID` — the request or prepared backend state violates the simulation contract.

This distinction is important for morphology-transfer experiments and future inverse inference. `INFEASIBLE` is evidence about the body; `UNSUPPORTED` is evidence about the solver; `INVALID` is evidence about the request/configuration.

## Backend strategy

Backends are interchangeable behind common realization and acoustic contracts.

`simulate_snapshot()` is the application-level façade. It first asks a `Realizer[TState]` for a physical state and, only on successful realization, passes that state to a compatible `AcousticBackend[TState]`.

```text
simulate_snapshot
      │
      ├── Realizer[TState]
      │       ↓
      │      TState
      │
      └── AcousticBackend[TState]
              ↓
         AcousticResponse
```

The façade does not construct a concrete transmission-line solver itself.

- **Fidelity 0:** static prepared 1D tract state + lossless segmented transmission-line acoustics.
- **Fidelity 1:** time-varying tract, losses, noise sources, side branches, source-filter coupling.
- **Higher fidelity:** multimodal / 3D acoustics and short validation runs with FEM or stronger coupled models.

The same `CreatureSpec` and `GestureScore` should remain meaningful across fidelity levels.

## Public API boundary

The package root exports domain contracts and stable orchestration. Concrete Fidelity-0 state, realizer, and acoustic solver types live in their respective subpackages so experimental backend details do not accidentally become the permanent top-level API.

## UI boundary

This repository is headless. A future site should call a stable simulation API and must not become the owner of physical state, gesture semantics, or scientific assumptions.
