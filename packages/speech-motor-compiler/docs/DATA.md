# SMC-3 DATA — candidate contract (Gate A)

## Canonical symbol-level vocabulary
- `PronunciationUnit(unit_id, symbol, start_offset, end_offset)` identifies a **candidate** phoneme for a source codepoint span. Different unit IDs may refer to the same source span.
- `MotorTask(task_id, goal_kind, capability_requirements)` identifies one body-neutral symbolic motor goal. No organ coordinates.
- `TaskAssociation(unit_id, task_id)` is a many-to-many link. Repeated references to one task ID do **not** duplicate the task.
- `EventAnchor(task_id, event, time_s)` optionally sets a synthetic absolute event time (relative to a local zero); necessary to resolve all times rather than just differences.
- `CouplingConstraint(source_task_id, source_event, target_task_id, target_event, lag)` describes equality `target_event_time = source_event_time + lag`. Events are ONSET/OFFSET and lag is an exact `fractions.Fraction` of seconds in this synthetic fixture only.
- `SymbolicPlan` aggregates source/units/tasks/associations/couplings, without physical fields.
- `ValidationReport` has STRUCTURALLY_VALID or INVALID and deterministic diagnostics. Neither state represents body feasibility or natural articulation.

## Invariants
- Unique nonblank source unit/task IDs; Unicode Python codepoint span [start,end) within original unchanged text.
- TaskAssociation endpoints must exist; duplicate associations rejected. Reject unit with no task and orphan task; do not fabricate associations.
- Coupling endpoints must exist; event names must be ONSET/OFFSET; lag must be exact Fraction. Contradictory graph equalities and nonpositive determined task duration fail closed.
- Plan fields must not include `CreatureSpec`, `GestureScore`, organ positions, F0, pressure, audio, waveform, body realization, or solver state.
- Canonical receipt should sort order-insensitive collections, preserve the exact Unicode script, and encode Fraction as [numerator,denominator]. Schema is provisional research-only.

## Synthetic many-to-many witness
```text
        G1 G2 G3
P1       1  1  0
P2       0  1  1
```
A single shared G2 node must be preserved across P1/P2. Wolfram proves that strict exactly-one Task per phoneme cannot cover all three task columns in this two-row abstract witness. This does not assert actual phonetic gestures.

## Existing integration boundary
Existing SMC-2 imports `morphoacoustics.integration.shared_timeline`. This sibling package will not; future Core integration belongs to a separate adapter and review.

## 2026-10-22 v0 candidate implementation
`Event` is ONSET/OFFSET, `lag_s` and `time_s` use exact `Fraction`. `validate_plan` checks symbolic references, duplicate links and internally inconsistent equalities; its success is only `STRUCTURALLY_VALID` (never capability or physical clearance). `resolve_timing` additionally requires every onset and offset connected to at least one common anchored origin and returns synthetic `TimingReport` only. A plan with valid associations but no anchors is structurally valid and has an explicitly invalid/unresolved timing report. There is no automatic phoneme-to-task inference.

### Implementation receipt
Type-check invariants include no accidental aliasing of `TaskAssociation` iteration variable and `EventAnchor` iteration variable; the first CI mypy gate correctly caught this and requires a new validated HEAD. Runtime pytest alone was insufficient proof.
