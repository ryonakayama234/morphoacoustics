"""Gate B-R finite canonical wire input boundary (synthetic research only).

No text-to-pronunciation model, TaskLexicon execution, organ dynamics or audio.
Never recursively inspect a caller's arbitrary nonbytes Python object.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from math import gcd
from typing import Any, NoReturn

SCHEMA_VERSION = "smc4-compile-request/v1"
BOUNDARY_VERSION = "smc4-canonical-boundary/v1"
MAX_BYTES = 262_144
MAX_DEPTH = 32
MAX_NODES = 4096
MAX_INT = (1 << 63) - 1
_UNORDERED = frozenset({
    "paths", "definitions", "bundles", "slots", "candidates",
    "shares", "anchors", "relations", "capabilities", "target_unit_ids",
    "members",
})
_ROOT = {"schema_version", "segment", "pronunciation", "motor_mapping", "coordination"}


class _Invalid(ValueError):
    """Reject before an executable request object exists."""


@dataclass(frozen=True, slots=True)
class IngressReceipt:
    request_schema_version: str | None
    boundary_version: str
    ingress_status: str
    code: str
    canonical_diagnostics: tuple[str, ...]
    submission_sha256: str | None
    canonical_request_sha256: str | None
    hash_status: str
    digest: str


@dataclass(frozen=True, slots=True)
class CanonicalCompileRequest:
    """Immutable, complete, validated canonical bytes; no mutable dictionaries."""

    schema_version: str
    canonical_bytes: bytes
    canonical_sha256: str


@dataclass(frozen=True, slots=True)
class BoundaryResult:
    request: CanonicalCompileRequest | None
    receipt: IngressReceipt


def _receipt(
    raw_digest: str | None, semantic_digest: str | None,
    hash_status: str, code: str, schema: str | None = None,
) -> IngressReceipt:
    status = "ACCEPTED" if code == "OK" else "REJECTED"
    diagnostics = () if code == "OK" else (code,)
    canonical = json.dumps({
        "boundary": BOUNDARY_VERSION, "status": status, "code": code,
        "schema": schema, "raw": raw_digest, "semantic": semantic_digest,
        "hash_status": hash_status, "diagnostics": diagnostics,
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt_digest = sha256(b"SMC4-BR-RECEIPT/v1\x00" + canonical).hexdigest()
    return IngressReceipt(
        schema, BOUNDARY_VERSION, status, code, diagnostics,
        raw_digest, semantic_digest, hash_status, receipt_digest,
    )


def _precheck_depth(text: str) -> None:
    depth = 0
    in_string = False
    escaped = False
    for ch in text:
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise _Invalid("NESTING_LIMIT")
        elif ch in "]}":
            depth -= 1
            if depth < 0:
                raise _Invalid("INVALID_JSON")


def _duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise _Invalid("DUPLICATE_KEY")
        out[key] = value
    return out


def _integer_token(text: str) -> int:
    if len(text.lstrip("-")) > 19:
        raise _Invalid("INTEGER_LIMIT")
    number = int(text)
    if abs(number) > MAX_INT:
        raise _Invalid("INTEGER_LIMIT")
    return number


def _invalid_float(_s: str) -> NoReturn:
    raise _Invalid("FLOAT_FORBIDDEN")


def _valid_unicode(value: str) -> bool:
    return not any(0xD800 <= ord(c) <= 0xDFFF for c in value)


def _str(value: Any, *, empty: bool = False, limit: int = 256) -> str:
    if (type(value) is not str or len(value) > limit
            or (not empty and not value) or not _valid_unicode(value)):
        raise _Invalid("INVALID_STRING")
    return value


def _int(value: Any, *, low: int = -MAX_INT, high: int = MAX_INT) -> int:
    if type(value) is not int or value < low or value > high:
        raise _Invalid("INVALID_INTEGER")
    return value


def _obj(value: Any, keys: set[str]) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise _Invalid("SCHEMA_FIELDS")
    return value


def _list(value: Any, limit: int) -> list[Any]:
    if type(value) is not list or len(value) > limit:
        raise _Invalid("INVALID_ARRAY")
    return value


def _unique(values: list[Any]) -> None:
    if len(values) != len(set(values)):
        raise _Invalid("DUPLICATE_ID")


def _frac(value: Any) -> None:
    d = _obj(value, {"numerator", "denominator"})
    n = _int(d["numerator"])
    q = _int(d["denominator"], low=1)
    if gcd(n, q) != 1:
        raise _Invalid("UNREDUCED_RATIONAL")


def _predicate(obj: Any) -> None:
    p = _obj(obj, {"op", "key", "expected", "operands"})
    op = _str(p["op"])
    key = _str(p["key"], empty=True)
    expected = _str(p["expected"], empty=True)
    operands = _list(p["operands"], 128)
    if op not in {"TRUE", "FALSE", "EQ", "NOT", "AND", "OR"}:
        raise _Invalid("INVALID_PREDICATE")
    if op in {"TRUE", "FALSE"} and (key or expected or operands):
        raise _Invalid("INVALID_PREDICATE")
    if op == "EQ" and (not key or operands):
        raise _Invalid("INVALID_PREDICATE")
    if op == "NOT" and (key or expected or len(operands) != 1):
        raise _Invalid("INVALID_PREDICATE")
    if op in {"AND", "OR"} and (key or expected or not operands):
        raise _Invalid("INVALID_PREDICATE")
    for child in operands:
        _predicate(child)


def _check_nodes(doc: Any) -> None:
    nodes = 0
    stack = [doc]
    while stack:
        val = stack.pop()
        nodes += 1
        if nodes > MAX_NODES:
            raise _Invalid("NODE_LIMIT")
        if type(val) is dict:
            for k, v in val.items():
                _str(k, empty=True)
                stack.append(v)
        elif type(val) is list:
            stack.extend(val)
        elif type(val) is str:
            _str(val, empty=True, limit=16384)
        elif type(val) is int:
            _int(val)
        elif val is None or type(val) is bool:
            continue
        else:
            raise _Invalid("INVALID_JSON_TYPE")


def _validate(doc: Any) -> None:
    d = _obj(doc, _ROOT)
    if d["schema_version"] != SCHEMA_VERSION:
        raise _Invalid("UNKNOWN_VERSION")
    s = _obj(d["segment"], {"segment_id", "source_text", "source_revision", "language"})
    for k in ("segment_id", "source_revision", "language"):
        _str(s[k])
    source = _str(s["source_text"], limit=16384)
    reading = _obj(d["pronunciation"], {"paths", "selected_path_id"})
    selected = _str(reading["selected_path_id"])
    path_ids: list[str] = []
    selected_complete = False
    for path in _list(reading["paths"], 256):
        p = _obj(path, {"path_id", "units", "required_spans", "complete"})
        pid = _str(p["path_id"])
        path_ids.append(pid)
        if type(p["complete"]) is not bool:
            raise _Invalid("INVALID_COMPLETE_FLAG")
        spans = _list(p["required_spans"], 256)
        if not spans:
            raise _Invalid("MISSING_COVERAGE")
        for span in spans:
            if type(span) is not list or len(span) != 2:
                raise _Invalid("INVALID_SPAN")
            start = _int(span[0], low=0)
            end = _int(span[1], low=1)
            if start >= end or end > len(source):
                raise _Invalid("INVALID_SPAN")
        ids: list[str] = []
        covered: set[int] = set()
        for unit in _list(p["units"], 256):
            u = _obj(unit, {"unit_id", "symbol", "start_offset", "end_offset"})
            ids.append(_str(u["unit_id"]))
            _str(u["symbol"])
            start = _int(u["start_offset"], low=0)
            end = _int(u["end_offset"], low=1)
            if start >= end or end > len(source):
                raise _Invalid("INVALID_SPAN")
            if pid == selected and any(i in covered for i in range(start, end)):
                raise _Invalid("OVERLAPPING_UNITS")
            covered.update(range(start, end))
        _unique(ids)
        if pid == selected:
            if not p["complete"] or not ids:
                raise _Invalid("INCOMPLETE_SELECTED_PATH")
            if any(i not in covered for start, end in spans for i in range(start, end)):
                raise _Invalid("COVERAGE_GAP")
            selected_complete = True
    _unique(path_ids)
    if not selected_complete:
        raise _Invalid("SELECTED_PATH_NOT_COMPLETE")

    mapping = _obj(d["motor_mapping"], {"profile", "context", "lexicon"})
    _str(mapping["profile"])
    if type(mapping["context"]) is not dict:
        raise _Invalid("INVALID_CONTEXT")
    for k, v in mapping["context"].items():
        _str(k)
        _str(v)
    lex = _obj(mapping["lexicon"], {"revision", "rule_revision", "definitions", "bundles"})
    _str(lex["revision"])
    _str(lex["rule_revision"])
    definitions: list[tuple[str, str]] = []
    for definition in _list(lex["definitions"], 256):
        x = _obj(definition, {
            "definition_id", "semantic_revision", "variable", "value_domain",
            "goal_kind", "applicability_domain", "capabilities", "algebra",
        })
        for k in ("definition_id", "semantic_revision", "variable",
                  "value_domain", "goal_kind", "applicability_domain", "algebra"):
            _str(x[k])
        definitions.append((x["definition_id"], x["semantic_revision"]))
        caps = [_str(c) for c in _list(x["capabilities"], 256)]
        _unique(caps)
    _unique(definitions)

    bundles: list[str] = []
    total_slots = 0
    for bundle in _list(lex["bundles"], 512):
        x = _obj(bundle, {
            "bundle_id", "unit_id", "symbol", "slots", "context", "priority",
            "profile", "target_scope_kind", "target_unit_ids",
        })
        for k in ("bundle_id", "unit_id", "symbol", "profile", "target_scope_kind"):
            _str(x[k])
        bundles.append(x["bundle_id"])
        if x["priority"] is not None:
            _int(x["priority"])
        _predicate(x["context"])
        targets = [_str(u) for u in _list(x["target_unit_ids"], 256)]
        _unique(targets)
        slots: list[str] = []
        for slot in _list(x["slots"], 1024):
            y = _obj(slot, {"slot_id", "candidates"})
            slots.append(_str(y["slot_id"]))
            total_slots += 1
            if total_slots > 1024:
                raise _Invalid("SLOT_LIMIT")
            templates: list[str] = []
            for candidate in _list(y["candidates"], 1024):
                z = _obj(candidate, {
                    "template_id", "definition_id", "semantic_revision", "lower",
                    "upper", "context", "priority", "evidence_id", "status",
                })
                for k in ("template_id", "definition_id", "semantic_revision",
                          "evidence_id", "status"):
                    _str(z[k])
                templates.append(z["template_id"])
                _frac(z["lower"])
                _frac(z["upper"])
                low = Fraction(z["lower"]["numerator"], z["lower"]["denominator"])
                up = Fraction(z["upper"]["numerator"], z["upper"]["denominator"])
                if low > up:
                    raise _Invalid("INVALID_GOAL_INTERVAL")
                _predicate(z["context"])
                if z["priority"] is not None:
                    _int(z["priority"])
                total_slots += 1
                if total_slots > 1024:
                    raise _Invalid("SLOT_LIMIT")
            _unique(templates)
        _unique(slots)
    _unique(bundles)

    coord = _obj(d["coordination"], {
        "coordination_kind", "shares", "anchors", "relations",
    })
    _str(coord["coordination_kind"])
    share_ids: list[str] = []
    for share in _list(coord["shares"], 1024):
        x = _obj(share, {"episode_id", "members"})
        share_ids.append(_str(x["episode_id"]))
        members = []
        for member in _list(x["members"], 256):
            if type(member) is not list or len(member) != 2:
                raise _Invalid("INVALID_SHARE")
            members.append((_str(member[0]), _str(member[1])))
        if len(members) < 2:
            raise _Invalid("INVALID_SHARE")
        _unique(members)
    _unique(share_ids)
    anchors = _list(coord["anchors"], 1024)
    relations = _list(coord["relations"], 1024)
    if len(anchors) + len(relations) > 1024:
        raise _Invalid("TIMING_LIMIT")
    for anchor in anchors:
        x = _obj(anchor, {"unit_id", "slot_id", "event", "time_s"})
        _str(x["unit_id"])
        _str(x["slot_id"])
        if x["event"] not in ("ONSET", "OFFSET"):
            raise _Invalid("INVALID_EVENT")
        _frac(x["time_s"])
    for relation in relations:
        x = _obj(relation, {
            "from_unit", "from_slot", "from_event", "to_unit", "to_slot",
            "to_event", "lag_s",
        })
        for k in ("from_unit", "from_slot", "to_unit", "to_slot"):
            _str(x[k])
        for k in ("from_event", "to_event"):
            if x[k] not in ("ONSET", "OFFSET"):
                raise _Invalid("INVALID_EVENT")
        _frac(x["lag_s"])


def _collection_key(field: str, val: Any) -> tuple[str | int, ...]:
    """Normative schema keys, never incidental serialized-field order."""
    if field == "paths":
        return (val["path_id"],)
    if field == "definitions":
        return (val["definition_id"], val["semantic_revision"])
    if field == "bundles":
        return (val["bundle_id"],)
    if field == "slots":
        return (val["slot_id"],)
    if field == "candidates":
        return (val["template_id"],)
    if field == "shares":
        return (val["episode_id"],)
    if field == "anchors":
        return (val["unit_id"], val["slot_id"], val["event"],
                val["time_s"]["numerator"], val["time_s"]["denominator"])
    if field == "relations":
        return (val["from_unit"], val["from_slot"], val["from_event"],
                val["to_unit"], val["to_slot"], val["to_event"],
                val["lag_s"]["numerator"], val["lag_s"]["denominator"])
    if field == "members":
        return (val[0], val[1])
    if field in ("capabilities", "target_unit_ids"):
        return (val,)
    raise AssertionError("unregistered canonical ordering field")


def _canonical(value: Any, field_name: str = "") -> Any:
    if type(value) is dict:
        return {k: _canonical(v, k) for k, v in value.items()}
    if type(value) is list:
        items = [_canonical(v) for v in value]
        if field_name in _UNORDERED:
            items.sort(key=lambda item: _collection_key(field_name, item))
        return items
    return value


def parse_canonical_request(payload: object) -> BoundaryResult:
    """Admit bytes only; produce no mutable IR and no partially executable plan."""
    if type(payload) is not bytes:
        return BoundaryResult(None, _receipt(
            None, None, "NON_WIRE", "NON_WIRE_INPUT"))
    if len(payload) > MAX_BYTES:
        return BoundaryResult(None, _receipt(
            None, None, "NOT_COMPUTED_OVER_LIMIT", "INPUT_TOO_LARGE"))
    raw = sha256(payload).hexdigest()
    try:
        text = payload.decode("utf-8", errors="strict")
        _precheck_depth(text)
        doc = json.loads(
            text, object_pairs_hook=_duplicates, parse_int=_integer_token,
            parse_float=_invalid_float, parse_constant=_invalid_float,
        )
        _check_nodes(doc)
        _validate(doc)
        semantic_json = json.dumps(
            _canonical(doc), ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
        semantic_hash = sha256(
            b"SMC4-BR-CANONICAL/v1\x00" + semantic_json).hexdigest()
        receipt = _receipt(raw, semantic_hash, "COMPUTED", "OK", SCHEMA_VERSION)
        return BoundaryResult(
            CanonicalCompileRequest(SCHEMA_VERSION, semantic_json, semantic_hash),
            receipt,
        )
    except (UnicodeError, _Invalid, ValueError, TypeError, RecursionError):
        return BoundaryResult(None, _receipt(
            raw, None, "COMPUTED", "INVALID_INPUT"))
