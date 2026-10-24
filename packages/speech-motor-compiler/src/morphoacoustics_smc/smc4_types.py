"""SMC-4 Gate B synthetic research types. No physical or phonetic assertions."""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from fractions import Fraction
from hashlib import sha256
from json import dumps
from typing import Mapping

from .model import Event, PronunciationUnit, SymbolicPlan


@dataclass(frozen=True, slots=True)
class PronunciationPath:
    path_id: str
    units: tuple[PronunciationUnit, ...]
    required_spans: tuple[tuple[int, int], ...]
    complete: bool


@dataclass(frozen=True, slots=True)
class Predicate:
    op: str  # TRUE, FALSE, EQ, NOT, AND, OR
    key: str = ""
    expected: str = ""
    operands: tuple[Predicate, ...] = ()


@dataclass(frozen=True, slots=True)
class TaskDefinition:
    definition_id: str
    semantic_revision: str
    variable: str
    value_domain: str
    goal_kind: str
    applicability_domain: str = "synthetic_functional_passage"
    capabilities: tuple[str, ...] = ()
    algebra: str = "SCALAR_INTERVAL"


@dataclass(frozen=True, slots=True)
class SlotCandidate:
    template_id: str
    definition_id: str
    semantic_revision: str
    lower: Fraction
    upper: Fraction
    context: Predicate
    priority: int | None
    evidence_id: str
    status: str = "SYNTHETIC_ONLY"


@dataclass(frozen=True, slots=True)
class GoalSlot:
    slot_id: str
    candidates: tuple[SlotCandidate, ...]


@dataclass(frozen=True, slots=True)
class TemplateBundle:
    bundle_id: str
    unit_id: str
    symbol: str
    slots: tuple[GoalSlot, ...]
    context: Predicate
    priority: int | None
    profile: str
    target_scope_kind: str = "EXACT_ONE_SELECTED_UNIT"
    target_unit_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TaskLexicon:
    revision: str
    rule_revision: str
    definitions: tuple[TaskDefinition, ...]
    bundles: tuple[TemplateBundle, ...]


@dataclass(frozen=True, slots=True)
class ShareDecision:
    episode_id: str
    members: tuple[tuple[str, str], ...]  # (path-local unit ID, required slot ID)


@dataclass(frozen=True, slots=True)
class TimeAnchor:
    unit_id: str
    slot_id: str
    event: Event
    time_s: Fraction


@dataclass(frozen=True, slots=True)
class TimeRelation:
    from_unit: str
    from_slot: str
    from_event: Event
    to_unit: str
    to_slot: str
    to_event: Event
    lag_s: Fraction


@dataclass(frozen=True, slots=True)
class CompileReceipt:
    status: str  # MAPPED_SYMBOLIC or REJECTED
    code: str
    detail: tuple[str, ...]
    digest: str
    evidence: tuple[str, ...]
    plan_digest: str | None = None
    timing_status: str = "NOT_REQUESTED"
    body_status: str = "UNVERIFIED"
    # Explicitly inspectable provenance, not merely an opaque hash.
    mapping_provenance: tuple[tuple[str, ...], ...] = ()
    task_targets: tuple[tuple[str, Fraction, Fraction], ...] = ()
    input_provenance: tuple[tuple[str, str], ...] = ()
    input_fingerprint: str = ""


@dataclass(frozen=True, slots=True)
class CompileResult:
    plan: SymbolicPlan | None
    receipt: CompileReceipt


def evaluate(predicate: Predicate, facts: Mapping[str, str]) -> str:
    """Strong Kleene three-valued logic with no guessed context facts."""
    if predicate.op == "TRUE":
        return "TRUE"
    if predicate.op == "FALSE":
        return "FALSE"
    if predicate.op == "EQ":
        if not predicate.key:
            return "UNKNOWN"
        if predicate.key not in facts:
            return "UNKNOWN"
        return "TRUE" if facts[predicate.key] == predicate.expected else "FALSE"
    if predicate.op == "NOT" and len(predicate.operands) == 1:
        value = evaluate(predicate.operands[0], facts)
        return {"TRUE": "FALSE", "FALSE": "TRUE", "UNKNOWN": "UNKNOWN"}[value]
    if predicate.op in ("AND", "OR") and predicate.operands:
        values = tuple(evaluate(p, facts) for p in predicate.operands)
        if predicate.op == "AND":
            if "FALSE" in values:
                return "FALSE"
            return "UNKNOWN" if "UNKNOWN" in values else "TRUE"
        if "TRUE" in values:
            return "TRUE"
        return "UNKNOWN" if "UNKNOWN" in values else "FALSE"
    return "UNKNOWN"


def pick(candidates: tuple[object, ...], facts: Mapping[str, str]
         ) -> tuple[object | None, str]:
    """Return a uniquely qualified choice; uncertainty is never a fallback."""
    true = [c for c in candidates if evaluate(c.context, facts) == "TRUE"]  # type: ignore[attr-defined]
    unknown = [c for c in candidates if evaluate(c.context, facts) == "UNKNOWN"]  # type: ignore[attr-defined]
    if not true:
        return (None, "INSUFFICIENT_CONTEXT" if unknown else "UNMAPPED")
    if len(true) == 1:
        winner = true[0]
    elif all(c.priority is not None for c in true):  # type: ignore[attr-defined]
        highest = max(c.priority for c in true)  # type: ignore[attr-defined]
        winners = [c for c in true if c.priority == highest]  # type: ignore[attr-defined]
        if len(winners) != 1:
            return None, "AMBIGUOUS"
        winner = winners[0]
    else:
        return None, "AMBIGUOUS"
    if unknown:
        # An unknown competitor is harmless only when explicit priority
        # proves it cannot win, independent of predicate completion.
        if (winner.priority is None or  # type: ignore[attr-defined]
                any(c.priority is None or c.priority >= winner.priority  # type: ignore[attr-defined]
                    for c in unknown)):
            return None, "INSUFFICIENT_CONTEXT"
    return winner, "SELECTED"


def _default_json(value: object) -> object:
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    raise TypeError("unsupported canonical field")


def digest_payload(payload: object) -> str:
    raw = dumps(payload, sort_keys=True, ensure_ascii=False,
                separators=(",", ":"), default=_default_json, allow_nan=False)
    return sha256(raw.encode("utf-8")).hexdigest()


def stable_task_id(parts: tuple[str, ...]) -> str:
    return "smc4:" + digest_payload(parts)[:32]


# Unlike a success plan hash, a rejection receipt must identify the
# complete attempted experiment (including invalid and unselected inputs).
_UNORDERED_FIELDS = frozenset({
    "paths", "units", "required_spans", "definitions", "bundles",
    "slots", "candidates", "members", "operands", "shares",
    "anchors", "relations",
})


def canonical_request_fingerprint(request: Mapping[str, object]) -> str:
    """Deterministic safe fingerprint even for malformed Unicode/runtime data.

    Sort genuinely unordered declarations; preserve ordered pairs and
    direction-sensitive tuples. Do not use Python repr of the entire lexicon,
    since it is ordering-sensitive and not stable under source reordering.
    """
    def normalized(value: object, field_name: str = "") -> object:
        if isinstance(value, Fraction):
            return {"rational": [value.numerator, value.denominator]}
        if is_dataclass(value) and not isinstance(value, type):
            return {"dataclass": type(value).__name__,
                    "fields": normalized(asdict(value))}
        if isinstance(value, Mapping):
            entries = [(str(k), normalized(v, str(k))) for k, v in value.items()]
            return {"entries": sorted(entries, key=lambda entry: entry[0])}
        if isinstance(value, (tuple, list, set, frozenset)):
            values = [normalized(item) for item in value]
            if field_name in _UNORDERED_FIELDS or isinstance(value, (set, frozenset)):
                values.sort(key=lambda item: dumps(item, sort_keys=True,
                                                  ensure_ascii=True))
            return values
        if value is None or isinstance(value, (str, bool, int)):
            return value
        # Nonfinite/unsupported values are fingerprinted, not executed as
        # valid script input; their public validation remains separate.
        return {"unrecognized_type": type(value).__name__, "repr": repr(value)}

    encoded = dumps(normalized(request), sort_keys=True, ensure_ascii=True,
                    separators=(",", ":"), allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()
