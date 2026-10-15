"""Independent analytical oracle: no UniformTube, graph matrix or production solver."""
from __future__ import annotations
import numpy as np


def tube_load(length: float, area: float, frequency: float, kind: str, load: complex,
              rho: float = 1.2, speed: float = 343.) -> complex:
    z = rho * speed / area
    q = np.tan(2 * np.pi * frequency * length / speed)
    if kind == "rigid_closed":
        return complex(-1j * z / q)
    return complex(z * (load + 1j*z*q) / (z + 1j*load*q))


def port_states(area_ratio: float, frequency: float, load_c: str, scale: complex = 1.) -> dict:
    """Fixed protocol fixture, scalar impedance recursion + explicit phase propagation."""
    lengths = (.08, .09, .06)
    areas = (3e-4, 3e-4, 3e-4 * area_ratio)
    zs = [1.2 * 343 / s for s in areas]
    phases = [2 * np.pi * frequency * l / 343 for l in lengths]
    c_load = zs[2] if load_c == "matched" else zs[0] if load_c == "fixed_impedance" else 0j
    zb = tube_load(lengths[1], areas[1], frequency, "matched", zs[1])
    zc = tube_load(lengths[2], areas[2], frequency, load_c, c_load)
    junction_load = 1 / (1/zb + 1/zc)
    zin = tube_load(lengths[0], areas[0], frequency, "impedance", junction_load)
    uin = 1e-6 * (1 + .4j) * scale
    pin = zin * uin
    pj = np.cos(phases[0]) * pin - 1j * zs[0] * np.sin(phases[0]) * uin
    ua = -1j * np.sin(phases[0]) * pin / zs[0] + np.cos(phases[0]) * uin
    ub, uc = pj / zb, pj / zc
    result = {"A.in": (pin, uin), "A.out": (pj, ua), "B.in": (pj, ub), "C.in": (pj, uc)}
    for i, name, flow in ((1, "B", ub), (2, "C", uc)):
        result[f"{name}.out"] = (
            np.cos(phases[i]) * pj - 1j * zs[i] * np.sin(phases[i]) * flow,
            -1j * np.sin(phases[i]) * pj / zs[i] + np.cos(phases[i]) * flow,
        )
    return result


def scatter_matrix(areas: tuple[float, float, float]) -> np.ndarray:
    y = np.asarray(areas)
    return 2 * np.tile(y / np.sum(y), (3, 1)) - np.eye(3)


def state_error(actual: dict, expected: dict, p_ref: float, u_ref: float = 1e-6) -> float:
    return float(max(abs(actual[key][i] - expected[key][i]) / (p_ref if i == 0 else u_ref)
                     for key in expected for i in (0, 1)))
