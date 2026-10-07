# Experiment 029 results — phonetic task-field embodied infeasibility

Issue: #67  
PR: #68  
Parent: #33

## Decision

**SUPPORT_PHONETIC_EMBODIED_INFEASIBILITY**

All frozen objective Gates passed without changing the canonical task plan, reach endpoints, capability-assignment policy, oracle, or thresholds after Python execution.

This supports the narrow claim:

> For the audited calibrated three-task phonetic path, changing only a PreparedMorphology reachability limit can change the reachable task set: reachable bodies retain the same physical/acoustic realization, while the unreachable body returns explicit INFEASIBLE and stops before physical/acoustic fallback.

It does not establish biological articulator limits, force/contact mechanics, arbitrary morphology infeasibility, perceptual phonetic identity, or production schema/API readiness.

## Canonical execution provenance

Initial scientific execution:

- GitHub Actions scientific run: `37702867705`
- source head: `2817a1c9f4d970ebdc3cf1b4a72aacaf5b094a24`
- output artifact: `experiment-029-output`
- artifact ID: `11518032253`
- artifact ZIP SHA-256: `d5f554bbc360f7f35ee40d87f372045a1385a12fda3cf58d884b9953469ea13b`
- Python: 3.11.17
- NumPy: 2.4.6

Repository CI on the same head:

- tests workflow: `37702867986`
- Python 3.11: PASS
- Python 3.12: PASS
- Python 3.13: PASS
- typecheck: PASS

## Codex review hardening

The first ready-for-review head received two Codex findings:

- **P1:** Experiment 028's runner/preflight had to be pinned *before import*, not merely checked after its live preflight function had executed.
- **P2:** the Experiment-029 workflow path filters had to include the transitive Experiment-008 and Experiment-011 dependencies recorded in the frozen implementation manifest.

Both findings were addressed without changing any scientific task value, morphology reach endpoint, oracle value, or Gate threshold.

Implementation hardening:

- Experiment-028 runner blob is now verified before dynamic import/execution;
- the Git blob hash uses the canonical `blob <size>\0<bytes>` representation;
- push and pull-request workflow filters include Experiments 008 and 011.

An intermediate CI attempt exposed an implementation mistake in the new pre-import guard (missing constant definition) and failed before Experiment 029 executed. That code defect was corrected; no scientific parameter was changed.

Final post-review-fix validation before this results update:

- scientific workflow: `37703773885` — PASS
- repository tests/typecheck: `37703773989` — PASS

These runs preserve the same scientific decision and outputs while exercising the strengthened audit boundary.

## Frozen upstream preflight: PASS

Experiment 029 reused Experiment 028's frozen-input preflight and additionally pinned the merged Experiment-028 runner blob.

Observed:

```text
upstream_frozen_preflight = true
local_frozen_preflight    = true
```

Therefore the V3c result was not obtained after silently changing the accepted Experiment-027 task-field implementation, M0 body, source generator, renderer, schedule, upstream oracle, or V3c oracle.

The canonical task-plan SHA-256 was:

```text
17148dea27e59abfb626b149beebcc7893d4ff9ba04ce4cf3af9ad408ce8a7bf
```

## Independent Wolfram reach oracle: PASS

A fresh evaluation of `wolfram/v3c_oracle.wl` regenerated the checked-in task plan, fixture/policy schema, margins and expected statuses.

The target task is the interior CONSTRICT at:

```text
task index = 1
location   = 0.7167402543883221
```

Observed versus frozen Wolfram values:

| condition | reachable_end | normalized margin | metric margin | observed |
|---|---:|---:|---:|---|
| M_plus | 0.75 | +0.03325974561167788 | +0.005321559297868462 m | FEASIBLE |
| M_boundary | 0.7167402543883221 | 0 | 0 | FEASIBLE |
| M_minus | 0.70 | -0.016740254388322162 | -0.002678440702131546 m | INFEASIBLE |

Every margin and status check passed within the frozen `1e-15` tolerance.

The exact-boundary condition confirms the inclusive contract:

```text
reachable_start <= task.location <= reachable_end
```

## Representation invariance: PASS

All conditions used the exact same frozen Experiment-027/028 task plan:

```text
OPEN       location=0.3424849103873983  degree=0.5921764128805103
CONSTRICT  location=0.7167402543883221  degree=0.9235962908995712
CONSTRICT  location=1.0                 degree=0.04495226070116771
```

All three tasks retained onset `0.150 s` and offset `0.350 s`.

The canonical plan contains no:

- articulator id;
- reach endpoint;
- section index;
- area/diameter vector;
- metric coordinate;
- formant target;
- waveform/spectrogram target;
- fallback target.

Body capability remained on the PreparedMorphology / realization side.

## Morphology intervention isolation: PASS

Every condition shared:

- the same calibrated Experiment-027 M0 `/a/` rest geometry;
- 16 × 0.010 m sections;
- identical section areas;
- identical cavity;
- identical `lip` capability `[0.95, 1.0]`;
- identical `oral-shaper.reachable_start = 0.0`;
- identical task plan;
- identical task-field mapping;
- identical source and acoustic path.

Only:

```text
oral-shaper.reachable_end
```

changed.

## Feasibility boundary: PASS

Observed pattern:

```text
M_plus      -> FEASIBLE
M_boundary  -> FEASIBLE
M_minus     -> INFEASIBLE
```

No condition returned `INVALID` or `UNSUPPORTED`.

Task reach traces also confirmed:

- task 0 OPEN remained reachable in every body;
- task 1 CONSTRICT alone crossed the oral-shaper boundary;
- task 2 outlet CONSTRICT remained reachable through the unchanged lip capability.

Thus the negative result is attributable to the intended body reach constraint rather than a general backend capability failure.

## Failure attribution: PASS

M_minus produced exactly one feasibility issue:

```text
code          = LOCATION_UNREACHABLE
gesture_index = 1
message       = oral-shaper cannot reach normalized location 0.7167402543883221
```

It did not clamp the task location to 0.70, weaken the degree, drop the task, or substitute another articulator.

## No physical/acoustic fallback: PASS

M_minus produced:

```text
physical endpoint present = false
waveform present          = false
acoustic transfer calls   = 0
```

No physical endpoint hash and no waveform hash exist for the negative condition.

This directly verifies that the performance stopped at the body feasibility boundary instead of synthesizing a nearby plausible output.

## Capability null control: PASS

M_plus and M_boundary differ only in unused positive reach slack. Their realized output was exactly identical.

### Physical endpoint

Both endpoint hashes:

```text
645c236c3232ed668159f37b5f79d0e742bde2ecc89c59fb7b61d93acd78f7c6
```

Result:

```text
physical_endpoints_exactly_equal = true
```

### Raw waveform

Both raw float64 waveform hashes:

```text
1b0ca7e7215af42428a1b11512e9a7547876c9f3b458c4d73c93a711800eb30e
```

Result:

```text
raw_waveforms_exactly_equal = true
```

### Acoustic evaluation count

```text
M_plus calls      = 102
M_boundary calls  = 102
equal and > 0     = true
```

The instrumented feasible renderer also matched the accepted Experiment-027 renderer output exactly.

This negative control demonstrates that unused reach capacity does not leak into physical/acoustic output while the requested task remains inside the reachable set.

## Gate summary

- upstream frozen preflight: PASS
- local frozen preflight: PASS
- representation invariance: PASS
- morphology intervention isolation: PASS
- Wolfram oracle reproduction: PASS
- feasibility boundary: PASS
- failure attribution: PASS
- no physical/acoustic fallback: PASS
- capability null control: PASS
- instrumented renderer / audited renderer parity: PASS

Final decision:

**SUPPORT_PHONETIC_EMBODIED_INFEASIBILITY**

## Interpretation

The three V3 slices now form a causal sequence:

```text
Experiment 027 / V3a
same low-dimensional task plan
    -> calibrated physical/acoustic realization on one body

Experiment 028 / V3b
same task plan
    -> different PreparedMorphology
    -> body-specific physical/acoustic realization
    -> body-relative /i/-like intent retained

Experiment 029 / V3c
same task plan
    -> reachable body      -> physical state + acoustics
    -> unreachable body    -> explicit INFEASIBLE
                             -> no physical/acoustic fallback
```

Experiment 029 does not make the reach boundary mechanically or biologically realistic. Its contribution is the causal contract: a body capability can determine whether a valid supported phonetic task is realizable, without rewriting the canonical task or fabricating output.

## Claim boundary

This result does not establish:

- biological tongue/lip reachability;
- muscle-force or stiffness limitations;
- collision/contact feasibility;
- arbitrary morphology transfer;
- perceptual vowel identity across arbitrary bodies;
- production realizer/schema readiness;
- general Task Dynamics;
- source-filter FSI;
- natural speech.

It establishes only the preregistered V3c reachability fixture for the audited three-task calibrated path.

## Handoff

With V3a, V3b and V3c all objectively supported, the next action is to re-evaluate parent #33 against its base completion criteria.

If the base V3 claim is now satisfied, close #33 with the explicit claim boundary and proceed to:

1. #20 CoordinationPlan;
2. #11 limited Script compiler;
3. Studio #10 live synthesis.

PHONETIC_TRANSFER with body-specific task adaptation remains a later revision and must not be conflated with this unchanged-task TASK_TRANSFER result.
