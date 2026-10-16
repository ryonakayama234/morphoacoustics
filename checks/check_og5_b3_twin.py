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
import struct
import subprocess
import sys
from typing import Any

PHYSICAL_TOL = 1e-10
DIAGNOSTIC_TOL = 1e-8
P_REF, U_REF = 1.372, 1e-6
EXPECTED_NAMES = ("case-results.jsonl", "mutations.json", "summary.json",
                  "provenance.json", "sha256sums.txt")
SCORED_METRICS = ("max_global_error", "max_recursive_error",
                  "max_power_defect", "max_condition_2")
ROOT = Path(__file__).resolve().parents[1]
PORTS = [f"{n}.{side}" for n in "ABCDE" for side in ("in", "out")]


def require(condition: Any, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical(value: Any) -> bytes:
    """Standalone A1 byte encoder; this audit imports no production Core."""
    if type(value) in (int, float):
        require(math.isfinite(value), "nonfinite canonical value")
        return b"d" + struct.pack(">d", 0. if value == 0 else float(value))
    if type(value) is str:
        raw = value.encode("ascii")
        return b"s" + struct.pack(">I", len(raw)) + raw
    if type(value) is list:
        return b"l" + struct.pack(">I", len(value)) + b"".join(map(canonical, value))
    require(type(value) is dict, "invalid canonical type")
    return b"m" + struct.pack(">I", len(value)) + b"".join(
        canonical(k) + canonical(value[k]) for k in sorted(value))


def digest(domain: str, value: Any) -> str:
    prefix = f"morphoacoustics.og5.{domain}.v1".encode("ascii") + b"\0"
    return "sha256:" + hashlib.sha256(prefix + canonical(value)).hexdigest()


def audit_record(record: dict[str, Any]) -> None:
    """Recompute raw comparisons, identities and power; distrust stored errors."""
    c, o, bp = record["case"], record["core_response"], record["input_blueprint"]
    require(o["port_ids"] == PORTS and o["status"] == "SUCCESS", "wrong port mapping/status")
    require(o["frequencies_hz"] == [float(c["frequency_hz"])], "wrong sample frequency")
    for collection, key in (("organs", "id"), ("junctions", "id"), ("loads", "port")):
        require(bp[collection] == sorted(bp[collection], key=lambda x: x[key]), "noncanonical blueprint")
    require(next(x["area_m2"] for x in bp["organs"] if x["id"] == "C") == c["c_area_m2"]
            and next(x["kind"] for x in bp["loads"] if x["port"] == "C.out") == c["c_load"]
            and bp["source"]["scale"] == c["scale"], "case/input mismatch")
    require(o["blueprint_digest"] == digest("blueprint", bp), "wrong blueprint digest")
    prepared = {"schema": "og5.tree5.prepared.snapshot.v1", "digest_version": o["digest_version"],
                "backend_id": o["backend_id"], "blueprint_digest": o["blueprint_digest"]}
    require(o["preparation_digest"] == digest("preparation", prepared), "wrong preparation digest")
    require(o["observation_digest"] == digest("observation", {
        k: v for k, v in o.items() if k != "observation_digest"}), "wrong observation digest")
    states = []
    for name, scale in (("pressure_pa", P_REF), ("volume_flow_m3_s", U_REF)):
        require(len(o[name]) == 1 and len(o[name][0]) == 10, "wrong state shape")
        values = [pair(z) for z in o[name][0]]
        states.append(values)
        for method in ("global", "recursive"):
            refs = c[method][name]
            require(len(refs) == 10, "wrong oracle shape")
            error = max(abs(v - complex(*r)) / scale for v, r in zip(values, refs))
            require(math.isfinite(error) and error <= PHYSICAL_TOL, "raw Core/oracle mismatch")
    powers = o["mean_power_w"][0]
    require(len(o["mean_power_w"]) == 1 and len(powers) == 10, "wrong power shape")
    p, u = states
    floor = .5 * P_REF * U_REF * abs(c["scale"])**2
    for v, a, b in zip(powers, p, u):
        expected = .5 * (a * b.conjugate()).real
        require(math.isfinite(v) and abs(v - expected) <= PHYSICAL_TOL * max(abs(expected), floor),
                "wrong raw power")
    require(powers[0] > 0 and abs(powers[0] - powers[5] - powers[7] - powers[9])
            <= PHYSICAL_TOL * max(abs(powers[0]), floor), "raw energy imbalance")


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
    expected = [(f, a, l, s) for f in (80, 250, 400, 733, 997, 1200, 2000, 4000)
                for a in (.00015, .0003, .0006) for l in ("matched", "rigid_closed") for s in (1., .5, -1.)]
    require([(r["case"]["frequency_hz"], r["case"]["c_area_m2"], r["case"]["c_load"], r["case"]["scale"])
             for r in cases] == expected, "incomplete/duplicate physical coverage")
    for record in cases:
        audit_record(record)
    require(len(summary["eight_mutants"]) == 8 and len(mutations) == 8, "mutation coverage lost")
    require(summary["eight_mutants"] == mutations, "summary mutation receipt differs")
    require(provenance["case_results_sha256"] == summary["raw_case_results_sha256"], "case checksum mismatch")
    require(provenance["mutations_sha256"] == summary["raw_mutations_sha256"], "mutation checksum mismatch")
    require(provenance["summary_sha256"] == hashlib.sha256((folder / "summary.json").read_bytes()).hexdigest(),
            "summary checksum mismatch")
    require(provenance["source_file_sha256"] == summary["source_file_sha256"], "source hash mismatch")
    required_sources = {"src/morphoacoustics_graph/tree5.py", "src/morphoacoustics_graph/tree5_contract.py",
                        "src/morphoacoustics/acoustics/uniform_tube.py", "checks/check_og5_b3_twin.py"}
    require(required_sources <= set(summary["source_file_sha256"]), "missing production source hashes")
    for name, sha in summary["source_file_sha256"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha, f"source differs: {name}")
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
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    require(pa["git_head"] == head, "archives do not match checked-out HEAD")
    require(sa["source_file_sha256"] == sb["source_file_sha256"], "not the same pinned source")
    require(sa["oracle_shards_sha256"] == sb["oracle_shards_sha256"], "different oracle")
    require(sa["oracle_kernel"] == sb["oracle_kernel"], "different Wolfram kernel")
    require(sa["positive_denominator"] == sb["positive_denominator"] == 144, "wrong denominator")
    require(sa["wolfram_paths"] == sb["wolfram_paths"], "wrong reference path")
    require(len(ma) == len(mb) == 8, "mutant count changed")
    for a_mut, b_mut in zip(ma, mb):
        require(a_mut["name"] == b_mut["name"] and a_mut["status"] == b_mut["status"],
                f"mutant kind/kill status diverges: {a_mut['name']}")
        if a_mut["status"] == "KILLED_FULL_STATE":
            x, y = a_mut["max_scaled_full_state_error"], b_mut["max_scaled_full_state_error"]
            require(min(x, y) > 1e-6 and abs(x - y) <= PHYSICAL_TOL,
                    f"mutant physical margin changed: {a_mut['name']}")
        else:
            require(a_mut["status"] == "KILLED_NUMERIC_REFUSAL"
                    and a_mut["receipt"] == b_mut["receipt"],
                    f"numeric refusal changed: {a_mut['name']}")
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
            if k == "condition_number_2":
                relative = abs(v - w) / max(abs(v), abs(w))
                require(relative <= DIAGNOSTIC_TOL, f"{i}: {k} differs: {relative}")
            elif k == "scaled_linear_residual":
                require(max(v, w) <= 1e-12, f"{i}: linear residual exceeds A1 bound")
            else:
                require(max(v, w) <= PHYSICAL_TOL, f"{i}: diagnostic {k} exceeds A1 bound")
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
