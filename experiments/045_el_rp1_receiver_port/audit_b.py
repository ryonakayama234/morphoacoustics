"""Audit frozen original JS-wave E2 oracle against Core-matrix outputs.

Exact Git blob, complete 15-column row, physics metadata and 16-condition
matrix are checked BEFORE zip/comparison (cf. historical PR #275 audit flaw).
"""
from __future__ import annotations
import hashlib
import json
from math import isfinite
from pathlib import Path

ORACLE = Path(__file__).with_name("b0_wave_oracle_16.json")
BLOB_SHA = "81286d0a2b7ea26cf33ce65d0eb98be6df47b607"
D0_SHA = "a33c8c68879f732cd830b2caab6b8024b5322297"
FIELDS = [
    "area_m2","length_m","frequency_hz","p0_real_pa","p0_imag_pa",
    "u0_real_m3_s","u0_imag_m3_s","pL_real_pa","pL_imag_pa",
    "uL_real_m3_s","uL_imag_m3_s","power_source_w","power_entrance_w",
    "power_terminal_w","power_source_resistor_loss_w",
]


class OracleError(ValueError):
    pass


def _strict_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise OracleError("duplicate JSON key " + key)
        out[key] = value
    return out


def validate_oracle(obj):
    if type(obj) is not dict or set(obj) != {
        "schema","scientific_scope","preregistration_sha","method","fixed","fields","rows",
    }:
        raise OracleError("oracle object fields changed")
    if obj["schema"] != "el-rp1.b0.traveling-wave-oracle.v1":
        raise OracleError("oracle schema changed")
    if obj["preregistration_sha"] != D0_SHA or obj["scientific_scope"] != "IDEAL_SYNTHETIC_1D_ONLY":
        raise OracleError("prereg or human claim changed")
    if obj["method"] != "independent_complex_travelling_waves_ecmascript_not_core_matrix":
        raise OracleError("oracle method changed")
    expected_fixed = {
        "source_pressure_pa":1, "source_impedance_pa_s_m3":13834333.333333334,
        "terminal_impedance_pa_s_m3":27668666.666666668,
        "air_density_kg_m3":1.21,"sound_speed_m_s":343,
        "phasor":"peak_exp_plus_iwt","positive_u":"entrance_to_terminal",
    }
    if obj["fixed"] != expected_fixed or type(obj["fixed"]) is not dict:
        raise OracleError("fixed source/load/media metadata changed")
    if obj["fields"] != FIELDS or type(obj["fields"]) is not list:
        raise OracleError("column schema or order changed")
    rows = obj["rows"]
    if type(rows) is not list or len(rows) != 16:
        raise OracleError("must retain exactly 16 rows")
    expected = {(a,l,f) for a in (4e-5,8e-5) for l in (.025,.035)
                for f in (750,2200,5100,7900)}
    actual = set()
    for idx, row in enumerate(rows):
        if type(row) is not list or len(row) != len(FIELDS):
            raise OracleError(f"row {idx}: truncated or extended column count")
        if any(type(x) not in (int,float) or not isfinite(x) for x in row):
            raise OracleError(f"row {idx}: malformed or nonfinite numeric field")
        key = tuple(row[:3])
        if key in actual:
            raise OracleError(f"row {idx}: duplicate fixture")
        actual.add(key)
    if actual != expected:
        raise OracleError("fixture grid changed, missing or extra trial")
    return rows


def load_oracle(path=ORACLE):
    raw = Path(path).read_bytes()
    prefix = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    actual_sha = hashlib.sha1(prefix+raw).hexdigest()
    if actual_sha != BLOB_SHA:
        raise OracleError(f"frozen Git blob mismatch {actual_sha} != {BLOB_SHA}")
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_object)
    validate_oracle(obj)
    return obj


def compare_row(row, obs):
    if type(row) is not list or len(row) != len(FIELDS):
        raise OracleError("refuse incomplete comparison row")
    zc = obs.zc_pa_s_m3
    fields = (
        obs.p0_pa.real, obs.p0_pa.imag,
        obs.u0_m3_s.real, obs.u0_m3_s.imag,
        obs.pL_pa.real, obs.pL_pa.imag,
        obs.uL_m3_s.real, obs.uL_m3_s.imag,
        obs.power_source_w, obs.power_entrance_w,
        obs.power_terminal_w, obs.power_source_resistor_loss_w,
    )
    if len(fields) != len(FIELDS)-3:
        raise OracleError("audit field count inconsistency")
    errors = []
    for index, (observed, reference) in enumerate(zip(fields,row[3:],strict=True)):
        if not (isfinite(observed) and isfinite(reference)):
            raise OracleError("nonfinite comparison")
        err = abs(observed-reference)
        if index in (2,3,6,7):   # volume flow scaled to comparable pressure dimension
            err *= zc
        if index < 8:
            tolerance = 1e-11
        else:
            scale = max(1e-12, abs(reference), abs(observed))
            tolerance = max(1e-13, 1e-10*scale)
        if err > tolerance:
            raise OracleError(f"field {FIELDS[index+3]} disagrees: {err} > {tolerance}")
        errors.append(err)
    return {
        "max_pressure_error_pa": max(errors[i] for i in (0,1,4,5)),
        "max_zc_scaled_flow_error_pa": max(errors[i] for i in (2,3,6,7)),
        "max_power_error_w": max(errors[i] for i in (8,9,10,11)),
    }


def compare_regenerated_bytes(raw: bytes):
    """Cross-runtime JS regeneration: strictly same 16x15 structure AND E2 tolerances.

    The original B0 Git blob is byte-exact; external JavaScript engine/libm
    roundoff is compared numerically, not silently treated as a new oracle.
    """
    if not isinstance(raw, bytes):
        raise OracleError("regenerated reference must be original bytes")
    recreated = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_object)
    validate_oracle(recreated)
    original = load_oracle()
    for key in ("schema","scientific_scope","preregistration_sha","method","fixed","fields"):
        if recreated[key] != original[key]:
            raise OracleError(f"regenerated metadata changed: {key}")
    max_press = max_flow = max_power = 0.
    for idx, (ref, other) in enumerate(zip(original["rows"],recreated["rows"],strict=True)):
        if ref[:3] != other[:3]:
            raise OracleError(f"row {idx}: order or input fixture changed")
        zc = original["fixed"]["air_density_kg_m3"] * original["fixed"]["sound_speed_m_s"] / ref[0]
        for j in range(3,len(FIELDS)):
            err = abs(ref[j]-other[j])
            if j in (3,4,7,8):
                max_press = max(max_press,err)
                tol = 1e-11
            elif j in (5,6,9,10):
                err *= zc
                max_flow = max(max_flow,err)
                tol = 1e-11
            else:
                max_power = max(max_power,err)
                tol = max(1e-13, 1e-10*max(abs(ref[j]),abs(other[j]),1e-12))
            if err > tol:
                raise OracleError(f"row {idx} column {FIELDS[j]} differs: {err} > {tol}")
    return {
        "max_pressure_error_pa":max_press,
        "max_scaled_flow_error_pa":max_flow,
        "max_power_error_w":max_power,
        "comparison":"cross_js_runtime_numeric_not_byte_exact",
    }
