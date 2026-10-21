"""NV1-EAR W1: preregistered, uncalibrated, physically conditioned breath surrogate.

This is an experiment-local equivalent monopole, NOT a human breath / CFD / voice model.
Wolfram independent pure-algebra oracle: docs/research/nv1-breath-to-ear/PREREGISTRATION.md
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math

import numpy as np
from scipy.signal import stft, istft

FS = 48_000
DURATION_S = 2.4
N = 115_200
RHO = 1.2
MU = 1.8e-5
C = 343.0
CD = 0.65
SEED = 133_041
EPSILON = 0.002
MAX_POWER_EFFICIENCY = 0.01
SCHEMA = "nv1-breath-ear.evidence.v0"
# Pressure in Pa, effective aperture in m²: *experimental* actuation fixtures.
PRESETS = {"P0": (120.0, 30e-6), "P2": (240.0, 30e-6),
           "A2": (120.0, 60e-6), "Z0": (0.0, 30e-6)}


@dataclass(frozen=True)
class FlowTrace:
    pressure_pa: np.ndarray
    aperture_m2: np.ndarray
    q_mean_m3_s: np.ndarray
    jet_speed_m_s: np.ndarray
    reynolds: np.ndarray
    pneumatic_power_w: np.ndarray
    diameter_m: float


@dataclass(frozen=True)
class SourceTrace:
    q_ac_m3_s: np.ndarray
    dq_dt_m3_s2: np.ndarray
    spectral_knee_hz: np.ndarray
    ideal_acoustic_power_w: float
    mean_pneumatic_power_w: float
    efficiency: float
    source_sha256: str


def _finite_nonnegative(name: str, x: float) -> float:
    if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or x < 0:
        raise ValueError(f"INVALID: {name} must be nonnegative finite")
    return float(x)


def steady_orifice(pressure_pa: float, aperture_m2: float) -> tuple[float, float, float, float]:
    """Q [m³/s], jet speed [m/s], Reynolds [-], pressure power [W]."""
    pressure = _finite_nonnegative("pressure_pa", pressure_pa)
    area = _finite_nonnegative("aperture_m2", aperture_m2)
    if not 15e-6 <= area <= 60e-6:
        raise ValueError("UNSUPPORTED: aperture outside research fixture")
    if pressure > 240:
        raise ValueError("UNSUPPORTED: pressure outside research fixture")
    diameter = math.sqrt(4 * area / math.pi)
    speed = CD * math.sqrt(2 * pressure / RHO)
    q = area * speed
    return q, speed, RHO * speed * diameter / MU, pressure * q


def realize_exhale(pressure_peak_pa: float, aperture_m2: float) -> FlowTrace:
    steady_orifice(pressure_peak_pa, aperture_m2)  # strict fail-closed validation
    time = np.arange(N, dtype=np.float64) / (N - 1)
    envelope = np.sin(np.pi * time) ** 2
    pressure = float(pressure_peak_pa) * envelope
    area = np.full(N, aperture_m2, dtype=np.float64)
    speed = CD * np.sqrt(2.0 * pressure / RHO)
    q = area * speed
    diameter = math.sqrt(4.0 * aperture_m2 / math.pi)
    reynolds = RHO * speed * diameter / MU
    power = pressure * q
    return FlowTrace(pressure, area, q, speed, reynolds, power, diameter)


def source_from_flow(flow: FlowTrace, seed: int = SEED) -> SourceTrace:
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32:
        raise ValueError("INVALID: seed must be unsigned 32-bit integer")
    if any(len(x) != N or not np.isfinite(x).all() for x in (
        flow.pressure_pa, flow.q_mean_m3_s, flow.jet_speed_m_s, flow.reynolds,
        flow.pneumatic_power_w,
    )):
        raise ValueError("INVALID: nonfinite or wrong-size flow trace")
    mean_power = float(np.mean(flow.pneumatic_power_w))
    if mean_power == 0.0:
        qac = np.zeros(N, dtype=np.float64)
        knee = np.zeros(N, dtype=np.float64)
    else:
        noise = np.random.Generator(np.random.PCG64(seed)).standard_normal(N)
        freqs, frames, coeff = stft(
            noise, fs=FS, window="hann", nperseg=2048, noverlap=1536,
            nfft=2048, detrend=False, return_onesided=True,
            boundary="zeros", padded=True, scaling="spectrum")
        speed_frames = np.interp(frames, np.arange(N) / FS, flow.jet_speed_m_s,
                                 left=0.0, right=0.0)
        st_knee = np.where(speed_frames > 0, 1.2 * speed_frames / flow.diameter_m, 0.0)
        ff = freqs[:, None]
        hp = ff / np.sqrt(ff**2 + 300.0**2)
        lp = 1.0 / np.sqrt(1.0 + (ff / 9000.0)**8)
        stshape = np.zeros((len(freqs), len(frames)), dtype=np.float64)
        np.divide(st_knee[None, :], np.sqrt(st_knee[None, :]**2 + ff**2),
                  out=stshape, where=st_knee[None, :] > 0)
        _, shaped = istft(
            coeff * hp * lp * stshape, fs=FS, window="hann",
            nperseg=2048, noverlap=1536, nfft=2048, input_onesided=True,
            boundary=True, scaling="spectrum")
        if len(shaped) < N:
            raise ValueError("INVALID: insufficient inverse STFT samples")
        gate = np.clip((flow.reynolds - 1000.0) / 2000.0, 0.0, 1.0)
        qac = EPSILON * flow.q_mean_m3_s * gate * shaped[:N]
        qac[0] = qac[-1] = 0.0
        knee = 1.2 * flow.jet_speed_m_s / flow.diameter_m
    derivative = np.gradient(qac, 1.0 / FS, edge_order=2)
    acoustic_power = RHO / (4 * math.pi * C) * float(np.mean(derivative**2))
    efficiency = acoustic_power / mean_power if mean_power > 0 else 0.0
    if not np.isfinite(qac).all() or not np.isfinite(derivative).all() or not math.isfinite(efficiency):
        raise ValueError("INVALID: nonfinite source")
    if efficiency > MAX_POWER_EFFICIENCY:
        raise ValueError(f"INFEASIBLE: uncalibrated equivalent source exceeds power budget ({efficiency:.4g})")
    digest = hashlib.sha256(qac.astype("<f8", copy=False).tobytes()).hexdigest()
    return SourceTrace(qac, derivative, knee, acoustic_power, mean_power, efficiency, digest)


def describe_spectrum(x: np.ndarray) -> dict[str, float]:
    """Comparable two-sided energy ratios, not a perception/naturalness score."""
    if len(x) != N:
        raise ValueError("INVALID: spectrum input length")
    sp = abs(np.fft.rfft(x)) ** 2
    hz = np.fft.rfftfreq(len(x), 1 / FS)
    total = float(np.sum(sp))
    if total == 0:
        return {"over_2khz_fraction": 0.0, "five_k_over_one_k_db": 0.0}
    def band(lo: float, hi: float) -> float:
        return float(np.mean(sp[(hz >= lo) & (hz < hi)]))
    p1, p5 = band(850, 1150), band(4850, 5150)
    return {"over_2khz_fraction": float(np.sum(sp[hz >= 2000]) / total),
            "five_k_over_one_k_db": 10 * math.log10(max(p5, 1e-300) / max(p1, 1e-300))}
