"""Documentation-only CVI Gate B1/B2 prereg integrity; NEVER runs any realizer.

The version 1.1 contract is source-pinned prior to Gate B experiments.
Checks prevent a protocol JSON edit from silently changing model tolerances,
fixture identity, guard expected stage, or a constructor into fake Core status.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "research" / "cvi1-body-motor-identity"
V1 = DOC / "gate_b1_b2_fixture_v1.json"
V11 = DOC / "gate_b1_b2_fixture_v1_1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw
    ).hexdigest()


def _canonical_sha256(payload: dict) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def test_review_revision_is_explicitly_superseding_unexecuted_v1() -> None:
    old, new = _load(V1), _load(V11)
    assert old["status"] == "SUPERSEDED_BEFORE_EXECUTION_BY_V1_1"
    assert old["superseded_by"]["file"] == V11.name
    assert new["schema"] == "cvi1-gate-b1-b2-frozen-fixture/v1.1"
    assert new["status"] == "REVIEW_CORRECTED_PREREGISTRATION_NOT_EXECUTED"
    assert new["supersedes"]["schema"] == "cvi1-gate-b1-b2-frozen-fixture/v1"
    assert new["supersedes"]["blob_sha"] == "6c2eec95b2f5d27ff2b569bb280ade6f746a1df5"
    assert (DOC / "GATE_B1_B2_PROTOCOL_V1.md").read_text().find(
        "SUPERSEDED BEFORE EXECUTION"
    ) >= 0
    assert (DOC / "GATE_B1_B2_PROTOCOL_V1_1.md").read_text().find(
        "Review-driven v1.1 correction"
    ) >= 0
    # The P2 amendment changes protocol observability, not historic thresholds.
    assert new["frozen_thresholds"] == old["frozen_thresholds"]
    assert new["r1"] == old["r1"]
    assert new["body"] == old["body"]
    assert new["source_base_commit"] == old["source_base_commit"]


def test_research_source_blobs_pinned_and_no_core_semantics_changed() -> None:
    new = _load(V11)
    assert new["source_base_commit"] == "f1020c568c54615bc9fdc4c9804128ddbcc3ff0d"
    for path, pinned_sha in new["source_blobs"].items():
        assert _git_blob_sha((ROOT / path).read_bytes()) == pinned_sha, path
    assert new["body"]["backend_id"] == "fidelity0.tract1d"


def test_prepared_body_canonical_contract_is_complete_and_stable() -> None:
    spec = _load(V11)
    guard = spec["preflight_guard"]
    body = spec["prepared_body_contract"]
    assert body["schema"] == "cvi1-prepared-body-contract/v1"
    assert body["backend_id"] == "fidelity0.tract1d"
    assert _canonical_sha256(body) == (
        "211740f581d685b78807ef0f2fcd1b67640add15731921924eee29bcb9bf532f"
    )
    assert guard["expected_body_contract_sha256"] == _canonical_sha256(body)
    assert len(body["rest_state"]["sections"]) == spec["body"]["section_count"] == 10
    assert all(s == {"length_m": 0.017, "area_m2": 0.0003}
               for s in body["rest_state"]["sections"])
    assert guard["owner"].startswith("experiment-local")
    assert [row["code"] for row in guard["order"]] == [
        "HARNESS_SECTION_MODEL_MISMATCH",
        "HARNESS_BACKEND_MISMATCH",
        "HARNESS_PREPARED_BODY_MISMATCH",
        "HARNESS_PROFILE_MISMATCH",
    ]
    assert all(row["failure_kind"] == "HARNESS_REJECTED"
               for row in guard["order"])
    assert guard["negative_controls"]["N07_16_section"] == (
        "HARNESS_SECTION_MODEL_MISMATCH"
    )
    assert guard["negative_controls"]["N06_backend"] == "HARNESS_BACKEND_MISMATCH"


def test_negative_control_phases_cannot_forge_native_core_receipts() -> None:
    spec = _load(V11)
    contract = spec["rejection_record_contract"]
    phases = set(contract["phase_enum"])
    assert {"CONSTRUCT_PARAMETER", "CONSTRUCT_PROFILE",
            "HARNESS_PREFLIGHT", "CORE_REALIZER"} <= phases
    assert len(spec["controls"]) == 14
    examples = {
        "constructor_example": ("CONSTRUCTOR_REJECTED", "CONSTRUCT_PARAMETER"),
        "harness_example": ("HARNESS_REJECTED", "HARNESS_PREFLIGHT"),
        "core_example": ("CORE_FEASIBILITY_REJECTED", "CORE_REALIZER"),
    }
    for name, (kind, phase) in examples.items():
        row = contract[name]
        assert row["outcome_kind"] == kind
        assert row["phase"] == phase
        assert set(contract["required_fields"]) == set(row)
        assert not row["did_invoke_acoustics"] and not row["did_emit_take"]
    for key in ("constructor_example", "harness_example"):
        row = contract[key]
        assert row["did_call_core"] is False
        assert row["native_feasibility"] is None
        assert row["core_result_exists"] is False
        assert row["core_state_present"] is None
    assert contract["constructor_example"]["exception"]["type"] == "ValueError"
    assert contract["harness_example"]["harness_code"] == (
        "HARNESS_SECTION_MODEL_MISMATCH"
    )
    assert contract["core_example"]["native_feasibility"] == "INVALID"
    assert contract["core_example"]["core_result_exists"] is True
    assert contract["core_example"]["core_state_present"] is False


def test_known_model_fixture_matches_pinned_historical_wolfram_reference() -> None:
    cfg = _load(V11)
    oracle = _load(
        ROOT / "experiments/019_material_conditioned_realization"
        / "wolfram/material_realization_oracle.json"
    )
    x, y, p = cfg["body"], cfg["r1"], oracle["parameters"]
    assert x["section_count"] == p["section_count"] == 10
    assert x["zero_based_target_section"] == p["target_section_index_zero_based"] == 6
    assert y["stiffness_perturbation"]["section"] == p["left_neighbor_section_index_zero_based"]
    assert x["rest_area_m2"] == p["rest_area_m2"]
    assert x["target_area_m2"] == p["gesture_target_area_m2"]
    assert y["smoothing_lambda"] == p["smoothness_lambda"]
    assert abs(x["normalized_axial_xi"] * x["total_length_m"]
               - x["axial_position_m"]) < 1e-14
    assert abs(x["target_area_m2"] / x["rest_area_m2"]
               - p["target_ratio"]) < 1e-14
    assert oracle["r1_candidate_left_neighbor_ratio"] > oracle[
        "r1_baseline_left_neighbor_ratio"
    ]
    assert cfg["gates"]["B3"] == "NOT_RUN"
    assert cfg["gates"]["C"] == "NOT_RUN"
    assert cfg["gates"]["acoustics"] == "NOT_RUN"
