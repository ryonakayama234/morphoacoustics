"""VF-1B2 C1-R0: sealed isentropic two-coordinate *mathematical control*.

No throughflow, spatial gas pressure gradient, tract coupling, biological source
or audio output is modeled here. This is NOT a physical phonator.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path


@dataclass(frozen=True)
class Fixture:
    L_g_m: float = 0.010
    ell_m: float = 0.010
    half_gap_m: float = 0.00020
    gamma: float = 1.4
    P0_abs_Pa: float = 101325.0
    Pext_abs_Pa: float = 101325.0
    rho0_kg_m3: float = 1.2
    m_L_kg: float = 0.0001
    m_U_kg: float = 0.0001
    k_L_N_m: float = 150.0
    k_U_N_m: float = 220.0
    k_c_N_m: float = 40.0
    d_L_Ns_m: float = 0.02
    d_U_Ns_m: float = 0.03
    x_L0_m: float = 3.0e-6
    x_U0_m: float = -1.0e-6
    v_L0_m_s: float = 0.0
    v_U0_m_s: float = 0.0


def physical_state(y: tuple[float, ...], f: Fixture) -> tuple[float, float, float]:
    x_l, x_u, _, _ = y
    if min(f.half_gap_m + x_l, f.half_gap_m + x_u) <= 0:
        raise ValueError("UNSUPPORTED_CONTACT")
    v0 = 2.0 * f.ell_m * f.L_g_m * f.half_gap_m
    v = v0 + f.ell_m * f.L_g_m * (x_l + x_u)
    if v <= 0 or not math.isfinite(v):
        raise ValueError("INVALID_VOLUME")
    p = f.P0_abs_Pa * (v0 / v) ** f.gamma
    rho = f.rho0_kg_m3 * v0 / v
    if not (math.isfinite(p) and math.isfinite(rho) and p > 0 and rho > 0):
        raise ValueError("INVALID_GAS")
    return v, p, rho


def derivative(y: tuple[float, ...], f: Fixture) -> tuple[float, ...]:
    x_l, x_u, v_l, v_u = y
    _, p, _ = physical_state(y, f)
    air_force = f.ell_m * f.L_g_m * (p - f.Pext_abs_Pa)
    return (
        v_l, v_u,
        (air_force - f.k_L_N_m * x_l - f.k_c_N_m * (x_l - x_u) - f.d_L_Ns_m * v_l) / f.m_L_kg,
        (air_force - f.k_U_N_m * x_u - f.k_c_N_m * (x_u - x_l) - f.d_U_Ns_m * v_u) / f.m_U_kg,
    )


def rk4_step(y: tuple[float, ...], dt: float, f: Fixture) -> tuple[float, ...]:
    k1 = derivative(y, f)
    k2 = derivative(tuple(a + dt * b / 2 for a, b in zip(y, k1)), f)
    k3 = derivative(tuple(a + dt * b / 2 for a, b in zip(y, k2)), f)
    k4 = derivative(tuple(a + dt * b for a, b in zip(y, k3)), f)
    out = tuple(a + dt * (p + 2 * q + 2 * r + s) / 6
                for a, p, q, r, s in zip(y, k1, k2, k3, k4))
    physical_state(out, f)
    return out


def simulate(f: Fixture, dt_s: float, duration_s: float = 0.006) -> dict:
    if not (math.isfinite(dt_s) and dt_s > 0 and math.isfinite(duration_s) and duration_s > 0):
        raise ValueError("INVALID_TIME")
    if f.gamma <= 1 or min(f.m_L_kg, f.m_U_kg, f.half_gap_m, f.rho0_kg_m3, f.P0_abs_Pa) <= 0:
        raise ValueError("INVALID_FIXTURE")
    if min(f.k_L_N_m, f.k_U_N_m, f.k_c_N_m, f.d_L_Ns_m, f.d_U_Ns_m) < 0:
        raise ValueError("INVALID_MATERIAL")
    steps_exact = duration_s / dt_s
    n = round(steps_exact)
    if n <= 0 or abs(steps_exact - n) > 1e-8:
        raise ValueError("NONINTEGER_TIME_GRID")
    y = (f.x_L0_m, f.x_U0_m, f.v_L0_m_s, f.v_U0_m_s)
    samples = []
    for k in range(n + 1):
        volume, pressure, density = physical_state(y, f)
        samples.append({"t_s": k * dt_s, "x_m": list(y[:2]), "v_m_s": list(y[2:]),
                        "V_m3": volume, "p_abs_Pa": pressure, "rho_kg_m3": density})
        if k != n:
            y = rk4_step(y, dt_s, f)
    return {"schema": "vf1b2.c1r0.sealed.v0-research", "fixture": asdict(f),
            "dt_s": dt_s, "duration_s": duration_s, "samples": samples}


def midpoint_linear_force(n: int, b_pa: float, a_pa: float, L_g_m: float, ell_m: float) -> tuple[float, float]:
    if n < 1:
        raise ValueError("INVALID_GRID")
    dz = L_g_m / n
    lower = upper = 0.0
    for i in range(n):
        fraction = (i + 0.5) / n
        pressure = b_pa + a_pa * fraction
        lower += pressure * (1 - fraction) * (2 * ell_m) * dz
        upper += pressure * fraction * (2 * ell_m) * dz
    return lower, upper


def save_trace(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")), encoding="utf-8")
