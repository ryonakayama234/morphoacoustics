"""Fail-closed VQ-1 G1-S research evidence: never a physiological/voice GO."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from static_force import (
    PressureDrop, SurfacePatch, PressureReference,
    ScientificHold, static_force,
)


def build_receipt():
    test_outcome = os.environ.get("VQ1_G1S_TEST_OUTCOME", "not_executed")
    tests_passed = test_outcome == "success"
    ref = PressureReference(100, 0, 3, 5)
    analytic = static_force(
        [PressureDrop(6, "FW", 25, 2, "synthetic_control")],
        [SurfacePatch(6, "FW", .1, 1)],
        ref,
    )
    try:
        static_force([], [SurfacePatch(6, "FW", .1, 1)], ref)
        missing_real_reference = "ERR_UNSAFE_UNEXPECTED_SUCCESS"
    except ScientificHold:
        missing_real_reference = "G1_S_SOURCE_HOLD_NO_QUALIFIED_SPATIAL_MEASUREMENTS"
    return {
        "schema": "vq1_g1s_synthetic_receipt_v0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "code_head_sha": os.environ.get("VQ1_G1S_EXPECTED_HEAD_SHA", "UNVERIFIED_LOCAL"),
        "tests_outcome": test_outcome,
        "synthetic_algebra_status": "PASS_LIMITED_SYNTHETIC_ONLY" if tests_passed else "NUMERICALLY_UNRESOLVED",
        "synthetic_force_example": asdict(analytic),
        "measured_M5_reference": missing_real_reference,
        "wet_surface_geometry": "UNQUALIFIED",
        "tracheal_to_exterior_reference": "UNQUALIFIED",
        "G1_S_physical_force": "INDETERMINATE",
        "G1_D_dynamic_wall_work": "HOLD",
        "G4_creator_voice": "NO_GO",
        "performance_contract_changes": False,
        "studio_panel_changes": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    receipt = build_receipt()
    Path(args.out).write_text(
        json.dumps(receipt, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if receipt["measured_M5_reference"].startswith("ERR_"):
        raise SystemExit("Unsafe source success reported")


if __name__ == "__main__":
    main()
