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


def _unresolved_receipt(test_outcome: str) -> dict:
    """Build archival evidence BEFORE any operation that might fail."""
    return {
        "schema": "vq1_g1s_synthetic_receipt_v0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "code_head_sha": os.environ.get("VQ1_G1S_EXPECTED_HEAD_SHA", "UNVERIFIED_LOCAL"),
        "tests_outcome": test_outcome,
        "synthetic_algebra_status": "NUMERICALLY_UNRESOLVED",
        "synthetic_force_example": None,
        "analytic_control_error": None,
        "measured_M5_reference": "G1_S_SOURCE_HOLD_NO_QUALIFIED_SPATIAL_MEASUREMENTS",
        "wet_surface_geometry": "UNQUALIFIED",
        "tracheal_to_exterior_reference": "UNQUALIFIED",
        "G1_S_physical_force": "INDETERMINATE",
        "G1_D_dynamic_wall_work": "HOLD",
        "G4_creator_voice": "NO_GO",
        "performance_contract_changes": False,
        "studio_panel_changes": False,
    }


def build_receipt():
    test_outcome = os.environ.get("VQ1_G1S_TEST_OUTCOME", "not_executed")
    receipt = _unresolved_receipt(test_outcome)
    # A broken analytic control must not prevent archival of a STOP receipt.
    try:
        analytic = static_force(
            [PressureDrop(6, "FW", 25, 2, "synthetic_control")],
            [SurfacePatch(6, "FW", .1, 1)],
            PressureReference(100, 0, 3, 5),
        )
        receipt["synthetic_force_example"] = asdict(analytic)
        if test_outcome == "success":
            receipt["synthetic_algebra_status"] = "PASS_LIMITED_SYNTHETIC_ONLY"
    except Exception as exc:
        receipt["analytic_control_error"] = type(exc).__name__ + ": " + str(exc)
    try:
        static_force(
            [],
            [SurfacePatch(6, "FW", .1, 1)],
            PressureReference(100, 0, 3, 5),
        )
        receipt["measured_M5_reference"] = "ERR_UNSAFE_UNEXPECTED_SUCCESS"
        receipt["synthetic_algebra_status"] = "NUMERICALLY_UNRESOLVED"
    except ScientificHold:
        pass  # Expected: no real M5 pressure has been supplied or qualified.
    except Exception as exc:
        receipt["measured_M5_reference"] = "SOURCE_REFUSAL_UNRESOLVED"
        receipt["source_refusal_error"] = type(exc).__name__ + ": " + str(exc)
        receipt["synthetic_algebra_status"] = "NUMERICALLY_UNRESOLVED"
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        receipt = build_receipt()
    except Exception as exc:
        receipt = _unresolved_receipt(os.environ.get("VQ1_G1S_TEST_OUTCOME", "not_executed"))
        receipt["runner_error"] = type(exc).__name__ + ": " + str(exc)
    Path(args.out).write_text(
        json.dumps(receipt, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if (receipt["synthetic_algebra_status"] == "NUMERICALLY_UNRESOLVED"
            or receipt["measured_M5_reference"] != "G1_S_SOURCE_HOLD_NO_QUALIFIED_SPATIAL_MEASUREMENTS"):
        raise SystemExit("Unresolved synthetic control or unsafe scientific source; receipt archived")


if __name__ == "__main__":
    main()
