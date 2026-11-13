"""Loaded outlet-to-inlet cascades, internal [p,U], reciprocal two-port scattering."""
from __future__ import annotations

import cmath
import math
import numpy as np
from ..prereg_binding import (RHO, C, R_PROXY_M, FREQUENCIES_HZ,
                              Refusal, require, validate_envelope, validate_lambda)
from .coefficients import coefficients


def _section_matrix(gamma: complex, zc: complex, length: float) -> np.ndarray:
    co, si = cmath.cosh(gamma * length), cmath.sinh(gamma * length)
    return np.array([[co, zc * si], [si / zc, co]], dtype=np.complex128)


def one_frequency(f: int, radii: tuple[float, ...], lengths: tuple[float, ...], loss: float) -> dict:
    zstar = RHO * C / (math.pi * radii[0] ** 2)
    load_r = 0.05 * RHO * C / (math.pi * radii[-1] ** 2)
    entries = [coefficients(f, radius, loss) for radius in radii]
    matrices = [_section_matrix(e[2], e[3], length) for e, length in zip(entries, lengths, strict=True)]
    total = np.eye(2, dtype=np.complex128)
    for section in matrices:
        total = total @ section
    a, b, c, d = total[0, 0], total[0, 1], total[1, 0], total[1, 1]
    denom = c * load_r + d
    require(abs(denom) >= 1e-12, "NUMERICALLY_UNRESOLVED", "near-pole loaded transfer")
    hu = 1 / denom
    zin = (a * load_r + b) / denom
    hp = (1j * 2 * math.pi * f * RHO / (4 * math.pi * R_PROXY_M)) * (
        cmath.exp(-1j * 2 * math.pi * f * R_PROXY_M / C)) * hu
    # Downstream port reference U>0 in physical flow direction.
    states = [None] * (len(matrices) + 1)
    states[-1] = np.array([load_r * hu, hu], dtype=np.complex128)
    for i in reversed(range(len(matrices))):
        states[i] = matrices[i] @ states[i + 1]
    require(abs(states[0][1] - 1) <= 1e-9, "NUMERICALLY_UNRESOLVED",
            "reverse p/U reconstruction not normalized to Uin=1")
    # Two-port power-wave scattering with *equal* positive reference Rref.
    sum_d = a + b / zstar + c * zstar + d
    require(abs(sum_d) >= 1e-12, "NUMERICALLY_UNRESOLVED", "scattering pole")
    det = a * d - b * c
    scatter = np.array([
        [(a + b / zstar - c * zstar - d) / sum_d,
         2 * det / sum_d],
        [2 / sum_d, (-a + b / zstar - c * zstar + d) / sum_d]
    ], dtype=np.complex128)
    require(bool(np.all(np.isfinite(total))) and bool(np.all(np.isfinite(scatter))),
            "NUMERICALLY_UNRESOLVED", "nonfinite network transfer")
    return {"f": f, "z": np.array([e[0] for e in entries]),
            "y": np.array([e[1] for e in entries]),
            "gamma": np.array([e[2] for e in entries]),
            "zc": np.array([e[3] for e in entries]),
            "sections": np.array(matrices),
            "T": total, "detT": det, "HU": hu, "Zin": zin, "Hp": hp,
            "S": scatter, "states": np.array(states),
            "Zstar": zstar, "load_R": load_r}


def compute_case(radii: tuple[float, ...], lengths: tuple[float, ...], loss: float) -> dict:
    validate_envelope(radii, lengths)
    validate_lambda(loss)
    bins = [one_frequency(f, radii, lengths, loss) for f in FREQUENCIES_HZ]
    keys = ("z", "y", "gamma", "zc", "sections", "T", "detT",
            "HU", "Zin", "Hp", "S", "states")
    return {**{key: np.asarray([b[key] for b in bins]) for key in keys},
            "frequency_hz": np.array(FREQUENCIES_HZ, dtype=np.int32),
            "radii_m": tuple(radii), "lengths_m": tuple(lengths),
            "lambda": loss, "Zstar": bins[0]["Zstar"], "load_R": bins[0]["load_R"]}
