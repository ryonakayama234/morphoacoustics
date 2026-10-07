# Experiment 028 preregistration — frozen task-field morphology transfer

Issue: #64  
Parent: #33  
Prerequisite: Experiment 027 / PR #63

## Question

Can the exact frozen Experiment-027 canonical three-task plan and task-field realizer be reused on a second prepared morphology whose only intervention is a 1.10x axial-length scaling, producing a body-specific physical/acoustic realization while retaining the same body-relative /i/-like endpoint relation?

This experiment is V3b / TASK_TRANSFER. Explicit physical infeasibility is deferred to V3c.

## Frozen representation

The canonical task plan is byte-for-byte the Experiment-027 plan:

```text
OPEN       location=0.3424849103873983  degree=0.5921764128805103
CONSTRICT  location=0.7167402543883221  degree=0.9235962908995712
CONSTRICT  location=1.0                 degree=0.04495226070116771
```

All tasks use `onset_s=0.150`, `offset_s=0.350`.

Frozen realizer core:

```text
field_space = log_diameter
x_j         = j/(N-1)
kappa       = 1.5
sigma       = 0.16
sigma_lip   = 0.10
```

Each task uses its own sampled smoothstep activation from its own onset/offset. No body-specific refit is allowed.

Canonical task data must not contain section index, absolute axial coordinate, exact area/diameter vector, F1/F2 target, waveform target, or body-specific target geometry.

## Morphologies

### M0

Experiment-027 calibrated primary body:

- 16 sections;
- every section length = 0.010 m;
- total length = 0.160 m;
- calibrated /a/ areas are the start body;
- calibrated /i/ geometry is observer-only.

### M1

Apply exactly one body intervention:

- same 16 sections;
- every section length = 0.011 m;
- total length = 0.176 m;
- same calibrated /a/ start areas;
- same source/backend;
- same task plan;
- same task-field constants.

For evaluation only, the body-specific /i/ observer reference uses the calibrated /i/ areas with the same 0.011 m section lengths.

The /i/ reference is never passed into the task realizer.

## Metric task coordinates

For diagnostic reporting only,

```text
x_metric = normalized_location * total_tract_length.
```

Frozen Wolfram values:

| task | M0 m | M1 m |
|---|---:|---:|
| OPEN | 0.05479758566198373 | 0.06027734422818210 |
| CONSTRICT | 0.11467844070213154 | 0.12614628477234469 |
| lip | 0.16000000000000000 | 0.17600000000000000 |

Every M1/M0 ratio is 1.10. These metric coordinates are observations, not canonical commands.

## Independent Wolfram oracle

`wolfram/v3b_oracle.wl` evaluates the frozen task plan with the same lossy segmented-tube model used by Experiments 027/026. The checked-in JSON is frozen before Python execution.

### M0 peaks

| geometry | P1 | P2 | P3 | P4 | P5 |
|---|---:|---:|---:|---:|---:|
| /a/ | 720.25 | 1288.50 | 2918.25 | 4196.00 | 4657.25 |
| /i/ | 281.25 | 2309.25 | 3212.00 | 4102.00 | 4899.25 |
| task endpoint | 275.00 | 2101.75 | 3164.75 | 4352.00 | 4817.75 |

### M1 peaks

| geometry | P1 | P2 | P3 | P4 | P5 |
|---|---:|---:|---:|---:|---:|
| /a/ | 655.00 | 1171.25 | 2653.00 | 3814.75 | 4233.75 |
| /i/ | 255.50 | 2099.50 | 2920.25 | 3729.25 | 4454.00 |
| task endpoint | 249.75 | 1910.75 | 2877.00 | 3956.50 | 4379.50 |

Endpoint error ratio:

```text
e0 = 0.18682836448690684
e1 = 0.1868627388125155
|e1-e0| = 0.00003437432560865483
```

The frozen transfer Gate uses:

- `e1 <= 0.20`;
- `|e1-e0| <= 0.005`.

The 0.005 value is an engineering transfer bound fixed after the Wolfram reconnaissance, not a blind discovery threshold.

The current model has fixed attenuation in Np/m, so exact lossless `1/L` frequency scaling is **not** a primary Gate. The largest first-three-mode residual from exact 1/1.1 scaling in the Wolfram reconnaissance is 0.25 Hz.

## Conditions

- **T0 / M0** — audited Experiment-027 task realization on the calibrated body.
- **T1 / M1** — the same task realization on the 1.10x axial-length body.
- **T1-ref** — M1 with 2.5 ms control cadence and 128-sample acoustic hop.

## Required records

- canonical task plan and digest;
- realizer parameters and digest;
- M0/M1 morphology specs and isolated diff;
- normalized and metric task coordinates;
- M0/M1 generated physical trajectories;
- M0/M1 P1/P2/P3 trajectories;
- M0/M1 task endpoint peaks and body-relative endpoint error ratio;
- M0/M1 raw pressure;
- M1 temporal-reference pressure;
- matched-time M0/M1 acoustic differences;
- source/backend provenance;
- finite/positivity/artifact checks;
- independent Wolfram parity.

## Frozen Gate — SUPPORT_TASK_TRANSFER

Requires all:

1. **Representation invariant**
   - the task plan is structurally clean;
   - it exactly matches Experiment 027 and the Wolfram frozen plan;
   - M0 and M1 use identical task-plan and realizer digests.

2. **Morphology intervention isolated**
   - section count remains 16;
   - /a/ and /i/ area values are exactly unchanged across M0/M1;
   - every section length changes only from 0.010 to 0.011 m;
   - source/backend are unchanged.

3. **Body-specific physical realization**
   - total length changes 0.160 -> 0.176 m;
   - each metric task coordinate scales by 1.10 within `1e-12`;
   - realized task endpoint area values remain equal while section lengths differ by 1.10, demonstrating the same normalized task on a distinct body coordinate system.

4. **Independent oracle**
   - M0 reproduces the Experiment-027 baseline;
   - all M0/M1 /a/, /i/, and task-endpoint first-five peaks match the frozen Wolfram oracle within 0.5 Hz.

5. **Body-relative acoustic intent retention**
   - M1 task endpoint is closer to M1 /i/ than M1 /a/ in P1/P2 space;
   - `e1 <= 0.20`.

6. **Transfer stability**
   - `|e1-e0| <= 0.005`.

7. **Dynamic numerical stability**
   - M1 areas and P1/P2/P3 are finite throughout;
   - max adjacent 10 ms P1/P2 step / M1 /a/-to-/i/ endpoint distance is < 0.20;
   - artifact jump ratio < 3.0;
   - `d(T1,T1-ref) < 0.20`;
   - common-gain listening outputs do not clip.

8. **Resolved morphology effect**
   - M0 and M1 task endpoint P1/P2 are not identical;
   - at least one of P1/P2 changes by more than `5 * 0.5 Hz = 2.5 Hz`.

## Failure classes

Ordered scientific categories:

- `REPRESENTATION_LEAK`
- `MORPHOLOGY_INTERVENTION_INVALID`
- `IMPLEMENTATION_MISMATCH`
- `MOTOR_REALIZATION_FAILED`
- `ACOUSTIC_INTENT_RETENTION_FAILED`
- `TASK_TRANSFER_FAILED`
- `NUMERICALLY_UNSTABLE`
- `MORPHOLOGY_EFFECT_UNRESOLVED`

## No post-output rescue

### Enforcement clarification after review (2026-10-07)

The original hypotheses, tasks, body parameters, oracle values, and thresholds
above remain unchanged. `frozen_reference.json` pins the audited `990e602` input
implementation, transitive experiment dependencies, acoustic/physical source
files, live realizer function origins/source, runtime constants, calibrated M0
area/length vectors, execution cadence, and source waveform digest.

Before rendering, any M0 mismatch is `MORPHOLOGY_INTERVENTION_INVALID`; any
implementation/oracle/threshold/cadence mismatch is `IMPLEMENTATION_MISMATCH`.
No waveform is produced by a rejected preflight. Source waveform identity is
also checked in the implementation Gate. Dynamic thresholds are local to 028
and must exactly match the frozen oracle. The oracle itself is checked against
the frozen canonical JSON digest.

This is stricter enforcement of the existing registration, not a revised
scientific hypothesis. The reference must not be regenerated from changed live
dependencies to rescue a result. A legitimate upstream implementation change
requires a new experiment/revision and explicit scientific review.

After Python execution, do not change:

- task kind/location/degree/schedule;
- kappa/sigma/sigma_lip;
- M1 axial scale;
- oracle tolerance;
- endpoint-retention or transfer thresholds.

A revised hypothesis requires a new experiment/revision.

## Claim boundary

A pass supports only:

> The frozen Experiment-027 normalized three-task motor plan transfers unchanged to the specified 1.10x axial-length PreparedMorphology, realizes in body-specific metric coordinates, produces body-dependent acoustics, and retains the preregistered body-relative /i/-like endpoint relation.

It does not establish arbitrary morphology transfer, non-self-similar transfer, explicit infeasibility, perceptual phonetic transfer, natural speech, production schema promotion, FEM/FSI, or TTS.
