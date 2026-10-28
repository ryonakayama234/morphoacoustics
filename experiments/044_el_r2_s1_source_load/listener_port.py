"""EL-R2-S1 Gate B: research-only finite-source / absolute-load boundary solve.

This is *not* a measured ear, ASMR renderer, or public Morphoacoustics API.
The propagation law belongs solely to Core UniformTube; this module solves
research-only boundary algebra and records complex port/mean-power observations.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, pi, sin
from numbers import Real
from sys import float_info
from typing import Literal

from morphoacoustics.acoustics.uniform_tube import UniformTube

Category = Literal["INVALID", "UNSUPPORTED", "NUMERICALLY_UNRESOLVED"]


class ResearchBoundaryError(ValueError):
    """Typed refusal: input or numerical status, NOT a science verdict."""

    def __init__(self, category: Category, field: str, reason: str) -> None:
        super().__init__(f"{category} {field}: {reason}")
        self.category = category
        self.field = field
        self.reason = reason


@dataclass(frozen=True, slots=True)
class Fixture:
    area_m2: float
    length_m: float
    frequency_hz: float
    source_pressure_pa: complex = 1.0 + 0j
    source_impedance_pa_s_m3: float = 13834333.333333334
    terminal_impedance_pa_s_m3: float = 27668666.666666668
    air_density_kg_m3: float = 1.21
    sound_speed_m_s: float = 343.0


@dataclass(frozen=True, slots=True)
class PortObservation:
    p0_pa: complex
    u0_m3_s: complex
    pL_pa: complex
    uL_m3_s: complex
    zc_pa_s_m3: float
    zin_pa_s_m3: complex | None
    gamma_in: complex
    h_drive: complex | None
    h_canal: complex | None
    h_total: complex | None
    power_drive_w: float
    power_entrance_w: float
    power_terminal_w: float
    power_source_loss_w: float
    source_residual_w: float
    tube_residual_w: float
    source_boundary_residual_pa: complex
    termination_boundary_residual_pa: complex
    matrix_pressure_residual_pa: complex
    matrix_flow_residual_m3_s: complex
    matrix_determinant_residual: complex
    dimensionless_denominator: complex
    dimensionless_denominator_residual: complex
    input_status: Literal["VALID"] = "VALID"
    source_reference_plane: str = "SOURCE_EQUIVALENT"
    entrance_plane: str = "CANAL_ENTRANCE"
    terminal_plane: str = "TERMINAL_SIDE"
    phasor: str = "peak_exp_plus_iwt"
    positive_u: str = "entrance_to_terminal"


def _real(value: object, name: str, *, positive: bool = False, nonnegative: bool = False) -> float:
    if isinstance(value, bool):
        raise ResearchBoundaryError("INVALID", name, "booleans are not numeric parameters")
    if isinstance(value, complex):
        if not (isfinite(value.real) and isfinite(value.imag)):
            raise ResearchBoundaryError("INVALID", name, "nonfinite number")
        if value.imag != 0:
            raise ResearchBoundaryError("UNSUPPORTED", name, "reactive complex impedance is outside resistive model")
        raise ResearchBoundaryError("INVALID", name, "expected a real SI scalar")
    if not isinstance(value, Real):
        raise ResearchBoundaryError("INVALID", name, "expected a real SI scalar")
    try:
        x = float(value)
    except (ValueError, OverflowError):
        raise ResearchBoundaryError("INVALID", name, "cannot represent input as finite float64") from None
    if not isfinite(x):
        raise ResearchBoundaryError("INVALID", name, "nonfinite or out-of-range float64 input")
    if positive and x <= 0:
        raise ResearchBoundaryError("INVALID", name, "must be > 0")
    if nonnegative and x < 0:
        raise ResearchBoundaryError("INVALID", name, "must be >= 0")
    return x


def _pressure(value: object) -> complex:
    if isinstance(value, bool):
        raise ResearchBoundaryError("INVALID", "source_pressure_pa", "bool is not a complex pressure")
    if isinstance(value, complex):
        p = value
    elif isinstance(value, Real):
        p = complex(_real(value, "source_pressure_pa"), 0)
    else:
        raise ResearchBoundaryError("INVALID", "source_pressure_pa", "expected finite complex Pa phasor")
    if not (isfinite(p.real) and isfinite(p.imag)):
        raise ResearchBoundaryError("INVALID", "source_pressure_pa", "nonfinite pressure")
    return p


def solve(fixture: Fixture) -> PortObservation:
    """Solve a single named positive-frequency SI fixture, fail-closed.

    No silent damping, clipping, magnitude normalization, or invented wave field.
    Valid zero-drive returns zero raw ports/powers, undefined pressure ratios.
    """
    if not isinstance(fixture, Fixture):
        raise ResearchBoundaryError("INVALID", "fixture", "expected explicitly named Fixture")

    a_m2 = _real(fixture.area_m2, "area_m2", positive=True)
    length = _real(fixture.length_m, "length_m", positive=True)
    freq = _real(fixture.frequency_hz, "frequency_hz")
    rho = _real(fixture.air_density_kg_m3, "air_density_kg_m3", positive=True)
    c_air = _real(fixture.sound_speed_m_s, "sound_speed_m_s", positive=True)
    ps = _pressure(fixture.source_pressure_pa)
    zs = _real(fixture.source_impedance_pa_s_m3, "source_impedance_pa_s_m3", nonnegative=True)
    zt = _real(fixture.terminal_impedance_pa_s_m3, "terminal_impedance_pa_s_m3", positive=True)

    if not (0.01 <= length <= 0.05):
        raise ResearchBoundaryError("UNSUPPORTED", "length_m", "outside research-only 0.01..0.05 m")
    if not (1e-5 <= a_m2 <= 1e-4):
        raise ResearchBoundaryError("UNSUPPORTED", "area_m2", "outside research-only 1e-5..1e-4 m2")
    if not 0 < freq <= 8000:
        raise ResearchBoundaryError("UNSUPPORTED", "frequency_hz", "positive harmonic 0<f<=8000 Hz only")
    small_signal_scale = rho * c_air * c_air
    if not isfinite(small_signal_scale) or small_signal_scale <= 0:
        raise ResearchBoundaryError("NUMERICALLY_UNRESOLVED", "air", "pressure scale overflow/underflow")
    if abs(ps) / small_signal_scale > 1e-3:
        raise ResearchBoundaryError("UNSUPPORTED", "source_pressure_pa", "outside conservative small-signal engineering guard")

    tube = UniformTube(length, a_m2, sound_speed_m_s=c_air, air_density_kg_m3=rho)
    try:
        zc = float(tube.characteristic_impedance_pa_s_m3)
        m = tube.transfer_matrix(freq)
        aa, bb, cc, dd = complex(m[0, 0]), complex(m[0, 1]), complex(m[1, 0]), complex(m[1, 1])
        rs, rt = zs / zc, zt / zc
        theta = 2 * pi * freq * length / c_air
        bn, cn = bb / zc, cc * zc
        dn = (aa + rs * cn) * rt + bn + rs * dd
        analytic_dn = (rs + rt) * cos(theta) + 1j * (1 + rs * rt) * sin(theta)
        scalars = [zc, rs, rt, theta, abs(dn), abs(analytic_dn), abs(dn - analytic_dn)]
        if not all(isfinite(v) for v in scalars):
            raise ResearchBoundaryError("NUMERICALLY_UNRESOLVED", "denominator", "nonfinite dimensionless acoustic solve")
        # This passive circuit has no true zero denominator. This is a numerical guard.
        warning_scale = max(1, rs + rt, 1 + rs * rt)
        if abs(dn) <= 64 * float_info.epsilon * warning_scale:
            raise ResearchBoundaryError("NUMERICALLY_UNRESOLVED", "denominator", "numerical cancellation or badly scaled fixture")
        pL = ps * rt / dn
        uL = pL / zt
        p0 = ps * (aa * rt + bn) / dn
        u0 = ps * (cn * rt + dd) / (zc * dn)
        fields = [p0, u0, pL, uL]
        if not all(isfinite(z.real) and isfinite(z.imag) for z in fields):
            raise ResearchBoundaryError("NUMERICALLY_UNRESOLVED", "ports", "nonfinite complex output")
        if max(abs(ps), abs(p0), abs(pL)) / small_signal_scale > 1e-3:
            raise ResearchBoundaryError("UNSUPPORTED", "ports", "outside conservative linear-pressure scope")

        # Reflection is structural, independent of drive; pressure transfer is not.
        gamma_l = (zt - zc) / (zt + zc)
        gamma_in = gamma_l * complex(cos(-2 * theta), sin(-2 * theta))
        ratio_defined = abs(ps) > 0
        h_drive = p0 / ps if ratio_defined else None
        h_total = pL / ps if ratio_defined else None
        h_canal = pL / p0 if ratio_defined and abs(p0) > 16 * float_info.epsilon * abs(ps) else None
        zin = p0 / u0 if abs(u0) > 0 else None
        pdrive = (ps * u0.conjugate()).real / 2
        pent = (p0 * u0.conjugate()).real / 2
        pterm = (pL * uL.conjugate()).real / 2
        ploss = zs * abs(u0) ** 2 / 2
        powers = [pdrive, pent, pterm, ploss]
        if not all(isfinite(v) for v in powers):
            raise ResearchBoundaryError("NUMERICALLY_UNRESOLVED", "powers", "nonfinite mean power")

        return PortObservation(
            p0, u0, pL, uL, zc, zin, gamma_in, h_drive, h_canal, h_total,
            pdrive, pent, pterm, ploss, pdrive - pent - ploss, pent - pterm,
            ps - p0 - zs * u0, pL - zt * uL,
            p0 - aa * pL - bb * uL, u0 - cc * pL - dd * uL,
            aa * dd - bb * cc - 1, dn, dn - analytic_dn,
        )
    except ResearchBoundaryError:
        raise
    except (OverflowError, FloatingPointError, ZeroDivisionError, ValueError) as e:
        raise ResearchBoundaryError("NUMERICALLY_UNRESOLVED", "solve", str(e)) from e