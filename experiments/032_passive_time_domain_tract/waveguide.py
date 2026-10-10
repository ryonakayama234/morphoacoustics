"""Experiment 032: fixed-segment passive 1D wave propagation, implicit midpoint.

The inlet volume flow is externally prescribed. This is not glottal feedback.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from morphoacoustics.physical import Tract1DGeometry


@dataclass(frozen=True)
class Geometry:
    lengths_m: tuple[float, ...] = (0.017,) * 10
    areas_m2: tuple[float, ...] = (3.0e-4,) * 10
    sound_speed_m_s: float = 343.0
    air_density_kg_m3: float = 1.21

    def __post_init__(self) -> None:
        if not self.lengths_m or len(self.lengths_m) != len(self.areas_m2):
            raise ValueError('lengths and areas must be nonempty and equal-sized')
        values = (*self.lengths_m, *self.areas_m2, self.sound_speed_m_s, self.air_density_kg_m3)
        if any(not math.isfinite(x) or x <= 0.0 for x in values):
            raise ValueError('geometry must contain strictly positive, finite quantities')

    @property
    def total_length_m(self) -> float:
        return sum(self.lengths_m)

    @property
    def characteristic_outlet_impedance(self) -> float:
        return self.air_density_kg_m3 * self.sound_speed_m_s / self.areas_m2[-1]

    def cells(self, subdivisions: int) -> tuple[np.ndarray, np.ndarray]:
        if type(subdivisions) is not int or subdivisions <= 0:
            raise ValueError('subdivisions must be a positive integer')
        lengths = np.repeat(np.array(self.lengths_m) / subdivisions, subdivisions)
        areas = np.repeat(np.array(self.areas_m2), subdivisions)
        return lengths, areas

    @classmethod
    def from_tract1d(cls, tract: 'Tract1DGeometry', *, sound_speed_m_s: float = 343.0,
                     air_density_kg_m3: float = 1.21) -> 'Geometry':
        """Read existing physical tract lengths/areas; no schema modification."""
        return cls(lengths_m=tuple(section.length_m for section in tract.sections),
                   areas_m2=tuple(section.area_m2 for section in tract.sections),
                   sound_speed_m_s=sound_speed_m_s,
                   air_density_kg_m3=air_density_kg_m3)

    @staticmethod
    def middle_constriction() -> 'Geometry':
        areas = [3.0e-4] * 10
        areas[5] *= 0.5
        return Geometry(areas_m2=tuple(areas))


@dataclass
class AcousticState:
    pressure_pa: np.ndarray
    face_flow_m3_s: np.ndarray


@dataclass(frozen=True)
class StepObservation:
    inlet_pressure_pa: float
    inlet_flow_m3_s: float
    outlet_flow_m3_s: float
    stored_energy_j: float
    injected_work_j: float
    dissipated_j: float
    energy_residual_j: float


class PassiveTract:
    def __init__(self, *, geometry: Geometry, subdivisions: int = 4,
                 dt_s: float = 1/48000, outlet_resistance_pa_s_m3: float | None = None):
        if not math.isfinite(dt_s) or dt_s <= 0:
            raise ValueError('dt must be finite and positive')
        if outlet_resistance_pa_s_m3 is None:
            outlet_resistance_pa_s_m3 = geometry.characteristic_outlet_impedance
        if not math.isfinite(outlet_resistance_pa_s_m3) or outlet_resistance_pa_s_m3 < 0:
            raise ValueError('passive outlet resistance must be finite and nonnegative')
        dx, area = geometry.cells(subdivisions)
        rho, c = geometry.air_density_kg_m3, geometry.sound_speed_m_s
        self.geometry = geometry
        self.subdivisions = subdivisions
        self.dt_s = dt_s
        self.outlet_resistance = outlet_resistance_pa_s_m3
        self.lengths_m = dx
        self.areas_m2 = area
        self.cell_compliance = area * dx / (rho*c*c)
        self.face_inertance = np.empty(len(dx) + 1)
        self.face_inertance[0] = rho*dx[0]/(2*area[0])
        self.face_inertance[-1] = rho*dx[-1]/(2*area[-1])
        self.face_inertance[1:-1] = rho*(dx[:-1]/area[:-1]+dx[1:]/area[1:])/2
        n = len(dx)
        self.state = AcousticState(np.zeros(n), np.zeros(n+1))
        # Pressure midpoints solved from a symmetric positive definite tridiagonal system.
        self.diag = 2 * self.cell_compliance / dt_s
        self.alpha = dt_s/(2 * self.face_inertance)
        self.beta_end = 1/(2*self.face_inertance[-1]/dt_s+outlet_resistance_pa_s_m3)
        self.gamma_end = 2*self.face_inertance[-1]/dt_s * self.beta_end
        self.main = self.diag.copy()
        self.off = -self.alpha[1:-1].copy()
        self.main[0] += self.alpha[1] if n>1 else self.beta_end
        if n>1:
            self.main[1:] += self.alpha[1:-1]
            self.main[1:-1] += self.alpha[2:-1]
            self.main[-1] += self.beta_end
        self.lu_denom = np.empty(n)
        self.lu_upper = np.empty(max(n-1,0))
        self.lu_denom[0] = self.main[0]
        for i in range(n-1):
            self.lu_upper[i] = self.off[i]/self.lu_denom[i]
            self.lu_denom[i+1] = self.main[i+1]-self.off[i]*self.lu_upper[i]
        if not np.all(self.lu_denom>0):
            raise ValueError('invalid positive-definite acoustic matrix')

    def energy(self, state: AcousticState | None = None) -> float:
        s = state if state is not None else self.state
        return float(0.5*(np.dot(self.cell_compliance, s.pressure_pa**2)
                          +np.dot(self.face_inertance,s.face_flow_m3_s**2)))

    def step(self, inlet_flow_m3_s: float) -> StepObservation:
        if not math.isfinite(inlet_flow_m3_s):
            raise ValueError('inlet flow must be finite')
        previous = self.state
        p, u = previous.pressure_pa, previous.face_flow_m3_s
        old_energy = self.energy()
        mid_inlet = 0.5*(u[0]+inlet_flow_m3_s)
        rhs = self.diag*p
        rhs[0] += mid_inlet
        if len(p)>1:
            rhs[0] -= u[1]
            rhs[1:-1] += u[1:-2]-u[2:-1]
            rhs[-1] += u[-2]-self.gamma_end*u[-1]
        else:
            rhs[0] -= self.gamma_end*u[-1]
        # LDL tridiagonal solve, pre-factorized.
        forward = np.empty_like(p)
        forward[0] = rhs[0]/self.lu_denom[0]
        for i in range(1, len(p)):
            forward[i] = (rhs[i]-self.off[i-1]*forward[i-1])/self.lu_denom[i]
        x = np.empty_like(p)
        x[-1] = forward[-1]
        for i in range(len(p)-2,-1,-1):
            x[i] = forward[i]-self.lu_upper[i]*x[i+1]
        umid = np.empty_like(u)
        umid[0] = mid_inlet
        umid[1:-1] = u[1:-1]+self.alpha[1:-1]*(x[:-1]-x[1:])
        umid[-1] = self.gamma_end*u[-1]+self.beta_end*x[-1]
        pnew = 2*x-p
        unew = 2*umid-u
        unew[0] = inlet_flow_m3_s
        self.state = AcousticState(pnew,unew)
        inlet_pressure = x[0]+self.face_inertance[0]*(inlet_flow_m3_s-u[0])/self.dt_s
        injected = self.dt_s*inlet_pressure*mid_inlet
        dissipated = self.dt_s*self.outlet_resistance*umid[-1]**2
        energy_new = self.energy()
        return StepObservation(float(inlet_pressure), float(mid_inlet),float(umid[-1]),
                               energy_new,float(injected),float(dissipated),
                               float((energy_new-old_energy)-(injected-dissipated)))


def exact_uniform_impedance(frequency_hz: float, geometry: Geometry, load: float) -> complex:
    rho, c, a, length = (geometry.air_density_kg_m3,geometry.sound_speed_m_s,
                         geometry.areas_m2[0],geometry.total_length_m)
    if any(area != a for area in geometry.areas_m2):
        raise ValueError('analytic oracle requires uniform area')
    zc = rho*c/a
    phi = 2*math.pi*frequency_hz*length/c
    return zc*(load+1j*zc*math.tan(phi))/(zc+1j*load*math.tan(phi))


def pressure_release_eigenfrequencies(geometry: Geometry, subdivisions: int,
                                       count: int = 3) -> np.ndarray:
    """Numerical semi-discrete free modes for p_out=0, u_in=0 (no time stepping)."""
    if count < 1:
        raise ValueError('count must be positive')
    model = PassiveTract(geometry=geometry,subdivisions=subdivisions,outlet_resistance_pa_s_m3=0.0)
    n = len(model.cell_compliance)
    # K = D M^-1 D^T ; D_i j = 1 at upstream, -1 at downstream, excluding fixed U0.
    d = np.zeros((n,n))
    for i in range(n):
        if i>0: d[i,i-1] = 1.0
        d[i,i] = -1.0
    k = (d/model.face_inertance[1:]) @ d.T
    h = k/np.sqrt(np.outer(model.cell_compliance,model.cell_compliance))
    eigs = np.linalg.eigvalsh(h)
    return np.sqrt(np.maximum(eigs[:count],0))/(2*math.pi)
