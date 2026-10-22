"""Bounded opt-in CLI ABI candidate over the CC-B1 Core physical research tool.

This command is NOT a public package, remote service, Studio Take, or
authenticated signature. Physical authority remains in the inherited Core
candidate performer; this outer layer only validates caller transport.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import runpy
import stat
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
VERSION = "cc-b1-core-limited-performer/v1"
REQUEST_MAX_BYTES = 4096
MANIFEST_MAX_BYTES = 65536


class StrictParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ValueError("CLI_ARGUMENT_INVALID")


def refusal(status: str, code: str, message: str) -> dict[str, object]:
    return {
        "schema_version": VERSION,
        "status": status,
        "error": {"code": code, "message": message},
        "artifacts": [],
    }


def unique_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError("NONFINITE_JSON_CONSTANT")


def assert_no_symlink_components(path: Path) -> None:
    """Conservative check only, NOT protection against concurrent path swaps."""
    for part in (path, *path.parents):
        if os.path.islink(part):
            raise ValueError("SYMLINK_PATH_UNSAFE")


def strict_json_file(path: Path, max_bytes: int) -> object:
    assert_no_symlink_components(path)
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("JSON_FILE_NOT_REGULAR")
    with path.open("rb") as handle:
        payload = handle.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise ValueError("JSON_FILE_TOO_LARGE")
    return json.loads(
        payload.decode("utf-8", errors="strict"),
        object_pairs_hook=unique_object_pairs,
        parse_constant=reject_constant,
    )


def candidate() -> dict[str, Any]:
    # Run only after caller transport has passed all strict validation.
    return runpy.run_path(str(ROOT / "tools/cc_b1_limited_performer.py"))


def assert_fixed_causal_metadata(manifest: dict[str, Any], backend: dict[str, Any]) -> None:
    """Bind claimed source/task/metadata to the actually installed fixed Core law.

    Not a signature or proof of the Git checkout's origin; the archive still
    requires a trusted local installation and controlled storage.
    """
    keys = {
        "schema_version", "status", "capability", "claim_limit", "parent",
        "edit_intent", "body_revision", "source", "task_plan_sha256",
        "baseline_quantized_sha256", "edited_quantized_sha256",
        "relative_raw_pa_l2", "acoustic_calls_per_body", "sample_rate_hz",
        "sample_count", "shared_playback_gain", "artifacts", "provenance",
        "limitations",
    }
    if set(manifest) != keys:
        raise ValueError("ARCHIVE_METADATA_MISMATCH: top-level fields")
    core = runpy.run_path(str(ROOT / "tools/cc_a2_live.py"))
    frozen = core["_load_frozen_adapter"]()
    exp = frozen._load_audited_experiment()
    source_list, _ = exp.EXP26.EXP13.build_sources()
    source = source_list[frozen.SOURCE_ID].source
    expected = {
        "schema_version": VERSION,
        "status": "SUCCEEDED",
        "capability": "site08-one-section-rest-area-0.90-or-1.10/v1",
        "claim_limit": "fixed LF and three-task, 16x10mm 1D computational physical model",
        "source": {"id": frozen.SOURCE_ID,
                   "sha256_le_f64": backend["source_sha"](source)},
        "task_plan_sha256": exp.sha256_json(exp.task_plan_payload()),
        "acoustic_calls_per_body": 102,
        "sample_rate_hz": 48000,
        "sample_count": 24000,
        "limitations": [
            "research candidate, not installed/published stable API",
            "no stable Studio Take yet", "no audible voice identity claim",
            "digest is integrity evidence, not cryptographic origin signature",
        ],
    }
    # JSON canonical serialization is type sensitive: True cannot spoof 1.
    def exact(value: object) -> str:
        return json.dumps(value, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"), allow_nan=False)
    for key, value in expected.items():
        if exact(manifest[key]) != exact(value):
            raise ValueError("ARCHIVE_METADATA_MISMATCH: " + key)
    provenance = manifest["provenance"]
    if type(provenance) is not dict or set(provenance) != {
        "core_checkout_sha", "gate_a_freeze_sha",
        "gate_b_limited_decision_sha", "numpy_version", "python_version",
    }:
        raise ValueError("ARCHIVE_METADATA_MISMATCH: provenance shape")
    for key, expected_sha in (
        ("gate_a_freeze_sha", backend["FROZEN_GATE_A_SHA"]),
        ("gate_b_limited_decision_sha", backend["ADOPTED_GATE_B_SHA"]),
    ):
        if provenance[key] != expected_sha:
            raise ValueError("ARCHIVE_METADATA_MISMATCH: " + key)
    reported_sha = provenance["core_checkout_sha"]
    if (type(reported_sha) is not str or len(reported_sha) != 40
        or any(char not in "0123456789abcdef" for char in reported_sha)):
        raise ValueError("ARCHIVE_METADATA_MISMATCH: checkout SHA shape")
    if (provenance["numpy_version"] != exp.AUDITED_NUMPY_VERSION
        or type(provenance["python_version"]) is not str
        or not provenance["python_version"]):
        raise ValueError("ARCHIVE_METADATA_MISMATCH: dependency provenance")
    expected_kinds = {
        "baseline_pa.npy": ("baseline-pressure", "application/x-npy"),
        "edited_pa.npy": ("edited-pressure", "application/x-npy"),
        "baseline.wav": ("baseline-audio", "audio/wav"),
        "edited.wav": ("edited-audio", "audio/wav"),
        "baseline_trace.csv": ("baseline-trace", "text/csv"),
        "edited_trace.csv": ("edited-trace", "text/csv"),
    }
    artifacts = manifest["artifacts"]
    if type(artifacts) is not list or len(artifacts) != 6:
        raise ValueError("ARCHIVE_METADATA_MISMATCH: artifacts")
    for item in artifacts:
        if (type(item) is not dict or set(item) != {
            "kind", "path", "media_type", "size_bytes", "sha256"
        } or item.get("path") not in expected_kinds
            or type(item["size_bytes"]) is not int):
            raise ValueError("ARCHIVE_METADATA_MISMATCH: artifact fields")
        if (item["kind"], item["media_type"]) != expected_kinds[item["path"]]:
            raise ValueError("ARCHIVE_METADATA_MISMATCH: artifact semantics")


def execute(argv: list[str] | None = None) -> dict[str, object]:
    parser = StrictParser(description="Opt-in limited CC-B1 Core research ABI")
    parser.add_argument("--protocol-version", required=True)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--inspect", action="store_true")
    operation.add_argument("--perform", action="store_true")
    operation.add_argument("--verify", action="store_true")
    parser.add_argument("--request", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--archive-dir", type=Path)
    try:
        args = parser.parse_args(argv)
    except (ValueError, argparse.ArgumentError):
        return refusal("INVALID", "CLI_ARGUMENT_INVALID", "Invalid operation or command arguments")
    if args.protocol_version != VERSION:
        return refusal("UNSUPPORTED", "SCHEMA_VERSION_UNSUPPORTED", "Unsupported protocol version")
    if args.inspect:
        if args.request is not None or args.output_dir is not None or args.archive_dir is not None:
            return refusal("INVALID", "CLI_ARGUMENT_INVALID", "Inspect does not accept paths")
        try:
            return candidate()["inspect_baseline"]()
        except Exception:
            return refusal("FAILED", "CORE_GATE_C_RUNTIME_FAILURE", "Inspection failed")
    if args.perform:
        if args.request is None or args.output_dir is None or args.archive_dir is not None:
            return refusal("INVALID", "CLI_ARGUMENT_INVALID", "Perform requires request and output directory")
        try:
            request = strict_json_file(args.request, REQUEST_MAX_BYTES)
        except (OSError, UnicodeError, ValueError, TypeError):
            return refusal("INVALID", "REQUEST_JSON_INVALID", "Unsafe or malformed request")
        try:
            assert_no_symlink_components(args.output_dir)
            if os.path.lexists(args.output_dir) or not args.output_dir.parent.is_dir():
                return refusal("INVALID", "OUTPUT_PATH_UNSAFE", "Destination must not exist and parent must exist")
        except (OSError, ValueError):
            return refusal("INVALID", "OUTPUT_PATH_UNSAFE", "Unsafe output path")
        try:
            return candidate()["perform"](request, args.output_dir)
        except Exception:
            return refusal("FAILED", "CORE_GATE_C_RUNTIME_FAILURE", "Core physical execution failed")
    if args.archive_dir is None or args.request is not None or args.output_dir is not None:
        return refusal("INVALID", "CLI_ARGUMENT_INVALID", "Verify requires archive directory")
    try:
        assert_no_symlink_components(args.archive_dir)
        if not stat.S_ISDIR(args.archive_dir.lstat().st_mode):
            raise ValueError("ARCHIVE_DIRECTORY_INVALID")
        # The inherited verifier does not currently use strict JSON parsing.
        # Defend the boundary here before its receipt replay and physical checks.
        manifest = strict_json_file(
            args.archive_dir / "result.json", MANIFEST_MAX_BYTES
        )
        if type(manifest) is not dict:
            raise ValueError("ARCHIVE_JSON_SHAPE_INVALID")
    except (OSError, UnicodeError, ValueError, TypeError):
        return refusal("INVALID", "ARCHIVE_JSON_INVALID", "Untrusted or incomplete archive manifest")
    try:
        backend = candidate()
        verified = backend["verify_output_archive"](args.archive_dir)
        assert_fixed_causal_metadata(verified, backend)
        return verified
    except Exception:
        return refusal("FAILED", "ARCHIVE_VERIFICATION_FAILED", "Core archive verification failed")


def main() -> None:
    result = execute()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    if result.get("status") != "SUCCEEDED" and "editable" not in result:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
