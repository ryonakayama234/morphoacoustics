"""Independent/adversarial G0-P tests, separate from the adapter implementation."""
from __future__ import annotations

import math
from pathlib import Path
import sys

import pytest

# This file is a research experiment, not a public installed package.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from port import FixedWaveguideInletPort, StalePortSnapshot  # noqa: E402

from morphoacoustics.physical import Tract1DGeometry, TubeSection  # noqa: E402
from morphoacoustics_waveguide import (  # noqa: E402
    PassiveWaveguideConfig,
    PassiveWaveguideSession,
)


def model(
    areas=(0.0008,),
    *,
    length=0.01,
    cells=2,
    termination="matched",
    forward=None,
    backward=None,
    b0_q=0.0,
):
    geom = Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(TubeSection(length_m=length, area_m2=a) for a in areas),
    )
    cfg = PassiveWaveguideConfig(
        geom, cells_per_section=cells, termination=termination
    )
    return PassiveWaveguideSession(
        cfg,
        initial_forward_pa=forward,
        initial_backward_pa=backward,
        initial_b0_q_m3_s=b0_q,
    )


def native_state(s):
    return (
        s.ticks,
        s.config,
        tuple(tuple(q) for q in s.forward),
        tuple(tuple(q) for q in s.backward),
        None if s._radiation is None else s._radiation.q,
        s.energies_j(),
    )


def oracle_pressure(s, flow):
    """Reconstruct native p independently of adapter using incident pressure waves.

    This oracle intentionally uses a separately stated wave boundary, not peek.
    """
    rho = s.config.air_density_kg_m3
    c = s.config.sound_speed_m_s
    area = s.config.geometry.sections[0].area_m2
    incident = s.backward[0][0]
    return incident + (incident + (rho * c / area) * flow)


def assert_pressure(pred, ref, *, b, z, flow):
    scale = max(abs(2 * b) + abs(z * flow), 1.0)
    assert abs(pred - ref) / scale <= 1e-10


@pytest.mark.parametrize("term", ["matched", "closed", "pressure_release", "b0"])
@pytest.mark.parametrize("cells", [2, 4])
@pytest.mark.parametrize("flow", [0.0, 1e-6, -1e-6])
def test_independent_initial_reflection_prediction_and_state_purity(term, cells, flow):
    back = (tuple([1.25] + [0.0] * (cells - 1)),)
    s = model(cells=cells, termination=term, backward=back)
    port = FixedWaveguideInletPort(s)
    snap = port.snapshot()
    before = native_state(s)
    z = 1.21 * 343 / 0.0008
    assert snap.b_pa == 1.25
    assert snap.z0_pa_s_m3 == pytest.approx(z)
    assert snap.dt_s == pytest.approx(0.01 / (343 * cells))
    probes = [port.peek(snap, u) for u in (0.0, 1e-6, -1e-6, flow)]
    assert native_state(s) == before
    assert [p.flow_m3_s for p in probes] == [0.0, 1e-6, -1e-6, flow]
    pred = probes[-1]
    ref = oracle_pressure(s, flow)
    assert_pressure(pred.pressure_pa, ref, b=1.25, z=z, flow=flow)
    assert pred.source_work_j == pytest.approx(
        s.config.timestep_s * ref * flow, rel=1e-12, abs=1e-24
    )
    old_energy = sum(s.energies_j())
    obs = port.commit_once(snap, flow)
    assert obs.tick == before[0] and s.ticks == before[0] + 1
    assert_pressure(obs.source_pressure_pa, ref, b=1.25, z=z, flow=flow)
    assert obs.source_work_j == pytest.approx(pred.source_work_j, rel=1e-12, abs=1e-24)
    assert obs.delta_stored_energy_j == pytest.approx(
        sum(s.energies_j()) - old_energy, rel=1e-12, abs=1e-20
    )
    with pytest.raises(StalePortSnapshot):
        port.commit_once(snap, flow)
    with pytest.raises(StalePortSnapshot):
        port.peek(snap, 0.0)


@pytest.mark.parametrize("term,reflection_sign", [
    ("closed", 1.0), ("pressure_release", -1.0), ("matched", 0.0)
])
@pytest.mark.parametrize("cells", [2, 4])
def test_closed_release_matched_return_after_exact_roundtrip(term, reflection_sign, cells):
    s = model(termination=term, cells=cells)
    port = FixedWaveguideInletPort(s)
    pulse_u = 1e-6
    z = 1.21 * 343 / 0.0008
    # First source pulse launches pressure wave ZU.
    port.commit_once(port.snapshot(), pulse_u)
    for _ in range(2 * cells - 1):
        snap = port.snapshot()
        assert snap.b_pa == 0.0
        port.commit_once(snap, 0.0)
    snap = port.snapshot()
    # Independent closed/open acoustic boundary oracle:
    # returned wave is +incident, -incident, or 0 after 2*cells ticks.
    expected_b = reflection_sign * z * pulse_u
    assert snap.tick == 2 * cells
    assert snap.b_pa == pytest.approx(expected_b, abs=1e-15)
    pred = port.peek(snap, 0.0)
    assert pred.pressure_pa == pytest.approx(2 * expected_b, abs=1e-15)
    if reflection_sign != 0:
        # A wrong-sign oracle, a delayed port, and a wrong impedance should fail.
        wrong_sign = -2 * expected_b
        assert abs(pred.pressure_pa - wrong_sign) > 0.1
    port.commit_once(snap, 0.0)


def test_two_section_junction_analytic_reflection_and_signed_power():
    zl, zr = (1.21 * 343 / a for a in (0.0008, 0.0004))
    r = (zr - zl) / (zr + zl)  # Independent junction pressure reflection.
    s = model(
        areas=(0.0008, 0.0004), termination="matched",
        forward=((1.0, 0.0), (0.0, 0.0)),
    )
    port = FixedWaveguideInletPort(s)
    port.commit_once(port.snapshot(), 0.0)  # first wave scatters at junction
    # Wave 1 incident at the junction, wave 2 incident = 0.
    # Pressure and flow continuity yield reflected=r and transmitted=1+r.
    reflected = s.backward[0][-1]
    transmitted = s.forward[1][-1]
    assert reflected == pytest.approx(r, rel=1e-13)
    assert transmitted == pytest.approx(1 + r, rel=1e-13)
    assert 1 + reflected == pytest.approx(transmitted, rel=1e-13)
    assert (1 - reflected) / zl == pytest.approx(transmitted / zr, rel=1e-13)
    assert (1 - reflected**2) / zl == pytest.approx(transmitted**2 / zr, rel=1e-13)
    port.commit_once(port.snapshot(), 0.0)
    snap = port.snapshot()
    assert snap.b_pa == pytest.approx(r, rel=1e-13)
    assert port.peek(snap, 0.0).pressure_pa == pytest.approx(2 * r, rel=1e-13)


@pytest.mark.parametrize("termination", ["matched", "pressure_release", "closed", "b0"])
def test_signed_power_ledger_nontrivial_endpoints(termination):
    s = model(areas=(0.0008, 0.0004), termination=termination)
    port = FixedWaveguideInletPort(s)
    saw_reflection = False
    saw_nonzero_energy = False
    for tick in range(128):
        snap = port.snapshot()
        u = 1e-6 * math.sin(0.171 * (tick + 1)) if tick < 64 else 0.0
        saw_reflection |= abs(snap.b_pa) > 1e-9
        ref = oracle_pressure(s, u)
        before_e = sum(s.energies_j())
        pred = port.peek(snap, u)
        assert_pressure(pred.pressure_pa, ref, b=snap.b_pa, z=snap.z0_pa_s_m3, flow=u)
        obs = port.commit_once(snap, u)
        after_e = sum(s.energies_j())
        delta = after_e - before_e
        signed_residual = delta - obs.source_work_j + obs.outlet_dissipation_j
        assert obs.delta_stored_energy_j == pytest.approx(delta, rel=1e-11, abs=1e-20)
        scale = max(abs(delta) + abs(obs.source_work_j)
                    + abs(obs.outlet_dissipation_j), 1e-12)
        assert abs(signed_residual) / scale <= 1e-10
        assert abs(obs.energy_residual_j) / scale <= 1e-10
        assert obs.duct_energy_j >= 0 and obs.radiation_energy_j >= 0
        assert obs.outlet_dissipation_j >= 0
        saw_nonzero_energy |= after_e > 1e-14
    assert saw_reflection, "test never exercised a genuinely evolved inlet reflection"
    assert saw_nonzero_energy, "test had no substantial stored acoustic energy"


@pytest.mark.parametrize("length", [0.010, 0.011])
def test_native_16_section_surrogate_duct_first_arrival_not_48khz(length):
    s = model(areas=(0.0008,) * 16, length=length, termination="matched")
    port = FixedWaveguideInletPort(s)
    dt = length / (343.0 * 2)
    assert port.snapshot().dt_s == pytest.approx(dt, rel=1e-14)
    assert dt != pytest.approx(1.0 / 48000.0)
    arrivals = []
    for k in range(34):
        obs = port.commit_once(port.snapshot(), 1e-6 if k == 0 else 0.0)
        arrivals.append(obs.mouth_pressure_pa)
    assert arrivals[:32] == [0.0] * 32
    assert arrivals[32] != 0.0


def test_snapshot_foreign_stale_direct_mutation_and_b0_state_rejected():
    s = model(termination="b0")
    port = FixedWaveguideInletPort(s)
    other = FixedWaveguideInletPort(s)
    snap = port.snapshot()
    with pytest.raises(StalePortSnapshot):
        other.peek(snap, 0.0)
    with pytest.raises(StalePortSnapshot):
        other.commit_once(snap, 0.0)
    assert s.ticks == 0
    s.forward[0][-1] = 0.002  # bypass adapter
    with pytest.raises(StalePortSnapshot):
        port.commit_once(snap, 0.0)
    fresh = port.snapshot()
    assert s._radiation is not None
    s._radiation.q = 1e-9  # direct B0 state mutation
    with pytest.raises(StalePortSnapshot):
        port.peek(fresh, 0.0)
    assert s.ticks == 0


def test_negative_input_and_failure_atomic_retry():
    s = model(termination="b0")
    port = FixedWaveguideInletPort(s)
    snap = port.snapshot()
    before = native_state(s)
    for u in (float("nan"), float("inf"), float("-inf"), True, False,
              "1e-6", None, 1+0j):
        with pytest.raises((ValueError, TypeError)):
            port.commit_once(snap, u)
        assert native_state(s) == before
    with pytest.raises(FloatingPointError):
        port.commit_once(snap, 1e308)
    assert native_state(s) == before
    # Same snapshot is reusable after *failed* commit, unlike a successful commit.
    obs = port.commit_once(snap, 1e-6)
    assert obs.tick == 0 and s.ticks == 1


def test_zero_drive_zero_state_no_phantom_source():
    s = model(termination="b0")
    port = FixedWaveguideInletPort(s)
    for tick in range(20):
        snap = port.snapshot()
        p = port.peek(snap, 0.0)
        assert p.pressure_pa == 0.0 and p.source_work_j == 0.0
        obs = port.commit_once(snap, 0.0)
        assert obs.tick == tick
        assert obs.source_work_j == obs.energy_residual_j == 0.0
        assert s.energies_j() == (0.0, 0.0)
