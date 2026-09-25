# morphoacoustics

A headless research kernel for morphology-conditioned embodied acoustic simulation.

The core causal path is:

```text
Morphology + task-level motor program
                ↓
        physical realization
                ↓
              acoustics
                ↓
            observation
```

The project treats waveform and spectrograms as downstream observations, not as the internal representation of a voice. The canonical motor representation is intended to be morphology-independent task/gesture space; each body is responsible for realizing those tasks in its own physical coordinates.

## Research goals

- Represent human, animal, and hypothetical vocal/oral morphologies under one schema.
- Execute the same task-level gesture score on different morphologies.
- Allow physically unrealizable gestures to fail explicitly.
- Support multiple interchangeable fidelity levels for realization and acoustics.
- Preserve inspectable causal traces from gesture through physical state to sound.
- Use neural components only as proposals, estimators, or residual models without bypassing the physical causal path.

## Initial vertical slice

The first end-to-end implementation deliberately keeps the physics small:

1. `CreatureSpec` and `GestureScore` remain backend-independent domain contracts.
2. Fidelity 0 realizes active `CONSTRICT` gestures onto a prepared serial 1D tract state.
3. A rigid, lossless segmented transmission-line backend evaluates the resulting frequency-domain input impedance with an ideal pressure-release outlet.
4. `simulate_snapshot()` orchestrates realization and acoustics without depending on the concrete Fidelity-0 solver.
5. Invalid requests, unsupported backend capability, and physical infeasibility are reported with distinct meanings.
6. The same normalized gesture can be applied to differently scaled 1D morphologies, producing different physical and acoustic outcomes.

Fidelity 0 is intentionally static, one-dimensional, rigid-wall, lossless, serial-tract, source-free, and waveform-free. Those properties are its model contract, not restrictions on the domain schema. See `docs/fidelity-0.md`.

No UI is included here. A future site/application should consume the stable simulation API rather than becoming part of the physics kernel.

## Repository layout

```text
docs/                  architecture, invariants, assumptions
src/morphoacoustics/   research kernel
experiments/            executable research experiments
tests/                  software and scientific tests
```

## Status

Early research scaffold. Domain and causal contracts come first; higher-fidelity numerical solvers follow.
