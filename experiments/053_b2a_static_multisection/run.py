"""SA-2B/B2-A research-only physically local PASSIVE multi-section traveling waves.

Gate A was committed before this implementation. Frozen prepared CC-A2
M0/M1 rest anatomies; no invented body. No moving articulators or 48k I/O.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
import argparse
import hashlib
import importlib.util
import io
import os
import traceback
import json
import math
from pathlib import Path
import runpy
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
PREREG="70e4875c77336df0eb3f2e2b6d4a402e209d3d6f"
RHO=1.21
C=343.
TERMS=("closed","pressure_release","matched","b0")
COLS=("tick","U_in_m3_s","source_a_pa","source_b_pa","mouth_a_pa",
      "mouth_b_pa","p_source_pa","p_mouth_pa","U_mouth_m3_s",
      "E_duct_j","E_B0_j","source_work_j","terminal_loss_j",
      "delta_total_E_j","energy_residual_j")

def _b0():
    key="sa2b_b2a_original_b0"
    if key in sys.modules:return sys.modules[key]
    path=ROOT/"experiments/050_b0_passive_radiation/run.py"
    spec=importlib.util.spec_from_file_location(key,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[key]=obj
    spec.loader.exec_module(obj)
    return obj

def prepared_bodies():
    """Use actual CC-A2 versioned registry, never manufacture a body alias."""
    sv=runpy.run_path(str(ROOT/"experiments/042_sv1_sustained_vowel/run.py"))
    _frozen,exp,m0=sv["_validated_context"]()
    cc=runpy.run_path(str(ROOT/"tools/cc_a2_live.py"))
    registry=cc["prepared_registry"](exp)
    from morphoacoustics.integration.body_presets import CharacterBodyBinding,BindingStatus
    frozen=json.loads((ROOT/"experiments/028_task_field_morphology_transfer/frozen_reference.json").read_text())
    result={}
    for name,step in (("M0",.010),("M1",.011)):
        bound=registry.resolve(
            CharacterBodyBinding("b2a-research","v3b-axial-"+name,1),
            required_backend_id=exp.TRACT1D_BACKEND_ID)
        if bound.status!=BindingStatus.BOUND or bound.snapshot is None or bound.preset is None:
            raise AssertionError("invalid frozen prepared body binding")
        geo=bound.preset.prepared.rest_state
        areas=np.array([s.area_m2 for s in geo.sections],dtype=np.float64)
        lengths=np.array([s.length_m for s in geo.sections],dtype=np.float64)
        assert len(areas)==16 and len(set(areas))>3
        assert np.array_equal(areas,np.array(frozen["M0"]["a_areas_m2"]))
        assert np.allclose(lengths,step,rtol=0,atol=1e-15)
        assert math.isclose(sum(lengths),.16*(step/.01),rel_tol=1e-13)
        result[name]={"areas":areas,"lengths":lengths,
            "preset_id":bound.snapshot.preset_id,
            "preset_revision":bound.snapshot.preset_revision,
            "preparation_digest":bound.snapshot.preparation_digest,
            "backend_id":bound.snapshot.backend_id,
            "geometry":geo}
    if m0.snapshot.preparation_digest!=result["M0"]["preparation_digest"]:
        raise AssertionError("SV1 and CC-A2 M0 source mismatch")
    return result

@dataclass(frozen=True)
class Config:
    areas:tuple[float,...]
    lengths:tuple[float,...]
    cells_per_section:int=2
    termination:str="b0"
    rho:float=RHO
    c:float=C
    def __post_init__(self):
        if type(self.cells_per_section)!=int or self.cells_per_section not in (2,4,8):
            raise ValueError("unsupported local resolution")
        if self.termination not in TERMS:raise ValueError("terminal")
        if not self.areas or len(self.areas)!=len(self.lengths):raise ValueError("geometry size")
        for a,l in zip(self.areas,self.lengths):
            if not math.isfinite(float(a)) or float(a)<=0 or not math.isfinite(float(l)) or float(l)<=0:
                raise ValueError("invalid section")
        if any(not math.isclose(l,self.lengths[0],rel_tol=0,abs_tol=1e-14) for l in self.lengths):
            raise ValueError("variable section lengths need physically verified different scheme")
        if not (math.isfinite(self.rho) and self.rho>0 and math.isfinite(self.c) and self.c>0):
            raise ValueError("air")
        if not math.isfinite(self.fs) or self.fs<=0:raise ValueError("clock")
    @property
    def fs(self):return self.c*self.cells_per_section/self.lengths[0]
    @property
    def h(self):return 1/self.fs
    @property
    def n(self):return len(self.areas)*self.cells_per_section
    @property
    def z(self):return tuple(self.rho*self.c/a for a in self.areas)
    @property
    def length(self):return sum(self.lengths)

def config_for(body,n=2,term="b0"):
    return Config(tuple(float(x) for x in body["areas"]),
                  tuple(float(x) for x in body["lengths"]),n,term)

def junction(a,b,zl,zr):
    """Exact local pressure scattering with both sides incident."""
    r=(zr-zl)/(zr+zl)
    return r*a+(1-r)*b,(1+r)*a-r*b

@dataclass(frozen=True)
class Step:
    tick:int
    inlet_flow:float
    source_a:float
    source_b:float
    mouth_a:float
    mouth_b:float
    p_source:float
    p_mouth:float
    U_mouth:float
    E_duct:float
    E_B0:float
    W_source:float
    D_terminal:float
    delta_E:float
    residual:float

class StaticMultisection:
    def __init__(self,cfg,*,forward=None,backward=None,initial_q=0.):
        self.cfg=cfg
        m=cfg.cells_per_section
        n=len(cfg.areas)
        self.f=[deque([0.]*m) for _ in range(n)]
        self.b=[deque([0.]*m) for _ in range(n)]
        for val,queues in ((forward,self.f),(backward,self.b)):
            if val is None:continue
            x=np.asarray(val,dtype=float)
            if x.shape!=(n,m) or not np.isfinite(x).all():raise ValueError("initial waves")
            for j in range(n):
                queues[j].clear();queues[j].extend(x[j].tolist())
        if not math.isfinite(float(initial_q)):raise ValueError("q")
        if cfg.termination!="b0" and initial_q!=0:raise ValueError("q without B0")
        self.port=None
        if cfg.termination=="b0":
            lib=_b0()
            self.port=lib.BaffledRadiationOnePort(
                lib.parameters_from_area(cfg.areas[-1],rho=cfg.rho,c=cfg.c,fs=cfg.fs),
                initial_q_m3_s=initial_q)
        self.ticks=0

    def E(self):
        z=self.cfg.z
        wave=self.cfg.h*sum(
            (sum(v*v for v in self.f[i])+sum(v*v for v in self.b[i]))/z[i]
            for i in range(len(z)))
        mouth=(.5*self.port.parameters.inertance_pa_s2_m3*self.port.q_m3_s**2
               if self.port else 0.)
        return wave,mouth

    def _step(self,u,with_ledger):
        if isinstance(u,(bool,np.bool_)) or not math.isfinite(float(u)):raise ValueError("inlet U")
        u=float(u)
        cfg=self.cfg
        old=sum(self.E()) if with_ledger else 0.
        aa=[q.popleft() for q in self.f]
        bb=[q.popleft() for q in self.b]
        # Interface output writes occur on same time tick, one spatial cell
        # traversed per tick; no global algebraic propagation solve.
        newf=[0.]*len(aa);newb=[0.]*len(bb)
        newf[0]=bb[0]+cfg.z[0]*u
        for j in range(len(aa)-1):
            newb[j],newf[j+1]=junction(aa[j],bb[j+1],cfg.z[j],cfg.z[j+1])
        mouth_a=aa[-1]
        if cfg.termination=="closed": mouth_b,loss=mouth_a,0.
        elif cfg.termination=="pressure_release":mouth_b,loss=-mouth_a,0.
        elif cfg.termination=="matched":
            mouth_b=0.;loss=cfg.h*mouth_a**2/cfg.z[-1]
        else:
            ans=self.port.step(mouth_a)
            mouth_b=ans.reflected_pa
            loss=ans.resistance_dissipation_j
        newb[-1]=mouth_b
        source_b=bb[0];source_a=newf[0]
        source_p=source_a+source_b
        mouth_p=mouth_a+mouth_b
        mouth_u=(mouth_a-mouth_b)/cfg.z[-1]
        if not all(math.isfinite(x) for x in newf+newb+[loss,source_p,mouth_p,mouth_u]):
            raise FloatingPointError("nonfinite physical scattering")
        for j in range(len(aa)):
            self.f[j].append(newf[j])
            self.b[j].append(newb[j])
        index=self.ticks;self.ticks+=1
        if not with_ledger:return mouth_p
        duct,port=self.E()
        de=duct+port-old
        work=cfg.h*source_p*u
        return Step(index,u,source_a,source_b,mouth_a,mouth_b,source_p,
                    mouth_p,mouth_u,duct,port,work,loss,de,de-work+loss)

    def step(self,u):return self._step(u,True)
    def impulse(self,ticks,amplitude=1e-6):
        result=np.zeros(ticks,dtype=float)
        for k in range(ticks):
            result[k]=self._step(amplitude if k==0 else 0.,False)
        return result
    def trace(self,inlet):
        x=np.asarray(inlet,dtype=float)
        if x.ndim!=1 or not np.isfinite(x).all():raise ValueError("invalid input trace")
        out=np.empty((len(x),len(COLS)))
        for k,v in enumerate(x):
            out[k]=tuple(vars(self.step(float(v))).values())
        return out

def energy_gate(tr,initial=0.):
    E=tr[:,9]+tr[:,10];previous=np.r_[initial,E[:-1]]
    W,D,de,res=tr[:,11],tr[:,12],tr[:,13],tr[:,14]
    tol=np.maximum(1e-9*np.maximum.reduce((abs(de),abs(W),D,np.full(len(E),1e-20))),
                   1e-12*np.maximum.reduce((E,previous,np.full(len(E),1e-20))))
    if np.any(abs(res)>tol) or np.any(E<0) or np.any(D<0):raise AssertionError("energy")
    cum=abs(float(sum(res)))
    lim=max(1e-9*max(float(sum(abs(W))+sum(D)),1e-20),
            1e-10*max(float(np.max(E,initial=0)),initial,1e-20))
    if cum>lim:raise AssertionError("energy cumulative")
    return {"max_norm_step":float(np.max(abs(res)/tol,initial=0)),
            "cumulative_residual_j":cum,"total_dissipation_j":float(sum(D))}

def npy_bytes(a):
    stream=io.BytesIO();np.save(stream,np.asarray(a),allow_pickle=False)
    return stream.getvalue()

def _run_science(out):
    bodies=prepared_bodies()
    rng=np.random.default_rng(20261025)
    manifest={"schema":"sa2b.b2a.v0","prereg_sha":PREREG,
        "decision":"AWAITING_INDEPENDENT_REVIEW",
        "production":"NOT_ADOPTED","source_sha":"VERIFY_CI_EVIDENCE",
        "bodies":{},"arrival":{},"energy":{},"sha256":{}}
    def archive(key,array):
        if key in manifest["sha256"]:raise FileExistsError("duplicate archive key "+key)
        binary=npy_bytes(array)
        # Write DURABLY before validating the resulting evidence. Any later
        # failure leaves source/port states for falsifiable investigation.
        with (out/key).open("xb") as stream:
            stream.write(binary)
            stream.flush()
            os.fsync(stream.fileno())
        manifest["sha256"][key]=hashlib.sha256(binary).hexdigest()
        (out/"PARTIAL_EVIDENCE.json").write_text(
            json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+"\n")
    for name,body in bodies.items():
        manifest["bodies"][name]={
            "preset_id":body["preset_id"],"revision":body["preset_revision"],
            "digest":body["preparation_digest"],"backend":body["backend_id"],
            "areas_m2":body["areas"].tolist(),"lengths_m":body["lengths"].tolist()}
        for n in (2,4,8):
            cfg=config_for(body,n)
            impulse=StaticMultisection(cfg).impulse(int(math.ceil(2*cfg.fs)))
            archive(f"{name}_n{n}_b0_full_impulse.npy",impulse)
            # The source-to-mouth first nonzero must reflect actual one-way
            # physical distance despite different impedance junctions.
            first=int(np.flatnonzero(impulse)[0])
            manifest["arrival"][f"{name}_n{n}"]={
                "tick":first,"one_way_s":first/cfg.fs,
                "clock_hz":cfg.fs,"length_m":cfg.length}
        for term in TERMS:
            cfg=config_for(body,2,term)
            excitation=np.zeros(1024);excitation[:128]=rng.normal(0,1e-6,128)
            model=StaticMultisection(cfg)
            tr=np.empty((len(excitation),len(COLS)),dtype=np.float64)
            # Full physical wave state AFTER each tick, two directions, all
            # original anatomy sections and all local cells. Independent audit
            # must reconstruct pressure/flow energy from these RAW wave states,
            # not trust the solver's energy ledger columns.
            waves=np.empty((len(excitation),2,len(cfg.areas),cfg.cells_per_section),
                           dtype=np.float64)
            inertance_q=np.empty(len(excitation),dtype=np.float64)
            for tick,flow in enumerate(excitation):
                step=model.step(float(flow))
                tr[tick]=tuple(vars(step).values())
                for cell in range(len(cfg.areas)):
                    waves[tick,0,cell,:]=model.f[cell]
                    waves[tick,1,cell,:]=model.b[cell]
                inertance_q[tick]=(model.port.q_m3_s if model.port else 0.)
            archive(f"{name}_{term}_signed_trace.npy",tr)
            archive(f"{name}_{term}_wave_states.npy",waves)
            archive(f"{name}_{term}_b0_q.npy",inertance_q)
            manifest["energy"][f"{name}_{term}"]=energy_gate(tr)
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return manifest


def run(out):
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    (out/"CI_EVIDENCE.txt").write_text(
        "EXACT_GITHUB_SHA="+os.getenv("GITHUB_SHA","LOCAL_UNVERIFIED")+"\n"
        "GITHUB_REF="+os.getenv("GITHUB_REF","LOCAL_UNVERIFIED")+"\n"
        "GITHUB_RUN_ID="+os.getenv("GITHUB_RUN_ID","LOCAL_UNVERIFIED")+"\n")
    try:
        return _run_science(out)
    except BaseException as exc:
        (out/"FAILED_GATE.json").write_text(json.dumps({
            "status":"B2A_HOLD_FAILURE_EVIDENCE_PRESERVED",
            "reason_type":type(exc).__name__,
            "reason_message":str(exc),
            "traceback":traceback.format_exc(),
            "prereg_sha":PREREG,
            "source_sha":os.getenv("GITHUB_SHA","LOCAL_UNVERIFIED"),
        },indent=2,sort_keys=True)+"\n")
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out",required=True,type=Path)
    result=run(parser.parse_args().out)
    print(json.dumps({"decision":result["decision"],"arrival":result["arrival"],
                      "energy":result["energy"]},indent=2,sort_keys=True))
