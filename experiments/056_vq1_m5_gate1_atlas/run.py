"""Emit machine-readable metrology status even for invalid inputs/RED tests."""
import argparse
import json
import os
from pathlib import Path
from atlas import audit_file


def default_receipt() -> dict:
    return {
        "source_metrology": "NUMERICALLY_UNRESOLVED",
        "source_qualified_samples": 0,
        "s2_reference": "HOLD", "s3_force": "HOLD",
        "g1_d": "HOLD", "voice": "NO_GO",
        "external_source_audit": "REQUIRED_NOT_PERFORMED",
        "case_id": "M5_UNIFORM_FIG2B_D002CM_DP10CMH2O",
        "code_head": os.environ.get("SOURCE_HEAD", os.environ.get("GITHUB_SHA", "UNKNOWN")),
        "test_outcome": os.environ.get("VQ1_M5_TEST_OUTCOME", "not_reported")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--figure", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = default_receipt()
    failure = False
    try:
        candidate = audit_file(args.input, args.figure)
        receipt.update(candidate)
    except Exception as exc:
        failure = True
        receipt["error"] = type(exc).__name__ + ": " + str(exc)
    if receipt["test_outcome"] != "success":
        failure = True
        receipt["test_gate"] = "RED_OR_UNREPORTED"
        # Crucially, never leave a successful candidate status on failed tests.
        receipt["source_metrology"] = "NUMERICALLY_UNRESOLVED"
        receipt["source_qualified_samples"] = 0
    try:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(receipt, ensure_ascii=False,
                                      sort_keys=True, indent=2)+"\n", encoding="utf-8")
    except Exception as exc:
        raise SystemExit("STOP: unable to preserve failure receipt: "+str(exc))
    if failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
