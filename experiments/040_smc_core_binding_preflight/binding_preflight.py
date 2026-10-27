"""CVI-1 Gate A: authenticate bounded SMC task/time; refuse unsupported Core semantics.

Research-only integration preflight; NO physical task conversion and NO audio.
Do not put this into SMC or Core public APIs. Protocol: PROTOCOL.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json

from morphoacoustics_smc.canonical_ingress import parse_canonical_request
from morphoacoustics_smc.model import Event
from morphoacoustics_smc.symbolic_bridge import compile_wire, timeline_table
from morphoacoustics_smc.temporal_stn import TemporalScenario, analyze_temporal_wire


@dataclass(frozen=True, slots=True)
class AuthenticatedTask:
    """The real SMC TaskGoal + verified fields recovered from canonical lexicon."""

    task_id: str
    definition_id: str
    semantic_revision: str
    goal_kind: str
    variable: str
    value_domain: str
    applicability_domain: str
    capabilities: tuple[str, ...]
    lower: Fraction  # SMC synthetic scalar, NOT SI Core measurement
    upper: Fraction
    members: tuple[tuple[str, str], ...]


# (Task ID, symbolic event, exact earliest, latest, selected)
ExactEvent = tuple[str, Event, Fraction, Fraction, Fraction]


@dataclass(frozen=True, slots=True)
class PreflightReceipt:
    stage_a: str
    stage_b: str
    reason: str
    canonical_request_sha256: str | None = None
    candidate_digest: str | None = None
    source_timing_digest: str | None = None
    tasks: tuple[AuthenticatedTask, ...] = ()
    exact_events: tuple[ExactEvent, ...] = ()
    # No serializer for an unverified body target; fail-closed on purpose.
    mapped_physical_tasks: tuple[()] = ()
    physical_trace_ref: None = None
    acoustic_trace_ref: None = None
    physical_coverage: tuple[int, int] = (0, 0)


def _reject(code: str) -> PreflightReceipt:
    return PreflightReceipt("REJECTED", "NOT_RUN", code)


def audit_smc_core_binding(payload: object) -> PreflightReceipt:
    """Authenticate SMC5/6 source and temporal identity; refuse unevidenced physics.

    A caller cannot attach a string-based or invented mapping: no binding input
    is accepted. One new separately preregistered evidence-gated adapter must
    be designed before physical goals can be emitted.
    """
    compiled = compile_wire(payload)
    if (
        compiled.receipt.status != "RESOLVED"
        or compiled.plan is None
        or compiled.timing is None
        or compiled.receipt.candidate_digest is None
        or compiled.receipt.canonical_request_sha256 is None
    ):
        return _reject("SMC5_" + compiled.receipt.code)

    # Decode ONLY canonical data revalidated by SMC4/5; never trust arbitrary
    # caller dicts or treat TaskGoal.goal_kind as a Core articulator identity.
    parsed = parse_canonical_request(payload)
    if (
        parsed.request is None
        or parsed.request.canonical_sha256 != compiled.receipt.canonical_request_sha256
    ):
        return _reject("CANONICAL_PROVENANCE_MISMATCH")
    canonical = json.loads(parsed.request.canonical_bytes)
    definitions = canonical["motor_mapping"]["lexicon"]["definitions"]
    by_id = {
        (entry["definition_id"], entry["semantic_revision"]): entry
        for entry in definitions
    }
    # The parser normally guarantees uniqueness; verify it again here
    # so this code does not accidentally make a last-entry-wins binding.
    if len(by_id) != len(definitions):
        return _reject("DUPLICATE_DEFINITION")

    tasks: list[AuthenticatedTask] = []
    for goal in compiled.goals:
        definition = by_id.get((goal.definition_id, goal.semantic_revision))
        if definition is None:
            return _reject("MISSING_CANONICAL_DEFINITION")
        if (
            definition["goal_kind"] != goal.goal_kind
            or tuple(sorted(definition["capabilities"])) != goal.capabilities
            or definition["algebra"] != "SCALAR_INTERVAL"
            or goal.lower > goal.upper
        ):
            return _reject("GOAL_DEFINITION_MISMATCH")
        tasks.append(AuthenticatedTask(
            task_id=goal.task_id,
            definition_id=goal.definition_id,
            semantic_revision=goal.semantic_revision,
            goal_kind=goal.goal_kind,
            variable=definition["variable"],
            value_domain=definition["value_domain"],
            applicability_domain=definition["applicability_domain"],
            capabilities=goal.capabilities,
            lower=goal.lower,
            upper=goal.upper,
            members=goal.members,
        ))
    if len(tasks) != len({task.task_id for task in tasks}):
        return _reject("DUPLICATE_TASK_ID")

    # Compatibility is the ONLY admitted initial CVI timing lane.
    # A synthetic override is never a faithful performance of source text.
    temporal = analyze_temporal_wire(
        payload,
        TemporalScenario(
            study_id="cvi1-smc-core-authentic-preflight-v0",
            lane="COMPATIBILITY",
            horizon_s=Fraction(2),
            minimum_duration_s=Fraction(1, 100),
            constraints=(),
        ),
    )
    if (
        temporal.status != "SAT_UNIQUE"
        or temporal.receipt is None
        or temporal.receipt.source_candidate_digest != compiled.receipt.candidate_digest
        or temporal.receipt.canonical_request_sha256 != compiled.receipt.canonical_request_sha256
        or temporal.receipt.witness_digest is None
    ):
        return _reject("SMC6_NOT_EXACT_COMPATIBLE_" + temporal.status)

    planned = timeline_table(compiled)
    expected = {
        (tid, ev): t
        for tid, start, end in planned
        for ev, t in ((Event.ONSET, start), (Event.OFFSET, end))
    }
    events: tuple[ExactEvent, ...] = tuple(
        sorted(temporal.events, key=lambda row: (row[0], row[1].value))
    )
    if len(events) != 2 * len(tasks):
        return _reject("SMC6_EVENT_COUNT_MISMATCH")
    if any(
        (tid, ev) not in expected
        or low != expected[(tid, ev)]
        or high != expected[(tid, ev)]
        or selected != expected[(tid, ev)]
        for tid, ev, low, high, selected in events
    ):
        return _reject("SMC6_ORIGINAL_TIMING_NOT_PRESERVED")

    # No accepted SMC TaskDefinition-to-dimensioned-Core-goal binding
    # exists in the audited research baseline. In particular synthetic
    # tract/open_closed is NOT a physical constriction target.
    return PreflightReceipt(
        stage_a="FORMAL_AUTHENTICATED",
        stage_b="UNMAPPED_SEMANTICS",
        reason="NO_EVIDENCED_PHYSICAL_TASK_BINDING",
        canonical_request_sha256=compiled.receipt.canonical_request_sha256,
        candidate_digest=compiled.receipt.candidate_digest,
        source_timing_digest=temporal.receipt.source_timing_digest,
        tasks=tuple(sorted(tasks, key=lambda task: task.task_id)),
        exact_events=events,
        physical_coverage=(0, len(tasks)),
    )
