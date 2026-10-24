"""SA-2A registered independent baffle/radiation tests.

Experiment-local SciPy: mainstream Core tests may skip if SciPy is absent,
but SA-2 GitHub Actions explicitly installs it and MUST run all tests.
"""
from __future__ import annotations
import io
import math
import runpy
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("scipy")
ROOT=Path(__file__).resolve().parents[1]
M=runpy.run_path(str(ROOT/"experiments/049_baffled_piston_sa2a/run.py"))


def test_analytic_gates_all_registered():
    g=M["analytic_gates"]()
    assert g["oracle_max_abs_error"]<=2e-9
    assert g["hemisphere_max_relative_power_error"]<=2e-8
    assert g["small_ka_R_relative_error"]<1e-3
    assert g["small_ka_X_relative_error"]<1e-3
    assert g["minimum_R"]>=-1e-12
    assert g["negative_frequency_conjugate"]
    assert g["onaxis_D"]==1.0


@pytest.mark.parametrize("x",[0.,.005,.02,.1,.25,.55,.8])
def test_rayleigh_pair_separation_independent_oracle(x):
    z=M["_normalized_nonnegative"](x)
    q=M["normalized_overlap_oracle"](x)
    assert abs(z-q)<=2e-9


@pytest.mark.parametrize("x",[0.,.005,.02,.1,.25,.55,.8])
def test_farfield_hemisphere_power_identity(x):
    z=M["_normalized_nonnegative"](x)
    R=M["hemisphere_resistance_quadrature"](x)
    assert float(R)>=0.
    if x:
        assert abs(float(R)-float(z.real))/float(z.real)<=2e-8
    else:
        assert R==0. and z==0.


def test_volume_flow_vs_mechanical_impedance_area_conversion():
    radius=.01
    area=math.pi*radius*radius
    z=M["radiation_impedance"](1000.,radius)
    normalized=M["_normalized_nonnegative"](2*math.pi*1000*radius/M["C"])
    assert abs(z/(M["RHO"]*M["C"]/area)-normalized)<2e-10
    # F/v = acoustic (p/U) * S²; not the same physical units.
    assert abs((z*area*area)/(M["RHO"]*M["C"]*area)-normalized)<2e-10


def test_mouth_geometry_affects_complex_resistance_and_reactance():
    a,b=(M["radiation_impedance"](1000.,r) for r in (.005,.01))
    assert a!=b
    assert a.real>0 and a.imag>0 and b.real>0 and b.imag>0


def test_stable_zero_and_finite_small_ka():
    zz=M["radiation_impedance"](np.array([0.,1e-7,200.]),.01)
    assert zz[0]==0
    assert np.all(np.isfinite(zz))
    assert np.all(zz.real>=0)


def test_negative_frequency_symmetry():
    f=np.array([-1000.,-200.,0.,200.,1000.])
    z=M["radiation_impedance"](f,.01)
    assert np.allclose(z[:2],np.conj(z[-1:-3:-1]),atol=1e-12,rtol=0)


@pytest.mark.parametrize("bad",[0.,-0.01,float("nan"),float("inf")])
def test_invalid_radius_rejected(bad):
    with pytest.raises(ValueError):
        M["radiation_impedance"](1000.,bad)


@pytest.mark.parametrize("bad",[float("nan"),float("inf")])
def test_invalid_frequency_rejected(bad):
    with pytest.raises(ValueError):
        M["radiation_impedance"](bad,.01)


def test_piston_directivity_theta_zero():
    assert M["directivity"](.8,0.)==1.
    assert np.isfinite(M["farfield_observer_per_volume_flow"](1000.,.01))


def test_real_cc_a2_m0_two_port_without_waveform():
    body, arrays=M["body_frequency_study"]()
    assert body["section_count"]==16
    assert body["lip_area_m2"]>0.
    assert body["lip_radius_m"]>0.
    assert body["port_identity_max_rel"]<2e-10
    assert body["minimum_power_dissipated_w"]>=-1e-12
    assert body["state"]=="FREQUENCY_ONLY_NO_CAUSAL_TIME_DOMAIN"
    assert len(body["traces"])>=1
    assert arrays["m0_zrad_pa_s_m3.npy"].dtype==np.complex128


def test_complex_evidence_retains_phase():
    x=np.array([2+3j, -1j])
    restored=np.load(io.BytesIO(M["_npy"](x)),allow_pickle=False)
    assert np.array_equal(x,restored)
