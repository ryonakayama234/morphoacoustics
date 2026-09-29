# Experiment 007 — Sampling convergence before temporal API promotion

## Research question

When the Experiment 006 activation trajectory is represented only by discrete samples and linear reconstruction, what temporal resolution is required to preserve:

1. task-level activation,
2. morphology-specific realized constriction area, and
3. the downstream 500 Hz Fidelity-0 input-impedance observation?

The purpose is **not** to choose a convenient frame rate. The purpose is to decide whether a sampled trajectory is a defensible building block for a future temporal API, and to identify where explicit event semantics are still required.

## Pre-registered hypotheses

### H1 — smooth activation converges under linear reconstruction

For the 50 ms cubic smoothstep ramp

```text
s(x) = 3 x^2 - 2 x^3
```

the second derivative satisfies

```text
max |s''(x)| = 6,  x in [0, 1].
```

For a boundary-aligned sample spacing `h`, the standard linear-interpolation bound is therefore

```text
max |s - s_hat| <= (6/8) (h / 50 ms)^2.
```

The independently evaluated Wolfram oracle gives:

| h | activation absolute-error bound |
|---:|---:|
| 10 ms | 0.03 |
| 5 ms | 0.0075 |
| 2.5 ms | 0.001875 |
| 1.25 ms | 0.00046875 |

Observed smoothstep maximum error should remain below these aligned bounds and should show approximately second-order convergence.

### H2 — physical-area error follows the activation error exactly

Experiment 006 maps activation onto the local body geometry using

```text
A(t) = A_rest + activation(t) (A_target - A_rest).
```

Therefore

```text
|Delta A| = |A_target - A_rest| |Delta activation|
```

must hold up to floating-point roundoff for each body. Failure of this invariant is treated as an implementation error, not as a sampling result.

### H3 — acoustic error need not obey the activation bound

The 500 Hz observation is downstream of the segmented-tube transfer matrices, so the activation interpolation bound is **not** reused as an acoustic guarantee.

The tract is 0.17 m long and the Fidelity-0 closed/open quarter-wave relation gives

```text
f1 = c / (4 L) = 504.4117647058823 Hz
```

for `c = 343 m/s`. The chosen 500 Hz observation is therefore close to the first ideal resonance and is intentionally sensitive.

### H4 — discontinuous step timing is not a smooth-trajectory problem

Linear reconstruction of a sampled step produces a ramp around the discontinuity. Refining `h` should reduce the *duration/integrated* error, but the local maximum error near an unresolved discontinuity need not converge to zero in the same way as smoothstep.

This is the discriminating test for whether a future representation needs:

```text
explicit events + continuous sampled trajectory
```

rather than a sampled trajectory alone.

## Controlled conditions

The experiment reuses Experiment 006:

- gesture: `CONSTRICT(location=0.55, target_area=5e-5 m2)`;
- onset: 50 ms;
- offset: 350 ms;
- smoothstep attack/release: 50 ms;
- tract length: 0.17 m;
- wide-body rest area: `3e-4 m2`;
- narrow-body rest area: `2e-4 m2`;
- observation: absolute input impedance at 500 Hz;
- Fidelity-0 realizer and acoustic backend.

Interventions are:

- activation mode: `step`, `smoothstep`;
- sample spacing: 10, 5, 2.5, 1.25 ms;
- grid phase:
  - `aligned`: onset/offset lie on the sampling grid;
  - `shifted`: grid shifted by half a sample step;
- body: wide, narrow.

This gives 32 conditions.

## Important realization detail

For Experiment 007 the sampled activation is intentionally made the **only temporal information** passed into the experimental snapshot target. The temporary snapshot gesture is active across the evaluation window, including when activation is zero.

This deliberately prevents the existing exact `Gesture.onset_s` / `offset_s` values from rescuing a poor sampled reconstruction. Otherwise the experiment would not actually test whether a sampled trajectory preserves event timing.

This remains experiment-local and does not alter the production `GestureScore`, realizer, simulation, or acoustic contracts.

## Evaluation

The reference trajectory is evaluated analytically.

Each candidate trajectory is:

```text
analytic activation
    -> sample every h
    -> linear interpolation
    -> independent dense evaluation grid (0.1 ms)
```

At every dense evaluation time the experiment records:

- reference/reconstructed activation;
- reference/reconstructed constriction area;
- reference/reconstructed 500 Hz input impedance;
- absolute errors;
- acoustic relative error.

`summary.csv` additionally records maximum, mean, and time-integrated errors. Absolute and relative acoustic errors are both retained, and non-finite observations are counted rather than hidden.

## Independent Wolfram oracle

`wolfram/interpolation_oracle.wl` contains the independent calculation used to establish:

- `max |s''| = 6`;
- the four boundary-aligned interpolation bounds;
- the 504.4117647058823 Hz first quarter-wave resonance.

The evaluated constants are checked in as `wolfram/interpolation_oracle.json`. They are not generated by `morphoacoustics` code.

## Decision rule

The experiment does not automatically promote a temporal API.

The result is classified using:

```text
ADOPT / REJECT / MORE_DATA
```

For this experiment, sampled continuous activation is considered supported only if:

1. aligned smoothstep remains within the independent Wolfram bounds;
2. observed smoothstep convergence is approximately second-order;
3. the area-error invariant holds for both morphologies.

A trajectory-only representation is considered insufficient for discontinuities if step maximum error remains large while its integrated error shrinks as the grid is refined.

Even if the continuous trajectory candidate succeeds, the core temporal API is deferred if the step experiment indicates that explicit event semantics still need their own representation.

## Results

Run: GitHub Actions `experiment-007`, PR #12, 2026-09-29.

All 32 conditions completed successfully. All 500 Hz impedance observations were finite. The repository's ordinary pytest matrix on Python 3.11 / 3.12 / 3.13 and mypy type checking also passed without changing production APIs.

### Smoothstep activation

For the boundary-aligned smoothstep cases, measured maximum activation errors were:

| h | measured max error | Wolfram bound |
|---:|---:|---:|
| 10 ms | 0.024041472 | 0.03 |
| 5 ms | 0.00675 | 0.0075 |
| 2.5 ms | 0.001779648 | 0.001875 |
| 1.25 ms | 0.000456456 | 0.00046875 |

All four remain inside the independent pre-registered Wolfram bounds.

The pairwise observed convergence orders were:

```text
1.8326
1.9233
1.9630
```

They approach the expected second-order behavior as the grid is refined. This supports sampled linear reconstruction as a viable representation for the **continuous smooth component** of gesture activation.

### Morphology-specific realization

The physical-area error followed

```text
|Delta A| = |A_target - A_rest| |Delta activation|
```

for both prepared morphologies, with maximum residual only at floating-point roundoff (about `5.6e-20 m2` or less across the recorded cases).

This confirms that the observed body differences are the expected morphology-specific scaling of a shared task-level activation error rather than a hidden timing discrepancy.

### Discontinuous step activation

The step control behaved fundamentally differently.

For the half-step-shifted grids, maximum activation error remained:

```text
0.5, 0.5, 0.5, 0.5
```

for 10 / 5 / 2.5 / 1.25 ms, while integrated activation error decreased:

```text
0.005000 s
0.002500 s
0.001252 s
0.000628 s
```

The aligned case likewise retained a large local maximum error near the discontinuity (`0.99 -> 0.92` on the fixed 0.1 ms evaluation grid) while its integrated error shrank.

Therefore grid refinement narrows the corrupted time interval but does not make a linearly reconstructed trajectory faithfully represent an unresolved discontinuity in maximum norm.

**Interpretation:** exact onset/offset-like discontinuities should not be encoded only as ordinary continuous samples. A future temporal representation should test explicit event timing alongside the continuous trajectory.

### Acoustic sensitivity near 500 Hz

The acoustic observation was finite in every case, but its error did **not** converge monotonically with activation error.

A particularly clear example is the narrow-body, aligned smoothstep condition:

| h | max absolute impedance error (Pa s / m3) | max relative error |
|---:|---:|---:|
| 10 ms | `1.70e10` | 1.81 |
| 5 ms | `2.51e12` | 59.38 |
| 2.5 ms | `2.78e10` | 0.657 |
| 1.25 ms | `6.79e9` | 0.160 |

The 5 ms reconstruction is therefore acoustically much worse than the coarser 10 ms case despite having substantially smaller activation error.

This does **not** contradict the activation convergence result. The 500 Hz observation lies close to the ideal 504.41 Hz first quarter-wave resonance, so small geometry changes can move the snapshot across a high-sensitivity part of the impedance response.

The experiment therefore rejects any attempt to turn the activation interpolation bound into a downstream acoustic-error guarantee.

## Decision

```text
Decision: MORE_DATA

continuous sampled trajectory candidate: SUPPORTED
discontinuous event semantics: REQUIRED
core temporal API promotion: DEFER
```

The evidence supports a sampled trajectory for smooth continuous gesture activation, but not as the entire temporal representation.

Before a core temporal API is promoted, the next discriminating experiment should test:

```text
explicit onset/offset events
        +
sampled continuous activation
```

and separately characterize the near-resonance acoustic sensitivity across frequency and morphology rather than relying on the single 500 Hz observation.

This is a successful research result: the experiment narrowed the representation choice without prematurely changing the core API.

## Outputs

Running the experiment writes:

```text
experiment-007-output/
  timeseries.csv
  summary.csv
  decision.json
```

`timeseries.csv` is the detailed 32-condition trace. `summary.csv` contains condition-level error metrics. `decision.json` records the pre-registered checks and recommendation.

## Run

From the repository root:

```bash
python experiments/007_gesture_sampling_convergence/run.py \
  --output-dir experiment-007-output
```

## Scope boundary

This experiment does **not**:

- synthesize a waveform;
- add a glottal/source model;
- solve a true time-domain acoustic PDE;
- promote smoothstep to a domain invariant;
- change `GestureScore`;
- change `simulate_snapshot()`;
- change the Fidelity-0 contract.

The acoustic values are still a sequence of independent frequency-domain snapshots.
