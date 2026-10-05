# Experiment 022 — Objective results

Issue: #51

Implementation PR: #52

Independent oracle: `wolfram/shared_body_multigesture_oracle.wl` and frozen `wolfram/shared_body_multigesture_oracle.json`.

## Decision

```text
SUPPORT_SHARED_BODY_MULTI_GESTURE_INTERACTION
```

The preregistered Experiment-022 workflow completed successfully on Python 3.11.16 / NumPy 2.4.6.

## Gate summary

All primary gates passed:

- representation isolation: PASS
- request / fixture validity: PASS
- shared equilibrium oracle: PASS
- independent-overlay null falsification: PASS
- exact propagation / continuity: PASS
- shared-body transient interaction: PASS
- contradictory task rejection: PASS
- acoustic oracle: PASS
- acoustic effect above numerical floor: PASS

## Equilibrium result

Shared simultaneous equilibrium versus independent equilibrium overlay:

```text
shared-vs-overlay L2
candidate: 0.18391987934434068
Wolfram:   0.18391987934434048

normalized nonadditivity
candidate: 0.1459188979585512
Wolfram:   0.14591889795855104
```

The compatible shared solution preserves both exact task targets to floating-point precision:

```text
max shared task residual = 1.1102230246251565e-16
```

The independent overlay does not satisfy the simultaneous targets:

```text
Gesture A residual = -0.09737827715355801
Gesture B residual = -0.12160228898426328
```

Maximum equilibrium-state error versus the independent Wolfram oracle:

```text
1.6653345369377348e-16
```

## Dynamic shared-state result

Primary time: 200 ms, after 120 ms of overlap.

```text
normalized shared-vs-null state difference
candidate: 0.12290066358145624
Wolfram:   0.12290066358145611

shared-vs-null state L2
candidate: 0.15490711301603682
Wolfram:   0.15490711301603667

shared-vs-null velocity L2
candidate: 0.6125910030146813
Wolfram:   0.6125910030146819
```

Maximum transient oracle error:

```text
1.8041124150158794e-15
```

The pre-overlap 80-ms regression remained effectively identical:

```text
shared/null error = 1.1102230246251565e-16
```

Exact-transition invariants:

```text
max split-propagation error   = 1.3322676295501878e-15
max zero-duration switch jump = 8.881784197001252e-16
```

Event-level normalized shared-vs-null differences:

| time | normalized difference |
|---:|---:|
| 80 ms | 1.3212480414219335e-16 |
| 200 ms | 0.12290066358145624 |
| 280 ms | 0.04771911772168379 |
| 400 ms | 0.004342750241695568 |

The interaction therefore appears when both tasks share the body, persists after the first Gesture releases, and decays after both release.

## Contradictory task positive control

The contradictory pair requested two different exact values at the same task coordinate.

Observed:

```text
rank(C)       = 1
rank([C | d]) = 2
diagnostic    = TASK_CONFLICT
```

The conflict path recorded:

```text
dynamics_called     = false
acoustics_called    = false
last_wins_used      = false
averaging_used      = false
target_coercion_used = false
```

Thus the experiment does not silently repair the contradictory request.

## Acoustic result

Primary 200-ms resonance comparison:

| mode | shared candidate | null candidate | candidate effect | Wolfram effect |
|---:|---:|---:|---:|---:|
| 1 | 404.70 Hz | 356.55 Hz | +48.15 Hz | +48.15788061797083 Hz |
| 2 | 1699.75 Hz | 1725.00 Hz | -25.25 Hz | -25.25661690100215 Hz |
| 3 | 2343.40 Hz | 2236.00 Hz | +107.40 Hz | +107.4002448437489 Hz |

Maximum acoustic oracle errors:

```text
candidate grid: 0.020564954220390064 Hz
reference grid: 0.003503727403085577 Hz
```

All shift signs matched the Wolfram oracle.

Effect / numerical-floor ratios:

```text
mode 1:  963x
mode 2:  505x
mode 3: 2148x
minimum: 505x
```

The downstream acoustic distinction is therefore comfortably above the preregistered observer floor.

## Interpretation

This experiment supports only the following reduced claim:

> In this 10-section fixture, two compatible task-level constrictions acting on one shared material-conditioned stateful body produce a physical trajectory that cannot be reproduced by independently realizing each Gesture and adding the deformations afterward; the difference agrees with an independent Wolfram oracle and remains observable acoustically. Contradictory exact task demands can also be rejected explicitly before dynamics or acoustics.

It does not establish:

- natural human coarticulation;
- biological tongue/jaw/lip competition;
- general Task Dynamics;
- calibrated tissue mechanics;
- muscle activation;
- FEM/XPBD/FSI validity;
- phonetic identity;
- a production multi-Gesture API.
