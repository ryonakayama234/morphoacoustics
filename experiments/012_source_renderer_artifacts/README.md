# Experiment 012 — source / renderer artifact attribution (A1)

## Why this experiment exists

Experiment 011 produced a scientifically useful coordination result, but blind listening exposed frequent small `snap` / `パツン` sounds in both conditions. Because the artifact is common to sequential and overlap Takes, it can contaminate creative/perceptual comparison without being caused by coordination itself.

The current source is an explicit deterministic harmonic inlet volume-velocity signal with `F0 = 100 Hz`, 40 phase-aligned sine harmonics and amplitude proportional to `k^-1.2`. The Experiment-011 renderer is a Hann-windowed, short-time, quasi-stationary transfer filter with 1024-sample frames and 256-sample hop at 48 kHz.

Post-hoc inspection suggested two separable phenomena:

1. frequent small sharp components approximately every 10 ms, matching the 100 Hz pitch period rather than the 5.33 ms hop;
2. a much larger startup transient near the beginning of the rendered signal.

This experiment preregisters a direct source-vs-renderer attribution test before changing any production API.

## Research questions

1. Is the frequent periodic snap primarily caused by the spectral/phase structure of the explicit harmonic source?
2. Is the startup transient primarily caused by short-time renderer edge handling?
3. Can the Experiment-011 sequential-vs-overlap effect survive after using a smoother source and safer renderer edge handling?

## Candidate source conditions

All candidates use the same `F0 = 100 Hz`, 48 kHz sample rate, 0.50 s duration and the same peak inlet volume velocity (`1e-5 m^3/s`).

- `current40_p1.2`: current 40-harmonic phase-aligned source, amplitude `k^-1.2`.
- `harmonic10_p1.2`: same law, first 10 harmonics only.
- `harmonic40_p2.0`: 40 harmonics with stronger rolloff `k^-2.0`.
- `smooth_flow_oq0.6`: experiment-local smooth nonnegative glottal-flow surrogate; in each 10 ms period it is `sin^2(pi * phase / 0.6)` for normalized phase `< 0.6`, and zero otherwise. This is a comparison waveform, not a physiological LF-model claim.

A 10 ms onset/offset envelope is applied consistently to all candidates for rendered comparisons.

## Independent Wolfram preregistration

A Wolfram calculation over the **steady periodic core before the common onset/offset envelope**, normalized to equal peak, gave the following source-only reference values before Python implementation. The envelope is intentionally excluded from this oracle so that source-shape differences are not confounded with the shared file-boundary taper.

| source | crest factor | max `|dx/dt|` / RMS | one-sided energy ratio >= 2 kHz |
|---|---:|---:|---:|
| current40_p1.2 | 1.48558845 | 17472.1481 | 0.00518197 |
| harmonic10_p1.2 | 1.65867154 | 5690.88222 | approximately 0 |
| harmonic40_p2.0 | 1.38003295 | 3634.51511 | 0.0000368463 |
| smooth_flow_oq0.6 | 2.10818511 | 1103.75558 | 3.86e-8 |

The Python experiment must independently reproduce the qualitative ordering on the untapered core. Rendered metrics are computed separately after the same 10 ms envelope is applied to every candidate; oracle values are not copied into implementation logic.

## Work plan

### A. Source-only metrics

For each source, compute:

- RMS and crest factor;
- max absolute first difference converted to per-second derivative, normalized by RMS;
- one-sided spectral energy fraction above 2 kHz;
- pitch-period phase profile of absolute derivative.

### B. Fixed-tract renderer test

Render every source through one fixed prepared tract using the same Experiment-009 acoustic assumptions. No Gesture is active. If the approximately 10 ms snap signature persists with a fixed tract and follows the source candidate, it is not a coordination artifact.

The preregistered fixed-tract periodic-transient metric is:

`pitch_phase_peak_ratio = max(mean(|Δp| grouped by sample-index mod 480)) / mean(|Δp|)`

computed on the 50–450 ms steady interval. A sharper pitch-synchronous event gives a larger value.

### C. Hop test

For the current source, render the same fixed tract with hop sizes 256, 128 and 64 samples while keeping frame size 1024.

For each output compute the same phase-peak ratio using both the 480-sample pitch period and the relevant hop period. The source-attribution condition is considered satisfied when the pitch-phase ratio is larger than the hop-phase ratio for all three hop sizes; this rule is fixed before running Python results.

### D. Startup-edge test

Compare two renderer edge modes with otherwise identical source/tract/frame/hop settings:

- `legacy_edge`: current finite signal starts at renderer sample zero;
- `preroll_edge`: prepend and append one frame of zeros, run the same overlap-add path, then crop back to the original duration.

The startup statistic is:

`startup_peak_over_steady_rms = max(|p| in first 20 ms) / RMS(p in 50–200 ms)`.

### E. Coordination-effect retention

Using the best artifact-reduction candidate selected by preregistered objective metrics (not listening preference), rerun Experiment-011 `sequential` and `overlap` with:

- candidate source;
- preroll edge handling;
- the same Gesture timings, body, acoustic model, control grid and hop.

Measure sequential-vs-overlap normalized RMS difference and discretization sensitivity.

## Preregistered hypotheses

### H1 — source attribution

At least one smoother source reduces both source max-derivative/RMS and fixed-tract periodic-transient metric by at least 50% relative to `current40_p1.2`, while the pitch-phase ratio remains larger than the hop-phase ratio for current-source fixed-tract renders at hop sizes 256, 128 and 64.

### H2 — renderer edge attribution

`preroll_edge` reduces `startup_peak_over_steady_rms` by at least 50% relative to `legacy_edge` without non-finite output.

### H3 — coordination survives cleanup

With the objectively selected cleaned source + preroll renderer:

- sequential-vs-overlap normalized RMS difference remains `> 0.01`;
- the effect remains `> 5x` the larger tested discretization difference;
- all output is finite.

## Objective source selection rule

Among source candidates that:

1. reduce fixed-tract `pitch_phase_peak_ratio` by >= 50%, and
2. reduce source derivative/RMS by >= 50%,

select the candidate with the smallest fixed-tract `pitch_phase_peak_ratio`. Ties are broken by lower >=2 kHz energy ratio.

This selection is intentionally independent of listening preference.

## Attribution decision

- `SOURCE_CONFIRMED`: H1 passes and H2 fails; startup behavior is recorded separately.
- `RENDERER_CONFIRMED`: H1 fails and H2 passes with evidence that hop/edge structure dominates.
- `MIXED`: H1 and H2 both pass — source structure explains the frequent snap while renderer edge handling independently explains startup artifact.
- `MORE_DATA`: the preregistered tests do not separate the causes.

H3 is reported separately and does not change the attribution label.

## Scope boundary

This experiment does not claim:

- physiological vocal-fold dynamics;
- an LF-model implementation;
- self-oscillating vocal folds or source-filter back-coupling;
- perceptual naturalness from objective metrics alone;
- that source cleanup solves all audible artifacts.

## Human role

After objective attribution and source selection are complete, prepare blinded listening candidates. Human listening will answer a separate creative question: whether the `パツン` is reduced without losing the emerging voice-like quality. It will not retroactively change the scientific attribution gates.

## Reproduction

```bash
python experiments/012_source_renderer_artifacts/run.py \
  --output-dir experiment-012-output
```

The experiment must record source metrics, fixed-tract metrics, hop tests, edge tests, cleaned sequential/overlap artifacts, decision JSON and environment provenance.
