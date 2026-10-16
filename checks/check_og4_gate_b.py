"""Fresh OG-4 Gate B acceptance evidence (never used by production runtime).

Usage:
 python checks/check_og4_gate_b.py --output-dir evidence-1 --expected-head-sha HEAD
Writes a deterministic case-by-case ledger and SHA sidecars. A preexisting output
directory or wrong HEAD must fail without overwriting archived evidence.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

from morphoacoustics_graph import branch3
from morphoacoustics_graph.branch3 import prepare_branch3, _system, _digest

ROOT = Path(__file__).resolve().parents[1]
PORTS = ["A.in", "A.out", "B.in", "B.out", "C.in", "C.out"]
FREQ = [80, 250, 400, 733, 997, 1200, 2000, 4000]
RATIOS = [.5, 1, 2]
LOADS = ["matched", "pressure_release", "rigid_closed", "fixed_impedance"]
SCALES = [1, .5, -1]
PINNED = {
    "experiments/038_og1_passive_branch/reference.py": "ddc315f941d4c850d8e72f02c9064b1a8f71b684b40863e4b4f0d4ec168ee7f5",
    "experiments/038_og1_passive_branch/run.py": "79b774a71211f5c10144180b959a6cf626de632c3ca221d4a020f6bc8318619b",
    "experiments/038_og1_passive_branch/wolfram/oracle.json": "c840db138214668e081fa2afa9e9fa693969005b6c4c4611b739476a97886e24",
    "experiments/038_og1_passive_branch/wolfram/oracle.wl": "6ddae77e57f61098d4b451b7a5a131961e38fb6a27b516ffcf6f21aba3a20cda",
}


def checksum(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def source():
    path = ROOT / "experiments/038_og1_passive_branch/reference.py"
    spec = importlib.util.spec_from_file_location("og4_independent_reference", path)
    assert spec is not None and spec.loader is not None
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)
    return ref


def blueprint(base: dict, ratio: float, kind: str, scale: float) -> dict:
    b = deepcopy(base)
    b["organs"][2]["area_m2"] = 3e-4 * ratio
    b["source"]["scale"] = scale
    b["loads"][1] = {"port": "C.out", "kind": kind}
    if kind == "fixed_impedance":
        b["loads"][1]["impedance_pa_s_m3"] = {"real": 1372000, "imag": 0}
    return b


def complex_output(observation: dict, sample: int) -> dict:
    result = {}
    for j, port in enumerate(PORTS):
        p = observation["pressure_pa"][sample][j]
        u = observation["volume_flow_m3_s"][sample][j]
        result[port] = (complex(p["real"], p["imag"]),
                        complex(u["real"], u["imag"]))
    return result


def serial(states: dict) -> dict:
    return {pid: [[float(z.real), float(z.imag)] for z in states[pid]] for pid in PORTS}


def scattering_controls() -> dict:
    """Solve pressure continuity + outward flow for three incident bases.

    This 4-unknown junction solve is distinct from the frozen Wolfram closed
    formula. It checks every coefficient, then complex mixed-incident power.
    """
    frozen = json.loads((ROOT / "docs/research/og4-wolfram-gate-a-result.json").read_text())
    results = {}
    for record in frozen["area_ratio_rows"]:
        ratio = float(Fraction(record["C_to_A_area_ratio"]))
        y = np.asarray([1, 1, ratio], dtype=float)
        matrix = np.zeros((4, 4))
        matrix[:3, :3] = np.eye(3)
        matrix[:3, 3] = -1
        matrix[3, :3] = y
        rhs = np.vstack((-np.eye(3), y))
        actual = np.linalg.solve(matrix, rhs)[:3]
        expected = np.asarray([float(Fraction(x)) for x in
                               record["S_rowmajor_rationals"]]).reshape(3, 3)
        coefficient_error = float(np.max(np.abs(actual - expected)))
        diag = np.diag(y)
        energy = float(np.max(np.abs(actual.T @ diag @ actual - diag)))
        reciprocity = float(np.max(np.abs(diag @ actual - (diag @ actual).T)))
        incident = np.array([1+.2j, -.3+.7j, .5-.8j])
        outgoing = actual @ incident
        power = float(abs(np.vdot(incident, diag @ incident) -
                          np.vdot(outgoing, diag @ outgoing)))
        wrong = 2 * np.ones((3, 3)) / 3 - np.eye(3)
        wrong_defect = float(np.max(np.abs(wrong.T @ diag @ wrong - diag)))
        expected_wrong = float(Fraction(record["wrong_particle_velocity_max_weighted_power_defect"]))
        if max(coefficient_error, energy, reciprocity, power,
               abs(wrong_defect - expected_wrong)) > 1e-12:
            raise AssertionError(("local scattering", ratio))
        results[str(ratio)] = {
            "expected_matrix": expected.tolist(), "actual_matrix": actual.tolist(),
            "max_coefficient_error": coefficient_error,
            "weighted_energy_error": energy, "reciprocity_error": reciprocity,
            "complex_mixed_incidence_power_error": power,
            "wrong_particle_velocity_power_defect": wrong_defect,
        }
    if len(results) != 3:
        raise AssertionError("scattering family incomplete")
    return results


def verify_observation_bindings(evidence: dict) -> None:
    """Recompute all identities from archived full inputs/outputs, without solving."""
    observations = evidence["observations"]
    by_digest = {}
    for record in observations:
        snapshot, observation = record["snapshot"], record["observation"]
        bd = _digest("blueprint", snapshot["blueprint"])
        pd = _digest("preparation", {
            "digest_version": snapshot["digest_version"], "backend_id": snapshot["backend_id"],
            "blueprint_digest": bd, "port_mapping": branch3.PORT_MAPPING})
        if (bd != snapshot["blueprint_digest"] or pd != snapshot["preparation_digest"] or
                pd != observation["preparation_digest"] or
                record["request_frequencies_hz"] != observation["frequencies_hz"] or
                _digest("observation", observation) != observation["observation_digest"]):
            raise AssertionError("archived request/observation identity mismatch")
        by_digest[observation["observation_digest"]] = record
    for family in evidence["comparison_families"].values():
        for case in family["cases"]:
            record = by_digest[case["observation_digest"]]
            snapshot, obs = record["snapshot"], record["observation"]
            index = obs["frequencies_hz"].index(case["frequency_hz"])
            if (case["actual_ports"] != serial(complex_output(obs, index)) or
                    case["blueprint_digest"] != snapshot["blueprint_digest"] or
                    case["preparation_digest"] != snapshot["preparation_digest"]):
                raise AssertionError("case detached from archived observation")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-head-sha", required=True)
    args = parser.parse_args()
    actual_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if actual_head != args.expected_head_sha:
        parser.error("HEAD mismatch: stale / wrong-target evidence rejected")
    if args.output_dir.exists():
        parser.error("stale output directory rejected")
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True)
    if status:
        parser.error("dirty worktree cannot be used as exact-HEAD evidence")
    if Path(branch3.__file__).resolve() != ROOT / "src/morphoacoustics_graph/branch3.py":
        parser.error("imported backend is not the checked-out source")
    source_hashes = {path: checksum(ROOT / path) for path in PINNED}
    if source_hashes != PINNED:
        parser.error("frozen research comparator or oracle was modified")
    source_hashes["src/morphoacoustics_graph/branch3.py"] = checksum(
        ROOT / "src/morphoacoustics_graph/branch3.py")
    source_hashes["src/morphoacoustics/acoustics/uniform_tube.py"] = checksum(
        ROOT / "src/morphoacoustics/acoustics/uniform_tube.py")
    provenance_paths = subprocess.check_output([
        "git", "ls-files", "src/morphoacoustics_graph", "docs/research/og4-*",
        "checks/check_og4_gate_b.py", "tests/test_branch3_public.py",
        ".github/workflows/og4-gate-b.yml", "pyproject.toml"], cwd=ROOT, text=True).splitlines()
    source_hashes.update({path: checksum(ROOT / path) for path in provenance_paths})
    golden = json.loads((ROOT / "docs/research/og4-branch3-api-golden.json").read_text())
    base = golden["snapshot_example"]["blueprint"]
    frozen = json.loads((ROOT / "experiments/038_og1_passive_branch/wolfram/oracle.json").read_text())
    ref = source()
    observations: list[dict] = []
    python_cases: list[dict] = []
    wolfram_cases: list[dict] = []
    max_python = 0.
    max_wolfram_state = 0.
    max_wolfram_power = 0.
    for ratio in RATIOS:
        for load in LOADS:
            for scale in SCALES:
                prepared = prepare_branch3(blueprint(base, ratio, load, scale))
                result = prepared.response(FREQ)
                observations.append({"snapshot": prepared.to_snapshot(),
                                     "request_frequencies_hz": list(FREQ), "observation": result})
                for index, f in enumerate(FREQ):
                    expected = ref.port_states(ratio, f, load, scale)
                    actual = complex_output(result, index)
                    discrepancy = float(ref.state_error(actual, expected, 1.372, 1e-6))
                    if discrepancy > 1e-10:
                        raise AssertionError(("Python", ratio, load, scale, f, discrepancy))
                    max_python = max(max_python, discrepancy)
                    python_cases.append({
                        "ratio": ratio, "load": load, "scale": scale, "frequency_hz": f,
                        "expected_ports": serial(expected), "actual_ports": serial(actual),
                        "max_state_error": discrepancy,
                        "diagnostics": result["diagnostics"][index],
                        "blueprint_digest": prepared.blueprint_digest,
                        "preparation_digest": prepared.preparation_digest,
                        "observation_digest": result["observation_digest"],
                    })
    for record in frozen["records"]:
        ratio, load, f = record["area_ratio"], record["load_c"], record["frequency_hz"]
        prepared = prepare_branch3(blueprint(base, ratio, load, 1))
        result = prepared.response([f])
        observations.append({"snapshot": prepared.to_snapshot(),
                             "request_frequencies_hz": [f], "observation": result})
        actual = complex_output(result, 0)
        expected = {pid: (complex(*record["ports"][pid][0]),
                          complex(*record["ports"][pid][1])) for pid in PORTS}
        error = float(ref.state_error(actual, expected, 1.372, 1e-6))
        power_error = max(abs(result["mean_power_w"][0][k] - power) / (.5*1.372e-6)
                          for k, power in zip((0, 3, 5), record["powers_input_B_C_w"]))
        if error > 1e-10 or power_error > 1e-10:
            raise AssertionError(("Wolfram", ratio, load, f, error, power_error))
        max_wolfram_state = max(max_wolfram_state, error)
        max_wolfram_power = max(max_wolfram_power, power_error)
        wolfram_cases.append({
            "ratio": ratio, "load": load, "frequency_hz": f,
            "expected_ports": serial(expected), "actual_ports": serial(actual),
            "max_state_error": error, "normalized_power_error": power_error,
            "expected_input_B_C_power_w": record["powers_input_B_C_w"],
            "actual_input_B_C_power_w": [result["mean_power_w"][0][k] for k in (0, 3, 5)],
            "blueprint_digest": prepared.blueprint_digest,
            "preparation_digest": prepared.preparation_digest,
            "observation_digest": result["observation_digest"],
        })
    if len(python_cases) != 288 or len(wolfram_cases) != 24:
        raise AssertionError("case family incomplete")
    # Deliberately falsify three independent junction laws on unequal areas.
    negative = {}
    test_bp = blueprint(base, 2, "matched", 1)
    fixed_prepared = prepare_branch3(test_bp)
    m0, rhs0 = _system(fixed_prepared._tubes,
                       {load["port"]: load for load in test_bp["loads"]},
                       1e-6*(1+.4j), 733)
    expected = ref.port_states(2, 733, "matched")
    for name in ("wrong_signed_flow", "wrong_particle_velocity", "wrong_pressure_sign"):
        bad = m0.copy()
        if name == "wrong_signed_flow":
            bad[8, 5], bad[8, 9] = 1, 1
        elif name == "wrong_particle_velocity":
            bad[8, 9] = -.5
        else:
            bad[6, 4] = 1
        solution = np.linalg.solve(bad, rhs0)
        actual = {port: (solution[2*i]*1.372, solution[2*i+1]*1e-6)
                  for i, port in enumerate(PORTS)}
        discrepancy = float(ref.state_error(actual, expected, 1.372, 1e-6))
        if not discrepancy > 1e-3:
            raise AssertionError(("wrong-law falsifier not detected", name, discrepancy))
        negative[name] = discrepancy
    scattering = scattering_controls()
    evidence = {
        "falsifying_mutation_normalized_errors": negative,
        "local_scattering_independent_controls": scattering,
        "evidence_kind": "og4.gate-b.fresh-full-port.v2",
        "decision": "GATE_B_REFERENCE_COMPARISONS_ONLY_NOT_ADOPTED",
        "git_head": actual_head,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "ci_context": {key: os.environ.get(key, "") for key in (
            "GITHUB_REPOSITORY", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_JOB")},
        "observations": observations,
        "source_sha256": source_hashes,
        "comparison_families": {
            "branch3_vs_inherited_python_288": {
                "count": 288, "max_normalized_complex_state_error": max_python,
                "cases": python_cases},
            "branch3_vs_frozen_wolfram_24": {
                "count": 24, "max_normalized_complex_state_error": max_wolfram_state,
                "max_normalized_power_error": max_wolfram_power,
                "cases": wolfram_cases},
        },
    }
    verify_observation_bindings(evidence)
    data = (json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True,
                       allow_nan=False) + "\n").encode("utf-8")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    (args.output_dir / "evidence.json").write_bytes(data)
    (args.output_dir / "sha256.txt").write_text(
        f"{hashlib.sha256(data).hexdigest()}  evidence.json\n")
    print(json.dumps({
        "python_cases": len(python_cases), "wolfram_cases": len(wolfram_cases),
        "max_python": max_python, "max_wolfram": max_wolfram_state,
        "max_wolfram_power": max_wolfram_power, "git_head": actual_head,
        "evidence_sha256": hashlib.sha256(data).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
