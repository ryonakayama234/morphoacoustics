# morphoacoustics

A headless research kernel for morphology-conditioned embodied acoustic simulation.

The core causal path is:

```text
Morphology + task-level motor program
                ↓
        physical dynamics
                ↓
              sound
```

The project treats waveform and spectrograms as downstream observations, not as the internal representation of a voice. The canonical motor representation is intended to be morphology-independent task/gesture space; each body is responsible for realizing those tasks in its own physical coordinates.

## Research goals

- Represent human, animal, and hypothetical vocal/oral morphologies under one schema.
- Execute the same task-level gesture score on different morphologies.
- Allow physically unrealizable gestures to fail explicitly.
- Support multiple interchangeable fidelity levels for the physical/acoustic backend.
- Preserve inspectable causal traces from gesture through physical state to sound.
- Use neural components only as proposals, estimators, or residual models without bypassing the physical causal path.

## Initial scope

The first milestone is deliberately small:

1. Define the domain model (`CreatureSpec`, `Gesture`, `GestureScore`, `SimulationResult`).
2. Add a simple 1D tube acoustic backend.
3. Map a small gesture vocabulary (`CONSTRICT`, `OPEN`, `PHONATE`, `PRESSURIZE`) to morphology-specific geometry/state.
4. Run the same gesture on multiple morphologies and observe different physical/acoustic outcomes.
5. Return an explicit infeasibility result when a task cannot be realized.

No UI is included here. A future site/application should consume a stable simulation API rather than becoming part of the physics kernel.

## Repository layout

```text
docs/                  architecture, invariants, assumptions
src/morphoacoustics/   research kernel
experiments/            executable research experiments
tests/                  software and scientific tests
```

## Status

Early research scaffold. The domain contracts come first; numerical solvers follow.
