"""Fail-closed graph checks and exact rational event arithmetic.

Validity here means only synthetic symbolic consistency. It NEVER authorizes
gesture execution, body capability, phonetic realism, or audio generation.
"""
from __future__ import annotations

from collections import defaultdict, deque
from fractions import Fraction
from hashlib import sha256
from json import dumps

from .model import (
    CouplingConstraint, Diagnostic, Event, EventAnchor, ReportStatus,
    SymbolicPlan, TimingReport, ValidationReport, SCHEMA_VERSION,
    REPRESENTATION_KIND,
)

_Node = tuple[str, Event]
_ORIGIN: _Node = ("", Event.ONSET)


def _fraction(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def canonical_plan_json(plan: SymbolicPlan) -> str:
    """Canonical, deterministic research receipt, not adopted wire contract."""
    data = {
        "segment_id": plan.segment_id,
        "source_text": plan.source_text,
        "schema_version": plan.schema_version,
        "representation_kind": plan.representation_kind,
        "pronunciation_units": sorted(
            [(u.unit_id, u.symbol, u.start_offset, u.end_offset)
             for u in plan.pronunciation_units]
        ),
        "tasks": sorted(
            [(t.task_id, t.goal_kind, sorted(t.capability_requirements))
             for t in plan.tasks]
        ),
        "associations": sorted((a.unit_id, a.task_id) for a in plan.associations),
        "couplings": sorted(
            [(c.source_task_id, str(c.source_event), c.target_task_id,
              str(c.target_event), _fraction(c.lag_s)) for c in plan.couplings]
        ),
        "anchors": sorted(
            [(a.task_id, str(a.event), _fraction(a.time_s))
             for a in plan.anchors]
        ),
    }
    return dumps(data, ensure_ascii=False, sort_keys=True,
                 separators=(",", ":"), allow_nan=False)


def plan_digest(plan: SymbolicPlan) -> str:
    return sha256(canonical_plan_json(plan).encode("utf-8")).hexdigest()


def _event_ok(value: object) -> bool:
    return isinstance(value, Event)


def _rational_ok(value: object) -> bool:
    return isinstance(value, Fraction)


def _edges(plan: SymbolicPlan) -> dict[_Node, list[tuple[_Node, Fraction]]]:
    adj: dict[_Node, list[tuple[_Node, Fraction]]] = defaultdict(list)

    def add(left: _Node, right: _Node, lag: Fraction) -> None:
        adj[left].append((right, lag))
        adj[right].append((left, -lag))

    for task in plan.tasks:
        adj[(task.task_id, Event.ONSET)]
        adj[(task.task_id, Event.OFFSET)]
    adj[_ORIGIN]
    for c in plan.couplings:
        add((c.source_task_id, c.source_event),
            (c.target_task_id, c.target_event), c.lag_s)
    for anchor in plan.anchors:
        add(_ORIGIN, (anchor.task_id, anchor.event), anchor.time_s)
    return adj


def _components(
    adj: dict[_Node, list[tuple[_Node, Fraction]]]
) -> tuple[dict[_Node, Fraction], dict[_Node, _Node], bool]:
    potential: dict[_Node, Fraction] = {}
    root: dict[_Node, _Node] = {}
    conflict = False
    for start in sorted(adj, key=lambda n: (n[0], str(n[1]))):
        if start in potential:
            continue
        potential[start] = Fraction(0)
        root[start] = start
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor, lag in adj[node]:
                expected = potential[node] + lag
                if neighbor not in potential:
                    potential[neighbor] = expected
                    root[neighbor] = start
                    queue.append(neighbor)
                elif potential[neighbor] != expected:
                    conflict = True
    return potential, root, conflict


def validate_plan(plan: SymbolicPlan) -> ValidationReport:
    """Structurally validate only. Capability and execution remain UNVERIFIED."""
    issues: list[Diagnostic] = []

    def issue(code: str, subject: str, detail: str) -> None:
        issues.append(Diagnostic(code, subject, detail))

    def reject_surrogates(field: str, value: object) -> None:
        # JSON-escaped lone (or paired) surrogate code points cannot be encoded
        # by the strict UTF-8 research digest. Keep diagnostic subjects ASCII.
        if isinstance(value, str) and any(
            0xD800 <= ord(char) <= 0xDFFF for char in value
        ):
            issue("INVALID_UNICODE_SCALAR", field,
                  "string contains UTF-8-unencodable surrogate code point")

    for field, value in (
        ("segment_id", plan.segment_id),
        ("source_text", plan.source_text),
        ("schema_version", plan.schema_version),
        ("representation_kind", plan.representation_kind),
    ):
        reject_surrogates(field, value)

    if not isinstance(plan.segment_id, str) or not plan.segment_id.strip():
        issue("INVALID_SEGMENT_ID", "", "segment ID must be nonblank")
    # Frozen dataclass type hints are not enforced at runtime. A malformed
    # source must be rejected as data, never crash during later span checks.
    source_length = len(plan.source_text) if isinstance(plan.source_text, str) else 0
    if not isinstance(plan.source_text, str) or not plan.source_text:
        issue("EMPTY_SOURCE", plan.segment_id, "source must be nonempty")
    if plan.schema_version != SCHEMA_VERSION or plan.representation_kind != REPRESENTATION_KIND:
        issue("UNSUPPORTED_REPRESENTATION", plan.segment_id, "schema/kind mismatch")
    unit_ids: set[str] = set()
    for u in plan.pronunciation_units:
        if not isinstance(u.unit_id, str) or not u.unit_id.strip() or u.unit_id in unit_ids:
            issue("INVALID_OR_DUPLICATE_UNIT_ID", str(u.unit_id), "unit IDs must be distinct")
        unit_ids.add(u.unit_id)
        reject_surrogates("pronunciation_unit.unit_id", u.unit_id)
        reject_surrogates("pronunciation_unit.symbol", u.symbol)
        if not isinstance(u.symbol, str) or not u.symbol:
            issue("UNRESOLVED_PRONUNCIATION", u.unit_id, "no supplied candidate")
        if (type(u.start_offset) is not int or type(u.end_offset) is not int
                or u.start_offset < 0 or u.start_offset >= u.end_offset
                or u.end_offset > source_length):
            issue("INVALID_SOURCE_SPAN", u.unit_id, "span must fit unchanged source")
    if not plan.pronunciation_units:
        issue("NO_PRONUNCIATION", plan.segment_id, "no candidate; do not invent reading")
    task_ids: set[str] = set()
    for t in plan.tasks:
        if not isinstance(t.task_id, str) or not t.task_id.strip() or t.task_id in task_ids:
            issue("INVALID_OR_DUPLICATE_TASK_ID", str(t.task_id), "task IDs must be distinct")
        task_ids.add(t.task_id)
        reject_surrogates("task.task_id", t.task_id)
        reject_surrogates("task.goal_kind", t.goal_kind)
        for requirement in t.capability_requirements:
            reject_surrogates("task.capability_requirement", requirement)
        if not isinstance(t.goal_kind, str) or not t.goal_kind:
            issue("UNRESOLVED_TASK_GOAL", t.task_id, "task goal must be supplied")
        if any(not isinstance(x, str) or not x for x in t.capability_requirements):
            issue("INVALID_CAPABILITY_TOKEN", t.task_id, "invalid symbolic requirement")
    if not plan.tasks:
        issue("NO_MOTOR_TASKS", plan.segment_id, "no tasks; do not invent gestures")
    links: set[tuple[str, str]] = set()
    for a in plan.associations:
        reject_surrogates("association.unit_id", a.unit_id)
        reject_surrogates("association.task_id", a.task_id)
        pair = (a.unit_id, a.task_id)
        if pair in links:
            issue("DUPLICATE_ASSOCIATION", a.task_id, "same link repeated")
        links.add(pair)
        if a.unit_id not in unit_ids or a.task_id not in task_ids:
            issue("UNKNOWN_ASSOCIATION_ENDPOINT", a.task_id, "dangling unit/task reference")
    for unit_id in unit_ids:
        if not any(a.unit_id == unit_id for a in plan.associations):
            issue("UNASSOCIATED_UNIT", unit_id, "no motor task linked")
    for task_id in task_ids:
        if not any(a.task_id == task_id for a in plan.associations):
            issue("ORPHAN_TASK", task_id, "no pronunciation unit linked")
    couplings: set[CouplingConstraint] = set()
    for c in plan.couplings:
        reject_surrogates("coupling.source_task_id", c.source_task_id)
        reject_surrogates("coupling.target_task_id", c.target_task_id)
        if c in couplings:
            issue("DUPLICATE_COUPLING", c.source_task_id, "same constraint repeated")
        couplings.add(c)
        if c.source_task_id not in task_ids or c.target_task_id not in task_ids:
            issue("UNKNOWN_COUPLING_ENDPOINT", c.target_task_id, "unknown task")
        if not _event_ok(c.source_event) or not _event_ok(c.target_event):
            issue("INVALID_EVENT", c.source_task_id, "expected ONSET or OFFSET")
        if not _rational_ok(c.lag_s):
            issue("INVALID_LAG", c.source_task_id, "must use exact Fraction")
    for anchor in plan.anchors:
        reject_surrogates("anchor.task_id", anchor.task_id)
        if anchor.task_id not in task_ids:
            issue("UNKNOWN_ANCHOR_ENDPOINT", anchor.task_id, "unknown task")
        if not _event_ok(anchor.event) or not _rational_ok(anchor.time_s):
            issue("INVALID_ANCHOR", anchor.task_id, "event and exact Fraction required")
    # Never run numerical graph arithmetic over malformed constraints.
    if not issues:
        potential, component, conflict = _components(_edges(plan))
        if conflict:
            issue("CONTRADICTORY_TIMING", plan.segment_id, "inconsistent exact equalities")
        else:
            # Conflicted components have arbitrary traversal potentials. Neither
            # negative time nor task duration may be inferred from them.
            for task_id in sorted(task_ids):
                onset, offset = (task_id, Event.ONSET), (task_id, Event.OFFSET)
                if component[onset] == component[offset] and potential[offset] <= potential[onset]:
                    issue("NONPOSITIVE_DURATION", task_id, "resolved OFFSET must follow ONSET")
            for task_id in sorted(task_ids):
                for event in (Event.ONSET, Event.OFFSET):
                    node = (task_id, event)
                    if component[node] == component[_ORIGIN] and potential[node] < potential[_ORIGIN]:
                        issue("NEGATIVE_ANCHORED_TIME", task_id, "time before zero")
    ordered = tuple(sorted(set(issues), key=lambda d: (d.code, d.subject_id, d.detail)))
    return ValidationReport(
        ReportStatus.INVALID if ordered else ReportStatus.STRUCTURALLY_VALID, ordered
    )


def resolve_timing(plan: SymbolicPlan) -> TimingReport:
    """Exact synthetic event times only; deliberately no GestureScore."""
    v = validate_plan(plan)
    if v.status is ReportStatus.INVALID:
        return TimingReport(ReportStatus.INVALID, (), v.diagnostics)
    potential, component, _ = _components(_edges(plan))
    unanchored = [
        task_id + "." + str(event)
        for task_id in sorted(t.task_id for t in plan.tasks)
        for event in (Event.ONSET, Event.OFFSET)
        if component[(task_id, event)] != component[_ORIGIN]
    ]
    if unanchored:
        return TimingReport(ReportStatus.INVALID, (), tuple(
            Diagnostic("UNRESOLVED_EVENT", name, "event not connected to absolute origin")
            for name in unanchored
        ))
    origin = potential[_ORIGIN]
    events = tuple(sorted(
        ((task_id, event, potential[(task_id, event)] - origin)
         for task_id in sorted(t.task_id for t in plan.tasks)
         for event in (Event.ONSET, Event.OFFSET)),
        key=lambda x: (x[0], str(x[1])),
    ))
    return TimingReport(ReportStatus.RESOLVED, events, ())
