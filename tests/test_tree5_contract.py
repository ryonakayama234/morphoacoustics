"""Normative Gate A / A1 public B2 contract tests (source independent of fixtures)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from morphoacoustics_graph.tree5 import (
    Tree5Error, decode_tree5_json, prepare_tree5, restore_tree5
)
from morphoacoustics_graph.tree5_contract import _encode, _hash, _snapshot, _normalize_blueprint

FIX = json.loads((Path(__file__).resolve().parents[1] / "docs/research/og5-contract-goldens.json").read_text())
VARIANTS = FIX["blueprint_snapshot_variants"]


@pytest.mark.parametrize("name", list(VARIANTS))
def test_prepared_and_snapshot_golden(name: str) -> None:
    v = VARIANTS[name]
    if v["prepare_status"] != "SUCCESS":
        with pytest.raises(Tree5Error) as err:
            prepare_tree5(v["input"])
        assert err.value.status == "UNSUPPORTED"
        return
    prepared = prepare_tree5(copy.deepcopy(v["input"]))
    assert prepared.to_snapshot() == v["snapshot"]
    restored = restore_tree5(copy.deepcopy(v["snapshot"]))
    assert restored.to_snapshot() == v["snapshot"]
    assert restored is not prepared
    obj = prepared.to_snapshot()
    obj["blueprint"]["organs"][0]["revision"] = "mutated!"
    assert prepared.to_snapshot() == v["snapshot"]


@pytest.mark.parametrize("case", FIX["error_contract_fixtures"], ids=lambda x: x["name"])
def test_a1_error_receipts(case: dict) -> None:
    op = case["operation"]
    with pytest.raises(Tree5Error) as err:
        if op == "prepare":
            prepare_tree5(copy.deepcopy(case["input"]))
        elif op == "restore":
            restore_tree5(copy.deepcopy(case["input"]))
        elif op == "response":
            restore_tree5(copy.deepcopy(case["input"]["receiver_snapshot"])).response(case["input"]["frequencies_hz"])
        elif op == "response_corrupted_receiver_test_seam":
            prepared = prepare_tree5(copy.deepcopy(VARIANTS["baseline"]["input"]))
            object.__setattr__(prepared, "_snapshot_json", json.dumps(case["input"]))
            prepared.response([733])
        elif op == "decode_json":
            decode_tree5_json(case["raw_json"])
        else:
            raise AssertionError(op)
    assert err.value.receipt() == case["expected_error"]
    assert str(err.value) == case["expected_message"]


def test_golden_bytes_and_domains() -> None:
    snap = VARIANTS["baseline"]["snapshot"]
    pairs = {
        "baseline_blueprint": snap["blueprint"],
        "baseline_preparation": {k: snap[k] for k in (
            "schema", "digest_version", "backend_id", "blueprint_digest")},
        "baseline_observation": {k: v for k, v in FIX["baseline_observation"].items()
                                 if k != "observation_digest"},
        "ordered_duplicate_observation": {k: v for k, v in FIX["ordered_duplicate_observation"].items()
                                          if k != "observation_digest"},
        "negative_zero": {"number": -0.},
        "positive_zero": {"number": 0.},
    }
    domains = {
        "baseline_blueprint": "blueprint", "baseline_preparation": "preparation",
        "baseline_observation": "observation", "ordered_duplicate_observation": "observation",
        "negative_zero": "blueprint", "positive_zero": "blueprint"}
    for name, value in pairs.items():
        vec = FIX["byte_vectors"][name]
        assert _encode(value).hex() == vec["canonical_hex"]
        assert _hash(domains[name], value) == vec["digest"]


def test_response_full_schema_and_frozen_physical_states() -> None:
    prepared = prepare_tree5(copy.deepcopy(VARIANTS["baseline"]["input"]))
    out = prepared.response([733., 997., 733.])
    assert out["frequencies_hz"] == [733., 997., 733.]
    assert len(out["pressure_pa"]) == 3
    assert len(out["pressure_pa"][0]) == 10
    assert len(out["volume_flow_m3_s"][0]) == 10
    assert out["pressure_pa"][0] == out["pressure_pa"][2]
    assert out["observation_digest"] == _hash(
        "observation", {k: v for k,v in out.items() if k != "observation_digest"})
    known = FIX["baseline_observation"]["pressure_pa"][0]
    for got, expected in zip(out["pressure_pa"][0], known):
        assert abs(complex(got["real"],got["imag"])-
                   complex(expected["real"],expected["imag"])) < 1e-10


def test_canonical_reorder_same_digest_and_revision_independent_physics() -> None:
    a = prepare_tree5(VARIANTS["baseline"]["input"])
    b = prepare_tree5(VARIANTS["reversed_collection_order"]["input"])
    r = prepare_tree5(VARIANTS["c_revision_r2"]["input"])
    assert a.blueprint_digest == b.blueprint_digest
    assert a.blueprint_digest != r.blueprint_digest
    assert a.response([733])["pressure_pa"] == r.response([733])["pressure_pa"]


def test_atomic_late_numeric_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    from morphoacoustics_graph import tree5
    original = tree5._solve_fixture
    def injected(area: float, load: str, scale: float, f: float):
        if f == 997:
            raise tree5.Tree5NumericalError("MATRIX_RANK_DEFICIENT")
        return original(area, load, scale, f)
    monkeypatch.setattr(tree5, "_solve_fixture", injected)
    with pytest.raises(Tree5Error) as err:
        prepare_tree5(VARIANTS["baseline"]["input"]).response([733,997])
    assert err.value.receipt() == {
        "status": "NUMERICALLY_UNRESOLVED",
        "code": "MATRIX_RANK_DEFICIENT", "path": "/frequencies_hz/1"}
