"""EL-R1 research-only passive listener ear-canal acoustic port.

Uses Core UniformTube without changing Core physics or public contracts.
Peak phasors, exp(+i*omega*t), +U from entrance toward terminal.
NOT a human eardrum model or a time-domain audio filter.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite

import numpy as np

from morphoacoustics.acoustics.uniform_tube import UniformTube

MODEL_VERSION = "el-r1.passive.uniform.v0a1"  # audit amendment A1
ENTRANCE = "CANAL_ENTRANCE"
TERMINAL = "TERMINAL_SIDE"
DRIVE_KIND = "PRESCRIBED_TOTAL_ENTRANCE_PRESSURE"
LOAD_KIND = "PASSIVE_REAL_RESISTANCE"


class InvalidListener(ValueError):
    status = "INVALID"


class UnsupportedListener(ValueError):
    status = "UNSUPPORTED"


class NumericallyUnresolved(ArithmeticError):
    status = "NUMERICALLY_UNRESOLVED"


@dataclass(frozen=True, slots=True)
class ListenerFixture:
    length_m: float = 0.025
    section_area_m2: float = 3e-5
    air_density_kg_m3: float = 1.21
    sound_speed_m_s: float = 343.0
    terminal_resistance_ratio_to_zc: float = 2.0
    terminal_load_kind: str = LOAD_KIND


@dataclass(frozen=True, slots=True)
class EntranceDrive:
    frequencies_hz: tuple[float, ...] = (0, 1000, 3000, 7000)
    entrance_pressure_pa: complex = 1.0 + 0j
    source_fixture_id: str = "synthetic-prescribed-pressure-A"
    reference_plane: str = ENTRANCE
    excitation_kind: str = DRIVE_KIND


def _positive_finite(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidListener(f"{name}: real numeric value required")
    try:
        number = float(value)
    except (OverflowError, ValueError, TypeError) as exc:
        raise InvalidListener(f"{name}: cannot convert to finite float") from exc
    if not isfinite(number) or number <= 0:
        raise InvalidListener(f"{name}: finite and > 0 required")
    return number


def _bounded(name: str, value: float, low: float, high: float) -> None:
    if not (low <= value <= high):
        raise UnsupportedListener(f"{name}: outside EL-R1 research capability [{low},{high}]")


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(np.real(value)), "imag": float(np.imag(value))}


def evaluate(fixture: ListenerFixture, drive: EntranceDrive) -> dict[str, object]:
    """Solve a *total entrance pressure* boundary plus positive resistive load.

    Neither the incident-wave amplitude nor entrance volume flow is prescribed.
    Reports both planes' complex p/U and mean *active* acoustic power.
    """
    if not isinstance(fixture, ListenerFixture) or not isinstance(drive, EntranceDrive):
        raise InvalidListener("fixture and drive types required")
    length = _positive_finite("length_m", fixture.length_m)
    area = _positive_finite("section_area_m2", fixture.section_area_m2)
    rho = _positive_finite("air_density_kg_m3", fixture.air_density_kg_m3)
    c = _positive_finite("sound_speed_m_s", fixture.sound_speed_m_s)
    ratio = _positive_finite("terminal_resistance_ratio_to_zc", fixture.terminal_resistance_ratio_to_zc)
    _bounded("length_m", length, 0.01, 0.05)
    _bounded("section_area_m2", area, 1e-5, 1e-4)
    _bounded("terminal_resistance_ratio_to_zc", ratio, 0.25, 4)
    if fixture.terminal_load_kind != LOAD_KIND:
        if fixture.terminal_load_kind == "PASSIVE_COMPLEX_IMPEDANCE":
            raise UnsupportedListener("reactive terminal load not solved by EL-R1 v0")
        raise InvalidListener("unrecognized terminal_load_kind")
    if drive.reference_plane != ENTRANCE:
        raise InvalidListener("reference_plane must be CANAL_ENTRANCE")
    if drive.excitation_kind != DRIVE_KIND:
        if drive.excitation_kind == "PRESCRIBED_INCIDENT_PRESSURE":
            raise UnsupportedListener("incident-wave boundary not solved by EL-R1 v0")
        raise InvalidListener("unrecognized excitation_kind")
    if not isinstance(drive.source_fixture_id, str) or not drive.source_fixture_id.strip():
        raise InvalidListener("source_fixture_id must be nonempty")
    if not isinstance(drive.frequencies_hz, (tuple, list)) or not 1 <= len(drive.frequencies_hz) <= 128:
        raise InvalidListener("frequencies_hz must contain 1..128 samples")
    for f in drive.frequencies_hz:
        if isinstance(f, bool) or not isinstance(f, (float, int)):
            raise InvalidListener("frequencies_hz: finite nonnegative real required")
        try:
            converted = float(f)
        except (OverflowError, ValueError, TypeError) as exc:
            raise InvalidListener("frequencies_hz: numeric conversion failed") from exc
        if not isfinite(converted) or converted < 0:
            raise InvalidListener("frequencies_hz: finite nonnegative real required")
    try:
        fs = np.asarray(drive.frequencies_hz, dtype=float)
    except (OverflowError, ValueError, TypeError) as exc:
        raise InvalidListener("frequencies_hz: numeric conversion failed") from exc
    if np.any(np.diff(fs) <= 0):
        raise InvalidListener("frequencies_hz must strictly increase")
    if fs[-1] > 8000:
        raise UnsupportedListener("frequency beyond 8000 Hz research capability")
    if isinstance(drive.entrance_pressure_pa, bool) or not isinstance(drive.entrance_pressure_pa, (float, int, complex)):
        raise InvalidListener("entrance_pressure_pa must be numeric phasor")
    try:
        p0 = complex(drive.entrance_pressure_pa)
    except (OverflowError, ValueError, TypeError) as exc:
        raise InvalidListener("entrance_pressure_pa numeric conversion failed") from exc
    if not isfinite(p0.real) or not isfinite(p0.imag):
        raise InvalidListener("entrance_pressure_pa must be finite")
    # Audit amendment A1: conservative engineering small-signal envelope.
    # epsilon=|p0|/(rho*c^2) is dimensionless; threshold is not a physiological law.
    medium_pressure_scale = rho * c * c
    if not isfinite(medium_pressure_scale) or medium_pressure_scale <= 0:
        raise InvalidListener("medium pressure scale rho*c^2 must be representable and positive")
    epsilon = abs(p0) / medium_pressure_scale
    if not isfinite(epsilon):
        raise InvalidListener("nonfinite dimensionless pressure perturbation")
    if epsilon > 1e-3:
        raise UnsupportedListener("entrance pressure exceeds small-signal research envelope epsilon<=1e-3")

    tube = UniformTube(length_m=length, area_m2=area, air_density_kg_m3=rho, sound_speed_m_s=c)
    zc = tube.characteristic_impedance_pa_s_m3
    zt = ratio * zc
    if not all(isfinite(x) and x > 0 for x in (zc, zt)):
        raise InvalidListener("derived impedances must be finite and positive")
    matrix = tube.transfer_matrix(fs)
    a, b = matrix[:, 0, 0], matrix[:, 0, 1]
    cc, d = matrix[:, 1, 0], matrix[:, 1, 1]
    # p0 = (a*Zt+b)*UL. Load pL=Zt*UL; U0 is solved, never prescribed.
    denom = a * zt + b
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        ul = p0 / denom
        pl = zt * ul
        u0 = cc * pl + d * ul
        h = zt / denom
        zin = (a * zt + b) / (cc * zt + d)
        gamma0 = (zin - zc) / (zin + zc)
        pin = np.real(p0 * np.conjugate(u0)) / 2.0
        pout = np.real(pl * np.conjugate(ul)) / 2.0
    nums = [ul, pl, u0, h, zin, gamma0, pin, pout]
    if any(not np.all(np.isfinite(x)) for x in nums):
        raise NumericallyUnresolved("nonfinite physical observation")
    if np.max(np.abs(np.linalg.det(matrix) - 1)) > 1e-12:
        raise NumericallyUnresolved("transfer determinant inconsistent")
    for x, y in zip(pin, pout):
        if x < -1e-12 or y < -1e-12:
            raise NumericallyUnresolved("negative mean passive power")
        if abs(x - y) > 1e-10 * max(1e-12, abs(x), abs(y)):
            raise NumericallyUnresolved("nonconservative lossless acoustic power")

    fixture_data = {
        "listener": {"length_m": length, "section_area_m2": area,
                     "air_density_kg_m3": rho, "sound_speed_m_s": c,
                     "terminal_resistance_ratio_to_zc": ratio,
                     "terminal_load_kind": fixture.terminal_load_kind},
        "drive": {"source_fixture_id": drive.source_fixture_id,
                  "excitation_kind": drive.excitation_kind, "reference_plane": drive.reference_plane,
                  "entrance_pressure_pa": _complex_record(p0),
                  "frequencies_hz": fs.tolist()},
        "schema_version": MODEL_VERSION,
    }
    canonical = json.dumps(fixture_data, sort_keys=True, separators=(",", ":"), allow_nan=False)
    result: dict[str, object] = {
        "schema_version": MODEL_VERSION, "status": "RESEARCH_ONLY",
        "listener": fixture_data["listener"],
        "drive": {k: v for k, v in fixture_data["drive"].items() if k != "frequencies_hz"},
        "fixture_sha256": sha256(canonical.encode("utf-8")).hexdigest(),
        "planes": [ENTRANCE, TERMINAL],
        "phase_convention": "exp(+i*omega*t)", "phasor_scale": "peak",
        "linear_pressure_perturbation_ratio": float(epsilon),
        "linear_pressure_perturbation_limit": 1e-3,
        "frequencies": [],
    }
    rows = result["frequencies"]
    assert isinstance(rows, list)
    for i, frequency in enumerate(fs):
        # At f=0 the algebraic phasor solution is only a limit, not a DC
        # acoustic power observation (where the 1/2 factor is inapplicable).
        zero_limit = frequency == 0.0
        rows.append({
            "frequency_hz": float(frequency),
            "frequency_interpretation": "ZERO_FREQUENCY_LIMIT" if zero_limit else "HARMONIC_AC",
            "formal_phasor_power_limit_w": ({
                "entrance": float(pin[i]), "terminal": float(pout[i])
            } if zero_limit else None),
            "entrance": {"pressure_pa": _complex_record(p0),
                         "volume_velocity_m3_s": _complex_record(u0[i]),
                         "mean_active_power_w": None if zero_limit else float(pin[i])},
            "terminal": {"pressure_pa": _complex_record(pl[i]),
                         "volume_velocity_m3_s": _complex_record(ul[i]),
                         "mean_active_power_w": None if zero_limit else float(pout[i])},
            "characteristic_impedance_pa_s_m3": float(zc),
            "input_impedance_pa_s_m3": _complex_record(zin[i]),
            "transfer_pressure_terminal_per_entrance": _complex_record(h[i]),
            "entrance_reflection_coefficient": _complex_record(gamma0[i]),
            "power_residual_w": None if zero_limit else float(pin[i] - pout[i]),
        })
    return result
