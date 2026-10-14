"""Recompute every frozen fixture and publish fresh, reproducible research evidence."""
from __future__ import annotations
import argparse
import csv
from dataclasses import replace
from hashlib import sha256
import itertools
import json
import os
from pathlib import Path
import re
import platform
import subprocess
import sys

import numpy as np
import network as n
import reference as r

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREQUENCIES = (80, 250, 400, 733, 997, 1200, 2000, 4000)
LOADS = ("matched", "pressure_release", "rigid_closed", "fixed_impedance")
PINNED_UNIFORM_BLOB = "8bceaf1426c2aec56eea91e2148cd402998516f2"


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n")


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    from hashlib import sha1
    return sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def checkout_attestation(expected_head_sha: str | None) -> dict[str, object]:
    """Derive true source identity from Git; never trust a claimed head SHA."""
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout.strip()

    head = git("rev-parse", "HEAD")
    if re.fullmatch(r"[0-9a-f]{40}", head) is None:
        raise RuntimeError("INVALID_GIT_HEAD")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("DIRTY_TRACKED_CHECKOUT")
    if expected_head_sha is not None and expected_head_sha != head:
        raise RuntimeError(f"HEAD_SHA_MISMATCH expected={expected_head_sha} actual={head}")
    return {
        "head_sha": head, "tracked_checkout_clean": True,
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "github_job": os.getenv("GITHUB_JOB"),
        "github_event_name": os.getenv("GITHUB_EVENT_NAME"),
    }


def run(output: Path, *, expected_head_sha: str | None = None) -> dict:
    checkout = checkout_attestation(expected_head_sha)
    # Reserve exclusively. Failed/incomplete directories never count as fresh evidence.
    output.mkdir(parents=True, exist_ok=False)
    primitive = ROOT / "src/morphoacoustics/acoustics/uniform_tube.py"
    if git_blob(primitive) != PINNED_UNIFORM_BLOB:
        raise RuntimeError("adopted UniformTube drift: re-audit rather than silently re-pin")
    oracle = json.loads((HERE / "wolfram/oracle.json").read_text())
    metrics, graphs, rows = [], {}, []
    finite_gates = []
    for ratio, load_c, scale, f in itertools.product((.5, 1., 2.), LOADS, (1., .5, -1.), FREQUENCIES):
        graph = n.fixture(ratio, load_c, scale)
        body = n.prepare(graph)
        graphs[body.graph_digest] = n.graph_payload(graph)
        result = n.solve(body, f)
        error = r.state_error(result.ports, r.port_states(ratio, f, load_c, scale), body.p_ref)
        gates = {
            "oracle": error <= 1e-10,
            "condition": result.condition <= 1e8,
            "backward": result.backward_error <= 1e-12,
            "pressure": result.junction_pressure_error <= 1e-10,
            "flow": result.junction_flow_error <= 1e-10,
            "power": result.power_error <= 1e-10,
            "passive_terminals": min(result.powers_w) >= -.5 * body.p_ref * n.U_REF * scale**2 * 1e-10,
        }
        if load_c in ("pressure_release", "rigid_closed"):
            gates["zero_terminal_power"] = abs(result.powers_w[2]) / (.5 * body.p_ref * n.U_REF * scale**2) <= 1e-10
        finite_gates.append(all(gates.values()))
        run_id = n.digest({"graph": body.graph_digest, "frequency_hz": f})
        metrics.append({"run_id": run_id, "graph_digest": body.graph_digest,
                        "area_ratio_c": ratio, "load_c": load_c, "source_scale": scale,
                        "frequency_hz": f, "oracle_error": error, "condition": result.condition,
                        "backward_error": result.backward_error,
                        "pressure_error": result.junction_pressure_error,
                        "flow_error": result.junction_flow_error, "power_error": result.power_error,
                        "powers_input_B_C_w": result.powers_w, "gates": gates})
        for key, (pressure, flow) in sorted(result.ports.items()):
            rows.append((run_id, body.graph_digest, ratio, load_c, scale, f, key,
                         pressure.real, pressure.imag, flow.real, flow.imag))
    wolfram_errors = []
    for record in oracle["records"]:
        body = n.prepare(n.fixture(record["area_ratio"], record["load_c"]))
        response = n.solve(body, record["frequency_hz"])
        expected = {key: tuple(complex(*value) for value in pair)
                    for key, pair in record["ports"].items()}
        wolfram_errors.append(r.state_error(response.ports, expected, body.p_ref))
    local_records: list[dict[str, object]] = []
    local_errors: list[float] = []
    for ratio in (.5, 1., 2.):
        areas = (3e-4, 3e-4, 3e-4 * ratio)
        scattering = np.column_stack([n.local_scatter(areas, incoming) for incoming in np.eye(3)])
        y = np.array([1, 1, ratio])
        coefficient_error = float(np.max(abs(scattering - r.scatter_matrix(areas))))
        identity_error = float(np.max(abs(scattering.conj().T @ np.diag(y) @ scattering - np.diag(y))))
        incoming = np.array([1+.4j, -.2+.7j, .6-.1j])
        outgoing = n.local_scatter(areas, incoming)
        mixed_error = float(abs(np.sum(y * abs(incoming)**2) - np.sum(y * abs(outgoing)**2)))
        local_errors.extend((coefficient_error, identity_error, mixed_error))
        local_records.append({"area_ratio_c": ratio, "pressure_scattering_real": scattering.real.tolist(),
                              "pressure_scattering_imag": scattering.imag.tolist(),
                              "reflection_B_C_power_fractions": (y * abs(scattering[:, 0])**2).tolist(),
                              "coefficient_error": coefficient_error, "weighted_identity_error": identity_error,
                              "mixed_incidence_power_error": mixed_error})
    mutation_errors = {}
    body = n.prepare(n.fixture(2.))
    for mutation in ("wrong_sign", "particle_velocity"):
        mutated = n.solve(body, 733, _mutation=mutation)
        mutation_errors[mutation] = r.state_error(mutated.ports, r.port_states(2., 733, "matched"), body.p_ref)
    singular = n.fixture(load_c="pressure_release")
    singular = replace(singular, tubes=tuple(replace(t, length_m=.08) for t in singular.tubes),
                       boundaries=(singular.boundaries[0], n.Boundary(n.Port("B", "out"), "pressure_release"),
                                   singular.boundaries[2]))
    try:
        n.solve(n.prepare(singular), 343 / (.08 * 2))
        singular_record = {"status": "FAILED", "diagnostic": "singular model fabricated a finite result"}
    except n.NumericallyUnresolved as exc:
        singular_record = {"status": exc.status, "diagnostic": str(exc)}
    checks = {"finite_fixtures": all(finite_gates), "wolfram": max(wolfram_errors) <= 1e-10,
              "local_scattering": max(local_errors) <= 1e-12,
              "mutation_controls": min(mutation_errors.values()) > 1e-3,
              "singular_reported": singular_record["status"] == "NUMERICALLY_UNRESOLVED"}
    with (output / "states.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("run_id", "graph_digest", "area_ratio_c", "load_c", "source_scale", "frequency_hz",
                         "port", "pressure_real_pa", "pressure_imag_pa", "flow_real_m3_s", "flow_imag_m3_s"))
        writer.writerows(rows)
    write_json(output / "metrics.json", metrics)
    write_json(output / "graphs.json", graphs)
    write_json(output / "local_scattering.json", local_records)
    sources = {str(path.relative_to(ROOT)): file_hash(path)
               for path in [HERE / "PROTOCOL.md", HERE / "network.py", HERE / "reference.py", HERE / "run.py",
                            HERE / "wolfram/oracle.wl", HERE / "wolfram/oracle.json", primitive]}
    evidence = {name: file_hash(output / name)
                for name in ("states.csv", "metrics.json", "graphs.json", "local_scattering.json")}
    identity = {"revision": checkout["head_sha"], "checkout_attestation": checkout,
                "sources": sources, "frequencies_hz": FREQUENCIES,
                "environment": {"python": platform.python_version(), "numpy": np.__version__,
                                "platform": platform.platform()}, "graph_digests": sorted(graphs)}
    summary = {"evidence_schema": "og1.evidence.v2", "checkout_attestation": checkout,
               "numeric_status": "PROVISIONAL_NUMERICAL_PASS" if all(checks.values()) else "FAILED",
               "adoption_status": "NOT_ADOPTED", "independent_review": "PENDING", "checks": checks,
               "nominal_runs": len(metrics), "wolfram_records": len(wolfram_errors),
               "max_oracle_error": max(float(m["oracle_error"]) for m in metrics),
               "max_wolfram_error": max(wolfram_errors), "max_local_error": max(local_errors),
               "max_condition": max(float(m["condition"]) for m in metrics),
               "max_backward_error": max(float(m["backward_error"]) for m in metrics),
               "max_power_error": max(float(m["power_error"]) for m in metrics),
               "mutation_errors": mutation_errors, "singular_fixture": singular_record,
               "evidence_sha256": evidence, "identity": identity, "run_identity_sha256": n.digest(identity)}
    # Completion marker last; no incomplete directory can masquerade as successful output.
    write_json(output / "summary.json", summary)
    (output / "summary_sha256.txt").write_text(file_hash(output / "summary.json") + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-head-sha", default=None)
    args = parser.parse_args()
    try:
        summary = run(args.output_dir, expected_head_sha=args.expected_head_sha)
    except (n.InvalidGraph, n.UnsupportedGraph, n.NumericallyUnresolved) as exc:
        failure = {"numeric_status": exc.status, "diagnostic": str(exc), "adoption_status": "NOT_ADOPTED"}
        if args.output_dir.is_dir() and not (args.output_dir / "summary.json").exists():
            write_json(args.output_dir / "failure.json", failure)
        print(json.dumps(failure), file=sys.stderr)
        sys.exit(2)
    print(json.dumps({key: summary[key] for key in ("numeric_status", "nominal_runs", "max_oracle_error",
                                                  "max_wolfram_error", "max_power_error", "mutation_errors")}, indent=2))
    sys.exit(0 if summary["numeric_status"] == "PROVISIONAL_NUMERICAL_PASS" else 1)
