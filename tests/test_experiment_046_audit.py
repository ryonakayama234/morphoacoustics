"""EL-NF2 immutable research-evidence arithmetic and mutation tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

P = Path(__file__).resolve().parents[1] / "experiments" / "046_el_nf2_spatial"
spec = importlib.util.spec_from_file_location("nf2_audit", P / "audit.py")
assert spec and spec.loader
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def synthetic_evidence():
    final = list(range(10))
    validation = list(range(10, 20))
    training = list(range(20, 49))
    groups = {"final": final, "validation": validation, "training": training}
    indices = {k: [[4 * d + i for i in range(4)] for d in ids] for k, ids in groups.items()}
    records = []
    for split in ("validation", "final"):
        for d in groups[split]:
            for stage, radii in (("S1", (0.2, 0.5)), ("S2", (0.3, 0.4))):
                for radius in radii:
                    for model in ("B0", "B1", "C1"):
                        base = {"B0": 2.0, "B1": 1.0, "C1": 0.5}[model]
                        records.append({
                            "split": split, "direction": d, "stage": stage, "radius_m": radius,
                            "model": model, "supported": True,
                            "target_index": 4 * d + ((0.2, 0.3, 0.4, 0.5).index(radius)),
                            "train_direction_ids": training,
                            "training_radius_indices": [0, 3] if stage == "S2" else ([0] if radius == 0.2 else [3]),
                            "abs_ild_errors_db": [base] * 4, "abs_itd_error_us": base * 3,
                            "ear_shape_rmse_db": [base * 2] * 2,
                        })
    def summary(split):
        records1 = [r for r in records if r["split"] == split]
        stats = {
            m: {
                "median_ild_error_db": {"B0": 2.0, "B1": 1.0, "C1": 0.5}[m],
                "S1_median_ild_error_db": {"B0": 2.0, "B1": 1.0, "C1": 0.5}[m],
                "S2_median_ild_error_db": {"B0": 2.0, "B1": 1.0, "C1": 0.5}[m],
                "median_abs_itd_error_us": {"B0": 6.0, "B1": 3.0, "C1": 1.5}[m],
                "p95_ild_error_db": {"B0": 2.0, "B1": 1.0, "C1": 0.5}[m],
                "median_ear_shape_rmse_db": {"B0": 4.0, "B1": 2.0, "C1": 1.0}[m],
            } for m in ("B0", "B1", "C1")
        }
        return {
            "verdict": "GO_LIMITED_NUMERICAL_CANDIDATE",
            "statistics": stats, "ild_improvement_ci95_db": [0.5, 0.5],
            "supported_directions": 10, "total_direction_count": 10,
            "bootstrap_seed": 20261030, "bootstrap_draws": 2000,
        }
    return {
        "schema_version": "el-nf2-evidence-v1", "adoption": "NOT_ADOPTED",
        "preregistration_commit": "9915d101cdbba273b7c69813098d4e14a364abb7",
        "split_direction_ids": groups, "split_measurement_indices": indices,
        "records": records, "validation": summary("validation"), "final": summary("final"),
        "measurement": {"md5": "4ba9cc348801a6805265c7168b5b3227", "sha256": "a" * 64},
        "g4_blind_listening": "PENDING", "g5_independent_science_review": "PENDING",
    }


def test_correct_synthetic_evidence_audits():
    assert audit.check(synthetic_evidence())["final_verdict"] == "GO_LIMITED_NUMERICAL_CANDIDATE"


def test_cannot_forge_adoption():
    e = synthetic_evidence()
    e["adoption"] = "ADOPTED"
    with pytest.raises(ValueError, match="research-only"):
        audit.check(e)


def test_cannot_forge_summary():
    e = synthetic_evidence()
    e["final"]["statistics"]["C1"]["median_ild_error_db"] = 0.0
    with pytest.raises(ValueError, match="forged summary"):
        audit.check(e)


def test_cannot_leak_final_direction():
    e = synthetic_evidence()
    e["split_direction_ids"]["training"][0] = e["split_direction_ids"]["final"][0]
    with pytest.raises(ValueError, match="duplicate direction"):
        audit.check(e)


def test_cannot_forge_bootstrap():
    e = synthetic_evidence()
    e["final"]["ild_improvement_ci95_db"] = [100, 100]
    with pytest.raises(ValueError, match="forged bootstrap"):
        audit.check(e)


def test_cannot_forge_verdict():
    e = synthetic_evidence()
    e["final"]["verdict"] = "REVISE_OR_REJECT"
    with pytest.raises(ValueError, match="forged gate"):
        audit.check(e)


def test_cannot_forge_itd_or_nonfinite():
    e = synthetic_evidence()
    e["final"]["statistics"]["C1"]["median_abs_itd_error_us"] = 999
    with pytest.raises(ValueError, match="forged summary"):
        audit.check(e)
    e = synthetic_evidence()
    e["records"][0]["abs_ild_errors_db"][0] = float("nan")
    with pytest.raises(ValueError, match="nonfinite"):
        audit.check(e)


def test_cannot_forge_final_reviewer():
    e = synthetic_evidence()
    e["g5_independent_science_review"] = "PASS"
    with pytest.raises(ValueError, match="self-approve"):
        audit.check(e)
