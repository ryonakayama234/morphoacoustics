"""VM-1B: research-only independent loaded frequency-domain two-port reference.

Implements analytic transmission matrices and exact phasor interpretation of
the *declared* B0 discrete-time shunt R+inertance boundary. This checks the
native waveguide numerics; it is NOT validation of a biological radiation law.
Gate A: docs/research/voice-metrology/VM1B_GATE_A.md.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
from math import ceil, cos, isfinite, pi, sin, sqrt, tan
from pathlib import Path

import numpy as np

from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics_waveguide import PassiveWaveguideConfig, PassiveWaveguideSession

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "experiments/028_task_field_morphology_transfer/frozen_reference.json"
BLOB_SHA1 = "7810dfbb72cb6c41af007db6e9d51c58cad9a522"
BASE_MAIN_SHA = "e05e3274ad69bfb9202816049f6661a18ba39ec0"
SOURCE_VOLUME_M3 = 1e-13
RHO = 1.21
C = 343.0
TARGETS_HZ = (100.0, 600.0)
PORTS = ("HpU", "Zin", "HU")
SCHEMA = "voice-metrology-loaded-transfer/vm1b"


def load_bodies() -> tuple[dict[str, Tract1DGeometry], str]:
    data = FROZEN.read_bytes()
    digest = sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()
    if digest != BLOB_SHA1:
        raise ValueError("FROZEN_BODY_BLOB_MISMATCH")
    j = json.loads(data)
    m0 = j["M0"]
    areas = m0["a_areas_m2"]
    if (len(areas) != 16 or len(m0["section_lengths_m"]) != 16
        or any(v != 0.01 for v in m0["section_lengths_m"])
        or not all(type(a) in (int, float) and isfinite(a) and a > 0 for a in areas)):
        raise ValueError("INVALID_FROZEN_MORPHOLOGY")
    geom = {
        name: Tract1DGeometry(
            "oracle-" + name,
            tuple(TubeSection(length, float(area)) for area in areas),
        )
        for name, length in (("M0", 0.010), ("M1", 0.011))
    }
    return geom, sha256(data).hexdigest()


def b0_shunt_parameters(area_m2: float) -> tuple[float, float]:
    if not isfinite(area_m2) or area_m2 <= 0:
        raise ValueError("INVALID_OUTLET_AREA")
    radius = sqrt(area_m2 / pi)
    inertance = 8.0 * RHO * radius / (3.0 * pi * area_m2)
    tau = 3.0 * pi * radius / (16.0 * C)
    resistance = inertance / tau
    return resistance, inertance


def terminal_admittance(
    area_m2: float, f_hz: float, dt_s: float, termination: str,
    *, continuum: bool = False
) -> complex:
    """Independent discrete phasor derivation, not a call to B0 waveguide."""
    if (not all(isfinite(x) and x > 0 for x in (area_m2, f_hz, dt_s))
        or f_hz >= 0.5 / dt_s):
        raise ValueError("FREQUENCY_OUTSIDE_POSITIVE_RESOLVED_BAND")
    zc = RHO * C / area_m2
    if termination == "matched":
        return complex(1.0 / zc)
    if termination != "b0":
        raise ValueError("UNSUPPORTED_TERMINATION")
    resistance, inertance = b0_shunt_parameters(area_m2)
    if continuum:
        return complex(1.0 / resistance, -1.0 / (2 * pi * f_hz * inertance))
    # q[n]-q[n-1] = dt*p[n]/m;
    # U[n] = p[n]/R + (q[n]+q[n-1])/2.
    # Under phasor z = exp(+i*w*dt), Y = 1/R + dt/(2m)*(1+z^-1)/(1-z^-1).
    return complex(1.0 / resistance, -dt_s / (2.0 * inertance * tan(pi * f_hz * dt_s)))


def reference_transfer(
    geometry: Tract1DGeometry, f_hz: float, *,
    termination: str, cells_per_section: int = 2, continuum: bool = False
) -> dict[str, complex]:
    """Independent distributed-duct 2x2 matrix with explicit *loaded* end."""
    if type(cells_per_section) is not int or cells_per_section not in (2, 4, 8):
        raise ValueError("UNSUPPORTED_CELL_COUNT")
    sections = geometry.sections
    if not sections:
        raise ValueError("EMPTY_GEOMETRY")
    if (not isfinite(f_hz) or f_hz <= 0
        or any(not isfinite(s.length_m) or not isfinite(s.area_m2)
               or s.length_m <= 0 or s.area_m2 <= 0 for s in sections)):
        raise ValueError("INVALID_FREQUENCY_OR_GEOMETRY")
    first = sections[0].length_m
    if any(abs(s.length_m - first) > 1e-14 for s in sections):
        raise ValueError("UNSUPPORTED_UNEQUAL_SECTION_LENGTHS")
    dt = first / (C * cells_per_section)
    admittance = terminal_admittance(
        sections[-1].area_m2, f_hz, dt, termination, continuum=continuum
    )
    total = np.eye(2, dtype=np.complex128)
    for section in sections:
        phi = 2.0 * pi * f_hz * section.length_m / C
        z = RHO * C / section.area_m2
        piece = np.array(
            [[cos(phi), 1j * z * sin(phi)],
             [1j * sin(phi) / z, cos(phi)]], dtype=np.complex128
        )
        total = total @ piece
    aa, bb, cc, dd = total[0, 0], total[0, 1], total[1, 0], total[1, 1]
    divisor = cc + dd * admittance
    if not np.isfinite(divisor) or abs(divisor) <= 1e-30:
        raise ArithmeticError("UNRESOLVED_LOADED_TRANSFER")
    return {
        "HpU": 1.0 / divisor,
        "Zin": (aa + bb * admittance) / divisor,
        "HU": admittance / divisor,
    }


def impulse_trace(
    config: PassiveWaveguideConfig, duration_s: float, *,
    amplitude_scale: float = 1.0
) -> dict:
    if not isfinite(duration_s) or duration_s <= 0:
        raise ValueError("INVALID_DURATION")
    if not isfinite(amplitude_scale) or amplitude_scale < 0:
        raise ValueError("INVALID_PULSE_SCALE")
    sample_count = int(ceil(duration_s * config.physics_clock_hz))
    if sample_count < 40:
        raise ValueError("INSUFFICIENT_NATIVE_SAMPLES")
    flow = np.zeros(sample_count, dtype=np.float64)
    flow[0] = SOURCE_VOLUME_M3 * config.physics_clock_hz * amplitude_scale
    pressure_in = np.empty(sample_count, dtype=np.float64)
    pressure_out = np.empty(sample_count, dtype=np.float64)
    flow_out = np.empty(sample_count, dtype=np.float64)
    max_scaled_energy_residual = 0.0
    session = PassiveWaveguideSession(config)
    prev_energy = 0.0
    for k, u in enumerate(flow):
        s = session.step(float(u))
        pressure_in[k] = s.source_pressure_pa
        pressure_out[k] = s.mouth_pressure_pa
        flow_out[k] = s.mouth_flow_m3_s
        energy = s.duct_energy_j + s.radiation_energy_j
        tol = max(
            1e-9 * max(abs(s.delta_stored_energy_j), abs(s.source_work_j),
                       s.outlet_dissipation_j, 1e-20),
            1e-12 * max(prev_energy, energy, 1e-20),
        )
        max_scaled_energy_residual = max(
            max_scaled_energy_residual, abs(s.energy_residual_j) / tol
        )
        prev_energy = energy
    if max_scaled_energy_residual > 1 or not all(
        np.isfinite(x).all() for x in (pressure_in, pressure_out, flow_out)
    ):
        raise ArithmeticError("NATIVE_ENERGY_OR_FINITE_GATE_FAILED")
    return {
        "U_in": flow, "p_in": pressure_in, "p_mouth": pressure_out,
        "U_mouth": flow_out, "energy_error_to_tolerance_max": max_scaled_energy_residual,
    }


def observed_transfer(
    config: PassiveWaveguideConfig, trace: dict, targets_hz: tuple[float, ...] = TARGETS_HZ
) -> list[dict]:
    u = trace["U_in"]
    freqs = np.fft.rfftfreq(len(u), d=config.timestep_s)
    uhat = np.fft.rfft(u)
    p_in = np.fft.rfft(trace["p_in"])
    p_out = np.fft.rfft(trace["p_mouth"])
    u_out = np.fft.rfft(trace["U_mouth"])
    points = []
    for requested in targets_hz:
        if not isfinite(requested) or requested <= 0:
            raise ValueError("INVALID_TARGET_FREQUENCY")
        idx = int(np.argmin(abs(freqs - requested)))
        if idx <= 0 or idx >= len(freqs) - 1 or abs(uhat[idx]) <= 1e-30:
            raise ValueError("UNRESOLVED_IMPULSE_TARGET")
        vals = {
            "HpU": p_out[idx] / uhat[idx],
            "Zin": p_in[idx] / uhat[idx],
            "HU": u_out[idx] / uhat[idx],
        }
        points.append({
            "requested_hz": requested, "actual_hz": float(freqs[idx]), "bin": idx,
            "bin_offset_hz": float(freqs[idx] - requested), "complex": vals,
        })
    return points


def relative_errors(expected: dict, actual: dict) -> dict[str, float]:
    ans = {}
    for name in PORTS:
        reference = expected[name]
        measured = actual[name]
        if not (np.isfinite(reference) and np.isfinite(measured)) or abs(reference) <= 1e-30:
            raise ArithmeticError("UNRESOLVED_COMPLEX_REFERENCE")
        ans[name] = float(abs(measured - reference) / abs(reference))
    return ans


def complex_json(x: complex) -> dict:
    if not np.isfinite(x):
        raise ArithmeticError("NONFINITE_COMPLEX_VALUE")
    return {"real": float(x.real), "imag": float(x.imag)}


def measure_case(
    body_name: str, geometry: Tract1DGeometry, termination: str, duration_s: float,
) -> dict:
    cfg = PassiveWaveguideConfig(geometry, cells_per_section=2, termination=termination)
    trace = impulse_trace(cfg, duration_s)
    pairs = observed_transfer(cfg, trace)
    max_error = 0.0
    checks = []
    for point in pairs:
        ref = reference_transfer(
            geometry, point["actual_hz"], termination=termination
        )
        errors = relative_errors(ref, point["complex"])
        max_error = max(max_error, *errors.values())
        checks.append({
            "frequency": {k: point[k] for k in
                          ("requested_hz", "actual_hz", "bin", "bin_offset_hz")},
            "analytic": {k: complex_json(ref[k]) for k in PORTS},
            "native": {k: complex_json(point["complex"][k]) for k in PORTS},
            "complex_relative_errors": errors,
        })
    tolerance = 1e-9 if termination == "matched" else (
        1e-5 if duration_s >= 0.60 else 2e-3
    )
    return {
        "case": body_name + "-" + termination + "-" + str(duration_s),
        "body": body_name, "termination": termination, "duration_s": duration_s,
        "source_boundary": "ideal-prescribed-flow-not-phonation",
        "observer": "native-acoustic-mouth-port-not-receiver",
        "physics_clock_hz": cfg.physics_clock_hz, "N": len(trace["U_in"]),
        "source_flow_sha256": sha256(trace["U_in"].astype("<f8").tobytes()).hexdigest(),
        "geometry_sha256": sha256(
            json.dumps(
                [{"length_m": s.length_m, "area_m2": s.area_m2}
                 for s in geometry.sections],
                separators=(",", ":"), sort_keys=True,
            ).encode()
        ).hexdigest(),
        "source_volume_m3": float(np.sum(trace["U_in"]) * cfg.timestep_s),
        "energy_residual_to_tolerance_max": trace["energy_error_to_tolerance_max"],
        "point_checks": checks, "max_complex_relative_error": max_error,
        "tolerance": tolerance, "pass": max_error <= tolerance,
    }


def refinements(body_name: str, geometry: Tract1DGeometry) -> list[dict]:
    records = []
    for f in TARGETS_HZ:
        limit = reference_transfer(geometry, f, termination="b0", continuum=True)
        xs = []
        for n in (2, 4, 8):
            actual = reference_transfer(geometry, f, termination="b0", cells_per_section=n)
            err = relative_errors(limit, actual)
            xs.append({
                "cells_per_section": n, "relative_complex_errors": err,
                "HpU": complex_json(actual["HpU"]),
            })
        monotonic = all(
            xs[i + 1]["relative_complex_errors"][name] <
            xs[i]["relative_complex_errors"][name]
            for name in PORTS for i in range(2)
        )
        records.append({
            "body": body_name, "frequency_hz": f,
            "continuous_limit": {k: complex_json(limit[k]) for k in PORTS},
            "levels": xs, "all_ports_complex_converge": monotonic,
        })
    return records


def run() -> dict:
    bodies, sha256_bytes = load_bodies()
    cases: dict[str, dict] = {}
    refines = []
    truncated_recovery = []
    for body, geom in bodies.items():
        refines.extend(refinements(body, geom))
        for termination, duration in (("matched", 0.30), ("b0", 0.30), ("b0", 0.60)):
            case = measure_case(body, geom, termination, duration)
            cases[case["case"]] = case
        short, long = cases[body + "-b0-0.3"], cases[body + "-b0-0.6"]
        # Compare each physical port's truncation error at each requested target,
        # while preserving each record's exact actual nearest-bin frequency.
        improved = all(
            long["point_checks"][i]["complex_relative_errors"][port] <=
            short["point_checks"][i]["complex_relative_errors"][port]
            for i in range(len(TARGETS_HZ)) for port in PORTS
        )
        truncated_recovery.append({"body": body, "improves_every_point": improved})
    zero_cfg = PassiveWaveguideConfig(bodies["M0"], termination="b0")
    zero_trace = impulse_trace(zero_cfg, 40 / zero_cfg.physics_clock_hz, amplitude_scale=0)
    silence = all(not np.any(zero_trace[port]) for port in ("p_in", "p_mouth", "U_mouth"))
    # Negative control: a matched load must not certify as B0 under same
    # body/input (at 100 Hz their loaded pressure transfer differs materially).
    b0_ref = reference_transfer(bodies["M0"], 100.0, termination="b0")
    wrong_ref = reference_transfer(bodies["M0"], 100.0, termination="matched")
    wrong_rel = relative_errors(b0_ref, wrong_ref)["HpU"]
    negative = {
        "zero_input_zero_output": silence, "wrong_matched_load_relative_error": wrong_rel,
        "wrong_load_rejected": wrong_rel > 2e-3,
    }
    passed = (all(x["pass"] for x in cases.values())
              and all(x["all_ports_complex_converge"] for x in refines)
              and all(x["improves_every_point"] for x in truncated_recovery)
              and silence and negative["wrong_load_rejected"])
    return {
        "schema_version": SCHEMA, "scope": "RESEARCH_ONLY",
        "scientific_result": ("NUMERICALLY_CONSISTENT_WITH_DECLARED_B0"
                              if passed else "FAIL_NUMERICAL_REFERENCE"),
        "physical_validity": "INDETERMINATE_REAL_RADIATION",
        "voice_quality": "VOICE_NO_GO_UNCHANGED",
        "creator_listening_requested": False,
        "base_main_sha": BASE_MAIN_SHA,
        "frozen_exp028_blob_sha1": BLOB_SHA1,
        "frozen_exp028_content_sha256": sha256_bytes,
        "model": {"air_density_kg_m3": RHO, "sound_speed_m_s": C,
                  "losses": "NONE", "phonation": "UNMODELED",
                  "receiver": "UNMODELED",
                  "B0": "DISCRETE_SHUNT_RESISTANCE_PLUS_INERTANCE"},
        "source": {"injected_volume_m3": SOURCE_VOLUME_M3,
                   "kind": "one-native-tick-volume-flow-pulse"},
        "cases": cases, "refinement": refines, "truncation": truncated_recovery,
        "negative_controls": negative, "gates_pass": passed,
        "limitations": ["no measured-mouth B0 impedance oracle",
                        "independently coded mathematics shares assumed B0 parameters",
                        "0.30 s finite-window DFT vs infinite harmonic response",
                        "no physically radiated or ear-position sound",
                        "no naturalness/phoneme/source-fold claims",
                        "not an adopted general organ graph or UI model"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\\n", encoding="utf-8"
    )
    print("VM-1B", report["scientific_result"], args.out)
    if not report["gates_pass"]:
        raise SystemExit("VM1B_GATE_FAILED")


if __name__ == "__main__":
    main()
