"""Frozen before implementation: BR01-BR14 CanonicalRequestBoundary preregressions.

This suite intentionally imports an as-yet-nonexistent module at test-only SHA.
It tests ingress only; there is NO pronunciation-to-Task bridge or audio claim.
"""
import hashlib
import json
from dataclasses import FrozenInstanceError
from dataclasses import replace

import pytest

from morphoacoustics_smc.canonical_ingress import parse_canonical_request


def fixture():
    true = {"op": "TRUE", "key": "", "expected": "", "operands": []}
    return {
        "schema_version": "smc4-compile-request/v1",
        "segment": {"segment_id": "s", "source_text": "甲乙", "source_revision": "r1", "language": "ja"},
        "pronunciation": {"selected_path_id": "p1", "paths": [
            {"path_id": "p1", "complete": True, "required_spans": [[0, 2]],
             "units": [{"unit_id": "P1", "symbol": "a", "start_offset": 0, "end_offset": 1},
                       {"unit_id": "P2", "symbol": "i", "start_offset": 1, "end_offset": 2}]},
            {"path_id": "p2", "complete": True, "required_spans": [[0, 2]],
             "units": [{"unit_id": "Q1", "symbol": "ai", "start_offset": 0, "end_offset": 2}]},
        ]},
        "motor_mapping": {"profile": "synthetic", "context": {"style": "neutral"},
                          "lexicon": {"revision": "lex1", "rule_revision": "rules1",
                                      "definitions": [
                                          {"definition_id": "tract", "semantic_revision": "1",
                                           "variable": "tract", "value_domain": "open_closed",
                                           "goal_kind": "FUNCTIONAL_TRACT",
                                           "applicability_domain": "synthetic", "algebra": "SCALAR_INTERVAL",
                                           "capabilities": ["flow", "contact"]},
                                          {"definition_id": "source", "semantic_revision": "1",
                                           "variable": "source", "value_domain": "active_inactive",
                                           "goal_kind": "SOURCE", "applicability_domain": "synthetic",
                                           "algebra": "SCALAR_INTERVAL", "capabilities": []},
                                      ], "bundles": [
                                          {"bundle_id": "BA", "unit_id": "P1", "symbol": "a",
                                           "profile": "synthetic", "priority": None, "target_scope_kind": "EXACT_ONE_SELECTED_UNIT",
                                           "target_unit_ids": ["P1"], "context": true,
                                           "slots": [{"slot_id": "tract", "candidates": [
                                               {"template_id": "AT", "definition_id": "tract",
                                                "semantic_revision": "1",
                                                "lower": {"numerator": 1, "denominator": 2},
                                                "upper": {"numerator": 1, "denominator": 1},
                                                "context": true, "priority": None,
                                                "evidence_id": "fixture", "status": "SYNTHETIC_ONLY"}]}]},
                                          {"bundle_id": "BI", "unit_id": "P2", "symbol": "i",
                                           "profile": "synthetic", "priority": None,
                                           "target_scope_kind": "EXACT_ONE_SELECTED_UNIT",
                                           "target_unit_ids": ["P2"], "context": true, "slots": []},
                                      ]}},
        "coordination": {"coordination_kind": "EXACT_EVENTS", "shares": [],
                         "anchors": [{"unit_id": "P1", "slot_id": "tract", "event": "ONSET",
                                      "time_s": {"numerator": 0, "denominator": 1}}],
                         "relations": []},
    }


def encoded(d, **kwargs):
    return json.dumps(d, ensure_ascii=False, separators=(",", ":"), **kwargs).encode("utf-8")


def test_br01_br02_raw_vs_canonical_ordering():
    d = fixture()
    first = parse_canonical_request(encoded(d))
    d["pronunciation"]["paths"].reverse()
    d["motor_mapping"]["lexicon"]["definitions"].reverse()
    d["motor_mapping"]["lexicon"]["bundles"].reverse()
    d["motor_mapping"]["lexicon"]["definitions"][0]["capabilities"].reverse()
    second = parse_canonical_request(encoded(d, sort_keys=True))
    assert first.request is not None and second.request is not None
    assert first.receipt.submission_sha256 != second.receipt.submission_sha256
    assert first.receipt.canonical_request_sha256 == second.receipt.canonical_request_sha256
    assert first.request.canonical_bytes == second.request.canonical_bytes


def test_br03_pronunciation_order_is_significant():
    d = fixture()
    a = parse_canonical_request(encoded(d))
    d["pronunciation"]["paths"][0]["units"].reverse()
    b = parse_canonical_request(encoded(d))
    assert a.request is not None
    assert b.request is None or a.receipt.canonical_request_sha256 != b.receipt.canonical_request_sha256


@pytest.mark.parametrize("wire", [
    b'{"schema_version":"x","schema_version":"y"}',
    b'{"schema_version":"bad"}', b'{"x":0}',
    b'{"x":NaN}', b'{"x":1.2}', b'{"x":1e9}',
    b'\xff', b'{"x":"\\ud800"}',
])
def test_br04_05_reject_invalid_wire(wire):
    result = parse_canonical_request(wire)
    assert result.request is None
    assert result.receipt.submission_sha256 == hashlib.sha256(wire).hexdigest()
    assert result.receipt.canonical_request_sha256 is None


@pytest.mark.parametrize("bad", [
    {"numerator": 2, "denominator": 4},
    {"numerator": 1, "denominator": 0},
    {"numerator": True, "denominator": 2},
    {"numerator": 2**65, "denominator": 1},
    {"numerator": 0.5, "denominator": 1},
])
def test_br06_rationals_must_be_typed_and_reduced(bad):
    d = fixture()
    d["coordination"]["anchors"][0]["time_s"] = bad
    assert parse_canonical_request(encoded(d)).request is None


def test_br07_payload_and_depth_bounds():
    assert parse_canonical_request(b"x" * 262145).receipt.hash_status == "NOT_COMPUTED_OVER_LIMIT"
    assert parse_canonical_request(b"x" * 262145).receipt.submission_sha256 is None
    deep = b"[" * 40 + b"0" + b"]" * 40
    bad = parse_canonical_request(deep)
    assert bad.request is None and bad.receipt.canonical_request_sha256 is None


def test_br08_nonbytes_cyclic_python_rejected_without_inspection():
    x = []
    x.append(x)
    for value in (x, {"context": x}, object()):
        r = parse_canonical_request(value)
        assert r.request is None and r.receipt.code == "NON_WIRE_INPUT"
        assert r.receipt.submission_sha256 is None


def test_br09_selected_path_changes_identity():
    d = fixture()
    a = parse_canonical_request(encoded(d))
    d["pronunciation"]["selected_path_id"] = "p2"
    b = parse_canonical_request(encoded(d))
    assert a.request is not None and b.request is not None
    assert a.receipt.canonical_request_sha256 != b.receipt.canonical_request_sha256


def test_br10_mapping_is_not_silently_inferred_by_ingress():
    d = fixture()
    d["motor_mapping"]["lexicon"]["bundles"] = []
    r = parse_canonical_request(encoded(d))
    assert r.request is not None and r.receipt.ingress_status == "ACCEPTED"
    assert not hasattr(r, "plan")


def test_br13_br14_canonical_hash_stable_and_immutable_snapshot():
    d = fixture()
    a = parse_canonical_request(encoded(d))
    b = parse_canonical_request(encoded(d))
    assert a.request is not None and b.request is not None
    assert a.receipt.digest == b.receipt.digest
    assert a.receipt.canonical_request_sha256 != a.receipt.submission_sha256
    assert a.request.canonical_bytes.startswith(b"{")
    with pytest.raises(FrozenInstanceError):
        a.request.canonical_bytes = b"changed"


def test_br_f09_duplicate_declaration_rejected():
    d = fixture()
    d["motor_mapping"]["lexicon"]["definitions"].append(d["motor_mapping"]["lexicon"]["definitions"][0])
    r = parse_canonical_request(encoded(d))
    assert r.request is None and r.receipt.canonical_request_sha256 is None
