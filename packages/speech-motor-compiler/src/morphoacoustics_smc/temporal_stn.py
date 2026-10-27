"""SMC-6: bounded, exact, SYNTHETIC time-coordination research sidecar.

Does not infer phonetics, define a public MotorScore, execute any body, or
generate physical/acoustic output. Never modifies SMC-3/SMC-5 contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from itertools import combinations
from typing import Any

from .model import Event
from .symbolic_bridge import compile_wire, timeline_table

_VERSION = "smc6-stn-research/v0"
_OVERRIDE = "SMC5_EXACT_TIMING_REPLACED_FOR_SYNTHETIC_STUDY"
_MAX_TASKS = 12
_MAX_CONSTRAINTS = 96
_MAX_PART = 10**9
Node = tuple[str, str]
Origin: Node = ("", "ORIGIN")
Edge = tuple[Node, Node, Fraction, str]
Endpoint = tuple[str, Event] | None
EventRow = tuple[str, Event, Fraction, Fraction, Fraction]
OverlapRow = tuple[str, str, Fraction, Fraction, Fraction]


@dataclass(frozen=True, slots=True)
class TemporalConstraint:
    constraint_id: str
    from_event: Endpoint
    to_event: Endpoint
    lower_s: Fraction
    upper_s: Fraction


@dataclass(frozen=True, slots=True)
class TemporalScenario:
    study_id: str
    lane: str
    horizon_s: Fraction
    minimum_duration_s: Fraction
    constraints: tuple[TemporalConstraint, ...]
    replacement_policy: str | None = None
    replacement_reason: str | None = None


@dataclass(frozen=True, slots=True)
class TemporalReceipt:
    version: str
    canonical_request_sha256: str
    source_plan_digest: str
    source_candidate_digest: str
    source_timing_digest: str
    study_digest: str
    witness_digest: str | None


@dataclass(frozen=True, slots=True)
class TemporalAnalysis:
    status: str
    code: str
    events: tuple[EventRow, ...] = ()
    overlaps: tuple[OverlapRow, ...] = ()
    negative_cycle_weight: Fraction | None = None
    negative_cycle: tuple[str, ...] = ()
    receipt: TemporalReceipt | None = None


class _BadScenario(Exception):
    pass


def _check_rational(value: object) -> Fraction:
    if not isinstance(value, Fraction):
        raise _BadScenario("NON_EXACT_RATIONAL")
    if abs(value.numerator) > _MAX_PART or value.denominator > _MAX_PART:
        raise _BadScenario("RATIONAL_LIMIT")
    return value


def _check_id(value: object, field: str) -> str:
    if (not isinstance(value, str) or not (1 <= len(value) <= 100)
            or not value.isascii() or not value.strip()
            or any(ord(c) < 33 or ord(c) > 126 for c in value)):
        raise _BadScenario("INVALID_" + field)
    return value


def _node(ref: Endpoint, permitted: set[str]) -> Node:
    if ref is None:
        return Origin
    if (not isinstance(ref, tuple) or len(ref) != 2
            or not isinstance(ref[0], str) or ref[0] not in permitted
            or not isinstance(ref[1], Event)):
        raise _BadScenario("UNKNOWN_OR_INVALID_EVENT")
    return (ref[0], ref[1].value)


def _pair(n: Fraction) -> tuple[int, int]:
    return (n.numerator, n.denominator)


def _hash(domain: str, data: object) -> str:
    serial = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(domain.encode("ascii") + b"\0" + serial).hexdigest()


def _edge_pair(left: Node, right: Node, low: Fraction, high: Fraction,
               name: str) -> tuple[Edge, Edge]:
    # low <= (right-left) <= high
    return ((left, right, high, name), (right, left, -low, name))


def _graph(nodes: tuple[Node, ...], edges: list[Edge]) -> tuple[
    list[list[Fraction | None]], tuple[str, ...], Fraction | None
]:
    """Exact difference constraints; derive an actual negative cycle via BF."""
    index = {key: i for i, key in enumerate(nodes)}
    indexed = sorted(
        ((index[a], index[b], w, cid) for a, b, w, cid in edges),
        key=lambda e: (e[0], e[1], e[2], e[3]),
    )
    n = len(nodes)
    potential = [Fraction(0)] * n
    pred: list[tuple[int, Fraction, str] | None] = [None] * n
    updated: int | None = None
    for _ in range(n):
        updated = None
        for a, b, w, name in indexed:
            if potential[b] > potential[a] + w:
                potential[b] = potential[a] + w
                pred[b] = (a, w, name)
                updated = b
        if updated is None:
            break
    if updated is not None:
        v = updated
        for _ in range(n):
            predecessor = pred[v]
            if predecessor is None:
                raise RuntimeError("negative-cycle predecessor missing")
            v = predecessor[0]
        start = v
        names: list[str] = []
        total = Fraction(0)
        for _ in range(n + 1):
            predecessor = pred[v]
            if predecessor is None:
                raise RuntimeError("negative-cycle witness missing")
            a, weight, name = predecessor
            names.append(name)
            total += weight
            v = a
            if v == start:
                break
        else:
            raise RuntimeError("negative-cycle witness did not close")
        if total >= 0:
            raise RuntimeError("nonnegative contradiction certificate")
        return [], tuple(reversed(names)), total

    dist: list[list[Fraction | None]] = [[None] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = Fraction(0)
    for a, b, w, _ in indexed:
        prev = dist[a][b]
        if prev is None or w < prev:
            dist[a][b] = w
    for k in range(n):
        for i in range(n):
            ik = dist[i][k]
            if ik is None:
                continue
            for j in range(n):
                kj = dist[k][j]
                if kj is None:
                    continue
                candidate = ik + kj
                before = dist[i][j]
                if before is None or candidate < before:
                    dist[i][j] = candidate
    if any(dist[i][i] is not None and dist[i][i] < 0 for i in range(n)):
        raise RuntimeError("Floyd/Bellman contradiction")
    return dist, (), None


def _relative_bounds(
    dist: list[list[Fraction | None]], idx: dict[Node, int],
    start: Node, end: Node,
) -> tuple[Fraction, Fraction]:
    high = dist[idx[start]][idx[end]]
    reverse = dist[idx[end]][idx[start]]
    if high is None or reverse is None:
        raise RuntimeError("unanchored finite horizon")
    return -reverse, high


def _joint_overlap(
    nodes: tuple[Node, ...], edges: list[Edge], idx: dict[Node, int],
    tid_a: str, tid_b: str,
) -> tuple[Fraction, Fraction]:
    sa, sb = (tid_a, Event.ONSET.value), (tid_b, Event.ONSET.value)
    ea, eb = (tid_a, Event.OFFSET.value), (tid_b, Event.OFFSET.value)
    mins: list[Fraction] = []
    maxes: list[Fraction] = []
    # Enumerate the four mutually exhaustive start/end order partitions.
    for later_start, earlier_start in ((sa, sb), (sb, sa)):
        for earlier_end, later_end in ((ea, eb), (eb, ea)):
            partition = edges + [
                # later_start >= earlier_start
                (later_start, earlier_start, Fraction(0), "ORDER_START"),
                # earlier_end <= later_end
                (later_end, earlier_end, Fraction(0), "ORDER_END"),
            ]
            distances, _, conflict = _graph(nodes, partition)
            if conflict is not None:
                continue
            lower, upper = _relative_bounds(distances, idx, later_start, earlier_end)
            mins.append(max(Fraction(0), lower))
            maxes.append(max(Fraction(0), upper))
    if not mins:
        raise RuntimeError("no feasible ordering for satisfiable model")
    return min(mins), max(maxes)


def _scenario_edges(
    scenario: TemporalScenario, task_ids: tuple[str, ...],
) -> tuple[list[Edge], tuple[object, ...]]:
    if not isinstance(scenario, TemporalScenario):
        raise _BadScenario("INVALID_SCENARIO")
    study_id = _check_id(scenario.study_id, "STUDY_ID")
    if scenario.lane not in ("COMPATIBILITY", "RESEARCH_OVERRIDE"):
        raise _BadScenario("UNSUPPORTED_LANE")
    horizon = _check_rational(scenario.horizon_s)
    epsilon = _check_rational(scenario.minimum_duration_s)
    if not (Fraction(0) < epsilon <= horizon <= Fraction(10)):
        raise _BadScenario("INVALID_HORIZON_OR_DURATION")
    if not isinstance(scenario.constraints, tuple) or len(scenario.constraints) > _MAX_CONSTRAINTS:
        raise _BadScenario("CONSTRAINT_COUNT_LIMIT")
    if scenario.lane == "RESEARCH_OVERRIDE":
        if scenario.replacement_policy != _OVERRIDE or (
            not isinstance(scenario.replacement_reason, str)
            or not scenario.replacement_reason.strip()
            or len(scenario.replacement_reason) > 500
        ):
            raise _BadScenario("MISSING_EXPLICIT_TIMING_OVERRIDE")
    elif scenario.replacement_policy is not None or scenario.replacement_reason is not None:
        raise _BadScenario("INVALID_COMPATIBILITY_OVERRIDE")
    permitted = set(task_ids)
    edges: list[Edge] = []
    canonical: list[object] = []
    seen: set[str] = set()
    for con in scenario.constraints:
        if not isinstance(con, TemporalConstraint):
            raise _BadScenario("UNSUPPORTED_CONSTRAINT_CLASS")
        name = _check_id(con.constraint_id, "CONSTRAINT_ID")
        if name in seen:
            raise _BadScenario("DUPLICATE_CONSTRAINT_ID")
        seen.add(name)
        start, end = _node(con.from_event, permitted), _node(con.to_event, permitted)
        low, high = _check_rational(con.lower_s), _check_rational(con.upper_s)
        if low > high:
            raise _BadScenario("INVALID_BOUND_ORDER")
        edges.extend(_edge_pair(start, end, low, high, name))
        canonical.append((name, start, end, _pair(low), _pair(high)))
    for tid in task_ids:
        onset, offset = (tid, Event.ONSET.value), (tid, Event.OFFSET.value)
        edges.extend(_edge_pair(Origin, onset, Fraction(0), horizon, "HORIZON"))
        edges.extend(_edge_pair(Origin, offset, Fraction(0), horizon, "HORIZON"))
        edges.extend(_edge_pair(onset, offset, epsilon, horizon, "MIN_DURATION"))
    return edges, (
        study_id, scenario.lane, _pair(horizon), _pair(epsilon),
        scenario.replacement_policy, scenario.replacement_reason,
        tuple(sorted(canonical, key=lambda x: x[0])),
    )


def analyze_temporal_wire(raw: object, scenario: TemporalScenario) -> TemporalAnalysis:
    """Fresh SMC-5 canonical ingress + body-neutral exact temporal research."""
    legacy = compile_wire(raw)
    if (legacy.plan is None or legacy.timing is None
            or legacy.receipt.candidate_digest is None
            or legacy.receipt.plan_digest is None
            or legacy.receipt.canonical_request_sha256 is None):
        return TemporalAnalysis("REJECTED", "UNTRUSTED_OR_UNRESOLVED_SMC5")
    tasks = tuple(sorted(x.task_id for x in legacy.plan.tasks))
    if not (1 <= len(tasks) <= _MAX_TASKS):
        return TemporalAnalysis("REJECTED", "TASK_COUNT_LIMIT")
    try:
        edges, canonical = _scenario_edges(scenario, tasks)
    except _BadScenario as exc:
        return TemporalAnalysis("REJECTED", str(exc))
    try:
        old = timeline_table(legacy)
        original = _hash("SMC6-ORIGINAL-TIMING/v0", {
            "events": [(tid, ev.value, _pair(t)) for tid, st, en in old
                       for ev, t in ((Event.ONSET, st), (Event.OFFSET, en))],
            "anchors": sorted((a.task_id, a.event.value, _pair(a.time_s))
                              for a in legacy.plan.anchors),
            "couplings": sorted(
                (c.source_task_id, c.source_event.value,
                 c.target_task_id, c.target_event.value, _pair(c.lag_s))
                for c in legacy.plan.couplings),
        })
        scenario_sha = _hash("SMC6-STUDY/v0", {
            "source_canonical": legacy.receipt.canonical_request_sha256,
            "source_candidate": legacy.receipt.candidate_digest,
            "source_plan": legacy.receipt.plan_digest,
            "source_timing": original,
            "study": canonical, "algorithm": _VERSION,
        })
        receipt = TemporalReceipt(
            _VERSION, legacy.receipt.canonical_request_sha256,
            legacy.receipt.plan_digest, legacy.receipt.candidate_digest,
            original, scenario_sha, None,
        )
        # Compatibility retains anchors, original coupling constraints AND
        # resolved event instants; adding bounds can narrow but never move them.
        if scenario.lane == "COMPATIBILITY":
            for tid, start, end in old:
                edges.extend(_edge_pair(Origin, (tid, Event.ONSET.value),
                                        start, start, "SMC5_EXACT_ONSET"))
                edges.extend(_edge_pair(Origin, (tid, Event.OFFSET.value),
                                        end, end, "SMC5_EXACT_OFFSET"))
            for a in legacy.plan.anchors:
                edges.extend(_edge_pair(Origin, (a.task_id, a.event.value),
                                        a.time_s, a.time_s, "SMC5_ANCHOR"))
            for c in legacy.plan.couplings:
                edges.extend(_edge_pair(
                    (c.source_task_id, c.source_event.value),
                    (c.target_task_id, c.target_event.value),
                    c.lag_s, c.lag_s, "SMC5_COUPLING"))
        nodes: tuple[Node, ...] = (Origin,) + tuple(
            (tid, ev.value) for tid in tasks for ev in (Event.ONSET, Event.OFFSET))
        idx = {node: i for i, node in enumerate(nodes)}
        dist, cycle, weight = _graph(nodes, edges)
        if weight is not None:
            return TemporalAnalysis("UNSAT", "TEMPORAL_UNSAT",
                                    negative_cycle_weight=weight,
                                    negative_cycle=cycle, receipt=receipt)
        rows: list[EventRow] = []
        witness: dict[Node, Fraction] = {Origin: Fraction(0)}
        for tid in tasks:
            for event in (Event.ONSET, Event.OFFSET):
                key = (tid, event.value)
                lo, hi = _relative_bounds(dist, idx, Origin, key)
                witness[key] = lo  # canonical earliest-component potential
                rows.append((tid, event, lo, hi, lo))
        # Extra independent direct check: all hard difference inequalities.
        for u, v, limit, _ in edges:
            if witness[v] - witness[u] > limit:
                raise RuntimeError("witness violates hard constraint")
        overlaps: list[OverlapRow] = []
        for a, b in combinations(tasks, 2):
            minimum, maximum = _joint_overlap(nodes, edges, idx, a, b)
            sa, ea = witness[(a, "ONSET")], witness[(a, "OFFSET")]
            sb, eb = witness[(b, "ONSET")], witness[(b, "OFFSET")]
            w = max(Fraction(0), min(ea, eb) - max(sa, sb))
            if not minimum <= w <= maximum:
                raise RuntimeError("witness overlap outside feasible region")
            overlaps.append((a, b, minimum, maximum, w))
        witness_sha = _hash("SMC6-WITNESS/v0", {
            "study": scenario_sha,
            "events": [(tid, ev.value, _pair(t)) for tid, ev, _, _, t in rows],
        })
        receipt = TemporalReceipt(
            receipt.version, receipt.canonical_request_sha256,
            receipt.source_plan_digest, receipt.source_candidate_digest,
            receipt.source_timing_digest, receipt.study_digest, witness_sha,
        )
        unique = all(lo == hi for _, _, lo, hi, _ in rows)
        return TemporalAnalysis("SAT_UNIQUE" if unique else "SAT_NONUNIQUE",
                                "OK", tuple(rows), tuple(overlaps), receipt=receipt)
    except (ValueError, TypeError, RuntimeError, OverflowError) as exc:
        # Never relabel algorithmic failure as a successful or physical plan.
        return TemporalAnalysis("INDETERMINATE", "INSTRUMENT_ERROR:" + type(exc).__name__)
