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
2. `PreparedMorphology[T]` explicitly binds a `CreatureSpec` to a backend-specific rest state plus preparation provenance without moving backend geometry into the universal morphology schema.
3. Fidelity 0 realizes active `CONSTRICT` gestures onto a prepared serial 1D tract state.
4. A rigid, lossless segmented transmission-line backend evaluates the resulting frequency-domain input impedance with an ideal pressure-release outlet.
5. `simulate_snapshot()` orchestrates realization and acoustics without depending on the concrete Fidelity-0 solver.
6. Invalid requests, unsupported backend capability, and physical infeasibility are reported with distinct meanings.
7. The same normalized gesture can be applied unchanged to differently prepared morphologies, producing morphology-specific physical and acoustic outcomes or an explicit `INFEASIBLE` result.

Fidelity 0 is intentionally static, one-dimensional, rigid-wall, lossless, serial-tract, source-free, and waveform-free. Those properties are its model contract, not restrictions on the domain schema. Its numerical geometry is currently prepared manually and explicitly bound to `CreatureSpec`; deriving geometry from richer morphology parameters is a later step. See `docs/fidelity-0.md`.

No UI is included here. A future site/application should consume the stable simulation API rather than becoming part of the physics kernel.

## Creative integration boundary

The repository also carries a versioned **Performance Contract v0** as an external integration contract for future creative applications. It defines creator-facing `CharacterSpec`, `Script`, `Direction`, `PerformanceRequest`, and `PerformanceResult` JSON Schemas without importing those concepts into `src/morphoacoustics`.

See `docs/performance-contract-v0.md` and `contracts/performance/v0/`. The first creator-facing Sites/Work implementation handoff is `docs/sites-performance-studio-v0.md`.

## Preparation boundary

`CreatureSpec` describes morphology semantics while numerical solvers consume backend-specific rest states. These are joined explicitly before simulation:

```text
CreatureSpec + backend-specific rest state
                 ↓
          preparation / binding
                 ↓
       PreparedMorphology[T]
                 +
            GestureScore
                 ↓
              Realizer
```

Preparation validates that a numerical state can coherently be bound to the creature and records provenance. It does not silently erase morphology that Fidelity 0 cannot solve: solver capability limits remain explicit `UNSUPPORTED` realization outcomes.

## Repository layout

```text
contracts/performance/  versioned external creative integration contracts
docs/                   architecture, invariants, assumptions
src/morphoacoustics/    research kernel
  preparation/          explicit CreatureSpec ↔ backend-state binding
experiments/             executable research experiments
tests/                   software and scientific tests
```

## Status

Early research scaffold. Domain and causal contracts come first; higher-fidelity numerical solvers follow.

## Current bounded capability index (2026-10-20)

The **Initial vertical slice** above remains historical architecture background, not a claim that every currently adopted solver is source-free or waveform-free. Present Core has progressed in distinct, scope-limited steps:

- **Adopted limited:** fixed passive OG-4 three-organ ideal junction **frequency-domain p/U**, on exactly eight isolated verified frequencies ([normative contract](docs/research/og4-branch3-api-v1.md), [PR #108](https://github.com/ryonakayama234/morphoacoustics/pull/108)); this **does not render a 48kHz waveform** and cannot be interpolated as an accepted continuous-band response.
- **Adopted limited:** CC-A2 fixed two *serial*-body physical audio/trace trusted request–Take path ([Core PR #122](https://github.com/ryonakayama234/morphoacoustics/pull/122), [Studio CC-A2](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/cc-a2-two-body-studio.md)); this **does not synthesize a branching-organ body**.
- **Research candidate / not adopted:** OG-AUD1 joins those two capacities only after a *new*, independently validated broadband acoustic response and finite-time physical pressure source/monitor. See [synchronized SYSTEM/DATA/EXPERIMENT](docs/research/og-aud1/SYSTEM.md), [review note](docs/research/og-aud1/GATE_A_REVIEW.md), [executed Wolfram 12-state exploratory preflight](experiments/043_og_aud1_preflight/RESULTS.md) and [Studio handoff](https://github.com/ryonakayama234/morphoacoustics-studio/pull/21). No graph-to-audio production solver, waveforms, or new Studio integration is claimed by these Draft files.

For current scientific decisions, maturity status, and cross-repo handoffs, follow [research index](docs/research/README.md) rather than treating the first introductory example as the latest capability boundary.
