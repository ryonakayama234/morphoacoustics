"""Scientific B1 gates; research-only and independent of adopted Core API."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys

import numpy as np
import pytest

pytest.importorskip("scipy")
SRC = Path(__file__).resolve().parents[1] / "experiments/051_b1_passive_duct/run.py"
spec = importlib.util.spec_from_file_location("sa2b_b1_test_module", SRC)
assert spec and spec.loader
b1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = b1
spec.loader.exec_module(b1)


@pytest.mark.parametrize("termination", ["closed", "matched", "b0"])
def test_zero_state_zero_drive_is_exact(termination):
    duct = b1.UniformDuct(b1.DuctConfig(termination=termination))
    tr = duct.trace(np.zeros(64))
    assert np.array_equal(tr, np.zeros_like(tr))
    assert np.array_equal(duct.state, np.zeros_like(duct.state))


@pytest.mark.parametrize("field,bad", [
    ("area_m2", 0.), ("length_m", -1.), ("rho", float("nan")),
    ("c", float("inf")), ("fs_hz", 0.), ("cells", 1), ("cells", True),
    ("termination", "unphysical"),
])
def test_fail_closed_invalid_physical_config(field, bad):
    kwargs = {field: bad}
    with pytest.raises(ValueError):
        b1.DuctConfig(**kwargs)


def test_nonfinite_input_does_not_mutate_state():
    duct = b1.UniformDuct(b1.DuctConfig())
    old = duct.state.copy()
    with pytest.raises(ValueError):
        duct.step(float("nan"))
    assert np.array_equal(old, duct.state)
    with pytest.raises(ValueError):
        duct.trace(np.array([1e-6,float("inf")]))
    assert np.array_equal(old, duct.state)


@pytest.mark.parametrize("termination", ["closed", "matched", "b0"])
def test_seeded_signed_external_drive_has_energy_ledger(termination):
    cfg = b1.DuctConfig(termination=termination)
    duct = b1.UniformDuct(cfg)
    rng = np.random.default_rng(20261024)
    inlet = np.zeros(300)
    inlet[:130] = rng.normal(scale=1e-6, size=130)
    tr = duct.trace(inlet)
    summary = b1.energy_gate(tr)
    assert summary["normalized_max_sample_residual"] <= 1.
    assert np.isfinite(duct.state).all()
    assert np.all(tr[:,9] >= 0)
    # Strict discrete identity, not a generic sound smoothing operation:
    assert np.max(np.abs(tr[:,11])) <= 1e-8 * np.max(
        np.maximum.reduce((abs(tr[:,10]), abs(tr[:,8]), abs(tr[:,9]),
                           np.full(len(tr),1e-20)))
    )


@pytest.mark.parametrize("termination", ["closed", "matched", "b0"])
def test_initial_stored_pressure_cannot_generate_net_energy(termination):
    cfg = b1.DuctConfig(termination=termination)
    initial = 1e-4 * np.cos(np.pi*(np.arange(cfg.cells)+0.5)/cfg.cells)
    duct = b1.UniformDuct(cfg, initial_pressure_pa=initial)
    initial_energy = duct.energy()
    energies = [initial_energy]
    samples = []
    for _ in range(1000):
        samples.append(duct.step(0.))
        energies.append(duct.energy())
    tr = np.array([tuple(vars(r).values()) for r in samples])
    # Slightly lower excitation makes the stringent pre-registered 1e-20 J
    # *absolute* zero-work floor numerically meaningful.
    summary = b1.energy_gate(tr,initial_energy_j=initial_energy)
    assert summary["normalized_max_sample_residual"]<=1.
    if termination == "closed":
        assert abs(energies[-1]-initial_energy) <= 1e-8*initial_energy
    else:
        assert all(energies[j+1] <= energies[j] +
                   1e-12*max(energies[j], 1e-20)
                   for j in range(1000))


def test_b0_unchanged_original_one_port_equivalence():
    cfg=b1.DuctConfig()
    duct=b1.UniformDuct(cfg)
    lib=b1._b0_module()
    rng=np.random.default_rng(170177)
    incident=rng.normal(scale=1e-6,size=120)
    for u in incident:
        before_q=float(duct.state[-1])
        step=duct.step(float(u))
        one=lib.BaffledRadiationOnePort(duct.b0, initial_q_m3_s=before_q).step(
            step.lip_incident_pa
        )
        comparisons=(
            (one.reflected_pa, step.lip_reflected_pa),
            (one.pressure_pa,step.lip_pressure_mid_pa),
            (one.volume_flow_m3_s,step.lip_volume_flow_mid_m3_s),
            (one.inertial_flow_m3_s,float(duct.state[-1])),
            (one.stored_energy_j,step.mouth_energy_j),
            (one.resistance_dissipation_j,step.dissipated_j),
        )
        for expected,actual in comparisons:
            assert abs(expected-actual) <= 1e-9*max(abs(expected),abs(actual),1e-15)


def test_exact_unrounded_duct_dimensions_and_resolution():
    cfg=b1.DuctConfig()
    assert math.isclose(cfg.courant,343/480,rel_tol=1e-13)
    assert math.isclose(48000*cfg.length_m/cfg.c,22.39067055393586,
                        rel_tol=1e-10)
    assert math.isclose(48000*0.01/cfg.c,1.399416909620991,
                        rel_tol=1e-10)
    assert cfg.dx==pytest.approx(0.01)
    assert b1.DuctConfig(cells=32,fs_hz=96000).courant==pytest.approx(cfg.courant)


def test_closed_tube_real_modal_oscillation_and_convergence():
    cfg=b1.DuctConfig(cells=16,fs_hz=48000,termination="closed")
    x = np.cos(np.pi*(np.arange(cfg.cells)+0.5)/cfg.cells)
    tube=b1.UniformDuct(cfg,initial_pressure_pa=x)
    tr=tube.trace(np.zeros(4800))
    amp=np.abs(np.fft.rfft(tr[:,0]))
    frequencies=np.fft.rfftfreq(len(tr),1/cfg.fs_hz)
    measured=frequencies[np.argmax(amp[1:])+1]
    assert abs(measured-b1.modal_frequency_hz(cfg)) <= 12
    errors=[]
    for n,fs in ((16,48000),(32,96000),(64,192000)):
        c=b1.DuctConfig(cells=n,fs_hz=fs,termination="closed")
        errors.append(abs(b1.modal_frequency_hz(c)-c.c/(2*c.length_m)))
    assert errors[0] > errors[1] > errors[2]
    assert errors[1]/errors[0] <= .36
    assert errors[2]/errors[1] <= .36


def test_continuum_complex_transfer_and_phase_grid_convergence():
    previous=None
    for n,fs in ((16,48000),(32,96000),(64,192000)):
        cfg=b1.DuctConfig(cells=n,fs_hz=fs,termination="b0")
        duct=b1.UniformDuct(cfg)
        errors=[]
        for f in (200.,400.,600.):
            exact=b1.continuum_b0_transfer(f,cfg)
            digital=b1.midpoint_transfer(f,duct)
            ratio=abs(digital-exact)/abs(exact)
            assert math.isfinite(ratio)
            assert math.isfinite(float(np.angle(digital/exact)))
            errors.append(ratio)
        if previous is None:
            assert max(errors)<=.25
        else:
            assert all(e <= .65*p for e,p in zip(errors,previous))
        previous=errors


def test_m0_3000hz_excluded_from_b0_theoretical_ka_domain():
    a=math.sqrt(b1.M0_LIP_AREA_M2/math.pi)
    assert 2*math.pi*3000*a/b1.SOUND_C > .8
    assert 2*math.pi*2600*a/b1.SOUND_C < .8


def test_archived_raw_trace_contains_actual_physical_port_energy(tmp_path):
    target=tmp_path/"first"
    result=b1.experiment(target)
    assert result["decision"] == "B1_EXPERIMENT_EXECUTED_AWAITING_INDEPENDENT_CI_AUDIT"
    assert result["human_voice_quality"] == "NOT_TESTED"
    assert len(result["sha256"]) == 3
    import hashlib
    for path,digest in result["sha256"].items():
        assert hashlib.sha256((target/path).read_bytes()).hexdigest()==digest
        assert np.load(target/path,allow_pickle=False).shape[1]==len(b1.TRACE_COLUMNS)
    with pytest.raises(FileExistsError):
        b1.experiment(target)
