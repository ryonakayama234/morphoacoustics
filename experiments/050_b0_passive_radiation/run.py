"""SA-2B/B0 — physical fixed-aperture passive acoustic one-port (research only).

This is a small-signal scattering TERMINATION, not a waveform filter, a
real-mouth/nearfield microphone model, or a coupled time-domain vocal tract.
Gate-A prerequisite: docs/research/sa-2b-b0/GATE_A.md, commit 64a11695.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import io
import json
import math
from pathlib import Path
import runpy

import numpy as np
from scipy.special import j1, struve

ROOT = Path(__file__).resolve().parents[2]
RHO = 1.21
SOUND_C = 343.0
SAMPLE_HZ = 48000.0
M0_AREA = 0.000804247719318987
ORACLE_KA = np.array([.02,.1,.29309,.55,.8],dtype=np.float64)
PREREG = "64a116950117a161f69b1b9831c733b9343db444"
PIN_MAIN = "6869cfec04041393eae44485ce2fc91f002114f5"
PIN_SA2A = "6eca7a250e30de8d758087dad83d5f02a1301f38"
TRACE_COLUMNS = ("a_in_Pa","b_out_Pa","p_mid_Pa","U_mid_m3_s",
                 "q_next_m3_s","stored_E_J","delta_E_J",
                 "resistor_D_J","incident_net_work_J","balance_residual_J")


def finite_positive(name: str, number: float) -> float:
    if isinstance(number, (bool,np.bool_)):
        raise ValueError(f"{name} must be a positive physical number")
    try:
        value=float(number)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError(f"{name} must be a positive physical number") from exc
    if not math.isfinite(value) or value<=0.:
        raise ValueError(f"{name} must be positive and finite")
    return value


@dataclass(frozen=True)
class PortCoefficients:
    """Immutable morphology-derived physical parameters; no gain/EQ knobs."""
    area_m2: float
    rho_kg_m3: float
    c_m_s: float
    sample_rate_hz: float
    radius_m: float
    zc_pa_s_m3: float
    inertance_pa_s2_m3: float
    resistance_pa_s_m3: float
    tau_s: float
    h_s: float

    def __post_init__(self) -> None:
        for name in ("area_m2","rho_kg_m3","c_m_s","sample_rate_hz",
                     "radius_m","zc_pa_s_m3","inertance_pa_s2_m3",
                     "resistance_pa_s_m3","tau_s","h_s"):
            finite_positive(name, getattr(self,name))
        # Disallow direct modifications to R or M outside anatomical inference.
        target = parameters_from_area(self.area_m2,
                     rho=self.rho_kg_m3,c=self.c_m_s,fs=self.sample_rate_hz,
                     _check=False)
        for name in ("radius_m","zc_pa_s_m3","inertance_pa_s2_m3",
                     "resistance_pa_s_m3","tau_s","h_s"):
            if not math.isclose(getattr(self,name),getattr(target,name),
                                rel_tol=2e-14,abs_tol=0):
                raise ValueError(f"{name} cannot be tuned independently from anatomy")


def parameters_from_area(area_m2: float, *,rho:float=RHO,
                         c:float=SOUND_C,fs:float=SAMPLE_HZ,
                         _check:bool=True)->PortCoefficients:
    s=finite_positive("lip area",area_m2)
    rho=finite_positive("rho",rho)
    c=finite_positive("c",c)
    fs=finite_positive("sample rate",fs)
    a=math.sqrt(s/math.pi)
    zc=rho*c/s
    m=8*rho*a/(3*math.pi*s)
    tau=3*math.pi*a/(16*c)
    resistor=m/tau
    h=1/fs
    values=(a,zc,m,tau,resistor,h)
    if not all(math.isfinite(v) and v>0 for v in values):
        raise ValueError("singular/nonfinite radiation circuit")
    # Bypass __post_init__ recursion with private constructor, but verify on public path.
    value=object.__new__(PortCoefficients)
    for name,v in zip(PortCoefficients.__dataclass_fields__,
        (s,rho,c,fs,a,zc,m,resistor,tau,h),strict=True):
        object.__setattr__(value,name,v)
    if _check: value.__post_init__()
    return value


def analog_impedance(s:complex|np.ndarray,p:PortCoefficients)->np.ndarray:
    val=np.asarray(s,dtype=np.complex128)
    if not (np.isfinite(val.real).all() and np.isfinite(val.imag).all()):
        raise ValueError("nonfinite Laplace parameter")
    with np.errstate(invalid="raise",divide="raise",over="raise"):
        z=p.inertance_pa_s2_m3*val/(1+p.tau_s*val)
    return np.asarray(z,dtype=np.complex128)


def gamma_analog(f_hz:float,p:PortCoefficients)->complex:
    f=float(f_hz)
    if not math.isfinite(f) or f<0: raise ValueError("invalid f")
    z=complex(analog_impedance(2j*math.pi*f,p))
    return (z-p.zc_pa_s_m3)/(z+p.zc_pa_s_m3)


def gamma_digital(f_hz:float,p:PortCoefficients)->complex:
    f=float(f_hz)
    if not math.isfinite(f) or not (0<=f<p.sample_rate_hz/2):
        raise ValueError("outside discrete physical clock")
    ss=2j/p.h_s*math.tan(math.pi*f/p.sample_rate_hz)
    z=complex(analog_impedance(ss,p))
    return (z-p.zc_pa_s_m3)/(z+p.zc_pa_s_m3)


def scattering_pole(p:PortCoefficients)->float:
    alpha=p.zc_pa_s_m3/p.resistance_pa_s_m3
    beta=p.zc_pa_s_m3*p.h_s/(2*p.inertance_pa_s2_m3)
    return (1+alpha-beta)/(1+alpha+beta)


def independent_state_space_gamma(f_hz:float,p:PortCoefficients)->complex:
    """Second derivation directly from one-step state-space, not bilinear Z."""
    k=1+p.zc_pa_s_m3/p.resistance_pa_s_m3
    k+=p.zc_pa_s_m3*p.h_s/(2*p.inertance_pa_s2_m3)
    lam=1-p.h_s*p.zc_pa_s_m3/(p.inertance_pa_s2_m3*k)
    forcing=2*p.h_s/(p.inertance_pa_s2_m3*k)
    z=complex(np.exp(2j*np.pi*f_hz/p.sample_rate_hz))
    return complex((2/k-1)-(p.zc_pa_s_m3/k)*forcing/(z-lam))


@dataclass(frozen=True)
class StepResult:
    incident_pa:float
    reflected_pa:float
    pressure_pa:float
    volume_flow_m3_s:float
    inertial_flow_m3_s:float
    stored_energy_j:float
    delta_energy_j:float
    resistance_dissipation_j:float
    net_incident_work_j:float
    energy_balance_residual_j:float


class BaffledRadiationOnePort:
    """One-port discrete passive reflection: strictly causal, fixed geometry."""
    def __init__(self,parameters:PortCoefficients,*,initial_q_m3_s:float=0.):
        self.parameters=parameters
        self.q_m3_s=float(initial_q_m3_s)
        if not math.isfinite(self.q_m3_s): raise ValueError("invalid initial state")
        self.integrated_dissipation_j=0.
        self.integrated_port_work_j=0.
        self.steps=0

    def step(self,incident_pa:float)->StepResult:
        a=float(incident_pa)
        if not math.isfinite(a):raise ValueError("invalid incident wave")
        p=self.parameters
        q_old=self.q_m3_s
        e_old=.5*p.inertance_pa_s2_m3*q_old*q_old
        denom=1+p.zc_pa_s_m3/p.resistance_pa_s_m3
        denom+=p.zc_pa_s_m3*p.h_s/(2*p.inertance_pa_s2_m3)
        pmid=(2*a-p.zc_pa_s_m3*q_old)/denom
        qnew=q_old+p.h_s*pmid/p.inertance_pa_s2_m3
        qmid=.5*(q_old+qnew)
        u=qmid+pmid/p.resistance_pa_s_m3
        b=pmid-a
        enew=.5*p.inertance_pa_s2_m3*qnew*qnew
        delta_e=enew-e_old
        d=p.h_s*pmid*pmid/p.resistance_pa_s_m3
        work=p.h_s*(a*a-b*b)/p.zc_pa_s_m3
        residual=work-delta_e-d
        fields=(pmid,qnew,u,b,enew,delta_e,d,work,residual)
        if not all(math.isfinite(v) for v in fields):
            raise FloatingPointError("nonfinite passive radiation step")
        if d<0:raise AssertionError("negative radiation dissipation")
        self.q_m3_s=qnew
        self.integrated_dissipation_j+=d
        self.integrated_port_work_j+=work
        self.steps+=1
        return StepResult(a,b,pmid,u,qnew,enew,delta_e,d,work,residual)


def run_trace(p:PortCoefficients,incident:np.ndarray,initial_q:float=0.)->np.ndarray:
    values=np.asarray(incident,dtype=np.float64)
    if values.ndim!=1 or not np.isfinite(values).all():
        raise ValueError("incident must be a finite 1D sample stream")
    port=BaffledRadiationOnePort(p,initial_q_m3_s=initial_q)
    result=np.empty((values.size,len(TRACE_COLUMNS)),dtype=np.float64)
    for i,a in enumerate(values):
        step=port.step(float(a))
        result[i]=(step.incident_pa,step.reflected_pa,step.pressure_pa,
                   step.volume_flow_m3_s,step.inertial_flow_m3_s,
                   step.stored_energy_j,step.delta_energy_j,
                   step.resistance_dissipation_j,step.net_incident_work_j,
                   step.energy_balance_residual_j)
    return result


def trace_energy_gate(trace:np.ndarray)->dict[str,float]:
    q=trace
    work=q[:,8]
    delta=q[:,6]
    diss=q[:,7]
    residual=work-delta-diss
    tolerance=1e-9*np.maximum.reduce((abs(work),abs(delta),abs(diss),
                                      np.full(work.shape,1e-20)))
    if not np.all(abs(residual)<=tolerance):
        raise AssertionError("per-step power identity failed")
    cumulative=float(abs(np.sum(residual)))
    cumtol=1e-9*max(float(np.sum(abs(work))),1e-20)
    if cumulative>cumtol:raise AssertionError("cumulative energy conservation failed")
    if np.any(diss< -1e-20) or np.any(q[:,5]<0):
        raise AssertionError("nonpassive radiation energy")
    return {"max_step_normalized_residual":float(np.max(abs(residual)/tolerance)),
            "cumulative_absolute_residual_j":cumulative,
            "cumulative_abs_port_work_j":float(np.sum(abs(work))),
            "total_resistance_dissipation_j":float(np.sum(diss))}


def exact_piston_normalized(x:np.ndarray)->np.ndarray:
    xx=np.asarray(x,dtype=np.float64)
    if not np.isfinite(xx).all() or np.any(xx<=0):
        raise ValueError("exact comparison requires ka>0")
    return (1-j1(2*xx)/xx)+1j*struve(1,2*xx)/xx


def rl_normalized(x:np.ndarray)->np.ndarray:
    xx=np.asarray(x,dtype=np.float64)
    a=8*xx/(3*np.pi)
    b=3*np.pi*xx/16
    return 1j*a/(1+1j*b)


def model_error_gate()->dict[str,object]:
    exact=exact_piston_normalized(ORACLE_KA)
    reduced=rl_normalized(ORACLE_KA)
    ce=np.abs(reduced-exact)/np.abs(exact)
    re=np.abs(reduced.real-exact.real)/exact.real
    if max(ce)>0.055 or max(re)>0.11:raise AssertionError("model error budget")
    return {"ka":ORACLE_KA.tolist(),
            "complex_relative":ce.tolist(),
            "resistance_relative":re.tolist(),
            "max_complex_relative":float(max(ce)),
            "max_resistance_relative":float(max(re))}


def validated_m0_geometry()->tuple[object,np.ndarray,np.ndarray]:
    sv=runpy.run_path(str(ROOT/"experiments/042_sv1_sustained_vowel/run.py"))
    _,_,resolution=sv["_validated_context"]()
    geometry=resolution.preset.prepared.rest_state
    a=np.array([v.area_m2 for v in geometry.sections],dtype=np.float64)
    length=np.array([v.length_m for v in geometry.sections],dtype=np.float64)
    if a.size!=16 or not math.isclose(float(a[-1]),M0_AREA,rel_tol=1e-12,abs_tol=0.):
        raise AssertionError("authenticated original M0 geometry mismatch")
    return geometry,a,length


def measure_gamma_by_least_squares(f:float,p:PortCoefficients)->tuple[complex,np.ndarray]:
    n=int(round(.2*p.sample_rate_hz))
    t=np.arange(n)
    omega=2*np.pi*f/p.sample_rate_hz
    a=np.sin(omega*t)
    trace=run_trace(p,a)
    select=t>=256
    basis=np.column_stack((np.cos(omega*t[select]),np.sin(omega*t[select])))
    # Independent least-squares fit to real cos/sin steady-state output.
    a_coef=np.linalg.lstsq(basis,a[select],rcond=None)[0]
    b_coef=np.linalg.lstsq(basis,trace[select,1],rcond=None)[0]
    a_hat=complex(a_coef[0],-a_coef[1])
    b_hat=complex(b_coef[0],-b_coef[1])
    return b_hat/a_hat,trace


def _npy_bytes(x:np.ndarray)->bytes:
    f=io.BytesIO()
    np.save(f,np.asarray(x),allow_pickle=False)
    return f.getvalue()


def experiment(out:Path)->dict[str,object]:
    if out.exists():raise FileExistsError("never overwrite prior evidence")
    geometry,areas,lengths=validated_m0_geometry()
    p=parameters_from_area(float(areas[-1]))
    err=model_error_gate()
    # Cross-check analytic passive certificate on Re(s)>=0 sample grid.
    z_pos=[]
    for sigma in (0.,10.,1000.):
        for f in (0.,200.,1000.,2600.):
            z_pos.append(float(np.real(analog_impedance(sigma+2j*np.pi*f,p))))
    if min(z_pos)<-1e-10 or p.tau_s<=0:
        raise AssertionError("positive-real analytic grid failed")
    if analog_impedance(0.,p).item()!=0:
        raise AssertionError("nonzero DC")
    pole=scattering_pole(p)
    tustin=(1-p.h_s/(2*p.tau_s))/(1+p.h_s/(2*p.tau_s))
    if abs(pole)>=1 or pole==tustin:
        raise AssertionError("wrong passive recurrence pole")
    # Independent pole reference: apply unforced a=0 to nonzero initial q.
    first=BaffledRadiationOnePort(p,initial_q_m3_s=1e-6)
    first.step(0.)
    if abs(first.q_m3_s/(1e-6)-pole)>1e-12:
        raise AssertionError("scattering pole in time domain")
    fs=int(p.sample_rate_hz)
    zero=run_trace(p,np.zeros(int(.2*fs)))
    if np.any(zero!=0):raise AssertionError("nonzero response to zero energy")
    impulse=np.zeros(int(.2*fs));impulse[0]=1.
    seed=np.random.default_rng(48017)
    noise=seed.standard_normal(int(.2*fs))
    noise=noise/np.sqrt(np.mean(noise*noise))
    traces={"zero_trace.npy":zero,"impulse_trace.npy":run_trace(p,impulse),
            "noise_trace.npy":run_trace(p,noise),
            "discharge_trace.npy":run_trace(p,np.zeros(int(.2*fs)),initial_q=1e-6)}
    for name,t in traces.items():
        trace_energy_gate(t)
        if name=="discharge_trace.npy" and np.any(np.diff(t[:,5])>1e-18):
            raise AssertionError("zero-input storage increased")
    signal_refs=[]
    transfer_gates=[]
    for f in (200.,1000.,2600.):
        gamma,trace=measure_gamma_by_least_squares(f,p)
        ref=gamma_digital(f,p)
        independent=independent_state_space_gamma(f,p)
        if abs(ref-independent)>1e-11 or abs(gamma-ref)>0.002:
            raise AssertionError(f"complex reflection mismatch at {f}Hz")
        trace_energy_gate(trace)
        traces[f"tone_{int(f)}Hz_trace.npy"]=trace
        signal_refs.append((gamma,ref,independent,gamma_analog(f,p)))
        transfer_gates.append({"frequency_hz":f,"ka":float(2*np.pi*f*p.radius_m/p.c_m_s),
              "empirical_gamma":{"re":gamma.real,"im":gamma.imag},
              "digital_gamma":{"re":ref.real,"im":ref.imag},
              "state_space_gamma":{"re":independent.real,"im":independent.imag},
              "analog_gamma":{"re":gamma_analog(f,p).real,"im":gamma_analog(f,p).imag},
              "empirical_abs_error":float(abs(gamma-ref)),
              "independent_analytic_abs_error":float(abs(ref-independent))})
    p96=parameters_from_area(float(areas[-1]),fs=96000.)
    error48=abs(gamma_digital(1000.,p)-gamma_analog(1000.,p))
    error96=abs(gamma_digital(1000.,p96)-gamma_analog(1000.,p96))
    if not (0<error96<=.35*error48):
        raise AssertionError("clock convergence failed")
    calibration=[]
    for radius in (.005,.010,.016):
        shape=parameters_from_area(np.pi*radius**2)
        if not math.isclose(shape.inertance_pa_s2_m3/shape.zc_pa_s_m3,
                            8*radius/(3*np.pi*SOUND_C),rel_tol=1e-13):
            raise AssertionError("inertance unit conversion")
        calibration.append({"radius_m":radius,"lip_area_m2":shape.area_m2,
           "Zc_pa_s_m3":shape.zc_pa_s_m3,
           "M_pa_s2_m3":shape.inertance_pa_s2_m3,
           "R_pa_s_m3":shape.resistance_pa_s_m3,"tau_s":shape.tau_s})
    if not np.isclose(p.radius_m,.016,rtol=1e-12):
        raise AssertionError("wrong physical M0")
    excluded=3000.
    if not 2*np.pi*excluded*p.radius_m/p.c_m_s>.8:
        raise AssertionError("must reject out-of-domain 3000Hz")
    traces["m0_areas_m2.npy"]=areas
    traces["m0_lengths_m.npy"]=lengths
    traces["reduction_exact_complex.npy"]=exact_piston_normalized(ORACLE_KA)
    traces["reduction_rl_complex.npy"]=rl_normalized(ORACLE_KA)
    traces["digital_reflection_complex.npy"]=np.array(signal_refs,dtype=np.complex128)
    # Record a separately normalized same-power drive at two different areas.
    power_calibration=[]
    for radius in (.005,.010):
        shape=parameters_from_area(np.pi*radius**2)
        incident_same_power=np.sqrt(shape.zc_pa_s_m3/p.zc_pa_s_m3)
        wave=run_trace(shape,np.array([1.,0.,0.]))
        wave_equal=run_trace(shape,np.array([incident_same_power,0.,0.]))
        trace_energy_gate(wave)
        trace_energy_gate(wave_equal)
        power_calibration.append({"radius_m":radius,
          "relative_incident_amplitude_for_equal_power":float(incident_same_power),
          "first_wave_reflection_same_pressure_pa":float(wave[0,1]),
          "first_wave_reflection_equal_power_pa":float(wave_equal[0,1])})
    out.mkdir(parents=True)
    sha={}
    for name,array in sorted(traces.items()):
        data=_npy_bytes(array)
        (out/name).write_bytes(data)
        sha[name]=hashlib.sha256(data).hexdigest()
    all_gates={name:trace_energy_gate(trace) for name,trace in traces.items()
               if name.endswith("_trace.npy")}
    result={"schema":"research.sa2b_b0.v0",
        "decision":"SA2B_BOUNDARY_VERIFIED_DUCT_PENDING","adoption":"NOT_ADOPTED",
        "b1_b2_b3":"NOT_RUN","vf1":"NOT_READY",
        "preregistration_commit":PREREG,"base_main_sha":PIN_MAIN,
        "sa2a_verified_source_sha":PIN_SA2A,
        "executed_git_sha":"VERIFY_VIA_EXACT_GITHUB_ACTIONS_RECEIPT",
        "source_model":"linear perturbation/parallel inertance+resistance, fixed flanged circular aperture",
        "clock_hz":fs,"m0_body":"prepared CC-A2 M0 /a/-like actual SV-1 strict binding",
        "m0_area_m2":p.area_m2,"m0_radius_m":p.radius_m,
        "m0_section_count":len(geometry.sections),
        "parameters":{"rho_kg_m3":p.rho_kg_m3,"c_m_s":p.c_m_s,
           "Zc_pa_s_m3":p.zc_pa_s_m3,
           "inertance_pa_s2_m3":p.inertance_pa_s2_m3,
           "R_pa_s_m3":p.resistance_pa_s_m3,"tau_s":p.tau_s,
           "time_step_s":p.h_s},
        "continuous_min_Re_Z_pa_s_m3":min(z_pos),
        "continuous_impedance_pole_s_1":-1/p.tau_s,
        "scattering_discrete_pole":pole,
        "fixed_flow_tustin_pole_DIFFERENT":tustin,
        "model_error":err,"energy_gates":all_gates,
        "frequency_transfer":transfer_gates,
        "clock_convergence":{"at_hz":1000,"error_48k":error48,
                             "error_96k":error96,"error_ratio":error96/error48},
        "synthetic_calibration_radii":calibration,
        "same_pressure_vs_same_power":power_calibration,
        "excluded_3000Hz":{"reason":"M0 ka>0.8 SA-2A physical domain",
            "ka":float(2*np.pi*3000*p.radius_m/p.c_m_s)},
        "trace_columns":TRACE_COLUMNS,"artifact_sha256":sha}
    (out/"manifest.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",
                                   encoding="utf-8")
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    config=ap.parse_args()
    result=experiment(config.out)
    print(json.dumps({"decision":result["decision"],
                      "model_error":result["model_error"],
                      "clock_convergence":result["clock_convergence"],
                      "frequency_transfer":result["frequency_transfer"],
                      "scattering_discrete_pole":result["scattering_discrete_pole"]},
                     indent=2,sort_keys=True))
