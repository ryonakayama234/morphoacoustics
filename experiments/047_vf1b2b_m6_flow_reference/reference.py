"""VF-1B2b: independent, immutable M6 measured-flow import and toy transfer sentinel.

Research-only comparison; NOT a fluid solver validated against M6 geometry.
No import of VF-1B2a, moving wall, audio or Core graph production code.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
from pathlib import Path

TABLE = Path(__file__).with_name("m6_table2_experimental.csv")
TABLE_SHA256 = "febecab692b5eb78d2e73520d27556c368de5cff4691ff02c20baab64556b6d0"
DOI = "10.1121/1.3455838"
SHAPES = ("convergent_10", "uniform_0", "divergent_10")
PRESSURES_KPA = (0.294, 0.491, 0.981, 1.472)
FLOW_ACCURACY_CM3_S = 6.0  # paper's approximate measurement accuracy, not 1 sigma
A_MIN_M2 = 0.122 * 1e-4  # measured minimum projected area, not a toy geometry
RHO_KG_M3 = 1.21  # toy assumed air density, NOT a reported M6 measurement
CD_ASSUMED = 0.7  # frozen VF-1B2a hypothesis, NOT fitted to the table


def _real(v: object, name: str, positive: bool = False) -> float:
    if type(v) not in (str, int, float):
        raise ValueError(name + ": numeric type required")
    try:
        f = float(v)
    except (ValueError, OverflowError) as exc:
        raise ValueError(name + ": invalid number") from exc
    if not math.isfinite(f) or (positive and f <= 0):
        raise ValueError(name + ": must be finite" + (" and positive" if positive else ""))
    return f


def read_m6_table(content: bytes | None = None) -> tuple[dict, ...]:
    """The source bytes must match the checked 2010 Table 2 transcription exactly."""
    raw = TABLE.read_bytes() if content is None else content
    if hashlib.sha256(raw).hexdigest() != TABLE_SHA256:
        raise ValueError("M6 reference fixture integrity: SHA256 mismatch")
    try:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8", errors="strict"))))
    except UnicodeError as exc:
        raise ValueError("M6 reference fixture: encoding") from exc
    columns = ["pressure_kpa", *SHAPES]
    if len(rows) != 4 or not rows or list(rows[0]) != columns:
        raise ValueError("M6 reference fixture: unexpected rows/header")
    out = []
    for i, row in enumerate(rows):
        if list(row) != columns or row["pressure_kpa"] != str(PRESSURES_KPA[i]):
            raise ValueError("M6 reference fixture: pressure or columns")
        dp = _real(row["pressure_kpa"], "delta_p_kpa", positive=True) * 1000.0
        q = {s: _real(row[s], s, positive=True) * 1e-6 for s in SHAPES}
        if min(q.values()) <= FLOW_ACCURACY_CM3_S * 1e-6:
            raise ValueError("M6 flow too small for fixed absolute accuracy interval")
        out.append({"delta_p_pa": dp, "q_measured_m3_s": q})
    return tuple(out)


def toy_flow(delta_p_pa: float, shape: str, cd: float = CD_ASSUMED) -> float:
    """Independent statement of VF-1B2a heuristic, not imported from the Draft.

    The area ramp is an *illustrative* surrogate only: 1D endpoint ratios
    (A,A), (2A,A), (A,2A), unrelated to M6 sinusoidal 3D geometry.
    """
    dp = _real(delta_p_pa, "delta_p_pa")
    c = _real(cd, "cd", positive=True)
    if dp < 0 or c > 1:
        raise ValueError("unsupported pressure drive or discharge factor")
    if shape not in SHAPES:
        raise ValueError("unsupported shape")
    a_sep = (1.2 if shape == "divergent_10" else 1.0) * A_MIN_M2
    return c * a_sep * math.sqrt(2.0 * dp / RHO_KG_M3)


def accuracy_interval_ratio(q_a: float, q_b: float) -> tuple[float, float]:
    """Worst-case interval, not Gaussian statistics or uncertainty propagation."""
    a = _real(q_a, "q_a", positive=True)
    b = _real(q_b, "q_b", positive=True)
    e = FLOW_ACCURACY_CM3_S * 1e-6
    if min(a, b) <= e:
        raise ValueError("uncertainty interval includes nonpositive flow")
    return ((a - e) / (b + e), (a + e) / (b - e))


def compare() -> dict:
    """A shape-ratio transfer mismatch is NOT model validation with mismatched M6."""
    entries = read_m6_table()
    cases: list[dict] = []
    mismatches = {s: 0 for s in SHAPES}
    for item in entries:
        dp = item["delta_p_pa"]
        q = item["q_measured_m3_s"]
        baseline = q["uniform_0"]
        for shape in SHAPES:
            measured = q[shape]
            lower, upper = accuracy_interval_ratio(measured, baseline)
            predicted = toy_flow(dp, shape)
            predicted_uniform = toy_flow(dp, "uniform_0")
            ratio = predicted / predicted_uniform
            outside = ratio < lower or ratio > upper
            if outside:
                mismatches[shape] += 1
            cases.append({
                "delta_p_pa": dp,
                "shape": shape,
                "q_measured_m3_s": measured,
                "measurement_accuracy_abs_m3_s": FLOW_ACCURACY_CM3_S * 1e-6,
                "q_toy_m3_s": predicted,
                "q_toy_minus_measured_m3_s": predicted - measured,
                "absolute_comparison_qualified": False,
                "measured_flow_ratio_to_uniform": measured / baseline,
                "ratio_min_from_accuracy": lower,
                "ratio_max_from_accuracy": upper,
                "toy_flow_ratio_to_uniform": ratio,
                "toy_outside_m6_accuracy_interval": outside,
            })
    return {
        "source": {"doi": DOI, "table": "Table 2, experimental Q only",
                   "real_life_equivalent": True, "accuracy_is_one_sigma": False,
                   "input_table_sha256": TABLE_SHA256},
        "assumptions": {"rho_kg_m3": RHO_KG_M3, "assumed_cd": CD_ASSUMED,
                        "min_projected_area_m2": A_MIN_M2,
                        "toy_endpoint_area_ramps": {
                            "convergent_10": [2 * A_MIN_M2, A_MIN_M2],
                            "uniform_0": [A_MIN_M2, A_MIN_M2],
                            "divergent_10": [A_MIN_M2, 2 * A_MIN_M2]},
                        "geometry_match": False,
                        "pressure_tap_data_available": False,
                        "mismatch_reasons": [
                            "M6 sinusoidal three-dimensional transverse shape vs 1D linear ramp",
                            "published M6 flow table does not specify toy separation criterion",
                            "different entrance/recovery/boundary geometry",
                            "no numeric mapped wall-tap pressure profile with uncertainty",
                        ]},
        "cases": cases,
        "mismatch_counts_out_of_four": mismatches,
        "transfer_sentinel": ("M6_SHAPE_TRANSFER_DISCREPANCY"
                              if mismatches["divergent_10"] >= 2
                              else "NO_M6_DIVERGENT_DISCREPANCY_DETECTED"),
        "g2": "INDETERMINATE_NO_MATCHED_PRESSURE_TAP_PROFILE_OR_GEOMETRY",
        "g3": "NOT_APPLICABLE_NO_MOVING_WALL",
        "g4": "VOICE_NO_GO",
    }


def audit_comparison(result: dict) -> bool:
    """Independent-output guard on controls and frozen input assumptions.

    This does not independently verify the empirical article or an FSI law.
    """
    if result.get("assumptions", {}).get("geometry_match") is not False:
        return False
    if result["assumptions"].get("pressure_tap_data_available") is not False:
        return False
    if result.get("source", {}).get("input_table_sha256") != TABLE_SHA256:
        return False
    src = result.get("source", {})
    if (src.get("doi") != DOI or src.get("table") != "Table 2, experimental Q only"
            or src.get("real_life_equivalent") is not True
            or src.get("accuracy_is_one_sigma") is not False):
        return False
    assum = result["assumptions"]
    expected_ramps = {
        "convergent_10": [2 * A_MIN_M2, A_MIN_M2],
        "uniform_0": [A_MIN_M2, A_MIN_M2],
        "divergent_10": [A_MIN_M2, 2 * A_MIN_M2],
    }
    if (assum.get("assumed_cd") != CD_ASSUMED
            or assum.get("min_projected_area_m2") != A_MIN_M2
            or assum.get("rho_kg_m3") != RHO_KG_M3
            or assum.get("toy_endpoint_area_ramps") != expected_ramps):
        return False
    rows = result.get("cases", [])
    if len(rows) != 12:
        return False
    observed_mismatches = {s: 0 for s in SHAPES}
    known = read_m6_table()
    for i, case in enumerate(rows):
        reference = known[i // 3]
        shape = SHAPES[i % 3]
        dp = reference["delta_p_pa"]
        measured = reference["q_measured_m3_s"][shape]
        unif = reference["q_measured_m3_s"]["uniform_0"]
        lo, hi = accuracy_interval_ratio(measured, unif)
        expected_ratio = 1.2 if shape == "divergent_10" else 1.0
        checks = (
            case.get("delta_p_pa") == dp, case.get("shape") == shape,
            abs(case.get("q_measured_m3_s", float("inf")) - measured) < 1e-15,
            abs(case.get("measurement_accuracy_abs_m3_s", float("inf"))
                - FLOW_ACCURACY_CM3_S * 1e-6) < 1e-15,
            abs(case.get("measured_flow_ratio_to_uniform", float("inf"))
                - measured / unif) < 1e-12,
            abs(case.get("q_toy_minus_measured_m3_s", float("inf"))
                - (toy_flow(dp, shape) - measured)) < 1e-15,
            abs(case.get("ratio_min_from_accuracy", float("inf")) - lo) < 1e-12,
            abs(case.get("ratio_max_from_accuracy", float("inf")) - hi) < 1e-12,
            abs(case.get("toy_flow_ratio_to_uniform", float("inf")) - expected_ratio) < 1e-12,
            abs(case.get("q_toy_m3_s", float("inf")) - toy_flow(dp, shape)) < 1e-15,
            case.get("absolute_comparison_qualified") is False,
            case.get("toy_outside_m6_accuracy_interval") is (expected_ratio < lo or expected_ratio > hi),
        )
        if not all(checks):
            return False
        observed_mismatches[shape] += int(expected_ratio < lo or expected_ratio > hi)
    return (
        result.get("mismatch_counts_out_of_four") == observed_mismatches
        and result.get("transfer_sentinel") == (
            "M6_SHAPE_TRANSFER_DISCREPANCY"
            if observed_mismatches["divergent_10"] >= 2
            else "NO_M6_DIVERGENT_DISCREPANCY_DETECTED")
        and result.get("g2") == "INDETERMINATE_NO_MATCHED_PRESSURE_TAP_PROFILE_OR_GEOMETRY"
        and result.get("g3") == "NOT_APPLICABLE_NO_MOVING_WALL"
        and result.get("g4") == "VOICE_NO_GO"
    )
