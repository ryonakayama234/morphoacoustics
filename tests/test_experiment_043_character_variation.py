"""Research-only structural falsifiers for Exp043. No listening-quality claim."""
from __future__ import annotations

import os
from pathlib import Path
import runpy

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PILOT = runpy.run_path(str(
    ROOT / "experiments" / "043_character_voice_variation" / "run.py"
))


def test_body_intervention_is_one_axial_dimension() -> None:
    model = PILOT["load_model"]()
    a = PILOT["make_body"](model, "M0")
    b = PILOT["make_body"](model, "M1")
    assert len(a.sections) == len(b.sections) == 16
    assert a.total_length_m == pytest.approx(0.16)
    assert b.total_length_m == pytest.approx(0.176)
    assert np.array_equal(
        [s.area_m2 for s in a.sections],
        [s.area_m2 for s in b.sections],
    )
    with pytest.raises(ValueError):
        PILOT["make_body"](model, "fake")


def test_timing_changes_motion_not_final_body_target() -> None:
    model = PILOT["load_model"]()
    a = PILOT["make_body"](model, "M0")
    original = PILOT["timing_tasks"](model, "reference")
    delayed = PILOT["timing_tasks"](model, "late_constriction")
    assert original[1].onset_s == 0.15
    assert delayed[1].onset_s == 0.19
    assert original[1].offset_s == delayed[1].offset_s
    assert original[1].degree == delayed[1].degree
    early_a, _ = PILOT["realize"](model, a, "reference", 0.17)
    early_b, _ = PILOT["realize"](model, a, "late_constriction", 0.17)
    end_a, _ = PILOT["realize"](model, a, "reference", 0.50)
    end_b, _ = PILOT["realize"](model, a, "late_constriction", 0.50)
    assert any(x.area_m2 != y.area_m2 for x, y in zip(early_a.sections, early_b.sections))
    assert all(x.area_m2 == y.area_m2 for x, y in zip(end_a.sections, end_b.sections))
    with pytest.raises(ValueError):
        PILOT["timing_tasks"](model, "invented")


@pytest.mark.skipif(
    os.getenv("EXP043_REAL_PHYSICS") != "1",
    reason="opt-in full 4-case acoustic render; archive outputs separately",
)
def test_full_research_render(tmp_path: Path) -> None:
    result = PILOT["run"](tmp_path / "evidence")
    assert result["status"] == "NUMERICAL_PILOT_ONLY"
    assert len(result["cases"]) == 4
    assert len(list((tmp_path / "evidence").glob("*_pressure_pa.npy"))) == 4
    assert len(list((tmp_path / "evidence").glob("*.wav"))) == 4
