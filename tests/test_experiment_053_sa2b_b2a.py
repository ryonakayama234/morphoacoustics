"""Frozen B2-A tests: passive static junction, exact M0/M1 and B1b parity."""
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest

pytest.importorskip("scipy")
ROOT=Path(__file__).resolve().parents[1]
def load(key,path):
    spec=importlib.util.spec_from_file_location(key,ROOT/path)
    mod=importlib.util.module_from_spec(spec);sys.modules[key]=mod;spec.loader.exec_module(mod)
    return mod
s=load("b2a_experiment_test","experiments/053_b2a_static_multisection/run.py")
b1=load("b1b_reference_test","experiments/052_b1b_local_waveguide/run.py")
FROZEN=json.loads((ROOT/"experiments/028_task_field_morphology_transfer/frozen_reference.json").read_text())

@pytest.fixture(scope="module")
def bodies():return s.prepared_bodies()

def test_actual_prepared_bodies_identity(bodies):
    for name,section_length in (("M0",.01),("M1",.011)):
        body=bodies[name]
        assert body["preset_id"]=="v3b-axial-"+name
        assert body["preset_revision"]==1
        assert body["preparation_digest"].startswith("sha256:")
        np.testing.assert_array_equal(body["areas"],FROZEN["M0"]["a_areas_m2"])
        np.testing.assert_allclose(body["lengths"],section_length,rtol=0,atol=1e-15)
    assert bodies["M0"]["preparation_digest"]!=bodies["M1"]["preparation_digest"]

@pytest.mark.parametrize("bad",[
    {"areas":(1.,0.)}, {"areas":(1.,float("nan"))},
    {"lengths":(.01,-.01)}, {"lengths":(.01,.011)},
    {"cells_per_section":3}, {"cells_per_section":True},
    {"termination":"invalid"}, {"rho":-1.}, {"c":float("nan")}
])
def test_bad_geometry_fails_closed(bad):
    values={"areas":(.001,.002),"lengths":(.01,.01)}
    values.update(bad)
    with pytest.raises(ValueError):s.Config(**values)

@pytest.mark.parametrize("n",[2,4,8])
@pytest.mark.parametrize("name",["M0","M1"])
def test_actual_wavefront_clock_and_zero_support(bodies,n,name):
    cfg=s.config_for(bodies[name],n,"matched")
    assert cfg.n==16*n
    assert cfg.fs==pytest.approx(343*n/(.01 if name=="M0" else .011))
    assert cfg.length==pytest.approx(.16 if name=="M0" else .176)
    d=s.StaticMultisection(cfg)
    assert np.array_equal(d.trace(np.zeros(128))[:,1:],np.zeros((128,len(s.COLS)-1)))
    pulse=s.StaticMultisection(cfg).impulse(cfg.n*3)
    assert np.all(pulse[:cfg.n]==0.)
    assert pulse[cfg.n]!=0.
    assert cfg.n/cfg.fs==pytest.approx(cfg.length/cfg.c,rel=1e-12)
    assert abs(cfg.length/cfg.c*48000-round(cfg.length/cfg.c*48000))>.05

@pytest.mark.parametrize("name",["M0","M1"])
@pytest.mark.parametrize("term",s.TERMS)
def test_signed_energy_and_seeded_storage(bodies,name,term):
    cfg=s.config_for(bodies[name],2,term)
    rng=np.random.default_rng(20261025)
    u=np.zeros(1024);u[:128]=rng.normal(scale=1e-6,size=128)
    d=s.StaticMultisection(cfg)
    t=d.trace(u)
    assert s.energy_gate(t)["max_norm_step"]<=1
    assert np.all(t[:,12]>=0)
    assert np.allclose(t[:,11],cfg.h*t[:,6]*t[:,1],rtol=1e-10,atol=1e-20)
    state=s.StaticMultisection(cfg,forward=rng.normal(scale=.001,size=(16,2)),
             backward=rng.normal(scale=.001,size=(16,2)),
             initial_q=1e-7 if term=="b0" else 0.)
    initial=sum(state.E())
    free=state.trace(np.zeros(1024))
    s.energy_gate(free,initial)
    energies=free[:,9]+free[:,10]
    if term in ("closed","pressure_release"):
        assert abs(energies[-1]-initial)<=max(initial*1e-10,1e-20)
    else:
        prev=np.r_[initial,energies[:-1]]
        assert np.all(energies<=prev+np.maximum(prev*1e-12,1e-20))

def test_junction_exact_power_identity_both_sides():
    rng=np.random.default_rng(167)
    for zl,zr in ((1.,4.),(4.,1.),(.5,1e3),(400000.,800000.),(2.,2.)):
        for _ in range(80):
            a,b=rng.normal(size=2)
            left,right=s.junction(a,b,zl,zr)
            before=a*a/zl+b*b/zr
            after=left*left/zl+right*right/zr
            assert abs(before-after)<=1e-11*max(before,after,1e-20)
            if zl==zr:
                assert left==pytest.approx(b,rel=1e-14,abs=1e-14)
                assert right==pytest.approx(a,rel=1e-14,abs=1e-14)

def test_equal_area_exact_b1b_reduction():
    area=s.FROZEN_AREA if hasattr(s,"FROZEN_AREA") else .000804247719318987
    for n in (2,4):
        cfg=s.Config((area,)*16,(.01,)*16,n,"b0")
        original=b1.PhysicalClockDuct(cells_per_section=n)
        old=b1.LocalTravelingWaveDuct(original)
        new=s.StaticMultisection(cfg)
        rng=np.random.default_rng(177)
        u=np.zeros(400);u[:100]=rng.normal(scale=1e-6,size=100)
        ot=old.trace(u);nt=new.trace(u)
        for oldcol,newcol in ((4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,12)):
            np.testing.assert_allclose(nt[:,newcol],ot[:,oldcol],rtol=1e-10,atol=1e-15)

def test_original_b0_is_unchanged(bodies):
    cfg=s.config_for(bodies["M0"],2,"b0")
    original=s._b0()
    d=s.StaticMultisection(cfg,initial_q=1e-7)
    independent=original.BaffledRadiationOnePort(
        original.parameters_from_area(cfg.areas[-1],rho=cfg.rho,c=cfg.c,fs=cfg.fs),
        initial_q_m3_s=1e-7)
    u=np.random.default_rng(78).normal(scale=1e-6,size=200)
    for v in u:
        x=d.step(v);y=independent.step(x.mouth_a)
        assert x.mouth_b==pytest.approx(y.reflected_pa,rel=1e-10,abs=1e-15)
        assert x.E_B0==pytest.approx(y.stored_energy_j,rel=1e-10,abs=1e-20)

def test_nonfinite_input_does_not_mutate_state(bodies):
    d=s.StaticMultisection(s.config_for(bodies["M0"]))
    before=([list(x) for x in d.f],[list(x) for x in d.b],d.ticks,d.port.q_m3_s)
    with pytest.raises(ValueError):d.step(float("nan"))
    with pytest.raises(ValueError):d.trace(np.r_[0.,float("inf")])
    assert before==([list(x) for x in d.f],[list(x) for x in d.b],d.ticks,d.port.q_m3_s)

def test_reversed_anatomy_changes_causal_response(bodies):
    cfg=s.config_for(bodies["M0"],2,"matched")
    reverse=s.Config(tuple(reversed(cfg.areas)),cfg.lengths,2,"matched")
    assert not np.array_equal(s.StaticMultisection(cfg).impulse(256),
                              s.StaticMultisection(reverse).impulse(256))
    assert s.junction(1.,0.,1.,10.)[0]!=s.junction(1.,0.,10.,1.)[0]
