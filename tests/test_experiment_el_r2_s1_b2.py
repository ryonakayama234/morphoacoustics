"""EL-R2-S1 B2: 24 prospective synthetic challenges, independent of the Core matrix.

D1 frozen the *inputs* before the ECMAScript traveling-wave reference was generated.
This is not human-ear data, a blinded validation, or a Studio/ASMR runtime feature.
"""
from __future__ import annotations

from dataclasses import replace
from math import cos, isfinite, sin
from pathlib import Path
import hashlib
import json
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments" / "044_el_r2_s1_source_load"
sys.path.insert(0, str(STUDY))
from listener_port import Fixture, PortObservation, solve

ORACLE_PATH = STUDY / "holdout_oracle_24.json"
ORACLE_GIT_BLOB_SHA1 = "0c3476899de4d3cdeaad46816895b8318b43cde0"
COLUMNS = (
    "area_m2", "length_m", "frequency_hz", "pL_real_pa", "pL_imag_pa",
    "p0_real_pa", "p0_imag_pa", "uL_real_m3_s", "uL_imag_m3_s",
    "u0_real_m3_s", "u0_imag_m3_s", "Psource_w", "Pentrance_w",
    "Pterminal_w", "Ploss_w",
)


def load_b2(path: Path = ORACLE_PATH) -> dict:
    raw = path.read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if sha != ORACLE_GIT_BLOB_SHA1:
        raise ValueError("B2 prospective numerical reference was modified")
    reference = json.loads(raw)
    if reference.get("schema") != "el-r2-s1.b2.scattering24.v1":
        raise ValueError("B2 reference schema mismatch")
    if tuple(reference.get("columns", ())) != COLUMNS:
        raise ValueError("B2 reference column identity mismatch")
    if (reference.get("phasor") != "peak_exp_plus_iwt"
        or reference.get("direction") != "+U entrance_to_terminal"
        or reference.get("reference_planes") != [
            "SOURCE_EQUIVALENT", "CANAL_ENTRANCE", "TERMINAL_SIDE"]):
        raise ValueError("Reference-plane or time convention changed")
    if (reference.get("rho_kg_m3") != 1.21 or reference.get("c_m_s") != 343
        or reference.get("source_pressure") != [1, 0]
        or reference.get("source_impedance_pa_s_m3") != 13834333.333333334
        or reference.get("terminal_impedance_pa_s_m3") != 27668666.666666668):
        raise ValueError("Fixed absolute drive/load conditions changed")
    expected = [
        (area, length, frequency)
        for area in (4e-5, 8e-5)
        for length in (.015, .035, .045)
        for frequency in (750, 2200, 5100, 7900)
    ]
    rows = reference.get("rows")
    if not isinstance(rows, list) or len(rows) != 24:
        raise ValueError("Expected precisely 24 ordered rows")
    if any(not isinstance(row, list) or len(row) != len(COLUMNS)
           or any(isinstance(x, bool) or not isinstance(x, (float, int))
                  or not isfinite(x) for x in row) for row in rows):
        raise ValueError("Nonfinite or malformed reference")
    if [tuple(row[:3]) for row in rows] != expected:
        raise ValueError("B2 condition identity/order mismatch")
    return reference


REFERENCE = load_b2()
ROWS = REFERENCE["rows"]


def fixture(row) -> Fixture:
    return Fixture(area_m2=row[0], length_m=row[1], frequency_hz=row[2],
                   source_pressure_pa=1+0j,
                   source_impedance_pa_s_m3=REFERENCE["source_impedance_pa_s_m3"],
                   terminal_impedance_pa_s_m3=REFERENCE["terminal_impedance_pa_s_m3"])


def finite(value: object) -> bool:
    try:
        c = complex(value)
        return isfinite(c.real) and isfinite(c.imag)
    except (TypeError, ValueError, OverflowError):
        return False


def audit_24(f: Fixture, o: PortObservation, ref: list[float]) -> tuple[str, ...]:
    """Evaluate raw ports against the separate frozen wave reference, fail-closed."""
    errors: list[str] = []
    raw = [o.p0_pa, o.pL_pa, o.u0_m3_s, o.uL_m3_s, o.zc_pa_s_m3,
           o.power_drive_w, o.power_entrance_w, o.power_terminal_w,
           o.power_source_loss_w, o.h_total, o.h_drive, o.h_canal]
    if not all(finite(v) for v in raw):
        return ("nonfinite_port_or_diagnostic",)
    if tuple(ref[:3]) != (f.area_m2, f.length_m, f.frequency_hz):
        errors.append("fixture_identity")
    expected = [complex(ref[3], ref[4]), complex(ref[5], ref[6]),
                complex(ref[7], ref[8]), complex(ref[9], ref[10])]
    computed = [o.pL_pa, o.p0_pa, o.uL_m3_s, o.u0_m3_s]
    for tag, value, comparison in zip(("pL", "p0", "uL", "u0"), computed, expected):
        scale = 1.0 if tag.startswith("p") else o.zc_pa_s_m3
        if (abs((value.real-comparison.real)*scale) > 1e-11
            or abs((value.imag-comparison.imag)*scale) > 1e-11):
            errors.append(tag + "_independent_reference")
    power_values = (o.power_drive_w, o.power_entrance_w, o.power_terminal_w,
                    o.power_source_loss_w)
    for label, value, comparison in zip(("Psource", "Pentrance", "Pterminal", "Ploss"),
                                        power_values, ref[11:15]):
        tolerance = max(1e-13, 1e-10*max(abs(value), abs(comparison), 1e-12))
        if abs(value-comparison) > tolerance:
            errors.append(label + "_independent_reference")
    ps, zs, zt = f.source_pressure_pa, f.source_impedance_pa_s_m3, f.terminal_impedance_pa_s_m3
    if abs(ps-o.p0_pa-zs*o.u0_m3_s) > 1e-11:
        errors.append("source_boundary")
    if abs(o.pL_pa-zt*o.uL_m3_s) > 1e-11:
        errors.append("terminal_boundary")
    tolerance = max(1e-13, 1e-10*max(o.power_drive_w, o.power_terminal_w, 1e-12))
    recomputed = ((ps*o.u0_m3_s.conjugate()).real/2,
                  (o.p0_pa*o.u0_m3_s.conjugate()).real/2,
                  (o.pL_pa*o.uL_m3_s.conjugate()).real/2,
                  zs*abs(o.u0_m3_s)**2/2)
    if any(abs(a-b)>tolerance for a,b in zip(power_values,recomputed)):
        errors.append("power_recomputed")
    if abs(recomputed[0]-recomputed[1]-recomputed[3])>tolerance:
        errors.append("source_energy")
    if abs(recomputed[1]-recomputed[2])>tolerance:
        errors.append("tube_energy")
    if any(value < -1e-13 for value in power_values):
        errors.append("passivity")
    if abs(o.h_total-o.pL_pa/ps)>1e-11:
        errors.append("h_total_from_ports")
    if abs(o.h_drive-o.p0_pa/ps)>1e-11:
        errors.append("h_drive_from_ports")
    if abs(o.h_canal-o.pL_pa/o.p0_pa)>1e-11:
        errors.append("h_canal_from_ports")
    if abs(o.h_total-o.h_drive*o.h_canal)>1e-11:
        errors.append("transfer_factorization")
    if not (o.source_reference_plane=="SOURCE_EQUIVALENT"
            and o.entrance_plane=="CANAL_ENTRANCE"
            and o.terminal_plane=="TERMINAL_SIDE"
            and o.phasor=="peak_exp_plus_iwt"
            and o.positive_u=="entrance_to_terminal"):
        errors.append("reference_planes")
    return tuple(errors)


@pytest.mark.parametrize("row", ROWS, ids=lambda r:f"A{r[0]}-L{r[1]}-f{r[2]}")
def test_prospective_24_scattering_reference(row):
    f = fixture(row)
    assert audit_24(f, solve(f), row) == ()


def test_reference_byte_pin_and_prospective_grid():
    assert load_b2() == REFERENCE
    assert len({tuple(row[:3]) for row in ROWS}) == 24
    assert {row[0] for row in ROWS}.isdisjoint({3e-5, 6e-5})


@pytest.mark.parametrize("idx", [0, 11, 23])
@pytest.mark.parametrize("factor", [0.5+0j, 2+0j, complex(cos(.63), sin(.63))])
def test_complex_source_scaling_and_phase_equivariance(idx, factor):
    base_f = fixture(ROWS[idx])
    base, scaled = solve(base_f), solve(replace(base_f, source_pressure_pa=factor))
    for name in ("p0_pa", "pL_pa", "u0_m3_s", "uL_m3_s"):
        unit_scale = 1 if name.startswith("p") else base.zc_pa_s_m3
        assert abs((getattr(scaled,name) - factor*getattr(base,name))*unit_scale) < 1e-11
    for name in ("power_drive_w", "power_entrance_w", "power_terminal_w", "power_source_loss_w"):
        assert abs(getattr(scaled,name)-abs(factor)**2*getattr(base,name)) < 1e-13
    assert abs(scaled.gamma_in-base.gamma_in)<1e-12
    assert abs(scaled.zc_pa_s_m3-base.zc_pa_s_m3)<1e-12


def test_mutated_observation_and_reference_cannot_pass():
    row = ROWS[5]
    f = fixture(row)
    valid = solve(f)
    assert audit_24(f, valid, row) == ()
    altered = [
        replace(valid,pL_pa=valid.pL_pa+1e-4),
        replace(valid,uL_m3_s=valid.uL_m3_s+1e-6),
        replace(valid,power_source_loss_w=valid.power_source_loss_w+1e-8),
        replace(valid,h_total=0j,h_drive=0j,h_canal=0j),
        replace(valid,p0_pa=complex(float('nan'),0)),
        replace(valid,u0_m3_s=complex(float('inf'),0)),
        replace(valid,terminal_plane="FREE_FIELD"),
    ]
    for mutant in altered:
        assert audit_24(f, mutant, row), repr(mutant)
    mutant_row = list(row)
    mutant_row[3] += 1e-4
    assert "pL_independent_reference" in audit_24(f,valid,mutant_row)
    mutant_row = list(row)
    mutant_row[12] += 1e-8
    assert "Pentrance_independent_reference" in audit_24(f,valid,mutant_row)


def test_oracle_byte_edit_rejected(tmp_path):
    original = ORACLE_PATH.read_bytes()
    path = tmp_path / "changed.json"
    path.write_bytes(original.replace(b"750", b"751", 1))
    with pytest.raises(ValueError, match="modified"):
        load_b2(path)
