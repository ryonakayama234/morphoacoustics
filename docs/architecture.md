# Architecture

## Causal contract

`morphoacoustics` is organized around a causal simulation path rather than around audio features:

```text
CreatureSpec + GestureScore
          ↓
 morphology-specific realization
          ↓
 physical state / geometry trajectory
          ↓
 source + airflow + acoustic backend
          ↓
 SimulationResult
          ↓
 waveform / spectral / perceptual analysis
```

Waveforms and spectrograms are observations. They are not allowed to become the internal motor representation.

## Representation layers

1. **Morphology** — cavities, source organs, articulators, materials, and constraints.
2. **Task / motor program** — morphology-independent gestures such as constriction, opening, phonation, and pressurization.
3. **Physical state** — morphology-specific positions, deformation, contact, pressure, and flow.
4. **Acoustic field** — source generation, propagation, resonances, losses, radiation, and eventually source-filter coupling.
5. **Observation** — waveform and derived analyses.

## Boundary rule

The domain schema should be able to represent more than any one backend can solve.

For example, `CreatureSpec` may represent branching cavities while an early fidelity-0 backend may only support one serial tube. Unsupported physics should be reported explicitly by the backend rather than removed from the domain model.

## Backend strategy

Backends are expected to be interchangeable behind a common simulation contract.

- **Fidelity 0:** simple source + 1D area function + transmission line.
- **Fidelity 1:** time-varying tract, losses, noise sources, side branches, source-filter coupling.
- **Higher fidelity:** multimodal / 3D acoustics and short validation runs with FEM or stronger coupled models.

The same `CreatureSpec` and `GestureScore` should remain meaningful across fidelity levels.

## UI boundary

This repository is headless. A future site should call a stable simulation API and must not become the owner of physical state, gesture semantics, or scientific assumptions.
