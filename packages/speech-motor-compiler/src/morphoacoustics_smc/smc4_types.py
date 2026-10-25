"""SMC-4 Gate B synthetic research types. No physical or phonetic assertions."""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
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



def valid_predicate(predicate: object) -> bool:
    """Validate Strong-Kleene predicates as bounded finite DAGs, not trees.

    Memoized subtree *heights* are checked at every attachment. An already
    validated child can be attached under a deeper parent, but cannot bypass
    the absolute root-to-leaf depth bound. Only back-edges on the ACTIVE path
    are cycles; repeated references to an immutable subtree remain legal.
    """
    pending: list[tuple[object, bool, int]] = [(predicate, False, 0)]
    active: set[int] = set()
    heights: dict[int, int] = {}
    while pending:
        node, leaving, depth = pending.pop()
        if not isinstance(node, Predicate):
            return False
        identity = id(node)
        if leaving:
            height = 1 + max(
                (heights[id(child)] for child in node.operands), default=0)
            if depth + height > 128:
                return False
            heights[identity] = height
            active.remove(identity)
            continue
        if identity in active:
            return False
        if identity in heights:
            if depth + heights[identity] > 128:
                return False
            continue
        if depth >= 128 or len(heights) + len(active) >= 1024:
            return False
        if (not isinstance(node.op, str) or not isinstance(node.key, str)
                or not isinstance(node.expected, str)):
            return False
        if any(0xD800 <= ord(ch) <= 0xDFFF
               for part in (node.op, node.key, node.expected) for ch in part):
            return False
        if not isinstance(node.operands, tuple):
            return False
        if node.op in ("TRUE", "FALSE"):
            if node.key or node.expected or node.operands:
                return False
        elif node.op == "EQ":
            if not node.key or node.operands:
                return False
        elif node.op == "NOT":
            if node.key or node.expected or len(node.operands) != 1:
                return False
        elif node.op in ("AND", "OR"):
            if node.key or node.expected or not node.operands:
                return False
        else:
            return False
        active.add(identity)
        pending.append((node, True, depth))
        pending.extend((child, False, depth + 1)
                       for child in reversed(node.operands))
    return True


def evaluate(predicate: Predicate, facts: Mapping[str, str]) -> str:
    """Strong Kleene semantics evaluated once per distinct DAG node.

    Unlike naive recursion, a shared child referenced k times does not create
    exponential work. The compiler validates all predicate declarations before
    this function is called; malformed direct callers yield UNKNOWN.
    """
    if not valid_predicate(predicate):
        return "UNKNOWN"
    done: dict[int, str] = {}
    pending: list[tuple[Predicate, bool]] = [(predicate, False)]
    while pending:
        node, leaving = pending.pop()
        key = id(node)
        if key in done:
            continue
        if not leaving:
            pending.append((node, True))
            pending.extend((child, False) for child in reversed(node.operands)
                           if id(child) not in done)
            continue
        if node.op == "TRUE":
            value = "TRUE"
        elif node.op == "FALSE":
            value = "FALSE"
        elif node.op == "EQ":
            value = ("UNKNOWN" if node.key not in facts
                     else "TRUE" if facts[node.key] == node.expected else "FALSE")
        elif node.op == "NOT":
            value = {"TRUE": "FALSE", "FALSE": "TRUE", "UNKNOWN": "UNKNOWN"}[
                done[id(node.operands[0])]]
        else:
            children = (done[id(child)] for child in node.operands)
            if node.op == "AND":
                outcomes = tuple(children)
                value = ("FALSE" if "FALSE" in outcomes else "UNKNOWN"
                         if "UNKNOWN" in outcomes else "TRUE")
            else:
                outcomes = tuple(children)
                value = ("TRUE" if "TRUE" in outcomes else "UNKNOWN"
                         if "UNKNOWN" in outcomes else "FALSE")
        done[key] = value
    return done[id(predicate)]


def pick(candidates: tuple[object, ...], facts: Mapping[str, str]
         ) -> tuple[object | None, str]:
    """Return a uniquely qualified choice; uncertainty is never a fallback."""
    # Frozen dataclass type hints are not enforced on runtime caller data.
    # Reject malformed priorities even when only one candidate would win.
    if any(c.priority is not None and type(c.priority) is not int  # type: ignore[attr-defined]
           for c in candidates):
        return None, "INVALID_PLAN"
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
    raw = dumps(payload, sort_keys=True, ensure_ascii=True,
                separators=(",", ":"), default=_default_json, allow_nan=False)
    return sha256(raw.encode("utf-8")).hexdigest()


def stable_task_id(parts: tuple[str, ...]) -> str:
    return "smc4:" + digest_payload(parts)[:32]


# Unlike a success plan hash, a rejection receipt must identify the
# complete attempted experiment (including invalid and unselected inputs).
_UNORDERED_FIELDS = frozenset({
    "paths", "units", "required_spans", "definitions", "bundles",
    "slots", "candidates", "members", "operands", "shares",
    "anchors", "relations", "capabilities", "target_unit_ids",
})



def _predicate_digest(root: Predicate) -> str:
    """Canonical structural fingerprint for valid DAGs AND invalid cycles.

    Acyclic graphs use exact bottom-up hashes. For cyclic caller-built graphs
    (which always fail semantic validation), fixed synchronous refinement
    hashes graph connectivity without any DFS-dependent cycle marker. AND/OR
    children are unordered; shared DAG nodes and their unfolded copies agree.
    """
    def atom(value: object) -> object:
        if value is None or isinstance(value, (str, int, bool)):
            return value
        return {"invalid_type": type(value).__name__, "repr": repr(value)}

    nodes: dict[int, Predicate] = {}
    pending = [root]
    while pending:
        node = pending.pop()
        identity = id(node)
        if identity in nodes:
            continue
        nodes[identity] = node
        if len(nodes) > 4096:
            return digest_payload({"predicate_over_budget": True})
        if isinstance(node.operands, tuple):
            pending.extend(child for child in node.operands
                           if isinstance(child, Predicate))

    def render(node: Predicate, hashes: dict[int, str]) -> str:
        operands: object
        if isinstance(node.operands, tuple):
            values = [
                hashes[id(child)] if isinstance(child, Predicate)
                else digest_payload({"malformed_operand": atom(child)})
                for child in node.operands
            ]
            if node.op in ("AND", "OR"):
                values.sort()
            operands = values
        else:
            operands = {"malformed_operands": atom(node.operands)}
        return digest_payload({
            "op": atom(node.op), "key": atom(node.key),
            "expected": atom(node.expected), "operands": operands,
        })

    dependencies: dict[int, set[int]] = {
        identity: {id(child) for child in node.operands
                   if isinstance(child, Predicate)}
        if isinstance(node.operands, tuple) else set()
        for identity, node in nodes.items()
    }
    parents: dict[int, set[int]] = {identity: set() for identity in nodes}
    for parent, children in dependencies.items():
        for child in children:
            parents[child].add(parent)
    remaining = {identity: len(children)
                 for identity, children in dependencies.items()}
    ready = [identity for identity, count in remaining.items() if count == 0]
    complete: dict[int, str] = {}
    while ready:
        identity = ready.pop()
        complete[identity] = render(nodes[identity], complete)
        for parent in parents[identity]:
            remaining[parent] -= 1
            if remaining[parent] == 0:
                ready.append(parent)
    if len(complete) == len(nodes):
        return complete[id(root)]

    # A cycle is invalid. Refine ALL reachable nodes synchronously from
    # intrinsic labels, without visit-order effects; fixed round count
    # produces equal receipts for commutative operand permutations.
    labels = {
        identity: digest_payload({
            "op": atom(node.op), "key": atom(node.key),
            "expected": atom(node.expected),
            "operands_type": type(node.operands).__name__,
        })
        for identity, node in nodes.items()
    }
    # In an invalid cyclic graph, a changed leaf can sit arbitrarily far
    # from the cycle (e.g. 70 nested NOT nodes). The number of reachable
    # distinct nodes bounds every simple source-to-root path, so refine
    # through the full graph rather than truncating at a fixed radius.
    # Also bind the reachable graph size in the final failure fingerprint.
    for _ in range(len(nodes) + 1):
        labels = {identity: render(node, labels)
                  for identity, node in nodes.items()}
    return digest_payload({"cyclic_nodes": len(nodes),
                           "refined_root": labels[id(root)]})


def canonical_request_fingerprint(request: Mapping[str, object]) -> str:
    """Deterministic safe fingerprint even for malformed Unicode/runtime data.

    Sort genuinely unordered declarations; preserve ordered pairs and
    direction-sensitive tuples. Do not use Python repr of the entire lexicon,
    since it is ordering-sensitive and not stable under source reordering.
    """
    def normalized(value: object, field_name: str = "") -> object:
        if isinstance(value, Fraction):
            return {"rational": [value.numerator, value.denominator]}
        if isinstance(value, Predicate):
            return {"predicate_digest": _predicate_digest(value)}
        if is_dataclass(value) and not isinstance(value, type):
            # asdict() recursively expands arbitrary caller data before we
            # can validate it, and crashes on deep/cyclic Predicate graphs.
            shallow = {field.name: getattr(value, field.name)
                       for field in fields(value)}
            return {"dataclass": type(value).__name__,
                    "fields": normalized(shallow)}
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
