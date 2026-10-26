"""VF-1A research-only energy-balanced two-mass compliant aperture / Exp032 tract.

This is an abstract pressure-driven compliant chamber, NOT validated vocal
fold aerodynamics. No prescribed periodic aperture, F0, waveform, or renderer.
All new source code resides only in experiments/036_vf1a_two_mass/.
Scientific protocol: docs/research/vf1/GATE_A.md (committed first).
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

import numpy as np

# An explicit PRECURSOR dependency: SFI-3 Draft #84 contains untouched SFI-2
# research-only tract. This pilot PR is STACKED on that exact research ref.
TRACT_PATH = Path(__file__).resolve().parents[1] / "032_passive_time_domain_tract"
if str(TRACT_PATH) not in sys.path:
    sys.path.append(str(TRACT_PATH))
from waveguide import Geometry, PassiveTract  # noqa: E402


class UnsupportedContact(RuntimeError):
    """Aperture reaches the unimplemented collision/closure regime."""


class NumericallyUnresolved(ArithmeticError):
    """No conservative/resolved solution at the declared timestep."""


@dataclass(frozen=True)
class Tissue:
    masses_kg: tuple[float, float] = (1.2e-4, 1.2e-4)
    stiffness_n_m: tuple[float, float] = (30.0, 30.0)
    coupling_n_m: float = 8.0
    damping_n_s_m: tuple[float, float] = (0.008, 0.008)
    pressure_areas_m2: tuple[float, float] = (3e-5, 3e-5)
    rest_aperture_m2: float = 3e-5
    width_m: float = 0.012
    aperture_floor_m2: float = 2e-6
    flow_inertance_pa_s2_m3: float = 1200.0
    flow_resistance_pa_s_m3: float = 1.5e6
    rho_kg_m3: float = 1.21
    discharge_coefficient: float = 0.7

    def __post_init__(self) -> None:
        positive = (*self.masses_kg, *self.stiffness_n_m,
                    self.rest_aperture_m2, self.width_m,
                    self.aperture_floor_m2, self.flow_inertance_pa_s2_m3,
                    self.rho_kg_m3, self.discharge_coefficient)
        nonnegative = (*self.damping_n_s_m, *self.pressure_areas_m2,
                       self.coupling_n_m, self.flow_resistance_pa_s_m3)
        if any(isinstance(v, bool) or not math.isfinite(v) or v <= 0
               for v in positive):
            raise ValueError("INVALID_POSITIVE_TISSUE_PARAMETER")
        if any(isinstance(v, bool) or not math.isfinite(v) or v < 0
               for v in nonnegative):
            raise ValueError("INVALID_NONNEGATIVE_TISSUE_PARAMETER")
        if self.aperture_floor_m2 >= self.rest_aperture_m2:
            raise ValueError("INVALID_APERTURE_FLOOR")

    @property
    def stiffness(self) -> np.ndarray:
        a, b = self.stiffness_n_m
        c = self.coupling_n_m
        return np.array(((a + c, -c), (-c, b + c)), dtype=float)

    @property
    def g(self) -> np.ndarray:
        return np.asarray(self.pressure_areas_m2, dtype=float)


@dataclass(frozen=True)
class TissueStep:
    time_s: float
    x_m: tuple[float, float]
    v_m_s: tuple[float, float]
    area_m2: float
    flow_valve_m3_s: float
    flow_tract_mid_m3_s: float
    pressure_mid_pa: float
    outlet_flow_mid_m3_s: float
    stored_tissue_j: float
    stored_flow_j: float
    stored_tract_j: float
    source_work_j: float
    linear_flow_loss_j: float
    nonlinear_flow_loss_j: float
    tissue_damping_loss_j: float
    outlet_loss_j: float
    tissue_energy_residual_j: float
    flow_energy_residual_j: float
    tract_energy_residual_j: float
    total_energy_residual_j: float
    port_flow_residual_m3_s: float
    valve_equation_residual_pa: float


class CoupledTwoMass:
    def __init__(self, *, tissue: Tissue, tract: PassiveTract,
                 x_init_m: tuple[float, float] = (2e-5, -2e-5)):
        if not isinstance(tract, PassiveTract):
            raise TypeError("VF1_REQUIRES_PINNED_PASSIVE_TRACT")
        if len(x_init_m) != 2 or any(not math.isfinite(v) for v in x_init_m):
            raise ValueError("INVALID_INITIAL_DISPLACEMENT")
        self.tissue = tissue
        self.tract = tract
        self.x = np.array(x_init_m, dtype=float)
        self.v = np.zeros(2)
        self.q = 0.0
        self.tick = 0
        self._area(self.x)
        self.K = tissue.stiffness
        self.m = np.array(tissue.masses_kg)
        self.d = np.array(tissue.damping_n_s_m)
        self.g = tissue.g
        self.dt = tract.dt_s
        # A fixed, passive linear tract makes p_mid(Uin_next) affine.
        saved = tract.state
        try:
            p0 = tract.step(0.0).inlet_pressure_pa
            tract.state = saved
            p1 = tract.step(1.0).inlet_pressure_pa
        finally:
            tract.state = saved
        self.port_slope = p1 - p0
        if not math.isfinite(self.port_slope) or self.port_slope <= 0:
            raise NumericallyUnresolved("NONPASSIVE_ACOUSTIC_PORT")

    def _area(self, x: np.ndarray) -> float:
        t = self.tissue
        a = t.rest_aperture_m2 + (t.width_m / 2) * float(np.sum(x))
        if not math.isfinite(a):
            raise NumericallyUnresolved("NONFINITE_APERTURE")
        if a <= t.aperture_floor_m2:
            raise UnsupportedContact("VF1_CONTACT_NOT_MODELED")
        return a

    def energy(self) -> tuple[float, float, float]:
        et = (float(0.5 * np.dot(self.m, self.v**2)) +
              float(0.5 * self.x @ self.K @ self.x))
        eq = 0.5 * self.tissue.flow_inertance_pa_s2_m3 * self.q**2
        return et, eq, self.tract.energy()

    def step(self, *, subglottal_pressure_pa: float) -> TissueStep:
        if isinstance(subglottal_pressure_pa, bool) or not math.isfinite(subglottal_pressure_pa):
            raise ValueError("INVALID_RESPIRATORY_PRESSURE")
        t, dt = self.tissue, self.dt
        old_x, old_v, old_q = self.x, self.v, self.q
        old_u = float(self.tract.state.face_flow_m3_s[0])
        old_et, old_eq, old_ea = self.energy()

        saved = self.tract.state
        try:
            d0 = self.tract.step(0.0).inlet_pressure_pa
        finally:
            self.tract.state = saved
        # Tissue midpoint: L v_mid = 2m/dt*v_old - K*x_old + g*p.
        L = np.diag(2 * self.m / dt + self.d) + (dt / 2) * self.K
        vb = np.linalg.solve(L, 2 * self.m / dt * old_v - self.K @ old_x)
        vr = np.linalg.solve(L, self.g)
        z = self.port_slope
        denom = 1.0 + 2 * z * float(self.g @ vr)
        if not math.isfinite(denom) or denom <= 0:
            raise NumericallyUnresolved("SINGULAR_MECHANICAL_ACOUSTIC_PORT")
        p0 = (d0 - z * old_u - 2 * z * float(self.g @ vb)) / denom
        ps = 2 * z / denom

        def residual(qmid: float) -> tuple[float, float, np.ndarray, float]:
            p = p0 + ps * qmid
            v = vb + vr * p
            xmid = old_x + dt * v / 2
            a = self._area(xmid)
            beta = t.rho_kg_m3 / (2 * t.discharge_coefficient**2 * a**2)
            r = ((2 * t.flow_inertance_pa_s2_m3 / dt + t.flow_resistance_pa_s_m3) * qmid
                 + beta * qmid * abs(qmid) + p
                 - subglottal_pressure_pa
                 - 2 * t.flow_inertance_pa_s2_m3 / dt * old_q)
            return r, p, v, a

        # A Newton iteration with monotone local backtracking. Reject rather
        # than silently clip the aperture or invent energy for a failed solve.
        qm = old_q
        for _ in range(32):
            r, p, vm, a = residual(qm)
            if abs(r) <= 1e-9 * max(1., abs(subglottal_pressure_pa), abs(p)):
                break
            area_slope = (t.width_m / 2) * float(np.sum(dt * vr * ps / 2))
            beta = t.rho_kg_m3 / (2 * t.discharge_coefficient**2 * a**2)
            dr = (2 * t.flow_inertance_pa_s2_m3 / dt + t.flow_resistance_pa_s_m3
                  + ps + 2 * beta * abs(qm)
                  - 2 * beta * area_slope / a * qm * abs(qm))
            if not math.isfinite(dr) or dr <= 0:
                raise NumericallyUnresolved("NONMONOTONE_FLOW_ROOT")
            change = -r / dr
            accepted = False
            for backtrack in range(32):
                candidate = qm + change * (0.5 ** backtrack)
                try:
                    rc, _, _, _ = residual(candidate)
                except UnsupportedContact:
                    continue
                if math.isfinite(rc) and abs(rc) < abs(r):
                    qm = candidate
                    accepted = True
                    break
            if not accepted:
                raise NumericallyUnresolved("FLOW_NEWTON_LINESEARCH_FAILED")
        else:
            raise NumericallyUnresolved("FLOW_NEWTON_ITERATION_EXHAUSTED")
        r, p, vm, a = residual(qm)
        un_mid = qm - float(self.g @ vm)
        un_next = 2 * un_mid - old_u
        qnext = 2 * qm - old_q
        vnext = 2 * vm - old_v
        xnext = old_x + dt * vm
        # Refuse contacts at the completed state, too.
        self._area(xnext)
        acoustic = self.tract.step(un_next)
        p_actual = acoustic.inlet_pressure_pa
        port_error = p_actual - p
        port_u_error = acoustic.inlet_flow_m3_s - un_mid
        if (abs(port_error) > 1e-7 * max(1., abs(p_actual), abs(p)) or
            abs(port_u_error) > 1e-9 * max(abs(un_mid), 1e-12)):
            raise NumericallyUnresolved("MISMATCHED_TIMESTEP_ACOUSTIC_PORT")
        et = (float(0.5 * np.dot(self.m, vnext**2))
              + float(0.5 * xnext @ self.K @ xnext))
        eq = 0.5 * t.flow_inertance_pa_s2_m3 * qnext**2
        work = dt * subglottal_pressure_pa * qm
        flow_lin = dt * t.flow_resistance_pa_s_m3 * qm**2
        flow_nlin = (dt * t.rho_kg_m3 / (2 * t.discharge_coefficient**2 * a**2)
                     * abs(qm)**3)
        damp = dt * float(self.d @ (vm**2))
        # Three separate local balances; pressure·g·v cancels *only in total*.
        me = (et - old_et) - (dt * p * float(self.g @ vm) - damp)
        fe = (eq - old_eq) - (work - dt * p * qm - flow_lin - flow_nlin)
        ae = acoustic.energy_residual_j
        total = me + fe + ae
        scales = (
            max(abs(et-old_et), abs(dt*p*float(self.g@vm)), damp, 1e-12),
            max(abs(eq-old_eq), abs(work), abs(dt*p*qm), flow_lin, flow_nlin, 1e-12),
            max(abs(acoustic.injected_work_j), abs(acoustic.dissipated_j),
                abs(acoustic.stored_energy_j-old_ea), 1e-12),
        )
        if not all(math.isfinite(v) for v in
                   (me, fe, ae, total, et, eq, a, qm, p, un_next)):
            raise NumericallyUnresolved("NONFINITE_COUPLED_ENERGY")
        if max(abs(me)/scales[0],abs(fe)/scales[1],abs(ae)/scales[2]) > 1e-8:
            raise NumericallyUnresolved("LOCAL_ENERGY_BALANCE_FAILED")
        if abs(r) > 1e-7 * max(1.,abs(subglottal_pressure_pa),abs(p)):
            raise NumericallyUnresolved("GLOTTAL_EQUATION_FAILED")
        self.x, self.v, self.q = xnext, vnext, qnext
        self.tick += 1
        return TissueStep(
            time_s=self.tick*dt, x_m=(float(xnext[0]),float(xnext[1])),
            v_m_s=(float(vnext[0]),float(vnext[1])),
            area_m2=a, flow_valve_m3_s=qnext,
            flow_tract_mid_m3_s=un_mid, pressure_mid_pa=p_actual,
            outlet_flow_mid_m3_s=acoustic.outlet_flow_m3_s,
            stored_tissue_j=et,stored_flow_j=eq,
            stored_tract_j=acoustic.stored_energy_j,
            source_work_j=work,linear_flow_loss_j=flow_lin,
            nonlinear_flow_loss_j=flow_nlin,tissue_damping_loss_j=damp,
            outlet_loss_j=acoustic.dissipated_j,
            tissue_energy_residual_j=me,flow_energy_residual_j=fe,
            tract_energy_residual_j=ae,total_energy_residual_j=total,
            port_flow_residual_m3_s=port_u_error,
            valve_equation_residual_pa=r,
        )


def make_pilot(*, pressure_shape: str="uniform", sample_rate_hz: int=48000,
               stiffness_scale: float=1.0, tissue: Tissue | None=None) -> CoupledTwoMass:
    if pressure_shape not in ("uniform", "constricted"):
        raise ValueError("INVALID_FROZEN_TRACT")
    if type(sample_rate_hz) is not int or sample_rate_hz <= 0:
        raise ValueError("INVALID_RATE")
    if not math.isfinite(stiffness_scale) or stiffness_scale <= 0:
        raise ValueError("INVALID_STIFFNESS_SCALE")
    from morphoacoustics.physical import Tract1DGeometry, TubeSection
    geom = Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(TubeSection(.017, .00015 if pressure_shape=="constricted"
                                   and j==5 else .0003) for j in range(10)))
    ac = Geometry.from_tract1d(geom)
    tract = PassiveTract(geometry=ac,subdivisions=2,
                         dt_s=1/sample_rate_hz,
                         outlet_resistance_pa_s_m3=ac.characteristic_outlet_impedance)
    if tissue is None:
        original = Tissue()
        tissue = Tissue(stiffness_n_m=tuple(v*stiffness_scale for v in
                                           original.stiffness_n_m))
    return CoupledTwoMass(tissue=tissue,tract=tract)
