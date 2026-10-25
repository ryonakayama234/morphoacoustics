"""Gate B finite TaskLexicon -> unchanged SMC-3 IR.

Research-only synthetic semantics. No phonetic, bodily or acoustic claims.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from typing import Mapping, cast

from .model import (
    CouplingConstraint, Event, EventAnchor, MotorTask, PronunciationUnit,
    ReportStatus, SymbolicPlan, TaskAssociation,
)
from .validation import plan_digest, resolve_timing, validate_plan
from .smc4_types import (
    CompileReceipt, CompileResult, GoalSlot, Predicate, PronunciationPath,
    ShareDecision, SlotCandidate, TaskDefinition, TaskLexicon, TemplateBundle,
    TimeAnchor, TimeRelation, canonical_request_fingerprint, digest_payload,
    evaluate, pick, stable_task_id, valid_predicate,
)

@dataclass(frozen=True)
class _Occurrence:
    unit_id: str
    slot_id: str
    bundle_id: str
    candidate: SlotCandidate
    definition: TaskDefinition

@dataclass(frozen=True)
class _Group:
    task_id: str
    members: tuple[_Occurrence, ...]
    lower: Fraction
    upper: Fraction

def _safe_digest(value: object) -> str:
    return sha256(repr(value).encode("utf-8", "backslashreplace")).hexdigest()

def _anchored_seconds(plan: SymbolicPlan) -> dict[tuple[str, Event], Fraction]:
    """Independently proved exact event times, even with unrelated free events.

    This is a read-only partial-time projection after SMC-3 validation succeeds;
    it never invents times for unanchored components.
    """
    origin: tuple[str, Event] = ("", Event.ONSET)
    edges: dict[tuple[str, Event],
                list[tuple[tuple[str, Event], Fraction]]] = defaultdict(list)
    def link(left: tuple[str, Event], right: tuple[str, Event],
             lag: Fraction) -> None:
        edges[left].append((right, lag))
        edges[right].append((left, -lag))
    for anchor in plan.anchors:
        link(origin, (anchor.task_id, anchor.event), anchor.time_s)
    for relation in plan.couplings:
        link((relation.source_task_id, relation.source_event),
             (relation.target_task_id, relation.target_event), relation.lag_s)
    times = {origin: Fraction(0)}
    queue = deque([origin])
    while queue:
        node = queue.popleft()
        for other, lag in edges[node]:
            if other not in times:
                times[other] = times[node] + lag
                queue.append(other)
    return times

def compile_lexicon(
    segment_id: str, source_text: str, language: str, profile: str,
    paths: tuple[PronunciationPath, ...], selected_path_id: str | None,
    lexicon: TaskLexicon, context: Mapping[str, str],
    *, shares: tuple[ShareDecision, ...] = (),
    anchors: tuple[TimeAnchor, ...] = (),
    relations: tuple[TimeRelation, ...] = (),
    coordination_kind: str = "EXACT_EVENTS",
    source_revision: str = "unspecified",
) -> CompileResult:
    """One complete explicitly selected path, no text-to-reading inference."""
    input_fingerprint = canonical_request_fingerprint({
        "segment_id": segment_id, "source_text": source_text,
        "source_revision": source_revision, "language": language,
        "profile": profile, "paths": paths,
        "selected_path_id": selected_path_id, "lexicon": lexicon,
        "context": context, "shares": shares,
        "anchors": anchors, "relations": relations,
        "coordination_kind": coordination_kind,
    })
    # A rejection never returns a partially assembled SymbolicPlan.
    # Its fingerprint binds all submitted hypotheses and even failed timing.
    def reject(code: str, *details: str) -> CompileResult:
        normalized = tuple(sorted(str(s) for s in details))
        token = digest_payload({
            "input_fingerprint": input_fingerprint,
            "code": code, "details": normalized,
        })
        return CompileResult(None, CompileReceipt(
            "REJECTED", code, normalized, token, (), None, "NOT_RESOLVED",
            input_fingerprint=input_fingerprint))

    def scalar(s: object) -> bool:
        return isinstance(s, str) and bool(s) and not any(
            0xD800 <= ord(ch) <= 0xDFFF for ch in s)

    # Canonical request fingerprint above handles malformed arbitrary runtime
    # containers; NOW validate the complete trust boundary before any access
    # that assumes dataclass members or hashable identifiers.
    if (not isinstance(lexicon, TaskLexicon)
            or not isinstance(lexicon.definitions, tuple)
            or not isinstance(lexicon.bundles, tuple)):
        return reject("INVALID_INPUT", "malformed TaskLexicon container")
    if not all(scalar(s) for s in
               (segment_id, source_text, language, profile, source_revision,
                lexicon.revision, lexicon.rule_revision)):
        return reject("INVALID_INPUT", "invalid source/identifier/Unicode scalar")
    if (not isinstance(context, Mapping) or
            any(not scalar(k) or not isinstance(v, str) or not scalar(v)
                for k, v in context.items())):
        return reject("INVALID_INPUT", "malformed context")
    if (not isinstance(paths, (tuple, list)) or not paths
            or any(not isinstance(p, PronunciationPath)
                   or not scalar(p.path_id) for p in paths)):
        return reject("INVALID_INPUT", "malformed pronunciation paths")
    if len({p.path_id for p in paths}) != len(paths):
        return reject("INVALID_INPUT", "duplicate pronunciation paths")
    if selected_path_id is not None and not scalar(selected_path_id):
        return reject("INVALID_INPUT", "malformed selected pronunciation path ID")
    if selected_path_id is None:
        return reject("AMBIGUOUS_PRONUNCIATION_PATH" if len(paths) > 1
                      else "INVALID_INPUT", *(p.path_id for p in paths))
    choices = [p for p in paths if p.path_id == selected_path_id]
    if len(choices) != 1:
        return reject("INVALID_INPUT", "selected path not present")
    path = choices[0]
    if type(path.complete) is not bool:
        return reject("INVALID_INPUT", "path.complete must be a bool")
    if (not isinstance(path.units, (tuple, list))
            or any(not isinstance(u, PronunciationUnit) for u in path.units)
            or not isinstance(path.required_spans, (tuple, list))):
        return reject("INVALID_INPUT", "malformed pronunciation/coverage container")
    if (not scalar(path.path_id) or
            any(not scalar(u.unit_id) or not scalar(u.symbol) for u in path.units)):
        return reject("INVALID_INPUT", "bad unit/path identifier or symbol")
    if len({u.unit_id for u in path.units}) != len(path.units):
        return reject("INVALID_INPUT", "duplicate selected path unit IDs")
    for u in path.units:
        if (type(u.start_offset) is not int or type(u.end_offset) is not int or
                not 0 <= u.start_offset < u.end_offset <= len(source_text)):
            return reject("INVALID_INPUT", u.unit_id, "invalid codepoint span")
    for span in path.required_spans:
        if (not isinstance(span, (tuple, list)) or len(span) != 2
                or type(span[0]) is not int or type(span[1]) is not int
                or not 0 <= span[0] < span[1] <= len(source_text)):
            return reject("INVALID_INPUT", "invalid required source coverage")
    if not path.complete or not path.units or not path.required_spans:
        return reject("UNRESOLVED_PRONUNCIATION", path.path_id)
    covered = {offset for u in path.units
               for offset in range(u.start_offset, u.end_offset)}
    if any(i not in covered for lo, hi in path.required_spans
           for i in range(lo, hi)):
        return reject("UNRESOLVED_PRONUNCIATION", path.path_id, "coverage gap")
    # Explicitly refuse overlap in the initial synthetic fixture domain.
    sorted_units = sorted(path.units, key=lambda u: (u.start_offset, u.end_offset, u.unit_id))
    if any(x.end_offset > y.start_offset
           for x, y in zip(sorted_units, sorted_units[1:])):
        return reject("UNSUPPORTED_MAPPING_SCOPE", "overlapping selected occurrences")

    defs: dict[tuple[str, str], TaskDefinition] = {}
    invalid_definitions: set[str] = set()
    for declared_definition in lexicon.definitions:
        if not isinstance(declared_definition, TaskDefinition):
            invalid_definitions.add("malformed TaskDefinition declaration")
            continue
        declaration_valid = all(scalar(s) for s in (
            declared_definition.definition_id, declared_definition.semantic_revision,
            declared_definition.variable, declared_definition.value_domain,
            declared_definition.goal_kind, declared_definition.applicability_domain))
        if not declaration_valid:
            invalid_definitions.add("malformed TaskDefinition declaration")
            continue
        key = (declared_definition.definition_id, declared_definition.semantic_revision)
        if key in defs:
            invalid_definitions.add(declared_definition.definition_id)
            continue
        caps = declared_definition.capabilities
        if (not isinstance(caps, tuple) or any(not scalar(cap) for cap in caps)
                or len(set(caps)) != len(caps)):
            invalid_definitions.add(declared_definition.definition_id)
            continue
        defs[key] = declared_definition
    if invalid_definitions:
        return reject("INVALID_PLAN", *sorted(invalid_definitions))
    # Every malformed rule is rejected, including losing competitors.
    # Collect a deterministic diagnostic set; never report first-in-input
    # declaration (F09 order-invariance of rejected experiments).
    invalid_rules: set[str] = set()
    for declared_bundle in lexicon.bundles:
        if not isinstance(declared_bundle, TemplateBundle):
            invalid_rules.add("malformed bundle declaration")
            continue
        if (not all(scalar(s) for s in (
                declared_bundle.bundle_id, declared_bundle.unit_id,
                declared_bundle.symbol, declared_bundle.profile,
                declared_bundle.target_scope_kind))
                or not isinstance(declared_bundle.target_unit_ids, tuple)
                or any(not scalar(u) for u in declared_bundle.target_unit_ids)):
            invalid_rules.add("invalid bundle identifier or mapping scope")
            continue
        if not valid_predicate(declared_bundle.context):
            invalid_rules.add(declared_bundle.bundle_id)
        if not isinstance(declared_bundle.slots, tuple):
            invalid_rules.add(declared_bundle.bundle_id)
            continue
        for declared_slot in declared_bundle.slots:
            if not isinstance(declared_slot, GoalSlot):
                invalid_rules.add(declared_bundle.bundle_id)
                continue
            if (not scalar(declared_slot.slot_id)
                    or not isinstance(declared_slot.candidates, tuple)):
                invalid_rules.add(declared_bundle.bundle_id)
                continue
            for declared_candidate in declared_slot.candidates:
                if (not isinstance(declared_candidate, SlotCandidate)
                        or not all(scalar(s) for s in (
                            declared_candidate.template_id,
                            declared_candidate.definition_id,
                            declared_candidate.semantic_revision,
                            declared_candidate.evidence_id,
                            declared_candidate.status))
                        or not valid_predicate(declared_candidate.context)):
                    invalid_rules.add(declared_bundle.bundle_id + "::" + declared_slot.slot_id)
    if invalid_rules:
        return reject("INVALID_PLAN", "invalid lexicon predicate or declaration",
                      *sorted(invalid_rules))
    units_by_id = {u.unit_id: u for u in path.units}
    unsupported_scope_ids: set[str] = set()
    for b in lexicon.bundles:
        if b.profile != profile:
            continue
        scope = set(b.target_unit_ids) | {b.unit_id}
        if (b.target_scope_kind != "EXACT_ONE_SELECTED_UNIT"
                or (b.target_unit_ids and b.target_unit_ids != (b.unit_id,))):
            if (scope & units_by_id.keys() and evaluate(b.context, context) != "FALSE"):
                unsupported_scope_ids.add(b.bundle_id)
    if unsupported_scope_ids:
        return reject("UNSUPPORTED_MAPPING_SCOPE", *sorted(unsupported_scope_ids))
    occurrences: dict[tuple[str, str], _Occurrence] = {}
    evidence: set[str] = set()
    selected_bundles: list[str] = []
    for unit in sorted(path.units, key=lambda u: u.unit_id):
        matching = tuple(b for b in lexicon.bundles
                         if b.profile == profile and b.unit_id == unit.unit_id
                         and b.symbol == unit.symbol
                         and b.target_scope_kind == "EXACT_ONE_SELECTED_UNIT"
                         and (not b.target_unit_ids or
                              b.target_unit_ids == (unit.unit_id,)))
        picked, error = pick(cast(tuple[object, ...], matching), context)
        if error != "SELECTED":
            return reject(error, unit.unit_id, "bundle selection",
                          *(candidate_bundle.bundle_id for candidate_bundle in matching))
        b = cast(TemplateBundle, picked)
        if not scalar(b.bundle_id) or not b.slots:
            return reject("INVALID_PLAN", unit.unit_id, "empty/invalid bundle")
        if len({s.slot_id for s in b.slots}) != len(b.slots):
            return reject("INVALID_PLAN", b.bundle_id, "duplicate required slots")
        selected_bundles.append(b.bundle_id)
        evidence.add(b.bundle_id)
        for slot in sorted(b.slots, key=lambda s: s.slot_id):
            if not scalar(slot.slot_id):
                return reject("INVALID_PLAN", b.bundle_id, "invalid slot")
            picked_c, error = pick(cast(tuple[object, ...], slot.candidates), context)
            if error != "SELECTED":
                return reject(error, unit.unit_id, slot.slot_id,
                              *(candidate_template.template_id
                                for candidate_template in slot.candidates))
            c = cast(SlotCandidate, picked_c)
            d = defs.get((c.definition_id, c.semantic_revision))
            if d is None or not scalar(c.template_id) or not scalar(c.evidence_id):
                return reject("INVALID_PLAN", unit.unit_id, slot.slot_id,
                              "dangling definition or provenance")
            if (not isinstance(c.lower, Fraction) or
                    not isinstance(c.upper, Fraction) or c.lower > c.upper):
                return reject("INVALID_PLAN", c.template_id, "invalid goal region")
            if c.status != "SYNTHETIC_ONLY":
                return reject("UNVERIFIED", c.template_id,
                              "empirical mapping evidence not audited in Gate B")
            occurrences[(unit.unit_id, slot.slot_id)] = _Occurrence(
                unit.unit_id, slot.slot_id, b.bundle_id, c, d)
            evidence.update((c.template_id, c.evidence_id, d.definition_id))
    if not occurrences:
        return reject("UNMAPPED", path.path_id)

    used: set[tuple[str, str]] = set()
    groups: list[_Group] = []
    if (not isinstance(shares, tuple) or
            any(not isinstance(s, ShareDecision) for s in shares)):
        return reject("INVALID_PLAN", "invalid share-decision container")
    for decision in shares:
        if (not scalar(decision.episode_id)
                or not isinstance(decision.members, tuple)
                or len(decision.members) < 2
                or any(not isinstance(m, tuple) or len(m) != 2
                       or not all(scalar(part) for part in m)
                       for m in decision.members)):
            return reject("INVALID_PLAN", "malformed share-member coordinate")
    if len({s.episode_id for s in shares}) != len(shares):
        return reject("INVALID_PLAN", "duplicate share episode IDs")
    for decision in sorted(shares, key=lambda s: s.episode_id):
        members = tuple(sorted(decision.members))
        if (not scalar(decision.episode_id) or len(members) < 2 or
                len(set(members)) != len(members) or
                any(k not in occurrences or k in used for k in members) or
                len({k[0] for k in members}) != len(members)):
            return reject("INVALID_PLAN", decision.episode_id,
                          "bad, overlapping or repeated share members")
        chosen = tuple(occurrences[k] for k in members)
        first = chosen[0].definition
        if any((v.definition.definition_id, v.definition.semantic_revision,
                v.definition.variable, v.definition.value_domain,
                v.definition.algebra, v.definition.applicability_domain) !=
               (first.definition_id, first.semantic_revision, first.variable,
                first.value_domain, first.algebra, first.applicability_domain)
               for v in chosen[1:]) or first.algebra != "SCALAR_INTERVAL":
            return reject("UNVERIFIED_SHARE_COMPATIBILITY", decision.episode_id)
        low = max(o.candidate.lower for o in chosen)
        high = min(o.candidate.upper for o in chosen)
        if low > high:
            return reject("TASK_SHARE_CONFLICT", decision.episode_id,
                          *(o.candidate.template_id for o in chosen))
        groups.append(_Group(stable_task_id(("shared", path.path_id,
                                            decision.episode_id)),
                             chosen, low, high))
        used.update(members)
        evidence.add("episode:" + decision.episode_id)
    for key in sorted(occurrences):
        if key not in used:
            o = occurrences[key]
            groups.append(_Group(stable_task_id(("local", path.path_id,
                                                 o.unit_id, o.slot_id)),
                                 (o,), o.candidate.lower, o.candidate.upper))
    groups.sort(key=lambda g: g.task_id)
    if len({g.task_id for g in groups}) != len(groups):
        return reject("INVALID_PLAN", "colliding task IDs")

    by_occ = {(o.unit_id, o.slot_id): g.task_id for g in groups for o in g.members}
    tasks = tuple(MotorTask(g.task_id, g.members[0].definition.goal_kind,
                            tuple(sorted(g.members[0].definition.capabilities)))
                  for g in groups)
    associations = tuple(TaskAssociation(u, t) for u, t in
                         sorted({(o.unit_id, g.task_id)
                                 for g in groups for o in g.members}))
    if coordination_kind != "EXACT_EVENTS":
        return reject("UNSUPPORTED_COORDINATION", coordination_kind)
    # Frozen dataclass hints are not runtime input validation. Validate the
    # entire timing declaration shape BEFORE hashing/sorting coordinates or
    # looking them up in the graph. No partial SymbolicPlan on any failure.
    if (not isinstance(anchors, tuple) or
            any(not isinstance(a, TimeAnchor)
                or not scalar(a.unit_id) or not scalar(a.slot_id)
                or not isinstance(a.event, Event)
                or not isinstance(a.time_s, Fraction)
                for a in anchors)):
        return reject("INVALID_PLAN", "invalid time anchor declaration")
    if (not isinstance(relations, tuple) or
            any(not isinstance(q, TimeRelation)
                or not all(scalar(v) for v in
                           (q.from_unit, q.from_slot, q.to_unit, q.to_slot))
                or not isinstance(q.from_event, Event)
                or not isinstance(q.to_event, Event)
                or not isinstance(q.lag_s, Fraction)
                for q in relations)):
        return reject("INVALID_PLAN", "invalid time relation declaration")
    # Proven dangling references are errors independent of caller declaration
    # ordering (F09). Reject ALL stage-local failures in a canonical set.
    dangling: set[str] = set()
    for a in anchors:
        if (a.unit_id, a.slot_id) not in by_occ:
            dangling.add("anchor:" + a.unit_id + ":" + a.slot_id)
    for q in relations:
        if (q.from_unit, q.from_slot) not in by_occ:
            dangling.add("relation-from:" + q.from_unit + ":" + q.from_slot)
        if (q.to_unit, q.to_slot) not in by_occ:
            dangling.add("relation-to:" + q.to_unit + ":" + q.to_slot)
    if dangling:
        return reject("INVALID_PLAN", *sorted(dangling))
    prepared_anchors: list[EventAnchor] = [
        EventAnchor(by_occ[(a.unit_id, a.slot_id)], a.event, a.time_s)
        for a in anchors
    ]
    prepared_relations: list[CouplingConstraint] = [
        CouplingConstraint(
            by_occ[(q.from_unit, q.from_slot)], q.from_event,
            by_occ[(q.to_unit, q.to_slot)], q.to_event, q.lag_s)
        for q in relations
    ]
    plan = SymbolicPlan(
        segment_id, source_text,
        tuple(sorted(path.units, key=lambda u: u.unit_id)), tasks, associations,
        # Sharing can project multiple identical lexical constraints onto
        # one Task; identical equalities are idempotent, not contradictory.
        tuple(sorted(set(prepared_relations), key=lambda c: (
            c.source_task_id, c.source_event, c.target_task_id,
            c.target_event, c.lag_s))),
        tuple(sorted(set(prepared_anchors), key=lambda a: (a.task_id, a.event, a.time_s))),
    )
    v = validate_plan(plan)
    if v.status is ReportStatus.INVALID:
        return reject("INVALID_PLAN", *(d.code + ":" + d.subject_id for d in v.diagnostics))
    timing = resolve_timing(plan)
    time_status = "RESOLVED" if timing.status is ReportStatus.RESOLVED else "UNRESOLVED"
    # Partial timing is enough to prove a contradiction for one pair; all
    # other unanchored Task windows remain unknown, not defaulted to zero.
    seconds = _anchored_seconds(plan)
    for ix, ga in enumerate(groups):
        for gb in groups[ix + 1:]:
            da, db = ga.members[0].definition, gb.members[0].definition
            if ((da.definition_id, da.semantic_revision, da.variable,
                 da.value_domain, da.algebra) !=
                (db.definition_id, db.semantic_revision, db.variable,
                 db.value_domain, db.algebra) or da.algebra != "SCALAR_INTERVAL"):
                continue
            keys = tuple((tid, event) for tid in (ga.task_id, gb.task_id)
                         for event in (Event.ONSET, Event.OFFSET))
            if not all(k in seconds for k in keys):
                continue
            overlap = (max(seconds[(ga.task_id, Event.ONSET)],
                           seconds[(gb.task_id, Event.ONSET)]) <
                       min(seconds[(ga.task_id, Event.OFFSET)],
                           seconds[(gb.task_id, Event.OFFSET)]))
            if overlap and (ga.upper < gb.lower or gb.upper < ga.lower):
                return reject("TASK_GOAL_CONFLICT", ga.task_id, gb.task_id)

    # Receipt is separate from the frozen SMC-3 plan digest.
    provenance = tuple(sorted((
        (o.unit_id, o.slot_id, o.bundle_id, o.candidate.template_id,
         o.candidate.evidence_id, o.definition.definition_id,
         o.definition.semantic_revision, o.definition.variable,
         o.definition.value_domain, o.candidate.lower, o.candidate.upper)
        for o in occurrences.values()), key=lambda x: (x[0], x[1])))
    group_details = tuple(sorted((
        g.task_id, tuple(sorted((o.unit_id, o.slot_id, o.candidate.template_id)
                                for o in g.members)), g.lower, g.upper)
        for g in groups))
    pdigest = plan_digest(plan)
    receipt_digest = digest_payload({
        "schema": "smc4-gate-b-lexical-receipt/v0",
        "segment_id": segment_id, "source_text": source_text,
        "source_revision": source_revision, "language": language, "profile": profile,
        "selected_path": path.path_id, "pronunciation": tuple(sorted(
            (u.unit_id, u.symbol, u.start_offset, u.end_offset) for u in path.units)),
        "lexicon_revision": lexicon.revision, "rule_revision": lexicon.rule_revision,
        "context": tuple(sorted(context.items())),
        "selected_bundles": tuple(sorted(selected_bundles)),
        "selected_templates": provenance,
        "groups": group_details, "plan_digest": pdigest,
        "timing_status": time_status, "input_fingerprint": input_fingerprint,
    })
    readable_provenance = tuple(sorted((
        (o.unit_id, o.slot_id, o.bundle_id, o.candidate.template_id,
         o.candidate.evidence_id, o.definition.definition_id,
         o.definition.semantic_revision, o.definition.variable,
         o.definition.value_domain, str(o.candidate.lower),
         str(o.candidate.upper)) for o in occurrences.values()
    ), key=lambda item: (item[0], item[1])))
    target_ranges = tuple((g.task_id, g.lower, g.upper) for g in groups)
    input_provenance = tuple(sorted((
        ("path_id", path.path_id), ("source_revision", source_revision),
        ("language", language), ("profile", profile),
        ("lexicon_revision", lexicon.revision),
        ("rule_revision", lexicon.rule_revision),
    )))
    return CompileResult(plan, CompileReceipt(
        "MAPPED_SYMBOLIC", "OK", (), receipt_digest, tuple(sorted(evidence)),
        pdigest, time_status, "UNVERIFIED", readable_provenance,
        target_ranges, input_provenance, input_fingerprint))


__all__ = [
    "PronunciationPath", "Predicate", "TaskDefinition", "SlotCandidate", "GoalSlot",
    "TemplateBundle", "TaskLexicon", "ShareDecision", "TimeAnchor",
    "TimeRelation", "CompileReceipt", "CompileResult", "compile_lexicon",
]
