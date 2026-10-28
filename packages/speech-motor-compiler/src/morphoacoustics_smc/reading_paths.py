"""SMC-7 Gate B L0: finite, research-only reading *hypotheses* and replay.

This module does not do Japanese phonetic G2P, choose motor Tasks, generate
natural timing, operate physical organs, or generate audio. Inherited SMC5
semantics/SMC6 COMPATIBILITY scenarios are externally supplied and revalidated.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, cast

from .canonical_ingress import parse_canonical_request
from .symbolic_bridge import CompileResult, compile_wire
from .temporal_stn import TemporalAnalysis, TemporalScenario, analyze_temporal_wire

_VERSION = "smc7-reading-l0/v0"
_MAX_SOURCE_CHARS = 256
_MAX_SOURCE_BYTES = 2048
_MAX_PATHS = 8
_MAX_UNITS = 32
_SILENT = frozenset(" \n\t、。！？…")


@dataclass(frozen=True, slots=True)
class ReadingUnit:
    unit_id: str
    symbol: str
    start_offset: int
    end_offset: int


@dataclass(frozen=True, slots=True)
class ReadingPath:
    path_id: str
    units: tuple[ReadingUnit, ...]
    evidence_id: str


@dataclass(frozen=True, slots=True)
class ReadingProposal:
    source_text: str
    source_revision: str
    source_digest: str | None
    paths: tuple[ReadingPath, ...]
    status: str
    code: str
    proposal_digest: str | None


@dataclass(frozen=True, slots=True)
class ReadingExecution:
    status: str
    stage: str
    code: str
    smc5: CompileResult | None
    smc6: TemporalAnalysis | None


def _ascii(value: object, maximum: int = 80) -> bool:
    return (isinstance(value, str) and type(value) is str
            and 0 < len(value) <= maximum
            and value.isascii()
            and all(33 <= ord(x) <= 126 for x in value))


def _scalar(text: str) -> bool:
    return all(not (0xD800 <= ord(c) <= 0xDFFF) for c in text)


def _source_error(source: object, revision: object) -> str | None:
    if not isinstance(source, str) or type(source) is not str or not source:
        return "INVALID_SOURCE"
    # Reject on O(1) length before any O(N) Unicode or UTF-8 traversal.
    if len(source) > _MAX_SOURCE_CHARS:
        return "SOURCE_LIMIT"
    if not _scalar(source):
        return "INVALID_SOURCE"
    if len(source.encode("utf-8")) > _MAX_SOURCE_BYTES:
        return "SOURCE_LIMIT"
    if not _ascii(revision):
        return "INVALID_REVISION"
    return None


def _reject(source: object, revision: object, code: str) -> ReadingProposal:
    return ReadingProposal(
        source if isinstance(source, str) else "",
        revision if isinstance(revision, str) else "",
        None, (), "REJECTED", code, None,
    )


def _digest(value: object) -> str:
    blob = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256(b"SMC7-READING-PROPOSAL/v0\0" + blob).hexdigest()


def make_proposal(
    source_text: object, source_revision: object, paths: object,
) -> ReadingProposal:
    """Register complete caller-supplied reading *hypotheses*, not verified truth."""
    problem = _source_error(source_text, source_revision)
    if problem:
        return _reject(source_text, source_revision, problem)
    assert isinstance(source_text, str) and isinstance(source_revision, str)
    if not isinstance(paths, tuple) or type(paths) is not tuple or not paths or len(paths) > _MAX_PATHS:
        return _reject(source_text, source_revision, "PATH_LIMIT")
    if not all(type(p) is ReadingPath for p in paths):
        return _reject(source_text, source_revision, "INVALID_PATH")
    readable = {i for i, ch in enumerate(source_text) if ch not in _SILENT}
    if not readable:
        return _reject(source_text, source_revision, "NO_PRONOUNCEABLE")
    path_ids: set[str] = set()
    for p in paths:
        if not _ascii(p.path_id) or not _ascii(p.evidence_id):
            return _reject(source_text, source_revision, "INVALID_PATH")
        if p.path_id in path_ids:
            return _reject(source_text, source_revision, "DUPLICATE_PATH")
        path_ids.add(p.path_id)
        if (not isinstance(p.units, tuple) or type(p.units) is not tuple
                or not p.units or len(p.units) > _MAX_UNITS):
            return _reject(source_text, source_revision, "UNIT_LIMIT")
        unit_ids: set[str] = set()
        positions: set[int] = set()
        last_end = 0
        for unit in p.units:
            if not isinstance(unit, ReadingUnit) or type(unit) is not ReadingUnit:
                return _reject(source_text, source_revision, "INVALID_UNIT")
            if not _ascii(unit.unit_id) or unit.unit_id in unit_ids:
                return _reject(source_text, source_revision, "INVALID_UNIT_ID")
            unit_ids.add(unit.unit_id)
            if (not isinstance(unit.symbol, str) or type(unit.symbol) is not str
                    or not 1 <= len(unit.symbol) <= 32
                    or not _scalar(unit.symbol)):
                return _reject(source_text, source_revision, "INVALID_SYMBOL")
            a, b = unit.start_offset, unit.end_offset
            if (type(a) is not int or type(b) is not int
                    or a < last_end or a < 0 or b <= a or b > len(source_text)):
                return _reject(source_text, source_revision, "INVALID_SPAN")
            new = set(range(a, b))
            if any(source_text[i] in _SILENT for i in new):
                return _reject(source_text, source_revision, "SILENT_SPAN")
            positions.update(new)
            last_end = b
        if positions != readable:
            return _reject(source_text, source_revision, "INCOMPLETE_PATH")
    source_digest = sha256(source_text.encode("utf-8")).hexdigest()
    identity = [
        [p.path_id, p.evidence_id, [
            [u.unit_id, u.symbol, u.start_offset, u.end_offset] for u in p.units
        ]] for p in paths
    ]
    proposal_digest = _digest([_VERSION, source_text, source_revision, identity])
    return ReadingProposal(
        source_text, source_revision, source_digest,
        paths, "PROPOSED", "OK", proposal_digest,
    )


def propose_kana(source_text: object, source_revision: object) -> ReadingProposal:
    """Literal kana-*character* passthrough; deliberately not phoneme analysis."""
    problem = _source_error(source_text, source_revision)
    if problem:
        return _reject(source_text, source_revision, problem)
    assert isinstance(source_text, str)
    units: list[ReadingUnit] = []
    for i, char in enumerate(source_text):
        if char in _SILENT:
            continue
        x = ord(char)
        if not (0x3041 <= x <= 0x3096 or 0x30A1 <= x <= 0x30FA):
            return _reject(source_text, source_revision, "UNKNOWN_READING")
        units.append(ReadingUnit(f"U{len(units) + 1:02d}", char, i, i + 1))
    if not units:
        return _reject(source_text, source_revision, "NO_PRONOUNCEABLE")
    if len(units) > _MAX_UNITS:
        return _reject(source_text, source_revision, "UNIT_LIMIT")
    return make_proposal(
        source_text, source_revision,
        (ReadingPath("kana-1", tuple(units), "ORTHOGRAPHIC_ONLY"),),
    )


def _refuse(stage: str, code: str,
            smc5: CompileResult | None = None,
            smc6: TemporalAnalysis | None = None,
            status: str = "REFUSED") -> ReadingExecution:
    return ReadingExecution(status, stage, code, smc5, smc6)


def compile_selected(
    proposal: object, selected_path_id: object, canonical_wire: object,
    temporal_scenario: object,
) -> ReadingExecution:
    """Authenticated replay of complete SMC4/5 wire, never fabricate Task lexicon."""
    if not isinstance(proposal, ReadingProposal) or type(proposal) is not ReadingProposal:
        return _refuse("PROPOSAL", "NO_VALID_PROPOSAL")
    # Never allow caller-defined __eq__ to judge an incoming receipt's integrity.
    # Check exact built-in scalar/container types before any equality comparison.
    if (type(proposal.source_text) is not str
            or type(proposal.source_revision) is not str
            or type(proposal.source_digest) is not str
            or type(proposal.proposal_digest) is not str
            or type(proposal.status) is not str
            or type(proposal.code) is not str
            or type(proposal.paths) is not tuple):
        return _refuse("PROPOSAL", "BAD_PROPOSAL_INTEGRITY")
    # Typed/frozen dataclasses are constructible and replaceable by callers.
    # Re-run the *complete* bounded validator on all proposed paths here.
    # A SHA-256 digest is an integrity/identity receipt, NOT an authorization
    # signature or evidence of real Japanese pronunciation.
    verified = make_proposal(
        proposal.source_text, proposal.source_revision, proposal.paths,
    )
    if verified.status != "PROPOSED" or proposal != verified:
        return _refuse("PROPOSAL", "BAD_PROPOSAL_INTEGRITY")
    if not isinstance(selected_path_id, str) or type(selected_path_id) is not str or not selected_path_id:
        return _refuse("SELECTION", "SELECTION_REQUIRED")
    matching = [p for p in proposal.paths if p.path_id == selected_path_id]
    if len(matching) != 1:
        return _refuse("SELECTION", "UNKNOWN_SELECTED_PATH")
    if (not isinstance(temporal_scenario, TemporalScenario)
            or type(temporal_scenario.lane) is not str
            or temporal_scenario.lane != "COMPATIBILITY"):
        return _refuse("TEMPORAL_POLICY", "UNSUPPORTED_LANE")
    if not isinstance(canonical_wire, bytes) or type(canonical_wire) is not bytes:
        return _refuse("INGRESS", "INVALID_WIRE")
    ingress = parse_canonical_request(canonical_wire)
    if ingress.request is None:
        return _refuse("INGRESS", ingress.receipt.code)
    doc = cast(dict[str, Any], json.loads(ingress.request.canonical_bytes))
    seg = cast(dict[str, Any], doc["segment"])
    if (seg["source_text"] != proposal.source_text
            or seg["source_revision"] != proposal.source_revision
            or seg["language"] != "ja"):
        return _refuse("PROJECTION", "SOURCE_MISMATCH")
    pronunciation = cast(dict[str, Any], doc["pronunciation"])
    if pronunciation["selected_path_id"] != selected_path_id:
        return _refuse("PROJECTION", "SELECTION_MISMATCH")
    wire_path = next(
        (p for p in pronunciation["paths"] if p["path_id"] == selected_path_id),
        None,
    )
    if wire_path is None or not wire_path["complete"]:
        return _refuse("PROJECTION", "PATH_MISMATCH")
    observed = tuple(
        (u["unit_id"], u["symbol"], u["start_offset"], u["end_offset"])
        for u in wire_path["units"]
    )
    expected = tuple(
        (u.unit_id, u.symbol, u.start_offset, u.end_offset)
        for u in matching[0].units
    )
    if observed != expected:
        return _refuse("PROJECTION", "PATH_MISMATCH")
    # The only legitimate bridge is the authentic, unchanged canonical wire;
    # no generated TaskDefinition or timing plan is added by this sidecar.
    smc5 = compile_wire(canonical_wire)
    if smc5.receipt.status != "RESOLVED" or smc5.plan is None:
        return _refuse("SMC5", smc5.receipt.code, smc5=smc5)
    smc6 = analyze_temporal_wire(canonical_wire, temporal_scenario)
    if smc6.status not in ("SAT_UNIQUE", "SAT_NONUNIQUE"):
        return _refuse("SMC6", smc6.code, smc5, smc6, "TEMPORAL_REFUSED")
    return ReadingExecution("SYMBOLIC_READY", "SMC6", "OK", smc5, smc6)
