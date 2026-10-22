"""Preregistered EL-R1 tests: independent Wolfram oracle and physical nulls."""
from __future__ import annotations

import importlib
import json
from math import pi
from pathlib import Path
import sys

import numpy as np
import pytest

from morphoacoustics.acoustics.uniform_tube import UniformTube

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "experiments" / "043_el_r1_ear_port"
sys.path.insert(0, str(RESEARCH))
port = importlib.import_module("listener_port")
ORACLE = json.loads((RESEARCH / "wolfram_oracle.json").read_text(encoding="utf-8"))


def z(rec: dict[str, float]) -> complex:
    return complex(rec["real"], rec["imag"])


@pytest.mark.parametrize("row", ORACLE["rows"])
def test_independently_executed_wolfram_oracle(row: list[float]) -> None:
    length, ratio, hr, hi, gr, gi, power = row
    response = port.evaluate(port.ListenerFixture(length_m=length, terminal_resistance_ratio_to_zc=ratio),
                             port.EntranceDrive(frequencies_hz=(3000,)))
    entry = response["frequencies"][0]
    assert abs(z(entry["transfer_pressure_terminal_per_entrance"]) - complex(hr, hi)) <= 1e-11
    assert abs(z(entry["entrance_reflection_coefficient"]) - complex(gr, gi)) <= 1e-11
    assert abs(entry["entrance"]["mean_active_power_w"] * entry["characteristic_impedance_pa_s_m3"] - power) <= 1e-11


@pytest.mark.parametrize("length", [0.02, 0.025, 0.03])
@pytest.mark.parametrize("ratio", [0.5, 1.0, 2.0])
def test_passivity_and_matrix_invariant(length: float, ratio: float) -> None:
    frequencies = (0, 1000, 3000, 7000)
    response = port.evaluate(port.ListenerFixture(length_m=length, terminal_resistance_ratio_to_zc=ratio),
                             port.EntranceDrive(frequencies_hz=frequencies))
    tube = UniformTube(length_m=length, area_m2=3e-5)
    det = np.linalg.det(tube.transfer_matrix(np.array(frequencies)))
    assert np.max(np.abs(det - 1)) <= 1e-12
    for row in response["frequencies"]:
        entry, terminal = row["entrance"], row["terminal"]
        pi_w = entry["mean_active_power_w"]
        po_w = terminal["mean_active_power_w"]
        assert abs(pi_w - po_w) <= 1e-10 * max(1e-12, abs(pi_w), abs(po_w))
        assert pi_w >= -1e-12 and po_w >= -1e-12
        assert abs(z(row["entrance_reflection_coefficient"])) < 1+1e-12
        assert abs(z(entry["pressure_pa"]) - 1) <= 1e-11
        assert abs(z(terminal["pressure_pa"]) - ratio*tube.characteristic_impedance_pa_s_m3*z(terminal["volume_velocity_m3_s"])) <= 1e-11


@pytest.mark.parametrize("frequency", [0, 1234, 3000, 7000])
def test_matched_load_free_phase(frequency: float) -> None:
    l = 0.025
    output = port.evaluate(port.ListenerFixture(terminal_resistance_ratio_to_zc=1),
                           port.EntranceDrive(frequencies_hz=(frequency,)))
    row = output["frequencies"][0]
    expected = np.exp(-1j*2*pi*frequency*l/343)
    assert abs(z(row["transfer_pressure_terminal_per_entrance"]) - expected) <= 1e-11
    assert abs(z(row["entrance_reflection_coefficient"])) <= 1e-11


def test_shape_intervention_and_standing_pressure_gain_not_energy_gain() -> None:
    hs = []
    for length in [0.02, 0.025, 0.03]:
        row = port.evaluate(port.ListenerFixture(length_m=length), port.EntranceDrive(frequencies_hz=(3000,)))["frequencies"][0]
        hs.append(z(row["transfer_pressure_terminal_per_entrance"]))
        assert row["entrance"]["mean_active_power_w"] == pytest.approx(row["terminal"]["mean_active_power_w"], rel=1e-10)
    assert all(abs(a-b) > 1e-3 for a,b in zip(hs,hs[1:]))
    assert all(abs(h) > 1.0 for h in hs)
    assert hs[0].imag < 0  # Mutation control: flipped Fourier sign would fail.
    assert abs(hs[0]-hs[0].conjugate()) > .1


def test_complex_drive_scales_power_quadratically() -> None:
    f = port.ListenerFixture()
    base = port.evaluate(f,port.EntranceDrive(frequencies_hz=(3000,)))["frequencies"][0]
    amp = 1+2j
    candidate = port.evaluate(f,port.EntranceDrive(frequencies_hz=(3000,), entrance_pressure_pa=amp))["frequencies"][0]
    assert z(candidate["terminal"]["pressure_pa"]) == pytest.approx(amp*z(base["terminal"]["pressure_pa"]))
    assert candidate["entrance"]["mean_active_power_w"] == pytest.approx(5*base["entrance"]["mean_active_power_w"],rel=1e-11)


def test_zero_drive_is_zero_state_with_defined_transfer() -> None:
    row = port.evaluate(port.ListenerFixture(), port.EntranceDrive(frequencies_hz=(3000,), entrance_pressure_pa=0j))["frequencies"][0]
    assert z(row["terminal"]["pressure_pa"]) == 0j
    assert z(row["entrance"]["volume_velocity_m3_s"]) == 0j
    assert row["entrance"]["mean_active_power_w"] == 0
    assert z(row["transfer_pressure_terminal_per_entrance"]) != 0j


@pytest.mark.parametrize("fixture,drive,expected", [
    (port.ListenerFixture(length_m=-.02), port.EntranceDrive(), port.InvalidListener),
    (port.ListenerFixture(section_area_m2=float("nan")), port.EntranceDrive(), port.InvalidListener),
    (port.ListenerFixture(terminal_resistance_ratio_to_zc=0), port.EntranceDrive(), port.InvalidListener),
    (port.ListenerFixture(terminal_resistance_ratio_to_zc=True), port.EntranceDrive(), port.InvalidListener),
    (port.ListenerFixture(length_m=.08), port.EntranceDrive(), port.UnsupportedListener),
    (port.ListenerFixture(terminal_resistance_ratio_to_zc=5), port.EntranceDrive(), port.UnsupportedListener),
    (port.ListenerFixture(terminal_load_kind="PASSIVE_COMPLEX_IMPEDANCE"), port.EntranceDrive(), port.UnsupportedListener),
    (port.ListenerFixture(), port.EntranceDrive(reference_plane="BLOCKED_EAR_HRTF"), port.InvalidListener),
    (port.ListenerFixture(), port.EntranceDrive(excitation_kind="PRESCRIBED_INCIDENT_PRESSURE"), port.UnsupportedListener),
    (port.ListenerFixture(), port.EntranceDrive(source_fixture_id=" "), port.InvalidListener),
    (port.ListenerFixture(), port.EntranceDrive(frequencies_hz=(3000,1000)), port.InvalidListener),
    (port.ListenerFixture(), port.EntranceDrive(frequencies_hz=(1000,1000)), port.InvalidListener),
    (port.ListenerFixture(), port.EntranceDrive(frequencies_hz=(-1,)), port.InvalidListener),
    (port.ListenerFixture(), port.EntranceDrive(frequencies_hz=(9000,)), port.UnsupportedListener),
    (port.ListenerFixture(), port.EntranceDrive(frequencies_hz=tuple(range(129))), port.InvalidListener),
    (port.ListenerFixture(), port.EntranceDrive(entrance_pressure_pa=complex(float("nan"),0)), port.InvalidListener),
])
def test_refusal_classes(fixture: object, drive: object, expected: type[Exception]) -> None:
    with pytest.raises(expected) as excinfo:
        port.evaluate(fixture,drive)
    assert excinfo.value.status == expected.status


def test_version_planes_digest_and_json_output_stable() -> None:
    a = port.evaluate(port.ListenerFixture(),port.EntranceDrive())
    b = port.evaluate(port.ListenerFixture(),port.EntranceDrive())
    assert a == b
    assert a["schema_version"] == port.MODEL_VERSION
    assert a["planes"] == [port.ENTRANCE,port.TERMINAL]
    assert a["phase_convention"] == "exp(+i*omega*t)"
    assert len(a["fixture_sha256"]) == 64
    assert len(a["frequencies"]) == 4
    assert json.loads(json.dumps(a,allow_nan=False)) == a
