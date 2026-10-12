"""Run OG-0 research-only acoustic port experiment; no adopted claim."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform

import numpy as np
from port_network import MODEL_VERSION, prepare_serial_graph, reference_spec

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ORACLE = REPO / "tests/scientific/oracles/og0_wolfram.json"
WAVE_ORACLE = REPO / "tests/scientific/oracles/og0_wave_amendment01_wolfram.json"
MODEL_SOURCE = HERE / "port_network.py"


def main() -> None:
    expected = json.loads(ORACLE.read_text(encoding="utf-8"))
    wave_expected = json.loads(WAVE_ORACLE.read_text(encoding="utf-8"))
    f = np.asarray(expected["frequency_grid_hz"], dtype=np.float64)
    assert f.tolist() == wave_expected["frequency_grid_hz"], "amendment grid mismatch"
    equal = prepare_serial_graph(reference_spec())
    unequal = prepare_serial_graph(reference_spec(downstream_area_m2=6e-4))
    t = equal.transfer_matrix(f)
    zref = equal.air_density_kg_m3 * equal.sound_speed_m_s / equal.upstream.area_m2
    normalized = t.copy()
    normalized[..., 0, 1] /= zref
    normalized[..., 1, 0] *= zref
    phase = 2*np.pi*f*0.17/343.
    theoretical = np.zeros_like(normalized)
    theoretical[..., 0, 0] = np.cos(phase)
    theoretical[..., 1, 1] = np.cos(phase)
    theoretical[..., 0, 1] = 1j*np.sin(phase)
    theoretical[..., 1, 0] = 1j*np.sin(phase)
    matrix_error = float(np.max(np.abs(normalized-theoretical)))
    det_error = float(np.max(np.abs(np.linalg.det(normalized)-1.)))
    impedance = unequal.input_impedance(np.asarray([733.]))[0]
    ref_z = complex(0., expected["area_mismatch"]["pressure_release_733hz_input_impedance_imag"])
    impedance_error = float(abs(impedance-ref_z)/max(1., abs(ref_z)))
    junction = unequal.junction_audit(733., outlet_flow_m3_s=1e-6, outlet_load="matched")

    # Amendment 01: traveling-wave oracle independent of graph-matrix
    # inversion. This is a regression on observed fixtures, NOT preregistered.
    a = complex(*wave_expected["incident_pressure_pa_re_im"])
    za = float(expected["air_density_kg_m3"] *
               expected["sound_speed_m_s"] / expected["upstream"]["area_m2"])
    zb = float(expected["air_density_kg_m3"] *
               expected["sound_speed_m_s"] /
               expected["downstream"]["mismatched_area_m2"])
    ra = (zb - za) / (za + zb)
    ta = 2 * zb / (za + zb)
    phase_a = 2 * np.pi * f * expected["upstream"]["length_m"] / expected["sound_speed_m_s"]
    phase_b = 2 * np.pi * f * expected["downstream"]["length_m"] / expected["sound_speed_m_s"]
    propagated_b = ta * a * np.exp(-1j * phase_b)
    imposed_b_out = np.stack((propagated_b, propagated_b / zb), axis=-1)
    independent_a_in = np.stack((
        a * (np.exp(1j * phase_a) + ra * np.exp(-1j * phase_a)),
        a * (np.exp(1j * phase_a) - ra * np.exp(-1j * phase_a)) / za,
    ), axis=-1)
    norm = np.array([abs(a), abs(a) / za])
    actual_a_in = np.einsum("nij,nj->ni", unequal.transfer_matrix(f), imposed_b_out)
    independent_wave_error = float(
        np.max(np.abs((actual_a_in - independent_a_in) / norm)))
    bad_junction = np.diag(
        [1., expected["upstream"]["area_m2"] /
         expected["downstream"]["mismatched_area_m2"]]).astype(np.complex128)
    t_a = unequal._tube(unequal.upstream).transfer_matrix(f)
    t_b = unequal._tube(unequal.downstream).transfer_matrix(f)
    bad_matrix = np.matmul(np.matmul(t_a, bad_junction), t_b)
    bad_a_in = np.einsum("nij,nj->ni", bad_matrix, imposed_b_out)
    bad_wave_error = float(np.max(np.abs((bad_a_in - independent_a_in) / norm)))
    released = unequal.junction_audit(733., outlet_flow_m3_s=1e-6,
                                      outlet_load="pressure_release")
    scattering_energy_error = float(
        abs(ra**2 + za * ta**2 / zb - 1.))
    checks = {
        "equal_area_normalized_matrix": matrix_error < 1e-11,
        "determinant": det_error < 1e-11,
        "wolfram_impedance": impedance_error < 1e-10,
        "pressure_continuity": junction["pressure_residual_rel"] < 1e-11,
        "volume_flow_conservation": junction["flow_residual_rel"] < 1e-11,
        "mean_power_conservation": junction["power_residual_rel"] < 1e-11,
        "wolfram_scattering": abs(junction["reflection_pressure_real"] -
            expected["area_mismatch"]["reflection_pressure_real"]) < 1e-12,
        "independent_wave_scattering_amendment01": independent_wave_error < 1e-11,
        "mutation_incorrect_area_junction_rejected":
            bad_wave_error > wave_expected["mutation_min_normalized_residual"],
        "matched_wave_energy_balance": scattering_energy_error < 1e-12,
        "pressure_release_terminal_zero_power": abs(released["mean_power_w"]) < 1e-13,
    }
    identity = {
        "model_version": MODEL_VERSION,
        "equal_graph_digest": equal.graph_sha256,
        "unequal_graph_digest": unequal.graph_sha256,
        "frequency_grid_hz": f.tolist(),
        "baseline_main_sha": expected["baseline_main_sha"],
        "protocol": "amendment01-post-exploratory-regression",
        "sources_sha256": {
            "model": hashlib.sha256(MODEL_SOURCE.read_bytes()).hexdigest(),
            "runner": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "original_wolfram_oracle": hashlib.sha256(ORACLE.read_bytes()).hexdigest(),
            "amended_wolfram_oracle": hashlib.sha256(WAVE_ORACLE.read_bytes()).hexdigest(),
        },
        "numpy_version": np.__version__,
        "python_version": platform.python_version(),
    }
    signature = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result = {
        "experiment": "030 / OG-0",
        "status": "PROVISIONAL_NUMERICAL_PASS" if all(checks.values()) else "FAILED",
        "review_status": "NOT_INDEPENDENTLY_REVIEWED",
        "adoption_status": "NOT_ADOPTED",
        "model_version": MODEL_VERSION,
        "baseline_main_sha": expected["baseline_main_sha"],
        "run_identity_sha256": signature,
        "equal_graph_sha256": equal.graph_sha256,
        "unequal_graph_sha256": unequal.graph_sha256,
        "frequency_grid_hz": f.tolist(),
        "matrix_max_normalized_abs_error": matrix_error,
        "determinant_max_abs_error": det_error,
        "wolfram_impedance_733_relative_error": impedance_error,
        "matched_junction_audit_733": junction,
        "amendment01_independent_wave_normalized_max_error": independent_wave_error,
        "amendment01_wrong_junction_normalized_max_error": bad_wave_error,
        "amendment01_wave_scattering_energy_error": scattering_energy_error,
        "amendment01_pressure_release_mean_outlet_power_w": released["mean_power_w"],
        "interpretation": "POST_EXPLORATORY_CONTROLLED_REGRESSION_NOT_PREREGISTERED",
        "checks": checks,
        "numpy_version": np.__version__,
        "python_version": platform.python_version(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
