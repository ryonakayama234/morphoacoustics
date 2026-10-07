# Experiment 027 preregistration — low-dimensional task field for calibrated /a/→/i/

Issue: #62  
Parent issue: #33  
Reference: #32 / Experiment 026

## Question

Can the Experiment-026 calibrated `/a/ -> /i/` physical/acoustic transition be approximated from a **small task-level command** without storing an exact area vector, section index, formant target, or waveform target in the canonical motor representation?

This experiment tests only the first V3 step on one calibrated body. Morphology transfer and deliberate `INFEASIBLE` fixtures are deferred.

## Hypothesis

**H_V3A:** Starting from the calibrated Experiment-026 `/a/` geometry, three normalized OPEN/CONSTRICT tasks can generate a continuous body-specific tract trajectory whose endpoint is acoustically close to the calibrated `/i/` endpoint, while preserving a clean task/physical representation boundary.

## Fixed upstream reference

Reuse Experiment 026 without changing its Gate or model:

- endpoint family: Experiment-023 Arai 16 x 10 mm fixtures;
- start state: calibrated `/a/`;
- target reference: calibrated `/i/`;
- source: Experiment-013 `lf_fixed`;
- F0: 100 Hz;
- Rd: 1.0;
- transition window: 0.150–0.350 s;
- progress: smoothstep `3u^2 - 2u^3`;
- primary control step: 5 ms;
- reference control step: 2.5 ms;
- primary acoustic hop: 256 samples;
- reference hop: 128 samples;
- Experiment-009 transfer and Experiment-012 preroll-edge renderer.

## Canonical candidate task plan

Frozen before Python execution:

```text
OPEN       location=0.3424849103873983  degree=0.5921764128805103
CONSTRICT  location=0.7167402543883221  degree=0.9235962908995712
CONSTRICT  location=1.0                 degree=0.04495226070116771
```

All three tasks have onset `0.150 s` and offset `0.350 s`. Each task's field activation is computed from that task's own `onset_s` / `offset_s`; the coincident values in this candidate are not allowed to degrade into one hidden global timing control.

The task plan may contain only:

- task kind;
- normalized location in `[0,1]`;
- dimensionless degree in `[0,1]`;
- onset / offset.

It must not contain:

- section index;
- exact area or diameter vector;
- mesh/node coordinate;
- F1/F2/formant target;
- waveform or spectrogram target;
- direct reference to the `/i/` target geometry.

## Experiment-local body-specific realizer

Do **not** promote this mapping to the production `Tract1DRealizer` in this PR.

For a prepared 1D body with `N` serial sections, map section slots to a normalized realization coordinate

```text
x_j = j / (N - 1),  j = 0 ... N-1.
```

This mapping is body/solver-side realization logic; `N` and section indices are not part of the canonical task plan.

Frozen constants:

```text
kappa = 1.5
sigma = 0.16
sigma_lip = 0.10
```

With Gaussian kernel

```text
K_sigma(x,l) = exp(-(x-l)^2 / (2 sigma^2)),
```

define the full-activation log-diameter field

```text
delta(x) = kappa * [
    + d_open      K_sigma(x, l_open)
    - d_constrict K_sigma(x, l_constrict)
    - d_lip       K_sigma_lip(x, 1)
].
```

At task activation `lambda(t)`:

```text
log D(x,t) = log D_a(x) + lambda(t) * delta(x).
```

Because circular section area is proportional to diameter squared, implementation may equivalently use

```text
log A(x,t) = log A_a(x) + 2 lambda(t) delta(x).
```

The resulting per-section area vector is a **realized physical state**, not a motor command.

## Frozen Wolfram oracle

`wolfram/v3a_oracle.wl` evaluates the fixed candidate; it does not optimize or refit it. `wolfram/v3a_oracle.json` is the Python-readable frozen oracle.

On the same 0.25 Hz segmented-tube frequency scan as Experiment 026:

| geometry | P1 Hz | P2 Hz | P3 Hz | P4 Hz | P5 Hz |
|---|---:|---:|---:|---:|---:|
| calibrated `/a/` | 720.25 | 1288.50 | 2918.25 | 4196.00 | 4657.25 |
| calibrated `/i/` | 281.25 | 2309.25 | 3212.00 | 4102.00 | 4899.25 |
| frozen 3-task endpoint | 275.00 | 2101.75 | 3164.75 | 4352.00 | 4817.75 |

P1/P2 distances:

- `/a/ -> /i/`: `1111.1487580427745 Hz`;
- task endpoint -> `/i/`: `207.59410516678935 Hz`;
- normalized endpoint error: `0.18682836448690684`;
- task endpoint -> `/a/`: `927.1586299010542 Hz`;
- task is `4.466208850950455x` farther from `/a/` than from `/i/` in P1/P2 space.

Peak tolerance is inherited from Experiment 026: `<= 0.5 Hz`.

These values were seen when selecting the candidate, so the `0.20` endpoint-error Gate below is an **engineering frozen-candidate Gate**, not a blind preregistered discovery threshold.

## Conditions

### R0 — V2 prescribed reference

Experiment-026 primary log-area `/a/ -> /i/` trajectory.

### R1 — task-field realization

The three canonical tasks above realized through the frozen experiment-local field on the same calibrated `/a/` body.

### R1-ref — temporal reference

R1 with the Experiment-026 2.5 ms control / 128-sample acoustic cadence.

## Recorded observables

Save at minimum:

- serialized canonical task plan;
- experiment-local realizer constants and mapping revision;
- generated geometry trajectory;
- start and task endpoint geometry diagnostics;
- P1/P2/P3 R0/R1 resonance trajectories at 10 ms cadence;
- matched-time R0/R1 P1/P2 distances;
- R0/R1/R1-ref raw pressure waveforms;
- R0-vs-R1 normalized waveform difference;
- R1-vs-R1-ref temporal numerical floor;
- artifact/reset diagnostics;
- source checksum and backend provenance;
- named R0/R1 listening WAVs under one common gain.

Human listening is exploratory and is not part of the primary Gate.

## Frozen Gate

### 1. Representation boundary

The serialized canonical task plan must contain only the allowed task fields above and none of the forbidden body/acoustic coordinates.

Failure: `REPRESENTATION_LEAK`.

### 2. Implementation / independent oracle

Require all:

- `lambda=0` returns the calibrated `/a/` start object exactly;
- generated endpoint areas reproduce the checked-in Wolfram endpoint-area oracle with `rtol=1e-12`, `atol=1e-15 m^2`;
- `/a/`, `/i/`, and task endpoint first five response peaks reproduce the Wolfram oracle within `0.5 Hz`;
- Experiment-013 fixed-LF source regression still passes.

Failure: `IMPLEMENTATION_MISMATCH`.

### 3. Geometry / trajectory / waveform stability

Require all:

- every generated analysed area is finite and positive;
- P1/P2/P3 are finite throughout R1;
- maximum adjacent 10 ms R1 P1/P2 step divided by the calibrated `/a/ -> /i/` P1/P2 distance is `< 0.20`;
- all rendered pressure arrays are finite;
- R1 transition-region max adjacent-sample jump / steady-endpoint max jump is `< 3.0`;
- normalized RMS difference `d(R1, R1-ref) < 0.20`;
- common-gain listening WAVs do not clip.

These are engineering stability bounds inherited from the Experiment-026 style of diagnostics, not psychoacoustic JNDs.

Failure: `NUMERICALLY_UNSTABLE`.

### 4. Representation sufficiency

Let

```text
e = distance_P1P2(task_endpoint, i) / distance_P1P2(a, i).
```

Require:

- `e <= 0.20`;
- the task endpoint is closer to calibrated `/i/` than to calibrated `/a/` in P1/P2 space.

Failure: `REPRESENTATION_INSUFFICIENT`.

### 5. No post-output refit

After Python execution, do not change task locations, degrees, `kappa`, `sigma`, `sigma_lip`, or Gate thresholds to rescue the result. A revised candidate requires a new experiment/revision.

## Decision

### ADOPT_TASK_FIELD_CANDIDATE

Only if all four objective Gates above pass.

Maximum claim:

> On the calibrated reference body, an exact target area-function need not be embedded in the canonical motor command: a frozen three-task normalized field can generate a continuous physical/acoustic transition to an `/i/`-like endpoint within the preregistered engineering error bound.

This is not yet evidence of task transfer across morphologies.

### REPRESENTATION_INSUFFICIENT

The task representation is clean and stable but cannot reach the frozen `/i/`-like acoustic endpoint criterion.

### IMPLEMENTATION_MISMATCH

Python realization does not reproduce the frozen independent Wolfram candidate.

### NUMERICALLY_UNSTABLE

The candidate endpoint may be plausible, but the continuous realization/rendering fails the frozen numerical/artifact sanity checks.

### REPRESENTATION_LEAK

Passing would require placing body-specific or acoustic target coordinates into the canonical task command.

## Non-goals

- second morphology;
- morphology transfer;
- deliberate `INFEASIBLE` fixture;
- arbitrary Japanese phonology;
- general Task Dynamics;
- production `Tract1DRealizer` promotion;
- Studio / X2;
- neural generation;
- FEM / FSI;
- naturalness optimization.

## Handoff on ADOPT

A passing result makes the candidate eligible for the next #33 step: same unchanged task plan on a second `PreparedMorphology`, including explicit FEASIBLE / INFEASIBLE separation. Promotion into production/integration code remains a separate decision.
