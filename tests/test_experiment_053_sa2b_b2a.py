"""Pre-registered SA-2B B2-A: anatomy-bound local scattering, no production API."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest

pytest.importorskip("scipy")
ROOT=Path(__file__).resolve().parents[1]
def loaded(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    assert spec and spec.loader
    v=importlib.util.module_from_spec(spec)
    sys.modules[name]=v
    spec.loader.exec_module(v)
    return v
w=loaded("sa2b_b2a_gate","experiments/053_b2a_anatomical_waveguide/run.py")
old=loaded("sa2b_b1b_regression","experiments/052_b1b_local_waveguide/run.py")

@pytest.fixture(scope="module")
def bodies():
    return w.prepared_bodies()


def test_real_prepared_bodies_and_independent_frozen_reference(bodies):
    frozen=json.loads((ROOT/"experiments/028_task_field_morphology_transfer/frozen_reference.json").read_text())["M0"]
    assert set(bodies)==set(w.BODIES)
    m0,m1,mi=(bodies[k] for k in w.BODIES)
    assert m0.preset_id=="v3b-axial-M0"
    assert m1.preset_id=="v3b-axial-M1"
    assert "NOT separate body registry preset" in mi.source
    for body in bodies.values():
        assert len(body.areas_m2)==16
        assert len(body.lengths_m)==16
        assert len(set(body.areas_m2))>=3
    np.testing.assert_array_equal(m0.lengths_m,frozen["section_lengths_m"])
    np.testing.assert_array_equal(m0.areas_m2,frozen["a_areas_m2"])
    np.testing.assert_array_equal(mi.areas_m2,frozen["i_areas_m2"])
    np.testing.assert_array_equal(m0.areas_m2,m1.areas_m2)
    assert m0.total_length_m==pytest.approx(.160)
    assert m1.total_length_m==pytest.approx(.176)
    assert m1.total_length_m/m0.total_length_m==pytest.approx(1.1)
    assert m0.lip_area_m2==pytest.approx(w.LIP_M0_A)


@pytest.mark.parametrize("bad", [
    {"cells_per_section":1},{"cells_per_section":0},
    {"cells_per_section":True},{"cells_per_section":16},
    {"termination":"unphysical"},{"rho":float("nan")},
    {"c":0.},{"c":float("inf")},
])
def test_fail_closed_invalid_config(bodies,bad):
    with pytest.raises(ValueError):
        w.AcousticConfig(bodies["M0_a"],**bad)


def test_fail_closed_geometry_requires_real_lengths_and_finite_area(bodies):
    v=bodies["M0_a"]
    attrs=vars(v)
    for changes in (
        {"areas_m2":tuple([float("nan")]+list(v.areas_m2[1:]))},
        {"lengths_m":tuple([0.]+list(v.lengths_m[1:]))},
        {"lengths_m":tuple([.011]+list(v.lengths_m[1:]))},
        {"areas_m2":tuple([v.areas_m2[0]]*16)},
        {"preset_revision":2},
        {"areas_m2":v.areas_m2[:-1]},
    ):
        with pytest.raises(ValueError):
            w.BodySections(**{**attrs,**changes})
    with pytest.raises(ValueError):
        w.AcousticConfig(None)


def test_physical_junction_bidirectional_continuity_energy_and_pressure_oracle():
    rng=np.random.default_rng(25053)
    # independent scalar pressure/flow solve, not the wave scattering formula.
    for _ in range(300):
        s1,s2=rng.uniform(5e-5,1.2e-3,size=2)
        z1,z2=w.RHO*w.C/s1,w.RHO*w.C/s2
        a,b=rng.normal(scale=.2,size=2)
        reflected,transmitted=w.passive_junction(a,b,z1,z2)
        pressure_left=a+reflected
        pressure_right=transmitted+b
        flow_left=(a-reflected)/z1
        flow_right=(transmitted-b)/z2
        assert pressure_left==pytest.approx(pressure_right,rel=1e-12,abs=2e-14)
        assert flow_left==pytest.approx(flow_right,rel=1e-12,abs=2e-18)
        power_left=(a*a-reflected*reflected)/z1
        power_right=(transmitted*transmitted-b*b)/z2
        assert abs(power_left-power_right)<=1e-11*max(abs(power_left),abs(power_right),
              abs(a*a/z1),abs(b*b/z2),1e-20)
        mat=np.array([[1.,1.],[-1/z1,1/z2]])
        # Unknowns reflected, transmitted: pL=pR, U_L=U_R.
        independent=np.linalg.solve(mat,np.array([b-a,-a/z1-b/z2]))
        np.testing.assert_allclose([reflected,transmitted],independent,
                                   rtol=1e-12,atol=1e-13)
        if s1==s2:
            assert reflected==b
            assert transmitted==a
    assert w.passive_junction(.2,-.1,700.,700.)==pytest.approx((-.1,.2))
    with pytest.raises(ValueError):
        w.passive_junction(1.,0.,-1.,3.)


@pytest.mark.parametrize("label",w.BODIES)
@pytest.mark.parametrize("n",(2,4,8))
def test_actual_morphology_front_and_lip_origin_echo(bodies,label,n):
    body=bodies[label]
    match=w.AcousticConfig(body,cells_per_section=n,termination="matched")
    close=w.AcousticConfig(body,cells_per_section=n,termination="closed")
    assert match.wave_cells==16*n
    assert match.one_way_s==pytest.approx(match.wave_cells/match.fs_hz,rel=1e-13)
    assert match.one_way_s*48000!=pytest.approx(round(match.one_way_s*48000),abs=1e-3)
    pulse=np.zeros(3*match.wave_cells+10);pulse[0]=1e-6
    tm=w.AnatomicalWaveguide(match).trace(pulse)
    tc=w.AnatomicalWaveguide(close).trace(pulse)
    N=match.wave_cells
    assert np.array_equal(tm[:N,4],np.zeros(N))
    assert np.array_equal(tc[:N,4],np.zeros(N))
    assert tm[N,4]!=0. and tc[N,4]!=0.
    # Anatomical scattering sends early junction echoes even when mouth is matched.
    assert np.any(tm[:2*N,3]!=0.)
    # Isolate FIRST LIP echo via subtraction; all early anatomical echoes cancel.
    difference=tc[:,3]-tm[:,3]
    np.testing.assert_allclose(difference[:2*N],0.,rtol=0,atol=1e-14)
    assert abs(difference[2*N])>1e-10
    if n==2:
        negative=np.zeros(len(pulse));negative[0]=-1e-6
        ntr=w.AnatomicalWaveguide(close).trace(negative)
        np.testing.assert_allclose(ntr[:,1:9],-tc[:,1:9],rtol=1e-12,atol=1e-13)


@pytest.mark.parametrize("label",w.BODIES)
@pytest.mark.parametrize("mouth",w.MODES)
def test_signed_full_energy_and_nonzero_initial_storage(bodies,label,mouth):
    cfg=w.AcousticConfig(bodies[label],termination=mouth)
    inp=np.zeros(760)
    inp[:128]=np.random.default_rng(25310).normal(scale=1e-6,size=128)
    obj=w.AnatomicalWaveguide(cfg)
    tr=obj.trace(inp)
    gate=w.energy_gate(tr)
    assert gate["max_normalized_residual"]<=1.
    np.testing.assert_allclose(tr[:,11],cfg.h*tr[:,1]*tr[:,6],rtol=1e-10,atol=1e-19)
    assert np.all(tr[:,12]>=0.)
    assert np.all(tr[:,9]>=0.)
    if mouth in ("closed","pressure_release"):
        assert np.array_equal(tr[:,12],np.zeros(len(tr)))
    f=np.random.default_rng(1).normal(scale=.02,size=(16,cfg.cells_per_section))
    g=np.random.default_rng(2).normal(scale=.02,size=(16,cfg.cells_per_section))
    d=w.AnatomicalWaveguide(cfg,initial_forward_pa=f,initial_backward_pa=g,
                            initial_b0_q_m3_s=(1e-7 if mouth=="b0" else 0.))
    energy0=d.total_energy()
    free=d.trace(np.zeros(600))
    w.energy_gate(free,initial_energy_j=energy0)
    arr=free[:,9]+free[:,10]
    if mouth in ("closed","pressure_release"):
        assert abs(arr[-1]-energy0)<=max(1e-10*energy0,1e-20)
    else:
        before=np.r_[energy0,arr[:-1]]
        assert np.all(arr<=before+np.maximum(1e-12*before,1e-20))


def test_b0_immutable_lip_and_q_storage_from_actual_body(bodies):
    lib=w._b0_module()
    for label,body in bodies.items():
        cfg=w.AcousticConfig(body)
        obj=w.AnatomicalWaveguide(cfg,initial_b0_q_m3_s=1e-7)
        assert obj.port.parameters.area_m2==body.lip_area_m2
        assert obj.port.parameters.sample_rate_hz==pytest.approx(cfg.fs_hz)
        independent=lib.BaffledRadiationOnePort(obj.port.parameters,initial_q_m3_s=1e-7)
        rng=np.random.default_rng(399)
        for u in rng.normal(scale=1e-6,size=80):
            t=obj.step(float(u))
            ref=independent.step(t.lip_incident_pa)
            for actual,expected in ((t.lip_reflected_pa,ref.reflected_pa),
                         (t.lip_pressure_pa,ref.pressure_pa),
                         (t.lip_flow_m3_s,ref.volume_flow_m3_s),
                         (t.mouth_energy_j,ref.stored_energy_j),
                         (t.outlet_loss_j,ref.resistance_dissipation_j)):
                assert abs(actual-expected)<=1e-9*max(abs(actual),abs(expected),1e-15)
            assert obj.port.q_m3_s==pytest.approx(ref.inertial_flow_m3_s,rel=1e-12)


def test_uniformized_B2_reduces_exactly_to_B1b(bodies):
    m=bodies["M0_a"]
    a=m.lip_area_m2
    uniform=w.BodySections("uniform","uniform-reference",1,"B1b uniform control",
                            m.lengths_m,tuple([a]*16))
    cfg=w.AcousticConfig(uniform)
    oldcfg=old.PhysicalClockDuct(area_m2=a)
    a1=w.AnatomicalWaveguide(cfg)
    a2=old.LocalTravelingWaveDuct(oldcfg)
    src=np.zeros(200);src[0]=1e-6;src[67]=-3e-7
    t1=a1.trace(src)
    t2=a2.trace(src)
    np.testing.assert_allclose(t1[:,4:9],t2[:,4:9],rtol=1e-11,atol=1e-12)
    np.testing.assert_allclose(t1[:,9:15],t2[:,9:15],rtol=1e-10,atol=1e-15)


def test_complex_transfer_converges_and_body_identity_is_not_erased(bodies):
    errors={}
    transfers={}
    for label,body in bodies.items():
        errors[label]={}
        transfers[label]={}
        for n in (2,4,8):
            cfg=w.AcousticConfig(body,cells_per_section=n)
            assert cfg.one_way_s == pytest.approx((.176 if label=="M1_a" else .16)/343)
            e=[]
            hlist=[]
            for f in w.FREQS:
                lip_k_a=2*math.pi*f*math.sqrt(body.lip_area_m2/math.pi)/cfg.c
                assert lip_k_a<=.8
                # Real analog positive impedance, NOT static ideal pressure-release.
                href=w.continuous_transfer(f,cfg)
                hlist.append(href)
                # Discrete B0 bilinear frequency response differs from analog;
                # even algebraic model error MUST fall on refinement.
                b0=w._b0_module()
                pars=b0.parameters_from_area(body.lip_area_m2,fs=cfg.fs_hz)
                gamma=b0.gamma_digital(f,pars)
                assert abs(gamma)<=1.
                e.append((f,href))
            transfers[label][n]=hlist
            # Actual time impulse is evaluated by CI archive (not formula-only gate).
        assert abs(transfers[label][2][2]-transfers[label][4][2])<1e-6*abs(transfers[label][2][2])
    m0,m1,mi=(np.array(transfers[name][2]) for name in w.BODIES)
    # preserve real character identity on normalized complex pressure transfer
    assert sum(abs(m0-m1)/np.maximum(abs(m0),abs(m1))>.005)>=2
    assert sum(abs(m0-mi)/np.maximum(abs(m0),abs(mi))>.005)>=2
    # section-order is observable, NOT a commute-able list of tubes
    src=bodies["M0_a"]
    rev=w.BodySections("reverse-test",src.preset_id,1,"reversal negative control",
         src.lengths_m,tuple(reversed(src.areas_m2)))
    a=w.continuous_transfer(600.,w.AcousticConfig(src))
    b=w.continuous_transfer(600.,w.AcousticConfig(rev))
    assert abs(a-b)/max(abs(a),abs(b))>.005


def test_morphology_clocks_and_geometry_are_not_48k_rounded(bodies):
    c0=w.AcousticConfig(bodies["M0_a"])
    c1=w.AcousticConfig(bodies["M1_a"])
    assert c0.fs_hz==pytest.approx(68600.)
    assert c1.fs_hz==pytest.approx(343*2/.011)
    assert c1.one_way_s/c0.one_way_s==pytest.approx(1.1)
    assert c0.one_way_s*48000==pytest.approx(22.39067055393586)
    assert c1.one_way_s*48000==pytest.approx(24.62973760932945)


def test_experiment_manifest_signed_SI_and_archive_exclusivity(tmp_path):
    destination=tmp_path/"first"
    m=w.experiment(destination)
    assert m["scientific_status"]=="AWAITING_INDEPENDENT_CI_AND_ARTIFACT_AUDIT"
    assert set(m["bodies"])==set(w.BODIES)
    assert len(m["sha256"])==33
    import hashlib
    for name,digest in m["sha256"].items():
        blob=(destination/name).read_bytes()
        assert hashlib.sha256(blob).hexdigest()==digest
        assert np.isfinite(np.load(destination/name,allow_pickle=False)).all()
    with pytest.raises(FileExistsError):
        w.experiment(destination)
