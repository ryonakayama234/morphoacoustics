"""SMC-5 synthetic-only canonical pronunciation → finite motor-task bridge.

Research candidate only. Does not infer pronunciation, select organ coordinates,
certify phonetic plausibility, execute physics, or generate acoustic waveforms.
Historical rejected SMC-4 Gate B source is intentionally NOT imported.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, cast

from .canonical_ingress import (
    CanonicalCompileRequest, IngressReceipt, parse_canonical_request,
)
from .model import (
    CouplingConstraint, Event, EventAnchor, MotorTask, PronunciationUnit,
    ReportStatus, SymbolicPlan, TaskAssociation, TimingReport,
)
from .validation import plan_digest, resolve_timing, validate_plan

COMPILER_VERSION = "smc5-synthetic-bridge/v0"


@dataclass(frozen=True, slots=True)
class TaskGoal:
    """Functional goal metadata absent from the unchanged SMC-3 SymbolicPlan."""

    task_id: str
    definition_id: str
    semantic_revision: str
    goal_kind: str
    capabilities: tuple[str, ...]
    lower: Fraction
    upper: Fraction
    members: tuple[tuple[str, str], ...]
    templates: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CompileReceipt:
    compiler_version: str
    status: str
    stage: str
    code: str
    submission_sha256: str | None
    canonical_request_sha256: str | None
    plan_digest: str | None
    candidate_digest: str | None
    provenance: tuple[tuple[str, str], ...]
    trace: tuple[str, ...]
    diagnostics: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CompileResult:
    plan: SymbolicPlan | None
    goals: tuple[TaskGoal, ...]
    timing: TimingReport | None
    receipt: CompileReceipt


class _Refusal(Exception):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail


def _fail(code: str, detail: str = "") -> None:
    raise _Refusal(code, detail)


def _frac(raw: dict[str, Any]) -> Fraction:
    # Canonical ingress already enforces reduced, bounded integral rationals.
    return Fraction(raw["numerator"], raw["denominator"])


def _tri(p: dict[str, Any], context: dict[str, str]) -> int:
    """Strong Kleene TRUE=1, UNKNOWN=0, FALSE=-1."""
    op: str = p["op"]
    if op == "TRUE":
        return 1
    if op == "FALSE":
        return -1
    if op == "EQ":
        return 0 if p["key"] not in context else (
            1 if context[p["key"]] == p["expected"] else -1)
    vals = [_tri(x, context) for x in p["operands"]]
    if op == "NOT":
        return -vals[0]
    if op == "AND":
        return -1 if -1 in vals else (0 if 0 in vals else 1)
    if op == "OR":
        return 1 if 1 in vals else (0 if 0 in vals else -1)
    _fail("UNSUPPORTED_PREDICATE", op)
    return 0


def _select(
    items: list[dict[str, Any]], context: dict[str, str],
    *, kind: str,
) -> dict[str, Any]:
    true_items: list[dict[str, Any]] = []
    unknown = False
    for item in items:
        if item["priority"] is not None:
            _fail("UNSUPPORTED_SELECTION_POLICY", kind)
        value = _tri(item["context"], context)
        if value == 0:
            unknown = True
        elif value == 1:
            true_items.append(item)
    # An unknown alternative might overturn even a currently unique choice.
    if unknown:
        _fail("INSUFFICIENT_CONTEXT", kind)
    if len(true_items) > 1:
        _fail("AMBIGUOUS", kind)
    if not true_items:
        _fail("UNMAPPED", kind)
    return true_items[0]


def _digest(payload: object) -> str:
    wire = json.dumps(
        payload, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return sha256(b"SMC5-TASK-CANDIDATE/v0\0" + wire).hexdigest()


def _receipt(
    status: str, stage: str, code: str, raw: str | None, semantic: str | None,
    provenance: tuple[tuple[str, str], ...] = (),
    trace: tuple[str, ...] = (), diagnostics: tuple[str, ...] = (),
    plan_sha: str | None = None, candidate_sha: str | None = None,
) -> CompileReceipt:
    return CompileReceipt(
        COMPILER_VERSION, status, stage, code, raw, semantic,
        plan_sha, candidate_sha, provenance, trace, diagnostics,
    )


def _ingress_fail(ingress: IngressReceipt) -> CompileResult:
    return CompileResult(
        None, (), None, _receipt(
            "REJECTED", "INGRESS", ingress.code,
            ingress.submission_sha256, ingress.canonical_request_sha256,
            diagnostics=ingress.canonical_diagnostics,
        ),
    )


def _compile_accepted(
    request: CanonicalCompileRequest, raw_sha: str | None,
) -> CompileResult:
    semantic_sha = request.canonical_sha256
    doc = cast(dict[str, Any], json.loads(request.canonical_bytes))
    segment = cast(dict[str, Any], doc["segment"])
    pronounce = cast(dict[str, Any], doc["pronunciation"])
    mapping = cast(dict[str, Any], doc["motor_mapping"])
    lex = cast(dict[str, Any], mapping["lexicon"])
    coord = cast(dict[str, Any], doc["coordination"])
    provenance = tuple(sorted((
        ("segment_id", segment["segment_id"]),
        ("source_revision", segment["source_revision"]),
        ("language", segment["language"]),
        ("selected_path_id", pronounce["selected_path_id"]),
        ("mapping_profile", mapping["profile"]),
        ("lexicon_revision", lex["revision"]),
        ("rule_revision", lex["rule_revision"]),
    )))
    trace: list[str] = []

    try:
        path = next(
            p for p in pronounce["paths"]
            if p["path_id"] == pronounce["selected_path_id"]
        )
        units = tuple(PronunciationUnit(
            u["unit_id"], u["symbol"], u["start_offset"], u["end_offset"],
        ) for u in path["units"])
        definitions: dict[tuple[str, str], dict[str, Any]] = {
            (d["definition_id"], d["semantic_revision"]): d
            for d in lex["definitions"]
        }
        context = cast(dict[str, str], mapping["context"])
        occurrences: dict[tuple[str, str], dict[str, Any]] = {}

        for unit in units:
            matching: list[dict[str, Any]] = []
            for bundle in lex["bundles"]:
                if bundle["profile"] != mapping["profile"]:
                    continue
                touches = (bundle["unit_id"] == unit.unit_id or
                           unit.unit_id in bundle["target_unit_ids"])
                if not touches:
                    continue
                if (bundle["target_scope_kind"] != "EXACT_ONE_SELECTED_UNIT"
                        or bundle["target_unit_ids"] != [unit.unit_id]):
                    _fail("UNSUPPORTED_MAPPING_SCOPE", bundle["bundle_id"])
                if bundle["unit_id"] != unit.unit_id or bundle["symbol"] != unit.symbol:
                    _fail("INVALID_MAPPING_REFERENCE", bundle["bundle_id"])
                matching.append(bundle)
            bundle = _select(matching, context, kind="bundle:" + unit.unit_id)
            if not bundle["slots"]:
                _fail("UNMAPPED", "no required goal slots:" + unit.unit_id)
            for slot in bundle["slots"]:
                if not slot["candidates"]:
                    _fail("UNMAPPED", "empty slot:" + slot["slot_id"])
                cand = _select(slot["candidates"], context, kind="slot:" + slot["slot_id"])
                if cand["status"] != "SYNTHETIC_ONLY":
                    _fail("UNSUPPORTED_EVIDENCE_STATUS", cand["template_id"])
                def_key = (cand["definition_id"], cand["semantic_revision"])
                definition = definitions.get(def_key)
                if definition is None:
                    _fail("UNKNOWN_DEFINITION", cand["definition_id"])
                if definition["algebra"] != "SCALAR_INTERVAL":
                    _fail("UNSUPPORTED_GOAL_ALGEBRA", definition["definition_id"])
                key = (unit.unit_id, slot["slot_id"])
                occurrences[key] = {
                    "definition": definition, "candidate": cand,
                    "lower": _frac(cand["lower"]), "upper": _frac(cand["upper"]),
                }
                trace.append(
                    "SELECT:" + unit.unit_id + "/" + slot["slot_id"] + "/" +
                    cand["template_id"] + "@" + cand["evidence_id"])

        # Explicit episode sharing: no implicit normalization by task goal kind.
        groups: list[tuple[str, tuple[tuple[str, str], ...]]] = []
        assigned: set[tuple[str, str]] = set()
        for share in coord["shares"]:
            members = tuple(sorted((cast(str, member[0]), cast(str, member[1]))
                                   for member in share["members"]))
            if len({u for u, _ in members}) < 2:
                _fail("INCOMPATIBLE_SHARE", share["episode_id"])
            for member in members:
                if member not in occurrences:
                    _fail("UNKNOWN_SHARE_MEMBER", str(member))
                if member in assigned:
                    _fail("DUPLICATE_SHARE_MEMBER", str(member))
                assigned.add(member)
            groups.append((share["episode_id"], members))
            trace.append("SHARE:" + share["episode_id"] + ":" + str(members))
        for member in sorted(occurrences):
            if member not in assigned:
                groups.append(("", (member,)))

        tasks: list[MotorTask] = []
        goals: list[TaskGoal] = []
        member_to_task: dict[tuple[str, str], str] = {}
        task_ids: set[str] = set()
        for episode_id, members in sorted(groups):
            records = [occurrences[member] for member in members]
            first = records[0]["definition"]
            identity = (
                first["definition_id"], first["semantic_revision"],
                first["variable"], first["value_domain"], first["goal_kind"],
                first["applicability_domain"], tuple(sorted(first["capabilities"])),
            )
            for record in records:
                d = record["definition"]
                other = (
                    d["definition_id"], d["semantic_revision"], d["variable"],
                    d["value_domain"], d["goal_kind"], d["applicability_domain"],
                    tuple(sorted(d["capabilities"])),
                )
                if other != identity:
                    _fail("INCOMPATIBLE_SHARE", episode_id)
            lower = max(record["lower"] for record in records)
            upper = min(record["upper"] for record in records)
            if lower > upper:
                _fail("INCOMPATIBLE_SHARE", episode_id)
            templates = tuple(sorted(record["candidate"]["template_id"] for record in records))
            evidence = tuple(sorted(record["candidate"]["evidence_id"] for record in records))
            task_id = "task-" + _digest({
                "kind": "occurrence-id-v0", "episode": episode_id, "members": members,
                "templates": templates, "lexicon": lex["revision"],
                "rules": lex["rule_revision"],
            })
            if task_id in task_ids:
                _fail("TASK_ID_COLLISION", task_id)
            task_ids.add(task_id)
            tasks.append(MotorTask(task_id, first["goal_kind"], tuple(sorted(first["capabilities"]))))
            goals.append(TaskGoal(
                task_id, first["definition_id"], first["semantic_revision"],
                first["goal_kind"], tuple(sorted(first["capabilities"])),
                lower, upper, members, templates, evidence,
            ))
            for member in members:
                member_to_task[member] = task_id

        if coord["coordination_kind"] != "EXACT_EVENTS":
            _fail("UNSUPPORTED_COORDINATION", coord["coordination_kind"])
        anchors: list[EventAnchor] = []
        anchor_keys: set[tuple[str, Event]] = set()
        for a in coord["anchors"]:
            member = (a["unit_id"], a["slot_id"])
            if member not in member_to_task:
                _fail("UNKNOWN_TIMING_MEMBER", str(member))
            key = (member_to_task[member], Event(a["event"]))
            if key in anchor_keys:
                _fail("DUPLICATE_COORDINATION", str(member))
            anchor_keys.add(key)
            anchors.append(EventAnchor(key[0], key[1], _frac(a["time_s"])))
        couplings: list[CouplingConstraint] = []
        constraint_keys: set[tuple[str, Event, str, Event, Fraction]] = set()
        for link in coord["relations"]:
            src = (link["from_unit"], link["from_slot"])
            dest = (link["to_unit"], link["to_slot"])
            if src not in member_to_task or dest not in member_to_task:
                _fail("UNKNOWN_TIMING_MEMBER", str((src, dest)))
            ck = (
                member_to_task[src], Event(link["from_event"]),
                member_to_task[dest], Event(link["to_event"]), _frac(link["lag_s"]),
            )
            if ck in constraint_keys:
                _fail("DUPLICATE_COORDINATION", str((src, dest)))
            constraint_keys.add(ck)
            couplings.append(CouplingConstraint(*ck))

        associations = tuple(sorted({
            TaskAssociation(unit_id, task_id)
            for (unit_id, _), task_id in member_to_task.items()
        }, key=lambda x: (x.unit_id, x.task_id)))
        plan = SymbolicPlan(
            segment_id=segment["segment_id"], source_text=segment["source_text"],
            pronunciation_units=units,
            tasks=tuple(sorted(tasks, key=lambda t: t.task_id)),
            associations=associations,
            couplings=tuple(sorted(couplings, key=lambda c: (
                c.source_task_id, str(c.source_event), c.target_task_id,
                str(c.target_event), c.lag_s,
            ))),
            anchors=tuple(sorted(anchors, key=lambda a: (
                a.task_id, str(a.event), a.time_s,
            ))),
        )
        validation = validate_plan(plan)
        if validation.status != ReportStatus.STRUCTURALLY_VALID:
            code = validation.diagnostics[0].code if validation.diagnostics else "INVALID_PLAN"
            _fail(code, "; ".join(x.code + ":" + x.subject_id for x in validation.diagnostics))
        timing = resolve_timing(plan)
        if timing.status != ReportStatus.RESOLVED:
            _fail("UNRESOLVED_TIMING", "; ".join(x.subject_id for x in timing.diagnostics))
        plan_sha = plan_digest(plan)
        ordered_goals = tuple(sorted(goals, key=lambda g: g.task_id))
        candidate_sha = _digest({
            "semantic_request": semantic_sha, "plan": plan_sha,
            "goals": [{
                "task_id": g.task_id, "definition": g.definition_id,
                "revision": g.semantic_revision, "goal_kind": g.goal_kind,
                "capabilities": g.capabilities, "members": g.members,
                "templates": g.templates, "evidence": g.evidence_ids,
                "lower": [g.lower.numerator, g.lower.denominator],
                "upper": [g.upper.numerator, g.upper.denominator],
            } for g in ordered_goals],
        })
        return CompileResult(
            plan, ordered_goals, timing, _receipt(
                "RESOLVED", "SYMBOLIC", "OK", raw_sha, semantic_sha,
                provenance, tuple(sorted(trace)), (), plan_sha, candidate_sha,
            ),
        )
    except _Refusal as error:
        # Preserve failure stage: lexical selection is not event coordination.
        if error.code in {
            "CONTRADICTORY_TIMING", "NONPOSITIVE_DURATION",
            "NEGATIVE_ANCHORED_TIME", "UNRESOLVED_TIMING",
        }:
            stage = "TIMING"
        elif error.code in {
            "UNSUPPORTED_COORDINATION", "UNKNOWN_TIMING_MEMBER",
            "DUPLICATE_COORDINATION",
        }:
            stage = "COORDINATION"
        elif error.code in {
            "INVALID_PLAN", "DUPLICATE_ASSOCIATION",
            "UNKNOWN_ASSOCIATION_ENDPOINT", "UNASSOCIATED_UNIT",
            "ORPHAN_TASK", "DUPLICATE_COUPLING",
        }:
            stage = "GRAPH"
        else:
            stage = "MAPPING"
        return CompileResult(
            None, (), None, _receipt(
                "REJECTED", stage, error.code, raw_sha, semantic_sha,
                provenance, tuple(sorted(trace)), (error.detail,),
            ),
        )


def compile_wire(payload: object) -> CompileResult:
    """Finite ingress is always applied first; nonbytes never traversed."""
    parsed = parse_canonical_request(payload)
    if parsed.request is None:
        return _ingress_fail(parsed.receipt)
    return _compile_accepted(parsed.request, parsed.receipt.submission_sha256)


def compile_canonical(request: CanonicalCompileRequest) -> CompileResult:
    """Revalidate even an allegedly immutable snapshot (may be forged by caller)."""
    if not isinstance(request, CanonicalCompileRequest):
        return compile_wire(request)
    parsed = parse_canonical_request(request.canonical_bytes)
    if parsed.request is None:
        return _ingress_fail(parsed.receipt)
    if (request.schema_version != parsed.request.schema_version
            or request.canonical_sha256 != parsed.request.canonical_sha256
            or request.canonical_bytes != parsed.request.canonical_bytes):
        return CompileResult(
            None, (), None, _receipt(
                "REJECTED", "INGRESS", "FORGED_CANONICAL_SNAPSHOT", None, None,
            ),
        )
    return _compile_accepted(request, parsed.receipt.submission_sha256)


def timeline_table(result: CompileResult) -> tuple[tuple[str, Fraction, Fraction], ...]:
    """Synthetic exact timing rows; no physical organ actuation or audio."""
    if result.plan is None or result.timing is None:
        return ()
    table = {(tid, event): value for tid, event, value in result.timing.events}
    return tuple(sorted(
        (task.task_id, table[(task.task_id, Event.ONSET)],
         table[(task.task_id, Event.OFFSET)])
        for task in result.plan.tasks
    ))
