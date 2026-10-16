"""OG-5 fixed passive 5-tube / 2-junction complex solver and v1 API facade.

The frozen Gate A/A1 contract governs prepare/restore/response. Gate C adoption
is recorded separately in the research receipts, never inferred from imports.
No arbitrary graph, wav, phonation or anatomical model.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import cast

import numpy as np
import numpy.typing as npt

from morphoacoustics.acoustics.uniform_tube import UniformTube

PORT_IDS = tuple(f"{n}.{side}" for n in "ABCDE" for side in ("in", "out"))
FREQUENCIES = frozenset((80., 250., 400., 733., 997., 1200., 2000., 4000.))
AREAS_C = frozenset((.00015, .0003, .0006))
SCALES = frozenset((1., .5, -1.))
P_REF = 1.372  # Pa
U_REF = 1e-6  # m^3/s
Z_REF = 1372000.  # Pa s/m^3
_EPS = np.finfo(np.float64).eps


class Tree5NumericalError(ValueError):
    """Internal trial error; not public Gate A Tree5Error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class Tree5PhysicalSample:
    frequency_hz: float
    port_ids: tuple[str, ...]
    pressure_pa: tuple[complex, ...]
    volume_flow_m3_s: tuple[complex, ...]
    mean_power_w: tuple[float, ...]
    condition_number_2: float
    scaled_linear_residual: float
    j1_scaled_pressure_residual: float
    j2_scaled_pressure_residual: float
    j1_scaled_flow_residual: float
    j2_scaled_flow_residual: float
    relative_power_defect: float


def _fixture_tubes(c_area_m2: float) -> tuple[UniformTube, ...]:
    """Create the *fixed* five-tube test fixture, not a public graph parser."""
    if type(c_area_m2) not in (int, float) or float(c_area_m2) not in AREAS_C:
        raise ValueError("unsupported Gate B1 C area")
    lengths = (.08, .09, .06, .07, .05)
    areas = (.0003, .0003, float(c_area_m2), .0003, .0006)
    return tuple(UniformTube(length_m=length, area_m2=area,
                             sound_speed_m_s=343., air_density_kg_m3=1.2)
                 for length, area in zip(lengths, areas))


def _system(tubes: tuple[UniformTube, ...], c_load_kind: str,
            scale: float, frequency_hz: float
            ) -> tuple[npt.NDArray[np.complex128], npt.NDArray[np.complex128]]:
    """Build coupled 20x20 system in frozen A1 row/column order.

    Columns: each organ's inlet P,Q then outlet P,Q in A..E order.
    Rows: two tube rows per organ, three J1, three J2, source, C,D,E loads.
    P=p/1.372 Pa and Q=U/1e-6 m^3/s.
    """
    if len(tubes) != 5 or c_load_kind not in ("matched", "rigid_closed") or \
            scale not in SCALES or float(frequency_hz) not in FREQUENCIES:
        raise ValueError("unsupported Gate B1 fixture")
    m = np.zeros((20, 20), dtype=np.complex128)
    b = np.zeros(20, dtype=np.complex128)
    for idx, tube in enumerate(tubes):
        t = tube.transfer_matrix(float(frequency_hz))
        k, row = idx * 4, idx * 2
        m[row, k], m[row, k + 2], m[row, k + 3] = 1., -t[0, 0], -t[0, 1] / Z_REF
        m[row + 1, k + 1] = 1.
        m[row + 1, k + 2], m[row + 1, k + 3] = -t[1, 0] * Z_REF, -t[1, 1]
    # J1: A.out=(B.in+C.in)
    m[10, 2], m[10, 4] = 1., -1.
    m[11, 2], m[11, 8] = 1., -1.
    m[12, 3], m[12, 5], m[12, 9] = 1., -1., -1.
    # J2: B.out=(D.in+E.in)
    m[13, 6], m[13, 12] = 1., -1.
    m[14, 6], m[14, 16] = 1., -1.
    m[15, 7], m[15, 13], m[15, 17] = 1., -1., -1.
    m[16, 1] = 1.
    b[16] = complex(1., .4) * scale
    for row, k, tube, load in ((17, 10, tubes[2], c_load_kind),
                               (18, 14, tubes[3], "matched"),
                               (19, 18, tubes[4], "matched")):
        if load == "rigid_closed":
            m[row, k + 1] = 1.
        else:
            m[row, k] = 1.
            m[row, k + 1] = -tube.characteristic_impedance_pa_s_m3 / Z_REF
    return m, b


def _certified_solution(m: npt.NDArray[np.complex128],
                        b: npt.NDArray[np.complex128]
                        ) -> tuple[npt.NDArray[np.complex128], float, float]:
    """Apply frozen SVD/rank/cond, no pseudoinverse or model fallback."""
    if m.shape != (20, 20) or b.shape != (20,) or not np.all(np.isfinite(m)) or not np.all(np.isfinite(b)):
        raise Tree5NumericalError("NUMERIC_NONFINITE")
    try:
        sigma = np.linalg.svd(m, compute_uv=False, full_matrices=True)
    except np.linalg.LinAlgError as exc:
        raise Tree5NumericalError("SOLVE_FAILED") from exc
    if sigma.shape != (20,) or not np.all(np.isfinite(sigma)):
        raise Tree5NumericalError("NUMERIC_NONFINITE")
    largest, smallest = float(sigma[0]), float(sigma[-1])
    if largest <= 0 or smallest <= 20 * _EPS * largest:
        raise Tree5NumericalError("MATRIX_RANK_DEFICIENT")
    condition = largest / smallest
    if not math.isfinite(condition) or condition > 1e4:
        raise Tree5NumericalError("MATRIX_ILL_CONDITIONED")
    try:
        x = np.linalg.solve(m, b)
    except np.linalg.LinAlgError as exc:
        raise Tree5NumericalError("SOLVE_FAILED") from exc
    if x.shape != (20,) or not np.all(np.isfinite(x)):
        raise Tree5NumericalError("NUMERIC_NONFINITE")
    residual = float(np.max(np.abs(m @ x - b)))
    if not math.isfinite(residual):
        raise Tree5NumericalError("NUMERIC_NONFINITE")
    if residual > 1e-12:
        raise Tree5NumericalError("RESIDUAL_TOO_LARGE")
    return cast(npt.NDArray[np.complex128], x), condition, residual


def _solve_fixture(c_area_m2: float, c_load_kind: str, scale: float,
                   frequency_hz: float) -> Tree5PhysicalSample:
    """Internal B1 experiment only; B2 must validate the versioned Blueprint."""
    tubes = _fixture_tubes(c_area_m2)
    m, b = _system(tubes, c_load_kind, scale, frequency_hz)
    x, condition, linear_residual = _certified_solution(m, b)
    p = x[0::2] * P_REF
    u = x[1::2] * U_REF
    watts = .5 * np.real(p * np.conj(u))
    j1p = float(max(abs(x[2] - x[4]), abs(x[2] - x[8])))
    j2p = float(max(abs(x[6] - x[12]), abs(x[6] - x[16])))
    j1u = float(abs(x[3] - x[5] - x[9]))
    j2u = float(abs(x[7] - x[13] - x[17]))
    floor = .5 * P_REF * U_REF * abs(scale)**2
    power = float(abs(watts[0] - watts[5] - watts[7] - watts[9]) /
                  max(abs(watts[0]), floor))
    metrics = (j1p, j2p, j1u, j2u, power)
    if not np.all(np.isfinite(watts)) or not all(math.isfinite(y) for y in metrics):
        raise Tree5NumericalError("NUMERIC_NONFINITE")
    if max(metrics[:4]) > 1e-10:
        raise Tree5NumericalError("RESIDUAL_TOO_LARGE")
    if watts[0] <= 0 or power > 1e-10 or watts[7] < -1e-10 * floor or \
            watts[9] < -1e-10 * floor or (c_load_kind == "matched" and watts[5] < -1e-10 * floor) or \
            (c_load_kind == "rigid_closed" and abs(watts[5]) > 1e-10 * floor):
        raise Tree5NumericalError("POWER_CHECK_FAILED")
    return Tree5PhysicalSample(
        frequency_hz=float(frequency_hz), port_ids=PORT_IDS,
        pressure_pa=tuple(complex(z) for z in p),
        volume_flow_m3_s=tuple(complex(z) for z in u),
        mean_power_w=tuple(float(w) for w in watts),
        condition_number_2=condition, scaled_linear_residual=linear_residual,
        j1_scaled_pressure_residual=j1p, j2_scaled_pressure_residual=j2p,
        j1_scaled_flow_residual=j1u, j2_scaled_flow_residual=j2u,
        relative_power_defect=power)

# B2 frozen public contract adapter (separate from numerical kernel).
from .tree5_contract import PreparedTree5, Tree5Error, decode_tree5_json, prepare_tree5, restore_tree5
