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
        if row["frequency_hz"] == 0:
            assert row["frequency_interpretation"] == "ZERO_FREQUENCY_LIMIT"
            assert entry["mean_active_power_w"] is None
            assert terminal["mean_active_power_w"] is None
            assert row["power_residual_w"] is None
            assert row["formal_phasor_power_limit_w"]["entrance"] == pytest.approx(
                row["formal_phasor_power_limit_w"]["terminal"], rel=1e-10)
        else:
            assert row["frequency_interpretation"] == "HARMONIC_AC"
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


# AUDIT A1 ADDENDUM TESTS (not part of frozen original Gate A).
FULL_ORACLE = json.loads((RESEARCH / "wolfram_oracle_36.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("row", FULL_ORACLE["rows"])
def test_audit_full_36_wolfram_wave_oracle(row: list[float]) -> None:
    length, ratio, freq, hr, hi, gr, gi, normalized_formal_power = row
    obs = port.evaluate(
        port.ListenerFixture(length_m=length, terminal_resistance_ratio_to_zc=ratio),
        port.EntranceDrive(frequencies_hz=(freq,)))
    entry = obs["frequencies"][0]
    assert abs(z(entry["transfer_pressure_terminal_per_entrance"])-complex(hr,hi)) <= 1e-11
    assert abs(z(entry["entrance_reflection_coefficient"])-complex(gr,gi)) <= 1e-11
    if freq == 0:
        assert entry["frequency_interpretation"] == "ZERO_FREQUENCY_LIMIT"
        assert entry["entrance"]["mean_active_power_w"] is None
        observed = entry["formal_phasor_power_limit_w"]["entrance"]
    else:
        assert entry["frequency_interpretation"] == "HARMONIC_AC"
        observed = entry["entrance"]["mean_active_power_w"]
    assert observed * entry["characteristic_impedance_pa_s_m3"] == pytest.approx(normalized_formal_power,abs=1e-11)


def test_audit_distinguish_total_vs_incident_pressure_boundaries() -> None:
    # Existing solver ONLY supports prescribed TOTAL p0; here an independent
    # incident-wave boundary is emulated by choosing p0=pi*(1+Gamma0) per L.
    # Equal external pressure fields are NOT claimed.
    f, ratio, p_inc = 3000.0, 2.0, 1+0j
    term_gamma = (ratio - 1)/(ratio + 1)
    incident_mags, total_mags = [], []
    for length in [0.02, 0.025, 0.03]:
        q = np.exp(-1j*2*pi*f*length/343.0)
        p_total = p_inc * (1+term_gamma*q*q)
        row_inc = port.evaluate(
            port.ListenerFixture(length_m=length,terminal_resistance_ratio_to_zc=ratio),
            port.EntranceDrive(frequencies_hz=(f,),entrance_pressure_pa=p_total)
        )["frequencies"][0]
        p_terminal = z(row_inc["terminal"]["pressure_pa"])
        assert p_terminal == pytest.approx(p_inc*q*(1+term_gamma),abs=1e-11)
        incident_mags.append(abs(p_terminal))
        row_total = port.evaluate(
            port.ListenerFixture(length_m=length,terminal_resistance_ratio_to_zc=ratio),
            port.EntranceDrive(frequencies_hz=(f,))
        )["frequencies"][0]
        total_mags.append(abs(z(row_total["terminal"]["pressure_pa"])))
    assert max(incident_mags)-min(incident_mags) < 1e-11
    assert max(total_mags)-min(total_mags) > 0.3


def test_audit_normalized_load_area_null_and_flow_power_change() -> None:
    # Fix R=Zt/Zc, so changing A changes Zt too; H and Gamma invariant.
    rows = [port.evaluate(
        port.ListenerFixture(section_area_m2=area,terminal_resistance_ratio_to_zc=2),
        port.EntranceDrive(frequencies_hz=(3000,))
    )["frequencies"][0] for area in [3e-5,6e-5]]
    a,b=rows
    assert z(a["transfer_pressure_terminal_per_entrance"]) == pytest.approx(
        z(b["transfer_pressure_terminal_per_entrance"]),abs=1e-11)
    assert z(a["entrance_reflection_coefficient"]) == pytest.approx(
        z(b["entrance_reflection_coefficient"]),abs=1e-11)
    assert z(b["terminal"]["volume_velocity_m3_s"]) == pytest.approx(
        2*z(a["terminal"]["volume_velocity_m3_s"]),rel=1e-11)
    assert b["entrance"]["mean_active_power_w"] == pytest.approx(
        2*a["entrance"]["mean_active_power_w"],rel=1e-11)


@pytest.mark.parametrize("field,value",[
    ("length_m",10**1000), ("area_m2",10**1000), ("sound_speed_m_s",10**1000),
    ("air_density_kg_m3",10**1000), ("terminal_resistance_ratio_to_zc",10**1000)
])
def test_audit_huge_integer_parameters_are_invalid(field: str,value: int) -> None:
    fixture=port.ListenerFixture(**{field:value})
    with pytest.raises(port.InvalidListener):
        port.evaluate(fixture,port.EntranceDrive())


@pytest.mark.parametrize("drive",[
    port.EntranceDrive(frequencies_hz=(10**1000,)),
    port.EntranceDrive(entrance_pressure_pa=10**1000),
])
def test_audit_huge_integer_drives_are_invalid(drive: object) -> None:
    with pytest.raises(port.InvalidListener):
        port.evaluate(port.ListenerFixture(),drive)


def test_audit_linear_small_signal_limit() -> None:
    medium_bulk_modulus = 1.21*343.0**2
    ok=port.evaluate(port.ListenerFixture(),port.EntranceDrive(
        frequencies_hz=(3000,),entrance_pressure_pa=0.0005*medium_bulk_modulus))
    assert ok["linear_pressure_perturbation_ratio"] == pytest.approx(0.0005)
    assert ok["linear_pressure_perturbation_limit"] == 1e-3
    with pytest.raises(port.UnsupportedListener):
        port.evaluate(port.ListenerFixture(),port.EntranceDrive(
            frequencies_hz=(3000,),entrance_pressure_pa=0.002*medium_bulk_modulus))


def test_audit_dc_is_not_measured_work_rate() -> None:
    ac, dc = port.evaluate(port.ListenerFixture(),port.EntranceDrive(
        frequencies_hz=(0,1000)))["frequencies"]
    assert dc["frequency_interpretation"] == "HARMONIC_AC"
    assert dc["entrance"]["mean_active_power_w"] is not None
    assert ac["frequency_interpretation"] == "ZERO_FREQUENCY_LIMIT"
    assert ac["entrance"]["mean_active_power_w"] is None
    assert ac["formal_phasor_power_limit_w"]["entrance"] > 0
    assert ac["terminal"]["mean_active_power_w"] is None
