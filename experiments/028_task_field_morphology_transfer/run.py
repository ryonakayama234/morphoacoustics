from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import inspect
import json
import math
import platform
import sys
import time
from pathlib import Path
from types import ModuleType

import numpy as np

from morphoacoustics.physical import Tract1DGeometry, TubeSection

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "v3b_oracle.json"
FROZEN_REFERENCE_PATH = HERE / "frozen_reference.json"
REPOSITORY_ROOT = EXPERIMENTS.parent

M0_SECTION_LENGTH_M = 0.010
M1_SECTION_LENGTH_M = 0.011
AXIAL_SCALE = 1.10
METRIC_SCALE_ATOL = 1e-12
ENDPOINT_ERROR_RATIO_LIMIT = 0.20
TRANSFER_ERROR_RATIO_DELTA_LIMIT = 0.005
MORPHOLOGY_EFFECT_MARGIN = 5.0
RESONANCE_STEP_S = 0.010
TRAJECTORY_STEP_RATIO_LIMIT = 0.20
ARTIFACT_JUMP_RATIO_LIMIT = 3.0
TEMPORAL_STABILITY_LIMIT = 0.20
LISTENING_PEAK = 0.90

FROZEN_GATE = {
    "M1_endpoint_error_ratio_max": ENDPOINT_ERROR_RATIO_LIMIT,
    "cross_body_endpoint_error_ratio_delta_max": TRANSFER_ERROR_RATIO_DELTA_LIMIT,
    "metric_coordinate_scale_abs_tolerance": METRIC_SCALE_ATOL,
    "body_effect_min_over_peak_tolerance": MORPHOLOGY_EFFECT_MARGIN,
    "trajectory_step_ratio_max": TRAJECTORY_STEP_RATIO_LIMIT,
    "artifact_jump_ratio_max": ARTIFACT_JUMP_RATIO_LIMIT,
    "temporal_normalized_rms_floor_max": TEMPORAL_STABILITY_LIMIT,
}


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP27 = load_experiment_module(
    "morpho_exp027_for_028",
    EXPERIMENTS / "027_task_field_vowel_transition" / "run.py",
)
EXP26 = EXP27.EXP26

SAMPLE_RATE_HZ = EXP27.SAMPLE_RATE_HZ
DURATION_S = EXP27.DURATION_S
PRIMARY_CONTROL_STEP_S = EXP27.PRIMARY_CONTROL_STEP_S
REFERENCE_CONTROL_STEP_S = EXP27.REFERENCE_CONTROL_STEP_S
PRIMARY_HOP_SIZE = EXP27.PRIMARY_HOP_SIZE
REFERENCE_HOP_SIZE = EXP27.REFERENCE_HOP_SIZE


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def implementation_identity() -> dict[str, object]:
    """Fingerprint files actually loaded and the live realizer callables.

    The checked-in expected hashes were captured from audited head 990e602,
    not from the current working tree at experiment execution time.
    """
    modules: dict[str, ModuleType] = {}

    def visit(module: ModuleType) -> None:
        path = Path(module.__file__).resolve()
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        if relative in modules:
            return
        modules[relative] = module
        for name, child in vars(module).items():
            if name.startswith("EXP") and isinstance(child, ModuleType):
                visit(child)

    visit(EXP27)
    files = {
        relative: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
        for relative, module in sorted(modules.items())
    }
    for directory in ("acoustics", "physical"):
        for path in sorted((REPOSITORY_ROOT / "src" / "morphoacoustics" / directory).glob("*.py")):
            files[path.relative_to(REPOSITORY_ROOT).as_posix()] = (
                hashlib.sha256(path.read_bytes()).hexdigest()
            )

    function_objects = {name: getattr(EXP27, name, None) for name in (
        "section_coordinates", "gaussian_kernel", "task_log_diameter_delta_for",
        "analytic_task_activation_scalar", "task_activation_at_time",
        "task_activations_at_time", "realize_task_geometry_from_activations",
        "realize_task_geometry", "task_geometry_for_time", "render_task_continuous",
    )}
    function_objects["source.build_sources"] = EXP26.EXP13.build_sources
    functions = {}
    for name, function in function_objects.items():
        try:
            source = inspect.getsource(function)
            code = function.__code__
            functions[name] = {
                "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                # inspect can unwrap decorated functions. Bind the live code
                # location too, so a replacement wrapper still fails.
                "code_path": Path(code.co_filename).resolve().relative_to(REPOSITORY_ROOT).as_posix(),
                "code_first_line": code.co_firstlineno,
                "code_name": code.co_name,
            }
        except (AttributeError, OSError, TypeError, ValueError):
            functions[name] = None

    constants = {
        relative: {
            name: value for name, value in sorted(vars(module).items())
            if name.isupper() and isinstance(value, (str, int, float, bool))
        }
        for relative, module in sorted(modules.items())
    }
    return {"files_sha256": files, "executed_functions": functions,
            "runtime_constants": constants}


def frozen_m0_matches(
    m0_a: Tract1DGeometry,
    m0_i: Tract1DGeometry,
    frozen: dict[str, object],
) -> bool:
    expected = frozen["M0"]
    return all(
        np.array_equal(EXP26.geometry_lengths(geometry), expected["section_lengths_m"])
        and np.array_equal(EXP26.geometry_areas(geometry), expected[f"{vowel}_areas_m2"])
        for vowel, geometry in (("a", m0_a), ("i", m0_i))
    )


def frozen_preflight(
    oracle: dict[str, object],
    frozen: dict[str, object],
    m0_a: Tract1DGeometry,
    m0_i: Tract1DGeometry,
) -> dict[str, object]:
    identity = implementation_identity()
    checks = {
        "executed_implementation_matches": identity == frozen["implementation"],
        "M0_matches_frozen_body": frozen_m0_matches(m0_a, m0_i, frozen),
        "oracle_gate_matches_local_limits": oracle.get("frozen_gate") == FROZEN_GATE,
        "runtime_gate_matches_frozen_limits": {
            "M1_endpoint_error_ratio_max": ENDPOINT_ERROR_RATIO_LIMIT,
            "cross_body_endpoint_error_ratio_delta_max": TRANSFER_ERROR_RATIO_DELTA_LIMIT,
            "metric_coordinate_scale_abs_tolerance": METRIC_SCALE_ATOL,
            "body_effect_min_over_peak_tolerance": MORPHOLOGY_EFFECT_MARGIN,
            "trajectory_step_ratio_max": TRAJECTORY_STEP_RATIO_LIMIT,
            "artifact_jump_ratio_max": ARTIFACT_JUMP_RATIO_LIMIT,
            "temporal_normalized_rms_floor_max": TEMPORAL_STABILITY_LIMIT,
        } == oracle.get("frozen_gate"),
        "oracle_matches_frozen_record": sha256_json(oracle) == frozen["oracle_sha256_canonical_json"],
        "execution_schedule_matches": {
            "sample_rate_hz": SAMPLE_RATE_HZ, "duration_s": DURATION_S,
            "primary_control_step_s": PRIMARY_CONTROL_STEP_S,
            "reference_control_step_s": REFERENCE_CONTROL_STEP_S,
            "primary_hop_size": PRIMARY_HOP_SIZE,
            "reference_hop_size": REFERENCE_HOP_SIZE,
            "resonance_step_s": RESONANCE_STEP_S, "listening_peak": LISTENING_PEAK,
        } == frozen["execution_schedule"],
    }
    return {"checks": checks, "pass": all(checks.values()),
            "implementation_sha256": sha256_json(identity), "implementation": identity,
            "reference_commit": frozen["reference_commit"]}


def reject_preflight(output_dir: Path, preflight: dict[str, object]) -> dict[str, object]:
    decision = {
        "decision": (
            "MORPHOLOGY_INTERVENTION_INVALID"
            if not preflight["checks"]["M0_matches_frozen_body"]
            else "IMPLEMENTATION_MISMATCH"
        ),
        "preflight": preflight,
        "gates": {"frozen_reference_preflight": False},
        "claim_boundary": "No transfer claim: frozen input or implementation changed.",
    }
    for name in ("decision.json", "provenance.json"):
        (output_dir / name).write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    return decision


def realizer_payload() -> dict[str, object]:
    return {
        "revision": "experiment-027-v3a-candidate-1",
        "coordinate_mapping": "section slots mapped uniformly to x=j/(N-1)",
        "field_space": "log_diameter",
        "kappa": EXP27.KAPPA,
        "sigma": EXP27.SIGMA,
        "sigma_lip": EXP27.SIGMA_LIP,
        "activation_semantics": (
            "each canonical task has its own sampled smoothstep activation "
            "derived from onset_s/offset_s"
        ),
        "area_relation": (
            "log A(x,t) = log A0(x) + 2 * Sum_i["
            "activation_i(t) * delta_log_diameter_i(x)]"
        ),
    }


def with_section_length(
    geometry: Tract1DGeometry,
    section_length_m: float,
    *,
    cavity_id: str,
) -> Tract1DGeometry:
    if not math.isfinite(section_length_m) or section_length_m <= 0.0:
        raise ValueError("section_length_m must be finite and positive")
    return Tract1DGeometry(
        cavity_id=cavity_id,
        sections=tuple(
            TubeSection(
                length_m=section_length_m,
                area_m2=float(section.area_m2),
            )
            for section in geometry.sections
        ),
    )


def total_length(geometry: Tract1DGeometry) -> float:
    return float(np.sum(EXP26.geometry_lengths(geometry)))


def metric_task_coordinates(geometry: Tract1DGeometry) -> np.ndarray:
    length = total_length(geometry)
    return np.asarray(
        [task.location * length for task in EXP27.TASKS],
        dtype=np.float64,
    )


def morphology_payload(
    m0_a: Tract1DGeometry,
    m0_i: Tract1DGeometry,
    m1_a: Tract1DGeometry,
    m1_i: Tract1DGeometry,
) -> dict[str, object]:
    return {
        "M0": {
            "section_count": len(m0_a.sections),
            "section_lengths_m": EXP26.geometry_lengths(m0_a).tolist(),
            "total_length_m": total_length(m0_a),
            "a_areas_m2": EXP26.geometry_areas(m0_a).tolist(),
            "i_areas_m2": EXP26.geometry_areas(m0_i).tolist(),
        },
        "M1": {
            "section_count": len(m1_a.sections),
            "section_lengths_m": EXP26.geometry_lengths(m1_a).tolist(),
            "total_length_m": total_length(m1_a),
            "a_areas_m2": EXP26.geometry_areas(m1_a).tolist(),
            "i_areas_m2": EXP26.geometry_areas(m1_i).tolist(),
        },
        "intervention": {
            "kind": "uniform_axial_section_length_scale",
            "section_length_m": {
                "M0": M0_SECTION_LENGTH_M,
                "M1": M1_SECTION_LENGTH_M,
            },
            "axial_scale": AXIAL_SCALE,
            "area_values_changed": False,
            "section_count_changed": False,
        },
    }


def morphology_intervention_is_isolated(
    m0_a: Tract1DGeometry,
    m0_i: Tract1DGeometry,
    m1_a: Tract1DGeometry,
    m1_i: Tract1DGeometry,
) -> bool:
    if not (
        len(m0_a.sections)
        == len(m0_i.sections)
        == len(m1_a.sections)
        == len(m1_i.sections)
        == 16
    ):
        return False

    m0_lengths = EXP26.geometry_lengths(m0_a)
    m1_lengths = EXP26.geometry_lengths(m1_a)
    if not np.array_equal(m0_lengths, EXP26.geometry_lengths(m0_i)):
        return False
    if not np.array_equal(m1_lengths, EXP26.geometry_lengths(m1_i)):
        return False
    if not np.allclose(
        m0_lengths,
        M0_SECTION_LENGTH_M,
        rtol=0.0,
        atol=1e-15,
    ):
        return False
    if not np.allclose(
        m1_lengths,
        M1_SECTION_LENGTH_M,
        rtol=0.0,
        atol=1e-15,
    ):
        return False

    if not np.array_equal(
        EXP26.geometry_areas(m0_a),
        EXP26.geometry_areas(m1_a),
    ):
        return False
    if not np.array_equal(
        EXP26.geometry_areas(m0_i),
        EXP26.geometry_areas(m1_i),
    ):
        return False

    return bool(
        math.isclose(
            total_length(m1_a) / total_length(m0_a),
            AXIAL_SCALE,
            rel_tol=0.0,
            abs_tol=METRIC_SCALE_ATOL,
        )
    )


def trajectory_rows(
    label: str,
    start: Tract1DGeometry,
    *,
    control_step_s: float,
) -> tuple[list[dict[str, object]], np.ndarray]:
    rows: list[dict[str, object]] = []
    peaks: list[np.ndarray] = []
    for time_s in np.arange(
        0.0,
        DURATION_S + RESONANCE_STEP_S / 2.0,
        RESONANCE_STEP_S,
        dtype=np.float64,
    ):
        activations = EXP27.task_activations_at_time(
            float(time_s),
            control_step_s=control_step_s,
        )
        geometry = EXP27.task_geometry_for_time(
            start,
            float(time_s),
            control_step_s=control_step_s,
            cavity_id=f"oral-v3b-{label}",
        )
        p = EXP26.peak_array(geometry, count=3)
        peaks.append(p)
        areas = EXP26.geometry_areas(geometry)
        lengths = EXP26.geometry_lengths(geometry)
        rows.append(
            {
                "condition": label,
                "time_s": float(time_s),
                "task0_activation": activations[0],
                "task1_activation": activations[1],
                "task2_activation": activations[2],
                "p1_hz": float(p[0]),
                "p2_hz": float(p[1]),
                "p3_hz": float(p[2]),
                "min_area_m2": float(np.min(areas)),
                "max_area_m2": float(np.max(areas)),
                "section_length_m": float(lengths[0]),
                "total_length_m": float(np.sum(lengths)),
            }
        )
    return rows, np.asarray(peaks, dtype=np.float64)


def area_trajectory_rows(
    m0_a: Tract1DGeometry,
    m1_a: Tract1DGeometry,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label, start in (("M0", m0_a), ("M1", m1_a)):
        for time_s in np.arange(
            0.0,
            DURATION_S + RESONANCE_STEP_S / 2.0,
            RESONANCE_STEP_S,
            dtype=np.float64,
        ):
            activations = EXP27.task_activations_at_time(
                float(time_s),
                control_step_s=PRIMARY_CONTROL_STEP_S,
            )
            geometry = EXP27.task_geometry_for_time(
                start,
                float(time_s),
                control_step_s=PRIMARY_CONTROL_STEP_S,
                cavity_id=f"oral-v3b-{label}-area",
            )
            for section_index, section in enumerate(geometry.sections):
                rows.append(
                    {
                        "condition": label,
                        "time_s": float(time_s),
                        "task0_activation": activations[0],
                        "task1_activation": activations[1],
                        "task2_activation": activations[2],
                        "section_index": section_index,
                        "length_m": section.length_m,
                        "area_m2": section.area_m2,
                    }
                )
    return rows


def compare_peak_oracles(
    observed: dict[str, np.ndarray],
    oracle: dict[str, object],
) -> tuple[bool, dict[str, dict[str, object]]]:
    tolerance_hz = float(oracle["model"]["peak_tolerance_hz"])
    checks: dict[str, dict[str, object]] = {}
    passed_all = True
    expected_all = oracle["peak_frequencies_hz"]
    for key, values in observed.items():
        expected = np.asarray(expected_all[key], dtype=np.float64)
        passed, errors = EXP27.compare_peaks(
            values,
            expected,
            tolerance_hz=tolerance_hz,
        )
        passed_all = passed_all and passed
        checks[key] = {
            "observed_hz": values.tolist(),
            "expected_hz": expected.tolist(),
            "abs_error_hz": errors,
            "pass": passed,
        }
    return passed_all, checks


def endpoint_metrics(
    p_a: np.ndarray,
    p_i: np.ndarray,
    p_task: np.ndarray,
) -> dict[str, float | bool]:
    a_to_i = float(np.linalg.norm(p_a[:2] - p_i[:2]))
    task_to_i = float(np.linalg.norm(p_task[:2] - p_i[:2]))
    task_to_a = float(np.linalg.norm(p_task[:2] - p_a[:2]))
    ratio = task_to_i / a_to_i
    return {
        "a_to_i_p1p2_distance_hz": a_to_i,
        "task_to_i_p1p2_distance_hz": task_to_i,
        "task_to_a_p1p2_distance_hz": task_to_a,
        "task_to_i_over_a_to_i": ratio,
        "closer_to_i_than_a": bool(task_to_i < task_to_a),
    }


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    frozen = json.loads(FROZEN_REFERENCE_PATH.read_text(encoding="utf-8"))
    v3a_oracle = json.loads(Path(EXP27.ORACLE_PATH).read_text(encoding="utf-8"))

    m0_a = EXP26.EXP23.primary_geometry("a")
    m0_i = EXP26.EXP23.primary_geometry("i")
    preflight = frozen_preflight(oracle, frozen, m0_a, m0_i)
    if not preflight["pass"]:
        return reject_preflight(output_dir, preflight)

    task_plan = EXP27.task_plan_payload()
    realizer = realizer_payload()
    task_digest = sha256_json(task_plan)
    realizer_parameter_digest = sha256_json(realizer)
    realizer_digest = preflight["implementation_sha256"]

    (output_dir / "task_plan.json").write_text(
        json.dumps(task_plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "realizer_parameters.json").write_text(
        json.dumps(realizer, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    representation_clean = EXP27.representation_is_clean(task_plan)
    frozen_task_match = bool(
        task_plan == v3a_oracle["task_plan"] == oracle["task_plan"]
    )
    realizer_core_match = bool(
        oracle["realizer"]
        == {
            "field_space": realizer["field_space"],
            "coordinate_mapping": realizer["coordinate_mapping"],
            "kappa": realizer["kappa"],
            "sigma": realizer["sigma"],
            "sigma_lip": realizer["sigma_lip"],
        }
    )

    schedule_checks = [
        {
            "onset": EXP27.task_activation_at_time(
                task,
                task.onset_s,
                control_step_s=PRIMARY_CONTROL_STEP_S,
            ),
            "midpoint": EXP27.task_activation_at_time(
                task,
                0.5 * (task.onset_s + task.offset_s),
                control_step_s=PRIMARY_CONTROL_STEP_S,
            ),
            "offset": EXP27.task_activation_at_time(
                task,
                task.offset_s,
                control_step_s=PRIMARY_CONTROL_STEP_S,
            ),
        }
        for task in EXP27.TASKS
    ]
    schedule_pass = all(
        math.isclose(row["onset"], 0.0, rel_tol=0.0, abs_tol=1e-12)
        and math.isclose(row["midpoint"], 0.5, rel_tol=0.0, abs_tol=1e-12)
        and math.isclose(row["offset"], 1.0, rel_tol=0.0, abs_tol=1e-12)
        for row in schedule_checks
    )

    m1_a = with_section_length(
        m0_a,
        M1_SECTION_LENGTH_M,
        cavity_id="oral-v3b-m1-a",
    )
    m1_i = with_section_length(
        m0_i,
        M1_SECTION_LENGTH_M,
        cavity_id="oral-v3b-m1-i-observer-only",
    )

    morphologies = morphology_payload(m0_a, m0_i, m1_a, m1_i)
    (output_dir / "morphologies.json").write_text(
        json.dumps(morphologies, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    morphology_isolated = morphology_intervention_is_isolated(
        m0_a,
        m0_i,
        m1_a,
        m1_i,
    )

    coords0 = metric_task_coordinates(m0_a)
    coords1 = metric_task_coordinates(m1_a)
    expected_coords0 = np.asarray(
        oracle["metric_task_coordinates_m"]["M0"],
        dtype=np.float64,
    )
    expected_coords1 = np.asarray(
        oracle["metric_task_coordinates_m"]["M1"],
        dtype=np.float64,
    )
    coord_oracle_pass = bool(
        np.allclose(coords0, expected_coords0, rtol=0.0, atol=1e-15)
        and np.allclose(coords1, expected_coords1, rtol=0.0, atol=1e-15)
    )
    coord_scales = coords1 / coords0
    metric_scale_pass = bool(
        np.allclose(
            coord_scales,
            AXIAL_SCALE,
            rtol=0.0,
            atol=METRIC_SCALE_ATOL,
        )
    )
    coordinate_rows = [
        {
            "task_index": index,
            "task": task.task,
            "normalized_location": task.location,
            "M0_metric_m": float(coords0[index]),
            "M1_metric_m": float(coords1[index]),
            "M1_over_M0": float(coord_scales[index]),
        }
        for index, task in enumerate(EXP27.TASKS)
    ]
    write_csv(output_dir / "metric_task_coordinates.csv", coordinate_rows)

    m0_task = EXP27.realize_task_geometry(
        m0_a,
        1.0,
        cavity_id="oral-v3b-m0-task-endpoint",
    )
    m1_task = EXP27.realize_task_geometry(
        m1_a,
        1.0,
        cavity_id="oral-v3b-m1-task-endpoint",
    )
    endpoint_area_equal = bool(
        np.array_equal(
            EXP26.geometry_areas(m0_task),
            EXP26.geometry_areas(m1_task),
        )
    )
    endpoint_length_scale_pass = bool(
        np.allclose(
            EXP26.geometry_lengths(m1_task)
            / EXP26.geometry_lengths(m0_task),
            AXIAL_SCALE,
            rtol=0.0,
            atol=METRIC_SCALE_ATOL,
        )
    )

    observed_peaks = {
        "M0_a": EXP26.peak_array(m0_a, count=5),
        "M0_i": EXP26.peak_array(m0_i, count=5),
        "M0_task_endpoint": EXP26.peak_array(m0_task, count=5),
        "M1_a": EXP26.peak_array(m1_a, count=5),
        "M1_i": EXP26.peak_array(m1_i, count=5),
        "M1_task_endpoint": EXP26.peak_array(m1_task, count=5),
    }
    oracle_pass, oracle_checks = compare_peak_oracles(observed_peaks, oracle)

    m0_v3a_peak_match = bool(
        np.array_equal(
            observed_peaks["M0_a"],
            np.asarray(v3a_oracle["peak_frequencies_hz"]["a"], dtype=np.float64),
        )
        and np.array_equal(
            observed_peaks["M0_i"],
            np.asarray(v3a_oracle["peak_frequencies_hz"]["i"], dtype=np.float64),
        )
        and np.array_equal(
            observed_peaks["M0_task_endpoint"],
            np.asarray(
                v3a_oracle["peak_frequencies_hz"]["task_endpoint"],
                dtype=np.float64,
            ),
        )
    )

    metrics0 = endpoint_metrics(
        observed_peaks["M0_a"],
        observed_peaks["M0_i"],
        observed_peaks["M0_task_endpoint"],
    )
    metrics1 = endpoint_metrics(
        observed_peaks["M1_a"],
        observed_peaks["M1_i"],
        observed_peaks["M1_task_endpoint"],
    )
    e0 = float(metrics0["task_to_i_over_a_to_i"])
    e1 = float(metrics1["task_to_i_over_a_to_i"])
    transfer_delta = abs(e1 - e0)

    intent_retention_pass = bool(
        metrics1["closer_to_i_than_a"]
        and e1 <= ENDPOINT_ERROR_RATIO_LIMIT
    )
    transfer_stability_pass = bool(
        math.isfinite(transfer_delta)
        and transfer_delta <= TRANSFER_ERROR_RATIO_DELTA_LIMIT
    )

    m0_rows, m0_peaks = trajectory_rows(
        "M0_task_field",
        m0_a,
        control_step_s=PRIMARY_CONTROL_STEP_S,
    )
    m1_rows, m1_peaks = trajectory_rows(
        "M1_task_field",
        m1_a,
        control_step_s=PRIMARY_CONTROL_STEP_S,
    )
    write_csv(output_dir / "resonance_trajectory.csv", m0_rows + m1_rows)
    write_csv(
        output_dir / "task_section_area_trajectory.csv",
        area_trajectory_rows(m0_a, m1_a),
    )

    matched = np.linalg.norm(
        m1_peaks[:, :2] - m0_peaks[:, :2],
        axis=1,
    )
    write_csv(
        output_dir / "m0_m1_trajectory_difference.csv",
        [
            {
                "time_s": float(m0_rows[index]["time_s"]),
                "M0_p1_hz": float(m0_peaks[index, 0]),
                "M0_p2_hz": float(m0_peaks[index, 1]),
                "M1_p1_hz": float(m1_peaks[index, 0]),
                "M1_p2_hz": float(m1_peaks[index, 1]),
                "p1p2_distance_hz": float(matched[index]),
            }
            for index in range(len(m0_rows))
        ],
    )

    geometry_valid = bool(
        all(
            math.isfinite(float(row["min_area_m2"]))
            and float(row["min_area_m2"]) > 0.0
            and math.isfinite(float(row["max_area_m2"]))
            and float(row["max_area_m2"]) > 0.0
            for row in m1_rows
        )
    )
    m1_endpoint_distance = float(metrics1["a_to_i_p1p2_distance_hz"])
    m1_step_ratio = EXP26.max_trajectory_step_ratio(
        m1_peaks,
        m1_endpoint_distance,
    )
    trajectory_stable = bool(
        np.all(np.isfinite(m1_peaks))
        and m1_peaks.shape[1] >= 3
        and m1_step_ratio < TRAJECTORY_STEP_RATIO_LIMIT
    )

    sources, _ = EXP26.EXP13.build_sources()
    source_result = sources["lf_fixed"]
    source = np.asarray(source_result.source, dtype=np.float64)
    source_regression = EXP26.source_regression(source_result)
    source_hash = EXP26.sha256_float64(source)
    # CPU SIMD paths may differ in the last bit of exp/sin results. Freeze the
    # source generator code/constants, not one hardware's floating byte stream.
    source_bytes_match_capture = source_hash == frozen["source_sha256_float64"]

    t0 = EXP27.render_task_continuous(
        source,
        m0_a,
        control_step_s=PRIMARY_CONTROL_STEP_S,
        hop_size=PRIMARY_HOP_SIZE,
        label="v3b-m0",
    )
    t1 = EXP27.render_task_continuous(
        source,
        m1_a,
        control_step_s=PRIMARY_CONTROL_STEP_S,
        hop_size=PRIMARY_HOP_SIZE,
        label="v3b-m1",
    )
    t1_ref = EXP27.render_task_continuous(
        source,
        m1_a,
        control_step_s=REFERENCE_CONTROL_STEP_S,
        hop_size=REFERENCE_HOP_SIZE,
        label="v3b-m1-reference",
    )

    waveforms = {
        "T0_M0_task_field": t0,
        "T1_M1_task_field": t1,
        "T1_ref_M1_task_field": t1_ref,
    }
    all_finite = all(
        bool(np.all(np.isfinite(values)))
        for values in waveforms.values()
    )
    for name, values in waveforms.items():
        np.save(output_dir / f"{name}_raw_pressure_pa.npy", values)

    transition_jump, endpoint_jump, artifact_ratio = EXP26.artifact_jump_ratio(t1)
    artifact_pass = bool(
        math.isfinite(artifact_ratio)
        and artifact_ratio < ARTIFACT_JUMP_RATIO_LIMIT
    )
    temporal_floor = EXP26.normalized_rms_difference(t1, t1_ref)
    temporal_pass = bool(
        math.isfinite(temporal_floor)
        and temporal_floor < TEMPORAL_STABILITY_LIMIT
    )
    body_waveform_effect = EXP26.normalized_rms_difference(t1, t0)

    listening_gain = EXP26.common_listening_gain(
        {
            "T0_M0_task_field": t0,
            "T1_M1_task_field": t1,
        }
    )
    listening = {
        "T0_M0_task_field": np.asarray(t0 * listening_gain, dtype=np.float64),
        "T1_M1_task_field": np.asarray(t1 * listening_gain, dtype=np.float64),
    }
    listening_no_clipping = all(
        float(np.max(np.abs(values))) <= LISTENING_PEAK + 1e-7
        for values in listening.values()
    )
    listening_dir = output_dir / "listening" / "named"
    listening_dir.mkdir(parents=True, exist_ok=True)
    for name, values in listening.items():
        EXP26.EXP23.write_wav(listening_dir / f"{name}.wav", values)

    signal_rows = [
        {
            "condition": name,
            "raw_peak_pa": float(np.max(np.abs(values))),
            "raw_rms_pa": EXP26.rms(values),
            "finite": bool(np.all(np.isfinite(values))),
            "source_sha256_float64": source_hash,
        }
        for name, values in waveforms.items()
    ]
    write_csv(output_dir / "signal_metrics.csv", signal_rows)

    task_endpoint_body_delta = np.abs(
        observed_peaks["M1_task_endpoint"][:2]
        - observed_peaks["M0_task_endpoint"][:2]
    )
    peak_tolerance_hz = float(oracle["model"]["peak_tolerance_hz"])
    body_effect_threshold_hz = MORPHOLOGY_EFFECT_MARGIN * peak_tolerance_hz
    body_effect_pass = bool(
        np.any(task_endpoint_body_delta > body_effect_threshold_hz)
    )

    representation_pass = bool(
        representation_clean
        and frozen_task_match
        and realizer_core_match
        and schedule_pass
    )
    physical_realization_pass = bool(
        coord_oracle_pass
        and metric_scale_pass
        and endpoint_area_equal
        and endpoint_length_scale_pass
    )
    implementation_pass = bool(
        oracle_pass
        and m0_v3a_peak_match
        and source_regression["pass"]
    )
    numerical_pass = bool(
        geometry_valid
        and trajectory_stable
        and all_finite
        and artifact_pass
        and temporal_pass
        and listening_no_clipping
    )

    if not representation_pass:
        decision_name = "REPRESENTATION_LEAK"
    elif not morphology_isolated:
        decision_name = "MORPHOLOGY_INTERVENTION_INVALID"
    elif not implementation_pass:
        decision_name = "IMPLEMENTATION_MISMATCH"
    elif not physical_realization_pass:
        decision_name = "MOTOR_REALIZATION_FAILED"
    elif not intent_retention_pass:
        decision_name = "ACOUSTIC_INTENT_RETENTION_FAILED"
    elif not transfer_stability_pass:
        decision_name = "TASK_TRANSFER_FAILED"
    elif not numerical_pass:
        decision_name = "NUMERICALLY_UNSTABLE"
    elif not body_effect_pass:
        decision_name = "MORPHOLOGY_EFFECT_UNRESOLVED"
    else:
        decision_name = "SUPPORT_TASK_TRANSFER"

    provenance = {
        "experiment": "028_task_field_morphology_transfer",
        "issue": 64,
        "parent_issue": 33,
        "reference_experiment": 27,
        "frozen_reference_preflight": preflight,
        "realizer_parameters_sha256": realizer_parameter_digest,
        "frozen_gate": FROZEN_GATE,
        "task_plan_sha256": {
            "M0": task_digest,
            "M1": task_digest,
        },
        "realizer_sha256": {
            "M0": realizer_digest,
            "M1": realizer_digest,
        },
        "observer_reference_policy": (
            "body-specific /i/ geometries are evaluation-only and are never "
            "passed to the task realizer"
        ),
        "morphology_intervention": morphologies["intervention"],
        "source": {
            "name": source_result.name,
            "f0_hz": EXP26.BASE_F0_HZ,
            "rd": EXP26.EXP13.RD,
            "sha256_float64": source_hash,
            "bytes_match_capture": source_bytes_match_capture,
            "byte_digest_is_diagnostic_only": True,
            "generator_identity_matches": preflight["checks"]["executed_implementation_matches"],
        },
        "renderer": {
            "transfer": "Experiment-009 far_field_pressure_transfer",
            "frame_renderer": "Experiment-012 frame_render",
            "edge_mode": "preroll_edge",
            "primary_hop_size": PRIMARY_HOP_SIZE,
            "reference_hop_size": REFERENCE_HOP_SIZE,
        },
        "oracle": {
            "path": "wolfram/v3b_oracle.json",
            "evaluated_before_python_execution": True,
            "exact_lossless_1_over_L_scaling_used_as_primary_gate": False,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }
    (output_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    decision = {
        "decision": decision_name,
        "preflight": preflight,
        "gates": {
            "representation_invariant": representation_pass,
            "morphology_intervention_isolated": morphology_isolated,
            "independent_oracle_and_baseline": implementation_pass,
            "body_specific_physical_realization": physical_realization_pass,
            "acoustic_intent_retention": intent_retention_pass,
            "task_transfer_stability": transfer_stability_pass,
            "dynamic_numerical_stability": numerical_pass,
            "resolved_body_acoustic_effect": body_effect_pass,
        },
        "task_plan": {
            "sha256_M0": task_digest,
            "sha256_M1": task_digest,
            "clean": representation_clean,
            "matches_v3a_and_v3b_frozen_oracles": frozen_task_match,
            "schedule_pass": schedule_pass,
            "schedule_checks": schedule_checks,
        },
        "realizer": {
            "sha256_M0": realizer_digest,
            "sha256_M1": realizer_digest,
            "frozen_core_match": realizer_core_match,
            "parameters_sha256": realizer_parameter_digest,
            "executed_implementation_matches_frozen_reference": True,
        },
        "morphology": {
            "isolated": morphology_isolated,
            "M0_total_length_m": total_length(m0_a),
            "M1_total_length_m": total_length(m1_a),
            "M1_over_M0_total_length": total_length(m1_a) / total_length(m0_a),
            "metric_coordinates_M0_m": coords0.tolist(),
            "metric_coordinates_M1_m": coords1.tolist(),
            "metric_coordinate_scales": coord_scales.tolist(),
            "metric_coordinate_scale_pass": metric_scale_pass,
            "endpoint_area_vectors_equal": endpoint_area_equal,
            "endpoint_section_length_scale_pass": endpoint_length_scale_pass,
        },
        "oracle_checks": oracle_checks,
        "M0_matches_experiment_027_peak_oracle_exactly": m0_v3a_peak_match,
        "endpoint_metrics": {
            "M0": metrics0,
            "M1": metrics1,
            "M1_error_ratio_limit": ENDPOINT_ERROR_RATIO_LIMIT,
            "cross_body_error_ratio_delta": transfer_delta,
            "cross_body_error_ratio_delta_limit": (
                TRANSFER_ERROR_RATIO_DELTA_LIMIT
            ),
        },
        "trajectory": {
            "M1_max_adjacent_p1p2_step_ratio": m1_step_ratio,
            "step_ratio_limit": TRAJECTORY_STEP_RATIO_LIMIT,
            "max_matched_time_M0_M1_p1p2_distance_hz": float(np.max(matched)),
        },
        "body_effect": {
            "M0_task_endpoint_p1p2_hz": (
                observed_peaks["M0_task_endpoint"][:2].tolist()
            ),
            "M1_task_endpoint_p1p2_hz": (
                observed_peaks["M1_task_endpoint"][:2].tolist()
            ),
            "absolute_p1p2_changes_hz": task_endpoint_body_delta.tolist(),
            "required_change_in_at_least_one_dimension_hz": (
                body_effect_threshold_hz
            ),
        },
        "source_regression": source_regression,
        "waveform": {
            "all_finite": all_finite,
            "transition_max_adjacent_sample_jump_pa": transition_jump,
            "endpoint_region_max_adjacent_sample_jump_pa": endpoint_jump,
            "artifact_jump_ratio": artifact_ratio,
            "artifact_jump_ratio_limit": ARTIFACT_JUMP_RATIO_LIMIT,
            "M1_temporal_normalized_rms_floor": temporal_floor,
            "temporal_stability_limit": TEMPORAL_STABILITY_LIMIT,
            "M0_M1_normalized_rms_difference": body_waveform_effect,
            "listening_no_clipping": listening_no_clipping,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": (
            "same frozen three-task plan transferred only across the specified "
            "1.10x axial-length morphology; not arbitrary morphology transfer "
            "or explicit embodied infeasibility"
        ),
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-028-output"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
