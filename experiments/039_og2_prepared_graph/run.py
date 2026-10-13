"""Experiment 039 reproducible runner and audit evidence, without a public API."""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
import os
import platform
import re
import subprocess
from pathlib import Path
import sys

import numpy as np

from morphoacoustics.acoustics import UniformTube


HERE = Path(__file__).resolve().parent
ORACLE_PATH = HERE / "wolfram" / "og2_oracle.json"
WL_PATH = HERE / "wolfram" / "og2_oracle.wl"
PROTOCOL_PATH = HERE / "PREREGISTRATION.md"
SOURCE_PATH = HERE / "og2.py"
REPO_ROOT = HERE.parents[1]
EVIDENCE_SCHEMA = "og2.evidence.v2"

spec = importlib.util.spec_from_file_location("og2_exp039_runner", SOURCE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load OG-2 research module")
og2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = og2
spec.loader.exec_module(og2)


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def as_complex_matrix(oracle: dict[str, object]) -> np.ndarray:
    pairs = np.asarray(oracle["normalized_matrix_rowmajor_re_im"], dtype=float)
    return (pairs[..., 0] + 1j * pairs[..., 1]).reshape(-1, 2, 2)


def complex_pairs(matrix: np.ndarray) -> list[object]:
    return np.stack((matrix.real, matrix.imag), axis=-1).tolist()


def checkout_attestation(expected_head_sha: str | None = None) -> dict[str, object]:
    """Never accept a caller-supplied SHA as proof of the checked-out source."""
    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True,
            text=True, check=True,
        )
        return result.stdout.strip()

    head_sha = git("rev-parse", "HEAD")
    if re.fullmatch(r"[0-9a-f]{40}", head_sha) is None:
        raise RuntimeError("INVALID_GIT_HEAD_SHA")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("DIRTY_TRACKED_CHECKOUT")
    if expected_head_sha is not None and expected_head_sha != head_sha:
        raise RuntimeError(f"HEAD_SHA_MISMATCH expected={expected_head_sha} actual={head_sha}")
    return {
        "head_sha": head_sha,
        "tracked_checkout_clean": True,
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "github_job": os.getenv("GITHUB_JOB"),
        "github_event_name": os.getenv("GITHUB_EVENT_NAME"),
    }


def run(output_dir: Path, *, expected_head_sha: str | None = None) -> dict[str, object]:
    attestation = checkout_attestation(expected_head_sha)
    # Stale evidence must never look like a fresh scientific rerun.
    output_dir.mkdir(parents=True, exist_ok=False)

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    assert oracle["baseline_main_sha"] == og2.ADOPTED_BASELINE_SHA
    frequency = np.asarray(oracle["frequencies_hz"], dtype=float)
    expected = as_complex_matrix(oracle)
    prepared = og2.prepare(og2.fixture())
    actual = prepared.scaled_transfer_matrix(frequency)
    matrix_delta = np.abs(actual - expected)
    worst_mismatch = float(np.max(matrix_delta))

    equal = og2.prepare(og2.fixture(area_b=0.0003))
    z = equal.reference_impedance
    d = np.diag([1.0, z])
    di = np.diag([1.0, 1.0 / z])
    equivalent_single = UniformTube(length_m=0.17, area_m2=0.0003)
    control = d @ equivalent_single.transfer_matrix(frequency) @ di
    worst_equal = float(np.max(np.abs(equal.scaled_transfer_matrix(frequency) - control)))

    a, b = prepared.tubes_in_path_order
    wrong_coupling = np.diag([1.0, a.area_m2 / b.area_m2])
    z = prepared.reference_impedance
    d = np.diag([1.0, z])
    di = np.diag([1.0, 1.0 / z])
    wrong = d @ (
        a.transfer_matrix(frequency)
        @ wrong_coupling
        @ b.transfer_matrix(frequency)
    ) @ di
    wrong_error = float(np.max(np.abs(wrong - expected)))
    swapped = d @ (
        b.transfer_matrix(frequency) @ a.transfer_matrix(frequency)
    ) @ di
    swapped_error = float(np.max(np.abs(swapped - expected)))

    reflected, transmitted, reflected_power, transmitted_power = prepared.interface_scattering()
    power_error = float(max(
        abs(reflected - oracle["isolated_interface"]["pressure_reflection"]),
        abs(transmitted - oracle["isolated_interface"]["pressure_transmission"]),
        abs(reflected_power - oracle["isolated_interface"]["power_reflection"]),
        abs(transmitted_power - oracle["isolated_interface"]["power_transmission"]),
        abs(reflected_power + transmitted_power - 1.0),
    ))
    intervened = og2.prepare(og2.fixture(area_b=0.0005))
    revised = og2.prepare(og2.fixture(revision_b="r2"))
    replay = og2.prepare(og2.fixture())
    branch = og2.branch_fixture()
    og2.validate(branch)
    branch_status = "unexpected-success"
    try:
        og2.prepare(branch)
    except og2.GraphError as exc:
        branch_status = exc.status

    invalid_status = "unexpected-success"
    try:
        og2.prepare(og2.fixture(area_b=float("nan")))
    except og2.GraphError as exc:
        invalid_status = exc.status

    tests = {
        "equal_area_full_complex_matrix": worst_equal <= 1e-10,
        "mismatch_full_complex_wolfram_oracle": worst_mismatch <= 1e-10,
        "matched_interface_power": power_error <= 1e-12,
        "wrong_velocity_continuity_killed": 1e-3 < wrong_error < 10.0,
        "wrong_reverse_order_killed": 1e-3 < swapped_error < 10.0,
        "valid_branch_is_unsupported": branch_status == "UNSUPPORTED",
        "invalid_geometry_is_invalid": invalid_status == "INVALID",
        "identical_blueprint_digest": prepared.preparation_digest == replay.preparation_digest,
        "B_area_intervention_digest": prepared.preparation_digest != intervened.preparation_digest,
        "B_revision_intervention_digest": prepared.preparation_digest != revised.preparation_digest,
        "A_unchanged_by_B_intervention": (
            prepared.organs_in_path_order[0] == intervened.organs_in_path_order[0]
        ),
    }
    decision = (
        "PROVISIONAL_NUMERICAL_PASS_REVIEW_PENDING_NOT_ADOPTED"
        if all(tests.values())
        else "GATE_FAILED_NOT_ADOPTED"
    )
    records = {
        "evidence_schema": EVIDENCE_SCHEMA,
        "checkout_attestation": attestation,
        "decision": decision,
        "claim_scope": "two fixed rigid lossless passive serial 1D organs only",
        "parent_issue": "https://github.com/ryonakayama234/morphoacoustics/issues/96",
        "base_adopted_main_sha": og2.ADOPTED_BASELINE_SHA,
        "source_hashes_sha256": {
            "protocol": file_sha(PROTOCOL_PATH),
            "og2_python": file_sha(SOURCE_PATH),
            "wolfram_source": file_sha(WL_PATH),
            "wolfram_reference_json": file_sha(ORACLE_PATH),
        },
        "toolchain": {"python": platform.python_version(), "numpy": np.__version__},
        "backend": prepared.backend_id,
        "preparation_digest": prepared.preparation_digest,
        "organ_mapping": [
            {
                "id": node.id,
                "revision": node.revision,
                "inlet": node.inlet.id,
                "outlet": node.outlet.id,
                "length_m": node.length_m,
                "area_m2": node.area_m2,
            }
            for node in prepared.organs_in_path_order
        ],
        "junction": {"id": prepared.junction.id, "law": prepared.junction.law,
                     "ports": list(prepared.junction.ports)},
        "diagnostics": {"branch": branch_status, "nonfinite_area": invalid_status},
        "metrics": {
            "max_equal_area_scaled_matrix_error": worst_equal,
            "max_mismatch_wolfram_scaled_matrix_error": worst_mismatch,
            "max_isolated_interface_power_error": power_error,
            "wrong_particle_velocity_scaled_matrix_error": wrong_error,
            "wrong_order_scaled_matrix_error": swapped_error,
            "pressure_reflection": reflected,
            "pressure_transmission": transmitted,
            "reflected_power": reflected_power,
            "transmitted_power": transmitted_power,
        },
        "tests": tests,
        "observations": [
            {
                "frequency_hz": float(f),
                "scaled_complex_T_rowmajor_re_im": complex_pairs(actual[i]).__getitem__(0)
                    + complex_pairs(actual[i]).__getitem__(1),
                "max_wolfram_error": float(np.max(matrix_delta[i])),
            }
            for i, f in enumerate(frequency)
        ],
    }
    encoded = json.dumps(records, sort_keys=True, indent=2, allow_nan=False) + "\n"
    (output_dir / "decision.json").write_text(encoded, encoding="utf-8")
    (output_dir / "evidence_sha256.txt").write_text(
        sha256(encoded.encode("utf-8")).hexdigest() + "\n", encoding="utf-8"
    )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-head-sha", default=os.getenv("OG2_EXPECTED_HEAD_SHA"))
    args = parser.parse_args()
    record = run(args.output_dir, expected_head_sha=args.expected_head_sha)
    print(json.dumps({"decision": record["decision"], "metrics": record["metrics"],
                      "tests": record["tests"]}, indent=2))
    if record["decision"] != "PROVISIONAL_NUMERICAL_PASS_REVIEW_PENDING_NOT_ADOPTED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
