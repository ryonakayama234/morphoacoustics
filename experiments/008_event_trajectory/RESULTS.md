# Experiment 008 result

CI run: `experiment-008` on PR #16.

## Decision

**ADOPT** the representation candidate for M3 design work:

```text
Temporal representation candidate
  ├─ explicit events
  │    ├─ onset
  │    └─ offset
  └─ sampled continuous trajectory
       └─ activation / target values
```

This decision does **not** promote a core temporal API. It only resolves the representation question needed before M3.

## Gate results

All preregistered gates passed:

- step events exact across aligned and shifted grids: **PASS**;
- continuous trajectory not degraded by event semantics: **PASS**;
- Wolfram smoothstep interpolation bounds: **PASS**;
- acoustic observations finite at 300 / 500 / 1500 / 2500 Hz: **PASS**;
- smoothstep convergence preserved: **PASS**;
- schema remains morphology-independent with no body-specific state: **PASS**.

Observed aligned smoothstep pairwise convergence orders for the wide-body fixture were identical for both representations:

| refinement pair | sampled-only | event+trajectory |
|---|---:|---:|
| 10 → 5 ms | 1.8783214434 | 1.8783214434 |
| 5 → 2.5 ms | 1.9275915045 | 1.9275915045 |
| 2.5 → 1.25 ms | 2.0461291707 | 2.0461291707 |

The continuous candidate therefore retained the near-second-order behavior observed in Experiment 007.

## Discontinuous counterexample

For step activation, sampled-only interpolation continued to smear the discontinuity. For example, on the wide-body 10 ms aligned grid:

- sampled-only maximum activation error: `0.9`;
- sampled-only onset timing error: `4.5 ms`;
- sampled-only offset timing error: `4.5 ms`;
- sampled-only boundary-state max error: approximately `1.0`.

With explicit events under the same condition:

- maximum activation error: `0`;
- onset timing error: `0`;
- offset timing error: `0`;
- boundary-state error: `0`.

The event+trajectory candidate also produced zero physical/acoustic error for the step fixture because the explicit event semantics reconstructed the intended discontinuous state exactly.

## Acoustic sensitivity remains separate

The sampled-only step cases again showed that small temporal/activation errors cannot be treated as simple acoustic-error bounds near resonance. The 500 Hz input-impedance relative error could become very large while every acoustic value remained finite.

This supports keeping temporal representation accuracy and acoustic sensitivity as separate diagnostics in M3.

## Consequence for M3

M3 may now use the following minimal timing semantics as its starting representation:

- explicit onset/offset events for discontinuous boundaries;
- sampled continuous trajectories for activation/target evolution between events;
- no body-specific solver state in the temporal schema.

Gesture overlap, phase coordination, coarticulation and a public core temporal API remain deferred until M3 or later experiments provide evidence for the additional concepts.
