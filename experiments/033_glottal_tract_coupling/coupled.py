"""Research-only SFI-3 power-port coupling of glottal valve and Exp032 tract.

- Exp031 provides the *physical law*, not its BE lumped chamber integrator.
- Import the *unaltered* Exp032 causal waveguide from this PR's stacked base.
- This model has a **strictly positive prescribed opening**; exact closure is
  unsupported until contact/projection work has its own validated gate.
- One shared implicit-midpoint port; never a lagged p_in[n] -> U[n+1] pass.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

WAVEGUIDE_DIR = Path(__file__).resolve().parents[1] / "032_passive_time_domain_tract"
if str(WAVEGUIDE_DIR) not in sys.path:
    sys.path.append(str(WAVEGUIDE_DIR))
from waveguide import Geometry, PassiveTract  # noqa: E402


@dataclass(frozen=True)
class GlottalParameters:
    air_density_kg_m3: float = 1.21
    discharge_coefficient: float = 0.70
    inertance_pa_s2_m3: float = 1200.0
    resistance_pa_s_m3: float = 1.5e6

    def __post_init__(self) -> None:
        for value in (
            self.air_density_kg_m3,
            self.discharge_coefficient,
            self.inertance_pa_s2_m3,
            self.resistance_pa_s_m3,
        ):
            if not math.isfinite(value) or value <= 0:
                raise ValueError("glottal parameters must be positive and finite")

    def loss_coefficient(self, area_m2: float) -> float:
        if not math.isfinite(area_m2) or area_m2 < 0:
            raise ValueError("area must be nonnegative and finite")
        if area_m2 == 0:
            raise NotImplementedError("CLOSED_GLOTTIS_UNSUPPORTED: needs a separate contact-work gate")
        b = self.air_density_kg_m3 / (2 * self.discharge_coefficient**2 * area_m2**2)
        if not math.isfinite(b):
            raise ValueError("area is too small for a finite valve loss coefficient")
        return b


@dataclass(frozen=True)
class CoupledStep:
    flow_m3_s: float
    flow_mid_m3_s: float
    inlet_pressure_mid_pa: float
    outlet_flow_mid_m3_s: float
    glottal_energy_j: float
    tract_energy_j: float
    total_energy_j: float
    delta_energy_j: float
    pressure_drive_work_j: float
    glottal_linear_loss_j: float
    glottal_nonlinear_loss_j: float
    outlet_loss_j: float
    nonreciprocal_port_work_j: float
    energy_residual_j: float
    glottal_equation_residual_pa: float
    port_affine_residual_pa: float


def monotone_root(a: float, b: float, right: float) -> float:
    """Solve a*u + b*u*abs(u) = right, a>0, b>=0, both flow directions."""
    if not all(math.isfinite(x) for x in (a, b, right)) or a <= 0 or b < 0:
        raise ValueError("invalid monotone scalar equation")
    if right == 0:
        return 0.0
    if b == 0:
        return right / a
    # Avoid catastrophic cancellation in the quadratic formula.
    radicand = math.hypot(a, 2 * math.sqrt(b) * math.sqrt(abs(right)))
    return math.copysign(2 * abs(right) / (a + radicand), right)


class StrongCoupling:
    def __init__(self, tract: PassiveTract, *, glottis: GlottalParameters | None = None,
                 feedback: bool = True):
        if not isinstance(tract, PassiveTract):
            raise TypeError("requires the original Exp032 PassiveTract")
        self.tract = tract
        self.glottis = glottis or GlottalParameters()
        self.feedback = feedback
        self.flow_m3_s = float(tract.state.face_flow_m3_s[0])
        # This coefficient is state-independent because the fixed tract is linear.
        # Two evaluations with identical prior state; no permanent time advance.
        saved = tract.state
        try:
            z0 = tract.step(0.0).inlet_pressure_pa
            tract.state = saved
            z1 = tract.step(1.0).inlet_pressure_pa
            tract.state = saved
        finally:
            tract.state = saved
        self.port_slope_pa_s_m3 = z1 - z0
        if not math.isfinite(self.port_slope_pa_s_m3) or self.port_slope_pa_s_m3 <= 0:
            raise FloatingPointError("nonpassive/invalid acoustic port slope")

    def step(self, *, area_m2: float, subglottal_pressure_pa: float) -> CoupledStep:
        if not math.isfinite(subglottal_pressure_pa):
            raise ValueError("subglottal pressure must be finite")
        b = self.glottis.loss_coefficient(area_m2)
        dt = self.tract.dt_s
        u_old = self.flow_m3_s
        if not math.isclose(float(self.tract.state.face_flow_m3_s[0]), u_old,
                            rel_tol=1e-13, abs_tol=1e-16):
            raise RuntimeError("power-port flow state mismatch")
        e_old = self.glottis.inertance_pa_s2_m3 * u_old**2 / 2 + self.tract.energy()

        # Read the pressure-port intercept without permanently advancing the
        # time-domain acoustic state; the boundary map is p_mid=d+k*u_next.
        saved = self.tract.state
        try:
            intercept = self.tract.step(0.0).inlet_pressure_pa
        finally:
            self.tract.state = saved

        inertance = self.glottis.inertance_pa_s2_m3
        resistance = self.glottis.resistance_pa_s_m3
        k = self.port_slope_pa_s_m3 if self.feedback else 0.0
        d = intercept if self.feedback else 0.0
        # Express in the shared midpoint x=(u_old+u_new)/2:
        # (2 I/dt + Rg + 2k)*x + b*x|x| = Psub - d + (2 I/dt + k)*u_old.
        a = 2 * inertance / dt + resistance + 2 * k
        right = subglottal_pressure_pa - d + (2 * inertance / dt + k) * u_old
        u_mid = monotone_root(a, b, right)
        u_next = 2 * u_mid - u_old
        if not math.isfinite(u_next):
            raise FloatingPointError("nonfinite valve flow")
        acoustic = self.tract.step(u_next)  # exactly one committed acoustic step
        self.flow_m3_s = u_next
        port_pressure = acoustic.inlet_pressure_pa
        port_residual = port_pressure - (intercept + self.port_slope_pa_s_m3 * u_next)
        equation_residual = (
            inertance * (u_next - u_old) / dt
            + resistance * u_mid
            + b * u_mid * abs(u_mid)
            + (port_pressure if self.feedback else 0.0)
            - subglottal_pressure_pa
        )
        if abs(port_residual) > 1e-7 * max(1., abs(port_pressure)):
            raise FloatingPointError("acoustic port is not affine: inconsistent strong coupling")
        if abs(equation_residual) > 1e-7 * max(1., abs(subglottal_pressure_pa)):
            raise FloatingPointError("glottal valve equation violated")
        e_glottal = inertance * u_next**2 / 2
        e_total = e_glottal + acoustic.stored_energy_j
        input_work = dt * subglottal_pressure_pa * u_mid
        linear_loss = dt * resistance * u_mid**2
        nonlinear_loss = dt * b * abs(u_mid)**3
        outlet_loss = acoustic.dissipated_j
        # C0 is deliberately nonreciprocal: pressure work enters the waveguide
        # without equal/opposite feedback power on the glottal source.
        nonreciprocal = 0.0 if self.feedback else dt * port_pressure * u_mid
        de = e_total - e_old
        residual = de - (
            input_work + nonreciprocal - linear_loss - nonlinear_loss - outlet_loss
        )
        if not all(math.isfinite(q) for q in (
            de, residual, port_pressure, e_total, input_work, outlet_loss,
        )):
            raise FloatingPointError("nonfinite energy budget")
        return CoupledStep(
            flow_m3_s=u_next,
            flow_mid_m3_s=u_mid,
            inlet_pressure_mid_pa=port_pressure,
            outlet_flow_mid_m3_s=acoustic.outlet_flow_m3_s,
            glottal_energy_j=e_glottal,
            tract_energy_j=acoustic.stored_energy_j,
            total_energy_j=e_total,
            delta_energy_j=de,
            pressure_drive_work_j=input_work,
            glottal_linear_loss_j=linear_loss,
            glottal_nonlinear_loss_j=nonlinear_loss,
            outlet_loss_j=outlet_loss,
            nonreciprocal_port_work_j=nonreciprocal,
            energy_residual_j=residual,
            glottal_equation_residual_pa=equation_residual,
            port_affine_residual_pa=port_residual,
        )


def make_model(*, constricted: bool = False, feedback: bool = True,
               sample_rate_hz: int = 48000, subdivisions: int = 4) -> StrongCoupling:
    if type(sample_rate_hz) is not int or sample_rate_hz <= 0:
        raise ValueError("positive integer sample rate required")
    # Take both fixture geometries through the real Core physical representation,
    # exactly as the Exp032 adapter contract specifies.
    from morphoacoustics.physical import Tract1DGeometry, TubeSection

    physical = Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(
                length_m=.017,
                area_m2=.00015 if constricted and i == 5 else .0003,
            )
            for i in range(10)
        ),
    )
    geom = Geometry.from_tract1d(physical)
    tract = PassiveTract(
        geometry=geom,
        subdivisions=subdivisions,
        dt_s=1 / sample_rate_hz,
        outlet_resistance_pa_s_m3=geom.characteristic_outlet_impedance,
    )
    return StrongCoupling(tract, feedback=feedback)
