"""EL-NF2 evidence-only audit (does not prove underlying measured acoustics)."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


def check(e: dict) -> dict:
    if e.get("schema_version") != "el-nf2-evidence-v1" or e.get("adoption") != "NOT_ADOPTED":
        raise ValueError("INVALID: research-only evidence identity")
    if e.get("preregistration_commit") != "9915d101cdbba273b7c69813098d4e14a364abb7":
        raise ValueError("INVALID: preregistration identity")
    groups = e.get("split_direction_ids")
    if sorted(groups) != ["final", "training", "validation"]:
        raise ValueError("INVALID: missing split direction groups")
    train, val, final = (groups[x] for x in ("training", "validation", "final"))
    if len(set(train + val + final)) != len(train + val + final) or not train or not val or not final:
        raise ValueError("INVALID: duplicate direction or empty split")
    if len(train + val + final) != 49:
        raise ValueError("INVALID: expected exactly 49 unique directions")
    if e.get("g4_blind_listening") != "PENDING" or e.get("g5_independent_science_review") != "PENDING":
        raise ValueError("INVALID: evidence cannot self-approve independent gates")
    measurement = e.get("measurement", {})
    if measurement.get("md5") != "4ba9cc348801a6805265c7168b5b3227":
        raise ValueError("INVALID: not original measured SOFA")
    if not isinstance(measurement.get("sha256"), str) or len(measurement["sha256"]) != 64:
        raise ValueError("INVALID: missing measured dataset digest")
    recorded = e.get("split_measurement_indices", {})
    for split_name, dirs in groups.items():
        index_groups = recorded.get(split_name)
        if len(index_groups) != len(dirs) or any(len(row) != 4 for row in index_groups):
            raise ValueError("INVALID: split index shape")
    all_indices = [idx for name in ("training", "validation", "final") for row in recorded[name] for idx in row]
    if len(set(all_indices)) != 196:
        raise ValueError("INVALID: leaked or duplicated measurement index")
    records = e.get("records")
    if not isinstance(records, list) or len(records) != 3 * 4 * (len(final) + len(val)):
        raise ValueError("INVALID: incomplete model×position evidence")
    seen = set()
    for row in records:
        k = (row.get("split"), row.get("direction"), row.get("stage"), row.get("radius_m"), row.get("model"))
        if k in seen:
            raise ValueError("INVALID: duplicate record")
        seen.add(k)
        split_name, direction, stage, radius, model = k
        if split_name not in ("validation", "final") or direction not in groups[split_name]:
            raise ValueError("INVALID: wrong split")
        if stage not in ("S1", "S2") or model not in ("B0", "B1", "C1"):
            raise ValueError("INVALID: unknown stage/model")
        if (stage == "S1" and radius not in (0.2, 0.5)) or (stage == "S2" and radius not in (0.3, 0.4)):
            raise ValueError("INVALID: wrong holdout radius")
        if row.get("train_direction_ids") != train:
            raise ValueError("INVALID: train direction leakage")
        indices = recorded[split_name][groups[split_name].index(direction)]
        if row["target_index"] not in indices:
            raise ValueError("INVALID: wrong heldout measurement index")
        if row["target_index"] in [idx for part in recorded["training"] for idx in part]:
            raise ValueError("INVALID: heldout measurement used as training")
        if row.get("supported"):
            if row.get("training_radius_indices") != ([0, 3] if stage == "S2" else [0 if radius == 0.2 else 3]):
                raise ValueError("INVALID: radial split mismatch")
            ild = row.get("abs_ild_errors_db")
            itd = row.get("abs_itd_error_us")
            shape = row.get("ear_shape_rmse_db")
            if not isinstance(ild, list) or len(ild) != 4 or not isinstance(shape, list) or len(shape) != 2:
                raise ValueError("INVALID: missing band/ear errors")
            if not all(isinstance(v, (int, float)) and math.isfinite(v) and v >= 0 for v in [*ild, itd, *shape]):
                raise ValueError("INVALID: negative or nonfinite errors")
        elif not str(row.get("refusal", "")).startswith("UNSUPPORTED:"):
            raise ValueError("INVALID: missing explicit unsupported reason")
    for name in ("validation", "final"):
        rows = [x for x in records if x["split"] == name]
        directions = sorted({row["direction"] for row in rows if row["supported"]})
        verdict = e[name]
        if len(directions) < 8:
            if verdict.get("verdict") != "INDETERMINATE" or verdict.get("supported_directions") != len(directions):
                raise ValueError("INVALID: insufficient support must be inconclusive")
            continue
        def metric(m: str, stage: str | None = None, field: str = "abs_ild_errors_db") -> float:
            vals = [v for row in rows if row["supported"] and row["model"] == m and (stage is None or stage == row["stage"])
                    for v in (row[field] if isinstance(row[field], list) else [row[field]])]
            return float(np.median(vals))
        stats = {}
        for m in ("B0", "B1", "C1"):
            stats[m] = {
                "median_ild_error_db": metric(m), "S1_median_ild_error_db": metric(m, "S1"),
                "S2_median_ild_error_db": metric(m, "S2"),
                "median_abs_itd_error_us": metric(m, field="abs_itd_error_us"),
                "p95_ild_error_db": float(np.percentile([
                    v for row in rows if row["model"] == m and row["supported"] for v in row["abs_ild_errors_db"]], 95)),
                "median_ear_shape_rmse_db": metric(m, field="ear_shape_rmse_db"),
            }
            for key, value in stats[m].items():
                if not math.isclose(value, verdict["statistics"][m][key], rel_tol=0, abs_tol=1e-9):
                    raise ValueError("INVALID: forged summary: " + m + "/" + key)
        matrix = {m: np.asarray([[v for row in rows if row["supported"] and row["direction"] == d and row["model"] == m
                                 for v in row["abs_ild_errors_db"]] for d in directions]) for m in ("B1", "C1")}
        rng = np.random.default_rng(20261030)
        diffs = []
        for _ in range(2000):
            indices = rng.integers(0, len(directions), size=len(directions))
            diffs.append(float(np.median(matrix["B1"][indices]) - np.median(matrix["C1"][indices])))
        ci = np.percentile(diffs, [2.5, 97.5])
        if not np.allclose(ci, verdict.get("ild_improvement_ci95_db"), rtol=0, atol=1e-9):
            raise ValueError("INVALID: forged bootstrap interval")
        b, c = stats["B1"], stats["C1"]
        pass_gate = (
            c["median_ild_error_db"] <= 0.8 * b["median_ild_error_db"] and ci[0] > 0
            and c["S1_median_ild_error_db"] < b["S1_median_ild_error_db"]
            and c["S2_median_ild_error_db"] < b["S2_median_ild_error_db"]
            and c["median_abs_itd_error_us"] <= b["median_abs_itd_error_us"] + 25
        )
        expected = "GO_LIMITED_NUMERICAL_CANDIDATE" if pass_gate else "REVISE_OR_REJECT"
        if verdict.get("verdict") != expected:
            raise ValueError("INVALID: forged gate decision")
        if verdict.get("supported_directions") != len(directions):
            raise ValueError("INVALID: forged directional coverage")
    return {"audit": "INDEPENDENT_EVIDENCE_ARITHMETIC_ONLY", "final_verdict": e["final"]["verdict"],
            "record_count": len(records), "training_direction_count": len(train), "final_direction_count": len(final)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True, type=Path)
    args = ap.parse_args()
    def refuse_constant(x: str):
        raise ValueError("INVALID: nonfinite JSON token " + x)
    e = json.loads(args.evidence.read_text(encoding="utf-8"), parse_constant=refuse_constant)
    print(json.dumps(check(e), sort_keys=True, allow_nan=False))
