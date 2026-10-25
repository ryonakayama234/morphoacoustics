"""Experimental static causal 1D waveguide (CORE-WG-1).

Port of the independently audited passive method from research B0/B1b/B2-A.
This is a physical acoustic *port*, not a synthesizer, voice renderer or 48k
sample-rate converter. See docs/research/core-passive-waveguide/GATE_A.md.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isclose, isfinite, pi, sqrt

from morphoacoustics.physical import Tract1DGeometry


@dataclass(frozen=True, slots=True)
class PassiveWaveguideConfig:
    """Geometry-derived clock; no implicit 48 kHz section rounding."""

    geometry: Tract1DGeometry
    cells_per_section: int = 2
    termination: str = "b0"
    air_density_kg_m3: float = 1.21
    sound_speed_m_s: float = 343.0

    def __post_init__(self) -> None:
        if type(self.cells_per_section) is not int or self.cells_per_section not in (2, 4, 8):
            raise ValueError("cells_per_section must be 2, 4, or 8")
        if self.termination not in ("b0", "closed", "pressure_release", "matched"):
            raise ValueError("unsupported passive outlet")
        for value in (self.air_density_kg_m3, self.sound_speed_m_s):
            if not isfinite(value) or value <= 0:
                raise ValueError("air properties must be finite and positive")
        first = self.geometry.sections[0].length_m
        if any(not isclose(section.length_m, first, rel_tol=0, abs_tol=1e-14)
               for section in self.geometry.sections):
            raise ValueError("unequal section lengths require a different verified solver")
        if not isfinite(self.physics_clock_hz):
            raise ValueError("nonfinite physical clock")

    @property
    def physics_clock_hz(self) -> float:
        return self.sound_speed_m_s * self.cells_per_section / self.geometry.sections[0].length_m

    @property
    def timestep_s(self) -> float:
        return 1.0 / self.physics_clock_hz

    @property
    def characteristic_impedances_pa_s_m3(self) -> tuple[float, ...]:
        return tuple(self.air_density_kg_m3 * self.sound_speed_m_s / section.area_m2
                     for section in self.geometry.sections)


@dataclass(frozen=True, slots=True)
class WaveguideStep:
    tick: int
    inlet_flow_m3_s: float
    source_pressure_pa: float
    mouth_pressure_pa: float
    mouth_flow_m3_s: float
    duct_energy_j: float
    radiation_energy_j: float
    source_work_j: float
    outlet_dissipation_j: float
    delta_stored_energy_j: float
    energy_residual_j: float


def scatter_pressures(
    left_incident_pa: float,
    right_incident_pa: float,
    left_impedance_pa_s_m3: float,
    right_impedance_pa_s_m3: float,
) -> tuple[float, float]:
    """Outgoing (left, right) pressure waves; local passive interface."""
    zl, zr = left_impedance_pa_s_m3, right_impedance_pa_s_m3
    if not all(isfinite(v) for v in
               (left_incident_pa, right_incident_pa, zl, zr)) or zl <= 0 or zr <= 0:
        raise ValueError("finite pressures and positive finite impedances required")
    r = (zr - zl) / (zr + zl)
    a, b = left_incident_pa, right_incident_pa
    return r * a + (1.0 - r) * b, (1.0 + r) * a - r * b


class _B0Radiation:
    """Fixed-aperture passive RL port from research B0; SI units."""

    def __init__(self, cfg: PassiveWaveguideConfig, initial_q_m3_s: float) -> None:
        area = cfg.geometry.sections[-1].area_m2
        radius = sqrt(area / pi)
        rho, c = cfg.air_density_kg_m3, cfg.sound_speed_m_s
        self.zc = rho * c / area
        self.m = 8.0 * rho * radius / (3.0 * pi * area)
        self.tau = 3.0 * pi * radius / (16.0 * c)
        self.resistance = self.m / self.tau
        self.h = cfg.timestep_s
        self.q = initial_q_m3_s

    @property
    def energy_j(self) -> float:
        return 0.5 * self.m * self.q * self.q

    def step(self, incident_pa: float) -> tuple[float, float]:
        denom = 1.0 + self.zc / self.resistance
        denom += self.zc * self.h / (2.0 * self.m)
        pressure = (2.0 * incident_pa - self.zc * self.q) / denom
        new_q = self.q + self.h * pressure / self.m
        reflected = pressure - incident_pa
        dissipation = self.h * pressure * pressure / self.resistance
        if not all(isfinite(v) for v in (new_q, reflected, dissipation)):
            raise FloatingPointError("nonfinite radiation state")
        self.q = new_q
        return reflected, dissipation


class PassiveWaveguideSession:
    """Mutable per-take state; one shift per local physical clock tick.

    No shared/global wave state. The caller is responsible for retaining this
    session across contiguous physical intervals rather than resetting it.
    """

    def __init__(
        self,
        config: PassiveWaveguideConfig,
        *,
        initial_forward_pa: tuple[tuple[float, ...], ...] | None = None,
        initial_backward_pa: tuple[tuple[float, ...], ...] | None = None,
        initial_b0_q_m3_s: float = 0.0,
    ) -> None:
        self.config = config
        n = len(config.geometry.sections)
        cells = config.cells_per_section
        self.forward = self._queues(initial_forward_pa, n, cells)
        self.backward = self._queues(initial_backward_pa, n, cells)
        if not isfinite(initial_b0_q_m3_s):
            raise ValueError("nonfinite initial radiation state")
        if config.termination != "b0" and initial_b0_q_m3_s != 0.0:
            raise ValueError("radiation state requires B0 termination")
        self._radiation = (
            _B0Radiation(config, initial_b0_q_m3_s) if config.termination == "b0" else None
        )
        self.ticks = 0

    @staticmethod
    def _queues(
        data: tuple[tuple[float, ...], ...] | None,
        n: int,
        cells: int,
    ) -> list[deque[float]]:
        if data is None:
            return [deque([0.0] * cells) for _ in range(n)]
        if len(data) != n or any(len(section) != cells for section in data):
            raise ValueError("wrong initial wave shape")
        if not all(isfinite(v) for section in data for v in section):
            raise ValueError("nonfinite initial wave")
        return [deque(float(v) for v in section) for section in data]

    def energies_j(self) -> tuple[float, float]:
        h = self.config.timestep_s
        impedances = self.config.characteristic_impedances_pa_s_m3
        duct = h * sum(
            (sum(x * x for x in self.forward[j]) + sum(x * x for x in self.backward[j]))
            / impedance
            for j, impedance in enumerate(impedances)
        )
        radiation = self._radiation.energy_j if self._radiation is not None else 0.0
        return duct, radiation

    def step(self, inlet_flow_m3_s: float) -> WaveguideStep:
        if isinstance(inlet_flow_m3_s, bool) or not isfinite(inlet_flow_m3_s):
            raise ValueError("inlet flow must be finite")
        cfg = self.config
        h = cfg.timestep_s
        impedances = cfg.characteristic_impedances_pa_s_m3
        old_energy = sum(self.energies_j())

        incident_forward = [q.popleft() for q in self.forward]
        incident_backward = [q.popleft() for q in self.backward]
        next_forward = [0.0] * len(incident_forward)
        next_backward = [0.0] * len(incident_backward)
        next_forward[0] = incident_backward[0] + impedances[0] * inlet_flow_m3_s
        for j in range(len(incident_forward) - 1):
            next_backward[j], next_forward[j + 1] = scatter_pressures(
                incident_forward[j], incident_backward[j + 1], impedances[j], impedances[j + 1]
            )
        mouth_incident = incident_forward[-1]
        if cfg.termination == "closed":
            mouth_reflected, loss = mouth_incident, 0.0
        elif cfg.termination == "pressure_release":
            mouth_reflected, loss = -mouth_incident, 0.0
        elif cfg.termination == "matched":
            mouth_reflected, loss = 0.0, h * mouth_incident**2 / impedances[-1]
        else:
            assert self._radiation is not None
            mouth_reflected, loss = self._radiation.step(mouth_incident)
        next_backward[-1] = mouth_reflected

        for queue, value in zip(self.forward, next_forward, strict=True):
            queue.append(value)
        for queue, value in zip(self.backward, next_backward, strict=True):
            queue.append(value)
        pressure_in = next_forward[0] + incident_backward[0]
        pressure_out = mouth_incident + mouth_reflected
        flow_out = (mouth_incident - mouth_reflected) / impedances[-1]
        duct, radiation = self.energies_j()
        delta_e = duct + radiation - old_energy
        source_work = h * pressure_in * inlet_flow_m3_s
        residual = delta_e - source_work + loss
        if not all(isfinite(v) for v in
                   (pressure_in, pressure_out, flow_out, duct, radiation,
                    delta_e, source_work, residual)):
            raise FloatingPointError("nonfinite waveguide state")
        tick = self.ticks
        self.ticks += 1
        return WaveguideStep(
            tick, inlet_flow_m3_s, pressure_in, pressure_out, flow_out,
            duct, radiation, source_work, loss, delta_e, residual
        )
