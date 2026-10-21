"""Bounded CC-B1 research-only tests; no production source or Studio changes."""
from __future__ import annotations

import os
from pathlib import Path
import runpy

import pytest

RUNNER = runpy.run_path(str(Path(__file__).resolve().parents[1] /
   "experiments/cc_b1_rest_area_pilot/run.py"), run_name="cc_b1_pilot")

def test_rejects_unsafe_ratios():
    validate = RUNNER["checked_ratio"]
    for illegal in (0.8, 1.2, -1.0, float("nan"), float("inf"), 0, 1, "1.00", None, True):
        with pytest.raises(ValueError, match="UNSUPPORTED"):
            validate(illegal)
    for allowed in (0.90, 1.00, 1.10):
        assert validate(allowed) == allowed

def test_single_section_rest_edit_is_identity_elsewhere():
    from morphoacoustics.physical import Tract1DGeometry, TubeSection
    baseline = Tract1DGeometry(
        cavity_id="oral", sections=tuple(TubeSection(length_m=0.01,area_m2=1e-4)
                                         for _ in range(16)))
    edit = RUNNER["edit_rest_geometry"](baseline,1.10)
    assert edit.sections[0].area_m2 == pytest.approx(1.1e-4)
    assert edit.sections[1:] == baseline.sections[1:]
    assert baseline.sections[0].area_m2 == pytest.approx(1e-4)
    with pytest.raises(ValueError, match="UNSUPPORTED"):
        RUNNER["edit_rest_geometry"](Tract1DGeometry(
            cavity_id="oral",sections=baseline.sections[:-1]), 1.1)

@pytest.mark.skipif(os.getenv("CC_B1_REAL_PHYSICS") != "1",
                    reason="dedicated CI invokes exact frozen physical run")
def test_fresh_experiment_has_real_three_conditions(tmp_path):
    out = tmp_path / "new-physical-output"
    receipt = RUNNER["run"](out)
    assert receipt["status"] == "EXPLORATORY_MACHINE_RESULT_NOT_ADOPTED"
    assert [x["ratio"] for x in receipt["conditions"]] == [0.9, 1.0, 1.1]
    assert receipt["conditions"][1]["relative_l2_difference_from_baseline"] == 0.0
    assert receipt["conditions"][0]["relative_l2_difference_from_baseline"] > 1e-8
    assert receipt["conditions"][2]["relative_l2_difference_from_baseline"] > 1e-8
    assert (out/"decision.json").exists()
    for ratio in (0.9,1.0,1.1):
        assert (out/f"pressure_{ratio:.2f}.npy").exists()
    with pytest.raises(FileExistsError):
        RUNNER["run"](out)
