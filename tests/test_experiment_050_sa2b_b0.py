"""Independent tests for immutable SA-2B B0 Gate-A physical one-port.

No adopted public API and no acoustical observer claims.
"""
from __future__ import annotations

from dataclasses import replace
import importlib.util
import io
import math
from pathlib import Path
import sys

import numpy as np
import pytest

pytest.importorskip("scipy")
ROOT = Path(__file__).resolve().parents[1]
SOURCE=ROOT/"experiments/050_b0_passive_radiation/run.py"
spec=importlib.util.spec_from_file_location("morpho_b0_experiment_test_module",SOURCE)
assert spec and spec.loader
b0=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=b0
spec.loader.exec_module(b0)


def _params(area=None,fs=48000.):
    return b0.parameters_from_area(b0.M0_AREA if area is None else area,fs=fs)


def test_m0_physical_coefficients_are_derived():
    p=_params()
    assert math.isclose(p.radius_m,.016,rel_tol=1e-12)
    assert math.isclose(p.inertance_pa_s2_m3,20.43310536787145,rel_tol=1e-12)
    assert math.isclose(p.tau_s,2.7477486766091486e-5,rel_tol=1e-12)
    assert math.isclose(p.resistance_pa_s_m3,743630.7964339324,rel_tol=1e-12)
    assert math.isclose(p.zc_pa_s_m3,516047.4689955415,rel_tol=1e-12)
    assert math.isclose(p.inertance_pa_s2_m3/p.zc_pa_s_m3,
                        8*p.radius_m/(3*math.pi*p.c_m_s),rel_tol=1e-13)


@pytest.mark.parametrize("v",[0.,-1.,float("nan"),float("inf"),-float("inf"),True])
def test_reject_unphysical_area(v):
    with pytest.raises(ValueError):
        b0.parameters_from_area(v)


@pytest.mark.parametrize("name,bad",[("rho",0.),("c",-343.),("fs",float("inf"))])
def test_reject_invalid_air_or_clock(name,bad):
    kw={name:bad}
    with pytest.raises(ValueError):
        b0.parameters_from_area(b0.M0_AREA,**kw)


def test_resistance_cannot_be_adjusted_like_an_eq_knob():
    p=_params()
    with pytest.raises(ValueError):
        replace(p,resistance_pa_s_m3=-1.)
    with pytest.raises(ValueError):
        replace(p,resistance_pa_s_m3=p.resistance_pa_s_m3*1.05)


def test_zero_must_give_zero_from_empty_storage():
    tr=b0.run_trace(_params(),np.zeros(64))
    assert np.array_equal(tr,np.zeros_like(tr))


def test_nonzero_stored_air_responds_with_zero_incident():
    p=_params()
    tr=b0.run_trace(p,np.zeros(100),initial_q=1e-6)
    assert tr[0,1]!=0.
    assert tr[0,8]<0. # the stored energy returns power into the acoustic wave
    assert np.all(np.diff(tr[:,5])<=1e-19)
    b0.trace_energy_gate(tr)


def test_causality_no_future_ahead_of_current_wave():
    p=_params()
    a=np.zeros(160); a[55]=2.;a[150]=-2.
    b=a.copy();b[150]=8.
    ta=b0.run_trace(p,a)
    tb=b0.run_trace(p,b)
    assert np.array_equal(ta[:150],tb[:150])
    assert ta[150,1]!=tb[150,1]


def test_analytic_independence_and_continuous_positive_real():
    p=_params()
    g=b0.model_error_gate()
    assert g["max_complex_relative"]<=.055
    assert g["max_resistance_relative"]<=.11
    assert b0.analog_impedance(0.,p).item()==0.
    for sigma in (0,10,1000):
        for f in (0,200,1000,2600):
            assert b0.analog_impedance(sigma+2j*math.pi*f,p).real>=-1e-10
    assert -1/p.tau_s<0


@pytest.mark.parametrize("f",[200.,1000.,2600.])
def test_analytic_scattering_state_space_matches_bilinear(f):
    p=_params()
    assert abs(b0.independent_state_space_gamma(f,p) -
               b0.gamma_digital(f,p))<=1e-11
    measured,trace=b0.measure_gamma_by_least_squares(f,p)
    assert abs(measured-b0.gamma_digital(f,p))<=.002
    assert abs(b0.gamma_digital(f,p))<1.
    b0.trace_energy_gate(trace)


def test_reflection_is_not_fixed_volume_flow_pole():
    p=_params()
    lam=b0.scattering_pole(p)
    expected=(1+p.zc_pa_s_m3/p.resistance_pa_s_m3 -
              p.zc_pa_s_m3*p.h_s/(2*p.inertance_pa_s2_m3))
    expected/=(1+p.zc_pa_s_m3/p.resistance_pa_s_m3 +
              p.zc_pa_s_m3*p.h_s/(2*p.inertance_pa_s2_m3))
    assert abs(lam-expected)<1e-12
    assert abs(lam)<1
    forced_flow_pole=(1-p.h_s/(2*p.tau_s))/(1+p.h_s/(2*p.tau_s))
    assert abs(lam-forced_flow_pole)>.1


def test_each_step_energy_and_seeded_random():
    p=_params()
    incoming=np.random.default_rng(48017).normal(size=500)
    trace=b0.run_trace(p,incoming)
    metrics=b0.trace_energy_gate(trace)
    assert metrics["total_resistance_dissipation_j"]>0
    assert np.all(trace[:,7]>=0)
    # Independent recomputation using complete past-state flow and pressure.
    for i in (0,1,2,25,250,499):
        e_before=0 if i==0 else trace[i-1,5]
        e_after=trace[i,5]
        diff=e_after-e_before
        rhs=p.h_s*trace[i,2]*trace[i,3]
        dissip=p.h_s*trace[i,2]**2/p.resistance_pa_s_m3
        assert abs(rhs-diff-dissip)<=1e-9*max(abs(rhs),abs(diff),abs(dissip),1e-20)


def test_clock_converges_to_analog_when_sample_rate_doubles():
    p48=_params(fs=48000.)
    p96=_params(fs=96000.)
    da=abs(b0.gamma_digital(1000.,p48)-b0.gamma_analog(1000.,p48))
    db=abs(b0.gamma_digital(1000.,p96)-b0.gamma_analog(1000.,p96))
    assert 0<db<=.35*da


def test_3000hz_out_of_registered_domain_for_real_m0():
    p=_params()
    assert 2*math.pi*3000*p.radius_m/p.c_m_s>.8
    assert 2*math.pi*2600*p.radius_m/p.c_m_s<=.8


def test_real_cc_a2_m0_prepared_binding():
    _,area,length=b0.validated_m0_geometry()
    assert len(area)==len(length)==16
    assert math.isclose(float(area[-1]),b0.M0_AREA,rel_tol=1e-12)


def test_complex_reference_arrays_retained_without_rounding():
    z=b0.exact_piston_normalized(b0.ORACLE_KA)
    raw=b0._npy_bytes(z)
    stored=np.load(io.BytesIO(raw),allow_pickle=False)
    assert np.array_equal(stored,z)


def test_disallow_nonfinite_wave_and_initial_state():
    p=_params()
    with pytest.raises(ValueError):
        b0.BaffledRadiationOnePort(p,initial_q_m3_s=float("nan"))
    with pytest.raises(ValueError):
        b0.BaffledRadiationOnePort(p).step(float("inf"))
    with pytest.raises(ValueError):
        b0.run_trace(p,np.array([1.,float("nan")]))
