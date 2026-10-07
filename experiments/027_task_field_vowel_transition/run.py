from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import importlib.util
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
ORACLE_PATH = HERE / "wolfram" / "v3a_oracle.json"

ENDPOINT_ERROR_RATIO_LIMIT = 0.20
ARTIFACT_JUMP_RATIO_LIMIT = 3.0
TEMPORAL_STABILITY_LIMIT = 0.20
TRAJECTORY_STEP_RATIO_LIMIT = 0.20
LISTENING_PEAK = 0.90
RESONANCE_STEP_S = 0.010


@dataclass(frozen=True, slots=True)
class CandidateTask:
    task: str
    location: float
    degree: float
    onset_s: float
    offset_s: float

    def __post_init__(self) -> None:
        if self.task not in {"OPEN", "CONSTRICT"}:
            raise ValueError(f"unsupported candidate task: {self.task}")
        if not math.isfinite(self.location) or not 0.0 <= self.location <= 1.0:
            raise ValueError("task location must lie in [0, 1]")
        if not math.isfinite(self.degree) or not 0.0 <= self.degree <= 1.0:
            raise ValueError("task degree must lie in [0, 1]")
        if not math.isfinite(self.onset_s) or self.onset_s < 0.0:
            raise ValueError("task onset must be finite and >= 0")
        if not math.isfinite(self.offset_s) or self.offset_s <= self.onset_s:
            raise ValueError("task offset must be greater than onset")


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP26 = load_experiment_module(
    "morpho_exp026_for_027",
    EXPERIMENTS / "026_moving_vowel_transition" / "run.py",
)

SAMPLE_RATE_HZ = EXP26.SAMPLE_RATE_HZ
DURATION_S = EXP26.DURATION_S
PRIMARY_CONTROL_STEP_S = EXP26.PRIMARY_CONTROL_STEP_S
REFERENCE_CONTROL_STEP_S = EXP26.REFERENCE_CONTROL_STEP_S
PRIMARY_HOP_SIZE = EXP26.PRIMARY_HOP_SIZE
REFERENCE_HOP_SIZE = EXP26.REFERENCE_HOP_SIZE
TRANSITION_START_S = EXP26.TRANSITION_START_S
TRANSITION_END_S = EXP26.TRANSITION_END_S

TASKS = (
    CandidateTask(
        task="OPEN",
        location=0.3424849103873983,
        degree=0.5921764128805103,
        onset_s=TRANSITION_START_S,
        offset_s=TRANSITION_END_S,
    ),
    CandidateTask(
        task="CONSTRICT",
        location=0.7167402543883221,
        degree=0.9235962908995712,
        onset_s=TRANSITION_START_S,
        offset_s=TRANSITION_END_S,
    ),
    CandidateTask(
        task="CONSTRICT",
        location=1.0,
        degree=0.04495226070116771,
        onset_s=TRANSITION_START_S,
        offset_s=TRANSITION_END_S,
    ),
)

KAPPA = 1.5
SIGMA = 0.16
SIGMA_LIP = 0.10


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def task_plan_payload() -> list[dict[str, object]]:
    return [asdict(task) for task in TASKS]


def representation_is_clean(payload: list[dict[str, object]]) -> bool:
    allowed_keys = {"task", "location", "degree", "onset_s", "offset_s"}
    if not payload or any(set(item) != allowed_keys for item in payload):
        return False
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).lower()
    forbidden = (
        "section",
        "area",
        "diameter",
        "mesh",
        "node",
        "f1",
        "f2",
        "formant",
        "waveform",
        "spectrogram",
    )
    return not any(token in encoded for token in forbidden)


def section_coordinates(section_count: int) -> np.ndarray:
    if section_count < 2:
        raise ValueError("task-field realizer requires at least two sections")
    return np.linspace(0.0, 1.0, section_count, dtype=np.float64)


def gaussian_kernel(
    coordinates: np.ndarray,
    *,
    location: float,
    sigma: float,
) -> np.ndarray:
    values = np.asarray(coordinates, dtype=np.float64)
    return np.exp(-((values - location) ** 2) / (2.0 * sigma * sigma))


def task_log_diameter_delta_for(
    task: CandidateTask,
    section_count: int,
) -> np.ndarray:
    x = section_coordinates(section_count)
    sigma = SIGMA_LIP if task.location == 1.0 else SIGMA
    sign = 1.0 if task.task == "OPEN" else -1.0
    return KAPPA * sign * task.degree * gaussian_kernel(
        x,
        location=task.location,
        sigma=sigma,
    )


def task_log_diameter_delta(section_count: int) -> np.ndarray:
    return np.sum(
        [task_log_diameter_delta_for(task, section_count) for task in TASKS],
        axis=0,
    )


def analytic_task_activation_scalar(
    task: CandidateTask,
    time_s: float,
) -> float:
    if time_s <= task.onset_s:
        return 0.0
    if time_s >= task.offset_s:
        return 1.0
    u = (time_s - task.onset_s) / (task.offset_s - task.onset_s)
    return float(u * u * (3.0 - 2.0 * u))


def task_activation_at_time(
    task: CandidateTask,
    time_s: float,
    *,
    control_step_s: float,
) -> float:
    sample_times = EXP26.progress_sampling_grid(control_step_s)
    sample_values = np.asarray(
        [analytic_task_activation_scalar(task, float(t)) for t in sample_times],
        dtype=np.float64,
    )
    return float(np.interp(time_s, sample_times, sample_values))


def task_activations_at_time(
    time_s: float,
    *,
    control_step_s: float,
) -> tuple[float, ...]:
    return tuple(
        task_activation_at_time(
            task,
            time_s,
            control_step_s=control_step_s,
        )
        for task in TASKS
    )


def realize_task_geometry_from_activations(
    start: Tract1DGeometry,
    activations: tuple[float, ...],
    *,
    cavity_id: str,
) -> Tract1DGeometry:
    if len(activations) != len(TASKS):
        raise ValueError("one activation is required for each canonical task")
    if any(
        not math.isfinite(value) or not 0.0 <= value <= 1.0
        for value in activations
    ):
        raise ValueError("task activations must be finite and lie in [0, 1]")
    if all(value == 0.0 for value in activations):
        return start

    base_areas = EXP26.geometry_areas(start)
    lengths = EXP26.geometry_lengths(start)
    delta_log_diameter = np.zeros(len(start.sections), dtype=np.float64)
    for task, activation in zip(TASKS, activations, strict=True):
        delta_log_diameter += activation * task_log_diameter_delta_for(
            task,
            len(start.sections),
        )

    # A is proportional to D^2, so each independently scheduled
    # log-diameter task field maps to log-area with a factor of two.
    # The section vector is a realized body state, never a canonical command.
    areas = base_areas * np.exp(2.0 * delta_log_diameter)
    if np.any(~np.isfinite(areas)) or np.any(areas <= 0.0):
        raise RuntimeError("task-field realization produced invalid area")

    return Tract1DGeometry(
        cavity_id=cavity_id,
        sections=tuple(
            TubeSection(length_m=float(length), area_m2=float(area))
            for length, area in zip(lengths, areas, strict=True)
        ),
    )


def realize_task_geometry(
    start: Tract1DGeometry,
    progress: float,
    *,
    cavity_id: str,
) -> Tract1DGeometry:
    if not math.isfinite(progress) or not 0.0 <= progress <= 1.0:
        raise ValueError("progress must be finite and lie in [0, 1]")
    if progress == 0.0:
        return start

    return realize_task_geometry_from_activations(
        start,
        tuple(progress for _ in TASKS),
        cavity_id=cavity_id,
    )


def task_geometry_for_time(
    start: Tract1DGeometry,
    time_s: float,
    *,
    control_step_s: float,
    cavity_id: str,
) -> Tract1DGeometry:
    activations = task_activations_at_time(
        time_s,
        control_step_s=control_step_s,
    )
    return realize_task_geometry_from_activations(
        start,
        activations,
        cavity_id=cavity_id,
    )


def render_task_continuous(
    source: np.ndarray,
    start: Tract1DGeometry,
    *,
    control_step_s: float,
    hop_size: int,
    label: str,
) -> np.ndarray:
    def transfer_for_time(
        center_s: float,
        frequencies_hz: np.ndarray,
    ) -> np.ndarray:
        geometry = task_geometry_for_time(
            start,
            center_s,
            control_step_s=control_step_s,
            cavity_id=f"oral-v3a-{label}",
        )
        return EXP26.EXP9.far_field_pressure_transfer(geometry, frequencies_hz)

    return EXP26.EXP12.frame_render(
        np.asarray(source, dtype=np.float64),
        transfer_for_time,
        hop_size=hop_size,
        edge_mode="preroll_edge",
    )


def compare_array(
    observed: np.ndarray,
    expected: np.ndarray,
    *,
    rtol: float,
    atol: float,
) -> tuple[bool, float]:
    if observed.shape != expected.shape:
        return False, math.inf
    error = float(np.max(np.abs(observed - expected)))
    return bool(np.allclose(observed, expected, rtol=rtol, atol=atol)), error


def compare_peaks(
    observed: np.ndarray,
    expected: np.ndarray,
    *,
    tolerance_hz: float,
) -> tuple[bool, list[float]]:
    if observed.shape != expected.shape:
        return False, []
    errors = np.abs(observed - expected)
    return bool(np.all(errors <= tolerance_hz)), errors.tolist()


def trajectory(
    start: Tract1DGeometry,
    target_i: Tract1DGeometry,
    *,
    condition: str,
    control_step_s: float,
) -> tuple[list[dict[str, object]], np.ndarray]:
    rows: list[dict[str, object]] = []
    peaks: list[np.ndarray] = []
    times = np.arange(
        0.0,
        DURATION_S + RESONANCE_STEP_S / 2.0,
        RESONANCE_STEP_S,
        dtype=np.float64,
    )
    for time_s in times:
        progress = EXP26.progress_at_time(float(time_s), step_s=control_step_s)
        if condition == "R0_v2_prescribed":
            activations = tuple(progress for _ in TASKS)
            geometry = EXP26.interpolate_geometry(
                start,
                target_i,
                progress,
                mode="log_area",
                cavity_id="oral-v3a-r0",
            )
        elif condition == "R1_task_field":
            activations = task_activations_at_time(
                float(time_s),
                control_step_s=control_step_s,
            )
            geometry = task_geometry_for_time(
                start,
                float(time_s),
                control_step_s=control_step_s,
                cavity_id="oral-v3a-r1",
            )
        else:
            raise ValueError(condition)

        p = EXP26.peak_array(geometry, count=3)
        peaks.append(p)
        areas = EXP26.geometry_areas(geometry)
        rows.append(
            {
                "condition": condition,
                "time_s": float(time_s),
                "progress": progress,
                "task0_activation": activations[0],
                "task1_activation": activations[1],
                "task2_activation": activations[2],
                "p1_hz": float(p[0]),
                "p2_hz": float(p[1]),
                "p3_hz": float(p[2]),
                "min_area_m2": float(np.min(areas)),
                "max_area_m2": float(np.max(areas)),
            }
        )
    return rows, np.asarray(peaks, dtype=np.float64)


def task_area_rows(start: Tract1DGeometry) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for time_s in np.arange(
        0.0,
        DURATION_S + RESONANCE_STEP_S / 2.0,
        RESONANCE_STEP_S,
        dtype=np.float64,
    ):
        progress = EXP26.progress_at_time(
            float(time_s), step_s=PRIMARY_CONTROL_STEP_S
        )
        activations = task_activations_at_time(
            float(time_s),
            control_step_s=PRIMARY_CONTROL_STEP_S,
        )
        geometry = task_geometry_for_time(
            start,
            float(time_s),
            control_step_s=PRIMARY_CONTROL_STEP_S,
            cavity_id="oral-v3a-task-area-trace",
        )
        for section_index, section in enumerate(geometry.sections):
            rows.append(
                {
                    "time_s": float(time_s),
                    "progress": progress,
                    "task0_activation": activations[0],
                    "task1_activation": activations[1],
                    "task2_activation": activations[2],
                    "section_index": section_index,
                    "length_m": section.length_m,
                    "area_m2": section.area_m2,
                }
            )
    return rows


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))

    task_payload = task_plan_payload()
    (output_dir / "task_plan.json").write_text(
        json.dumps(task_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    realizer_payload = {
        "revision": "experiment-027-v3a-candidate-1",
        "coordinate_mapping": "section slots mapped uniformly to x=j/(N-1)",
        "field_space": "log_diameter",
        "kappa": KAPPA,
        "sigma": SIGMA,
        "sigma_lip": SIGMA_LIP,
        "area_relation": "log A = log A0 + 2 * activation * delta_log_diameter",
    }
    (output_dir / "realizer_parameters.json").write_text(
        json.dumps(realizer_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    representation_clean = representation_is_clean(task_payload)
    schedule_checks = [
        {
            "onset_activation": task_activation_at_time(
                task,
                task.onset_s,
                control_step_s=PRIMARY_CONTROL_STEP_S,
            ),
            "midpoint_activation": task_activation_at_time(
                task,
                0.5 * (task.onset_s + task.offset_s),
                control_step_s=PRIMARY_CONTROL_STEP_S,
            ),
            "offset_activation": task_activation_at_time(
                task,
                task.offset_s,
                control_step_s=PRIMARY_CONTROL_STEP_S,
            ),
        }
        for task in TASKS
    ]
    task_schedule_pass = all(
        math.isclose(check["onset_activation"], 0.0, rel_tol=0.0, abs_tol=1e-12)
        and math.isclose(check["midpoint_activation"], 0.5, rel_tol=0.0, abs_tol=1e-12)
        and math.isclose(check["offset_activation"], 1.0, rel_tol=0.0, abs_tol=1e-12)
        for check in schedule_checks
    )

    primary_a = EXP26.EXP23.primary_geometry("a")
    primary_i = EXP26.EXP23.primary_geometry("i")

    start_realized = realize_task_geometry(
        primary_a,
        0.0,
        cavity_id="start-realized",
    )
    start_exact = start_realized is primary_a

    task_endpoint = realize_task_geometry(
        primary_a,
        1.0,
        cavity_id="task-endpoint",
    )
    endpoint_areas = EXP26.geometry_areas(task_endpoint)
    expected_areas = np.asarray(
        oracle["endpoint_areas_m2"], dtype=np.float64
    )
    area_oracle_pass, area_max_error = compare_array(
        endpoint_areas,
        expected_areas,
        rtol=1e-12,
        atol=1e-15,
    )

    tolerance_hz = float(oracle["model"]["peak_tolerance_hz"])
    observed_peaks = {
        "a": EXP26.peak_array(primary_a, count=5),
        "i": EXP26.peak_array(primary_i, count=5),
        "task_endpoint": EXP26.peak_array(task_endpoint, count=5),
    }
    peak_oracle_checks: dict[str, dict[str, object]] = {}
    peak_oracle_pass = True
    for key, observed in observed_peaks.items():
        expected = np.asarray(
            oracle["peak_frequencies_hz"][key], dtype=np.float64
        )
        passed, errors = compare_peaks(
            observed,
            expected,
            tolerance_hz=tolerance_hz,
        )
        peak_oracle_pass = peak_oracle_pass and passed
        peak_oracle_checks[key] = {
            "observed_hz": observed.tolist(),
            "expected_hz": expected.tolist(),
            "abs_error_hz": errors,
            "pass": passed,
        }

    endpoint_distance_hz = float(
        np.linalg.norm(observed_peaks["a"][:2] - observed_peaks["i"][:2])
    )
    task_to_i_hz = float(
        np.linalg.norm(
            observed_peaks["task_endpoint"][:2] - observed_peaks["i"][:2]
        )
    )
    task_to_a_hz = float(
        np.linalg.norm(
            observed_peaks["task_endpoint"][:2] - observed_peaks["a"][:2]
        )
    )
    endpoint_error_ratio = task_to_i_hz / endpoint_distance_hz
    endpoint_accuracy_pass = bool(
        math.isfinite(endpoint_error_ratio)
        and endpoint_error_ratio <= ENDPOINT_ERROR_RATIO_LIMIT
    )
    closer_to_i_pass = bool(task_to_i_hz < task_to_a_hz)

    r0_rows, r0_peaks = trajectory(
        primary_a,
        primary_i,
        condition="R0_v2_prescribed",
        control_step_s=PRIMARY_CONTROL_STEP_S,
    )
    r1_rows, r1_peaks = trajectory(
        primary_a,
        primary_i,
        condition="R1_task_field",
        control_step_s=PRIMARY_CONTROL_STEP_S,
    )
    write_csv(output_dir / "resonance_trajectory.csv", r0_rows + r1_rows)
    write_csv(output_dir / "task_section_area_trajectory.csv", task_area_rows(primary_a))

    geometry_valid = bool(
        all(
            math.isfinite(float(row["min_area_m2"]))
            and float(row["min_area_m2"]) > 0.0
            and math.isfinite(float(row["max_area_m2"]))
            and float(row["max_area_m2"]) > 0.0
            for row in r1_rows
        )
    )
    r1_step_ratio = EXP26.max_trajectory_step_ratio(
        r1_peaks,
        endpoint_distance_hz,
    )
    trajectory_continuity_pass = bool(
        np.all(np.isfinite(r1_peaks))
        and r1_peaks.shape[1] >= 3
        and r1_step_ratio < TRAJECTORY_STEP_RATIO_LIMIT
    )

    matched_p1p2 = np.linalg.norm(
        r1_peaks[:, :2] - r0_peaks[:, :2], axis=1
    )
    trajectory_error_rows = [
        {
            "time_s": float(r1_rows[index]["time_s"]),
            "progress": float(r1_rows[index]["progress"]),
            "r0_p1_hz": float(r0_peaks[index, 0]),
            "r0_p2_hz": float(r0_peaks[index, 1]),
            "r1_p1_hz": float(r1_peaks[index, 0]),
            "r1_p2_hz": float(r1_peaks[index, 1]),
            "p1p2_distance_hz": float(matched_p1p2[index]),
            "distance_over_a_to_i_endpoint": float(
                matched_p1p2[index] / endpoint_distance_hz
            ),
        }
        for index in range(len(r1_rows))
    ]
    write_csv(output_dir / "r0_r1_trajectory_difference.csv", trajectory_error_rows)

    sources, _ = EXP26.EXP13.build_sources()
    source_result = sources["lf_fixed"]
    source = np.asarray(source_result.source, dtype=np.float64)
    source_regression = EXP26.source_regression(source_result)
    source_hash = EXP26.sha256_float64(source)

    r0 = EXP26.render_continuous(
        source,
        primary_a,
        primary_i,
        mode="log_area",
        control_step_s=PRIMARY_CONTROL_STEP_S,
        hop_size=PRIMARY_HOP_SIZE,
        label="v3a-r0",
    )
    r1 = render_task_continuous(
        source,
        primary_a,
        control_step_s=PRIMARY_CONTROL_STEP_S,
        hop_size=PRIMARY_HOP_SIZE,
        label="primary",
    )
    r1_ref = render_task_continuous(
        source,
        primary_a,
        control_step_s=REFERENCE_CONTROL_STEP_S,
        hop_size=REFERENCE_HOP_SIZE,
        label="reference",
    )

    waveforms = {
        "R0_v2_prescribed": r0,
        "R1_task_field": r1,
        "R1_reference_task_field": r1_ref,
    }
    all_finite = all(
        bool(np.all(np.isfinite(values))) for values in waveforms.values()
    )
    for name, values in waveforms.items():
        np.save(output_dir / f"{name}_raw_pressure_pa.npy", values)

    transition_jump, endpoint_jump, artifact_ratio = EXP26.artifact_jump_ratio(r1)
    artifact_pass = bool(
        math.isfinite(artifact_ratio)
        and artifact_ratio < ARTIFACT_JUMP_RATIO_LIMIT
    )

    temporal_floor = EXP26.normalized_rms_difference(r1, r1_ref)
    temporal_stability_pass = bool(
        math.isfinite(temporal_floor)
        and temporal_floor < TEMPORAL_STABILITY_LIMIT
    )
    r0_r1_waveform_difference = EXP26.normalized_rms_difference(r1, r0)
    effect_over_temporal_floor = (
        r0_r1_waveform_difference / temporal_floor
        if temporal_floor > 0.0
        else math.inf
    )

    comparison_for_listening = {
        "R0_v2_prescribed": r0,
        "R1_task_field": r1,
    }
    listening_gain = EXP26.common_listening_gain(comparison_for_listening)
    listening = {
        name: np.asarray(values * listening_gain, dtype=np.float64)
        for name, values in comparison_for_listening.items()
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

    implementation_oracle_pass = bool(
        start_exact
        and area_oracle_pass
        and peak_oracle_pass
        and source_regression["pass"]
        and task_schedule_pass
    )
    numerical_stability_pass = bool(
        geometry_valid
        and trajectory_continuity_pass
        and all_finite
        and artifact_pass
        and temporal_stability_pass
        and listening_no_clipping
    )
    representation_sufficient = bool(
        endpoint_accuracy_pass and closer_to_i_pass
    )

    if not representation_clean:
        decision_name = "REPRESENTATION_LEAK"
    elif not implementation_oracle_pass:
        decision_name = "IMPLEMENTATION_MISMATCH"
    elif not numerical_stability_pass:
        decision_name = "NUMERICALLY_UNSTABLE"
    elif not representation_sufficient:
        decision_name = "REPRESENTATION_INSUFFICIENT"
    else:
        decision_name = "ADOPT_TASK_FIELD_CANDIDATE"

    provenance = {
        "experiment": "027_task_field_vowel_transition",
        "issue": 62,
        "parent_issue": 33,
        "reference_experiment": 26,
        "candidate_scope": (
            "single calibrated body only; morphology transfer and infeasibility "
            "are explicitly deferred"
        ),
        "task_plan": task_payload,
        "realizer": realizer_payload,
        "transition": {
            "from": "calibrated_a",
            "intent": "i_like_endpoint",
            "start_s": TRANSITION_START_S,
            "end_s": TRANSITION_END_S,
            "progress": "Experiment-026 smoothstep with sampled linear reconstruction",
            "primary_control_step_s": PRIMARY_CONTROL_STEP_S,
            "reference_control_step_s": REFERENCE_CONTROL_STEP_S,
        },
        "source": {
            "name": source_result.name,
            "f0_hz": EXP26.BASE_F0_HZ,
            "rd": EXP26.EXP13.RD,
            "sha256_float64": source_hash,
        },
        "renderer": {
            "transfer": "Experiment-009 far_field_pressure_transfer",
            "frame_renderer": "Experiment-012 frame_render",
            "edge_mode": "preroll_edge",
            "primary_hop_size": PRIMARY_HOP_SIZE,
            "reference_hop_size": REFERENCE_HOP_SIZE,
        },
        "oracle": {
            "path": "wolfram/v3a_oracle.json",
            "evaluated_before_python_execution": True,
            "python_refit_forbidden": True,
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
        "gates": {
            "representation_clean": representation_clean,
            "implementation_oracle": implementation_oracle_pass,
            "numerical_stability": numerical_stability_pass,
            "representation_sufficient": representation_sufficient,
        },
        "start_exact_reproduction": start_exact,
        "task_schedule_checks": {
            "pass": task_schedule_pass,
            "tasks": schedule_checks,
        },
        "endpoint_area_oracle": {
            "pass": area_oracle_pass,
            "max_abs_error_m2": area_max_error,
        },
        "peak_oracle_checks": peak_oracle_checks,
        "endpoint_metrics": {
            "a_to_i_p1p2_distance_hz": endpoint_distance_hz,
            "task_to_i_p1p2_distance_hz": task_to_i_hz,
            "task_to_a_p1p2_distance_hz": task_to_a_hz,
            "task_to_i_over_a_to_i": endpoint_error_ratio,
            "limit": ENDPOINT_ERROR_RATIO_LIMIT,
            "endpoint_accuracy_pass": endpoint_accuracy_pass,
            "closer_to_i_pass": closer_to_i_pass,
        },
        "trajectory_metrics": {
            "r1_max_adjacent_p1p2_step_over_a_to_i": r1_step_ratio,
            "step_ratio_limit": TRAJECTORY_STEP_RATIO_LIMIT,
            "max_r0_r1_p1p2_distance_hz": float(np.max(matched_p1p2)),
            "max_r0_r1_distance_over_a_to_i": float(
                np.max(matched_p1p2) / endpoint_distance_hz
            ),
        },
        "source_regression": source_regression,
        "waveform_metrics": {
            "all_finite": all_finite,
            "transition_max_adjacent_sample_jump_pa": transition_jump,
            "endpoint_region_max_adjacent_sample_jump_pa": endpoint_jump,
            "artifact_jump_ratio": artifact_ratio,
            "artifact_jump_ratio_limit": ARTIFACT_JUMP_RATIO_LIMIT,
            "temporal_normalized_rms_floor": temporal_floor,
            "temporal_stability_limit": TEMPORAL_STABILITY_LIMIT,
            "r0_r1_normalized_rms_difference": r0_r1_waveform_difference,
            "r0_r1_effect_over_temporal_floor": effect_over_temporal_floor,
            "listening_no_clipping": listening_no_clipping,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": (
            "low-dimensional task-field candidate on one calibrated body only; "
            "not morphology transfer, natural speech, or production motor control"
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
        default=Path("experiment-027-output"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
