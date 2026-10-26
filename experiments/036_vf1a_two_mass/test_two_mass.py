"""Adversarial VF-1A science tests; run by dedicated experiment workflow only."""
from __future__ import annotations

from dataclasses import replace
import json
import math
import pathlib
import sys

import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from two_mass import (Tissue, CoupledTwoMass, UnsupportedContact, NumericallyUnresolved,
                      make_pilot)


def test_positive_and_nonnegative_si_contract_refuses_bad_data():
    with pytest.raises(ValueError):
        Tissue(masses_kg=(-0.1, 0.00012))
    with pytest.raises(ValueError):
        Tissue(damping_n_s_m=(-0.008, 0.008))
    with pytest.raises(ValueError):
        Tissue(rest_aperture_m2=float("nan"))
    with pytest.raises(ValueError):
        Tissue(aperture_floor_m2=3e-5)
    with pytest.raises(ValueError):
        Tissue(pressure_areas_m2=(-1, 3e-5))
    with pytest.raises(ValueError):
        make_pilot(pressure_shape="unspecified")
    with pytest.raises(ValueError):
        make_pilot(stiffness_scale=0)
    with pytest.raises(ValueError):
        make_pilot(sample_rate_hz=0)


def test_two_mass_unforced_antisymmetric_analytic_midpoint_frequency():
    # Independent free two-mass mode: g=d=0, x1=-x2, q=p=0.
    tissue = Tissue(damping_n_s_m=(0.,0.),pressure_areas_m2=(0.,0.))
    sim = make_pilot(tissue=tissue)
    w = math.sqrt((30 + 2*8) / 1.2e-4)
    theta = 2 * math.atan(0.5 * w * sim.dt)
    for i in range(1,201):
        out = sim.step(subglottal_pressure_pa=0.)
        expected = 2e-5 * math.cos(i * theta)
        assert abs(out.x_m[0] - expected) < 2e-14
        assert abs(out.x_m[0]+out.x_m[1]) < 2e-14
        assert out.flow_valve_m3_s == pytest.approx(0,abs=2e-16)
        assert out.stored_tract_j == pytest.approx(0,abs=1e-20)


def test_free_tissue_steady_zero_drive_has_no_energy_growth():
    s = make_pilot()
    previous = sum(s.energy())
    for _ in range(150):
        r = s.step(subglottal_pressure_pa=0)
        now = sum(s.energy())
        assert now <= previous + 1e-12
        assert r.outlet_loss_j >= 0
        assert r.tissue_damping_loss_j >= 0
        previous = now


def test_tissue_fluid_acoustic_local_and_total_power_in_same_tick():
    s = make_pilot()
    for _ in range(200):
        r = s.step(subglottal_pressure_pa=800.)
        assert r.area_m2 > s.tissue.aperture_floor_m2
        assert all(math.isfinite(v) for v in
                   (r.flow_valve_m3_s,r.pressure_mid_pa,r.stored_tissue_j,
                    r.stored_flow_j,r.stored_tract_j))
        assert abs(r.port_flow_residual_m3_s) < 1e-12
        assert abs(r.valve_equation_residual_pa) < 1e-4
        assert abs(r.total_energy_residual_j) < 1e-9
        assert min(r.linear_flow_loss_j,r.nonlinear_flow_loss_j,
                   r.tissue_damping_loss_j,r.outlet_loss_j) >= 0


def test_output_load_changes_upstream_tissue_and_valve_flow_not_only_mouth():
    a,b = make_pilot(),make_pilot(pressure_shape="constricted")
    tissue_delta=[]
    valve_delta=[]
    for _ in range(700):
        ra=a.step(subglottal_pressure_pa=800.)
        rb=b.step(subglottal_pressure_pa=800.)
        tissue_delta.append(ra.x_m[0]-rb.x_m[0])
        valve_delta.append(ra.flow_valve_m3_s-rb.flow_valve_m3_s)
    assert np.max(np.abs(tissue_delta)) > 1e-12
    assert np.max(np.abs(valve_delta)) > 1e-12


def test_declared_stiffness_change_physically_changes_tissue_response():
    a,b=make_pilot(),make_pilot(stiffness_scale=1.1)
    for _ in range(500):
        ra=a.step(subglottal_pressure_pa=800.)
        rb=b.step(subglottal_pressure_pa=800.)
    assert abs(ra.x_m[0]-rb.x_m[0]) > 1e-9


def test_time_step_refinement_for_fixed_physical_duration():
    def final(dt_rate: int) -> float:
        s=make_pilot(sample_rate_hz=dt_rate)
        for _ in range(int(0.012*dt_rate)):
            out=s.step(subglottal_pressure_pa=800)
        return out.x_m[0]
    x24,x48,x96=(final(n) for n in (24000,48000,96000))
    assert math.isfinite(x24+x48+x96)
    assert abs(x96-x48) < abs(x48-x24)


def test_refuses_unsupported_tissue_contact_not_silently_clamped():
    sim=make_pilot()
    with pytest.raises(UnsupportedContact):
        sim._area(np.array((-0.004,-0.004)))


def test_tampered_duct_energy_receipt_is_detected_independently(monkeypatch):
    sim=make_pilot()
    raw=sim.tract.step
    def forged(u: float):
        obs=raw(u)
        return replace(obs,energy_residual_j=obs.energy_residual_j+1e-5)
    monkeypatch.setattr(sim.tract,"step",forged)
    with pytest.raises(NumericallyUnresolved,match="LOCAL_ENERGY_BALANCE_FAILED"):
        sim.step(subglottal_pressure_pa=800.)


def test_bad_pressure_input_rejected():
    sim=make_pilot()
    for bad in (float("nan"), float("inf"), float("-inf"), True):
        with pytest.raises(ValueError):
            sim.step(subglottal_pressure_pa=bad)


def test_independently_executed_wolfram_oracle_is_preserved_and_used():
    path = pathlib.Path(__file__).parent / "wolfram/oracle.json"
    ref = json.loads(path.read_text(encoding="utf-8"))
    assert ref["midpoint_full_power_identity_residual"] == 0
    assert math.sqrt(30/1.2e-4)/(2*math.pi) == pytest.approx(
        ref["symmetric_free_mode_hz"],abs=1e-12)
    w=math.sqrt((30+2*8)/1.2e-4)
    assert w/(2*math.pi) == pytest.approx(ref["antisymmetric_free_mode_hz"],abs=1e-12)
    assert 2*math.atan(w/(2*48000)) == pytest.approx(
        ref["midpoint_antisymmetric_48k_rad_per_step"],abs=1e-12)


def test_scientific_gate_blocks_false_pass_from_failed_or_missing_pytest(tmp_path):
    # Exact Codex P2 regression: scientifically valid traces must NOT trump
    # a failed independent suite, even when the runner continues for diagnostics.
    import importlib.util
    spec=importlib.util.spec_from_file_location(
        "vf1a_runner_gate",pathlib.Path(__file__).parent/"run.py")
    assert spec is not None and spec.loader is not None
    runner=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    absent=runner.independent_test_receipt(tmp_path/"missing.json")
    assert not absent["eligible"]
    assert not runner.scientific_gate_eligible(True,absent)
    path=tmp_path/"status.json"
    for record in (
        {"schema":"vf1a.science-pytest.v1","passed":False,"exit_code":1},
        {"schema":"vf1a.science-pytest.v1","passed":True,"exit_code":1},
        {"schema":"vf1a.science-pytest.v1","passed":1,"exit_code":0},
        {"schema":"vf1a.science-pytest.v1","passed":True,"exit_code":False},
        {"schema":"forged.other","passed":True,"exit_code":0},
    ):
        path.write_text(json.dumps(record),encoding="utf-8")
        result=runner.independent_test_receipt(path)
        assert not result["eligible"]
        assert not runner.scientific_gate_eligible(True,result)
    path.write_text("{malformed",encoding="utf-8")
    assert not runner.independent_test_receipt(path)["eligible"]
    path.write_text(json.dumps({"schema":"vf1a.science-pytest.v1",
                                "passed":True,"exit_code":0}),encoding="utf-8")
    ok=runner.independent_test_receipt(path)
    assert ok["eligible"]
    assert runner.scientific_gate_eligible(True,ok)
    assert not runner.scientific_gate_eligible(False,ok)
