"""Gate-B audit: validate observations against the *frozen* Wolfram oracle.

No solver code is called here. All checks return explicit named failures.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import cos, isfinite, pi, sin
from pathlib import Path
import hashlib
import json

from listener_port import Fixture, PortObservation
from morphoacoustics.acoustics.uniform_tube import UniformTube

HERE = Path(__file__).resolve().parent
GATE_A_ORACLE_BLOB = "f89ccf20cb60019c4487873a13af678e983beb6b"
GATE_A_SOURCE_BLOB = "fa8c2112f36f2b7119d40e8125e4d979ba091eef"
COLUMNS = (
    "area_m2", "length_m", "frequency_hz", "terminal_pressure_real_pa",
    "terminal_pressure_imag_pa", "entrance_pressure_real_pa",
    "entrance_pressure_imag_pa", "source_mean_power_w",
    "terminal_mean_power_w", "source_resistor_dissipation_w",
)


def git_blob_digest(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_oracle(path: Path | None = None, *, verify_pin: bool = True) -> dict:
    """Load frozen data by explicit column identity, refusing substitution/reordering."""
    path = path or HERE / "wolfram_oracle_18.json"
    raw = path.read_bytes()
    if verify_pin and git_blob_digest(raw) != GATE_A_ORACLE_BLOB:
        raise ValueError("Frozen Wolfram oracle Git blob SHA mismatch")
    payload = json.loads(raw)
    if payload.get("schema") != "el-r2-s1.wolfram.scattering.v0":
        raise ValueError("Wrong Wolfram oracle schema")
    if tuple(payload.get("columns", ())) != COLUMNS:
        raise ValueError("Frozen column identity/order changed")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != 18 or any(not isinstance(r, list) or len(r) != 10 for r in rows):
        raise ValueError("Expected precisely 18 ten-column oracle rows")
    if len({(r[0], r[1], r[2]) for r in rows}) != 18:
        raise ValueError("Duplicate A/L/f fixture")
    expected = [(a, length, freq) for a in (3e-5, 6e-5) for length in (.02, .025, .03) for freq in (1000, 3000, 7000)]
    if [(r[0], r[1], r[2]) for r in rows] != expected:
        raise ValueError("Ordered frozen factorial identity mismatch")
    if any(any(isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(float(v)) for v in r) for r in rows):
        raise ValueError("Nonfinite/non-numeric oracle row")
    return payload


@dataclass(frozen=True, slots=True)
class AuditResult:
    verdict: str
    failures: tuple[str, ...]
    max_complex_pressure_error_pa: float
    max_power_error_w: float


def audit_row(f: Fixture, o: PortObservation, row: Sequence[float]) -> AuditResult:
    """Check one frozen reference row plus independent physical boundary invariants."""
    failures: list[str] = []
    if (f.area_m2, f.length_m, f.frequency_hz) != tuple(row[:3]):
        failures.append("fixture_identity")
    if o.input_status != "VALID":
        failures.append("invalid_observation_state")

    pL_ref = complex(row[3], row[4])
    p0_ref = complex(row[5], row[6])
    pressure_diffs = [abs(o.pL_pa.real-pL_ref.real), abs(o.pL_pa.imag-pL_ref.imag), abs(o.p0_pa.real-p0_ref.real), abs(o.p0_pa.imag-p0_ref.imag)]
    if not all(isfinite(v) and v <= 1e-11 for v in pressure_diffs):
        failures.append("frozen_complex_pressure_oracle")

    powers = [o.power_drive_w, o.power_terminal_w, o.power_source_loss_w]
    oracle_powers = row[7:10]
    power_diffs = [abs(a-b) for a,b in zip(powers,oracle_powers)]
    for value, ref, difference in zip(powers, oracle_powers, power_diffs):
        if not isfinite(difference) or difference > max(1e-13, 1e-10*max(abs(ref),abs(value),1e-12)):
            failures.append("frozen_mean_power_oracle")
            break

    scale = max(o.power_drive_w, o.power_terminal_w, 1e-12)
    power_tol = max(1e-13, 1e-10*scale)
    if not (abs(o.source_residual_w) <= power_tol and abs(o.power_drive_w-o.power_terminal_w-o.power_source_loss_w) <= power_tol):
        failures.append("source_energy_ledger")
    if abs(o.tube_residual_w) > power_tol:
        failures.append("tube_energy_ledger")
    if not all(isfinite(p) and p >= -1e-13 for p in [*powers, o.power_entrance_w]):
        failures.append("passivity")
    # Independently *recompute* invariants from the observed raw port fields.
    # Stored residuals alone are not audit evidence: a mutated port may retain
    # a stale zero residual, producing a false-positive PASS without these checks.
    source_actual = f.source_pressure_pa - o.p0_pa - f.source_impedance_pa_s_m3 * o.u0_m3_s
    terminal_actual = o.pL_pa - f.terminal_impedance_pa_s_m3 * o.uL_m3_s
    if abs(source_actual) > 1e-11 or abs(o.source_boundary_residual_pa-source_actual)>1e-11:
        failures.append("source_boundary_recomputed")
    if abs(terminal_actual) > 1e-11 or abs(o.termination_boundary_residual_pa-terminal_actual)>1e-11:
        failures.append("terminal_boundary_recomputed")
    source_power_actual=(f.source_pressure_pa*o.u0_m3_s.conjugate()).real/2
    entrance_power_actual=(o.p0_pa*o.u0_m3_s.conjugate()).real/2
    terminal_power_actual=(o.pL_pa*o.uL_m3_s.conjugate()).real/2
    source_loss_actual=f.source_impedance_pa_s_m3*abs(o.u0_m3_s)**2/2
    if any(abs(reported-recomputed)>power_tol for reported,recomputed in zip(
            (o.power_drive_w,o.power_entrance_w,o.power_terminal_w,o.power_source_loss_w),
            (source_power_actual,entrance_power_actual,terminal_power_actual,source_loss_actual))):
        failures.append("powers_recomputed_from_ports")
    tube=UniformTube(f.length_m, f.area_m2,
                     sound_speed_m_s=f.sound_speed_m_s,air_density_kg_m3=f.air_density_kg_m3)
    t=tube.transfer_matrix(f.frequency_hz)
    actual_p=o.p0_pa-(complex(t[0,0])*o.pL_pa+complex(t[0,1])*o.uL_m3_s)
    actual_u=o.u0_m3_s-(complex(t[1,0])*o.pL_pa+complex(t[1,1])*o.uL_m3_s)
    if (abs(actual_p)>1e-11 or abs(actual_u*o.zc_pa_s_m3)>1e-11 or
            abs(o.matrix_pressure_residual_pa-actual_p)>1e-11 or
            abs((o.matrix_flow_residual_m3_s-actual_u)*o.zc_pa_s_m3)>1e-11):
        failures.append("core_matrix_boundary_recomputed")
    if abs(o.source_boundary_residual_pa) > 1e-11:
        failures.append("source_boundary")
    if abs(o.termination_boundary_residual_pa) > 1e-11:
        failures.append("terminal_boundary")
    if abs(o.matrix_pressure_residual_pa) > 1e-11 or abs(o.matrix_flow_residual_m3_s*o.zc_pa_s_m3) > 1e-11:
        failures.append("core_matrix_boundary")
    if abs(o.matrix_determinant_residual) > 1e-11:
        failures.append("core_matrix_unimodular")
    if abs(o.dimensionless_denominator_residual) > 1e-11*max(1, abs(o.dimensionless_denominator)):
        failures.append("dimensionless_denominator")
    if not (o.h_total is not None and o.h_drive is not None and o.h_canal is not None):
        failures.append("unexpected_missing_transfers")
    elif max(abs((o.h_total-o.h_drive*o.h_canal).real), abs((o.h_total-o.h_drive*o.h_canal).imag)) > 1e-11:
        failures.append("H_B6_factorization")

    theta=2*pi*f.frequency_hz*f.length_m/f.sound_speed_m_s
    gamma_l=(f.terminal_impedance_pa_s_m3-o.zc_pa_s_m3)/(f.terminal_impedance_pa_s_m3+o.zc_pa_s_m3)
    gamma_expected=gamma_l*complex(cos(-2*theta),sin(-2*theta))
    if abs(o.gamma_in-gamma_expected) > 1e-11 or not abs(o.gamma_in) < 1:
        failures.append("reflection_reference_plane")
    if o.source_reference_plane!="SOURCE_EQUIVALENT" or o.entrance_plane!="CANAL_ENTRANCE" or o.terminal_plane!="TERMINAL_SIDE" or o.phasor!="peak_exp_plus_iwt" or o.positive_u!="entrance_to_terminal":
        failures.append("declared_port_conventions")
    return AuditResult("FAIL" if failures else "PASS", tuple(dict.fromkeys(failures)), max(pressure_diffs), max(power_diffs))


def verify_wolfram_source(path: Path | None = None) -> str:
    p=path or HERE/"wolfram_oracle_18.wl"
    sha=git_blob_digest(p.read_bytes())
    if sha != GATE_A_SOURCE_BLOB:
        raise ValueError("Frozen Wolfram source Git blob SHA mismatch")
    return sha