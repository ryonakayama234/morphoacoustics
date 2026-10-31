"""Experimental, fixed-wall, low-Re analytical-control solver. NO phonation/FSI."""
from __future__ import annotations
from dataclasses import dataclass
import math


class UnsupportedRegime(ValueError):
    """This physical approximation cannot support this declared condition."""


@dataclass(frozen=True)
class RigidChannel:
    length_m: float = 0.01
    width_m: float = 0.01
    half_gap_m: float = 0.00012
    taper_slope: float = 0.0


@dataclass(frozen=True)
class Fluid:
    viscosity_pa_s: float = 1.81e-5
    density_kg_m3: float = 1.21
    sound_speed_m_s: float = 343.0


@dataclass(frozen=True)
class Observation:
    volume_flow_m3_s: float
    face_pressure_pa: tuple[float, ...]
    loss_per_cell_w: tuple[float, ...]
    input_power_w: float
    dissipation_w: float
    power_residual_w: float
    virtual_force_lower_n: float
    virtual_force_upper_n: float
    reynolds_upper_bound: float
    mach_upper_bound: float


def _positive(x: float) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x > 0


def solve_fixed_wall(
    geometry: RigidChannel,
    fluid: Fluid,
    upstream_gauge_pressure_pa: float,
    sections: int,
) -> Observation:
    """Cell-midpoint lubrication resistance, then cumulative face pressure.

    This is a *steady fixed-wall* positive-flow mathematical reference, not a
    moving-wall source and not an empirical glottal model. Full external
    pneumatic power is dissipated by a prescribed Stokes resistance.
    """
    if not isinstance(geometry, RigidChannel) or not isinstance(fluid, Fluid):
        raise ValueError("typed geometry and fluid required")
    g, f = geometry, fluid
    if not all(_positive(v) for v in (
        g.length_m, g.width_m, g.half_gap_m,
        f.viscosity_pa_s, f.density_kg_m3, f.sound_speed_m_s,
    )):
        raise ValueError("all geometric/fluid scales must be positive finite SI values")
    if not isinstance(g.taper_slope, (float, int)) or isinstance(g.taper_slope, bool) or not math.isfinite(g.taper_slope) or abs(g.taper_slope) >= 1:
        raise ValueError("taper must be finite and preserve strictly positive gap")
    if not isinstance(sections, int) or isinstance(sections, bool) or sections < 2:
        raise ValueError("at least two integer cells required")
    if not isinstance(upstream_gauge_pressure_pa, (float, int)) or isinstance(upstream_gauge_pressure_pa, bool) or not math.isfinite(upstream_gauge_pressure_pa):
        raise ValueError("finite SI pressure required")
    if upstream_gauge_pressure_pa < 0:
        raise UnsupportedRegime("negative/reverse flow outside registered one-way regime")
    hmin = g.half_gap_m * (1 - abs(g.taper_slope))
    hmax = g.half_gap_m * (1 + abs(g.taper_slope))
    if 2 * hmax / g.length_m > .05 or g.width_m / (2 * hmax) < 20:
        raise UnsupportedRegime("channel outside declared lubrication aspect range")

    dz = g.length_m / sections
    resistance_per_cell = tuple(
        3 * f.viscosity_pa_s * dz /
        (2 * g.width_m * (g.half_gap_m * (1 + g.taper_slope * (2 * (j+.5) / sections - 1)))**3)
        for j in range(sections)
    )
    resistance = math.fsum(resistance_per_cell)
    flow = upstream_gauge_pressure_pa / resistance
    max_speed = flow / (2 * g.width_m * hmin)
    reynolds_bound = f.density_kg_m3 * max_speed * 4 * hmax / f.viscosity_pa_s
    mach_bound = max_speed / f.sound_speed_m_s
    if reynolds_bound > 1 or mach_bound > .01:
        raise UnsupportedRegime("Reynolds/Mach outside registered Stokes-lubrication domain")

    pressures = [float(upstream_gauge_pressure_pa)]
    dissipations = []
    f_lower = f_upper = 0.0
    for j, rj in enumerate(resistance_per_cell):
        drop = flow * rj
        pressures.append(pressures[-1] - drop)
        dissipations.append(flow * drop)
        mid_pressure = (pressures[-2] + pressures[-1]) / 2
        z_normal = (j + .5) / sections
        f_lower += 2 * g.width_m * dz * (1 - z_normal) * mid_pressure
        f_upper += 2 * g.width_m * dz * z_normal * mid_pressure

    input_power = upstream_gauge_pressure_pa * flow
    dissipation = math.fsum(dissipations)
    if abs(pressures[-1]) > 1e-11 * max(1., upstream_gauge_pressure_pa):
        raise ArithmeticError("discrete downstream pressure does not close")
    return Observation(
        flow, tuple(pressures), tuple(dissipations), input_power,
        dissipation, input_power - dissipation, f_lower, f_upper,
        reynolds_bound, mach_bound,
    )


def check_receipt(obs: Observation, upstream_pa: float) -> bool:
    """Fail-closed independent-form checks; never trust a stored PASS flag."""
    if not isinstance(obs, Observation) or not isinstance(upstream_pa, (int, float)) or not math.isfinite(upstream_pa) or upstream_pa < 0:
        return False
    vals = (obs.volume_flow_m3_s, *obs.face_pressure_pa, *obs.loss_per_cell_w,
            obs.input_power_w, obs.dissipation_w, obs.power_residual_w,
            obs.virtual_force_lower_n, obs.virtual_force_upper_n,
            obs.reynolds_upper_bound, obs.mach_upper_bound)
    if not all(math.isfinite(v) for v in vals):
        return False
    if len(obs.face_pressure_pa) != len(obs.loss_per_cell_w) + 1 or not obs.loss_per_cell_w:
        return False
    flow = obs.volume_flow_m3_s
    if flow < 0 or abs(obs.face_pressure_pa[0] - upstream_pa) > 1e-12 * max(1, upstream_pa):
        return False
    if abs(obs.face_pressure_pa[-1]) > 1e-11 * max(1, upstream_pa):
        return False
    if any(obs.face_pressure_pa[j] + 1e-12 < obs.face_pressure_pa[j+1] for j in range(len(obs.loss_per_cell_w))):
        return False
    if any(x < -1e-18 for x in obs.loss_per_cell_w):
        return False
    port_power = flow * (obs.face_pressure_pa[0] - obs.face_pressure_pa[-1])
    loss = math.fsum(obs.loss_per_cell_w)
    tol = 1e-12 * max(abs(port_power), 1e-18)
    # An aggregate work identity alone misses pressure/loss redistribution.
    if any(abs(obs.loss_per_cell_w[j] - flow * (obs.face_pressure_pa[j] - obs.face_pressure_pa[j+1])) > tol
           for j in range(len(obs.loss_per_cell_w))):
        return False
    return (abs(obs.input_power_w - upstream_pa * flow) <= tol
        and abs(obs.dissipation_w - loss) <= tol
        and abs(obs.power_residual_w - (obs.input_power_w - loss)) <= tol
        and abs(port_power - loss) <= tol
        and obs.reynolds_upper_bound <= 1 and obs.mach_upper_bound <= .01)
