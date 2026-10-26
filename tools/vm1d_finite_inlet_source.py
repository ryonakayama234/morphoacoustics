"""VM-1D: bounded frequency-domain passive source/tract load ablation.

This is NOT laryngeal self-oscillation, listener audio, or a new Core API.
Frozen protocol: docs/research/voice-metrology/VM1D_GATE_A.md.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
import math
import os
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "experiments/028_task_field_morphology_transfer/frozen_reference.json"
BODY_BLOB_SHA1 = "7810dfbb72cb6c41af007db6e9d51c58cad9a522"
RHO = 1.21
SPEED = 343.0
FREQUENCIES = (100.0, 600.0, 2500.0)
RESISTANCE_MULTIPLIERS = (0.1, 1.0, 10.0)
P_DRIVE = 1.0
IDEAL_FLOW = 1e-6
SCHEMA = "vm1d.passive-finite-source.v1"


def positive(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError("INVALID_" + name)
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("INVALID_" + name)
    return value


def fixture() -> tuple[dict[str, tuple[float, np.ndarray]], str]:
    raw = FROZEN.read_bytes()
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != BODY_BLOB_SHA1:
        raise ValueError("FROZEN_BODY_BLOB_MISMATCH")
    body = json.loads(raw)["M0"]
    lengths = body["section_lengths_m"]
    areas = body["a_areas_m2"]
    if (len(lengths) != 16 or len(areas) != 16
            or any(type(v) not in (int, float) or v != 0.01 for v in lengths)):
        raise ValueError("FROZEN_REST_GEOMETRY_INVALID")
    vals = np.array([positive("AREA", x) for x in areas], dtype=float)
    # This is the explicit M1 geometry rule used in VM-1B, not a
    # new anatomical revision read from the frozen fixture.
    return {"M0": (0.010, vals), "M1": (0.011, vals.copy())}, sha256(raw).hexdigest()


def cascade(areas: np.ndarray, section_length_m: float, f_hz: float) -> np.ndarray:
    positive("LENGTH", section_length_m)
    positive("FREQUENCY", f_hz)
    if not isinstance(areas, np.ndarray) or areas.ndim != 1 or len(areas) != 16:
        raise ValueError("INVALID_SECTIONS")
    if not np.isfinite(areas).all() or np.any(areas <= 0):
        raise ValueError("INVALID_AREA")
    k_l = 2 * math.pi * f_hz * section_length_m / SPEED
    co, si = math.cos(k_l), math.sin(k_l)
    matrix = np.eye(2, dtype=np.complex128)
    for area in areas:
        zc = RHO * SPEED / float(area)
        m = np.array([[co, 1j * zc * si], [1j * si / zc, co]],
                     dtype=np.complex128)
        matrix = matrix @ m
    return matrix


def b0_load(area_m2: float, f_hz: float) -> complex:
    positive("AREA", area_m2)
    positive("FREQUENCY", f_hz)
    radius = math.sqrt(area_m2 / math.pi)
    inertance = 8 * RHO * radius / (3 * math.pi * area_m2)
    resistance = inertance / (3 * math.pi * radius / (16 * SPEED))
    # Time convention exp(+i omega t); shunt resistor || inertance.
    admittance = complex(1 / resistance, -1 / (2 * math.pi * f_hz * inertance))
    return 1 / admittance


def average_power(p: complex, u: complex) -> float:
    return 0.5 * (p * u.conjugate()).real


def power_residual(p_in: complex, u_in: complex, p_out: complex,
                   u_out: complex, p_drive: complex | None = None,
                   source_r: float = 0.0) -> dict[str, float | bool]:
    p_in_w = average_power(p_in, u_in)
    p_out_w = average_power(p_out, u_out)
    source_loss_w = 0.5 * source_r * abs(u_in) ** 2
    drive_w = average_power(p_drive, u_in) if p_drive is not None else None
    residual_duct_w = p_in_w - p_out_w
    residual_source_w = (drive_w - p_in_w - source_loss_w
                         if drive_w is not None else 0.0)
    denom = max(abs(p_in_w), abs(p_out_w), abs(source_loss_w),
                abs(drive_w) if drive_w is not None else 0, 1e-25)
    relative = max(abs(residual_duct_w), abs(residual_source_w)) / denom
    valid = (all(math.isfinite(v) for v in
                 (p_in_w, p_out_w, source_loss_w, relative))
             and p_in_w > 0 and p_out_w > 0
             and (drive_w is None or drive_w > 0)
             and source_loss_w >= 0 and relative <= 1e-9)
    return {
        "inlet_w": p_in_w, "mouth_w": p_out_w,
        "source_resistor_w": source_loss_w,
        "drive_w": drive_w, "duct_residual_w": residual_duct_w,
        "source_residual_w": residual_source_w,
        "relative_residual": relative, "pass": bool(valid),
    }


def drive(matrix: np.ndarray, load: complex, *, flow: float | None = None,
          p_drive: float | None = None, source_r: float | None = None) -> dict:
    if not np.isfinite(matrix).all() or matrix.shape != (2, 2):
        raise ValueError("INVALID_MATRIX")
    if not math.isfinite(load.real) or not math.isfinite(load.imag) or load.real <= 0:
        raise ValueError("INVALID_LOAD")
    a, b, c, d = matrix.flat
    q = c * load + d
    z = a * load + b
    if flow is not None:
        if p_drive is not None or source_r is not None:
            raise ValueError("MIXED_DRIVE_BOUNDARY")
        flow = positive("FLOW", flow)
        if abs(q) < 1e-25:
            raise ArithmeticError("SINGULAR_DUCT")
        u_l = flow / q
        p_src = None
        r = 0.0
    else:
        if p_drive is None or source_r is None:
            raise ValueError("MISSING_SOURCE_BOUNDARY")
        p_src = positive("SOURCE_PRESSURE", p_drive)
        r = positive("SOURCE_RESISTANCE", source_r)
        divisor = z + r * q
        if abs(divisor) < 1e-25:
            raise ArithmeticError("SINGULAR_SOURCE_DUCT")
        u_l = p_src / divisor
    p_l = load * u_l
    p_in, u_in = z * u_l, q * u_l
    if not all(np.isfinite(v) for v in (p_l, u_l, p_in, u_in)):
        raise ArithmeticError("NONFINITE_PORT")
    ledger = power_residual(p_in, u_in, p_l, u_l, p_src, r)
    if not ledger["pass"]:
        raise ArithmeticError("NONCONSERVATIVE_LOADED_NETWORK")
    return {"p_in": p_in, "U_in": u_in, "p_mouth": p_l,
            "U_mouth": u_l, "Zin": p_in / u_in,
            "power": ledger}


def number(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def provenance() -> dict:
    hashes = {}
    for name in ("tools/vm1d_finite_inlet_source.py",
                 "tests/test_vm1d_finite_inlet_source.py",
                 ".github/workflows/vm1d-finite-inlet.yml"):
        file = ROOT / name
        hashes[name] = sha256(file.read_bytes()).hexdigest() if file.is_file() else "MISSING"
    result = {"implementation_sha256": hashes, "verified": False,
              "executed_checkout_sha": None, "commit_parents": [],
              "note": "Git execution identity unavailable"}
    try:
        def git(*args: str) -> str:
            return subprocess.run(["git", *args], cwd=ROOT, check=True,
                                  capture_output=True, text=True, timeout=5).stdout.strip()
        head = git("rev-parse", "HEAD")
        raw = git("cat-file", "-p", "HEAD")
        parents = [ln[7:] for ln in raw.splitlines() if ln.startswith("parent ")]
        clean = not git("status", "--porcelain=v1", "--untracked-files=no")
        ci_sha = os.environ.get("GITHUB_SHA")
        result.update(executed_checkout_sha=head, commit_parents=parents,
                      verified=(len(head) == 40 and clean and
                                (not ci_sha or ci_sha == head) and
                                all(len(p) == 40 for p in parents) and
                                "MISSING" not in hashes.values()),
                      note="actual checked-out Git commit and tracked implementation hashes")
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    return result


def uniform_oracle() -> dict:
    errors = []
    # Independent analytic closed form, no B0 or matrix inverse.
    area = 2.0e-4
    zc = RHO * SPEED / area
    areas = np.full(16, area)
    for f in FREQUENCIES:
        matrix = cascade(areas, 0.01, f)
        for mult in RESISTANCE_MULTIPLIERS:
            result = drive(matrix, zc + 0j, p_drive=P_DRIVE,
                           source_r=zc * mult)
            observed = result["p_mouth"] / P_DRIVE
            expected = (zc / (zc + mult * zc) *
                        np.exp(-1j * 2 * math.pi * f * 0.16 / SPEED))
            errors.append(abs(observed - expected) / abs(expected))
    return {"max_complex_relative_error": float(max(errors)),
            "pass": bool(max(errors) <= 1e-10)}


def negative_controls() -> dict:
    matrix = cascade(np.full(16, 2e-4), .01, 100.0)
    conditions = {
        "negative_source_R": lambda: drive(matrix, 1e6+0j, p_drive=1.0, source_r=-1.0),
        "zero_source_pressure": lambda: drive(matrix, 1e6+0j, p_drive=0.0, source_r=1e6),
        "nonfinite_pressure": lambda: drive(matrix, 1e6+0j, p_drive=float("nan"), source_r=1e6),
        "zero_inlet_flow": lambda: drive(matrix, 1e6+0j, flow=0.0),
        "bad_area": lambda: cascade(np.full(16, -0.1), .01, 100.0),
        "nan_frequency": lambda: cascade(np.full(16, 2e-4), .01, float("nan")),
    }
    caught = {}
    for name, fn in conditions.items():
        try:
            fn()
        except ValueError:
            caught[name] = True
        else:
            caught[name] = False
    # A falsified source input cannot have identical accounted power.
    good = drive(matrix, 1e6+0j, p_drive=1.0, source_r=1e6)
    bad = power_residual(good["p_in"], good["U_in"], good["p_mouth"],
                         good["U_mouth"], 1.1+0j, 1e6)
    caught["tampered_source_power_rejected"] = not bad["pass"]
    return {"checks": caught, "pass": all(caught.values())}


def run() -> dict:
    bodies, body_hash = fixture()
    oracle = uniform_oracle()
    neg = negative_controls()
    cases = {}
    max_det = 0.0
    max_power = 0.0
    sensitivity = {}
    for label, (length, areas) in bodies.items():
        fixed = {}
        for f in FREQUENCIES:
            m = cascade(areas, length, f)
            max_det = max(max_det, abs(np.linalg.det(m) - 1))
            load = b0_load(float(areas[-1]), f)
            ideal = drive(m, load, flow=IDEAL_FLOW)
            zs = RHO * SPEED / float(areas[0])
            finite = {}
            max_power = max(max_power, ideal["power"]["relative_residual"])
            for mult in RESISTANCE_MULTIPLIERS:
                d = drive(m, load, p_drive=P_DRIVE, source_r=mult * zs)
                max_power = max(max_power, d["power"]["relative_residual"])
                finite[str(mult)] = {
                    "p_mouth_per_drive": number(d["p_mouth"] / P_DRIVE),
                    "U_in_m3_s": number(d["U_in"]),
                    "Zin_pa_s_m3": number(d["Zin"]),
                    "source_resistance_pa_s_m3": mult * zs,
                    "power": d["power"],
                }
            fixed[str(int(f))] = {
                "frequency_hz": f,
                "ideal_prescribed_flow": {
                    "HpU_pa_s_m3": number(ideal["p_mouth"] / IDEAL_FLOW),
                    "Zin_pa_s_m3": number(ideal["Zin"]),
                    "power": ideal["power"],
                },
                "finite_source": finite,
                "b0_continuous_load_pa_s_m3": number(load),
            }
        def as_complex(j: dict) -> complex:
            return complex(j["real"], j["imag"])
        ideal_ratio = 20 * math.log10(
            abs(as_complex(fixed["600"]["ideal_prescribed_flow"]["HpU_pa_s_m3"])) /
            abs(as_complex(fixed["100"]["ideal_prescribed_flow"]["HpU_pa_s_m3"])))
        ratios = {}
        for mult in RESISTANCE_MULTIPLIERS:
            key = str(mult)
            ratio = 20 * math.log10(
                abs(as_complex(fixed["600"]["finite_source"][key]["p_mouth_per_drive"])) /
                abs(as_complex(fixed["100"]["finite_source"][key]["p_mouth_per_drive"])))
            ratios[key] = {"H600_H100_db": ratio,
                           "delta_vs_ideal_flow_db": ratio - ideal_ratio,
                           "exceeds_preregistered_0p1_db_sensitivity":
                           abs(ratio - ideal_ratio) > .1}
        cases[label] = {"section_length_m": length,
                        "areas_m2": areas.tolist(), "frequency_cases": fixed}
        sensitivity[label] = {"ideal_flow_H600_H100_db": ideal_ratio,
                              "finite_pressure_source": ratios}
    p = provenance()
    math_pass = (oracle["pass"] and neg["pass"] and
                 max_det <= 1e-10 and max_power <= 1e-9)
    return {
        "schema": SCHEMA, "scope": "RESEARCH_ONLY",
        "git_fixture_blob_sha1": BODY_BLOB_SHA1, "fixture_sha256": body_hash,
        "model": "16-section rigid lossless 1D, continuous B0 shunt termination",
        "stimuli": {"ideal_flow_m3_s": IDEAL_FLOW, "pressure_drive_pa": P_DRIVE,
                    "frequency_hz": FREQUENCIES,
                    "source_R_over_Zcin": RESISTANCE_MULTIPLIERS},
        "provenance": p,
        "uniform_matched_tube_oracle": oracle,
        "negative_controls": neg,
        "max_abs_matrix_det_minus_one": float(max_det),
        "max_relative_power_residual": float(max_power),
        "g0_g1_numerical_pass": bool(math_pass),
        "g0_evidence_pass": bool(p["verified"]),
        "research_verdict": ("G0_G1_PASS_SOURCE_LOADING_SENSITIVITY"
                             if math_pass and p["verified"] else
                             "EVIDENCE_INCOMPLETE" if math_pass else
                             "NUMERICALLY_UNRESOLVED"),
        "source_loading_sensitivity": sensitivity, "raw_cases": cases,
        "g2_biological_physics": "INDETERMINATE_PHYSIOLOGY",
        "g3": "NOT_RUN_NO_SELF_OSCILLATOR", "g4": "VOICE_NO_GO_UNCHANGED",
        "note": "Mouth port only; neither receiver pressure nor human/animal phonation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    path = parser.parse_args().out
    try:
        report = run()
    except Exception as exc:
        report = {"schema": SCHEMA, "research_verdict": "NUMERICALLY_UNRESOLVED",
                  "failure_type": type(exc).__name__, "failure": str(exc)}
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        report = {"schema": SCHEMA, "research_verdict": "NUMERICALLY_UNRESOLVED",
                  "failure_type": "REPORT_SERIALIZATION_FAILED",
                  "failure": str(exc), "provenance": provenance()}
        serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    path.write_text(serialized + "\n", encoding="utf-8")
    print("VM-1D:", report["research_verdict"])
    if "source_loading_sensitivity" in report:
        print("VM1D_PORT_SELECTIVITY_SI_CALIBRATED",
              json.dumps(report["source_loading_sensitivity"],
                         sort_keys=True, allow_nan=False))
        print("VM1D_NUMERICAL_GATES",
              json.dumps({"uniform_oracle": report["uniform_matched_tube_oracle"],
                          "max_matrix_det_error": report["max_abs_matrix_det_minus_one"],
                          "max_relative_power_residual": report["max_relative_power_residual"],
                          "negative_controls": report["negative_controls"],
                          "executed_sha": report["provenance"]["executed_checkout_sha"]},
                         sort_keys=True, allow_nan=False))
    if report["research_verdict"] != "G0_G1_PASS_SOURCE_LOADING_SENSITIVITY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
