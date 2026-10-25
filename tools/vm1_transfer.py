"""VM-1A: research-only, volume-normalized tract impulse transfer measurement.

A physical mouth *port* is not a microphone. No synthetic voice, equalizer,
articulatory control, glottal oscillator, wall loss or Studio output is created.
Frozen preregistration: docs/research/voice-metrology/VM1A_GATE_A.md.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
from math import ceil, isfinite, log10, pi
from pathlib import Path

import numpy as np

from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics_waveguide import PassiveWaveguideConfig, PassiveWaveguideSession

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "experiments/028_task_field_morphology_transfer/frozen_reference.json"
FROZEN_BLOB_SHA1 = "7810dfbb72cb6c41af007db6e9d51c58cad9a522"
VOLUME_M3 = 1e-13
DURATION_S = 0.30
SCHEMA = "voice-metrology-transfer/vm1a"
BASE_SHA = "e05e3274ad69bfb9202816049f6661a18ba39ec0"
PORTS = ("U_in_m3_s", "p_in_pa", "p_mouth_pa", "U_mouth_m3_s")


def frozen_bodies() -> tuple[dict[str, Tract1DGeometry], str]:
    """Load immutable Experiment028 anatomical area vector, not a hand-copied vowel."""
    data = FROZEN.read_bytes()
    digest = sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()
    if digest != FROZEN_BLOB_SHA1:
        raise ValueError("FROZEN_BODY_BLOB_MISMATCH")
    reference = json.loads(data)
    m0 = reference["M0"]
    areas = m0["a_areas_m2"]
    if (len(areas) != 16 or len(m0["section_lengths_m"]) != 16
            or any(x != 0.010 for x in m0["section_lengths_m"])
            or not all(type(x) in (int, float) and isfinite(x) and x > 0 for x in areas)):
        raise ValueError("FROZEN_BODY_GEOMETRY_MISMATCH")
    geometries = {
        name: Tract1DGeometry(
            cavity_id="oral-" + name,
            sections=tuple(TubeSection(section_len, float(a)) for a in areas),
        )
        for name, section_len in (("M0", 0.010), ("M1", 0.011))
    }
    return geometries, sha256(data).hexdigest()


def make_pulse(config: PassiveWaveguideConfig, count: int, volume_m3: float) -> np.ndarray:
    if type(count) is not int or count <= 32:
        raise ValueError("INSUFFICIENT_IMPULSE_OBSERVATION")
    if not isfinite(volume_m3) or volume_m3 <= 0:
        raise ValueError("INVALID_INJECTED_VOLUME")
    flow = np.zeros(count, dtype=np.float64)
    flow[0] = volume_m3 / config.timestep_s
    assert np.sum(flow) * config.timestep_s == volume_m3 or np.isclose(
        np.sum(flow) * config.timestep_s, volume_m3, rtol=1e-15, atol=0)
    return flow


def native_trace(config: PassiveWaveguideConfig, flow: np.ndarray) -> dict[str, np.ndarray | float]:
    if (not isinstance(flow, np.ndarray) or flow.ndim != 1 or len(flow) < 33
            or not np.isfinite(flow).all()):
        raise ValueError("INVALID_FLOW_TRACE")
    session = PassiveWaveguideSession(config)
    pin = np.empty(len(flow), dtype=np.float64)
    pout = np.empty(len(flow), dtype=np.float64)
    uout = np.empty(len(flow), dtype=np.float64)
    max_scaled_energy_residual = 0.0
    energy = 0.0
    for i, x in enumerate(flow):
        step = session.step(float(x))
        pin[i], pout[i], uout[i] = (
            step.source_pressure_pa, step.mouth_pressure_pa, step.mouth_flow_m3_s
        )
        new_energy = step.duct_energy_j + step.radiation_energy_j
        tolerance = max(
            1e-9 * max(abs(step.delta_stored_energy_j),
                       abs(step.source_work_j), step.outlet_dissipation_j, 1e-20),
            1e-12 * max(energy, new_energy, 1e-20),
        )
        if abs(step.energy_residual_j) > tolerance:
            raise ArithmeticError("INVALID_WAVEGUIDE_ENERGY_LEDGER")
        max_scaled_energy_residual = max(
            max_scaled_energy_residual,
            abs(step.energy_residual_j) / tolerance,
        )
        energy = new_energy
    if not (np.isfinite(pin).all() and np.isfinite(pout).all() and np.isfinite(uout).all()):
        raise ArithmeticError("NONFINITE_PHYSICAL_OUTPUT")
    return {
        "U_in_m3_s": flow,
        "p_in_pa": pin,
        "p_mouth_pa": pout,
        "U_mouth_m3_s": uout,
        "max_energy_residual_fraction_of_tolerance": max_scaled_energy_residual,
    }


def transfer(config: PassiveWaveguideConfig, trace: dict, targets: tuple[float, ...] = (100., 600.)) -> dict:
    flow = trace["U_in_m3_s"]
    freq = np.fft.rfftfreq(len(flow), d=config.timestep_s)
    uhat = np.fft.rfft(flow)
    if np.any(np.abs(uhat) <= 0.0):
        raise ArithmeticError("IMPULSE_SPECTRAL_NULL")
    phat = np.fft.rfft(trace["p_mouth_pa"])
    zhat = np.fft.rfft(trace["p_in_pa"])
    qhat = np.fft.rfft(trace["U_mouth_m3_s"])
    hp = phat / uhat
    zin = zhat / uhat
    hu = qhat / uhat
    points = []
    for target in targets:
        k = int(np.argmin(abs(freq - target)))
        if k <= 0 or k >= len(freq) - 1:
            raise ValueError("TARGET_OUTSIDE_RESOLVED_BAND")
        if not all(np.isfinite(z) for z in (hp[k], zin[k], hu[k])):
            raise ArithmeticError("NONFINITE_COMPLEX_TRANSFER")
        points.append({
            "target_hz": target, "actual_hz": float(freq[k]),
            "bin": k, "offset_hz": float(freq[k] - target),
            "HpU_real": float(hp[k].real), "HpU_imag": float(hp[k].imag),
            "Zin_real": float(zin[k].real), "Zin_imag": float(zin[k].imag),
            "HU_real": float(hu[k].real), "HU_imag": float(hu[k].imag),
        })
    a, b = abs(hp[points[0]["bin"]]), abs(hp[points[1]["bin"]])
    ratio_db = 20 * log10(b / a) if a > 1e-30 and b > 1e-30 else None
    return {
        "df_hz": float(freq[1]), "points": points,
        "H600_to_H100_db": ratio_db, "reference_status": "NOT_YET_SEGMENTED_B0_VALIDATED",
    }


def uniform_matched_oracle() -> dict:
    """Independent analytic traveling-wave delay, exact for a uniform matched tube."""
    geom = Tract1DGeometry("uniform-control", tuple(
        TubeSection(0.010, 8e-4) for _ in range(16)
    ))
    config = PassiveWaveguideConfig(geom, termination="matched")
    flow = make_pulse(config, 512, VOLUME_M3)
    raw = native_trace(config, flow)
    ticks = 16 * config.cells_per_section
    zc = config.characteristic_impedances_pa_s_m3[0]
    shifted = np.zeros_like(flow)
    shifted[ticks:] = flow[:-ticks]
    for actual, expected in (
        (raw["p_in_pa"], zc * flow),
        (raw["p_mouth_pa"], zc * shifted),
        (raw["U_mouth_m3_s"], shifted),
    ):
        if not np.allclose(actual, expected, rtol=1e-11, atol=1e-14 if actual is not raw["U_mouth_m3_s"] else 1e-17):
            raise ArithmeticError("UNIFORM_MATCHED_DELAY_ORACLE_FAILED")
    tfr = transfer(config, raw)
    max_rel_error = 0.0
    for entry in tfr["points"]:
        f = entry["actual_hz"]
        exact = np.exp(-2j * pi * f * ticks / config.physics_clock_hz)
        obs_p = complex(entry["HpU_real"], entry["HpU_imag"])
        obs_z = complex(entry["Zin_real"], entry["Zin_imag"])
        obs_u = complex(entry["HU_real"], entry["HU_imag"])
        max_rel_error = max(max_rel_error, abs(obs_p - zc * exact) / zc,
                            abs(obs_z - zc) / zc, abs(obs_u - exact))
    if max_rel_error > 1e-9:
        raise ArithmeticError("UNIFORM_COMPLEX_REFERENCE_FAILED")
    return {
        "status": "MATCHED_UNIFORM_ANALYTIC_PASS",
        "first_nonzero_outlet_tick": ticks,
        "expected_delay_s": ticks * config.timestep_s,
        "characteristic_impedance_pa_s_m3": zc,
        "max_relative_complex_transfer_error": max_rel_error,
    }


def one_run(name: str, geometry: Tract1DGeometry, termination: str) -> dict:
    config = PassiveWaveguideConfig(geometry, termination=termination)
    n = int(ceil(DURATION_S * config.physics_clock_hz))
    flow = make_pulse(config, n, VOLUME_M3)
    trace = native_trace(config, flow)
    spectrum = transfer(config, trace)
    if trace["max_energy_residual_fraction_of_tolerance"] > 1.0:
        raise ArithmeticError("ENERGY_GATE_FAILED")
    return {
        "body": name, "termination": termination,
        "source_boundary": "ideal-prescribed-volume-flow",
        "observer": "mouth-port-not-a-microphone",
        "body_reference": f"v3b-axial-{name}@1",
        "section_length_m": geometry.sections[0].length_m,
        "total_length_m": geometry.total_length_m,
        "geometry_sha256": sha256(
            json.dumps([{"length_m": s.length_m, "area_m2": s.area_m2}
                        for s in geometry.sections], sort_keys=True,
                       separators=(",", ":")).encode()
        ).hexdigest(),
        "physics_clock_hz": config.physics_clock_hz, "duration_s": n * config.timestep_s,
        "N": n, "source_flow_sha256": sha256(flow.astype("<f8").tobytes()).hexdigest(),
        "integrated_injected_volume_m3": float(np.sum(flow) * config.timestep_s),
        "energy_residual_fraction_max": trace["max_energy_residual_fraction_of_tolerance"],
        "measurement": spectrum,
    }


def run() -> dict:
    reference = uniform_matched_oracle()
    geometries, reference_sha = frozen_bodies()
    runs = {}
    for name, geometry in geometries.items():
        for term in ("matched", "b0"):
            runs[name + "-" + term] = one_run(name, geometry, term)
    return {
        "schema_version": SCHEMA, "kind": "RESEARCH_ONLY",
        "quality_status": "NOT_ASSESSED",
        "scientific_status": "TRANSFER_DIAGNOSTIC_B0_REFERENCE_PENDING",
        "base_core_sha": BASE_SHA,
        "frozen_exp028_blob_sha1": FROZEN_BLOB_SHA1,
        "frozen_exp028_sha256": reference_sha,
        "stimulus": {"type": "single-native-tick-imposed-flow",
                     "injected_volume_m3": VOLUME_M3, "physical_clock_specific": True},
        "physical_model": {"rho_kg_m3": 1.21, "c_m_s": 343.0,
                           "static_tract": True, "walls": "RIGID_LOSSLESS",
                           "phonation": "UNMODELED", "receiver": "UNMODELED"},
        "analytic_control": reference,
        "runs": runs,
        "limitations": ["no independent segmented/B0 oracle",
                        "no frequency-width/Q or ringdown certification",
                        "no microphone or ear pressure",
                        "pulse response not a historical LF-source replay",
                        "not a measure of voice quality"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\\n", encoding="utf-8")
    print("VM-1A diagnostic created: no voice-quality approval", args.out)


if __name__ == "__main__":
    main()
