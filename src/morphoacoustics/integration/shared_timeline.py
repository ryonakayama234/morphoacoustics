from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import TypeAlias

from morphoacoustics.domain import Gesture, GestureScore, Task, TaskParameter

COMPILER_VERSION = "shared-timeline-candidate/v1"
_TIMING_TOLERANCE_S = 1e-9


class GestureEvent(StrEnum):
    ONSET = "onset"
    OFFSET = "offset"


class ProsodyEventKind(StrEnum):
    BOUNDARY = "boundary"
    PROMINENCE = "prominence"
    DURATION_SCALE = "duration_scale"
    EFFORT = "effort"
    VOICING = "voicing"


class PlanCompileStatus(StrEnum):
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class ResolvedAnchor:
    id: str
    time_s: float
    provenance: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("anchor id must be non-empty")
        if not isfinite(self.time_s) or self.time_s < 0.0:
            raise ValueError("anchor time_s must be finite and >= 0")
        if not self.provenance.strip():
            raise ValueError("anchor provenance must be non-empty")


@dataclass(frozen=True, slots=True)
class ResolvedTimeline:
    anchors: tuple[ResolvedAnchor, ...]

    def __post_init__(self) -> None:
        ids = [anchor.id for anchor in self.anchors]
        if len(ids) != len(set(ids)):
            raise ValueError("timeline anchor ids must be unique")

    def time_for(self, anchor_id: str) -> float | None:
        anchor = next((item for item in self.anchors if item.id == anchor_id), None)
        return None if anchor is None else anchor.time_s


@dataclass(frozen=True, slots=True)
class GestureTemplate:
    id: str
    task: Task
    target: str | None = None
    location: float | None = None
    parameters: tuple[TaskParameter, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("gesture template id must be non-empty")
        if self.target is not None and not self.target.strip():
            raise ValueError("target must be non-empty when provided")
        if self.location is not None and not 0.0 <= self.location <= 1.0:
            raise ValueError("normalized gesture location must lie within [0, 1]")
        names = [parameter.name for parameter in self.parameters]
        if len(names) != len(set(names)):
            raise ValueError("gesture parameter names must be unique")


@dataclass(frozen=True, slots=True)
class AnchorRef:
    anchor_id: str

    def __post_init__(self) -> None:
        if not self.anchor_id.strip():
            raise ValueError("anchor ref must be non-empty")


@dataclass(frozen=True, slots=True)
class GestureEventRef:
    gesture_id: str
    event: GestureEvent

    def __post_init__(self) -> None:
        if not self.gesture_id.strip():
            raise ValueError("gesture event gesture_id must be non-empty")


TimingReference: TypeAlias = AnchorRef | GestureEventRef


@dataclass(frozen=True, slots=True)
class TimingConstraint:
    subject: GestureEventRef
    reference: TimingReference
    offset_s: float = 0.0

    def __post_init__(self) -> None:
        if not isfinite(self.offset_s):
            raise ValueError("timing offset_s must be finite")


@dataclass(frozen=True, slots=True)
class CoordinationPlan:
    constraints: tuple[TimingConstraint, ...]


@dataclass(frozen=True, slots=True)
class ProsodyEvent:
    anchor_id: str
    kind: ProsodyEventKind
    value: float

    def __post_init__(self) -> None:
        if not self.anchor_id.strip():
            raise ValueError("prosody anchor_id must be non-empty")
        if not isfinite(self.value):
            raise ValueError("prosody value must be finite")
        if self.kind is ProsodyEventKind.DURATION_SCALE and self.value <= 0.0:
            raise ValueError("duration_scale must be > 0")


@dataclass(frozen=True, slots=True)
class ProsodyPlan:
    events: tuple[ProsodyEvent, ...]


@dataclass(frozen=True, slots=True)
class ResolvedGestureEvent:
    gesture_id: str
    event: GestureEvent
    time_s: float


@dataclass(frozen=True, slots=True)
class ResolvedProsodyEvent:
    anchor_id: str
    kind: ProsodyEventKind
    value: float
    time_s: float


@dataclass(frozen=True, slots=True)
class PlanDiagnostic:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class PlanCompileResult:
    status: PlanCompileStatus
    score: GestureScore | None
    resolved_events: tuple[ResolvedGestureEvent, ...]
    resolved_prosody: tuple[ResolvedProsodyEvent, ...]
    diagnostics: tuple[PlanDiagnostic, ...]
    compiler_version: str = COMPILER_VERSION


_Node: TypeAlias = tuple[str, str, str]


def _anchor_node(anchor_id: str) -> _Node:
    return ("anchor", anchor_id, "")


def _event_node(reference: GestureEventRef) -> _Node:
    return ("gesture", reference.gesture_id, reference.event.value)


def _node_for_reference(reference: TimingReference) -> _Node:
    if isinstance(reference, AnchorRef):
        return _anchor_node(reference.anchor_id)
    return _event_node(reference)


def _constraint_sort_key(constraint: TimingConstraint) -> tuple[str, ...]:
    reference = constraint.reference
    if isinstance(reference, AnchorRef):
        ref_key = ("anchor", reference.anchor_id, "")
    else:
        ref_key = ("gesture", reference.gesture_id, reference.event.value)
    return (
        constraint.subject.gesture_id,
        constraint.subject.event.value,
        *ref_key,
        f"{constraint.offset_s:.17g}",
    )


def _diagnostic_sort_key(diagnostic: PlanDiagnostic) -> tuple[str, str]:
    return (diagnostic.code, diagnostic.message)


def compile_shared_timeline(
    *,
    gestures: tuple[GestureTemplate, ...],
    coordination: CoordinationPlan,
    prosody: ProsodyPlan,
    timeline: ResolvedTimeline,
) -> PlanCompileResult:
    diagnostics: list[PlanDiagnostic] = []

    gesture_ids = [gesture.id for gesture in gestures]
    if len(gesture_ids) != len(set(gesture_ids)):
        duplicates = sorted(
            gesture_id
            for gesture_id in set(gesture_ids)
            if gesture_ids.count(gesture_id) > 1
        )
        diagnostics.append(
            PlanDiagnostic(
                "DUPLICATE_GESTURE_ID",
                f"duplicate gesture template ids: {', '.join(duplicates)}",
            )
        )

    gestures_by_id = {gesture.id: gesture for gesture in gestures}
    anchors_by_id = {anchor.id: anchor for anchor in timeline.anchors}

    graph: dict[_Node, list[tuple[_Node, float]]] = defaultdict(list)
    event_nodes = {
        (gesture.id, event): _event_node(GestureEventRef(gesture.id, event))
        for gesture in gestures
        for event in GestureEvent
    }

    for constraint in sorted(coordination.constraints, key=_constraint_sort_key):
        if constraint.subject.gesture_id not in gestures_by_id:
            diagnostics.append(
                PlanDiagnostic(
                    "UNKNOWN_GESTURE",
                    f"unknown subject gesture: {constraint.subject.gesture_id}",
                )
            )
            continue

        reference = constraint.reference
        if isinstance(reference, AnchorRef):
            if reference.anchor_id not in anchors_by_id:
                diagnostics.append(
                    PlanDiagnostic(
                        "UNKNOWN_ANCHOR",
                        f"unknown timing anchor: {reference.anchor_id}",
                    )
                )
                continue
        elif reference.gesture_id not in gestures_by_id:
            diagnostics.append(
                PlanDiagnostic(
                    "UNKNOWN_GESTURE",
                    f"unknown reference gesture: {reference.gesture_id}",
                )
            )
            continue

        subject_node = _event_node(constraint.subject)
        reference_node = _node_for_reference(reference)
        graph[reference_node].append((subject_node, constraint.offset_s))
        graph[subject_node].append((reference_node, -constraint.offset_s))

    times: dict[_Node, float] = {}
    queue: deque[_Node] = deque()

    for anchor in sorted(timeline.anchors, key=lambda item: item.id):
        node = _anchor_node(anchor.id)
        times[node] = anchor.time_s
        queue.append(node)

    contradiction_messages: set[str] = set()
    while queue:
        node = queue.popleft()
        base_time = times[node]
        neighbors = sorted(
            graph.get(node, ()),
            key=lambda item: (item[0], f"{item[1]:.17g}"),
        )
        for neighbor, delta in neighbors:
            candidate = base_time + delta
            if neighbor not in times:
                times[neighbor] = candidate
                queue.append(neighbor)
                continue
            if abs(times[neighbor] - candidate) > _TIMING_TOLERANCE_S:
                contradiction_messages.add(
                    "incompatible timing constraints resolve "
                    f"{neighbor[0]}:{neighbor[1]}:{neighbor[2]} to both "
                    f"{times[neighbor]:.12g}s and {candidate:.12g}s"
                )

    for message in sorted(contradiction_messages):
        diagnostics.append(PlanDiagnostic("CONTRADICTORY_TIMING", message))

    for gesture in sorted(gestures, key=lambda item: item.id):
        for event in GestureEvent:
            node = event_nodes[(gesture.id, event)]
            if node not in times:
                diagnostics.append(
                    PlanDiagnostic(
                        "UNRESOLVED_EVENT",
                        f"{gesture.id}.{event.value} has no path to a resolved anchor",
                    )
                )

    resolved_prosody: list[ResolvedProsodyEvent] = []
    for event in sorted(
        prosody.events,
        key=lambda item: (item.anchor_id, item.kind.value, f"{item.value:.17g}"),
    ):
        anchor = anchors_by_id.get(event.anchor_id)
        if anchor is None:
            diagnostics.append(
                PlanDiagnostic(
                    "UNKNOWN_ANCHOR",
                    f"unknown prosody anchor: {event.anchor_id}",
                )
            )
            continue
        resolved_prosody.append(
            ResolvedProsodyEvent(
                anchor_id=event.anchor_id,
                kind=event.kind,
                value=event.value,
                time_s=anchor.time_s,
            )
        )

    score: GestureScore | None = None
    resolved_events: list[ResolvedGestureEvent] = []
    if not diagnostics:
        compiled_gestures: list[Gesture] = []
        for template in sorted(gestures, key=lambda item: item.id):
            onset = times[event_nodes[(template.id, GestureEvent.ONSET)]]
            offset = times[event_nodes[(template.id, GestureEvent.OFFSET)]]
            resolved_events.extend(
                (
                    ResolvedGestureEvent(template.id, GestureEvent.ONSET, onset),
                    ResolvedGestureEvent(template.id, GestureEvent.OFFSET, offset),
                )
            )
            try:
                compiled_gestures.append(
                    Gesture(
                        task=template.task,
                        onset_s=onset,
                        offset_s=offset,
                        target=template.target,
                        location=template.location,
                        parameters=template.parameters,
                    )
                )
            except ValueError as exc:
                diagnostics.append(
                    PlanDiagnostic(
                        "INVALID_GESTURE_WINDOW",
                        f"{template.id}: {exc}",
                    )
                )

        if not diagnostics:
            score = GestureScore(tuple(compiled_gestures))

    diagnostics_tuple = tuple(sorted(diagnostics, key=_diagnostic_sort_key))
    if diagnostics_tuple:
        return PlanCompileResult(
            status=PlanCompileStatus.INVALID,
            score=None,
            resolved_events=tuple(
                sorted(
                    resolved_events,
                    key=lambda item: (item.time_s, item.gesture_id, item.event.value),
                )
            ),
            resolved_prosody=tuple(resolved_prosody),
            diagnostics=diagnostics_tuple,
        )

    return PlanCompileResult(
        status=PlanCompileStatus.VALID,
        score=score,
        resolved_events=tuple(
            sorted(
                resolved_events,
                key=lambda item: (item.time_s, item.gesture_id, item.event.value),
            )
        ),
        resolved_prosody=tuple(resolved_prosody),
        diagnostics=(),
    )
