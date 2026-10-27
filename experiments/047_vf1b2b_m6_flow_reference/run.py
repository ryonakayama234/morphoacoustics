"""Emit auditable, fail-closed VF-1B2b measured-flow comparison CSV and receipt."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from reference import compare, audit_comparison, TABLE_SHA256

TRACKED = (
    "experiments/047_vf1b2b_m6_flow_reference/m6_table2_experimental.csv",
    "experiments/047_vf1b2b_m6_flow_reference/reference.py",
    "experiments/047_vf1b2b_m6_flow_reference/test_reference.py",
    "experiments/047_vf1b2b_m6_flow_reference/run.py",
    ".github/workflows/vf1b2b-m6-measured-flow.yml",
    "docs/research/vf1b2b/SYSTEM.md",
    "docs/research/vf1b2b/DATA.md",
    "docs/research/vf1b2b/EXPERIMENT.md",
)
CSV_FIELDS = (
    "delta_p_pa", "shape", "q_measured_m3_s",
    "measurement_accuracy_abs_m3_s", "q_toy_m3_s",
    "q_toy_minus_measured_m3_s", "absolute_comparison_qualified",
    "measured_flow_ratio_to_uniform", "ratio_min_from_accuracy",
    "ratio_max_from_accuracy", "toy_flow_ratio_to_uniform",
    "toy_outside_m6_accuracy_interval",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*argv: str) -> str:
    return subprocess.run(["git", *argv], cwd=ROOT, check=True,
                          text=True, capture_output=True, timeout=12).stdout.strip()


def suite_status(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {"eligible": False, "reason": "MISSING_UNITTTEST_RECEIPT"}
    blob = path.read_bytes()
    try:
        record = json.loads(blob)
        ok = (type(record) is dict
              and record.get("schema") == "vf1b2b.unittest.v1"
              and record.get("passed") is True
              and type(record.get("exit_code")) is int
              and record["exit_code"] == 0)
    except (ValueError, UnicodeError):
        ok = False
    return {"eligible": ok,
            "reason": "UNITTEST_PASS" if ok else "UNITTEST_FAIL_OR_INVALID",
            "test_receipt_sha256": hashlib.sha256(blob).hexdigest()}


def run(out: Path, suite: Path | None) -> dict:
    result = compare()
    audit = audit_comparison(result)
    head = git("rev-parse", "HEAD")
    pinned = os.environ.get("VF1B2B_EXPECTED_SHA", "")
    prov = {
        "commit_sha": head,
        "tree_sha": git("rev-parse", "HEAD^{tree}"),
        "expected_core_main_parent": "e05e3274ad69bfb9202816049f6661a18ba39ec0",
        "tracked_clean": not bool(git("status", "--porcelain=v1", "--untracked-files=no")),
        "github_sha_matches": not pinned or pinned == head,
        "source_sha256": {path: sha(ROOT / path) for path in TRACKED},
    }
    suite_rec = suite_status(suite)
    out.mkdir(parents=True, exist_ok=True)
    cases_path = out / "m6_measured_vs_toy_flow.csv"
    with cases_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(result["cases"])
    success = (audit and suite_rec["eligible"] and prov["tracked_clean"]
               and prov["github_sha_matches"]
               and prov["source_sha256"][TRACKED[0]] == TABLE_SHA256)
    result.update({
        "schema": "vf1b2b.m6-measured-flow-transfer.v1",
        "provenance": prov,
        "test_receipt": suite_rec,
        "audit_output_controls": audit,
        "comparison_csv_sha256": sha(cases_path),
        "g0": ("PASS_REFERENCED_12_MEASUREMENTS" if success
               else "NUMERICALLY_UNRESOLVED"),
        "g1": ("PASS_TOY_MATH_AUDIT_NOT_BIOPHYSICS" if success
               else "NUMERICALLY_UNRESOLVED"),
        "verdict": ("EXPERIMENT_ONLY_M6_TRANSFER_SENTINEL_NO_PHYSICAL_G2"
                    if success else "NUMERICALLY_UNRESOLVED"),
        "next_step_hold": {
            "vf1b2c_moving_wall_fsi": "HOLD",
            "missing": [
                "mapped numeric wall pressure taps with published or defensible uncertainty",
                "matched geometry/entrance/recovery and independently validated flow closure",
                "audited non-double-counted moving-wall conjugate power law",
                "independent exact-head qualified source/physics review",
            ],
        },
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--test-status-file", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = run(args.output_dir, args.test_status_file)
    except Exception as exc:
        result = {
            "schema": "vf1b2b.m6-measured-flow-transfer.v1",
            "verdict": "NUMERICALLY_UNRESOLVED",
            "failure": {"type": type(exc).__name__, "message": str(exc)},
            "g0": "NUMERICALLY_UNRESOLVED",
            "g1": "NUMERICALLY_UNRESOLVED",
            "g2": "INDETERMINATE_NO_MATCHED_PRESSURE_TAP_PROFILE_OR_GEOMETRY",
            "g3": "NOT_APPLICABLE_NO_MOVING_WALL",
            "g4": "VOICE_NO_GO",
        }
    path = args.output_dir / "vf1b2b_receipt.json"
    path.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)
                    + "\n", encoding="utf-8")
    print("VF1B2B_VERDICT", result["verdict"])
    if "cases" in result:
        for shape, value in result["mismatch_counts_out_of_four"].items():
            print("VF1B2B_RATIO_OUTSIDE", shape, value, "/4")
        print("VF1B2B_GATES", result["g0"], result["g1"], result["g2"])
    if result["verdict"] != "EXPERIMENT_ONLY_M6_TRANSFER_SENTINEL_NO_PHYSICAL_G2":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
