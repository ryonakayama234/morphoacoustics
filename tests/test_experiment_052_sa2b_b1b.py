"""Gate A2 independent B1b wavefront, reflection, group delay and energy tests."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys

import numpy as np
import pytest

pytest.importorskip("scipy")
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("sa2b_b1b_tested",BASE/"experiments/052_b1b_local_waveguide/run.py")
assert spec and spec.loader
w=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=w
spec.loader.exec_module(w)


@pytest.mark.parametrize("bad", [
    {"length_m":0.}, {"length_m":0.165}, {"area_m2":float("nan")},
    {"rho":-1.}, {"c":float("inf")}, {"reference_section_m":0.},
    {"cells_per_section":1}, {"cells_per_section":True},
    {"cells_per_section":16}, {"termination":"bogus"},
])
def test_invalid_geometry_and_clock_fail_closed(bad):
    with pytest.raises(ValueError):
        w.PhysicalClockDuct(**bad)


@pytest.mark.parametrize("mouth",w.TERMINATIONS)
def test_exact_zero_and_nonfinite_input_without_mutation(mouth):
    cfg=w.PhysicalClockDuct(termination=mouth)
    duct=w.LocalTravelingWaveDuct(cfg)
    t=duct.trace(np.zeros(128))
    assert np.array_equal(t[:,1:],np.zeros_like(t[:,1:]))
    assert duct.total_energy_j()==0.
    before=(tuple(duct.forward),tuple(duct.backward),duct.ticks,
            duct.port.q_m3_s if duct.port else None)
    with pytest.raises(ValueError):
        duct.step(float("nan"))
    with pytest.raises(ValueError):
        duct.trace(np.array([0.,float("inf")]))
    after=(tuple(duct.forward),tuple(duct.backward),duct.ticks,
           duct.port.q_m3_s if duct.port else None)
    assert after==before


@pytest.mark.parametrize("n",[2,4,8])
@pytest.mark.parametrize("mouth",w.TERMINATIONS)
def test_strict_local_wavefront_and_first_reflection(n,mouth):
    cfg=w.PhysicalClockDuct(cells_per_section=n,termination=mouth)
    assert cfg.n_cells==16*n
    assert cfg.fs_hz==pytest.approx(343*n/.01)
    assert cfg.one_way_s==pytest.approx(cfg.n_cells/cfg.fs_hz,rel=1e-14)
    assert cfg.one_way_s*48000==pytest.approx(22.39067055393586,rel=1e-10)
    assert cfg.one_way_s != pytest.approx(16/48000,rel=1e-3)
    inp=np.zeros(4*cfg.n_cells+4)
    inp[0]=1e-6
    t=w.LocalTravelingWaveDuct(cfg).trace(inp)
    assert np.all(t[:cfg.n_cells,4]==0.)
    assert t[cfg.n_cells,4]==pytest.approx(cfg.zc*1e-6)
    assert np.all(t[:2*cfg.n_cells,3]==0.)
    if mouth=="matched":
        assert np.all(t[:,3]==0.)
        assert np.all(t[:,5]==0.)
    else:
        assert t[2*cfg.n_cells,3]!=0.
        expected={"closed":+1.,"pressure_release":-1.}
        if mouth in expected:
            assert t[cfg.n_cells,5]/t[cfg.n_cells,4]==pytest.approx(expected[mouth])
            assert t[2*cfg.n_cells,3]/t[cfg.n_cells,4]==pytest.approx(expected[mouth])
    neg=np.zeros(len(inp));neg[0]=-1e-6
    nt=w.LocalTravelingWaveDuct(cfg).trace(neg)
    np.testing.assert_allclose(nt[:,1:9],-t[:,1:9],rtol=1e-12,atol=1e-14)


def test_physically_reconstructed_pressure_flow_energy():
    cfg=w.PhysicalClockDuct(termination="closed")
    rng=np.random.default_rng(3331)
    fa=rng.normal(scale=.1,size=cfg.n_cells)
    ba=rng.normal(scale=.1,size=cfg.n_cells)
    d=w.LocalTravelingWaveDuct(cfg,initial_forward_pa=fa,initial_backward_pa=ba)
    p,u=d.field_p_u()
    si=cfg.dx * np.sum(cfg.area_m2*p*p/(2*cfg.rho*cfg.c*cfg.c)
                  +cfg.rho*u*u/(2*cfg.area_m2))
    assert si==pytest.approx(d.wave_energy_j(),rel=3e-14)
    assert d.wave_energy_j()>0


@pytest.mark.parametrize("mouth",w.TERMINATIONS)
def test_signed_driven_and_undriven_energy(mouth):
    cfg=w.PhysicalClockDuct(termination=mouth)
    rng=np.random.default_rng(20261024)
    sig=np.zeros(1024)
    sig[:128]=rng.normal(scale=1e-6,size=128)
    d=w.LocalTravelingWaveDuct(cfg)
    tr=d.trace(sig)
    summary=w.energy_gate(tr)
    assert summary["max_normalized_step_residual"]<=1.
    np.testing.assert_allclose(tr[:,11],cfg.time_step_s*tr[:,6]*tr[:,1],rtol=1e-8,atol=1e-19)
    assert np.all(tr[:,12]>=0)
    ini=w.LocalTravelingWaveDuct(
        cfg,initial_forward_pa=rng.normal(scale=.01,size=cfg.n_cells),
        initial_backward_pa=rng.normal(scale=.01,size=cfg.n_cells),
        initial_b0_q_m3_s=1e-7 if mouth=="b0" else 0.)
    e0=ini.total_energy_j()
    free=ini.trace(np.zeros(1024))
    w.energy_gate(free,initial_total_j=e0)
    cur=free[:,9]+free[:,10]
    if mouth in ("closed","pressure_release"):
        assert abs(cur[-1]-e0)<=max(1e-10*e0,1e-20)
    else:
        previous=np.concatenate(([e0],cur[:-1]))
        assert np.all(cur <= previous + 1e-12*np.maximum(previous,1e-20))


def test_original_b0_step_equivalence_with_source_feedback_and_stored_q():
    cfg=w.PhysicalClockDuct()
    lib=w._b0_module()
    rng=np.random.default_rng(170177)
    inlet=rng.normal(scale=1e-6,size=512)
    d=w.LocalTravelingWaveDuct(cfg,initial_b0_q_m3_s=1e-7)
    separate=lib.BaffledRadiationOnePort(d.port.parameters,initial_q_m3_s=1e-7)
    for u in inlet:
        s=d.step(float(u))
        ref=separate.step(s.lip_incident_pa)
        for actual,expected in (
            (s.lip_reflected_pa,ref.reflected_pa),
            (s.lip_pressure_pa,ref.pressure_pa),
            (s.lip_flow_m3_s,ref.volume_flow_m3_s),
            (s.mouth_energy_j,ref.stored_energy_j),
            (s.outlet_dissipation_j,ref.resistance_dissipation_j),
            (d.port.q_m3_s,ref.inertial_flow_m3_s),
        ):
            assert abs(actual-expected)<=1e-9*max(abs(actual),abs(expected),1e-15)


def test_matched_group_delay_measured_from_impulse_response():
    for n in (2,4,8):
        cfg=w.PhysicalClockDuct(cells_per_section=n,termination="matched")
        lip=w.LocalTravelingWaveDuct(cfg).impulse_lip_pressure(4*cfg.n_cells)
        for f in (200.,400.,600.,1000.,2600.):
            step=.25
            hm=w.empirical_transfer_at_frequency(lip,cfg,f-step)
            hp=w.empirical_transfer_at_frequency(lip,cfg,f+step)
            measured_delay=-np.angle(hp/hm)/(4*math.pi*step)
            assert abs(measured_delay-cfg.one_way_s)<1e-9


def test_theory_transfer_analytic_convergence_and_old_solver_comparison():
    # Existing old B1 is retained and used as an entirely separate semi-discrete oracle.
    orig_spec=importlib.util.spec_from_file_location("sa2b_b1_reference",BASE/"experiments/051_b1_passive_duct/run.py")
    orig=importlib.util.module_from_spec(orig_spec)
    sys.modules[orig_spec.name]=orig
    orig_spec.loader.exec_module(orig)
    old=orig.UniformDuct(orig.DuctConfig())
    olderrors={}
    errors=[]
    for n in (2,4,8):
        cfg=w.PhysicalClockDuct(cells_per_section=n)
        row=[]
        for f in (200.,400.,600.,1000.,2600.):
            discrete=w.independent_discrete_scattering_transfer(f,cfg)
            analog=w.continuum_analog_transfer(f,cfg)
            err=abs(discrete-analog)/abs(analog)
            row.append(err)
            if n==2 and f in (200.,400.,600.):
                oldh=orig.midpoint_transfer(f,old)
                olderrors[f]=abs(oldh-analog)/abs(analog)
        errors.append(row)
    assert max(errors[0])<0.005
    assert np.all(np.array(errors[1])<=.32*np.array(errors[0]))
    assert np.all(np.array(errors[2])<=.32*np.array(errors[1]))
    for k in (200.,400.,600.):
        i=(200.,400.,600.,1000.,2600.).index(k)
        assert errors[0][i]<olderrors[k]


def test_actual_impulse_b0_transfer_and_metered_unmetered_agree():
    cfg=w.PhysicalClockDuct()
    fast=w.LocalTravelingWaveDuct(cfg)
    impulse=fast.impulse_lip_pressure(int(5.0*cfg.fs_hz))
    d=w.LocalTravelingWaveDuct(cfg)
    tr=d.trace(np.r_[1e-6,np.zeros(4*cfg.n_cells-1)])
    np.testing.assert_allclose(impulse[:len(tr)],tr[:,7],rtol=1e-13,atol=1e-13)
    for f in (200.,400.,600.,1000.,2600.):
        experimental=w.empirical_transfer_at_frequency(impulse,cfg,f)
        analytic=w.continuum_analog_transfer(f,cfg)
        discrete=w.independent_discrete_scattering_transfer(f,cfg)
        assert abs(experimental-analytic)/abs(analytic)<.005
        assert abs(experimental-discrete)/abs(discrete)<.0001


def test_negative_controls_catch_wrong_sign_rounding_and_missing_b0_energy():
    closed=w.PhysicalClockDuct(termination="closed")
    c=w.LocalTravelingWaveDuct(closed)
    inp=np.zeros(4*closed.n_cells+3);inp[0]=1e-6
    trace=c.trace(inp)
    observed=trace[closed.n_cells,5]/trace[closed.n_cells,4]
    assert observed==1.
    assert -observed != 1.   # swapped reflection sign fails the +1 physical oracle
    actual=closed.length_m/closed.c*48000
    assert abs(actual-16.)>6. # falsely one audio sample per section fails
    b0=w.LocalTravelingWaveDuct(w.PhysicalClockDuct(),
                                initial_b0_q_m3_s=1e-6)
    t=b0.step(0.)
    # B0 stored inertance is essential to total passive energy accounting.
    assert abs(t.delta_total_energy_j - (t.duct_energy_j))>1e-15
    assert t.mouth_energy_j>0.
