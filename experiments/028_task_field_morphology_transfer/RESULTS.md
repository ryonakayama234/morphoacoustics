# Experiment 028 results — frozen task-field morphology transfer

Issue: #64  
PR: #65  
Parent: #33

## Decision

**SUPPORT_TASK_TRANSFER**

The initial objective checks passed without changing the Experiment-027 task plan,
realizer constants, M1 morphology intervention, or scientific thresholds. Review
found incomplete enforcement of frozen implementation/body/threshold identity;
the stronger checks and rerun below supersede that enforcement claim.

## Review correction and rerun (2026-10-07)

All four findings from the review of `990e602` are addressed:

- The actual imported implementation/dependency files, live realizer functions,
  their code origins, and runtime constants are pinned to `frozen_reference.json`.
- M0 /a/ and /i/ area/length vectors are compared exactly with the audited record,
  independently of the live M0/M1 pair comparison and resonance peak oracle.
- The trajectory/artifact/temporal limits are local to 028 and exactly matched
  against the frozen oracle. A canonical oracle digest prevents simultaneous
  edits to the oracle and local limits from silently rescuing this experiment.
- The Wolfram source constructs and exports the complete consumed JSON schema.
  A fresh evaluation through the Wolfram Language evaluator on 2026-10-07
  reproduced every field exactly after JSON parsing, including all six sets of
  five peaks, all metrics, model metadata, and thresholds.

The strengthened baseline rerun remains **SUPPORT_TASK_TRANSFER**. All scientific
metrics and raw waveforms match the original run. No task, geometry parameter,
source, backend, oracle value, or scientific threshold was retuned.

The executed implementation identity SHA-256 is now:

```text
045b298d4feb6a559a65a643a79510b985ae5c2eb01baac85f588c23cc84f629
```

The historical `bf666498...` hash recorded below identifies only the parameter
dictionary, not the executed code. It is retained separately for traceability.

Regression checks cover the original body-specific activation-squaring example
(including a decorated replacement), uniform area drift in /a/, /i/, and both,
dependency-file changes, local and upstream relaxation of all three dynamic
limits, oracle-limit edits, and source waveform drift. All such conditions are
rejected; input-preflight violations produce no pressure waveforms. The narrow
claim boundary remains unchanged.

This supports the narrow claim:

> The frozen Experiment-027 normalized three-task motor plan transfers unchanged to the specified 1.10x axial-length PreparedMorphology, realizes in body-specific metric coordinates, produces body-dependent acoustics, and retains the preregistered body-relative /i/-like endpoint relation.

It does not establish arbitrary or non-self-similar morphology transfer, explicit physical infeasibility, perceptual phonetic transfer, or production motor-control APIs.

## Canonical execution provenance

First objective PR run:

- GitHub Actions scientific run: `37624920861`
- repository tests run: `37624920785`
- source head: `1972ce6f25cb6b6d23a0ccb7be5b2ca29173c8a2`
- output artifact: `experiment-028-output`
- artifact ID: `11483442530`
- artifact ZIP SHA-256: `61e0318414bd0e9b6b1c28a28db4e2d0cee43d7c8d6c0ce80e5ef107220a7e10`
- artifact size: 618676 bytes
- Python: 3.11.16
- NumPy: 2.4.6

Both the dedicated Experiment-028 workflow and the repository test workflow passed.

## Representation invariant: PASS

The canonical plan is the exact audited Experiment-027 plan:

```text
OPEN       location=0.3424849103873983  degree=0.5921764128805103
CONSTRICT  location=0.7167402543883221  degree=0.9235962908995712
CONSTRICT  location=1.0                 degree=0.04495226070116771
```

All tasks use onset 0.150 s and offset 0.350 s.

Canonical task-plan SHA-256 was identical for M0 and M1:

```text
17148dea27e59abfb626b149beebcc7893d4ff9ba04ce4cf3af9ad408ce8a7bf
```

The serialized plan:

- remained structurally clean;
- matched both the Experiment-027 and Experiment-028 frozen Wolfram task-plan records exactly;
- retained task-local schedule semantics.

For each task:

- onset activation = 0.0;
- midpoint activation = 0.5000000000000001;
- offset activation = 1.0.

Realizer SHA-256 was also identical for M0 and M1:

```text
bf666498ae0b0b555101dbe18fd371469911e6fc01b0d5e80ddd980afc964d22
```

The frozen realizer core matched the oracle exactly.

## Morphology intervention isolation: PASS

M0:

- 16 sections;
- section length = 0.010 m;
- total length = 0.160 m.

M1:

- 16 sections;
- section length = 0.011 m;
- total length = 0.176 m.

Observed total-length ratio:

```text
M1 / M0 = 1.0999999999999999
```

The calibrated /a/ and /i/ area values were exactly unchanged between M0 and M1. Section count, task representation, source, and backend were unchanged.

Thus the only prepared-body intervention was the preregistered axial section-length scaling.

## Body-specific physical realization: PASS

The same normalized task locations mapped to different metric coordinates:

| task | normalized location | M0 m | M1 m | M1/M0 |
|---|---:|---:|---:|---:|
| OPEN | 0.3424849103873983 | 0.05479758566198373 | 0.06027734422818210 | 1.1 |
| CONSTRICT | 0.7167402543883221 | 0.11467844070213154 | 0.12614628477234469 | 1.0999999999999999 |
| lip CONSTRICT | 1.0 | 0.16000000000000000 | 0.17600000000000000 | 1.0999999999999999 |

All scale residuals were inside the frozen `1e-12` tolerance.

At full task activation:

- M0 and M1 realized endpoint **area vectors were exactly equal**;
- M1/M0 section-length ratio was 1.10.

This is the expected self-similar physical result: the normalized task and cross-sectional realization remain the same while the metric axial body coordinates change.

## Independent Wolfram oracle: PASS

All six geometries matched the frozen 0.25 Hz-grid Wolfram oracle exactly.

| condition | P1 Hz | P2 Hz | P3 Hz | P4 Hz | P5 Hz |
|---|---:|---:|---:|---:|---:|
| M0 /a/ | 720.25 | 1288.50 | 2918.25 | 4196.00 | 4657.25 |
| M0 /i/ | 281.25 | 2309.25 | 3212.00 | 4102.00 | 4899.25 |
| M0 task endpoint | 275.00 | 2101.75 | 3164.75 | 4352.00 | 4817.75 |
| M1 /a/ | 655.00 | 1171.25 | 2653.00 | 3814.75 | 4233.75 |
| M1 /i/ | 255.50 | 2099.50 | 2920.25 | 3729.25 | 4454.00 |
| M1 task endpoint | 249.75 | 1910.75 | 2877.00 | 3956.50 | 4379.50 |

Observed error was **0.0 Hz** for every checked peak.

The M0 peaks also reproduced the audited Experiment-027 oracle exactly.

The current model has fixed attenuation in Np/m, so exact lossless 1/L scaling was not used as a primary Gate. The preregistered Wolfram reconnaissance found a maximum 0.25 Hz first-three-mode residual from exact 1/1.1 scaling.

## Body-relative acoustic intent retention: PASS

M0:

- /a/→/i/ P1/P2 distance = **1111.1487580427745 Hz**
- task→/i/ distance = **207.59410516678935 Hz**
- task→/a/ distance = **927.1586299010542 Hz**
- normalized error `e0 = 0.18682836448690684`

M1:

- /a/→/i/ P1/P2 distance = **1010.5683116444925 Hz**
- task→/i/ distance = **188.83756247102957 Hz**
- task→/a/ distance = **843.2602282213954 Hz**
- normalized error `e1 = 0.1868627388125155`

M1 task endpoint remained closer to M1 /i/ than M1 /a/.

Frozen retention Gate:

```text
e1 <= 0.20
```

Observed:

```text
0.1868627388125155 <= 0.20
```

PASS.

## Cross-body task-transfer stability: PASS

Frozen Gate:

```text
|e1 - e0| <= 0.005
```

Observed:

```text
|e1 - e0| = 3.437432560865483e-05
```

PASS.

This bound was fixed after the independent Wolfram reconnaissance and is an engineering transfer bound, not a perceptual threshold.

## Resolved body acoustic effect: PASS

Task endpoint P1/P2:

```text
M0 = 275.00 / 2101.75 Hz
M1 = 249.75 / 1910.75 Hz
```

Absolute changes:

- P1: **25.25 Hz**
- P2: **191.0 Hz**

Frozen resolved-effect requirement:

```text
at least one of P1/P2 > 5 * 0.5 Hz = 2.5 Hz
```

Both exceeded the requirement by a wide margin.

The maximum matched-time M0/M1 P1/P2 distance over the dynamic trajectory was:

```text
192.66178266589355 Hz
```

Thus the morphology intervention was acoustically observable rather than being cancelled by the unchanged task realization.

## Dynamic stability: PASS

M1 maximum adjacent 10 ms P1/P2 step normalized by the M1 /a/→/i/ endpoint distance:

```text
0.06614268085113642
```

Frozen limit:

```text
< 0.20
```

PASS.

All generated areas and P1/P2/P3 trajectory values were finite and positive.

### Waveform artifact diagnostic

M1:

- transition-region maximum adjacent-sample jump = **0.0007042153013083917 Pa**
- steady-endpoint maximum adjacent-sample jump = **0.0007100894178641525 Pa**
- artifact ratio = **0.9917276382269865**
- frozen limit = **< 3.0**

PASS.

### Temporal numerical floor

```text
d(T1, T1-ref) = 0.009399413606352729
```

Frozen limit:

```text
< 0.20
```

PASS.

The M0-vs-M1 normalized waveform difference was:

```text
0.4532106164124934
```

This is a diagnostic of the body effect, not an additional Gate.

Common-gain listening outputs did not clip.

## Source regression: PASS

The source matches the final audited Experiment-027 provenance:

- source = `lf_fixed`
- F0 identically 100 Hz: PASS
- stochastic noise exactly zero: PASS
- cycle-boundary jump / RMS = **4.406218549921945e-05**
- limit = **< 0.01**
- source float64 SHA-256:

```text
724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc
```

This is the same source hash recorded in the final Experiment-027 `RESULTS.md`.

## Gate summary

- representation invariant: PASS
- morphology intervention isolated: PASS
- independent Wolfram oracle and Experiment-027 baseline: PASS
- body-specific physical realization: PASS
- body-relative acoustic intent retention: PASS
- cross-body task-transfer stability: PASS
- dynamic numerical stability: PASS
- resolved body acoustic effect: PASS

Final decision: **SUPPORT_TASK_TRANSFER**.

## Interpretation

Experiment 027 established:

```text
task plan
  -> one calibrated body
  -> physical trajectory
  -> /i/-like acoustic endpoint
```

Experiment 028 adds:

```text
same exact task plan + same realizer
        |
        +--> M0 body coordinates -> M0 acoustics
        |
        +--> M1 body coordinates -> M1 acoustics
```

The task representation did not copy physical coordinates between bodies. The body changed the metric geometry and acoustics, while the body-relative endpoint relation remained nearly invariant.

This completes the **feasible-transfer half** of #33 R2 for the frozen 1.10x axial-length fixture.

## Limitations

- M1 is deliberately self-similar in the axial dimension;
- the area profile does not change across bodies;
- Experiment 016 already established a related scale-covariance principle for a simpler CONSTRICT task;
- this experiment's added evidence is specifically that the calibrated three-task phonetic candidate from Experiment 027 also transfers unchanged;
- exact 1/L acoustic scaling is not claimed because the model has fixed attenuation per meter;
- the /i/ body reference is an observer fixture, not a learned or inferred target;
- no human perceptual Gate is added;
- explicit physical infeasibility is not tested here.

A stronger non-self-similar morphology transfer remains useful later, but it is not required to interpret this narrow V3b result.

## Handoff

The next base-V3 experiment should be V3c:

```text
same frozen three-task plan
    + constrained PreparedMorphology
        -> explicit INFEASIBLE
        -> no physical fallback
        -> no acoustic backend call
```

That experiment should reuse the no-fallback methodology from Experiment 017 while keeping the calibrated three-task path and current failure taxonomy.

Do not close #33 until that explicit infeasibility path is established.
