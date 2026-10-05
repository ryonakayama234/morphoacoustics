# Experiment 020 results

## Decision

**SUPPORT_STATEFUL_FINITE_TIME_REALIZATION**

for the narrow G1-B claim:

> In this fixed reduced morphology/material fixture, a single scalar stateful finite-time task model makes duration- and history-dependent physical/acoustic predictions that differ from, and converge toward, the Experiment-019 quasi-static equilibrium while preserving the same task intent.

This does not establish general Task Dynamics or biological articulator mechanics.

## CI execution

GitHub Actions `experiment-020` completed successfully on:

- Python 3.11.16
- NumPy 2.4.6

Objective run: `37201709319`.

## Representation and request validity

The timing-independent task-intent SHA-256 remained:

```text
6b2aeb5e728064923c80d66998d52c9effea6cc6f89d117b0c7634de4b9c441c
```

Full score hashes differed only because Gesture offset/duration was intentionally varied.

Every duration-specific CONSTRICT request remained FEASIBLE under the production Fidelity-0 validator and resolved to zero-based section 6.

## R1 equilibrium regression

The Experiment-019 baseline equilibrium was recovered without production changes.

Maximum state error versus the independent Wolfram equilibrium:

```text
1.11e-16
```

Maximum R1 resonance errors:

- candidate 0.05-Hz grid: `0.0220155 Hz`
- reference 0.01-Hz grid: `0.00201548 Hz`

Both remain within the preregistered 0.05 / 0.01 Hz gates.

## R2 dynamic oracle

The largest error over all preregistered activation, velocity, task-error, and 50/100-ms release-state values was:

```text
1.78e-15
```

against the independent Wolfram analytic oracle.

Measured offset-minus task errors were:

| duration | omega T | task error fraction |
|---:|---:|---:|
| 40 ms | 1 | 0.7357588823 |
| 80 ms | 2 | 0.4060058497 |
| 120 ms | 3 | 0.1991482735 |
| 200 ms | 5 | 0.0404276820 |
| 320 ms | 8 | 0.0030191637 |

The errors decrease monotonically toward the R1 zero-error equilibrium prediction.

## Exact propagation consistency

One exact propagation over each duration and four exact propagations over one quarter of that duration agreed with maximum state discrepancy:

```text
8.88e-16
```

This is below the preregistered `1e-12` consistency gate.

## Event continuity

The target switched from active to rest at offset without resetting state.

Maximum measured offset event jump across both activation and velocity:

```text
0.0
```

Thus the R2 state itself is continuous across the event.

## Post-release memory

The minimum R2 activation 50 ms after offset was:

```text
0.3020883131
```

The minimum activation 100 ms after offset was:

```text
0.1514092698
```

Both exceed the preregistered 0.10 memory discriminator, even though the current input is already `u=0`.

The 50/100-ms release states also depend systematically on the prior Gesture duration, demonstrating history dependence rather than a prescribed function of current input alone.

## Physical convergence toward R1

The R2 geometry L2 distance from the R1 equilibrium decreased monotonically:

| duration | L2 distance from R1 |
|---:|---:|
| 40 ms | 0.7119674 |
| 80 ms | 0.3928773 |
| 120 ms | 0.1927086 |
| 200 ms | 0.0391204 |
| 320 ms | 0.00292154 |

This is the intended finite-time -> quasi-static limit.

## Acoustic oracle

Across all five durations and three modes:

- maximum candidate-grid error vs Wolfram: `0.0247009 Hz`
- maximum reference-grid error vs Wolfram: `0.00470092 Hz`

Both pass the 0.05 / 0.01 Hz gates.

## R1 vs R2 acoustic discrimination

Every duration/mode remained resolved above the numerical floor.

The weakest case was the 320-ms second mode:

```text
observed R2-R1 shift = -0.95 Hz
numerical floor       = 0.05 Hz
effect / floor        = 19x
```

The preregistered minimum was 5x.

The absolute R2-R1 acoustic distance decreased monotonically with duration for all three modes, as predicted by convergence toward the R1 equilibrium.

## Settling reference

The independent Wolfram oracle gives:

```text
95% settling time = 189.7545807 ms
99% settling time = 265.5340827 ms
```

These are fixture diagnostics for `omega=25 s^-1`, not biological timing claims.

## Interpretation

Experiment 020 distinguishes a stateful finite-time model from both:

1. the Experiment-019 quasi-static equilibrium model; and
2. the earlier prescribed smooth activation trajectories.

The new evidence is specifically:

- duration-dependent task error;
- state continuity across an event;
- post-release memory under identical current input;
- monotone convergence to the quasi-static physical/acoustic limit.

The result does not show that this critically damped scalar model is the correct biological control law. It shows that a minimal stateful model class is measurable, independently reproducible, and causally distinguishable from the project's current quasi-static and prescribed-trajectory alternatives.

## Claim boundary

Still unsupported:

- general Task Dynamics;
- calibrated biological inertia or damping;
- muscle or force-level actuation;
- articulator competition;
- coupled multi-task dynamics;
- nonlinear/viscoelastic tissue mechanics;
- FEM / XPBD / FSI;
- phonetic validity;
- perceptual naturalness;
- promotion into the production temporal API.

## Next falsification layer

The next meaningful step is no longer another single-task duration sweep.

A stronger candidate is:

```text
single-task stateful dynamics
    -> two simultaneous/overlapping task states
    -> competition/coupling intervention
```

before connecting the dynamic realizer to V3 calibrated phonetic task realization.
