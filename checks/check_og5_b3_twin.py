#!/usr/bin/env python3
"""Audit TWO independent raw OG-5 B3 trial archives.

Raw SHA256 checked byte-exact separately. Do NOT demand bit-identical float
observations across different Ubuntu/BLAS workers: compare physical p/U/power
with frozen tolerances, semantic identity exact, diagnostics with tight floating
tolerances. Exact Observation hashes may differ while both computations are sound.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

PHYSICAL_TOL = 1e-10
DIAGNOSTIC_TOL = 1e-8
P_REF, U_REF = 1.372, 1e-6
EXPECTED_NAMES = ("case-results.jsonl", "mutations.json", "summary.json",
                  "provenance.json", "sha256sums.txt")
SCORED_METRICS = ("max_global_error", "max_recursive_error",
                  "max_power_defect", "max_condition_2")


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(folder: Path) -> tuple[list[dict[str, Any]], Any, dict[str, Any], dict[str, Any]]:
    for name in EXPECTED_NAMES:
        require((folder / name).is_file(), f"missing {folder}/{name}")
    seen: set[str] = set()
    for line in (folder / "sha256sums.txt").read_text().splitlines():
        sha, name = line.split("  ", 1)
        require(name not in seen, f"duplicate checksum {name}")
        seen.add(name)
        actual = hashlib.sha256((folder / name).read_bytes()).hexdigest()
        require(sha == actual, f"tampered raw archive {folder}/{name}")
    require(seen == set(EXPECTED_NAMES) - {"sha256sums.txt"}, "incomplete checksums")
    cases = [json.loads(line) for line in (folder / "case-results.jsonl").read_text().splitlines()]
    mutations = json.loads((folder / "mutations.json").read_text())
    summary = json.loads((folder / "summary.json").read_text())
    provenance = json.loads((folder / "provenance.json").read_text())
    require(summary["positive_success"] == 144 and len(cases) == 144, "positive denominator lost")
    require(summary["status"] == "B3_SCIENTIFIC_MACHINE_CANDIDATE_PASS_NOT_GATE_C", "wrong status")
    require(len(summary["eight_mutants"]) == 8 and len(mutations) == 8, "mutation coverage lost")
    require(summary["eight_mutants"] == mutations, "summary mutation receipt differs")
    require(provenance["case_results_sha256"] == summary["raw_case_results_sha256"], "case checksum mismatch")
    require(provenance["mutations_sha256"] == summary["raw_mutations_sha256"], "mutation checksum mismatch")
    require(provenance["summary_sha256"] == hashlib.sha256((folder / "summary.json").read_bytes()).hexdigest(),
            "summary checksum mismatch")
    require(provenance["source_file_sha256"] == summary["source_file_sha256"], "source hash mismatch")
    return cases, mutations, summary, provenance


def comp_number(a: Any, b: Any, atol: float, label: str) -> float:
    require(type(a) in (float, int) and type(b) in (float, int), f"{label}: wrong numeric type")
    require(math.isfinite(a) and math.isfinite(b), f"{label}: nonfinite")
    error = abs(a - b) / atol
    require(error <= PHYSICAL_TOL, f"{label}: exceeds tolerance {error}")
    return error


def pair(c: Any) -> complex:
    require(set(c) == {"real", "imag"}, "wrong complex schema")
    require(all(math.isfinite(x) for x in c.values()), "nonfinite complex")
    return complex(c["real"], c["imag"])


def compare_two(root: Path) -> float:
    aa, ma, sa, pa = load(root / "og5-b3-a")
    bb, mb, sb, pb = load(root / "og5-b3-b")
    require(pa["run_slot"] == "a" and pb["run_slot"] == "b", "runner slot mislabeled")
    require(pa["git_head"] == pb["git_head"] == sa["git_head"] == sb["git_head"], "cross-head evidence")
    require(sa["source_file_sha256"] == sb["source_file_sha256"], "not the same pinned source")
    require(sa["oracle_shards_sha256"] == sb["oracle_shards_sha256"], "different oracle")
    require(sa["oracle_kernel"] == sb["oracle_kernel"], "different Wolfram kernel")
    require(sa["positive_denominator"] == sb["positive_denominator"] == 144, "wrong denominator")
    require(sa["wolfram_paths"] == sb["wolfram_paths"], "wrong reference path")
    require(ma == mb, "mutant detection/provenance changed between runners")
    maximum = 0.0
    for i, (a, b) in enumerate(zip(aa, bb)):
        require(a["index"] == b["index"] == i, "case order changed")
        require(a["input_blueprint"] == b["input_blueprint"], f"case {i}: body changed")
        require(a["case"] == b["case"], f"case {i}: oracle changed")
        ax, bx = a["core_response"], b["core_response"]
        for name in ("schema", "digest_version", "backend_id", "blueprint_digest",
                     "preparation_digest", "status", "frequencies_hz", "port_ids"):
            require(ax[name] == bx[name], f"case {i}: identity {name} changed")
        require(len(ax["pressure_pa"]) == len(bx["pressure_pa"]) == 1, "wrong pressure grid")
        require(len(ax["volume_flow_m3_s"]) == len(bx["volume_flow_m3_s"]) == 1, "wrong flow grid")
        for name, unit in (("pressure_pa", P_REF), ("volume_flow_m3_s", U_REF)):
            xp, yp = ax[name][0], bx[name][0]
            require(len(xp) == len(yp) == 10, f"{i}: wrong port count")
            for k, (one, two) in enumerate(zip(xp, yp)):
                e = abs(pair(one) - pair(two)) / unit
                require(math.isfinite(e) and e <= PHYSICAL_TOL, f"{i}: {name}/{k}: {e}")
                maximum = max(maximum, e)
        require(len(ax["mean_power_w"]) == len(bx["mean_power_w"]) == 1, "wrong power grid")
        floor = .5 * P_REF * U_REF * abs(a["case"]["scale"])**2
        for k, (x, y) in enumerate(zip(ax["mean_power_w"][0], bx["mean_power_w"][0])):
            e = abs(x - y) / max(abs(x), abs(y), floor)
            require(math.isfinite(e) and e <= PHYSICAL_TOL, f"{i}: mean power/{k}: {e}")
        for k in ("global", "recursive"):
            x, y = a["errors"][k], b["errors"][k]
            require(math.isfinite(x) and math.isfinite(y), "nonfinite comparator metric")
            require(max(x, y) <= PHYSICAL_TOL, f"{i}: failing Core vs oracle")
        for k, v in ax["diagnostics"][0].items():
            w = bx["diagnostics"][0][k]
            require(math.isfinite(v) and math.isfinite(w), f"{i}: nonfinite {k}")
            relative = abs(v - w) / max(abs(v), abs(w), 1e-12)
            require(relative <= DIAGNOSTIC_TOL, f"{i}: {k} differs: {relative}")
    for k in SCORED_METRICS:
        require(math.isfinite(sa[k]) and math.isfinite(sb[k]), f"nonfinite {k}")
        if k == "max_condition_2":
            require(abs(sa[k] - sb[k]) / max(sa[k], sb[k]) <= DIAGNOSTIC_TOL, "condition unstable")
        else:
            require(max(sa[k], sb[k]) <= PHYSICAL_TOL, f"{k}: invalid upper bound")
    print(json.dumps({"status": "TWO_RAW_ARCHIVES_VALID_PHYSICALLY_EQUIVALENT",
                      "git_head": pa["git_head"], "cases": 144, "mutants": 8,
                      "max_normalized_cross_runner_port_error": maximum,
                      "raw_byte_identical_required": False, "gate_c": "PENDING"}, sort_keys=True))
    return maximum


if __name__ == "__main__":
    compare_two(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("twin"))
