"""NR-1a research-only terminal-route comparison (NOT a Core public backend).

N and O use the adopted OG-4 prepare_branch3/response path as-is.
M (oral distal closed) uses an isolated recursive impedance solver only;
OG-4 must still reject M. Full state is checked versus independent Wolfram
global12 solution, never fed from it. No WAV or velopharyngeal valve model.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
from typing import Any

from morphoacoustics_graph.branch3 import Branch3Error, prepare_branch3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORACLE_PATH = HERE / "wolfram" / "global12_oracle.json"
FREQUENCIES = [80, 250, 400, 733, 997, 1200, 2000, 4000]
PORTS = ["A.in", "A.out", "B.in", "B.out", "C.in", "C.out"]
CASES = {
    "N": ("matched", "rigid_closed"),
    "O": ("matched", "matched"),
    "M": ("rigid_closed", "matched"),
}
LENGTHS = (.08, .09, .06)
AREAS = (.0003, .0003, .00015)
RHO = 1.2
SPEED = 343.0
SOURCE = complex(1e-6, 4e-7)
P_REF, U_REF = 1.372, 1e-6
MAX_STATE = 1e-10
MAX_POWER = 1e-10
MAX_RESIDUAL = 1e-10
MAX_INTERNAL_CONDITION = 1e8
EXPERIMENT_BACKEND = "nr1a.research-only.recursive3.v0"


def pack(z: complex) -> dict[str, float]:
    return {"real": float(z.real) if z.real else 0.0,
            "imag": float(z.imag) if z.imag else 0.0}


def unpack(z: dict[str, float]) -> complex:
    return complex(z["real"], z["imag"])


def blueprint(case: str) -> dict[str, Any]:
    """Complete typed OG-4 blueprint, even when M is beyond its capability."""
    if case not in CASES:
        raise ValueError("UNSUPPORTED:UNKNOWN_CASE")
    organs = []
    for name, length, area in zip("ABC", LENGTHS, AREAS):
        organs.append({
            "id": name, "revision": "nr1a.r0", "length_m": length,
            "area_m2": area, "sound_speed_m_s": SPEED,
            "air_density_kg_m3": RHO,
            "inlet": {"id": name + ".in", "kind": "acoustic.p_u",
                      "direction": "inlet"},
            "outlet": {"id": name + ".out", "kind": "acoustic.p_u",
                       "direction": "outlet"},
        })
    return {
        "schema": "og4.passive.branch3.v1", "organs": organs,
        "junctions": [{"id": "J", "law": "ideal.branch3.p_u",
                       "ports": ["A.out", "B.in", "C.in"]}],
        "source": {
            "kind": "prescribed_volume_flow", "phasor_schema": "og4.peak.exp_plus_i.v1",
            "port": "A.in", "amplitude_m3_s": pack(SOURCE), "scale": 1.0,
        },
        "loads": [{"port": name + ".out", "kind": kind}
                  for name, kind in zip("BC", CASES[case])],
    }


def canonical_sha(obj: Any) -> str:
    """Research/evidence SHA only, explicitly NOT the OG-4 canonical ABI."""
    body = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("ascii")
    return "sha256:" + sha256(body).hexdigest()


def power(p: complex, u: complex) -> float:
    return 0.5 * (p * u.conjugate()).real


def recursive_mouth_closed(case: str, fs: list[int]) -> dict[str, Any]:
    """Independent reduction using terminal admittances; only M is allowed.

    Harmonic transfer from distal to proximal:
    [p_in,U_in] = [[cos(t), i*Z*sin(t)], [i*sin(t)/Z,cos(t)]] [p_out,U_out].
    Solve branch input admittances, J pressure, then reconstruct six endpoints.
    This NEVER assembles the Wolfram global 12x12 equations.
    """
    if case != "M" or fs != FREQUENCIES:
        raise ValueError("UNSUPPORTED:RESEARCH_SCOPE")
    state_p: list[list[dict[str, float]]] = []
    state_u: list[list[dict[str, float]]] = []
    state_power: list[list[float]] = []
    diagnostics: list[dict[str, float]] = []
    z = [RHO * SPEED / a for a in AREAS]
    for f in fs:
        t = [2.0 * math.pi * f * length / SPEED for length in LENGTHS]
        cs, sn = [math.cos(x) for x in t], [math.sin(x) for x in t]
        # Each terminal vector equals (Z*g, g) for matched and (Z*g, 0)
        # for rigid-closed. Here g is a complex flow-amplitude parameter.
        coeff = []
        for i, matched in ((1, False), (2, True)):
            q = 1.0 if matched else 0.0
            a = z[i] * (cs[i] + 1j * q * sn[i])  # p_in / g
            b = (1j * sn[i] + q * cs[i])          # U_in / g
            if abs(a) <= 1e-9 * z[i]:
                raise ArithmeticError("NUMERICALLY_UNRESOLVED:BRANCH_RESONANCE")
            coeff.append((a, b, q))
        yb, yc = (b / a for a, b, _ in coeff)
        yj = yb + yc
        denominator = 1j * sn[0] / z[0] + cs[0] * yj
        guard = abs(denominator) * z[0]
        if not (math.isfinite(guard) and guard > 1.0 / MAX_INTERNAL_CONDITION):
            raise ArithmeticError("NUMERICALLY_UNRESOLVED:INPUT_RESONANCE")
        pj = SOURCE / denominator
        ua_out = yj * pj
        pa_in = cs[0] * pj + 1j * z[0] * sn[0] * ua_out
        bterm = pj / coeff[0][0]
        cterm = pj / coeff[1][0]
        pp = [pa_in, pj, pj, z[1] * bterm, pj, z[2] * cterm]
        uu = [SOURCE, ua_out, coeff[0][1] * bterm, 0j,
              coeff[1][1] * cterm, cterm]
        watts = [power(p, u) for p, u in zip(pp, uu)]
        jp = max(abs(pp[1] - pp[2]), abs(pp[1] - pp[4])) / P_REF
        ju = abs(uu[1] - uu[2] - uu[4]) / U_REF
        pw = abs(watts[0] - watts[3] - watts[5]) / (0.5 * P_REF * U_REF)
        # Distal two-port equations, valid for both zero-flow and matched ends.
        tube = []
        for i in range(3):
            j = 2 * i
            pin = cs[i] * pp[j+1] + 1j * z[i] * sn[i] * uu[j+1]
            uin = 1j * sn[i] / z[i] * pp[j+1] + cs[i] * uu[j+1]
            tube.extend((abs(pp[j] - pin) / P_REF, abs(uu[j] - uin) / U_REF))
        residual = max(jp, ju, pw, *tube,
                       abs(uu[3]) / U_REF,
                       abs(pp[5] - z[2] * uu[5]) / P_REF)
        if not all(math.isfinite(v) for x in [*pp, *uu]
                   for v in (x.real, x.imag)) or not all(
                       math.isfinite(x) for x in [*watts, residual]
                   ) or residual > MAX_RESIDUAL:
            raise ArithmeticError("NUMERICALLY_UNRESOLVED:PHYSICAL_RESIDUAL")
        state_p.append([pack(v) for v in pp])
        state_u.append([pack(v) for v in uu])
        state_power.append([float(x) for x in watts])
        diagnostics.append({"physical_residual": float(residual),
                            "recursive_denom_scaled": float(guard)})
    return {
        "schema": "nr1a.research.only.response.v0", "status": "OK",
        "backend_id": EXPERIMENT_BACKEND, "port_ids": list(PORTS),
        "frequencies_hz": list(fs), "pressure_pa": state_p,
        "volume_flow_m3_s": state_u, "mean_power_w": state_power,
        "diagnostics": diagnostics,
    }


def observe(case: str) -> dict[str, Any]:
    bp = blueprint(case)
    if case == "M":
        try:
            prepare_branch3(deepcopy(bp))
        except Branch3Error as e:
            if (e.status, e.code) != ("UNSUPPORTED", "FROZEN_LOAD"):
                raise AssertionError("unexpected OG-4 refusal") from e
        else:
            raise AssertionError("OG-4 silently expanded its adopted capability")
        response = recursive_mouth_closed(case, list(FREQUENCIES))
        binding = {
            "source": "experiment-only", "backend_id": EXPERIMENT_BACKEND,
            "blueprint_research_digest": canonical_sha(bp),
        }
    else:
        prepared = prepare_branch3(deepcopy(bp))
        response = prepared.response(list(FREQUENCIES))
        binding = {
            "source": "adopted-core", "backend_id": response["backend_id"],
            "blueprint_digest": prepared.blueprint_digest,
            "preparation_digest": prepared.preparation_digest,
            "observation_digest": response["observation_digest"],
        }
    derived = []
    for idx, f in enumerate(FREQUENCIES):
        pp = [unpack(value) for value in response["pressure_pa"][idx]]
        uu = [unpack(value) for value in response["volume_flow_m3_s"][idx]]
        if abs(uu[0]) <= 1e-30 or abs(pp[0]) <= 1e-12:
            raise ArithmeticError("NUMERICALLY_UNRESOLVED:TRANSFER_NORMALIZATION")
        derived.append({
            "frequency_hz": f,
            "input_impedance_pa_s_m3": pack(pp[0] / uu[0]),
            "transfer_p_B_out_over_p_A_in": pack(pp[3] / pp[0]),
            "transfer_p_C_out_over_p_A_in": pack(pp[5] / pp[0]),
        })
    return {"case": case, "physical_blueprint": bp,
            "physical_blueprint_research_digest": canonical_sha(bp),
            "binding": binding, "response": response,
            "derived_observables": derived}


def load_oracle() -> dict[str, Any]:
    data = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    if (data["schema"] != "nr1a.wolfram.global12.oracle.v0" or
            data["status"] != "CANDIDATE_NOT_FROZEN" or
            data["port_ids"] != PORTS or data["frequencies_hz"] != FREQUENCIES or
            len(data["records"]) != 24):
        raise AssertionError("unrecognized/unfrozen Wolfram oracle")
    names = [(r["case"], r["frequency_hz"]) for r in data["records"]]
    if names != [(n, f) for n in "NOM" for f in FREQUENCIES]:
        raise AssertionError("incorrect oracle case/frequency ordering")
    return data


def endpoint_error(obs: dict[str, Any], oracle_record: dict[str, Any], idx: int) -> float:
    r = obs["response"]
    if r["port_ids"] != PORTS or r["frequencies_hz"][idx] != oracle_record["frequency_hz"]:
        raise AssertionError("port/frequency binding mismatch")
    if not (len(r["pressure_pa"][idx]) == len(r["volume_flow_m3_s"][idx]) == 6):
        raise AssertionError("missing endpoint")
    errors = [
        abs(unpack(r[field][idx][j]) - complex(*oracle_record[field][j])) / norm
        for field, norm in (("pressure_pa", P_REF), ("volume_flow_m3_s", U_REF))
        for j in range(6)
    ]
    return max(errors)


def compare(observed: dict[str, dict[str, Any]]) -> dict[str, Any]:
    data = load_oracle()
    report: dict[str, Any] = {"per_case": {}, "total": 0, "status": "CANDIDATE_ONLY"}
    for case in "NOM":
        obs = observed[case]
        r = obs["response"]
        if r["status"] != "OK" or r["frequencies_hz"] != FREQUENCIES:
            raise AssertionError("invalid response envelope")
        peak = 0.0
        for idx, f in enumerate(FREQUENCIES):
            row = data["records"][list("NOM").index(case) * 8 + idx]
            err = endpoint_error(obs, row, idx)
            derived = obs["derived_observables"][idx]
            z = unpack(derived["input_impedance_pa_s_m3"])
            zref = complex(*row["input_impedance_pa_s_m3"])
            if abs(z - zref) / (P_REF / U_REF) > MAX_STATE:
                raise AssertionError(f"input impedance mismatch: {case}/{f}")
            pref = complex(*row["pressure_pa"][0])
            for idx_end, name in ((3, "B"), (5, "C")):
                transfer = unpack(derived[f"transfer_p_{name}_out_over_p_A_in"])
                transfer_ref = complex(*row["pressure_pa"][idx_end]) / pref
                if abs(transfer - transfer_ref) > MAX_STATE:
                    raise AssertionError(f"transfer mismatch: {case}/{f}/{name}")
            peak = max(peak, err)
            if not math.isfinite(err) or err > MAX_STATE:
                raise AssertionError(f"complex mismatch: {case}/{f}/{err}")
            for j in range(6):
                pw_error = abs(r["mean_power_w"][idx][j] - row["mean_power_w"][j])
                if pw_error / (0.5 * P_REF * U_REF) > MAX_POWER:
                    raise AssertionError(f"power mismatch: {case}/{f}/{j}")
            p = [unpack(v) for v in r["pressure_pa"][idx]]
            u = [unpack(v) for v in r["volume_flow_m3_s"][idx]]
            if (abs(p[1]-p[2])/P_REF > MAX_RESIDUAL or
                abs(p[1]-p[4])/P_REF > MAX_RESIDUAL or
                abs(u[1]-u[2]-u[4])/U_REF > MAX_RESIDUAL):
                raise AssertionError("junction law violated")
            closure = 5 if case == "N" else 3 if case == "M" else None
            if closure is not None and (abs(u[closure])/U_REF > MAX_RESIDUAL or
                                        abs(r["mean_power_w"][idx][closure]) /
                                            (0.5*P_REF*U_REF) > MAX_POWER):
                raise AssertionError("closed outlet leaks")
            if case == "O" and not (r["mean_power_w"][idx][3] > 0 and
                                    r["mean_power_w"][idx][5] > 0):
                raise AssertionError("matched outlet is non-passive")
            pin = r["mean_power_w"][idx][0]
            pout = r["mean_power_w"][idx][3] + r["mean_power_w"][idx][5]
            if abs(pin - pout) / (0.5 * P_REF * U_REF) > MAX_POWER:
                raise AssertionError("acoustic power balance mismatch")
            report["total"] += 1
        report["per_case"][case] = {"max_scaled_endpoint_error": peak,
                                    "backend_id": obs["binding"]["backend_id"]}
    if report["total"] != 24:
        raise AssertionError("incomplete experiment")
    return report


def execute() -> tuple[dict[str, Any], dict[str, Any]]:
    data = {case: observe(case) for case in "NOM"}
    return data, compare(data)


def git_head() -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def sha_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-head", type=str, required=True)
    args = parser.parse_args()
    head = git_head()
    if not args.expected_head or args.expected_head != head:
        raise SystemExit("REFUSED: exact Git HEAD mismatch")
    outputs, comparison = execute()
    outdir: Path = args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "nr1a.research.evidence.v0",
        "scientific_claim": "CANDIDATE_ONLY_NOT_ADOPTED",
        "exact_head": head,
        "oracle_sha256": sha_file(ORACLE_PATH),
        "oracle_source_sha256": sha_file(HERE / "wolfram" / "global12_oracle.wl"),
        "runner_sha256": sha_file(Path(__file__)),
        "cases": outputs, "comparison": comparison,
    }
    raw = json.dumps(result, sort_keys=True, allow_nan=False, indent=2) + "\n"
    filename = outdir / "nr1a-evidence.json"
    filename.write_text(raw, encoding="utf-8")
    (outdir / "nr1a-evidence.sha256").write_text(
        sha256(raw.encode("utf-8")).hexdigest() + "  nr1a-evidence.json\n",
        encoding="ascii")
    print(json.dumps({"exact_head": head, "cases": comparison["total"],
                      "per_case": comparison["per_case"],
                      "evidence_sha256": sha256(raw.encode()).hexdigest()}))


if __name__ == "__main__":
    main()
