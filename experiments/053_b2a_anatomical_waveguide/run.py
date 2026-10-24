"""B2-A research-only stationary anatomical waveguide; Gate A commit 147a275.

One passive local traveling-wave mechanism with area-step scattering.
Not a moving-wall, glottal-source or native 48k audio model.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
def _b1():
    key="sa2b_b1b_for_b2a"
    if key not in sys.modules:
        path=ROOT/"experiments/052_b1b_local_waveguide/run.py"
        spec=importlib.util.spec_from_file_location(key,path)
        module=importlib.util.module_from_spec(spec)
        sys.modules[key]=module
        spec.loader.exec_module(module)
    return sys.modules[key]

@dataclass(frozen=True)
class AnatomicalDuct:
    lengths_m: tuple[float,...]
    areas_m2: tuple[float,...]
    cells_per_section: int=2
    termination: str="b0"
    rho: float=1.21
    c: float=343.0

    def __post_init__(self):
        if len(self.lengths_m)!=len(self.areas_m2) or not self.lengths_m:
            raise ValueError("invalid anatomy")
        if self.cells_per_section not in (2,4,8) or type(self.cells_per_section) is not int:
            raise ValueError("unsupported refinement")
        if self.termination not in ("b0","matched","closed","pressure_release"):
            raise ValueError("invalid termination")
        if not all(math.isfinite(x) and x>0 for x in (*self.lengths_m,*self.areas_m2,self.rho,self.c)):
            raise ValueError("nonphysical dimensions")
        if not all(math.isclose(x,self.lengths_m[0],rel_tol=0,abs_tol=1e-12) for x in self.lengths_m):
            raise ValueError("unequal section lengths not yet physically clocked")

    @property
    def dt(self): return self.lengths_m[0]/(self.cells_per_section*self.c)
    @property
    def fs_hz(self): return 1/self.dt
    @property
    def n_cells(self): return len(self.lengths_m)*self.cells_per_section
    @property
    def z(self): return np.repeat(self.rho*self.c/np.asarray(self.areas_m2),self.cells_per_section)
    @property
    def one_way_s(self): return sum(self.lengths_m)/self.c

def junction(left_incident,right_incident,z_left,z_right):
    """Return left- and right-going outgoing pressure waves at one junction."""
    p=2*(left_incident/z_left+right_incident/z_right)/(1/z_left+1/z_right)
    return p-left_incident,p-right_incident

class AnatomicalTravelingWaveDuct:
    def __init__(self,cfg:AnatomicalDuct):
        self.cfg=cfg
        self.forward=np.zeros(cfg.n_cells)
        self.backward=np.zeros(cfg.n_cells)
        self.z=cfg.z
        self.port=None
        if cfg.termination=="b0":
            b0=_b1()._b0_module()
            params=b0.parameters_from_area(cfg.areas_m2[-1],rho=cfg.rho,c=cfg.c,fs=cfg.fs_hz)
            self.port=b0.BaffledRadiationOnePort(params)
        self.ticks=0

    def energies(self):
        duct=self.cfg.dt*float(np.sum((self.forward**2+self.backward**2)/self.z))
        mouth=0. if self.port is None else .5*self.port.parameters.inertance_pa_s2_m3*self.port.q_m3_s**2
        return duct,mouth

    def step(self,inlet_flow_m3_s):
        u=float(inlet_flow_m3_s)
        if not math.isfinite(u): raise ValueError("nonfinite source")
        old=sum(self.energies())
        n=self.cfg.n_cells
        # Wave values are located in cells; scattering at each cell boundary
        # precedes one local wave propagation tick.
        incoming_right=self.forward.copy()
        incoming_left=self.backward.copy()
        a_lip=float(incoming_right[-1])
        b_source=float(incoming_left[0])
        a_source=b_source+self.z[0]*u
        if self.cfg.termination=="closed":
            b_lip=a_lip;diss=0.
        elif self.cfg.termination=="pressure_release":
            b_lip=-a_lip;diss=0.
        elif self.cfg.termination=="matched":
            b_lip=0.;diss=self.cfg.dt*a_lip*a_lip/self.z[-1]
        else:
            result=self.port.step(a_lip)
            b_lip=result.reflected_pa
            diss=result.resistance_dissipation_j
        f=np.empty(n);b=np.empty(n)
        f[0]=a_source;b[-1]=b_lip
        for j in range(n-1):
            # outgoing right travels into next cell; outgoing left into previous
            left_out,right_out=junction(incoming_right[j],incoming_left[j+1],self.z[j],self.z[j+1])
            f[j+1]=right_out;b[j]=left_out
        self.forward=f;self.backward=b;self.ticks+=1
        work=self.cfg.dt*(a_source*a_source-b_source*b_source)/self.z[0]
        duct,mouth=self.energies()
        residual=duct+mouth-old-work+diss
        return {"tick":self.ticks-1,"a_lip_pa":a_lip,"b_lip_pa":b_lip,
                "p_lip_pa":a_lip+b_lip,"u_lip_m3_s":(a_lip-b_lip)/self.z[-1],
                "p_in_pa":a_source+b_source,"source_work_j":work,
                "outlet_dissipation_j":diss,"duct_energy_j":duct,
                "mouth_energy_j":mouth,"residual_j":residual}

    def impulse(self,ticks,amplitude=1e-6):
        out=np.zeros(ticks)
        for i in range(ticks):
            out[i]=self.step(amplitude if i==0 else 0.)["p_lip_pa"]
        return out

def continuum_transfer(f_hz,cfg:AnatomicalDuct):
    """Independent frequency-domain cascaded two-port oracle."""
    w=2*math.pi*f_hz
    matrix=np.eye(2,dtype=complex)
    for length,area in zip(cfg.lengths_m,cfg.areas_m2):
        z=cfg.rho*cfg.c/area
        k=w*length/cfg.c
        t=np.array([[math.cos(k),1j*z*math.sin(k)],
                    [1j*math.sin(k)/z,math.cos(k)]])
        matrix=matrix@t
    if cfg.termination!="b0": raise ValueError("analog oracle requires B0")
    b0=_b1()._b0_module()
    params=b0.parameters_from_area(cfg.areas_m2[-1],rho=cfg.rho,c=cfg.c,fs=cfg.fs_hz)
    zload=b0.analog_impedance(1j*w,params)
    return 1/(matrix[1,0]+matrix[1,1]/zload)

def empirical_transfer(impulse,cfg,f_hz,amplitude=1e-6):
    ticks=np.arange(len(impulse))
    return np.dot(impulse,np.exp(-2j*math.pi*f_hz*cfg.dt*ticks))/amplitude

