"""Scientific regression tests for experiment 040 (EL-G0)."""
import importlib.util
import math
from pathlib import Path

import pytest


SOURCE = Path(__file__).resolve().parents[1] / "experiments" / "040_listener_g0" / "run.py"
spec = importlib.util.spec_from_file_location("listener_g0_experiment", SOURCE)
assert spec and spec.loader
exp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp)


def test_frozen_preregistered_gates() -> None:
    result = exp.generate_report()
    assert result["decision"] == "PROVISIONAL_ANALYTIC_BASELINE"
    assert all(result["gates"].values())
    assert result["preregistration_id"] == "EL-G0-PREREG"


def test_pressure_units_and_analytic_distance_ratio() -> None:
    out = exp.observe(exp.SOURCES["offset"])
    l, r = out["left_probe"], out["right_probe"]
    assert r["pressure_magnitude_pa"] > l["pressure_magnitude_pa"]
    assert math.isclose(
        r["pressure_magnitude_pa"] / l["pressure_magnitude_pa"],
        l["distance_m"] / r["distance_m"],
        rel_tol=1e-13,
    )


def test_mirror_symmetry() -> None:
    plus = exp.observe(exp.SOURCES["offset"])
    minus = exp.observe(exp.SOURCES["mirror"])
    assert plus["right_minus_left_delay_s"] < 0
    assert plus["right_over_left_level_db"] > 0
    assert plus["right_minus_left_delay_s"] == pytest.approx(
        -minus["right_minus_left_delay_s"], abs=1e-14
    )
    assert plus["right_over_left_level_db"] == pytest.approx(
        -minus["right_over_left_level_db"], abs=1e-12
    )


@pytest.mark.parametrize(
    "source,receiver,options",
    [
        ((0, 0, 0), (0, 0, 0), {}),
        ((float("nan"), 0, 0), (1, 0, 0), {}),
        ((0, 0, 0), (1, 0, 0), {"frequency_hz": 0}),
        ((0, 0, 0), (1, 0, 0), {"sound_speed_m_s": -1}),
        ((0, 0, 0), (1, 0, 0), {"density_kg_m3": float("inf")}),
    ],
)
def test_invalid_inputs_are_rejected(source, receiver, options) -> None:
    with pytest.raises(ValueError, match="INVALID"):
        exp.point_pressure(source, receiver, **options)


def test_result_scope_is_not_anatomical() -> None:
    report = exp.generate_report()
    assert "NOT_anatomical" in report["receiver_type"]
    assert "No pinna" in report["claim_limit"]
