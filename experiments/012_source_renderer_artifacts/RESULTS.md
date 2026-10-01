# Experiment 012 results — source / renderer artifact attribution

## Decision

**MIXED**.

The blind-listening artifact separated into two independently supported causes under the preregistered tests:

1. the frequent pitch-synchronous `snap` is primarily explained by the sharp explicit harmonic source;
2. the extreme startup transient is independently explained by finite-signal short-time renderer edge handling.

The objective cleanup also preserved the Experiment-011 coordination effect above its numerical-stability gate.

## H1 — periodic snap source attribution: PASS

### Source sharpness

With the common 10 ms file-boundary envelope applied, the current source had:

- max `|dx/dt| / RMS`: `17671.9788`

The objectively selected `smooth_flow_oq0.6` source had:

- max `|dx/dt| / RMS`: `1118.62971`

This is about a 93.7% reduction in the preregistered source sharpness metric.

The independent untapered Wolfram source oracle agreed with the Python implementation to essentially floating-point precision for crest factor and derivative metrics; the maximum reported relative discrepancies were below `1e-9` for the checked quantities.

### Fixed-tract periodic-transient metric

With the same fixed tract and preroll renderer:

- current `current40_p1.2`: pitch-phase peak ratio `8.05284`
- `harmonic10_p1.2`: `4.42682`
- `harmonic40_p2.0`: `8.02305`
- `smooth_flow_oq0.6`: `2.16836`

Only `smooth_flow_oq0.6` satisfied both preregistered >=50% reduction gates, so it was selected without reference to listening preference.

### Pitch period vs renderer hop

For the current source, changing only hop size produced:

| hop samples | pitch-phase ratio | hop-phase ratio |
|---:|---:|---:|
| 256 | 8.05284 | 1.44572 |
| 128 | 8.05298 | 1.44146 |
| 64 | 8.05298 | 1.44098 |

The sharp pattern stayed dominated by the 480-sample / 100 Hz pitch period rather than following the renderer hop. This supports source attribution for the frequent snap.

## H2 — startup renderer-edge attribution: PASS

Using the current source and fixed tract:

- `legacy_edge` startup peak / steady RMS: `1236.23981`
- `preroll_edge`: `5.99426`
- preroll / legacy ratio: `0.00484879`

The one-frame zero-preroll/crop experiment reduced the startup statistic by about 99.5%, far beyond the preregistered 50% gate.

This does not prove that preroll is the final production renderer design. It establishes that the very large startup transient is an edge-context artifact rather than a necessary property of the source or tract model.

## H3 — coordination survives objective cleanup: PASS

Using the objectively selected `smooth_flow_oq0.6` source plus preroll edge handling:

- sequential-vs-overlap normalized RMS difference: `0.220098`
- sequential discretization difference: `0.0118195`
- overlap discretization difference: `0.0123151`
- effect / max discretization perturbation: about `17.9x`

All outputs were finite. The effect remains above both preregistered gates (`> 0.01` and `> 5x` maximum tested discretization perturbation).

The larger normalized effect than Experiment 011 must not be interpreted as perceptual improvement by itself: the source waveform and edge context changed, so the normalized RMS scale is not directly a naturalness score.

## Interpretation

The previous blind listening observation was scientifically useful because it exposed two model/renderer artifacts that the original coordination experiment was not designed to diagnose.

The evidence now supports this decomposition:

```text
frequent ~10 ms snap
    -> explicit harmonic source sharpness

extreme beginning transient
    -> short-time renderer edge context

sequential vs overlap difference
    -> still present after both cleanup interventions
```

Therefore Experiment 011's narrow coordination conclusion does not appear to depend on either audible artifact.

## What this does not promote

This experiment does **not** promote `smooth_flow_oq0.6` as the production vocal-fold model. It is an experiment-local low-artifact source surrogate used to establish attribution.

A future source-model study may compare explicit glottal-flow models, reduced vocal-fold oscillators, or source-filter coupling under separate scientific criteria.

Likewise, the successful preroll test supports fixing renderer boundary handling, but does not by itself choose the final streaming/linear-convolution architecture.

## Human follow-up

Prepare blinded listening comparisons using the generated artifacts and ask separately:

- Is the frequent `パツン` actually reduced?
- Is the extreme beginning click reduced?
- Does the smoother source retain or improve the emerging voice-like quality?
- Does the sequential/overlap creative difference remain audible?

Human results are recorded as perceptual evidence and do not alter the already-preregistered attribution decision.
