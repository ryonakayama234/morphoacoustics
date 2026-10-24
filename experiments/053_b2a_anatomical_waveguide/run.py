"""SA-2B/B2-A — passive LOCAL waveguide across authentic prepared body sections.

Stationary 1D serial tract ONLY. The wave propagation and source/terminal p/U
conventions extend independently verified B1b; between sections, continuity
of p and U imposes power-unitary local wave scattering.

Frozen prerequisite: docs/research/sa-2b-b2a/GATE_A.md
commit 46fa9a4767886428c712c6aaff263965b0351480, before B2-A code.
No public Core/Studio modification, no native 48k audio, no moving walls.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import runpy
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PREREG = "46fa9a4767886428c712c6aaff263965b0351480"
RHO = 1.21
C = 343.
LIP_M0_A = 0.000804247719318987
REFERENCE = ROOT/"experiments/028_task_field_morphology_transfer/frozen_reference.json"
MODES = ("closed","pressure_release","matched","b0")
BODIES = ("M0_a","M1_a","M0_i")
FREQS = (200.,400.,600.,1000.,2600.)
TRACE_COLUMNS = (
    "time_s", "U_in_m3_s", "a_source_pa", "b_source_pa",
    "a_lip_pa", "b_lip_pa", "p_source_pa", "p_lip_pa", "U_lip_m3_s",
    "tube_energy_j", "B0_energy_j", "signed_source_work_j",
    "mouth_dissipation_j", "delta_total_energy_j", "residual_j",
)


def _b0_module():
    key="sa2b_b0_b2a_verified_original"
    if key not in sys.modules:
        path=ROOT/"experiments/050_b0_passive_radiation/run.py"
        spec=importlib.util.spec_from_file_location(key,path)
        if spec is None or spec.loader is None:
            raise RuntimeError("original B0 source missing")
        obj=importlib.util.module_from_spec(spec)
        sys.modules[key]=obj
        spec.loader.exec_module(obj)
    return sys.modules[key]


@dataclass(frozen=True)
class BodySections:
    """Provenance-aware section geometry, one prepared numerical body."""
    name: str
    preset_id: str
    preset_revision: int
    source: str
    lengths_m: tuple[float,...]
    areas_m2: tuple[float,...]

    def __post_init__(self):
        if len(self.lengths_m)!=16 or len(self.areas_m2)!=16:
            raise ValueError("B2-A requires exactly 16 serial physical sections")
        if not self.preset_id or not self.source or not self.name or self.preset_revision != 1:
            raise ValueError("body preset identity missing")
        if not all(math.isfinite(v) and v>0 for v in self.lengths_m+self.areas_m2):
            raise ValueError("invalid physical lengths or areas")
        if max(self.lengths_m)-min(self.lengths_m)>1e-12:
            raise ValueError("unequal section lengths need a separate time-grid gate")
        if len(set(round(v,14) for v in self.areas_m2))<3 and self.name in BODIES:
            raise ValueError("authentic shape lacks its frozen anatomical variation")

    @property
    def area_digest(self):
        raw=np.array(self.areas_m2,dtype="<f8").tobytes()
        return hashlib.sha256(raw).hexdigest()

    @property
    def total_length_m(self):
        return math.fsum(self.lengths_m)

    @property
    def lip_area_m2(self):
        return self.areas_m2[-1]


def prepared_bodies():
    """Resolve existing CC-A2 prepared v1 presets; never invent anatomy.

    M0/i is sourced from the frozen Exp028 alternative vowel shape and clearly
    identified as a REFERENCE SHAPE, not a separately registered body preset.
    """
    cc=runpy.run_path(str(ROOT/"tools/cc_a2_live.py"))
    frozen=cc["_load_frozen_adapter"]()
    exp=frozen._load_audited_experiment()
    registry=cc["prepared_registry"](exp)
    from morphoacoustics.integration.body_presets import CharacterBodyBinding, BindingStatus
    expected=json.loads(REFERENCE.read_text(encoding="utf-8"))["M0"]
    frozen_lengths=np.asarray(expected["section_lengths_m"],dtype=np.float64)
    frozen_a=np.asarray(expected["a_areas_m2"],dtype=np.float64)
    frozen_i=np.asarray(expected["i_areas_m2"],dtype=np.float64)
    result={}
    for key,preset in (("M0_a","v3b-axial-M0"),("M1_a","v3b-axial-M1")):
        resolution=registry.resolve(
            CharacterBodyBinding("b2a-anatomical-research",preset,1),
            required_backend_id=exp.TRACT1D_BACKEND_ID)
        if (resolution.status!=BindingStatus.BOUND or resolution.preset is None
                or resolution.snapshot is None):
            raise RuntimeError("original prepared CC-A2 body not bound: "+key)
        geometry=resolution.preset.prepared.rest_state
        lengths=np.array([v.length_m for v in geometry.sections],dtype=np.float64)
        areas=np.array([v.area_m2 for v in geometry.sections],dtype=np.float64)
        if (len(areas)!=16 or
            not np.array_equal(areas,frozen_a) or
            not np.allclose(lengths, frozen_lengths*(1.1 if key=="M1_a" else 1.),
                            rtol=0,atol=1e-12) or
            not resolution.snapshot.preparation_digest.startswith("sha256:")):
            raise RuntimeError("prepared body drift against frozen experiment 028")
        result[key]=BodySections(key,preset,1,
            "CC-A2 prepared registry / Experiment-028 frozen M0-a+M1-axis",
            tuple(float(v) for v in lengths),tuple(float(v) for v in areas))
    assert np.array_equal(np.array(result["M0_a"].areas_m2),
                          np.array(result["M1_a"].areas_m2))
    # Compare against the actual prepared M0/a before using reference M0/i.
    if not np.array_equal(np.array(result["M0_a"].lengths_m),frozen_lengths):
        raise RuntimeError("M0/frozen reference lengths drift")
    if np.array_equal(frozen_a,frozen_i):
        raise RuntimeError("two vowels' anatomy unexpectedly identical")
    result["M0_i"]=BodySections(
        "M0_i", "v3b-axial-M0",1,
        "Experiment028 frozen M0/i alternative; NOT separate body registry preset",
        tuple(float(v) for v in frozen_lengths),
        tuple(float(v) for v in frozen_i))
    return result


def _positive(name,value):
    if isinstance(value,(bool,np.bool_)):
        raise ValueError(name)
    try: x=float(value)
    except (ValueError,TypeError,OverflowError) as exc: raise ValueError(name) from exc
    if not math.isfinite(x) or x<=0: raise ValueError(name)
    return x


@dataclass(frozen=True)
class AcousticConfig:
    body: BodySections
    cells_per_section: int=2
    termination: str="b0"
    rho: float=RHO
    c: float=C

    def __post_init__(self):
        if not isinstance(self.body,BodySections):
            raise ValueError("validated prepared body required")
        if type(self.cells_per_section) is not int or self.cells_per_section not in (2,4,8):
            raise ValueError("unsupported spatial subdivision")
        if self.termination not in MODES:
            raise ValueError("unsupported mouth load")
        _positive("rho",self.rho)
        _positive("c",self.c)
        if not math.isfinite(self.fs_hz) or self.fs_hz<=0:
            raise ValueError("invalid physical clock")
        if self.body.total_length_m<=0:
            raise ValueError("invalid body length")

    @property
    def section_length_m(self):
        return self.body.lengths_m[0]

    @property
    def dx(self):
        return self.section_length_m/self.cells_per_section

    @property
    def fs_hz(self):
        return self.c/self.dx

    @property
    def h(self):
        return self.dx/self.c

    @property
    def one_way_s(self):
        return self.body.total_length_m/self.c

    @property
    def wave_cells(self):
        return 16*self.cells_per_section

    @property
    def z(self):
        return tuple(self.rho*self.c/a for a in self.body.areas_m2)


@dataclass(frozen=True)
class Step:
    time_s:float
    source_flow_m3_s:float
    source_out_pa:float
    source_in_pa:float
    lip_incident_pa:float
    lip_reflected_pa:float
    source_pressure_pa:float
    lip_pressure_pa:float
    lip_flow_m3_s:float
    tube_energy_j:float
    mouth_energy_j:float
    inlet_work_j:float
    outlet_loss_j:float
    delta_energy_j:float
    energy_residual_j:float


def passive_junction(a_left:float,b_right:float,z_left:float,z_right:float):
    """Return (b_left,a_right) pressure traveling waves at zero-volume junction."""
    z1=_positive("left impedance",z_left)
    z2=_positive("right impedance",z_right)
    if not all(math.isfinite(v) for v in (a_left,b_right)):
        raise ValueError("nonfinite incoming wave")
    denom=z1+z2
    if not math.isfinite(denom):
        raise ValueError("singular junction")
    reflect=(z2-z1)/denom
    b_left=reflect*a_left+(2*z1/denom)*b_right
    a_right=(2*z2/denom)*a_left-reflect*b_right
    if not all(math.isfinite(v) for v in (b_left,a_right)):
        raise FloatingPointError("junction generated nonfinite field")
    return b_left,a_right


class AnatomicalWaveguide:
    """Local two-sided delay queues for EVERY physical section (16x), B0 at lip."""

    def __init__(self,cfg:AcousticConfig,*,initial_forward_pa=None,
                 initial_backward_pa=None,initial_b0_q_m3_s:float=0.):
        self.cfg=cfg
        self.z=cfg.z
        self.junction_scatter=tuple(
            ((zr-zl)/(zl+zr),2*zl/(zl+zr),2*zr/(zl+zr))
            for zl,zr in zip(self.z[:-1],self.z[1:])
        )
        self.forward=[deque([0.]*cfg.cells_per_section) for _ in range(16)]
        self.backward=[deque([0.]*cfg.cells_per_section) for _ in range(16)]
        for name,initial,queues in (
            ("forward",initial_forward_pa,self.forward),
            ("backward",initial_backward_pa,self.backward),
        ):
            if initial is not None:
                vals=np.asarray(initial,dtype=np.float64)
                if vals.shape!=(16,cfg.cells_per_section) or not np.isfinite(vals).all():
                    raise ValueError("bad "+name+" initial state")
                for i,row in enumerate(vals):
                    queues[i].clear()
                    queues[i].extend(float(v) for v in row)
        if not math.isfinite(float(initial_b0_q_m3_s)):
            raise ValueError("bad B0 stored inertial flow")
        if cfg.termination!="b0" and initial_b0_q_m3_s!=0:
            raise ValueError("B0 state supplied to non-B0 mouth")
        self.port=None
        if cfg.termination=="b0":
            lib=_b0_module()
            params=lib.parameters_from_area(cfg.body.lip_area_m2,
                                             rho=cfg.rho,c=cfg.c,fs=cfg.fs_hz)
            self.port=lib.BaffledRadiationOnePort(params,
                                         initial_q_m3_s=float(initial_b0_q_m3_s))
        self.tick=0

    def energy(self):
        h=self.cfg.h
        z=self.cfg.z
        return h*sum(
            (sum(v*v for v in self.forward[i])+
             sum(v*v for v in self.backward[i]))/z[i] for i in range(16))

    def mouth_energy(self):
        if self.port is None:
            return 0.
        return .5*self.port.parameters.inertance_pa_s2_m3*self.port.q_m3_s**2

    def total_energy(self):
        return self.energy()+self.mouth_energy()

    def _advance(self,inlet_flow_m3_s:float,*,audit:bool):
        if isinstance(inlet_flow_m3_s,(bool,np.bool_)):
            raise ValueError("bool physical source")
        u=float(inlet_flow_m3_s)
        if not math.isfinite(u):
            raise ValueError("nonfinite inlet source")
        old=self.total_energy() if audit else 0.
        incoming_a=[q.popleft() for q in self.forward]
        incoming_b=[q.popleft() for q in self.backward]
        z=self.z
        out_a=[0.]*16
        out_b=[0.]*16
        out_a[0]=incoming_b[0]+z[0]*u
        for i,(reflection,left_to_right,right_to_left) in enumerate(self.junction_scatter):
            a,b=incoming_a[i],incoming_b[i+1]
            # Algebraically identical to independently tested passive_junction.
            out_b[i]=reflection*a+left_to_right*b
            out_a[i+1]=right_to_left*a-reflection*b
        mouth_a=incoming_a[15]
        if self.cfg.termination=="closed":
            mouth_b,loss,mouthE=mouth_a,0.,0.
        elif self.cfg.termination=="pressure_release":
            mouth_b,loss,mouthE=-mouth_a,0.,0.
        elif self.cfg.termination=="matched":
            mouth_b=0.
            loss=self.cfg.h*mouth_a*mouth_a/z[15]
            mouthE=0.
        else:
            v=self.port.step(mouth_a)
            mouth_b=v.reflected_pa
            mouthE=v.stored_energy_j
            loss=v.resistance_dissipation_j
        out_b[15]=mouth_b
        for i in range(16):
            self.forward[i].append(out_a[i])
            self.backward[i].append(out_b[i])
        self.tick+=1
        lip_pressure=mouth_a+mouth_b
        if not audit:
            return lip_pressure
        tubeE=self.energy()
        now=tubeE+mouthE
        work=self.cfg.h*(out_a[0]*out_a[0]-incoming_b[0]*incoming_b[0])/z[0]
        delta=now-old
        return Step((self.tick-1)*self.cfg.h,u,out_a[0],incoming_b[0],
             mouth_a,mouth_b,out_a[0]+incoming_b[0],lip_pressure,
             (mouth_a-mouth_b)/z[-1],tubeE,mouthE,work,loss,delta,
             delta-work+loss)

    def step(self,inlet_flow_m3_s):
        return self._advance(inlet_flow_m3_s,audit=True)

    def trace(self,inlet):
        values=np.asarray(inlet,dtype=np.float64)
        if values.ndim!=1 or not np.isfinite(values).all():
            raise ValueError("finite one-dimensional source stream required")
        a=np.empty((len(values),len(TRACE_COLUMNS)),dtype=np.float64)
        for i,v in enumerate(values):
            a[i,:]=tuple(vars(self.step(float(v))).values())
        return a

    def trace_with_states(self,inlet):
        """Archive every physical FIFO wave cell and B0 inertial state per tick.

        Unlike an energy column, these are independently re-integrable raw
        states. Returned in [tick, section, forward/backward, local cell] order.
        """
        values=np.asarray(inlet,dtype=np.float64)
        if values.ndim!=1 or not np.isfinite(values).all():
            raise ValueError("finite source required")
        rows=np.empty((len(values),len(TRACE_COLUMNS)),dtype=np.float64)
        states=np.empty((len(values),16,2,self.cfg.cells_per_section),dtype=np.float64)
        q=np.zeros(len(values),dtype=np.float64)
        for i,u in enumerate(values):
            rows[i,:]=tuple(vars(self.step(float(u))).values())
            for sec in range(16):
                states[i,sec,0,:]=tuple(self.forward[sec])
                states[i,sec,1,:]=tuple(self.backward[sec])
            if self.port is not None:
                q[i]=self.port.q_m3_s
        return rows,states,q

    def impulse_lip_pressure(self,length,amplitude_m3_s=1e-6):
        if type(length) is not int or length<=0 or not math.isfinite(amplitude_m3_s) or amplitude_m3_s==0:
            raise ValueError("invalid impulse")
        arr=np.empty(length,dtype=np.float64)
        for i in range(length):
            arr[i]=self._advance(amplitude_m3_s if i==0 else 0.,audit=False)
        return arr


def energy_gate(tr,initial_energy_j=0.):
    v=np.asarray(tr,dtype=np.float64)
    if v.ndim!=2 or v.shape[1]!=len(TRACE_COLUMNS) or not np.isfinite(v).all():
        raise ValueError("invalid B2-A SI trace")
    energy=v[:,9]+v[:,10]
    previous=np.r_[initial_energy_j,energy[:-1]]
    work,loss=v[:,11],v[:,12]
    delta=energy-previous
    residual=delta-work+loss
    bound=np.maximum(
        1e-9*np.maximum.reduce((abs(delta),abs(work),abs(loss),np.full(len(v),1e-20))),
        1e-12*np.maximum.reduce((previous,energy,np.full(len(v),1e-20))))
    if np.any(abs(residual)>bound) or np.any(loss<0) or np.any(energy<0):
        raise AssertionError("B2-A energy ledger violates passive port")
    if np.max(abs(residual-v[:,14]),initial=0.)>1e-17*max(1.,float(np.max(energy,initial=0.))):
        raise AssertionError("B2-A residual field was altered")
    cum=abs(float(sum(residual)))
    allowed=max(1e-9*max(float(sum(abs(work))+sum(loss)),1e-20),
                1e-10*max(initial_energy_j,float(np.max(energy,initial=0.)),1e-20))
    if cum>allowed:
        raise AssertionError("B2-A cumulative energy mismatch")
    return {"max_normalized_residual":float(np.max(abs(residual)/bound,initial=0.)),
            "cumulative_abs_residual_j":cum,
            "total_signed_source_work_j":float(sum(work)),
            "total_dissipation_j":float(sum(loss))}


def continuous_transfer(hz,cfg):
    """Independent continuous transfer via 2x2 p/U matrices, NOT local scatter."""
    f=_positive("frequency",hz)
    if cfg.termination!="b0":
        raise ValueError("continuous acoustic oracle requires B0")
    mat=np.eye(2,dtype=np.complex128)
    for length,z in zip(cfg.body.lengths_m,cfg.z):
        angle=2*math.pi*f*length/cfg.c
        cs=math.cos(angle)
        sn=math.sin(angle)
        sec=np.array([[cs,1j*z*sn],[1j*sn/z,cs]],dtype=np.complex128)
        mat=mat@sec
    b0=_b0_module().parameters_from_area(cfg.body.lip_area_m2,rho=cfg.rho,c=cfg.c,fs=cfg.fs_hz)
    zload=complex(_b0_module().analog_impedance(2j*math.pi*f,b0))
    return 1/(mat[1,0]+mat[1,1]/zload)


def empirical_transfer(pressure,cfg,f,source_impulse=1e-6):
    t=np.arange(len(pressure),dtype=np.float64)/cfg.fs_hz
    return complex(np.dot(np.asarray(pressure),np.exp(-2j*np.pi*f*t))/source_impulse)


def _npy(v):
    s=io.BytesIO()
    np.save(s,np.asarray(v),allow_pickle=False)
    return s.getvalue()


def experiment(out:Path):
    """Sample all three frozen bodies and all scales; immutable verifiable evidence."""
    if out.exists():
        raise FileExistsError("never overwrite physical evidence")
    # Reserve a new evidence folder BEFORE any audit can fail; stage data
    # incrementally and leave source-state evidence behind on scientific HOLD.
    out.mkdir(parents=True)
    (out/"RUN_STARTED.txt").write_text(
        "B2-A source experiment started; absence of RUN_COMPLETE means HOLD.\n")
    reference_bytes=REFERENCE.read_bytes()
    reference_git_blob=hashlib.sha1(
        b"blob "+str(len(reference_bytes)).encode("ascii")+b"\0"+reference_bytes
    ).hexdigest()
    if reference_git_blob!="7810dfbb72cb6c41af007db6e9d51c58cad9a522":
        raise RuntimeError("frozen experiment 028 reference changed")
    (out/"frozen_reference.json").write_bytes(reference_bytes)
    sha={}
    def save(name,arr):
        binary=_npy(arr)
        (out/name).write_bytes(binary)
        sha[name]=hashlib.sha256(binary).hexdigest()
    bodies=prepared_bodies()
    rng=np.random.default_rng(20261025)
    ledgers={}
    fronts={}
    transfer={}
    for label,body in bodies.items():
        ledgers[label]={}
        fronts[label]={}
        transfer[label]={}
        for termination in MODES:
            cfg=AcousticConfig(body,termination=termination)
            x=np.zeros(768);x[:128]=rng.normal(scale=1e-6,size=128)
            d=AnatomicalWaveguide(cfg)
            tr,states,q=d.trace_with_states(x)
            # Evidence FIRST, physical acceptance SECOND.
            save(label+"_"+termination+"_port.npy",tr)
            save(label+"_"+termination+"_states.npy",states)
            if termination=="b0":
                save(label+"_"+termination+"_q.npy",q)
            ledgers[label][termination]=energy_gate(tr)
            impulse=np.zeros(4*cfg.wave_cells+4);impulse[0]=1e-6
            front=AnatomicalWaveguide(cfg).trace(impulse)
            save(label+"_"+termination+"_front.npy",front)
            fronts[label][termination]={
                "first_lip_incident_tick":int(np.flatnonzero(front[:,4])[0]),
                "first_source_reflection_tick":(
                    int(np.flatnonzero(front[:,3])[0]) if np.any(front[:,3]) else None),
                "physical_first_arrival_seconds":cfg.one_way_s,
                "internal_physics_clock_hz":cfg.fs_hz,
            }
        for n in (2,4,8):
            cfg=AcousticConfig(body,cells_per_section=n)
            # Gate A2: M0/i has genuine long-lived passive ringing; never
            # zero-pad, window, damp, or analytically replace its real time trace.
            duration_s=18.0 if label=="M0_i" else 5.0
            signal=AnatomicalWaveguide(cfg).impulse_lip_pressure(
                int(math.ceil(duration_s*cfg.fs_hz)))
            save(label+"_b0_full_impulse_n"+str(n)+".npy",signal)
            errors={}
            for f in FREQS:
                a=continuous_transfer(f,cfg)
                h=empirical_transfer(signal,cfg,f)
                errors[str(f)]={
                    "complex_relative":float(abs(h-a)/abs(a)),
                    "empirical_complex":[h.real,h.imag],
                    "analog_complex":[a.real,a.imag],
                }
            transfer[label][str(n)]=errors
    result={
        "schema":"research.sa2b_b2a.v1-state-archive",
        "frozen_reference_sha256":hashlib.sha256(reference_bytes).hexdigest(),
        "frozen_reference_git_blob_sha1":reference_git_blob,
        "prereg_sha":PREREG,
        "executed_sha":"VERIFY_WITH_GITHUB_ACTIONS_RECEIPT",
        "scientific_status":"AWAITING_INDEPENDENT_CI_AND_ARTIFACT_AUDIT",
        "adoption":"NOT_ADOPTED",
        "bodies":{name:{"preset_id":v.preset_id,"preset_revision":v.preset_revision,
                         "source":v.source,"areas_digest_float64":v.area_digest,
                         "lip_area_m2":v.lip_area_m2,
                         "length_m":v.total_length_m,
                         "section_lengths_m":list(v.lengths_m),
                         "areas_m2":list(v.areas_m2)}
                   for name,v in bodies.items()},
        "impulse_duration_s":{"M0_a":5.0,"M1_a":5.0,"M0_i":18.0},
        "post_failure_amendment":"AMENDMENT_02_LONG_RINGDOWN.md",
        "port_columns":TRACE_COLUMNS,
        "one_way":fronts,
        "energy":ledgers,
        "transfer":transfer,
        "sha256":sha,
        "limitations":["stationary serial lossless rigid 1D","no native 48k observer",
                       "no animated anatomy","no sound quality validation",
                       "not a public Core runtime"],
    }
    (out/"manifest.json").write_text(
        json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    (out/"RUN_COMPLETE.txt").write_text("B2-A source experiment completed; separate independent raw audit still required.\n")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    opts=parser.parse_args()
    try:
        data=experiment(opts.out)
    except Exception as failure:
        if opts.out.is_dir():
            (opts.out/"RUN_FAILED.txt").write_text(
                type(failure).__name__+": "+str(failure)+"\n")
        raise
    print(json.dumps({"scientific_status":data["scientific_status"],
                      "energy":data["energy"],"arrival":data["one_way"],
                      "transfer":{b:{n:{f:d["complex_relative"] for f,d in rows.items()}
                                     for n,rows in val.items()}
                                  for b,val in data["transfer"].items()}},
                     indent=2,sort_keys=True))
