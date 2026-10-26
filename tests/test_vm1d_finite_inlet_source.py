"""Scientific checks for research-only VM-1D; Gate A precedes this source."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "vm1d_finite_inlet_source", ROOT / "tools/vm1d_finite_inlet_source.py"
)
assert spec is not None and spec.loader is not None
vm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vm)


def test_fixture_is_exact_and_two_lengths_do_not_alias():
    bodies, digest = vm.fixture()
    assert len(digest) == 64
    assert len(bodies["M0"][1]) == 16
    assert np.array_equal(bodies["M0"][1], bodies["M1"][1])
    assert bodies["M0"][0] == .010 and bodies["M1"][0] == .011


def test_uniform_matched_tube_has_independent_closed_form_oracle():
    result = vm.uniform_oracle()
    assert result["pass"]
    assert result["max_complex_relative_error"] <= 1e-10


def test_passive_b0_and_lossless_two_port_have_positive_power_and_identity():
    bodies, _ = vm.fixture()
    for length, areas in bodies.values():
        for f in vm.FREQUENCIES:
            m = vm.cascade(areas, length, f)
            assert abs(np.linalg.det(m) - 1) <= 1e-10
            load = vm.b0_load(float(areas[-1]), f)
            assert load.real > 0
            ideal = vm.drive(m, load, flow=vm.IDEAL_FLOW)
            assert ideal["power"]["pass"]
            for mult in vm.RESISTANCE_MULTIPLIERS:
                zc = vm.RHO * vm.SPEED / float(areas[0])
                d = vm.drive(m, load, p_drive=vm.P_DRIVE, source_r=mult * zc)
                assert d["power"]["pass"]
                assert abs(d["p_in"] + mult * zc * d["U_in"] - vm.P_DRIVE) <= 1e-9


def test_pre_registered_adversarial_controls():
    controls = vm.negative_controls()
    assert controls["pass"], controls
    assert len(controls["checks"]) >= 7
    with pytest.raises(ValueError, match="MIXED_DRIVE"):
        vm.drive(np.eye(2), 1e6 + 0j, flow=1e-6, p_drive=1.0, source_r=1e6)


def test_finite_source_is_not_mislabeled_prescribed_flow():
    result = vm.run()
    assert result["g0_g1_numerical_pass"]
    assert result["g2_biological_physics"] == "INDETERMINATE_PHYSIOLOGY"
    assert result["g3"] == "NOT_RUN_NO_SELF_OSCILLATOR"
    assert result["g4"] == "VOICE_NO_GO_UNCHANGED"
    for body in ("M0", "M1"):
        entry = result["source_loading_sensitivity"][body]
        for r in vm.RESISTANCE_MULTIPLIERS:
            item = entry["finite_pressure_source"][str(r)]
            assert abs(item["delta_vs_ideal_flow_db"]) > .1
            assert item["exceeds_preregistered_0p1_db_sensitivity"]
        for f in ("100", "600", "2500"):
            v = result["raw_cases"][body]["frequency_cases"][f]
            assert "HpU_pa_s_m3" in v["ideal_prescribed_flow"]
            assert "p_mouth_per_drive" in v["finite_source"]["1.0"]
            assert "WAV" not in str(v)


def test_report_is_strict_json_and_can_be_archived_after_test_failures():
    report = vm.run()
    encoded = json.dumps(report, allow_nan=False, sort_keys=True)
    assert '"uniform_matched_tube_oracle"' in encoded
    assert '"g4": "VOICE_NO_GO_UNCHANGED"' in encoded
