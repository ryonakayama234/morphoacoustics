"""Independent and adversarial VF-1B1 modal observer tests.

All claims concern the exactly symmetric VF-1A surrogate, not human phonation.
"""
from __future__ import annotations

from dataclasses import replace
import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"036_vf1a_two_mass"))
from two_mass import Tissue, make_pilot
from modal import (coordinates,energy,midpoint_transition,observe_step,
                   independent_work_identity)


def test_orthonormal_modes_reconstruct_original_tissue_energy():
    t=Tissue()
    for x,v in (((2e-5,-2e-5),(0.,0.)),
                ((5e-4,3e-4),(0.1,-0.2)),
                ((0.,0.),(0.,1.))):
        stored=sum(energy(x,v,t))
        raw=0.5*np.dot(np.array(t.masses_kg),np.array(v)**2)+0.5*np.array(x)@t.stiffness@np.array(x)
        assert stored==pytest.approx(raw,rel=3e-15,abs=2e-17)
        xx,vv=coordinates(x,v)
        assert np.dot(xx,xx)==pytest.approx(np.dot(x,x),abs=1e-15)
        assert np.dot(vv,vv)==pytest.approx(np.dot(v,v),abs=1e-15)


def test_antisymmetric_midpoint_oracle_independent_of_driving_flow_and_tract():
    cases=[
        make_pilot(pressure_shape="uniform"),
        make_pilot(pressure_shape="constricted"),
        make_pilot(pressure_shape="uniform")
    ]
    conditions=(0.,800.,1300.)
    predictors=[]
    for sim in cases:
        x,v=coordinates(sim.x,sim.v)
        predictors.append(np.array((x[1],v[1])))
    for k in range(1100):
        current=[]
        for sim,drive,prior in zip(cases,conditions,predictors):
            expected=midpoint_transition(sim.tissue,sim.dt)@prior
            x0,v0=sim.x.copy(),sim.v.copy()
            out=sim.step(subglottal_pressure_pa=drive)
            got=observe_step(sim.tissue,sim.dt,x0,v0,out)
            assert got.antisym_midpoint_oracle_error<2e-14
            assert got.pressure_work_j[1]==0
            assert got.damping_loss_j[1]>=0
            assert got.residual_j[1]==pytest.approx(0,abs=2e-13)
            current.append(np.asarray(got.coordinate_after_m[1:]+got.velocity_after_m_s[1:]))
            predictors[cases.index(sim)]=expected
        # Anti mode cannot know Psub or pressure_shape in this symmetric model.
        assert current[0][0]==pytest.approx(current[1][0],abs=2e-14)
        assert current[1][0]==pytest.approx(current[2][0],abs=2e-14)


def test_independently_rebuilt_total_work_and_mode_work_are_identical():
    sim=make_pilot()
    for i in range(500):
        x0,v0=sim.x.copy(),sim.v.copy()
        out=sim.step(subglottal_pressure_pa=800.)
        record=observe_step(sim.tissue,sim.dt,x0,v0,out)
        external=independent_work_identity(sim.tissue,sim.dt,x0,v0,out)
        assert sum(record.pressure_work_j)==pytest.approx(external["full_pressure_work_j"],abs=3e-16)
        assert sum(record.damping_loss_j)==pytest.approx(external["full_damping_loss_j"],abs=3e-16)
        assert sum(record.energy_after_j)-sum(record.energy_before_j)==pytest.approx(external["full_mechanical_delta_j"],abs=3e-16)
        assert max(map(abs,record.residual_j))<2e-13
        assert abs(external["full_identity_residual_j"])<2e-13


def test_antisymmetric_mode_dissipates_without_aerodynamic_pumping():
    sim=make_pilot()
    energy_old=energy(sim.x,sim.v,sim.tissue)[1]
    assert energy_old>0
    for _ in range(1000):
        x0,v0=sim.x.copy(),sim.v.copy()
        out=sim.step(subglottal_pressure_pa=800.)
        obs=observe_step(sim.tissue,sim.dt,x0,v0,out)
        assert obs.pressure_work_j[1]==0
        assert obs.energy_after_j[1]<=energy_old+2e-18
        energy_old=obs.energy_after_j[1]
    assert energy_old < energy((2e-5,-2e-5),(0.,0.),sim.tissue)[1]


def test_refuse_false_antisymmetric_decoupling_for_asymmetric_tissue():
    base=Tissue()
    for modified in (
        replace(base,masses_kg=(1.2e-4,1.3e-4)),
        replace(base,stiffness_n_m=(30.,31.)),
        replace(base,damping_n_s_m=(0.008,0.01)),
        replace(base,pressure_areas_m2=(3e-5,2e-5)),
    ):
        with pytest.raises(ValueError,match="UNSUPPORTED_ASYMMETRIC"):
            midpoint_transition(modified,1/48000)


def test_false_mechanical_trace_is_not_certified():
    sim=make_pilot()
    x0,v0=sim.x.copy(),sim.v.copy()
    out=sim.step(subglottal_pressure_pa=800.)
    correct=observe_step(sim.tissue,sim.dt,x0,v0,out)
    assert max(map(abs,correct.residual_j))<1e-12
    tampered=replace(out,x_m=(out.x_m[0]+1e-4,out.x_m[1]))
    corrupt=observe_step(sim.tissue,sim.dt,x0,v0,tampered)
    assert max(map(abs,corrupt.residual_j))>1e-10
    assert corrupt.antisym_midpoint_oracle_error>1e-9


def test_tests_are_required_for_aggregate_scientific_pass(tmp_path):
    import run
    assert not run.test_status(None)["eligible"]
    p=tmp_path/"test_status.json"
    for bad in (
        {"schema":"vf1b1.independent-pytest.v1","passed":True,"exit_code":False},
        {"schema":"vf1b1.independent-pytest.v1","passed":True,"exit_code":1},
        {"schema":"vf1b1.independent-pytest.v1","passed":1,"exit_code":0},
        {"schema":"vf1b1.independent-pytest.v1","passed":False,"exit_code":1},
        {"schema":"vf1a.science-pytest.v1","passed":True,"exit_code":0}
    ):
        p.write_text(json.dumps(bad),encoding="utf-8")
        assert not run.test_status(p)["eligible"]
    p.write_text("{bad",encoding="utf-8")
    assert not run.test_status(p)["eligible"]
    p.write_text(json.dumps({"schema":"vf1b1.independent-pytest.v1",
                             "passed":True,"exit_code":0}),encoding="utf-8")
    assert run.test_status(p)["eligible"]


def test_invalid_timestep_rejected():
    for val in (float("nan"),float("inf"),-1,0):
        with pytest.raises(ValueError):
            midpoint_transition(Tissue(),val)


def test_modal_damping_rate_is_positive_under_default_tissue():
    t=Tissue()
    transition=midpoint_transition(t,1/48000)
    assert np.max(np.abs(np.linalg.eigvals(transition)))<1.0
    assert np.isclose(np.linalg.det(transition),np.prod(np.linalg.eigvals(transition)))
