"""Experiment-local SFI-1 two-state valve+chamber ODE, coupled backward Euler.

The lumped chamber is NOT a 1D/3D vocal tract or a self-oscillating source.
U [m^3/s], p [Pa]; I [Pa s^2/m^3], R [Pa s/m^3], C [m^3/Pa].
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Parameters:
    air_density_kg_m3: float = 1.21
    discharge_coefficient: float = 0.70
    glottal_inertance_pa_s2_m3: float = 1200.0
    glottal_resistance_pa_s_m3: float = 1.5e6
    compliance_m3_pa: float = 3.5e-10
    outlet_resistance_pa_s_m3: float = 8.0e6

    def __post_init__(self) -> None:
        positive = (
            self.air_density_kg_m3,
            self.discharge_coefficient,
            self.glottal_inertance_pa_s2_m3,
            self.glottal_resistance_pa_s_m3,
            self.compliance_m3_pa,
            self.outlet_resistance_pa_s_m3,
        )
        if any(not math.isfinite(x) or x <= 0.0 for x in positive):
            raise ValueError("all fixture parameters must be finite and strictly positive")

    def quadratic_loss_coefficient(self, area_m2: float) -> float:
        if not math.isfinite(area_m2) or area_m2 <= 0.0:
            raise ValueError("open aperture must be finite and positive")
        coefficient = (
            self.air_density_kg_m3
            / (2.0 * self.discharge_coefficient**2 * area_m2**2)
        )
        if not math.isfinite(coefficient):
            raise ValueError("quadratic flow coefficient overflow")
        return coefficient


@dataclass(frozen=True)
class State:
    flow_m3_s: float = 0.0
    chamber_pressure_pa: float = 0.0


@dataclass(frozen=True)
class EnergyBudget:
    """Energy in J. Numerical BE losses and valve projection reported separately."""

    change_j: float
    pressure_work_j: float
    glottal_linear_loss_j: float
    glottal_quadratic_loss_j: float
    outlet_loss_j: float
    numerical_flow_loss_j: float
    numerical_chamber_loss_j: float
    closure_projection_loss_j: float
    nonreciprocal_work_j: float
    residual_j: float


@dataclass(frozen=True)
class Step:
    state: State
    budget: EnergyBudget
    aperture_closed: bool


def signed_quadratic_root(a: float, b: float, rhs: float) -> float:
    """Unique real solution to b*u*abs(u)+a*u=rhs, a>0 and b>=0.

    Hypot avoids large-intermediate square overflow; rationalization avoids
    cancellation in the small-b limit. Solves reverse-flow signs as well.
    """
    if not (math.isfinite(a) and math.isfinite(b) and math.isfinite(rhs)):
        raise ValueError("nonfinite scalar equation")
    if a <= 0 or b < 0:
        raise ValueError("requires a>0 and b>=0")
    if rhs == 0:
        return 0.0
    if b == 0:
        return rhs / a
    discriminant_root = math.hypot(a, 2.0 * math.sqrt(b) * math.sqrt(abs(rhs)))
    return math.copysign(2.0 * abs(rhs) / (a + discriminant_root), rhs)


def energy(state: State, parameters: Parameters) -> float:
    return 0.5 * (
        parameters.glottal_inertance_pa_s2_m3 * state.flow_m3_s**2
        + parameters.compliance_m3_pa * state.chamber_pressure_pa**2
    )


def step(
    previous: State,
    *,
    parameters: Parameters,
    dt_s: float,
    area_m2: float,
    subglottal_pressure_pa: float,
    feedback: bool,
) -> Step:
    """Advance both variables implicitly, retaining downstream p even in C0.

    C0 excludes p only from the glottal flow equation, preserving all controls
    and chamber dynamics. Its nonreciprocal chamber input work is explicit.
    """
    if not (math.isfinite(dt_s) and dt_s > 0):
        raise ValueError("dt must be finite and positive")
    if not (math.isfinite(area_m2) and area_m2 >= 0):
        raise ValueError("area must be finite and nonnegative")
    if not math.isfinite(subglottal_pressure_pa):
        raise ValueError("driving pressure must be finite")
    if not all(math.isfinite(x) for x in (previous.flow_m3_s, previous.chamber_pressure_pa)):
        raise ValueError("prior state must be finite")

    c = parameters.compliance_m3_pa
    r_out = parameters.outlet_resistance_pa_s_m3
    inertance = parameters.glottal_inertance_pa_s2_m3
    r_glottal = parameters.glottal_resistance_pa_s_m3
    alpha = c / (c + dt_s / r_out)
    beta = dt_s / (c + dt_s / r_out)
    closed = (area_m2 == 0.0)
    if closed:
        next_u = 0.0  # exact no-leakage ideal closure: dissipative reset
        b = 0.0
    else:
        b = parameters.quadratic_loss_coefficient(area_m2)
        a = inertance / dt_s + r_glottal + (beta if feedback else 0.0)
        rhs = (
            subglottal_pressure_pa
            + inertance / dt_s * previous.flow_m3_s
            - (alpha * previous.chamber_pressure_pa if feedback else 0.0)
        )
        next_u = signed_quadratic_root(a, b, rhs)
    next_p = alpha * previous.chamber_pressure_pa + beta * next_u
    current = State(flow_m3_s=next_u, chamber_pressure_pa=next_p)
    if not math.isfinite(next_u) or not math.isfinite(next_p):
        raise FloatingPointError("nonfinite coupled state")

    du = next_u - previous.flow_m3_s
    dp = next_p - previous.chamber_pressure_pa
    change = energy(current, parameters) - energy(previous, parameters)
    pressure_work = dt_s * subglottal_pressure_pa * next_u
    glottal_linear = dt_s * r_glottal * next_u**2
    glottal_quadratic = dt_s * b * abs(next_u)**3 if not closed else 0.0
    outlet = dt_s * next_p**2 / r_out
    numerical_flow = 0.0 if closed else 0.5 * inertance * du**2
    numerical_chamber = 0.5 * c * dp**2
    contact = 0.5 * inertance * previous.flow_m3_s**2 if closed else 0.0
    nonreciprocal = 0.0 if feedback else dt_s * next_p * next_u
    balance_rhs = (
        pressure_work
        + nonreciprocal
        - glottal_linear
        - glottal_quadratic
        - outlet
        - numerical_flow
        - numerical_chamber
        - contact
    )
    budget = EnergyBudget(
        change_j=change,
        pressure_work_j=pressure_work,
        glottal_linear_loss_j=glottal_linear,
        glottal_quadratic_loss_j=glottal_quadratic,
        outlet_loss_j=outlet,
        numerical_flow_loss_j=numerical_flow,
        numerical_chamber_loss_j=numerical_chamber,
        closure_projection_loss_j=contact,
        nonreciprocal_work_j=nonreciprocal,
        residual_j=change - balance_rhs,
    )
    return Step(state=current, budget=budget, aperture_closed=closed)


def steady_flow(
    *, area_m2: float, subglottal_pressure_pa: float, parameters: Parameters
) -> State:
    """Independent constant-A, constant-drive steady coupled equilibrium."""
    b = parameters.quadratic_loss_coefficient(area_m2)
    u = signed_quadratic_root(
        parameters.glottal_resistance_pa_s_m3
        + parameters.outlet_resistance_pa_s_m3,
        b,
        subglottal_pressure_pa,
    )
    return State(flow_m3_s=u, chamber_pressure_pa=parameters.outlet_resistance_pa_s_m3 * u)
