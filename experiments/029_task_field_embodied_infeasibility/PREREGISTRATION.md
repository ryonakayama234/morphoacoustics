# Experiment 029 preregistration — frozen phonetic task plan at a body reachability boundary

Issue: #67  
Parent: #33  
Prerequisites: Experiment 027 / PR #63 and Experiment 028 / PR #65

## Question

Can the exact audited three-task phonetic plan remain unchanged while a PreparedMorphology capability boundary alone changes the outcome from FEASIBLE to explicit INFEASIBLE, with no physical or acoustic fallback?

This experiment integrates the Experiment-017 infeasibility methodology with the calibrated task-field path established by Experiments 027–028.

## Frozen task plan

Experiment 027/028 exactly:

```text
0 OPEN       location=0.3424849103873983  degree=0.5921764128805103
1 CONSTRICT  location=0.7167402543883221  degree=0.9235962908995712
2 CONSTRICT  location=1.0                 degree=0.04495226070116771
```

All tasks use onset 0.150 s and offset 0.350 s.

The canonical command does not contain an articulator id, reach endpoint, section index, area vector, metric coordinate, formant target, waveform target, or fallback target.

## Upstream frozen preflight

Before evaluating any V3c condition, reuse Experiment 028's frozen-input preflight. It must confirm that the audited Experiment-027 task-field implementation, transitive dependencies, M0 calibrated body, source generator, renderer, schedule, and frozen upstream oracle still match the accepted Experiment-028 record.

If that preflight fails, Experiment 029 cannot make a new infeasibility claim.

## Experiment-local capability policy

Do not promote this policy to production schema/API.

PreparedMorphology carries two capability articulators in the oral cavity:

- `oral-shaper` for interior task fields;
- `lip` for a task whose normalized location is exactly `1.0`.

Assignment is realization-side:

```text
task.location == 1.0  -> lip
otherwise             -> oral-shaper
```

Supported task kinds are exactly `OPEN` and `CONSTRICT`.

Reach intervals are inclusive.

## Fixed physical fixture

Every condition uses the same calibrated Experiment-027 M0 `/a/` rest geometry:

- 16 sections;
- 0.010 m per section;
- total length 0.160 m;
- identical section areas;
- identical cavity;
- identical lip reach `[0.95, 1.0]`;
- identical oral-shaper reach start `0.0`;
- identical task plan, task-field realizer, source and acoustic renderer.

Only `oral-shaper.reachable_end` changes.

## Conditions

| condition | oral-shaper reachable_end | central-task normalized margin | metric margin at 0.160 m | expected |
|---|---:|---:|---:|---|
| M_plus | 0.75 | +0.03325974561167788 | +0.005321559297868462 m | FEASIBLE |
| M_boundary | 0.7167402543883221 | 0 | 0 | FEASIBLE |
| M_minus | 0.70 | -0.016740254388322162 | -0.002678440702131546 m | INFEASIBLE |

The exact-boundary condition is FEASIBLE because the contract is inclusive.

## Independent Wolfram oracle

`wolfram/v3c_oracle.wl` computes the frozen margins and status sign rule independently of Python:

```text
margin = reachable_end - requested_location
margin >= 0 -> FEASIBLE
margin <  0 -> INFEASIBLE
```

`wolfram/v3c_oracle.json` is the checked-in machine-readable result.

Python margin/status values must match within `1e-15`.

## Utterance-level preflight

For this experiment, the complete frozen task plan is checked against body capability before rendering begins.

- valid + supported + reachable -> FEASIBLE
- valid + supported + unreachable -> INFEASIBLE
- unsupported task kind / missing required actuator kind -> UNSUPPORTED
- corrupted fixture/request -> experiment preflight failure

M_minus contains a future scheduled task outside the reachable set, so the whole performance is INFEASIBLE. No partial audio is permitted.

This utterance-level behavior is experiment-local.

## FEASIBLE execution

M_plus and M_boundary execute the unchanged Experiment-027 task-field mapping.

Because they differ only in unused positive reach slack:

- full-activation physical endpoints must be exactly equal;
- complete raw pressure waveforms must be exactly equal;
- instrumented acoustic transfer-call counts must be equal and > 0.

The instrumented renderer must also reproduce the audited Experiment-027 renderer output exactly on the feasible fixture.

## INFEASIBLE no-fallback contract

M_minus must produce exactly:

```text
status = INFEASIBLE
issue.code = LOCATION_UNREACHABLE
issue.gesture_index = 1
physical endpoint = None
waveform = None
acoustic transfer-call count = 0
```

It may not:

- clamp location to 0.70;
- reduce degree;
- drop task 1;
- realize a nearby state;
- call acoustics then discard the result;
- synthesize fallback audio.

## Frozen objective Gate

### 1. Representation invariance

- current task plan equals the Experiment-028 frozen task plan;
- task plan is identical for every condition;
- no body-specific field is inserted into the canonical command.

Failure: `REPRESENTATION_LEAK` or `IMPLEMENTATION_MISMATCH` when a clean global plan simply differs from the frozen accepted plan.

### 2. Intervention isolation

M_plus / M_boundary / M_minus differ only in `oral-shaper.reachable_end`.

Failure: `MORPHOLOGY_INTERVENTION_INVALID`.

### 3. Oracle reproduction

- task plan / policy / fixture constants match the V3c oracle;
- normalized and metric margins match within `1e-15`;
- predicted statuses match.

Failure: `IMPLEMENTATION_MISMATCH`.

### 4. Feasibility boundary

Require:

- M_plus FEASIBLE;
- M_boundary FEASIBLE;
- M_minus INFEASIBLE;
- no condition INVALID or UNSUPPORTED.

Failure: `FEASIBILITY_BOUNDARY_FAILED` or `BACKEND_UNSUPPORTED`.

### 5. Failure attribution

M_minus must report only `LOCATION_UNREACHABLE` for task index 1.

Failure: `FAILURE_ATTRIBUTION_INCONSISTENT`.

### 6. No fallback

M_minus:

- physical endpoint is None;
- waveform is None;
- acoustic calls = 0.

Failure: `ACOUSTIC_FALLBACK_LEAK`.

### 7. Capability null control

M_plus and M_boundary:

- physical endpoint exactly equal;
- waveform exactly equal;
- acoustic call counts equal and > 0.

Failure: `CAPABILITY_NULL_CONTROL_FAILED`.

## Decision

### SUPPORT_PHONETIC_EMBODIED_INFEASIBILITY

Only if all frozen Gates pass without post-output changes.

Maximum claim:

> For the audited calibrated three-task phonetic path, changing only a PreparedMorphology reachability limit can change the reachable task set: reachable bodies retain the same physical/acoustic realization, while the unreachable body returns explicit INFEASIBLE and stops before physical/acoustic fallback.

## Non-goals

- biological articulator anatomy;
- force/stiffness or collision mechanics;
- non-self-similar transfer;
- perceptual phonetic identity;
- production realizer/schema promotion;
- CoordinationPlan;
- Script compiler;
- Studio;
- FEM/FSI;
- neural fallback.

## Handoff

If Experiment 029 passes, V3a + V3b + V3c collectively satisfy the base #33 task-realization / transfer / explicit-infeasibility slices. Then re-evaluate #33 for closure before proceeding to #20 / #11.
