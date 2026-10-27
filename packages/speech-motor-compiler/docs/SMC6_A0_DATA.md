# SMC-6 A0 DATA — proposed private research objects and invariants

**DESIGN ONLY / NOT A JSON SCHEMA / NOT A PUBLIC ABI.** Reference [#219](https://github.com/ryonakayama234/morphoacoustics/issues/219), SMC5 `symbolic_bridge.py` at exact `894d2f0d68169e7f794d78be729057b3b31d6017`.

## Units and semantics (careful not to collapse categories)
- `TaskOccurrence` references SMC5 `MotorTask.task_id` and `TaskGoal` unchanged; distinct occurrences with the same `goal_kind` stay separate; explicitly shared SMC5 Task has exactly **one** ONSET/OFFSET pair even if associated with several PronunciationUnits.
- `TemporalEvent` = (`task_id`, `ONSET|OFFSET`); measurement is planned Task activation [ONSET,OFFSET), not acoustic or muscle activation.
- `HardDifferenceConstraint` = (`constraint_id`, `from_event`, `to_event`, `lower_s:Fraction`, `upper_s:Fraction`, `origin_provenance`). Meaning `lower_s≤t_to-t_from≤upper_s`. No float/exponent/NaN, implicit units, soft preference or phonetic source-truth.
- `TemporalStudyScenario` = immutable study ID/version, lane, finite horizon, minimum positive Task duration, original SMC5 receipts/sha, original exact constraints SHA, explicit *replacement rationale* when applicable, constraint set and provenance. A new study changes study digest, **not** inherited SMC5 candidate digest.
- `TemporalAnalysis` = SAT|UNSAT|INDETERMINATE|REJECTED, per-event earliest/latest **if finite/anchored**, constraint violations or unsatisfiable-cycle evidence, witness schedule (only when warranted), deterministic provenance and measured overlap/sensitivity fields with a clear source (witness versus range).
- `CoordinationPreference` is **future/unadopted**: weighted target intervals, rhythmic or speech evidence, selection objectives. Never silently mixed into the hard STN.
- `ActivationEnvelope` from one selected witness is start/end markers only. A continuous activation curve, stiffness, target interpolation, phase oscillators and physical geometry are separate research layers.

## Example candidate (illustrative names and numbers, NOT implemented shape)
```yaml
study_version: smc6-a0-design/0
lane: RESEARCH_OVERRIDE
smc5:
  candidate_digest: "<existing immutable digest>"
  original_exact_timing_digest: "<digest>"
timing_policy: SMC5_EXACT_TIMING_REPLACED_FOR_SYNTHETIC_STUDY
horizon_s: [3, 5]
min_task_duration_s: [1, 100]
constraints:
  - id: G1_start
    from: ORIGIN
    to: [G1, ONSET]
    lower_s: [0, 1]
    upper_s: [0, 1]
  - id: G1_duration
    from: [G1, ONSET]
    to: [G1, OFFSET]
    lower_s: [3, 10]
    upper_s: [3, 10]
  - id: G2_start_lag
    from: [G1, ONSET]
    to: [G2, ONSET]
    lower_s: [9, 50]
    upper_s: [11, 50]
  - id: G2_duration
    from: [G2, ONSET]
    to: [G2, OFFSET]
    lower_s: [19, 100]
    upper_s: [19, 100]
analysis_status: NOT_RUN
```
The above is **schema illustration**, not an admissible real SMC5 request; original timing needs a verified pinned source. Exact SMC5 Task IDs are long digest-derived identifiers, not illustrative `G1`/`G2`.

## Provenance and canonical identity
```mermaid
erDiagram
  CANONICAL_SMC5_REQUEST ||--|| SMC5_COMPILE_RECEIPT : validates
  SMC5_COMPILE_RECEIPT ||--|| SMC5_SYMBOLIC_PLAN : identifies
  SMC5_SYMBOLIC_PLAN ||--|{ TASK_OCCURRENCE : defines
  TASK_OCCURRENCE ||--|| TASK_GOAL : annotated
  TEMPORAL_STUDY_SCENARIO ||--|| SMC5_COMPILE_RECEIPT : references
  TEMPORAL_STUDY_SCENARIO ||--|{ HARD_DIFFERENCE_CONSTRAINT : owns
  HARD_DIFFERENCE_CONSTRAINT }o--|| TEMPORAL_EVENT : from
  HARD_DIFFERENCE_CONSTRAINT }o--|| TEMPORAL_EVENT : to
  TEMPORAL_STUDY_SCENARIO ||--|| TEMPORAL_ANALYSIS : analyzes
  TEMPORAL_ANALYSIS ||--o| WITNESS_SCHEDULE : if_valid
  TEMPORAL_ANALYSIS ||--o{ METRIC_OBSERVATION : records
```

Identity rules:
1. SMC5 `plan_digest` omits TaskGoal value ranges; SMC5 `candidate_digest` additionally commits to goals. SMC6 needs its **own** domain-separated hash over canonical scenario bytes + pinned original digests + resolved constraint semantics + solver/policy revision, never overload either inherited digest.
2. Ordering-insensitive constraint arrays canonicalize by typed IDs and rational numeric tuples; relation direction, task identity, original text order, chosen pronunciation and activation semantics remain meaningful. Never string-sort rational numbers as if numeric.
3. Repeated identical constraints with different IDs remain **distinct provenance** or are explicitly rejected by specified policy; never silently deduplicate evidence. A shared Task referenced by two pronunciation units is still one Task for timing/overlap computation.
4. `lane=COMPATIBILITY` imports original equalities/anchors as hard exact bounds. `lane=RESEARCH_OVERRIDE` must retain a frozen copy/hash of discarded original exact constraints, make the divergence conspicuous, and never represent the result as the original SMC5 timing verdict.
5. Refusal receipts should keep authenticated ingress semantic hash when valid; no plan/witness digest if schedule did not exist. Every metric includes calculation version, schedule identity or feasible-set scope, units, measurement provenance and evidence class.

## Measurand class
- **FORMAL_EXACT**: exact rational temporal algebra, graph satisfiability and derived overlap of a frozen synthetic witness. Report no floating-point "error bars" for exact arithmetic.
- **ESTIMATED_FROM_REFERENCE**: future EMA/ultrasound/video/manual annotation with units, calibration, segmentation variability, inter-rater error. Not measured in A0.
- **PHYSICAL_OBSERVATION**: future Core actuator/tract/flow/acoustic traces, with explicit port/body/model clocks. Not measured in A0.
- **SUBJECTIVE_OBSERVATION**: future creator listening and perceptual judgments. Not measured in A0.

## Explicit exclusions
No arbitrary Japanese reading generation, body-specific values or `INFEASIBLE` claims, phoneme-to-waveform synthesis, neural augmentation, source/tract physics, new Studio panel or public `MotorScore` schema. The term `relative onset fraction` must not be named `oscillator_phase`.
