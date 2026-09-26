# Experiment 006 — Gesture timecourse before temporal API promotion

## Research question

Can temporal gesture activation be explored on top of the existing snapshot architecture without prematurely changing the domain or backend contracts?

The experiment treats activation as a candidate interpretation layer between a morphology-independent `GestureScore` and morphology-specific snapshot realization. It deliberately does **not** define the final temporal API.

## Hypothesis

1. The current binary semantics can be reproduced as a `step` activation.
2. A bounded smooth activation can produce a continuous attack/release trajectory while leaving the existing `Realizer.realize_snapshot()` and `AcousticBackend.simulate_snapshot()` contracts unchanged.
3. The same activation value can map to different physical areas in different prepared morphologies, preserving the distinction between task-level timing and body-specific realization.

## Intervention

Use one unchanged task-level gesture:

```text
CONSTRICT(
    location = 0.55,
    target_area = 5e-5 m2,
    onset = 0.05 s,
    offset = 0.35 s,
)
```

Compare two experiment-local activation hypotheses:

- `step`: activation is 1 throughout the active interval and 0 otherwise, matching the current active/inactive interpretation.
- `smoothstep`: a 50 ms attack and 50 ms release use the cubic Hermite function

  `s(x) = 3 x^2 - 2 x^3`, for `x` clamped to `[0, 1]`.

For each requested time, the experiment converts activation into a temporary body-specific target area between that body's local rest area and the canonical gesture target, then calls the existing snapshot simulation unchanged.

That interpolation is an **experimental realization hypothesis**, not a new domain invariant.

## Morphologies

Two prepared serial tracts differ only in uniform rest cross-sectional area:

- `wide-body`: `3e-4 m2`,
- `narrow-body`: `2e-4 m2`.

Both use the same 0.17 m tract length, articulator reach, gesture score, acoustic backend, and observation request.

At half activation, the experiment therefore predicts different body-specific instantaneous areas:

- `wide-body`: `1.75e-4 m2`,
- `narrow-body`: `1.25e-4 m2`.

This is intentional: activation is shared, physical realization is not.

## Observation

For times from 0 to 0.4 s, `run.py` prints CSV rows containing:

- activation mode,
- body,
- time,
- activation,
- realized area at the constriction location,
- magnitude of the 500 Hz input impedance observation.

The acoustic observation remains a sequence of independent Fidelity-0 frequency-domain snapshots. It is **not** a waveform and does not claim to be a true time-domain acoustic solution.

## Controlled variables

Within each body/mode comparison, tract length, gesture target, gesture location, articulator reach, acoustic backend, frequency request, and sample times are fixed. Between the two bodies, only prepared rest area changes.

## External mathematical check

The chosen cubic smoothstep was checked with Wolfram before implementation:

- `s(0) = 0`, `s(1) = 1`,
- `s'(0) = s'(1) = 0`,
- `s'(x) = 6 x (1 - x) >= 0` on `[0, 1]`,
- its range on `[0, 1]` is `[0, 1]`,
- `s(0.5) = 0.5`.

Reference: Wolfram Function Repository, `SmoothStep`: https://resources.wolframcloud.com/FunctionRepository/resources/SmoothStep/

## Expected result

`step` should reproduce the present instantaneous target behavior while active. `smoothstep` should start from rest at onset, approach the target continuously, hold the target through the middle of the interval, and return continuously toward rest before offset.

At equal smooth activation, the two bodies should have different physical areas because activation is translated through each prepared rest geometry.

## Acceptance criterion

The experiment is considered successful if:

1. all snapshots remain `FEASIBLE`,
2. `step` matches the current binary activation semantics,
3. `smoothstep` satisfies the expected 0 → 1 → 0 attack/hold/release trajectory,
4. half activation yields `1.75e-4 m2` for `wide-body` and `1.25e-4 m2` for `narrow-body`,
5. no production `domain`, `realization`, `simulation`, or `acoustics` contract needs to change.

Success does **not** automatically promote smoothstep into the canonical temporal model. It only establishes that temporal activation can be investigated cleanly above the snapshot primitive. A later experiment should test temporal sampling convergence before a core trajectory API is introduced.

## Run

From the repository root in the project environment:

```bash
python experiments/006_gesture_timecourse/run.py
```
