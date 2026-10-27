"""Published M5 scalar exit-pressure reference. NOT a measured p(tap) profile."""
from __future__ import annotations
import csv
import hashlib
import io
import json
import math
from pathlib import Path

SOURCE = Path(__file__).with_name("table1_table2_m5.csv")
SOURCE_GIT_BLOB_SHA = "026f91bb98380254d111bf8e84e24a23818eed6e"
# Fulcher, Scherer, Powell 2011, DOI 10.1121/1.3514424,
# Tables I (Q), II (experiment-derived k_ex), Eqs. (2)-(3).
RHO_KG_M3 = 1.21  # paper: 0.00121 g/cm^3
GLOTTAL_LENGTH_CM = 1.2
TRACT_AREA_CM2 = 2.4
PA_PER_CM_H2O = 98.0665  # conventional unit conversion, not uncertainty
HEADERS = ["d_cm", "pressure_cmH2O", "flow_cm3_s", "kex_experimental"]
EXPECTED_PRESSURES = {
    "0.005": (3, 5, 10, 15, 25),
    "0.0075": (3, 5, 10, 15, 25),
    "0.01": (3, 5, 10, 15, 25),
    "0.02": (3, 5, 10, 15, 25),
    "0.04": (3, 5, 10, 15),
    "0.08": (3, 5, 10, 15),
    "0.16": (3, 5, 10, 15),
    "0.32": (1, 3, 5),
}


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def read_source(raw: bytes | None = None) -> list[dict]:
    raw = SOURCE.read_bytes() if raw is None else raw
    if git_blob_sha(raw) != SOURCE_GIT_BLOB_SHA:
        raise ValueError("unreviewed change to published Table I/II transcription")
    return parse_rows(raw.decode("utf-8", errors="strict"))


def parse_rows(content: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(content, newline=""), strict=True)
    if reader.fieldnames != HEADERS:
        raise ValueError("wrong source field names/order")
    rows, keys = [], set()
    for row in reader:
        if None in row or any(v is None or not v.strip() for v in row.values()):
            raise ValueError("missing/extra field: blank publication cells must be omitted")
        d_literal = row["d_cm"]
        if d_literal not in EXPECTED_PRESSURES:
            raise ValueError("unknown diameter")
        try:
            pressure = int(row["pressure_cmH2O"])
            d = float(d_literal)
            q = float(row["flow_cm3_s"])
            k = float(row["kex_experimental"])
        except (ValueError, OverflowError) as exc:
            raise ValueError("unreadable source value") from exc
        if (pressure not in EXPECTED_PRESSURES[d_literal] or
                not all(math.isfinite(v) for v in (d, q, k)) or
                d <= 0 or pressure <= 0 or q <= 0):
            raise ValueError("invalid or absent paper condition")
        key = (d_literal, pressure)
        if key in keys:
            raise ValueError("duplicate diameter/pressure condition")
        keys.add(key)
        rows.append({"d_cm": d, "pressure_cmH2O": pressure,
                     "Q_cm3_s": q, "k_experimental": k})
    required = {(d, p) for d, pressures in EXPECTED_PRESSURES.items() for p in pressures}
    if keys != required or len(rows) != 35:
        raise ValueError("35-table-pair integrity failure")
    return rows


def kex_im(d_cm: float) -> float:
    """Paper Eq (3) Ishizaka-Matsudaira abrupt expansion; untuned."""
    ratio = GLOTTAL_LENGTH_CM * d_cm / TRACT_AREA_CM2
    if not math.isfinite(ratio) or not 0 < ratio < 1:
        raise ValueError("invalid glottal/tract area ratio")
    return 2 * ratio * (1 - ratio)


def reconstructed_p16_minus_p11_pa(row: dict) -> float:
    """Algebraically IMPLIED from published derived k_ex and Q; NOT raw pressure."""
    area_m2 = GLOTTAL_LENGTH_CM * row["d_cm"] * 1e-4
    flow_m3_s = row["Q_cm3_s"] * 1e-6
    return row["k_experimental"] * RHO_KG_M3 * (flow_m3_s / area_m2)**2 / 2


def evaluate(rows: list[dict]) -> dict:
    if len(rows) != 35:
        raise ValueError("incomplete table")
    by_case = {(r["d_cm"], r["pressure_cmH2O"]): r for r in rows}
    if len(by_case) != 35:
        raise ValueError("duplicate source condition")
    records = []
    for row in rows:
        pred = kex_im(row["d_cm"])
        obs = row["k_experimental"]
        records.append({
            "diameter_cm": row["d_cm"],
            "pressure_cmH2O": row["pressure_cmH2O"],
            "Delta_p_T_Pa": row["pressure_cmH2O"] * PA_PER_CM_H2O,
            "Q_m3_s": row["Q_cm3_s"] * 1e-6,
            "k_experiment_derived_published": obs,
            "k_IM_unfitted_abrupt_exit": pred,
            "k_IM_minus_published": pred - obs,
            "p16_minus_p11_Pa_ALGEBRAIC_NOT_MEASURED_TAP": reconstructed_p16_minus_p11_pa(row),
        })
    narrow = [by_case[(.005, p)]["k_experimental"] for p in (3, 5, 10, 15, 25)]
    target = [by_case[(.02, p)]["k_experimental"] for p in (3, 5, 10, 15, 25)]
    im_pressures = [kex_im(by_case[(.02, p)]["d_cm"]) for p in (3, 5, 10, 15, 25)]
    middle = by_case[(.16, 5)]["k_experimental"]
    hypotheses = {
        "H_SIGN": all(x < 0 for x in narrow) and all(x > 0 for x in target),
        "H_DRIVE": (all(a > b for a, b in zip(target, target[1:]))
                    and len(set(im_pressures)) == 1),
        "H_GEOMETRY": target[1] > middle and kex_im(.02) < kex_im(.16),
    }
    # This inversion is a units sanity check, never independent scientific validation.
    algebraic_error = max(abs(
        2 * (GLOTTAL_LENGTH_CM * r["d_cm"] * 1e-4)**2 *
        reconstructed_p16_minus_p11_pa(r) /
        (RHO_KG_M3 * (r["Q_cm3_s"] * 1e-6)**2)
        - r["k_experimental"]) for r in rows)
    if algebraic_error > 1e-12:
        raise ValueError("SI pressure-recovery algebra inconsistent")
    hypotheses["H_RECONSTRUCTION_ALGEBRA_ONLY"] = True
    errors = [abs(x["k_IM_minus_published"]) for x in records]
    negatives = sum(x["k_experimental"] < 0 for x in rows)
    return {
        "source": {"doi": "10.1121/1.3514424", "tables": "I (Q) + II (derived k_ex)",
                   "git_blob_sha": SOURCE_GIT_BLOB_SHA},
        "gate0": "PUBLISHED_SCALAR_TABLE_SOFTWARE_CHECKED_INDEPENDENT_SOURCE_REVIEW_PENDING",
        "case_count": 35, "blank_source_cells": 13,
        "negative_k_count": negatives, "positive_k_count": 35 - negatives,
        "hypotheses": hypotheses,
        "k_IM_d002": kex_im(.02), "k_IM_d016": kex_im(.16),
        "k_observed_d002_P5": target[1], "k_observed_d016_P5": middle,
        "im_MAE_all_35": sum(errors) / 35,
        "im_MAX_all_35": max(errors),
        "im_wrong_sign_cases_all_35": negatives,  # IM predicts positive at all 35 geometries
        "g2": "INDETERMINATE_NO_AUDITED_NUMERIC_TAP_PROFILE_OR_MATCHED_SOLVER",
        "g3": "HOLD_NO_MOVING_WALL_ENERGY_LAW",
        "g4": "VOICE_NO_GO",
        "rows": records,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(read_source()), indent=2, sort_keys=True, allow_nan=False))
