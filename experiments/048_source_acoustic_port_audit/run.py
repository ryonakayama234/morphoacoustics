"""SA-1: audited glottal volume-flow -> tract -> radiation port reconstruction.

Experiment-local only. The inherited real Core pressure renderer is unchanged.
Frequency-domain port variables are algebraic reconstructions, NOT FSI states.
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, runpy
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SR=48000
N=24000
FROZEN_JET_SHA="9a79fa616e280de24daab5bfbe3cce57fda92256"
CASES={"noise_off":(800.,0.,0.),"modal":(800.,0.,.02),
       "breathy_gap":(800.,.15e-6,.02),"pressure_x2":(1600.,0.,.02)}
OLD_FRACTION={"noise_off":.0005240323048667825,"modal":.8075755574998604,
              "breathy_gap":.8614920631830499,"pressure_x2":.9364001042145957}
OLD_SOURCE_SHA={
 "noise_off":"0a6aeba10600837c3b9795afb35f18d3a03ed25212779cf9b9042fd7fc920544",
 "modal":"bec8047b9ff4583c5cec3c183f0e78604c7e47d7b2fdc3cc945db96d0a40077c",
 "breathy_gap":"0ac4c951afe466f513757bf313b49e146087f753c989bd197a15be77f187040c",
 "pressure_x2":"5abb4844b4dff8ddbd504059cc38e2a31a9c9ad09359e6201208cd98927d700b",
}

def npy(x):
    b=io.BytesIO()
    np.save(b,np.asarray(x),allow_pickle=False)
    return b.getvalue()

def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x)**2)))

def high(x,*,steady=False):
    x=np.asarray(x)[2400:21600] if steady else np.asarray(x)
    f=np.fft.rfftfreq(x.size,1/SR)
    p=np.abs(np.fft.rfft(x))**2
    return float(np.sum(p[f>=2000])/np.sum(p)) if np.sum(p)>0 else 0.

def stats(x):
    return {"rms":rms(x),"above_2khz_full":high(x),"above_2khz_steady":high(x,steady=True)}

def replay_source(pressure_pa,leak_m2,noise_fraction,*,seed=47001,count=N):
    """Exact numerical sequence of frozen JET-P0 source, with SHA check afterward.
    Its jet/Reynolds law is hypothetical, not experimentally calibrated.
    """
    if (not all(math.isfinite(z) for z in (pressure_pa,leak_m2,noise_fraction))
        or min(pressure_pa,leak_m2,noise_fraction)<0
        or type(seed) is not int or count<960):
        raise ValueError("invalid replay controls")
    phase=np.mod(np.arange(count,dtype=np.float64)*(100./SR),1.)
    aperture=np.zeros(count,dtype=np.float64)
    opened=phase<.6
    aperture[opened]=np.sin(np.pi*phase[opened]/.6)**2
    area=leak_m2+1e-6*aperture
    velocity=.6*math.sqrt(2.*pressure_pa/1.2)
    flow=area*velocity
    re=1.2*velocity*1e-3/1.8e-5
    gate=max(0.,1.-1000./re) if re>0 else 0.
    corner=velocity/(2.*math.pi*2e-3) if velocity>0 else 0.
    decay=math.exp(-2.*math.pi*corner/SR)
    xi=np.random.default_rng(seed).standard_normal(count)
    colored=np.empty(count,dtype=np.float64)
    prev=0.
    diffusion=math.sqrt(max(0.,1.-decay*decay))
    for i in range(count):
        prev=decay*prev+diffusion*xi[i]
        colored[i]=prev
    ramp=int(.01*SR)
    env=np.ones(count,dtype=np.float64)
    fade=np.sin(np.arange(ramp)*(.5*np.pi/ramp))**2
    env[:ramp]*=fade
    env[-ramp:]*=fade[::-1]
    mean=flow*env
    residue=noise_fraction*gate*flow*colored*env
    return mean+residue,mean,residue

def matched_oracle():
    """Independent matched, lossless uniform-tube analytic oracle."""
    from morphoacoustics.acoustics.uniform_tube import UniformTube
    t=UniformTube(length_m=.17,area_m2=3e-4,
                  sound_speed_m_s=343.,air_density_kg_m3=1.21)
    f=np.array([100.,500.,1000.,2000.,4000.])
    a=t.transfer_matrix(f)
    zc=t.characteristic_impedance_pa_s_m3
    A,B,C,D=a[:,0,0],a[:,0,1],a[:,1,0],a[:,1,1]
    tu=1./(C*zc+D)
    zin=(A*zc+B)/(C*zc+D)
    expected=np.exp(-1j*2.*np.pi*f*.17/343.)
    e_u=float(np.max(np.abs(tu-expected)))
    e_z=float(np.max(np.abs(zin/zc-1.)))
    if not (e_u<1e-10 and e_z<1e-10): raise AssertionError(("uniform_oracle",e_u,e_z))
    return {"flow_complex_abs_error":e_u,"zin_relative_error":e_z,
            "matched_zc_pa_s_m3":zc}

def ports(exp9,geometry,f):
    """p_g, p_lips, U_lips derived from Exp009 two-port; not measured CFD."""
    t=exp9.lossy_transfer_matrix(geometry,f)
    A,B,C,D=t[...,0,0],t[...,0,1],t[...,1,0],t[...,1,1]
    zc=exp9.AIR_DENSITY_KG_M3*exp9.SOUND_SPEED_M_S/geometry.sections[-1].area_m2
    zl=exp9.LOAD_FRACTION_OF_OUTLET_ZC*zc
    denom=C*zl+D
    if np.any(~np.isfinite(denom)) or np.any(abs(denom)<1e-12):
        raise AssertionError("singular or nonfinite acoustic boundary")
    tu=1./denom
    zin=(A*zl+B)/denom
    omega=2.*np.pi*f
    radiation=1j*omega*exp9.AIR_DENSITY_KG_M3/(4.*np.pi*exp9.OBSERVATION_DISTANCE_M)*np.exp(
        -1j*omega*exp9.OBSERVATION_DISTANCE_M/exp9.SOUND_SPEED_M_S)
    radiation=np.asarray(radiation,dtype=np.complex128)
    radiation[f==0.]=0.
    actual_tu=exp9.outlet_volume_velocity_transfer(geometry,f)
    actual_total=exp9.far_field_pressure_transfer(geometry,f)
    err=max(float(np.max(abs(actual_tu-tu)/np.maximum(1.,abs(tu)))),
            float(np.max(abs(actual_total-tu*radiation)/np.maximum(1.,abs(tu*radiation)))))
    if not np.isfinite(err) or err>=1e-10: raise AssertionError(("transfer_identity",err))
    return {"tube":tu,"radiation":radiation,"total":tu*radiation,
            "zin":zin,"zload":np.full(f.shape,zl,dtype=np.complex128),
            "identity_error":err}

def separated_frame(exp12,exp9,geom,source,stage):
    # Each stage applies to ORIGINAL U_in with same OLA. Never cascade two OLA
    # operations and describe the result as physical mouth radiation.
    def tr(_time,f):return ports(exp9,geom,f)[stage]
    return exp12.frame_render(source,tr,hop_size=256,edge_mode="preroll_edge")

def execute(output_dir):
    output_dir=Path(output_dir)
    if output_dir.exists():raise FileExistsError("refusing to overwrite research output")
    oracle=matched_oracle()
    sv1=runpy.run_path(str(ROOT/"experiments/042_sv1_sustained_vowel/run.py"))
    _,exp,resolution=sv1["_validated_context"]()
    geom=resolution.preset.prepared.rest_state
    exp23=exp.EXP26.EXP23
    exp9,exp12=exp23.EXP9,exp23.EXP12
    if exp9.SAMPLE_RATE_HZ!=SR or exp12.DEFAULT_HOP_SIZE!=256:
        raise RuntimeError("frozen physics sampling/hop mismatch")
    src={name:replay_source(*values) for name,values in CASES.items()}
    for name,(s,_,__) in src.items():
        if hashlib.sha256(npy(s)).hexdigest()!=OLD_SOURCE_SHA[name]:
            raise AssertionError("JET source byte provenance changed "+name)

    p={name:sv1["_render"](exp,geom,v[0]) for name,v in src.items()}
    mean,noise=src["modal"][1:]
    pmean=sv1["_render"](exp,geom,mean)
    pnoise=sv1["_render"](exp,geom,noise)
    pnull=exp23.render_static(np.zeros(N,dtype=np.float64),geom)
    assert not np.any(pnull)
    rel=rms(p["modal"]-pmean-pnoise)/max(rms(p["modal"]),rms(pmean),rms(pnoise))
    if rel>=1e-10:raise AssertionError(("linearity",rel))
    historic={}
    for name,pressure in p.items():
        ratio=high(pressure)
        if abs(ratio-OLD_FRACTION[name])>=1e-4:
            raise AssertionError(("historic_JET_P0",name,ratio,OLD_FRACTION[name]))
        historic[name]={"old":OLD_FRACTION[name],"recomputed":ratio,
                         "source_npy_sha256":OLD_SOURCE_SHA[name]}

    frame_f=np.fft.rfftfreq(1024,1./SR)
    response=ports(exp9,geom,frame_f)
    # Peak-phasor acoustic power coefficients normalized by |U_in|^2.
    # Both powers use their OWN matched pressure/flow port, not farfield Pa^2.
    # The resistive load and lossy tube should not create passive port power.
    inlet_power_coeff=.5*np.real(response["zin"])
    outlet_power_coeff=.5*np.real(response["zload"])*np.abs(response["tube"])**2
    dissipated_coeff=inlet_power_coeff-outlet_power_coeff
    if (np.any(inlet_power_coeff < -1e-8)
        or np.any(outlet_power_coeff < -1e-8)
        or np.any(dissipated_coeff < -1e-8)):
        raise AssertionError("acoustic two-port passivity oracle failed")
    # Check the declared monopole observation gain grows precisely with f.
    rad_reference=ports(exp9,geom,np.array([1000.,3000.]))["radiation"]
    rad_gain_ratio=float(np.abs(rad_reference[1])/np.abs(rad_reference[0]))
    if abs(rad_gain_ratio-3.)>1e-12:
        raise AssertionError(("monopole frequency gain law",rad_gain_ratio))
    lip={name:separated_frame(exp12,exp9,geom,src[name][0],"tube") for name in CASES}
    rad_only=separated_frame(exp12,exp9,geom,src["modal"][0],"radiation")
    # Independent same-source renderer sensitivity to finite OLA hop.
    def render_alt(hop):
        return exp12.frame_render(src["modal"][0],
            lambda _t,f: exp9.far_field_pressure_transfer(geom,f),
            hop_size=hop,edge_mode="preroll_edge")
    hop128=render_alt(128)
    hop_sensitivity={"original_hop256_highband":high(p["modal"]),
                     "hop128_highband":high(hop128),
                     "relative_pressure_rms_difference":rms(hop128-p["modal"])/rms(p["modal"])}
    calibrations={}
    for hz in (200,1000,3000):
        t=np.arange(N,dtype=np.float64)/SR
        u=math.sqrt(2.)*1e-6*np.sin(2*np.pi*hz*t)
        pr=exp23.render_static(u,geom)
        calibrations[str(hz)]={"inlet_rms_m3_s":rms(u[2400:21600]),
                               "observed_rms_pa":rms(pr[2400:21600]),
                               "gain_pa_s_m3":rms(pr[2400:21600])/rms(u[2400:21600])}

    # Exact algebraic per-frequency attribution (one full-record FFT).
    # Distinct from the real windowed OLA output.
    fft_f=np.fft.rfftfreq(N,1./SR)
    fq=ports(exp9,geom,fft_f)
    U=np.fft.rfft(src["modal"][0])
    M=np.fft.rfft(mean)
    V=np.fft.rfft(noise)
    def frac(spectrum):
        ps=abs(spectrum)**2
        return float(ps[fft_f>=2000].sum()/ps.sum()) if ps.sum()>0 else 0.
    decomposition={
        "inlet_full":frac(U),"mean_source":frac(M),"noise_only_source":frac(V),
        "lip_flow_ideal_full_fft":frac(U*fq["tube"]),
        "observer_ideal_full_fft":frac(U*fq["total"]),
        "radiation_only_ideal_full_fft":frac(U*fq["radiation"]),
        "real_core_observer_ola":high(p["modal"]),
        "noise_fraction_source_rms":rms(noise)/rms(src["modal"][0]),
        "observer_delta_to_noise_off_rms":rms(p["modal"]-p["noise_off"])/rms(p["noise_off"]),
    }
    # No source impedance is inferred from p_g/U_g: this is the tract input load.
    diagnostics={
        "uniform_matched_oracle":oracle,
        "zero_input_observer_rms_pa":rms(pnull),
        "fixed_tract_superposition_relative_error":rel,
        "transfer_identity_max_error":response["identity_error"],
        "passive_port_power_per_inlet_flow_peak2":{
            "minimum_inlet_coefficient":float(inlet_power_coeff.min()),
            "minimum_outlet_coefficient":float(outlet_power_coeff.min()),
            "minimum_internal_loss_coefficient":float(dissipated_coeff.min()),
            "unit":"Pa s / m3 (actual port power is coefficient times |U_in|^2)",
            "boundary_is_physical_lip_radiation":False,
        },
        "monopole_3khz_to_1khz_gain_ratio":rad_gain_ratio,
        "hop256_vs_hop128":hop_sensitivity,
        "jet_p0_original_reproduction":historic,
        "tone_calibration":calibrations,
        "band_attribution":decomposition,
        "cases":{name:{"inlet_flow":stats(src[name][0]),
                       "reconstructed_lip_flow":stats(lip[name]),
                       "real_core_observer_pa":stats(p[name])} for name in CASES},
        "radiation_only_on_original_inlet":stats(rad_only),
        "physics_limitation":"ZL=0.05 Zc resistor is separate from monopole observer; unified lip radiation impedance unvalidated.",
        "decision":"DIAGNOSIS_VERIFIED_REPAIR_REQUIRED",
    }
    output_dir.mkdir(parents=True)
    hashes={}
    def save(name,x):
        b=npy(x); (output_dir/name).write_bytes(b)
        hashes[name]=hashlib.sha256(b).hexdigest()
    for name in CASES:
        save(name+"_inlet_U_m3_s.npy",src[name][0])
        save(name+"_observer_pa.npy",p[name])
        save(name+"_lip_reconstruction_U_m3_s.npy",lip[name])
    save("modal_noise_inlet_U_m3_s.npy",noise)
    save("modal_mean_observer_pa.npy",pmean)
    save("modal_noise_observer_pa.npy",pnoise)
    save("modal_radiation_only_observer_pa.npy",rad_only)
    save("modal_hop128_actual_core_pa.npy",hop128)
    save("zero_observer_pa.npy",pnull)
    save("frame_frequencies_hz.npy",frame_f)
    for part in ("tube","radiation","total","zin","zload"):
        save("frame_"+part+"_complex.npy",response[part])
    data={"schema":"research.sa1.v0","status":"NUMERIC_DIAGNOSIS_REQUIRES_REVIEW",
          "adoption":"NOT_ADOPTED","base_main_sha":"6869cfec04041393eae44485ce2fc91f002114f5",
          "jet_source_sha":FROZEN_JET_SHA,
          "actual_sa1_head":"BIND_VIA_GITHUB_ACTIONS_RUN",
          "sample_rate_hz":SR,"duration_samples":N,
          "body":"adopted CC-A2 M0 prepared rest geometry via SV-1 preflight",
          "window":"1024 Hann OLA; hop 256; preroll_edge",
          "zload_fraction_zc":exp9.LOAD_FRACTION_OF_OUTLET_ZC,
          "observer_distance_m":exp9.OBSERVATION_DISTANCE_M,
          "unit_notes":"U:m3/s, p:Pa, Zin and radiation:Pa*s/m3; all port series except real observer p are computed reconstructions",
          "artifact_sha256":hashes,"diagnostics":diagnostics}
    (output_dir/"manifest.json").write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return data

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(execute(args.out)["diagnostics"],indent=2,sort_keys=True))
