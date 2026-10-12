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


def main() -> None:
    expected = json.loads(ORACLE.read_text(encoding="utf-8"))
    f = np.asarray(expected["frequency_grid_hz"], dtype=np.float64)
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
    checks = {
        "equal_area_normalized_matrix": matrix_error < 1e-11,
        "determinant": det_error < 1e-11,
        "wolfram_impedance": impedance_error < 1e-10,
        "pressure_continuity": junction["pressure_residual_rel"] < 1e-11,
        "volume_flow_conservation": junction["flow_residual_rel"] < 1e-11,
        "mean_power_conservation": junction["power_residual_rel"] < 1e-11,
        "wolfram_scattering": abs(junction["reflection_pressure_real"] -
            expected["area_mismatch"]["reflection_pressure_real"]) < 1e-12,
    }
    identity = {
        "model_version": MODEL_VERSION,
        "equal_graph_digest": equal.graph_sha256,
        "unequal_graph_digest": unequal.graph_sha256,
        "frequency_grid_hz": f.tolist(),
        "baseline_main_sha": expected["baseline_main_sha"],
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
        "checks": checks,
        "numpy_version": np.__version__,
        "python_version": platform.python_version(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
