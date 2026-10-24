"""Experiment 051: lossless uniform-duct wave dynamics + exact B0 lip one-port.

RESEARCH ONLY; NOT Core public API, NOT a voice waveform synthesizer.
Prerecorded gate: docs/research/sa-2b-b1/GATE_A.md at 0241f5f2439e11fc6c9a7352af3a8a450dca2f94.
The source is an externally driven physical acoustic port, not a vocal fold.
"""
from __future__ import annotations

import argparse
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
GATE_A_SHA = "0241f5f2439e11fc6c9a7352af3a8a450dca2f94"
M0_LIP_AREA_M2 = 0.000804247719318987
RHO = 1.21
SOUND_C = 343.0
TUBE_LENGTH_M = 0.16
TRACE_COLUMNS = (
    "p_in_mid_Pa", "p_lip_mid_Pa", "U_in_mid_m3_s",
    "U_lip_mid_m3_s", "a_lip_in_Pa", "b_lip_out_Pa",
    "E_tube_J", "E_B0_J", "drive_work_J", "dissipation_J",
    "delta_total_E_J", "energy_residual_J",
)


def _b0_module():
    name = "sa2b_b0_research_original"
    if name in sys.modules:
        return sys.modules[name]
    path = ROOT / "experiments/050_b0_passive_radiation/run.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("B0 physical one-port unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def positive(name: str, value: float) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} is not a positive physical value")
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{name} is not a positive physical value") from exc
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be positive finite")
    return number


@dataclass(frozen=True)
class DuctConfig:
    cells: int = 16
    fs_hz: float = 48000.0
    area_m2: float = M0_LIP_AREA_M2
    length_m: float = TUBE_LENGTH_M
    rho: float = RHO
    c: float = SOUND_C
    termination: str = "b0"

    def __post_init__(self) -> None:
        if type(self.cells) is not int or self.cells < 2:
            raise ValueError("cells must be integer >= 2")
        for name in ("fs_hz", "area_m2", "length_m", "rho", "c"):
            positive(name, getattr(self, name))
        if self.termination not in ("closed", "matched", "b0"):
            raise ValueError("unsupported passive physical termination")

    @property
    def dx(self) -> float:
        return self.length_m / self.cells

    @property
    def h(self) -> float:
        return 1 / self.fs_hz

    @property
    def courant(self) -> float:
        return self.c * self.h / self.dx

    @property
    def zc(self) -> float:
        return self.rho * self.c / self.area_m2


@dataclass(frozen=True)
class Sample:
    inlet_pressure_mid_pa: float
    lip_pressure_mid_pa: float
    inlet_volume_flow_mid_m3_s: float
    lip_volume_flow_mid_m3_s: float
    lip_incident_pa: float
    lip_reflected_pa: float
    tube_energy_j: float
    mouth_energy_j: float
    drive_work_j: float
    dissipated_j: float
    delta_total_energy_j: float
    energy_residual_j: float


class UniformDuct:
    """Finite-volume port-Hamiltonian duct with midpoint time integration.

    Cell pressures and internal face flows are independent physical states.
    B0 q is an extra stored-energy state; no wave delay is rounded to samples.
    """
    def __init__(self, config: DuctConfig, *, initial_pressure_pa: np.ndarray | None = None):
        self.config = config
        self.b0 = _b0_module().parameters_from_area(
            config.area_m2, rho=config.rho, c=config.c, fs=config.fs_hz
        ) if config.termination == "b0" else None
        n = config.cells
        capacitance = config.area_m2 * config.dx / (config.rho * config.c**2)
        face_inertance = config.rho * config.dx / config.area_m2
        with_mouth = config.termination == "b0"
        nstate = 2*n - 1 + int(with_mouth)
        matrix = np.zeros((nstate, nstate), dtype=np.float64)
        injection = np.zeros(nstate, dtype=np.float64)
        injection[0] = 1 / capacitance
        for i in range(n):
            if i > 0:
                matrix[i, n + i - 1] += 1 / capacitance
            if i < n - 1:
                matrix[i, n + i] -= 1 / capacitance
        for j in range(n - 1):
            matrix[n+j, j] += 1 / face_inertance
            matrix[n+j, j+1] -= 1 / face_inertance
        if config.termination == "matched":
            matrix[n-1, n-1] -= 1 / (capacitance * config.zc)
        elif with_mouth:
            assert self.b0 is not None
            matrix[n-1, n-1] -= 1 / (capacitance * self.b0.resistance_pa_s_m3)
            matrix[n-1, -1] -= 1 / capacitance
            matrix[-1, n-1] += 1 / self.b0.inertance_pa_s2_m3

        weights = np.concatenate([
            np.full(n, capacitance),
            np.full(n-1, face_inertance),
            np.array([self.b0.inertance_pa_s2_m3]) if with_mouth else np.empty(0),
        ])
        h = config.h
        ident = np.eye(nstate)
        left = ident - 0.5*h*matrix
        # Matrix inverse is NOT recomputed per audio sample. These matrices
        # implement the exact implicit-midpoint linear system, not an EQ.
        combined_rhs = np.column_stack((ident + 0.5*h*matrix, h*injection))
        solved = np.linalg.solve(left, combined_rhs)
        self.transition = solved[:, :nstate]
        self.drive = solved[:, -1]
        self.matrix = matrix
        self.injection = injection
        self.weights = weights
        self.state = np.zeros(nstate, dtype=np.float64)
        if initial_pressure_pa is not None:
            pressure = np.asarray(initial_pressure_pa, dtype=np.float64)
            if pressure.shape != (n,) or not np.isfinite(pressure).all():
                raise ValueError("initial pressure must be finite, one per cell")
            self.state[:n] = pressure

    def energy(self, state: np.ndarray | None = None) -> float:
        x = self.state if state is None else state
        return float(0.5 * np.dot(self.weights, x*x))

    def step(self, inlet_flow_mid_m3_s: float) -> Sample:
        if isinstance(inlet_flow_mid_m3_s, (bool, np.bool_)):
            raise ValueError("invalid volume flow")
        uin = float(inlet_flow_mid_m3_s)
        if not math.isfinite(uin):
            raise ValueError("nonfinite inlet flow")
        old = self.state
        new = self.transition @ old + self.drive * uin
        mid = (old + new) * 0.5
        if not np.isfinite(new).all():
            raise FloatingPointError("nonfinite wave state")
        n = self.config.cells
        pin, plip = float(mid[0]), float(mid[n-1])
        qold_energy = self.energy(old)
        qnew_energy = self.energy(new)
        b0_energy_new = 0.0
        if self.b0:
            outlet = float(mid[-1] + plip/self.b0.resistance_pa_s_m3)
            dissipation = self.config.h*plip**2/self.b0.resistance_pa_s_m3
            b0_energy_new = 0.5*self.b0.inertance_pa_s2_m3*new[-1]**2
            a = 0.5*(plip + self.config.zc*outlet)
            b = plip-a
        elif self.config.termination == "matched":
            outlet = plip/self.config.zc
            dissipation = self.config.h*plip**2/self.config.zc
            a = b = 0.0
        else:
            outlet = dissipation = a = b = 0.0
        work = self.config.h*pin*uin
        delta = qnew_energy-qold_energy
        residual = delta-work+dissipation
        if not all(map(math.isfinite, (outlet,dissipation,a,b,work,delta,residual))):
            raise FloatingPointError("nonfinite port power")
        self.state = new
        return Sample(pin, plip, uin, outlet, a, b,
                      qnew_energy-b0_energy_new, b0_energy_new,
                      work, dissipation, delta, residual)

    def trace(self, inlet: np.ndarray) -> np.ndarray:
        signal = np.asarray(inlet, dtype=np.float64)
        if signal.ndim != 1 or not np.isfinite(signal).all():
            raise ValueError("inlet must be finite 1D volume-flow sequence")
        rows = np.zeros((len(signal),len(TRACE_COLUMNS)), dtype=np.float64)
        for j,u in enumerate(signal):
            rows[j,:] = tuple(vars(self.step(float(u))).values())
        return rows


def continuum_b0_transfer(f_hz: float, config: DuctConfig) -> complex:
    """Independent analytic 2-port uniform tube with analog B0 lip impedance."""
    if config.termination != "b0":
        raise ValueError("B0 continuum reference requires B0")
    b0 = _b0_module()
    p = b0.parameters_from_area(config.area_m2, rho=config.rho,
                                c=config.c, fs=config.fs_hz)
    freq = positive("reference frequency", f_hz)
    omega = 2*math.pi*freq
    lip_z = complex(b0.analog_impedance(1j*omega, p))
    kL = omega*config.length_m/config.c
    return 1 / (1j*math.sin(kL)/config.zc + math.cos(kL)/lip_z)


def midpoint_transfer(f_hz: float, duct: UniformDuct) -> complex:
    """Exact digital frequency response of *different* semi-discrete equations."""
    fs = duct.config.fs_hz
    f = positive("digital frequency", f_hz)
    if not f < fs/2:
        raise ValueError("frequency beyond Nyquist")
    s = 2j*fs*math.tan(math.pi*f/fs)
    z = np.linalg.solve(s*np.eye(len(duct.state))-duct.matrix, duct.injection)
    return complex(z[duct.config.cells-1])


def modal_frequency_hz(c: DuctConfig) -> float:
    spatial_omega = 2*c.c/c.dx*math.sin(math.pi/(2*c.cells))
    return c.fs_hz/math.pi*math.atan(spatial_omega/(2*c.fs_hz))


def energy_gate(rows: np.ndarray, *,initial_energy_j: float = 0.) -> dict:
    r = np.asarray(rows, dtype=np.float64)
    if r.ndim != 2 or r.shape[1] != len(TRACE_COLUMNS) or not np.isfinite(r).all():
        raise ValueError("bad trace")
    d, w, loss, residual = r[:,10], r[:,8], r[:,9], r[:,11]
    tolerance = 1e-8*np.maximum.reduce((abs(d),abs(w),abs(loss),
                                         np.full(len(r), 1e-20)))
    if not np.all(abs(residual) <= tolerance):
        raise AssertionError("energy: per-sample balance failed")
    cumulative = abs(float(np.sum(residual)))
    allowed = 1e-8*max(float(sum(abs(w))+sum(abs(loss))), 1e-20)
    if cumulative > allowed:
        raise AssertionError("energy: cumulative balance failed")
    if np.any(loss < 0) or np.any(r[:,6] < 0) or np.any(r[:,7] < 0):
        raise AssertionError("negative physical energy or loss")
    return {
        "normalized_max_sample_residual": float(max(abs(residual)/tolerance)) if len(r) else 0.0,
        "absolute_cumulative_residual_j": cumulative,
        "sum_abs_work_j": float(sum(abs(w))),
        "sum_dissipation_j": float(sum(loss)),
        "initial_energy_j": initial_energy_j,
    }


def _npy_bytes(array: np.ndarray) -> bytes:
    buffer=io.BytesIO()
    np.save(buffer,np.asarray(array),allow_pickle=False)
    return buffer.getvalue()


def experiment(out: Path) -> dict:
    if out.exists():
        raise FileExistsError("never replace experimental evidence")
    rng = np.random.default_rng(20261024)
    rows = {}
    gates = {}
    for terminal in ("closed", "matched", "b0"):
        cfg = DuctConfig(termination=terminal)
        duct = UniformDuct(cfg)
        excitation = np.zeros(1024)
        excitation[:128] = rng.normal(scale=1e-6, size=128)
        trace = duct.trace(excitation)
        gates[terminal] = energy_gate(trace)
        rows[terminal+"_port_trace.npy"] = trace
    phases = {}
    error_by_resolution = {}
    for n,fs in ((16,48000),(32,96000),(64,192000)):
        cfg=DuctConfig(cells=n,fs_hz=fs,termination="b0")
        duct=UniformDuct(cfg)
        errors={}
        for f in (200,400,600):
            actual=midpoint_transfer(f,duct)
            exact=continuum_b0_transfer(f,cfg)
            errors[str(f)] = {
                "complex_relative": float(abs(actual-exact)/abs(exact)),
                "phase_error_rad": float(np.angle(actual/exact)),
                "analytic_abs_pa_per_m3_s": float(abs(exact)),
            }
        error_by_resolution[f"{n}@{fs}"]=errors
        phases[f"{n}@{fs}"]={
            "Courant":cfg.courant,
            "modal_frequency_hz":modal_frequency_hz(cfg),
            "modal_continuum_hz":cfg.c/(2*cfg.length_m),
        }
    out.mkdir(parents=True)
    digests={}
    for name,array in sorted(rows.items()):
        data=_npy_bytes(array)
        (out/name).write_bytes(data)
        digests[name]=hashlib.sha256(data).hexdigest()
    result={
        "schema":"research.sa2b_b1.v0",
        "decision":"B1_EXPERIMENT_EXECUTED_AWAITING_INDEPENDENT_CI_AUDIT",
        "adoption":"NOT_ADOPTED", "b2_b3_vf1":"NOT_RUN",
        "preregistration_commit":GATE_A_SHA,
        "exact_executed_git_sha":"VERIFY_EXTERNAL_GITHUB_ACTIONS_RECEIPT",
        "geometry":"uniform calibration 0.16m; NOT genuine sectionwise M0",
        "B0_origin":"research/sa2b-b0-passive-radiation-20261024",
        "area_m2":M0_LIP_AREA_M2,
        "one_way_transit_seconds":TUBE_LENGTH_M/SOUND_C,
        "samples_one_way_at_48k":48000*TUBE_LENGTH_M/SOUND_C,
        "ten_mm_samples_at_48k":48000*.01/SOUND_C,
        "trace_columns":TRACE_COLUMNS,
        "energy_gates":gates,
        "grid_phase":phases,
        "transfer_errors":error_by_resolution,
        "sha256":digests,
        "human_voice_quality":"NOT_TESTED",
        "studio_audition":"NOT_TESTED",
    }
    (out/"manifest.json").write_text(
        json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    result = experiment(parser.parse_args().out)
    print(json.dumps({
        "decision":result["decision"], "energy_gates":result["energy_gates"],
        "grid_phase":result["grid_phase"], "transfer_errors":result["transfer_errors"],
    }, indent=2, sort_keys=True))
