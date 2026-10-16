#!/usr/bin/env python3
"""OG-5 B3 fail-closed scientific scorer. Independent Wolfram data, actual public candidate Core API.

Never imports the Wolfram solver or oracle into the physical Core. Does not decide Gate C.
Uses all 144 rows and both full-port reference paths; negative mutants touch ONLY Core.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import replace
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from morphoacoustics_graph import tree5 as physical  # noqa: E402
from morphoacoustics_graph.tree5 import Tree5Error, prepare_tree5  # noqa: E402

P_REF, U_REF = 1.372, 1e-6
FREQS = (80, 250, 400, 733, 997, 1200, 2000, 4000)
AREAS = (.00015, .0003, .0006)
LOADS = ("matched", "rigid_closed")
SCALES = (1., .5, -1.)
PORTS = tuple(f"{name}.{side}" for name in "ABCDE" for side in ("in", "out"))
GOLDENS = ROOT / "docs/research/og5-contract-goldens.json"
ORACLE_FILES = tuple(ROOT / f"docs/research/og5-b3-oracle-{i:02}.json" for i in range(8))
LIMIT = 1e-10
MUTANT_LIMIT = 1e-6


def _fail(message: str) -> None:
    raise AssertionError(message)


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _complex(value: Any, label: str) -> complex:
    if isinstance(value, dict) and set(value) == {"real", "imag"}:
        real, imag = value["real"], value["imag"]
    elif isinstance(value, list) and len(value) == 2:
        real, imag = value
    else:
        _fail(f"{label}: malformed complex")
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in (real, imag)):
        _fail(f"{label}: nonfinite/non-numeric complex")
    return complex(real, imag)


def _states(payload: Any, label: str, encoded_as_core: bool) -> tuple[list[complex], list[complex]]:
    if not isinstance(payload, dict):
        _fail(f"{label}: missing state container")
    result = []
    for name in ("pressure_pa", "volume_flow_m3_s"):
        arr = payload.get(name)
        if not isinstance(arr, list) or len(arr) != 10:
            _fail(f"{label}/{name}: expected 10 endpoints")
        result.append([_complex(v, f"{label}/{name}/{i}") for i, v in enumerate(arr)])
    return result[0], result[1]


def _distance(got: tuple[list[complex], list[complex]],
              ref: tuple[list[complex], list[complex]]) -> float:
    return max(max(abs(a - b) / scale for a, b in zip(g, r))
               for g, r, scale in zip(got, ref, (P_REF, U_REF)))


def _case_key(x: dict[str, Any]) -> tuple[int, float, str, float]:
    return x["frequency_hz"], x["c_area_m2"], x["c_load"], x["scale"]


def load_oracle() -> tuple[list[dict[str, Any]], dict[str, str]]:
    result: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    for i, path in enumerate(ORACLE_FILES):
        raw = path.read_bytes()
        hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
        shard = json.loads(raw)
        if (set(shard) != {"schema", "kernel", "start_index", "cases"}
                or shard["schema"] != "og5.b3.oracle.v1"
                or not str(shard["kernel"]).startswith("15.0.1 for Linux")
                or shard["start_index"] != 18 * i
                or not isinstance(shard["cases"], list)
                or len(shard["cases"]) != 18):
            _fail(f"{path}: corrupted or misindexed Wolfram shard")
        result.extend(shard["cases"])
    expected = [(f, a, l, s) for f in FREQS for a in AREAS for l in LOADS for s in SCALES]
    keys = [_case_key(x) for x in result]
    if keys != expected or len(set(keys)) != 144:
        _fail(f"oracle incomplete/duplicate/out of order: {len(keys)} cases")
    for i, case in enumerate(result):
        if set(case) != {"frequency_hz", "c_area_m2", "c_load", "scale",
                         "global", "recursive", "oracle_max_scaled_difference",
                         "recursive_relative_power_defect",
                         "recursive_max_scaled_pressure_residual",
                         "recursive_max_scaled_flow_residual"}:
            _fail(f"oracle case {i}: unexpected/missing field")
        global_state = _states(case["global"], f"oracle global {i}", False)
        recursive = _states(case["recursive"], f"oracle recursive {i}", False)
        if _distance(global_state, recursive) > LIMIT:
            _fail(f"Wolfram two-algorithm discrepancy at case {i}")
        if (abs(_distance(global_state, recursive) - case["oracle_max_scaled_difference"]) > 1e-13
                or any(not math.isfinite(case[key]) or case[key] > LIMIT for key in (
                    "recursive_relative_power_defect",
                    "recursive_max_scaled_pressure_residual",
                    "recursive_max_scaled_flow_residual"))):
            _fail(f"Wolfram stored diagnostic mismatch at case {i}")
    return result, hashes


def blueprint(case: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    bp = copy.deepcopy(base)
    organ = next(o for o in bp["organs"] if o["id"] == "C")
    organ["area_m2"] = case["c_area_m2"]
    load = next(x for x in bp["loads"] if x["port"] == "C.out")
    load["kind"] = case["c_load"]
    bp["source"]["scale"] = case["scale"]
    return bp


def score_case(i: int, case: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    bp = blueprint(case, base)
    receiver = prepare_tree5(bp)  # Real B2 public candidate, including validation and immutable binding
    response = receiver.response([case["frequency_hz"]])
    if (response.get("status") != "SUCCESS"
            or response.get("port_ids") != list(PORTS)
            or response.get("frequencies_hz") != [float(case["frequency_hz"])]
            or len(response.get("pressure_pa", [])) != 1
            or len(response.get("volume_flow_m3_s", [])) != 1
            or len(response.get("mean_power_w", [])) != 1
            or len(response.get("diagnostics", [])) != 1):
        _fail(f"case {i}: malformed/truncated response")
    actual = _states({"pressure_pa": response["pressure_pa"][0],
                      "volume_flow_m3_s": response["volume_flow_m3_s"][0]},
                     f"Core response {i}", True)
    errors = {}
    for path in ("global", "recursive"):
        reference = _states(case[path], f"oracle {path}/{i}", False)
        err = _distance(actual, reference)
        if not math.isfinite(err) or err > LIMIT:
            _fail(f"case {i}: {path} full 20-complex-state mismatch: {err}")
        errors[path] = err
    d = response["diagnostics"][0]
    required = ("condition_number_2", "scaled_linear_residual",
                "j1_scaled_pressure_residual", "j2_scaled_pressure_residual",
                "j1_scaled_flow_residual", "j2_scaled_flow_residual",
                "relative_power_defect")
    if set(d) != set(required) or any(
        type(d[k]) not in (int, float) or not math.isfinite(d[k]) or d[k] < 0
        for k in required):
        _fail(f"case {i}: invalid diagnostics")
    if (d["condition_number_2"] > 1e4
            or d["scaled_linear_residual"] > 1e-12
            or any(d[k] > LIMIT for k in required[2:])):
        _fail(f"case {i}: failed solver/junction/power diagnostic")
    powers = response["mean_power_w"][0]
    if len(powers) != 10 or any(type(v) not in (int, float) or not math.isfinite(v) for v in powers):
        _fail(f"case {i}: invalid mean powers")
    floor = .5 * P_REF * U_REF * abs(case["scale"])**2
    for j, watt in enumerate(powers):
        independent_watt = .5 * (actual[0][j] * actual[1][j].conjugate()).real
        if abs(independent_watt - watt) > 1e-10 * max(abs(independent_watt), floor):
            _fail(f"case {i}: wrong power formula / port {j}")
    defect = abs(powers[0] - powers[5] - powers[7] - powers[9]) / max(abs(powers[0]), floor)
    if (powers[0] <= 0 or defect > LIMIT
            or powers[7] < -LIMIT * floor or powers[9] < -LIMIT * floor
            or (case["c_load"] == "matched" and powers[5] < -LIMIT * floor)
            or (case["c_load"] == "rigid_closed" and abs(powers[5]) > LIMIT * floor)):
        _fail(f"case {i}: independently recomputed power conservation failure")
    if response.get("blueprint_digest") != receiver.blueprint_digest or \
            response.get("preparation_digest") != receiver.preparation_digest:
        _fail(f"case {i}: identity lost")
    return {"index": i, "input_blueprint": bp, "case": case,
            "core_response": response, "errors": errors,
            "independent_power_defect": defect}


def mutations(baseline: dict[str, Any], base: dict[str, Any]) -> list[dict[str, Any]]:
    """Eight A1.5 controls. Core injection seam, reference held fixed."""
    original_system = physical._system
    original_solve = physical._solve_fixture
    reference = _states(baseline["global"], "baseline global", False)
    out: list[dict[str, Any]] = []
    names = ("wrong_j1_sign", "wrong_j2_sign", "particle_velocity_j1",
             "particle_velocity_j2", "pressure_sign", "endpoint_reversal",
             "wrong_c_load", "output_identity_swap")
    fixed_bp = blueprint(baseline, base)
    for name in names:
        def wrong_matrix(tubes: Any, load: str, scale: float, frequency: float) -> Any:
            m, b = original_system(tubes, load, scale, frequency)
            m = m.copy()
            if name == "wrong_j1_sign":
                m[12, 9] = +1.
            elif name == "wrong_j2_sign":
                m[15, 17] = +1.
            elif name == "particle_velocity_j1":
                m[12, 9] = -2.
            elif name == "particle_velocity_j2":
                m[15, 17] = -.5
            elif name == "pressure_sign":
                m[10, 4] = +1.
            elif name == "endpoint_reversal":
                m[:2, :4] = m[:2, [2, 3, 0, 1]]
            elif name == "wrong_c_load":
                m[17, 11] *= .5
            return m, b
        def wrong_identity(a: float, l: str, s: float, f: float) -> Any:
            sample = original_solve(a, l, s, f)
            if name != "output_identity_swap":
                return sample
            p, u, power = list(sample.pressure_pa), list(sample.volume_flow_m3_s), list(sample.mean_power_w)
            for arr in (p, u, power):
                arr[7], arr[9] = arr[9], arr[7]
            return replace(sample, pressure_pa=tuple(p), volume_flow_m3_s=tuple(u),
                           mean_power_w=tuple(power))
        try:
            if name == "output_identity_swap":
                physical._solve_fixture = wrong_identity
            else:
                physical._system = wrong_matrix
            try:
                obs = prepare_tree5(copy.deepcopy(fixed_bp)).response([733.])
                got = _states({"pressure_pa": obs["pressure_pa"][0],
                               "volume_flow_m3_s": obs["volume_flow_m3_s"][0]},
                              f"mutant {name}", True)
                error = _distance(got, reference)
                if not math.isfinite(error) or error <= MUTANT_LIMIT:
                    _fail(f"mutation {name} SURVIVED: {error}")
                out.append({"name": name, "status": "KILLED_FULL_STATE",
                            "max_scaled_full_state_error": error})
            except Tree5Error as exc:
                if exc.status != "NUMERICALLY_UNRESOLVED" or exc.path != "/frequencies_hz/0":
                    raise
                out.append({"name": name, "status": "KILLED_NUMERIC_REFUSAL",
                            "receipt": exc.receipt()})
        finally:
            physical._system = original_system
            physical._solve_fixture = original_solve
    if len(out) != 8:
        _fail("missing mutation controls")
    return out


def run(output: Path, expected_head: str) -> dict[str, Any]:
    actual_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if not expected_head or actual_head != expected_head:
        _fail(f"STALE_GIT_HEAD: actual={actual_head} expected={expected_head}")
    cases, oracle_hashes = load_oracle()
    base = json.loads(GOLDENS.read_text())["blueprint_snapshot_variants"]["baseline"]["input"]
    if len(cases) != 144:
        _fail("wrong positive denominator")
    records = [score_case(i, case, base) for i, case in enumerate(cases)]
    assert len(records) == 144
    fixed = next((case for case in cases if _case_key(case) == (733, .00015, "matched", 1.)), None)
    if fixed is None:
        _fail("mutant baseline not in actual oracle")
    mutant_results = mutations(fixed, base)
    output.mkdir(parents=True, exist_ok=True)
    cases_file = output / "case-results.jsonl"
    cases_file.write_text("".join(_json(x) + "\n" for x in records), encoding="utf-8")
    (output / "mutations.json").write_text(_json(mutant_results) + "\n", encoding="utf-8")
    tracked = [ROOT / "docs/research/og5-gate-b3-independent-oracle.wl",
               ROOT / "checks/check_og5_gate_b3.py", GOLDENS, *ORACLE_FILES]
    tracked_hashes = {path.relative_to(ROOT).as_posix(): _sha(path) for path in tracked}
    summary = {
        "status": "B3_SCIENTIFIC_MACHINE_CANDIDATE_PASS_NOT_GATE_C",
        "git_head": actual_head,
        "oracle_kernel": "15.0.1 for Linux x86 (64-bit) (July 2, 2026)",
        "positive_denominator": 144,
        "positive_success": len(records),
        "full_complex_values_per_case": 20,
        "wolfram_paths": ("global20", "independent_recursion"),
        "max_global_error": max(x["errors"]["global"] for x in records),
        "max_recursive_error": max(x["errors"]["recursive"] for x in records),
        "max_power_defect": max(x["independent_power_defect"] for x in records),
        "max_condition_2": max(x["core_response"]["diagnostics"][0]["condition_number_2"] for x in records),
        "eight_mutants": mutant_results,
        "raw_case_results_sha256": _sha(cases_file),
        "raw_mutations_sha256": _sha(output / "mutations.json"),
        "source_file_sha256": tracked_hashes,
        "oracle_shards_sha256": oracle_hashes,
    }
    (output / "summary.json").write_text(_json(summary) + "\n", encoding="utf-8")
    provenance = {
        "git_head": actual_head, "git_sha_env": os.getenv("GITHUB_SHA"),
        "run_id": os.getenv("GITHUB_RUN_ID"), "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "run_slot": os.getenv("OG5_RUN_SLOT"), "python": sys.version,
        "source_file_sha256": tracked_hashes,
        "case_results_sha256": _sha(cases_file),
        "mutations_sha256": _sha(output / "mutations.json"),
        "summary_sha256": _sha(output / "summary.json"),
        "qualification": "Numerical conformance, not biological voice, Gate C, or merged Core",
    }
    (output / "provenance.json").write_text(_json(provenance) + "\n", encoding="utf-8")
    (output / "sha256sums.txt").write_text("".join(
        f"{_sha(output / name)}  {name}\n"
        for name in ("case-results.jsonl", "mutations.json", "summary.json", "provenance.json")),
        encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args()
    try:
        summary = run(args.output_dir, args.expected_head)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure = {"status": "FAILED_NOT_ADOPTED", "exception": type(exc).__name__, "detail": str(exc)}
        (args.output_dir / "failure.json").write_text(_json(failure) + "\n", encoding="utf-8")
        raise
    print(_json({k: v for k, v in summary.items() if k not in ("source_file_sha256", "oracle_shards_sha256", "eight_mutants")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
