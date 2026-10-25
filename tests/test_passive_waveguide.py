"""CORE-WG-1: preregistered static passive waveguide regression controls."""
from __future__ import annotations

from math import isclose, pi, sqrt

import numpy as np
import pytest

from morphoacoustics_waveguide import (
    PassiveWaveguideConfig,
    PassiveWaveguideSession,
    scatter_pressures,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection


def tract(length: float = 0.01, areas: tuple[float, ...] | None = None) -> Tract1DGeometry:
    if areas is None:
        areas = (0.0008,) * 16
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(TubeSection(length_m=length, area_m2=a) for a in areas),
    )


@pytest.mark.parametrize("left,right", [(1.5, 0.0), (0.0, -0.7), (1.5, -0.7), (-2.0, 3.0)])
def test_junction_pressure_flow_and_energy_are_conserved(left: float, right: float) -> None:
    zl, zr = 350000.0, 1250000.0
    outgoing_left, outgoing_right = scatter_pressures(left, right, zl, zr)
    assert left + outgoing_left == pytest.approx(outgoing_right + right, rel=1e-12)
    assert (left - outgoing_left) / zl == pytest.approx(
        (outgoing_right - right) / zr, rel=1e-12, abs=1e-20
    )
    assert (left**2 - outgoing_left**2) / zl == pytest.approx(
        (outgoing_right**2 - right**2) / zr, rel=1e-12, abs=1e-20
    )


def test_clock_and_local_first_arrival_follow_body_length() -> None:
    arrival_times: list[float] = []
    for length in (0.01, 0.011):
        config = PassiveWaveguideConfig(tract(length), termination="matched")
        assert config.physics_clock_hz == pytest.approx(343.0 * 2 / length)
        session = PassiveWaveguideSession(config)
        pressures = [session.step(1e-6 if k == 0 else 0.0).mouth_pressure_pa
                     for k in range(38)]
        assert np.all(np.array(pressures[:32]) == 0.0)
        assert pressures[32] != 0.0
        arrival_times.append(32.0 / config.physics_clock_hz)
    assert isclose(arrival_times[1] / arrival_times[0], 1.1, abs_tol=1e-13)


def test_empty_waveguide_is_silent_without_external_flow() -> None:
    model = PassiveWaveguideSession(PassiveWaveguideConfig(tract()))
    for k in range(100):
        step = model.step(0.0)
        assert step.tick == k
        assert step.mouth_pressure_pa == 0.0
        assert step.source_work_j == 0.0
        assert step.duct_energy_j == 0.0
        assert step.radiation_energy_j == 0.0


@pytest.mark.parametrize("termination", ["closed", "pressure_release", "matched", "b0"])
def test_signed_port_energy_ledger(termination: str) -> None:
    areas = tuple(0.0003 + 0.00004 * (j % 7) for j in range(16))
    config = PassiveWaveguideConfig(tract(areas=areas), termination=termination)
    model = PassiveWaveguideSession(config)
    random = np.random.default_rng(20261025)
    energy = 0.0
    drive = list(random.normal(0.0, 1e-6, 128)) + [0.0] * 512
    for u in drive:
        step = model.step(float(u))
        delta = step.delta_stored_energy_j
        w = step.source_work_j
        diss = step.outlet_dissipation_j
        e = step.duct_energy_j + step.radiation_energy_j
        tol = max(1e-9 * max(abs(delta), abs(w), diss, 1e-20),
                  1e-12 * max(energy, e, 1e-20))
        assert abs(step.energy_residual_j) <= tol
        assert step.duct_energy_j >= 0
        assert step.radiation_energy_j >= 0
        assert step.outlet_dissipation_j >= 0
        energy = e


def test_original_b0_equations_derive_outlet_state_from_lip_area() -> None:
    area = 0.0008
    cfg = PassiveWaveguideConfig(tract(areas=(area,)), termination="b0")
    model = PassiveWaveguideSession(
        cfg, initial_forward_pa=((1.0, 0.0),)
    )
    step = model.step(0.0)
    radius = sqrt(area / pi)
    z = cfg.air_density_kg_m3 * cfg.sound_speed_m_s / area
    m = 8 * cfg.air_density_kg_m3 * radius / (3 * pi * area)
    tau = 3 * pi * radius / (16 * cfg.sound_speed_m_s)
    resistance = m / tau
    mid = 2.0 / (1.0 + z / resistance + z * cfg.timestep_s / (2 * m))
    expected_b = mid - 1.0
    assert step.mouth_pressure_pa == pytest.approx(1.0 + expected_b, rel=1e-12)
    assert step.mouth_flow_m3_s == pytest.approx((1.0 - expected_b) / z, rel=1e-12)
    q = cfg.timestep_s * mid / m
    assert step.radiation_energy_j == pytest.approx(0.5 * m * q**2, rel=1e-12)
    assert step.outlet_dissipation_j == pytest.approx(
        cfg.timestep_s * mid**2 / resistance, rel=1e-12
    )


def test_reject_unsupported_length_and_invalid_flow_without_mutation() -> None:
    bad = Tract1DGeometry(
        cavity_id="oral",
        sections=(TubeSection(0.01, 0.0008), TubeSection(0.011, 0.0006)),
    )
    with pytest.raises(ValueError, match="unequal"):
        PassiveWaveguideConfig(bad)
    session = PassiveWaveguideSession(PassiveWaveguideConfig(tract()))
    before = (tuple(tuple(q) for q in session.forward),
              tuple(tuple(q) for q in session.backward), session.energies_j())
    with pytest.raises(ValueError, match="inlet flow"):
        session.step(float("nan"))
    assert (tuple(tuple(q) for q in session.forward),
            tuple(tuple(q) for q in session.backward), session.energies_j()) == before
    assert session.ticks == 0


def test_extreme_impedances_do_not_silently_overflow_scattering() -> None:
    reflected, transmitted = scatter_pressures(1.0, 0.0, 1e308, 1.5e308)
    assert reflected == pytest.approx(0.2, abs=1e-15)
    assert transmitted == pytest.approx(1.2, abs=1e-15)
    r1 = scatter_pressures(-1.5, 0.25, 1e200, 1.5e200)
    r2 = scatter_pressures(-1.5, 0.25, 1e300, 1.5e300)
    assert r1 == pytest.approx(r2, rel=1e-13)


@pytest.mark.parametrize(
    "geometry,rho,c",
    [
        (tract(areas=(1e-310,)), 1.21, 343.0),
        (tract(), 1e-300, 1e-300),
        (tract(1e-309), 1.21, 343.0),
    ],
)
def test_derived_physical_coefficients_must_be_finite(
    geometry: Tract1DGeometry, rho: float, c: float,
) -> None:
    with pytest.raises(ValueError):
        PassiveWaveguideConfig(
            geometry, air_density_kg_m3=rho, sound_speed_m_s=c
        )


def test_large_finite_input_failure_is_atomic_for_waves_and_b0() -> None:
    session = PassiveWaveguideSession(PassiveWaveguideConfig(tract()))
    session.step(1e-6)
    initial_forward = tuple(tuple(q) for q in session.forward)
    initial_backward = tuple(tuple(q) for q in session.backward)
    initial_energy = session.energies_j()
    tick = session.ticks
    with pytest.raises(FloatingPointError):
        session.step(1e308)
    assert tuple(tuple(q) for q in session.forward) == initial_forward
    assert tuple(tuple(q) for q in session.backward) == initial_backward
    assert session.energies_j() == initial_energy
    assert session.ticks == tick
    # A failed call cannot poison the next ordinary physical tick.
    assert np.isfinite(session.step(0.0).mouth_pressure_pa)


def test_failed_nonfinite_initial_wave_is_rejected() -> None:
    with pytest.raises(ValueError, match="nonfinite initial wave"):
        PassiveWaveguideSession(
            PassiveWaveguideConfig(tract(areas=(0.0008,))),
            initial_forward_pa=((0.0, float("inf")),),
        )
