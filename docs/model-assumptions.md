# Model assumptions

This file records assumptions that are currently part of the model so they can be challenged later rather than becoming invisible implementation facts.

## A1. Task-space is the canonical motor representation

The initial API represents motor intent as task-level gestures. Muscle activations, joint coordinates, and morphology-specific trajectories are realizations produced downstream.

## A2. Gesture location may use normalized morphology coordinates

When a gesture needs a location along an ordered tract, the initial representation may use a normalized coordinate in `[0, 1]`. This is a task-space convenience, not a claim that every morphology is a single tube.

For the Fidelity-0 serial tract, `0` is the inlet/source side and `1` is the outlet/radiation side. If a normalized location lies exactly on an internal discretization boundary, it belongs to the downstream section. This boundary rule is part of the Fidelity-0 mapping convention, not a universal biological claim.

## A3. Morphology is graph-shaped

The domain model permits cavities and connections rather than assuming one vocal-tract tube. Early solvers may support only a subset of these topologies.

## A4. Physical quantities use explicit units

Physical task parameters should carry units. Numerical solver internals should use SI units unless a backend has a documented reason not to.

## A5. Source-filter separation is an approximation, not a permanent law

Early fidelity levels may separate acoustic source and tract filter. Later backends must be free to model bidirectional source-filter coupling.

## A6. Acoustic inversion is not assumed to be unique

Future audio-to-gesture inference should represent candidate hypotheses or distributions rather than claiming that one acoustic observation determines one true motor program.

## A7. Receiver and environment are downstream physical components

Radiation, near-field propagation, pinna/ear-canal effects, microphone response, and environment are not part of the motor representation. They may be introduced as later physical/observation stages.
