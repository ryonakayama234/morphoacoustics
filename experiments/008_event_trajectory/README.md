# Experiment 008 — explicit events + sampled continuous trajectory

Issue: [#13](https://github.com/ryonakayama234/morphoacoustics/issues/13)

## Research question

Experiment 007 showed two different behaviors:

- sampled smooth continuous activation converged as the grid was refined;
- a discontinuous step retained a non-vanishing maximum error because onset/offset semantics were represented only by samples.

This experiment compares two temporal representations without changing the production temporal API:

1. **sampled-only** — reconstruct everything by linear interpolation of sampled activation;
2. **event + trajectory** — retain onset/offset as explicit events and sample only the continuous activation/target trajectory between them.

The candidate schema intentionally contains no body-specific solver state.

## Preregistered hypotheses

- **H1**: explicit onset/offset events preserve discontinuous boundaries independently of sample-grid alignment.
- **H2**: adding event semantics does not degrade smoothstep interpolation convergence.
- **H3**: the same event/trajectory schema is reusable for both prepared morphologies.
- **H4**: the candidate carries enough model-independent timing information for M3 to trace Gesture, realization and acoustic observations on one time axis.

A successful experiment promotes only the **representation candidate** for M3 design work. It does not promote a core temporal API.

## Fixed fixture

The experiment reuses the Experiment 007 causal fixture:

- one `CONSTRICT` Gesture;
- onset `0.05 s`, offset `0.35 s`;
- smoothstep attack/release `0.05 s` when continuous mode is used;
- target area `5e-5 m²` at normalized location `0.55`;
- two uniform 0.17 m prepared tracts with rest areas `3e-4 m²` and `2e-4 m²`;
- sample steps `10 / 5 / 2.5 / 1.25 ms`;
- aligned and half-step-shifted grids.

The evaluation grid is generated independently from the candidate sample grids.

## Interventions

For each body, activation mode, sample spacing and grid phase:

- reconstruct with `sampled-only`;
- reconstruct with `event+trajectory`.

`event+trajectory` uses the same sampled smooth trajectory as the baseline, but gates it with explicit onset/offset semantics. For a true step, the interior state is defined by the explicit active interval rather than a linearly smeared boundary.

## Measurements

### Event accuracy

- onset absolute timing error;
- offset absolute timing error;
- event ordering;
- state error immediately before/after onset/offset.

### Continuous trajectory accuracy

- maximum activation error;
- integrated activation error;
- observed pairwise convergence order;
- comparison to the independent Wolfram linear-interpolation bound.

### Physical propagation

- realized constriction-area error.

### Acoustic propagation

Input-impedance magnitude is observed independently at:

- 300 Hz;
- 500 Hz;
- 1500 Hz;
- 2500 Hz.

These frequencies deliberately include observations near the first several resonant regions of the existing 0.17 m Fidelity-0 fixture. Activation error is **not** treated as a bound on acoustic error.

All non-finite acoustic results are counted and surfaced.

## Independent Wolfram oracle

`wolfram/event_trajectory_oracle.wl` checks the analytic smoothstep

```text
s(x) = 3 x^2 - 2 x^3
```

and `max |s''(x)| = 6` on `[0,1]`. For a 50 ms ramp, the standard linear-interpolation bound

```text
(max |f''| / 8) h^2
```

gives activation absolute-error bounds:

| h | bound |
|---:|---:|
| 10 ms | 0.03 |
| 5 ms | 0.0075 |
| 2.5 ms | 0.001875 |
| 1.25 ms | 0.00046875 |

The Wolfram file is an analytic reference, not a reimplementation of the Python transfer-matrix loop.

## Decision rule

The runner writes `decision.json`.

`ADOPT` requires all of the following:

- explicit-event step boundaries are exact for every aligned/shifted grid;
- smooth continuous trajectory error is not worse than sampled-only under the same condition;
- aligned smoothstep results satisfy the Wolfram bounds;
- observed smoothstep convergence remains better than order 1.5 over the tested refinement pairs;
- all selected acoustic observations remain finite;
- the candidate schema remains morphology-independent and embeds no body-specific state.

Otherwise the decision is `MORE_DATA`.

`REJECT` is not emitted automatically from one numerical failure; a failed gate remains evidence and should be reviewed before deciding whether the representation itself is wrong or the experiment is insufficient.

## Reproduction

```bash
python experiments/008_event_trajectory/run.py \
  --output-dir experiment-008-output
```

Outputs:

- `summary.csv`
- `timeseries.csv`
- `decision.json`

## Scope boundary

This experiment does **not** implement:

- a core temporal API;
- general Gesture overlap or phase coordination;
- coarticulation;
- time-domain waveform synthesis for M3;
- Studio timeline UI.
