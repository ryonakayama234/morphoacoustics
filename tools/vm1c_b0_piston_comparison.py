"""VM-1C: scientific S1 comparison, SA-2A flanged-piston vs native B0.

Research only, stacked on unmerged SA-2A branch. No new reference function
for the baffled piston, no time-domain boundary or voice-quality assertion.
Prospective experiment: docs/research/voice-metrology/VM1C_GATE_A.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import runpy
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "experiments/049_baffled_piston_sa2a/run.py"
BODY = ROOT / "experiments/028_task_field_morphology_transfer/frozen_reference.json"
REF_BLOB_SHA1 = "3e7439b426adfd3549586bb43210eec66242606c"
BODY_BLOB_SHA1 = "7810dfbb72cb6c41af007db6e9d51c58cad9a522"
RHO, C = 1.21, 343.0
KA_MAX = 0.8
U_IN = 1e-6
FREQUENCIES_HZ = (100.0, 300.0, 600.0, 1000.0, 1600.0, 2500.0)
CALIBRATION_RADII_M = (0.005, 0.010, 0.016)
MODEL_NAMES = ("ideal_piston", "B0_continuous", "B0_native_discrete")
SCHEMA = "voice-metrology/sa2a-vs-b0/vm1c"


def blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def verified_inputs() -> tuple[dict, dict]:
    if blob_sha1(REFERENCE.read_bytes()) != REF_BLOB_SHA1:
        raise ValueError("SA2A_REFERENCE_SHA_MISMATCH")
    if blob_sha1(BODY.read_bytes()) != BODY_BLOB_SHA1:
        raise ValueError("FROZEN_BODY_SHA_MISMATCH")
    j = json.loads(BODY.read_text(encoding="utf-8"))
    areas = j["M0"]["a_areas_m2"]
    m0_lengths = j["M0"]["section_lengths_m"]
    if len(areas) != 16 or len(m0_lengths) != 16 or any(
        not isinstance(x, (int, float)) or isinstance(x, bool) or
        not math.isfinite(x) or x <= 0 for x in areas
    ) or any(x != 0.010 for x in m0_lengths):
        raise ValueError("FROZEN_M0_INVALID")
    if not math.isclose(math.sqrt(areas[-1] / math.pi), 0.016, abs_tol=1e-14):
        raise ValueError("OUTLET_16MM_GUARD")
    # Reference's own independent disk-area oracle stays executed unchanged.
    sa2a = runpy.run_path(str(REFERENCE))
    if sa2a["RHO"] != RHO or sa2a["C"] != C or sa2a["X_MAX"] != KA_MAX:
        raise ValueError("SA2A_REFERENCE_CONSTANTS_MISMATCH")
    return j, sa2a


def git_revision() -> dict:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=ROOT, check=True, capture_output=True,
            text=True, timeout=10,
        ).stdout.strip()
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("DIRTY_EXECUTED_TREE")
    head = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    raw = git("cat-file", "-p", "HEAD")
    parents = [line[7:] for line in raw.splitlines() if line.startswith("parent ")]
    if len(head) != 40 or [line[5:] for line in raw.splitlines()
                            if line.startswith("tree ")] != [tree]:
        raise RuntimeError("UNVERIFIABLE_EXECUTED_GIT_TREE")
    paths = [
        "experiments/049_baffled_piston_sa2a/run.py",
        "experiments/028_task_field_morphology_transfer/frozen_reference.json",
        "tools/vm1c_b0_piston_comparison.py",
        "tests/test_vm1c_b0_piston_comparison.py",
        ".github/workflows/vm1c-b0-piston.yml",
    ]
    return {
        "head_sha": head, "git_tree_sha": tree, "raw_commit_parents": parents,
        "sha256_files": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                         for p in paths},
        "clean_tracked_checkout": True,
    }


def check_frequency(radius: float, frequency: float) -> float:
    if not all(isinstance(x, (float, int)) and not isinstance(x, bool)
               and math.isfinite(x) and x > 0 for x in (radius, frequency)):
        raise ValueError("INVALID_APERTURE_OR_FREQUENCY")
    x = 2 * math.pi * frequency * radius / C
    if x > KA_MAX + 1e-13:
        raise ValueError("UNSUPPORTED_KA")
    return x


def b0_impedance(radius: float, frequency: float, *, dt: float | None = None) -> complex:
    check_frequency(radius, frequency)
    area = math.pi * radius * radius
    mass = 8 * RHO * radius / (3 * math.pi * area)
    tau = 3 * math.pi * radius / (16 * C)
    resistance = mass / tau
    if dt is None:
        admittance = 1 / resistance - 1j / (2 * math.pi * frequency * mass)
    else:
        if not math.isfinite(dt) or dt <= 0 or frequency >= .5 / dt:
            raise ValueError("INVALID_NATIVE_CLOCK")
        admittance = 1 / resistance - 1j * dt / (
            2 * mass * math.tan(math.pi * frequency * dt)
        )
    return 1 / admittance


def port_matrix(areas: list[float], segment_length: float, frequency: float) -> np.ndarray:
    """Independent lossless two-port; none of VM-1B's implementation is imported."""
    if len(areas) != 16 or not math.isfinite(segment_length) or segment_length <= 0:
        raise ValueError("INVALID_MATRIX_GEOMETRY")
    if not math.isfinite(frequency) or frequency <= 0:
        raise ValueError("INVALID_MATRIX_FREQUENCY")
    total = np.eye(2, dtype=np.complex128)
    phi = 2 * math.pi * frequency * segment_length / C
    for area in areas:
        if not math.isfinite(area) or area <= 0:
            raise ValueError("INVALID_AREA")
        z = RHO * C / area
        t = np.array(
            [[math.cos(phi), 1j * z * math.sin(phi)],
             [1j * math.sin(phi) / z, math.cos(phi)]], dtype=np.complex128,
        )
        total = total @ t
    return total


def tube_load(total: np.ndarray, z_load: complex) -> dict:
    if not np.isfinite(z_load) or z_load.real < -1e-12:
        raise ValueError("INVALID_NONPASSIVE_BOUNDARY")
    aa, bb, cc, dd = total[0, 0], total[0, 1], total[1, 0], total[1, 1]
    denom = cc * z_load + dd
    if abs(denom) <= 1e-20:
        raise ValueError("UNRESOLVED_LOAD")
    hu = 1 / denom
    hpu = z_load * hu
    zin = (aa * z_load + bb) / denom
    pin = 0.5 * (zin * U_IN * U_IN).real
    pout = 0.5 * (z_load * abs(hu * U_IN)**2).real
    power_ref = max(abs(pin), abs(pout), 1e-30)
    power_error = abs(pin-pout)/power_ref
    if pin < -1e-15 or pout < -1e-15:
        raise ValueError("NEGATIVE_PHYSICAL_POWER")
    return {"HpU": hpu, "HU": hu, "Zin": zin,
            "inlet_power_w": pin, "mouth_power_w": pout,
            "power_balance_relative_error": power_error}


def cnumber(x: complex) -> dict:
    if not np.isfinite(x):
        raise ValueError("NONFINITE_COMPLEX_REPORT")
    return {"real": float(x.real), "imag": float(x.imag)}


def run() -> dict:
    bodies, oracle = verified_inputs()
    provenance = git_revision()
    x_grid = np.array((0.02, 0.10, 0.25, 0.55, 0.80), dtype=float)
    analytic = oracle["_normalized_nonnegative"](x_grid)
    rayleigh = oracle["normalized_overlap_oracle"](x_grid)
    reference_abs_error = float(np.max(abs(analytic - rayleigh)))
    asym_f = 0.001 * C / (2 * math.pi * 0.010)
    asym_ref = complex(oracle["radiation_impedance"](asym_f, 0.010))
    asym_approx = b0_impedance(.010, asym_f)
    asym_zc = RHO * C / (math.pi * .010**2)
    asym_norm_abs_error = abs(asym_ref - asym_approx)/asym_zc
    ref_pass = reference_abs_error <= 2e-9 and np.all(analytic.real >= -1e-12)
    asym_pass = asym_norm_abs_error <= 2e-6

    calibrations = []
    refused = []
    for radius in CALIBRATION_RADII_M:
        for f in FREQUENCIES_HZ:
            try:
                ka = check_frequency(radius, f)
            except ValueError as exc:
                if str(exc) != "UNSUPPORTED_KA":
                    raise
                refused.append({"radius_m": radius, "frequency_hz": f,
                                "reason": "UNSUPPORTED_KA"})
                continue
            ideal = complex(oracle["radiation_impedance"](f, radius))
            cont = b0_impedance(radius, f)
            # Native n=2 time tick of M0 10mm: demonstrative clock only for
            # this isolated radius control, not a physical aperture time scale.
            disc = b0_impedance(radius, f, dt=.010 / (2*C))
            zc = RHO*C / (math.pi*radius**2)
            if min(ideal.real, cont.real, disc.real) < -1e-12:
                raise ValueError("RADIATION_PASSIVITY_VIOLATION")
            calibrations.append({
                "radius_m": radius, "frequency_hz": f, "ka": ka, "Zc_pa_s_m3": zc,
                "ideal_piston": cnumber(ideal),
                "B0_continuous": cnumber(cont), "B0_native_discrete": cnumber(disc),
                "model_complex_relative_error": abs(cont-ideal)/abs(ideal),
                "native_timestep_complex_relative_error": abs(disc-cont)/abs(cont),
                "phase_delta_B0_minus_piston_rad": float(np.angle(cont/ideal)),
                "normalized_exact": cnumber(ideal/zc),
                "normalized_B0": cnumber(cont/zc),
            })

    areas = [float(a) for a in bodies["M0"]["a_areas_m2"]]
    outlet_radius = math.sqrt(areas[-1] / math.pi)
    cases = {}
    selectivity = []
    all_power_ok = True
    for body, length in (("M0", .010), ("M1", .011)):
        cases[body] = []
        for f in FREQUENCIES_HZ:
            ka = check_frequency(outlet_radius, f)
            model_z = {
                "ideal_piston": complex(oracle["radiation_impedance"](f, outlet_radius)),
                "B0_continuous": b0_impedance(outlet_radius, f),
                "B0_native_discrete": b0_impedance(outlet_radius, f, dt=length/(2*C)),
            }
            total = port_matrix(areas, length, f)
            for name, z in model_z.items():
                trace = tube_load(total, z)
                all_power_ok &= trace["power_balance_relative_error"] <= 1e-8
                cases[body].append({
                    "body": body, "frequency_hz": f, "ka": ka, "law": name,
                    "lip_Z": cnumber(z),
                    "HpU": cnumber(trace["HpU"]), "HU": cnumber(trace["HU"]),
                    "Zin": cnumber(trace["Zin"]),
                    "inlet_power_w": trace["inlet_power_w"],
                    "mouth_power_w": trace["mouth_power_w"],
                    "power_balance_relative_error": trace["power_balance_relative_error"],
                })
        for law in MODEL_NAMES:
            p100 = next(x for x in cases[body] if x["law"] == law and x["frequency_hz"] == 100)
            p600 = next(x for x in cases[body] if x["law"] == law and x["frequency_hz"] == 600)
            h100 = complex(**{"real": p100["HpU"]["real"], "imag": p100["HpU"]["imag"]})
            h600 = complex(**{"real": p600["HpU"]["real"], "imag": p600["HpU"]["imag"]})
            selectivity.append({
                "body": body, "law": law,
                "H600_over_H100_db": 20 * math.log10(abs(h600)/abs(h100)),
                "metric": "mouth port HpU per equal ideal inlet flow; not audio",
            })
    wrong_boundary = b0_impedance(outlet_radius, 600) != complex(
        oracle["radiation_impedance"](600, outlet_radius)
    )
    gates = {
        "analytic_baffled_oracle": bool(ref_pass),
        "low_ka_asymptote": bool(asym_pass),
        "correctly_typed_passive_power": bool(all_power_ok),
        "wrong_boundary_detected": bool(wrong_boundary),
    }
    return {
        "schema": SCHEMA, "scope": "RESEARCH_ONLY",
        "research_verdict": ("SA2A_IDEAL_PISTON_COMPARISON_MEASURED"
                             if all(gates.values()) else "REFERENCE_OR_POWER_GATE_FAILED"),
        "gates_pass": all(gates.values()),
        "real_biological_radiation": "INDETERMINATE_REAL_RADIATION",
        "voice_quality": "VOICE_NO_GO_UNCHANGED",
        "creator_listening_requested": False,
        "source": "unmodified-SA2A-analytical-oracle-on-unmerged-research-branch",
        "underlying_sa2a_git_blob_sha1": REF_BLOB_SHA1,
        "frozen_body_git_blob_sha1": BODY_BLOB_SHA1,
        "provenance": provenance,
        "air": {"rho_kg_m3": RHO, "speed_m_s": C},
        "n2_native_clock": "dt=section_length/(2c)",
        "limiting_ka": KA_MAX,
        "independent_oracle_max_normalized_abs_error": reference_abs_error,
        "B0_low_ka_max_normalized_abs_error": asym_norm_abs_error,
        "gates": gates, "calibrations": calibrations,
        "refused_calibration_points": refused,
        "M0_M1_loaded_cases": cases, "port_selectivity": selectivity,
        "limitations": [
            "ideal infinite-rigid-baffle circular piston, not actual human or creature mouth",
            "prescribed input harmonic volume flow, not physically self-oscillating vocal tissue",
            "steady-state 1D lossless duct, not new causal time-domain termination",
            "no wall compliance/loss or material model",
            "no listener/receiver audio, acoustically plausible quality not assessed",
            "B0 approximation compared only within declared ka <= 0.8",
            "experiment stacked on SA2A Draft #172, no Core/main adoption",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out
    result = run()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+"\n",
                   encoding="utf-8")
    print("VM-1C", result["research_verdict"], out)
    for p in result["calibrations"]:
        if p["radius_m"] == 0.016:
            print("RADIATION_MODEL_DELTA", "radius_m", p["radius_m"],
                  "frequency_hz", p["frequency_hz"],
                  "B0_vs_piston_rel_complex_err", p["model_complex_relative_error"],
                  "B0_discretization_rel_complex_err", p["native_timestep_complex_relative_error"],
                  "phase_delta_rad", p["phase_delta_B0_minus_piston_rad"])
    for s in result["port_selectivity"]:
        print(s["body"], s["law"], "H600/H100 dB", s["H600_over_H100_db"])
    if not result["gates_pass"]:
        raise SystemExit("VM1C_GATE_FAILED")


if __name__ == "__main__":
    main()
