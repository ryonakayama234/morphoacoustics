"""OD-3 limited physical coordination tests; full physics runs only in pinned CI."""
from __future__ import annotations

import json
import os
from pathlib import Path
import runpy

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
OD3 = runpy.run_path(str(ROOT / "experiments/od3_body_performance/run.py"))
pytestmark = pytest.mark.skipif(
    np.__version__ != "2.4.6", reason="OD-3 physics pinned to NumPy 2.4.6",
)


@pytest.fixture(scope="module")
def physics_context():
    return OD3["_context"]()


def test_selected_body_and_schedule_refusals(physics_context):
    runner, exp, parent = physics_context
    assert len(OD3["SELECTED"]) == 3
    for c, r in OD3["SELECTED"]:
        ref = OD3["_receipt"](runner, exp, parent, c, r)
        assert ref["revision_id"]
        assert len(ref["rest_areas_hex"]) == 16
    for c, r in ((True, "1.10"), (4.0, "1.10"), (4, 1.10),
                 (8, "1.10"), (4, "nan"), (4, "1.11"), (7, "1.00")):
        with pytest.raises(OD3["OD3Error"]):
            OD3["validate_selection"](c, r)
    for bad in ("G2", "", True, None, 0):
        with pytest.raises(OD3["OD3Error"]):
            OD3["validate_schedule"](bad)


def test_G1_is_only_plus_20ms_for_task1(physics_context):
    _, exp, _ = physics_context
    canonical = tuple(exp.EXP27.TASKS)
    g0 = OD3["_tasks"](exp, "G0")
    g1 = OD3["_tasks"](exp, "G1")
    assert g0 == canonical
    assert g1[0] == g0[0] and g1[2] == g0[2]
    assert g1[1].task == g0[1].task
    assert g1[1].degree == g0[1].degree
    assert g1[1].location == g0[1].location
    assert g1[1].onset_s == pytest.approx(.170, abs=1e-14)
    assert g1[1].offset_s == pytest.approx(.370, abs=1e-14)
    for t in (.0, .2, .4, .5):
        v0 = [OD3["_activation"](exp, task, t) for task in g0]
        v1 = [OD3["_activation"](exp, task, t) for task in g1]
        assert v0[0] == v1[0] and v0[2] == v1[2]
        if t == .2:
            assert v0[1] != v1[1]
        if t in (.0, .4, .5):
            assert v0[1] == v1[1]


def test_inherited_prepared_bodies_and_area_independence(physics_context):
    runner, exp, parent = physics_context
    for c, r in OD3["SELECTED"]:
        ref = OD3["_receipt"](runner, exp, parent, c, r)
        prep = OD3["_prepared"](parent, ref)
        assert prep.rest_state.total_length_m == pytest.approx(.16)
        g0 = OD3["_probe"](exp, prep.rest_state, OD3["_tasks"](exp, "G0"))
        g1 = OD3["_probe"](exp, prep.rest_state, OD3["_tasks"](exp, "G1"))
        assert g0[0]["areas_hex"] == g1[0]["areas_hex"]
        assert g0[4]["areas_hex"] == g1[4]["areas_hex"]
        assert g0[5]["areas_hex"] == g1[5]["areas_hex"]
        assert g0[1]["areas_hex"] != g1[1]["areas_hex"]
        assert all(float.fromhex(v) > 0 for row in g1 for v in row["areas_hex"])


def test_read_json_rejects_duplicate_and_nonfinite(tmp_path):
    path = tmp_path / "f.json"
    for malformed in ('{"x":1,"x":2}', '{"x":{"y":0,"y":1}}', '{"x":NaN}'):
        path.write_text(malformed, "utf-8")
        with pytest.raises(OD3["OD3Error"]):
            OD3["read_json"](path)


@pytest.mark.skipif(os.environ.get("OD3_REAL_PHYSICS") != "1",
                    reason="full real pressure and mutation tests in pinned OD-3 workflow")
def test_actual_six_physical_cases_and_frozen_regression(tmp_path):
    output = tmp_path / "suite"
    result = OD3["perform_archive"](output)
    assert result["status"] == "GO_LIMITED_OD3_RESEARCH_EXECUTION"
    assert result["verified_bodies"] == 3 and result["verified_new_physical_cases"] == 6
    assert all(np.isfinite(x) and x > 1e-8 for x in result["timing_effect_l2"])
    assert len(result["timing_log_area_at_020"]) == 3
    assert all(x > 1e-9 for x in result["timing_log_area_at_020"])
    assert len(result["body_motor_interactions"]) == 2
    assert all(row["body_x_schedule_log_area_linf_at_020"] <= 1e-10
               for row in result["body_motor_interactions"])
    assert OD3["verify_archive"](output) == result
    decision = OD3["read_json"](output / "decision.json")
    assert len(decision["conditions"]) == 6
    assert len({c["revision_id"] for c in decision["conditions"]}) == 3
    assert {c["schedule_id"] for c in decision["conditions"]} == {"G0", "G1"}
    assert all(c["acoustic_calls"] == 102 for c in decision["conditions"])
    assert (output / "cases" / "c04_r100_G0.npy").is_file()


@pytest.mark.skipif(os.environ.get("OD3_REAL_PHYSICS") != "1",
                    reason="actual select-body pair and negative physical checks")
def test_selected_pair_restart_and_coordinated_false_pressure(tmp_path):
    output = tmp_path / "pair"
    result = OD3["perform_archive"](output, kind="pair", center=4, ratio="1.10")
    assert result["verified_new_physical_cases"] == 2
    assert result["body_motor_interactions"] == []
    assert OD3["verify_archive"](output) == result
    marker = output / "manifest.json"
    saved_marker = marker.read_bytes()
    try:
        changed = json.loads(saved_marker)
        changed["unexpected"] = "same-audio-no-change"
        marker.write_bytes(OD3["canonical"](changed))
        with pytest.raises(OD3["OD3Error"], match="manifest fields"):
            OD3["verify_archive"](output)
    finally:
        marker.write_bytes(saved_marker)
    with pytest.raises(OD3["OD3Error"], match="overwritten"):
        OD3["perform_archive"](output, kind="pair", center=4, ratio="1.10")
    marker = output / "manifest.json"
    decision = output / "decision.json"
    raw = output / "cases" / "c04_r110_G1.npy"
    original_manifest = marker.read_bytes()
    original_decision = decision.read_bytes()
    original_raw = raw.read_bytes()
    try:
        data = np.load(raw, allow_pickle=False)
        with raw.open("wb") as handle:
            np.save(handle, -data, allow_pickle=False)
        manifest = json.loads(original_manifest)
        manifest["artifact_sha256"][raw.name] = OD3["sha"](raw.read_bytes())
        marker.write_bytes(OD3["canonical"](manifest))
        # Even when all simple hashes agree with the changed bytes, full
        # replay from the exact Core body + task schedule refuses the forged Pa.
        with pytest.raises(OD3["OD3Error"], match="model-authoritative raw SHA"):
            OD3["verify_archive"](output)
    finally:
        raw.write_bytes(original_raw)
        marker.write_bytes(original_manifest)
    # Reviewer P2: one-ULP pressure change is inside numerical replay tolerance,
    # but MUST fail immutable SHA receipt integrity even with a rewritten
    # artifact inventory hash.
    try:
        data = np.load(raw, allow_pickle=False)
        data[1024] = np.nextafter(data[1024], np.inf)
        with raw.open("wb") as handle:
            np.save(handle, data, allow_pickle=False)
        forged = json.loads(original_manifest)
        forged["artifact_sha256"][raw.name] = OD3["sha"](raw.read_bytes())
        marker.write_bytes(OD3["canonical"](forged))
        with pytest.raises(OD3["OD3Error"], match="model-authoritative raw SHA"):
            OD3["verify_archive"](output)
    finally:
        raw.write_bytes(original_raw)
        marker.write_bytes(original_manifest)
    try:
        body = json.loads(original_decision)
        body["conditions"][0]["revision_id"] = "od2-" + "0" * 64
        decision.write_bytes(OD3["canonical"](body))
        manifest = json.loads(original_manifest)
        manifest["decision_sha256"] = OD3["sha"](decision.read_bytes())
        marker.write_bytes(OD3["canonical"](manifest))
        with pytest.raises(OD3["OD3Error"], match="fresh physics"):
            OD3["verify_archive"](output)
    finally:
        decision.write_bytes(original_decision)
        marker.write_bytes(original_manifest)
    assert OD3["verify_archive"](output) == result
