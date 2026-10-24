"""B1b independent LOCAL two-direction acoustic traveling-wave duct.

Research only. Geometry is a uniform tube, NOT authentic variable-area M0.
Pre-code A2: docs/research/sa-2b-b1/GATE_A2_LOCAL_WAVEGUIDE.md
at commit ef7d74cbbafeca5113db9e4b34bbb0d220b228c4.

Key decision: the acoustical clock is derived from physical dx/c and is
NOT the audio observation rate. The discrete waveguide has exact local
finite support and strictly passive boundary scattering.
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
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PREREG_SHA = "ef7d74cbbafeca5113db9e4b34bbb0d220b228c4"
LENGTH_M = 0.16
REFERENCE_SECTION_M = 0.01
M0_LIP_AREA_M2 = 0.000804247719318987
RHO = 1.21
C = 343.0
TERMINATIONS = ("closed", "pressure_release", "matched", "b0")
TRACE_COLUMNS = (
    "time_s", "U_in_m3_s", "a_source_pa", "b_source_pa",
    "a_lip_pa", "b_lip_pa", "p_in_pa", "p_lip_pa", "U_lip_m3_s",
    "E_duct_j", "E_B0_j", "source_work_j", "outlet_dissipation_j",
    "delta_total_E_j", "energy_residual_j",
)


def _b0_module():
    key = "sa2b_b0_waveguide_original"
    if key in sys.modules:
        return sys.modules[key]
    path = ROOT / "experiments/050_b0_passive_radiation/run.py"
    spec = importlib.util.spec_from_file_location(key, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("original B0 one-port missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


def _positive(name, v):
    if isinstance(v, (bool, np.bool_)):
        raise ValueError(name)
    try:
        f = float(v)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(name) from exc
    if not math.isfinite(f) or f <= 0:
        raise ValueError(name)
    return f


@dataclass(frozen=True)
class PhysicalClockDuct:
    length_m: float = LENGTH_M
    area_m2: float = M0_LIP_AREA_M2
    rho: float = RHO
    c: float = C
    reference_section_m: float = REFERENCE_SECTION_M
    cells_per_section: int = 2
    termination: str = "b0"

    def __post_init__(self):
        for name in ("length_m", "area_m2", "rho", "c", "reference_section_m"):
            _positive(name, getattr(self, name))
        if type(self.cells_per_section) is not int or self.cells_per_section not in (2, 4, 8):
            raise ValueError("cells_per_section must be 2,4,8")
        if self.termination not in TERMINATIONS:
            raise ValueError("unknown passive termination")
        # Calibration geometry must be exactly integral sections. Do not
        # secretly quantize nonintegral physical body lengths.
        sections = self.length_m / self.reference_section_m
        if not math.isclose(sections, round(sections), rel_tol=0, abs_tol=1e-10):
            raise ValueError("nonintegral reference geometry requires another solver")
        if sections < 1 or sections > 1024:
            raise ValueError("unsupported calibration length")
        if not all(math.isfinite(x) and x > 0 for x in
                   (self.fs_hz, self.zc, self.time_step_s)):
            raise ValueError("invalid derived physical clock")

    @property
    def n_cells(self):
        return int(round(self.length_m / self.reference_section_m)) * self.cells_per_section

    @property
    def dx(self):
        return self.reference_section_m / self.cells_per_section

    @property
    def fs_hz(self):
        return self.c / self.dx

    @property
    def time_step_s(self):
        return self.dx / self.c

    @property
    def one_way_s(self):
        return self.length_m / self.c

    @property
    def zc(self):
        return self.rho * self.c / self.area_m2


@dataclass(frozen=True)
class WaveStep:
    time_s: float
    inlet_flow_m3_s: float
    source_incident_pa: float
    source_reflected_pa: float
    lip_incident_pa: float
    lip_reflected_pa: float
    inlet_pressure_pa: float
    lip_pressure_pa: float
    lip_flow_m3_s: float
    duct_energy_j: float
    mouth_energy_j: float
    source_work_j: float
    outlet_dissipation_j: float
    delta_total_energy_j: float
    residual_j: float


class LocalTravelingWaveDuct:
    """One local spatial-cell shift per physics clock: two physical wave FIFOs."""

    def __init__(self, config: PhysicalClockDuct, *,
                 initial_forward_pa=None, initial_backward_pa=None,
                 initial_b0_q_m3_s=0.0):
        self.cfg = config
        self.forward = deque([0.0] * config.n_cells)
        self.backward = deque([0.0] * config.n_cells)
        for name, provided, buffer in (
            ("forward", initial_forward_pa, self.forward),
            ("backward", initial_backward_pa, self.backward),
        ):
            if provided is not None:
                x = np.asarray(provided, dtype=np.float64)
                if x.shape != (config.n_cells,) or not np.isfinite(x).all():
                    raise ValueError("invalid " + name + " initial wave state")
                buffer.clear()
                buffer.extend(float(v) for v in x)
        if not math.isfinite(float(initial_b0_q_m3_s)):
            raise ValueError("invalid original B0 stored q")
        if config.termination != "b0" and initial_b0_q_m3_s != 0:
            raise ValueError("B0 q belongs only to physical B0 termination")
        self.port = None
        if config.termination == "b0":
            lib = _b0_module()
            params = lib.parameters_from_area(
                config.area_m2, rho=config.rho, c=config.c, fs=config.fs_hz
            )
            self.port = lib.BaffledRadiationOnePort(
                params, initial_q_m3_s=initial_b0_q_m3_s
            )
        self.ticks = 0

    def wave_energy_j(self):
        factor = self.cfg.time_step_s / self.cfg.zc
        return factor * (sum(x*x for x in self.forward) +
                         sum(x*x for x in self.backward))

    def mouth_energy_j(self):
        if self.port is None:
            return 0.0
        return 0.5 * self.port.parameters.inertance_pa_s2_m3 * self.port.q_m3_s**2

    def total_energy_j(self):
        return self.wave_energy_j() + self.mouth_energy_j()

    def field_p_u(self):
        """Physical p/U cell states from co-located counter-traveling waves.

        Cell 0 is the source side, cell N-1 is the lip side.
        """
        a = np.asarray(list(self.forward)[::-1], dtype=np.float64)
        b = np.asarray(list(self.backward), dtype=np.float64)
        return a + b, (a - b) / self.cfg.zc

    def _advance(self, inlet_flow_m3_s: float, *, audit: bool):
        if isinstance(inlet_flow_m3_s, (bool, np.bool_)):
            raise ValueError("invalid flow")
        u = float(inlet_flow_m3_s)
        if not math.isfinite(u):
            raise ValueError("nonfinite inlet flow")
        old = self.total_energy_j() if audit else 0.0
        # Pop only the nearest end, not an all-domain matrix inversion.
        a_lip = self.forward.popleft()
        b_source = self.backward.popleft()
        a_source = b_source + self.cfg.zc*u
        if self.cfg.termination == "closed":
            b_lip, diss, mouth_e = a_lip, 0.0, 0.0
        elif self.cfg.termination == "pressure_release":
            b_lip, diss, mouth_e = -a_lip, 0.0, 0.0
        elif self.cfg.termination == "matched":
            b_lip = 0.0
            diss = self.cfg.time_step_s*a_lip*a_lip/self.cfg.zc
            mouth_e = 0.0
        else:
            assert self.port is not None
            result = self.port.step(a_lip)
            b_lip = result.reflected_pa
            diss = result.resistance_dissipation_j
            mouth_e = result.stored_energy_j
        p_in = a_source+b_source
        p_lip = a_lip+b_lip
        u_lip = (a_lip-b_lip)/self.cfg.zc
        if not all(math.isfinite(z) for z in
                   (a_source,b_lip,p_in,p_lip,u_lip,diss)):
            raise FloatingPointError("invalid acoustic wave transfer")
        self.forward.append(a_source)
        self.backward.append(b_lip)
        self.ticks += 1
        if not audit:
            return p_lip
        pipe_e = self.wave_energy_j()
        current = pipe_e + mouth_e
        work = self.cfg.time_step_s * (a_source*a_source-b_source*b_source) / self.cfg.zc
        delta = current - old
        residual = delta - work + diss
        return WaveStep(
            (self.ticks-1)*self.cfg.time_step_s, u, a_source,b_source,
            a_lip,b_lip,p_in,p_lip,u_lip,pipe_e,mouth_e,work,diss,delta,residual
        )

    def step(self, inlet_flow_m3_s):
        return self._advance(inlet_flow_m3_s, audit=True)

    def trace(self, inlet):
        inp = np.asarray(inlet, dtype=np.float64)
        if inp.ndim != 1 or not np.isfinite(inp).all():
            raise ValueError("expected finite 1D volume-flow stream")
        output = np.empty((len(inp),len(TRACE_COLUMNS)), dtype=np.float64)
        for i,u in enumerate(inp):
            output[i,:] = tuple(vars(self.step(float(u))).values())
        return output

    def impulse_lip_pressure(self, length: int, *, amplitude_m3_s: float=1e-6):
        """Real time-step experiment using identical physical state transitions.

        The fast path skips repeated O(N) energy logging, never the B0 step.
        Tested against the audited step path on identical input sequences.
        """
        if type(length) is not int or length <= 0:
            raise ValueError("invalid impulse length")
        _positive("amplitude", abs(amplitude_m3_s))
        out = np.empty(length, dtype=np.float64)
        for j in range(length):
            out[j] = self._advance(amplitude_m3_s if j==0 else 0., audit=False)
        return out


def energy_gate(tr: np.ndarray, initial_total_j=0.0):
    a = np.asarray(tr, dtype=np.float64)
    if a.ndim != 2 or a.shape[1] != len(TRACE_COLUMNS) or not np.isfinite(a).all():
        raise ValueError("invalid SI trace")
    cur = a[:,9]+a[:,10]
    old = np.concatenate(([initial_total_j],cur[:-1]))
    work,diss,de,res = a[:,11],a[:,12],a[:,13],a[:,14]
    bound = np.maximum(
        1e-9*np.maximum.reduce((np.abs(de),np.abs(work),diss,np.full(len(a),1e-20))),
        1e-12*np.maximum.reduce((old,cur,np.full(len(a),1e-20))))
    if np.any(abs(res)>bound) or np.any(diss < 0) or np.any(cur < 0):
        raise AssertionError("energy/power non-passive B1b")
    cumulative = abs(float(sum(res)))
    allowed=max(
        1e-9*max(float(sum(abs(work))+sum(diss)),1e-20),
        1e-10*max(float(max(cur,initial=0.)),initial_total_j,1e-20))
    if cumulative>allowed:
        raise AssertionError("energy ledger accumulates mismatch")
    return {
        "max_normalized_step_residual":float(max(abs(res)/bound,default=0.0)),
        "cumulative_residual_j":cumulative,
        "max_stored_energy_j":float(max(cur,initial=0.)),
        "total_outlet_dissipation_j":float(sum(diss)),
        "sum_signed_inlet_work_j":float(sum(work)),
    }


def continuum_analog_transfer(f_hz:float,cfg:PhysicalClockDuct):
    if cfg.termination != "b0":
        raise ValueError("B0 reference needs B0")
    f=_positive("f",f_hz)
    b0=_b0_module()
    p=b0.parameters_from_area(cfg.area_m2,rho=cfg.rho,c=cfg.c,fs=cfg.fs_hz)
    z=complex(b0.analog_impedance(2j*math.pi*f,p))
    kl=2*math.pi*f*cfg.length_m/cfg.c
    return 1/(1j*math.sin(kl)/cfg.zc+math.cos(kl)/z)


def independent_discrete_scattering_transfer(f_hz:float,cfg:PhysicalClockDuct):
    """Analytic port/scattering reference, independent of measured time trace."""
    if cfg.termination != "b0":
        raise ValueError("B0 scattering reference needs B0")
    b0=_b0_module()
    p=b0.parameters_from_area(cfg.area_m2,rho=cfg.rho,c=cfg.c,fs=cfg.fs_hz)
    gamma=b0.gamma_digital(f_hz,p)
    d=complex(np.exp(-2j*np.pi*f_hz*cfg.one_way_s))
    return cfg.zc*d*(1+gamma)/(1-gamma*d*d)


def empirical_transfer_at_frequency(impulse_p_lip, cfg, frequency_hz,
                                    amplitude_m3_s=1e-6):
    """Actual emitted mouth p from a delta U at source, one-sided DTFT."""
    j=np.arange(len(impulse_p_lip),dtype=np.float64)
    phase=np.exp(-2j*np.pi*frequency_hz/cfg.fs_hz*j)
    return complex(np.dot(np.asarray(impulse_p_lip),phase)/amplitude_m3_s)


def _raw_npy(array):
    f=io.BytesIO()
    np.save(f,np.asarray(array),allow_pickle=False)
    return f.getvalue()


def experiment(out:Path):
    if out.exists():
        raise FileExistsError("never overwrite evidence")
    rng=np.random.default_rng(20261024)
    cfg=PhysicalClockDuct()
    data={}
    energy={}
    fronts={}
    for termination in TERMINATIONS:
        current=PhysicalClockDuct(termination=termination)
        model=LocalTravelingWaveDuct(current)
        inp=np.zeros(1152)
        inp[:128]=rng.normal(scale=1e-6,size=128)
        rows=model.trace(inp)
        energy[termination]=energy_gate(rows)
        data[termination+"_port_trace.npy"]=rows
        front=LocalTravelingWaveDuct(current)
        pulse=np.zeros(4*current.n_cells+2);pulse[0]=1e-6
        rows2=front.trace(pulse)
        data[termination+"_wavefront_trace.npy"]=rows2
        fronts[termination]={
            "first_lip_nonzero_tick":int(np.flatnonzero(rows2[:,4])[0]),
            "first_source_return_nonzero_tick":int(np.flatnonzero(rows2[:,3])[0]) if np.any(rows2[:,3]) else None,
        }
    comparisons={}
    for n in (2,4,8):
        cfg_n=PhysicalClockDuct(cells_per_section=n)
        # Record fully empirical frequency response, not just algebraic gamma.
        ticks=int(math.ceil(5.0*cfg_n.fs_hz))
        signal=LocalTravelingWaveDuct(cfg_n).impulse_lip_pressure(ticks)
        per={}
        for f in (200.,400.,600.,1000.,2600.):
            experimental=empirical_transfer_at_frequency(signal,cfg_n,f)
            analytic=continuum_analog_transfer(f,cfg_n)
            scattering=independent_discrete_scattering_transfer(f,cfg_n)
            per[str(f)]={
                "empirical_vs_analog_complex_relative":float(abs(experimental-analytic)/abs(analytic)),
                "discrete_vs_analog_complex_relative":float(abs(scattering-analytic)/abs(analytic)),
                "empirical_vs_discrete_complex_relative":float(abs(experimental-scattering)/abs(scattering)),
                "empirical_phase_rad":float(np.angle(experimental)),
            }
        comparisons[str(n)]=per
        # Compact raw impulse excerpts containing direct arrival and first reflection.
        data["b0_impulse_prefix_"+str(n)+".npy"]=signal[:4*cfg_n.n_cells].copy()
    out.mkdir(parents=True)
    digests={}
    for name,array in sorted(data.items()):
        binary=_raw_npy(array)
        (out/name).write_bytes(binary)
        digests[name]=hashlib.sha256(binary).hexdigest()
    manifest={
        "schema":"research.sa2b_b1b.v0",
        "preregistration_git_sha":PREREG_SHA,
        "exact_executed_git_sha":"VERIFY_FROM_CI_RECEIPT",
        "decision":"AWAITING_INDEPENDENT_A2_AUDIT",
        "adoption":"NOT_ADOPTED",
        "geometry":"uniform 0.16m calibration; lip area from M0; NOT full M0",
        "physics_clock_hz":{"2":68600,"4":137200,"8":274400},
        "audio_observer_48k":"NOT_IMPLEMENTED; cross-clock port NOT_VERIFIED",
        "one_way_seconds":cfg.one_way_s,
        "48k_equivalent_samples":cfg.one_way_s*48000,
        "first_arrival":fronts,
        "energy":energy,
        "complex_transfer":comparisons,
        "trace_columns":TRACE_COLUMNS,
        "sha256":digests,
        "voice_quality":"NOT_TESTED"
    }
    (out/"manifest.json").write_text(
        json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+"\n",
        encoding="utf-8")
    return manifest


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    result=experiment(args.out)
    print(json.dumps({"decision":result["decision"],
                      "arrival":result["first_arrival"],
                      "complex_transfer":result["complex_transfer"],
                      "energy":result["energy"]},indent=2,sort_keys=True))
