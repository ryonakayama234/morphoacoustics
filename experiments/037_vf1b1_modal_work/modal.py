"""VF-1B1 independent modal power observer for the frozen VF-1A symmetric model.

Research only. No new force, oscillator, acoustic processing, public contract or
species claim. Splits tissue mechanics into orthonormal +/- normal modes ONLY
when m1=m2, k1=k2, d1=d2 and pressure-area coefficients g1=g2.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

SQRT2 = math.sqrt(2.0)


def require_symmetric(tissue) -> tuple[float, float, float, float, float]:
    m1, m2 = tissue.masses_kg
    k1, k2 = tissue.stiffness_n_m
    d1, d2 = tissue.damping_n_s_m
    g1, g2 = tissue.pressure_areas_m2
    if (m1 != m2 or k1 != k2 or d1 != d2 or g1 != g2):
        raise ValueError("UNSUPPORTED_ASYMMETRIC_MODAL_DECOMPOSITION")
    return m1, k1, d1, g1, tissue.coupling_n_m


def coordinates(x, v) -> tuple[np.ndarray, np.ndarray]:
    x1, x2 = map(float, x)
    v1, v2 = map(float, v)
    return (np.array(((x1+x2)/SQRT2, (x1-x2)/SQRT2)),
            np.array(((v1+v2)/SQRT2, (v1-v2)/SQRT2)))


def energy(x, v, tissue) -> np.ndarray:
    m, k, _, _, kc = require_symmetric(tissue)
    xx, vv = coordinates(x, v)
    return 0.5*m*vv**2 + 0.5*np.array((k, k+2*kc))*xx**2


def midpoint_transition(tissue, dt_s: float) -> np.ndarray:
    """Independent exact amplification matrix for autonomous antisymmetric mode.

    Implicit-midpoint z' = [[0,1],[-(k+2kc)/m,-d/m]] z.
    """
    m, k, d, _, kc = require_symmetric(tissue)
    if not math.isfinite(dt_s) or dt_s <= 0:
        raise ValueError("INVALID_DT")
    a = np.array(((0., 1.), (-(k+2*kc)/m, -d/m)))
    identity = np.eye(2)
    return np.linalg.solve(identity - 0.5*dt_s*a,
                           identity + 0.5*dt_s*a)


@dataclass(frozen=True)
class ModalReceipt:
    energy_before_j: tuple[float, float]
    energy_after_j: tuple[float, float]
    pressure_work_j: tuple[float, float]
    damping_loss_j: tuple[float, float]
    residual_j: tuple[float, float]
    coordinate_after_m: tuple[float, float]
    velocity_after_m_s: tuple[float, float]
    antisym_midpoint_oracle_error: float


def observe_step(tissue, dt_s: float, x_before, v_before, output) -> ModalReceipt:
    """Observe a completed unchanged VF-1A step, independently of its ledger."""
    m, k, d, g, kc = require_symmetric(tissue)
    xb, vb = coordinates(x_before, v_before)
    xa, va = coordinates(output.x_m, output.v_m_s)
    velocity_mid = 0.5*(vb+va)
    eb = 0.5*m*vb**2 + 0.5*np.array((k,k+2*kc))*xb**2
    ea = 0.5*m*va**2 + 0.5*np.array((k,k+2*kc))*xa**2
    # g=(g,g). Its antisymmetric component is identically zero.
    force = np.array((SQRT2*g*output.pressure_mid_pa, 0.))
    work = dt_s*force*velocity_mid
    damping = dt_s*d*velocity_mid**2
    residual = (ea-eb)-work+damping
    predicted = midpoint_transition(tissue, dt_s) @ np.array((xb[1],vb[1]))
    oracle_error = float(np.linalg.norm(predicted-np.array((xa[1],va[1]))))
    def pair(a):
        return (float(a[0]),float(a[1]))
    return ModalReceipt(pair(eb),pair(ea),pair(work),pair(damping),
                        pair(residual),pair(xa),pair(va),oracle_error)


def independent_work_identity(tissue, dt_s, x_before, v_before, output) -> dict:
    """Recover full tissue pressure work without calling observe_step."""
    _, _, d, g, _ = require_symmetric(tissue)
    v0 = np.asarray(v_before, dtype=float)
    v1 = np.asarray(output.v_m_s, dtype=float)
    work = dt_s*output.pressure_mid_pa*g*float(np.sum((v0+v1)*0.5))
    loss = dt_s*d*float(np.sum(((v0+v1)*0.5)**2))
    full_delta = float(sum(energy(output.x_m,output.v_m_s,tissue))
                       -sum(energy(x_before,v_before,tissue)))
    return {"full_pressure_work_j":work, "full_damping_loss_j":loss,
            "full_mechanical_delta_j":full_delta,
            "full_identity_residual_j":full_delta-work+loss}
