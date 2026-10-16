"""Normative Gate A / A1 public B2 contract tests (source independent of fixtures)."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from morphoacoustics_graph.tree5 import (
    Tree5Error, decode_tree5_json, prepare_tree5, restore_tree5
)
from morphoacoustics_graph.tree5_contract import _encode, _hash, _snapshot, _normalize_blueprint

FIX = json.loads((Path(__file__).resolve().parents[1] / "docs/research/og5-contract-goldens.json").read_text())
VARIANTS = FIX["blueprint_snapshot_variants"]


@pytest.mark.parametrize("operation", ["prepare", "restore"])
@pytest.mark.parametrize("nested", [False, True])
def test_non_ascii_keys_refuse_at_containing_object(operation: str, nested: bool) -> None:
    value = copy.deepcopy(VARIANTS["baseline"]["input" if operation == "prepare" else "snapshot"])
    bp = value if operation == "prepare" else value["blueprint"]
    target = bp["organs"][0] if nested else bp
    target["未知"] = 0
    path = ("/blueprint" if operation == "restore" else "") + ("/organs/0" if nested else "")
    with pytest.raises(Tree5Error) as error:
        (prepare_tree5 if operation == "prepare" else restore_tree5)(value)
    assert error.value.receipt() == {"status": "INVALID", "code": "INVALID_STRING", "path": path}


@pytest.mark.parametrize("operation", ["prepare", "restore"])
@pytest.mark.parametrize("duplicate", ["organ", "port", "junction"])
def test_independent_reference_error_competes_with_duplicate_identity(operation: str, duplicate: str) -> None:
    value = copy.deepcopy(VARIANTS["baseline"]["input" if operation == "prepare" else "snapshot"])
    bp = value if operation == "prepare" else value["blueprint"]
    bp["junctions"][0]["ports"][0] = "missing"
    if duplicate == "organ":
        bp["organs"][1]["id"] = "A"
    elif duplicate == "port":
        bp["organs"][1]["inlet"]["id"] = "A.in"
    else:
        bp["junctions"][1]["id"] = "J1"
    prefix = "/blueprint" if operation == "restore" else ""
    with pytest.raises(Tree5Error) as error:
        (prepare_tree5 if operation == "prepare" else restore_tree5)(value)
    assert error.value.receipt() == {
        "status": "INVALID", "code": "UNKNOWN_PORT", "path": prefix + "/junctions/0/ports/0"}


@pytest.mark.parametrize("module", ["tree5", "tree5_contract"])
def test_import_order_does_not_require_preloading_public_facade(module: str) -> None:
    subprocess.run([sys.executable, "-c", f"import morphoacoustics_graph.{module}"], check=True)


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


@pytest.mark.parametrize("fixture", FIX["numeric_refusal_test_seams"], ids=lambda x: x["name"])
def test_a1_actual_solver_boundary_seams(fixture: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise the real coupled-matrix/rank/linear-solve certification path.

    This test never fakes _solve_fixture or asks for an unsupported Blueprint.
    """
    from morphoacoustics_graph import tree5
    import numpy as np

    real_system = tree5._system
    real_solve = tree5.np.linalg.solve
    name = fixture["name"]
    inject_index = fixture["inject_at_sample_index"]
    target_frequency = fixture["frequencies_hz"][inject_index]

    if name in ("rank", "condition", "nonfinite", "late_atomicity"):
        def matrix_mutant(tubes, load, scale, frequency):
            m, rhs = real_system(tubes, load, scale, frequency)
            if frequency != target_frequency:
                return m, rhs
            mutant, b = m.copy(), rhs.copy()
            if name in ("rank", "late_atomicity"):
                mutant[-1, :] = mutant[-2, :]
                b[-1] = b[-2]
            elif name == "condition":
                mutant = np.diag(np.array([1.] * 19 + [1e-5], dtype=np.complex128))
                b = np.ones(20, dtype=np.complex128)
            elif name == "nonfinite":
                mutant[0, 0] = np.nan
            return mutant, b
        monkeypatch.setattr(tree5, "_system", matrix_mutant)
    else:
        def solver_mutant(m, rhs):
            if name == "convergence":
                raise np.linalg.LinAlgError("injected expected solver failure")
            result = real_solve(m, rhs)
            result[0] += 1e-3
            return result
        monkeypatch.setattr(tree5.np.linalg, "solve", solver_mutant)

    receiver = restore_tree5(copy.deepcopy(fixture["receiver_snapshot"]))
    with pytest.raises(Tree5Error) as failure:
        receiver.response(fixture["frequencies_hz"])
    assert failure.value.receipt() == fixture["expected_error"]
    assert fixture["observation_must_be_absent"] is True
    assert fixture["digest_must_be_absent"] is True
