from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import platform
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Literal

import numpy as np

from morphoacoustics.physical import Tract1DGeometry, TubeSection

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "v2_oracle.json"

TRANSITION_START_S = 0.150
TRANSITION_END_S = 0.350
PRIMARY_CONTROL_STEP_S = 0.005
REFERENCE_CONTROL_STEP_S = 0.0025
PRIMARY_HOP_SIZE = 256
REFERENCE_HOP_SIZE = 128
RESONANCE_STEP_S = 0.010
TEMPORAL_STABILITY_LIMIT = 0.20
DISCRIMINATION_MARGIN = 5.0
ARTIFACT_JUMP_RATIO_LIMIT = 3.0
TRAJECTORY_STEP_RATIO_LIMIT = 0.20
SPATIAL_PATH_RATIO_LIMIT = 0.20
SOURCE_CYCLE_JUMP_LIMIT = 0.01
LISTENING_PEAK = 0.90
RNG_SEED = 26026

InterpolationMode = Literal["log_area", "linear_area"]


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP23 = load_experiment_module(
    "morpho_exp023_for_026",
    EXPERIMENTS / "023_static_vowel_calibration" / "run.py",
)
EXP13 = EXP23.EXP13
EXP12 = EXP23.EXP12
EXP9 = EXP23.EXP9

SAMPLE_RATE_HZ = EXP23.SAMPLE_RATE_HZ
DURATION_S = EXP23.DURATION_S
BASE_F0_HZ = EXP23.BASE_F0_HZ


def rms(values: np.ndarray) -> float:
    array = np.asarray(values, dtype=np.float64)
    return float(np.sqrt(np.mean(array * array)))


def sha256_float64(values: np.ndarray) -> str:
    array = np.asarray(values, dtype="<f8")
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def analytic_progress_scalar(time_s: float) -> float:
    if time_s <= TRANSITION_START_S:
        return 0.0
    if time_s >= TRANSITION_END_S:
        return 1.0
    u = (time_s - TRANSITION_START_S) / (
        TRANSITION_END_S - TRANSITION_START_S
    )
    return float(u * u * (3.0 - 2.0 * u))


def analytic_progress(times_s: np.ndarray) -> np.ndarray:
    times = np.asarray(times_s, dtype=np.float64)
    values = np.empty_like(times)
    before = times <= TRANSITION_START_S
    after = times >= TRANSITION_END_S
    middle = ~(before | after)
    values[before] = 0.0
    values[after] = 1.0
    u = (times[middle] - TRANSITION_START_S) / (
        TRANSITION_END_S - TRANSITION_START_S
    )
    values[middle] = u * u * (3.0 - 2.0 * u)
    return values


def progress_sampling_grid(step_s: float) -> np.ndarray:
    first = math.floor(-step_s / step_s) - 1
    last = math.ceil((DURATION_S + step_s) / step_s) + 1
    return np.arange(first, last + 1, dtype=np.float64) * step_s


def reconstructed_progress(times_s: np.ndarray, *, step_s: float) -> np.ndarray:
    sample_times = progress_sampling_grid(step_s)
    sample_values = analytic_progress(sample_times)
    return np.interp(
        np.asarray(times_s, dtype=np.float64),
        sample_times,
        sample_values,
    )


def progress_at_time(time_s: float, *, step_s: float) -> float:
    return float(
        reconstructed_progress(
            np.asarray([time_s], dtype=np.float64), step_s=step_s
        )[0]
    )


def geometry_areas(geometry: Tract1DGeometry) -> np.ndarray:
    return np.asarray(
        [section.area_m2 for section in geometry.sections], dtype=np.float64
    )


def geometry_lengths(geometry: Tract1DGeometry) -> np.ndarray:
    return np.asarray(
        [section.length_m for section in geometry.sections], dtype=np.float64
    )


def interpolate_geometry(
    start: Tract1DGeometry,
    end: Tract1DGeometry,
    progress: float,
    *,
    mode: InterpolationMode,
    cavity_id: str,
) -> Tract1DGeometry:
    if not (0.0 <= progress <= 1.0) or not math.isfinite(progress):
        raise ValueError(f"progress must be finite in [0, 1], got {progress}")
    if len(start.sections) != len(end.sections):
        raise ValueError("endpoint section counts must match")

    start_lengths = geometry_lengths(start)
    end_lengths = geometry_lengths(end)
    if not np.array_equal(start_lengths, end_lengths):
        raise ValueError("endpoint section lengths must match exactly")

    if progress == 0.0:
        return start
    if progress == 1.0:
        return end

    a0 = geometry_areas(start)
    a1 = geometry_areas(end)
    if np.any(a0 <= 0.0) or np.any(a1 <= 0.0):
        raise ValueError("endpoint areas must be positive")

    if mode == "log_area":
        areas = np.exp((1.0 - progress) * np.log(a0) + progress * np.log(a1))
    elif mode == "linear_area":
        areas = (1.0 - progress) * a0 + progress * a1
    else:
        raise AssertionError(mode)

    if np.any(~np.isfinite(areas)) or np.any(areas <= 0.0):
        raise RuntimeError(f"{mode}: invalid interpolated area")

    return Tract1DGeometry(
        cavity_id=cavity_id,
        sections=tuple(
            TubeSection(length_m=float(length), area_m2=float(area))
            for length, area in zip(start_lengths, areas, strict=True)
        ),
    )


def geometry_for_time(
    start: Tract1DGeometry,
    end: Tract1DGeometry,
    time_s: float,
    *,
    mode: InterpolationMode,
    control_step_s: float,
    cavity_id: str,
) -> Tract1DGeometry:
    return interpolate_geometry(
        start,
        end,
        progress_at_time(time_s, step_s=control_step_s),
        mode=mode,
        cavity_id=cavity_id,
    )


def render_static_segment(
    source: np.ndarray, geometry: Tract1DGeometry
) -> np.ndarray:
    def transfer_for_time(_: float, frequencies_hz: np.ndarray) -> np.ndarray:
        return EXP9.far_field_pressure_transfer(geometry, frequencies_hz)

    return EXP12.frame_render(
        np.asarray(source, dtype=np.float64),
        transfer_for_time,
        hop_size=PRIMARY_HOP_SIZE,
        edge_mode="preroll_edge",
    )


def render_static_concat(
    source: np.ndarray,
    start: Tract1DGeometry,
    end: Tract1DGeometry,
) -> np.ndarray:
    midpoint = source.size // 2
    left = render_static_segment(source[:midpoint], start)
    right = render_static_segment(source[midpoint:], end)
    return np.concatenate([left, right]).astype(np.float64, copy=False)


def render_continuous(
    source: np.ndarray,
    start: Tract1DGeometry,
    end: Tract1DGeometry,
    *,
    mode: InterpolationMode,
    control_step_s: float,
    hop_size: int,
    label: str,
) -> np.ndarray:
    def transfer_for_time(
        center_s: float, frequencies_hz: np.ndarray
    ) -> np.ndarray:
        geometry = geometry_for_time(
            start,
            end,
            center_s,
            mode=mode,
            control_step_s=control_step_s,
            cavity_id=f"oral-vowel-a-i-{label}-{mode}",
        )
        return EXP9.far_field_pressure_transfer(geometry, frequencies_hz)

    return EXP12.frame_render(
        np.asarray(source, dtype=np.float64),
        transfer_for_time,
        hop_size=hop_size,
        edge_mode="preroll_edge",
    )


def normalized_rms_difference(
    candidate: np.ndarray, reference: np.ndarray
) -> float:
    denominator = rms(reference)
    if not math.isfinite(denominator) or denominator <= 0.0:
        return math.inf
    return float(rms(np.asarray(candidate) - np.asarray(reference)) / denominator)


def peak_array(
    geometry: Tract1DGeometry, count: int = 5
) -> np.ndarray:
    return EXP23.peak_frequencies(geometry, count=count)


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


def trajectory_rows(
    start: Tract1DGeometry,
    end: Tract1DGeometry,
    *,
    mode: InterpolationMode,
    control_step_s: float,
    label: str,
) -> tuple[list[dict[str, object]], np.ndarray]:
    times = np.arange(
        0.0,
        DURATION_S + RESONANCE_STEP_S / 2.0,
        RESONANCE_STEP_S,
        dtype=np.float64,
    )
    rows: list[dict[str, object]] = []
    peak_values: list[np.ndarray] = []
    for time_s in times:
        progress = progress_at_time(float(time_s), step_s=control_step_s)
        geometry = interpolate_geometry(
            start,
            end,
            progress,
            mode=mode,
            cavity_id=f"oral-vowel-a-i-{label}-{mode}",
        )
        peaks = peak_array(geometry, count=3)
        peak_values.append(peaks)
        rows.append(
            {
                "path": label,
                "mode": mode,
                "time_s": float(time_s),
                "progress": progress,
                "p1_hz": float(peaks[0]),
                "p2_hz": float(peaks[1]),
                "p3_hz": float(peaks[2]),
                "min_area_m2": float(np.min(geometry_areas(geometry))),
                "max_area_m2": float(np.max(geometry_areas(geometry))),
            }
        )
    return rows, np.asarray(peak_values, dtype=np.float64)


def area_trajectory_rows(
    start: Tract1DGeometry,
    end: Tract1DGeometry,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for time_s in np.arange(
        0.0,
        DURATION_S + RESONANCE_STEP_S / 2.0,
        RESONANCE_STEP_S,
    ):
        progress = progress_at_time(
            float(time_s), step_s=PRIMARY_CONTROL_STEP_S
        )
        geometry = interpolate_geometry(
            start,
            end,
            progress,
            mode="log_area",
            cavity_id="oral-vowel-a-i-area-log",
        )
        for section_index, section in enumerate(geometry.sections):
            rows.append(
                {
                    "time_s": float(time_s),
                    "progress": progress,
                    "section_index": section_index,
                    "length_m": section.length_m,
                    "area_m2": section.area_m2,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def artifact_jump_ratio(
    values: np.ndarray,
) -> tuple[float, float, float]:
    pressure = np.asarray(values, dtype=np.float64)
    jumps = np.abs(np.diff(pressure))
    times = np.arange(1, pressure.size, dtype=np.float64) / SAMPLE_RATE_HZ
    transition = (times >= TRANSITION_START_S) & (
        times <= TRANSITION_END_S
    )
    steady_a = (times >= 0.05) & (times <= 0.14)
    steady_i = (times >= 0.36) & (times <= 0.45)

    transition_max = float(np.max(jumps[transition]))
    endpoint_max = max(
        float(np.max(jumps[steady_a])),
        float(np.max(jumps[steady_i])),
    )
    ratio = transition_max / max(
        endpoint_max, np.finfo(np.float64).tiny
    )
    return transition_max, endpoint_max, float(ratio)


def max_trajectory_step_ratio(
    peaks: np.ndarray, endpoint_distance_hz: float
) -> float:
    steps = np.linalg.norm(np.diff(peaks[:, :2], axis=0), axis=1)
    return float(np.max(steps) / endpoint_distance_hz)


def spatial_path_ratio(
    primary_peaks: np.ndarray,
    refined_peaks: np.ndarray,
    endpoint_distance_hz: float,
) -> tuple[float, float]:
    deltas = np.linalg.norm(
        primary_peaks[:, :2] - refined_peaks[:, :2], axis=1
    )
    maximum = float(np.max(deltas))
    return maximum, float(maximum / endpoint_distance_hz)


def source_regression(source_result: object) -> dict[str, object]:
    planned = np.asarray(source_result.planned_f0_hz, dtype=np.float64)
    noise = np.asarray(source_result.noise, dtype=np.float64)
    f0_fixed = bool(
        np.allclose(planned, BASE_F0_HZ, rtol=0.0, atol=1e-12)
    )
    noise_zero = bool(np.all(noise == 0.0))
    cycle_jump = float(EXP13.cycle_boundary_jump_ratio(source_result))
    return {
        "source_name": source_result.name,
        "planned_f0_fixed_100_hz": f0_fixed,
        "noise_component_exactly_zero": noise_zero,
        "cycle_boundary_jump_per_rms": cycle_jump,
        "cycle_boundary_jump_limit": SOURCE_CYCLE_JUMP_LIMIT,
        "pass": bool(
            source_result.name == "lf_fixed"
            and f0_fixed
            and noise_zero
            and math.isfinite(cycle_jump)
            and cycle_jump < SOURCE_CYCLE_JUMP_LIMIT
        ),
    }


def common_listening_gain(
    waveforms: dict[str, np.ndarray]
) -> float:
    peak = max(
        float(np.max(np.abs(values))) for values in waveforms.values()
    )
    if not math.isfinite(peak) or peak <= 0.0:
        raise RuntimeError("cannot normalize invalid comparison waveforms")
    return LISTENING_PEAK / peak


def make_blind_package(
    output_dir: Path,
    listening: dict[str, np.ndarray],
) -> None:
    blind_dir = output_dir / "listening" / "transition_blind"
    blind_dir.mkdir(parents=True, exist_ok=True)
    conditions = ["T0_static_concat", "T1_continuous_log"]
    rng = np.random.default_rng(RNG_SEED)
    order = list(rng.permutation(conditions))

    public_rows: list[dict[str, object]] = []
    key_rows: list[dict[str, object]] = []
    for index, condition in enumerate(order, start=1):
        trial_id = f"X{index:02d}"
        filename = f"{trial_id}.wav"
        EXP23.write_wav(blind_dir / filename, listening[str(condition)])
        public_rows.append({"trial_id": trial_id, "file": filename})
        key_rows.append(
            {
                "trial_id": trial_id,
                "condition": str(condition),
                "file": filename,
            }
        )

    write_csv(blind_dir / "manifest.csv", public_rows)
    write_csv(
        blind_dir / "response_template.csv",
        [
            {
                "trial_id": row["trial_id"],
                "file": row["file"],
                "click_snap_reset": "",
                "pasted_vs_single_motion": "",
                "smooth_transition": "",
                "voice_like_quality": "",
                "notes": "",
            }
            for row in public_rows
        ],
    )
    write_csv(output_dir / "blind_key.csv", key_rows)
    (blind_dir / "README.txt").write_text(
        "Experiment 026 exploratory transition listening\n"
        "Do not inspect blind_key.csv before freezing observations.\n"
        "For each file record click/snap/reset, pasted-vs-single-motion, "
        "transition smoothness, voice-like quality, and notes.\n"
        "This is not the primary scientific Gate and is not an open-set speech test.\n",
        encoding="utf-8",
    )


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    tolerance_hz = float(oracle["model"]["peak_tolerance_hz"])

    primary_a = EXP23.primary_geometry("a")
    primary_i = EXP23.primary_geometry("i")
    refined_a = EXP23.refined_geometry("a")
    refined_i = EXP23.refined_geometry("i")

    endpoint_exact = (
        interpolate_geometry(
            primary_a,
            primary_i,
            0.0,
            mode="log_area",
            cavity_id="endpoint-a",
        )
        is primary_a
        and interpolate_geometry(
            primary_a,
            primary_i,
            1.0,
            mode="log_area",
            cavity_id="endpoint-i",
        )
        is primary_i
    )

    observed_oracles = {
        "a": peak_array(primary_a),
        "i": peak_array(primary_i),
        "log_midpoint": peak_array(
            interpolate_geometry(
                primary_a,
                primary_i,
                0.5,
                mode="log_area",
                cavity_id="log-midpoint",
            )
        ),
        "linear_midpoint": peak_array(
            interpolate_geometry(
                primary_a,
                primary_i,
                0.5,
                mode="linear_area",
                cavity_id="linear-midpoint",
            )
        ),
    }

    oracle_checks: dict[str, dict[str, object]] = {}
    oracle_pass = True
    for key, observed in observed_oracles.items():
        expected = np.asarray(
            oracle["peak_frequencies_hz"][key], dtype=np.float64
        )
        passed, errors = compare_peaks(
            observed, expected, tolerance_hz=tolerance_hz
        )
        oracle_pass = oracle_pass and passed
        oracle_checks[key] = {
            "observed_hz": observed.tolist(),
            "expected_hz": expected.tolist(),
            "abs_error_hz": errors,
            "pass": passed,
        }

    midpoint_area_checks: dict[str, object] = {}
    for mode, oracle_key in (
        ("log_area", "log"),
        ("linear_area", "linear"),
    ):
        geometry = interpolate_geometry(
            primary_a,
            primary_i,
            0.5,
            mode=mode,
            cavity_id=f"{mode}-midpoint-area-check",
        )
        observed = geometry_areas(geometry)
        expected = np.asarray(
            oracle["midpoint_areas_m2"][oracle_key], dtype=np.float64
        )
        midpoint_area_checks[mode] = {
            "max_abs_error_m2": float(
                np.max(np.abs(observed - expected))
            ),
            "pass": bool(
                np.allclose(observed, expected, rtol=1e-12, atol=1e-15)
            ),
        }

    dense_times = np.arange(
        0.0, DURATION_S + 0.000005, 0.00001
    )
    analytic = analytic_progress(dense_times)
    progress_errors: dict[str, float] = {}
    progress_pass = True
    for name, step, oracle_field in (
        (
            "primary_5ms",
            PRIMARY_CONTROL_STEP_S,
            "primary_max_abs_progress_reconstruction_error",
        ),
        (
            "reference_2p5ms",
            REFERENCE_CONTROL_STEP_S,
            "reference_max_abs_progress_reconstruction_error",
        ),
    ):
        reconstructed = reconstructed_progress(dense_times, step_s=step)
        error = float(np.max(np.abs(analytic - reconstructed)))
        bound = float(oracle["trajectory"][oracle_field])
        progress_errors[name] = error
        progress_pass = progress_pass and bool(
            error <= bound + 1e-12
        )

    progress_rows = [
        {
            "time_s": float(time_s),
            "analytic_progress": analytic_progress_scalar(
                float(time_s)
            ),
            "primary_reconstructed_progress": progress_at_time(
                float(time_s), step_s=PRIMARY_CONTROL_STEP_S
            ),
            "reference_reconstructed_progress": progress_at_time(
                float(time_s), step_s=REFERENCE_CONTROL_STEP_S
            ),
        }
        for time_s in np.arange(
            0.0,
            DURATION_S + RESONANCE_STEP_S / 2.0,
            RESONANCE_STEP_S,
        )
    ]
    write_csv(
        output_dir / "progress_trajectory.csv", progress_rows
    )

    primary_rows, primary_peaks = trajectory_rows(
        primary_a,
        primary_i,
        mode="log_area",
        control_step_s=PRIMARY_CONTROL_STEP_S,
        label="primary_16x10mm",
    )
    refined_rows, refined_peaks = trajectory_rows(
        refined_a,
        refined_i,
        mode="log_area",
        control_step_s=PRIMARY_CONTROL_STEP_S,
        label="refined_32x5mm",
    )
    write_csv(
        output_dir / "resonance_trajectory.csv",
        primary_rows + refined_rows,
    )
    write_csv(
        output_dir / "section_area_trajectory.csv",
        area_trajectory_rows(primary_a, primary_i),
    )

    geometry_valid = bool(
        all(
            math.isfinite(float(row["min_area_m2"]))
            and float(row["min_area_m2"]) > 0.0
            and math.isfinite(float(row["max_area_m2"]))
            and float(row["max_area_m2"]) > 0.0
            for row in primary_rows + refined_rows
        )
    )

    endpoint_distance_hz = float(
        np.linalg.norm(
            observed_oracles["a"][:2]
            - observed_oracles["i"][:2]
        )
    )
    primary_step_ratio = max_trajectory_step_ratio(
        primary_peaks, endpoint_distance_hz
    )
    refined_step_ratio = max_trajectory_step_ratio(
        refined_peaks, endpoint_distance_hz
    )
    spatial_max_delta_hz, spatial_ratio = spatial_path_ratio(
        primary_peaks, refined_peaks, endpoint_distance_hz
    )

    spatial_rows = []
    for primary_row, refined_row in zip(
        primary_rows, refined_rows, strict=True
    ):
        delta = math.hypot(
            float(primary_row["p1_hz"])
            - float(refined_row["p1_hz"]),
            float(primary_row["p2_hz"])
            - float(refined_row["p2_hz"]),
        )
        spatial_rows.append(
            {
                "time_s": float(primary_row["time_s"]),
                "progress": float(primary_row["progress"]),
                "primary_p1_hz": float(primary_row["p1_hz"]),
                "primary_p2_hz": float(primary_row["p2_hz"]),
                "refined_p1_hz": float(refined_row["p1_hz"]),
                "refined_p2_hz": float(refined_row["p2_hz"]),
                "p1p2_displacement_hz": delta,
                "displacement_over_primary_endpoint_distance": (
                    delta / endpoint_distance_hz
                ),
            }
        )
    write_csv(
        output_dir / "spatial_diagnostics.csv", spatial_rows
    )

    inherited_primary_peaks = {
        vowel: peak_array(EXP23.primary_geometry(vowel), count=2)
        for vowel in ("a", "i", "u")
    }
    inherited_refined_peaks = {
        vowel: peak_array(EXP23.refined_geometry(vowel), count=2)
        for vowel in ("a", "i", "u")
    }
    inherited_between = [
        float(
            np.linalg.norm(
                inherited_primary_peaks[left]
                - inherited_primary_peaks[right]
            )
        )
        for left, right in itertools.combinations(
            ("a", "i", "u"), 2
        )
    ]
    inherited_regrid = [
        float(
            np.linalg.norm(
                inherited_primary_peaks[vowel]
                - inherited_refined_peaks[vowel]
            )
        )
        for vowel in ("a", "i", "u")
    ]
    spatial_prerequisite_ratio = min(inherited_between) / max(
        max(inherited_regrid), np.finfo(np.float64).tiny
    )
    spatial_prerequisite_pass = bool(
        spatial_prerequisite_ratio > 5.0
    )

    resonance_tracking_pass = bool(
        np.all(np.isfinite(primary_peaks))
        and primary_peaks.shape[1] >= 3
        and primary_step_ratio < TRAJECTORY_STEP_RATIO_LIMIT
    )
    spatial_path_pass = bool(
        np.all(np.isfinite(refined_peaks))
        and refined_peaks.shape[1] >= 3
        and refined_step_ratio < TRAJECTORY_STEP_RATIO_LIMIT
        and spatial_ratio < SPATIAL_PATH_RATIO_LIMIT
    )

    sources, _ = EXP13.build_sources()
    source_result = sources["lf_fixed"]
    source = np.asarray(source_result.source, dtype=np.float64)
    source_check = source_regression(source_result)
    source_hash = sha256_float64(source)

    t0 = render_static_concat(source, primary_a, primary_i)
    t1 = render_continuous(
        source,
        primary_a,
        primary_i,
        mode="log_area",
        control_step_s=PRIMARY_CONTROL_STEP_S,
        hop_size=PRIMARY_HOP_SIZE,
        label="primary",
    )
    t1_ref = render_continuous(
        source,
        primary_a,
        primary_i,
        mode="log_area",
        control_step_s=REFERENCE_CONTROL_STEP_S,
        hop_size=REFERENCE_HOP_SIZE,
        label="reference",
    )
    t2 = render_continuous(
        source,
        primary_a,
        primary_i,
        mode="linear_area",
        control_step_s=PRIMARY_CONTROL_STEP_S,
        hop_size=PRIMARY_HOP_SIZE,
        label="linear-diagnostic",
    )

    waveforms = {
        "T0_static_concat": t0,
        "T1_continuous_log": t1,
        "T1_reference_log": t1_ref,
        "T2_continuous_linear": t2,
    }
    all_finite = all(
        bool(np.all(np.isfinite(values)))
        for values in waveforms.values()
    )
    for name, values in waveforms.items():
        np.save(
            output_dir / f"{name}_raw_pressure_pa.npy",
            values,
        )

    (
        transition_max_jump,
        endpoint_max_jump,
        jump_ratio,
    ) = artifact_jump_ratio(t1)
    artifact_pass = bool(
        math.isfinite(jump_ratio)
        and jump_ratio < ARTIFACT_JUMP_RATIO_LIMIT
    )

    temporal_floor = normalized_rms_difference(t1, t1_ref)
    transition_effect = normalized_rms_difference(t1, t0)
    temporal_stable = bool(
        math.isfinite(temporal_floor)
        and temporal_floor < TEMPORAL_STABILITY_LIMIT
    )
    effect_resolved = bool(
        math.isfinite(transition_effect)
        and transition_effect
        > DISCRIMINATION_MARGIN * temporal_floor
    )

    listening_subset = {
        "T0_static_concat": t0,
        "T1_continuous_log": t1,
        "T2_continuous_linear": t2,
    }
    listening_gain = common_listening_gain(listening_subset)
    listening = {
        name: np.asarray(values * listening_gain, dtype=np.float64)
        for name, values in listening_subset.items()
    }
    listening_dir = output_dir / "listening" / "named"
    listening_dir.mkdir(parents=True, exist_ok=True)
    for name, values in listening.items():
        EXP23.write_wav(
            listening_dir / f"{name}.wav", values
        )
    make_blind_package(output_dir, listening)

    signal_rows: list[dict[str, object]] = []
    for name, values in waveforms.items():
        signal_rows.append(
            {
                "condition": name,
                "raw_peak_pa": float(np.max(np.abs(values))),
                "raw_rms_pa": rms(values),
                "finite": bool(np.all(np.isfinite(values))),
                "source_sha256_float64": source_hash,
            }
        )
    write_csv(
        output_dir / "signal_metrics.csv", signal_rows
    )

    gate_endpoint = bool(
        endpoint_exact
        and oracle_pass
        and all(
            bool(value["pass"])
            for value in midpoint_area_checks.values()
        )
    )
    gate_geometry = geometry_valid
    gate_source_single_pass = bool(source_check["pass"])
    gate_artifact = bool(all_finite and artifact_pass)
    gate_resonance = resonance_tracking_pass
    gate_temporal = bool(
        temporal_stable and effect_resolved
    )
    gate_spatial = bool(
        spatial_prerequisite_pass and spatial_path_pass
    )

    if not gate_endpoint:
        decision_name = "STATIC_ENDPOINT_REGRESSION"
    elif not (
        gate_geometry
        and progress_pass
        and gate_source_single_pass
    ):
        decision_name = "ACOUSTIC_TRANSITION_FAILED"
    elif not (gate_artifact and gate_resonance):
        decision_name = "ACOUSTIC_TRANSITION_FAILED"
    elif not gate_temporal:
        decision_name = "NUMERICALLY_UNRESOLVED"
    elif not gate_spatial:
        decision_name = "SPATIAL_PATH_SENSITIVE"
    else:
        decision_name = "SUPPORT_MOVING_ACOUSTICS"

    provenance = {
        "experiment": "026_moving_vowel_transition",
        "issue": 32,
        "model_class": (
            "quasi-stationary time-varying short-time transfer filtering; "
            "no moving-domain PDE and no carried acoustic state between frames"
        ),
        "primary_transition": {
            "from": "a",
            "to": "i",
            "interpolation": "log_area",
            "progress": "smoothstep",
            "start_s": TRANSITION_START_S,
            "end_s": TRANSITION_END_S,
            "control_step_s": PRIMARY_CONTROL_STEP_S,
            "frame_size": EXP12.FRAME_SIZE,
            "hop_size": PRIMARY_HOP_SIZE,
            "single_full_duration_renderer_call": True,
        },
        "reference_transition": {
            "control_step_s": REFERENCE_CONTROL_STEP_S,
            "frame_size": EXP12.FRAME_SIZE,
            "hop_size": REFERENCE_HOP_SIZE,
        },
        "source": {
            "name": source_result.name,
            "f0_hz": BASE_F0_HZ,
            "rd": EXP13.RD,
            "sha256_float64": source_hash,
            "diagnostic_experiment_025_source_excluded": True,
        },
        "endpoint_fixture": {
            "source_url": EXP23.SOURCE_URL,
            "citation": EXP23.SOURCE_CITATION,
            "primary": (
                "Experiment 023 literal Arai 16x10mm /a/ and /i/"
            ),
            "spatial_diagnostic": (
                "Experiment 023 32x5mm center regrid"
            ),
        },
        "renderer": {
            "transfer": (
                "Experiment 009 far_field_pressure_transfer"
            ),
            "frame_renderer": (
                "Experiment 012 frame_render"
            ),
            "edge_mode": "preroll_edge",
        },
        "listening": {
            "normalization": (
                "one common gain across T0/T1/T2 preserving relative "
                "level, global peak -> 0.90 full scale"
            ),
            "common_gain_fullscale_per_pa": listening_gain,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }
    (output_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )

    decision = {
        "decision": decision_name,
        "gates": {
            "endpoint_oracle_reproduction": gate_endpoint,
            "geometry_validity": gate_geometry,
            "progress_reconstruction": progress_pass,
            "source_regression_and_single_pass_contract": (
                gate_source_single_pass
            ),
            "finite_and_artifact": gate_artifact,
            "resonance_tracking": gate_resonance,
            "temporal_convergence_and_effect_resolution": (
                gate_temporal
            ),
            "spatial_path_diagnostic": gate_spatial,
        },
        "oracle_checks": oracle_checks,
        "midpoint_area_checks": midpoint_area_checks,
        "progress_max_abs_error": progress_errors,
        "source_regression": source_check,
        "endpoint_p1p2_distance_hz": endpoint_distance_hz,
        "primary_max_adjacent_p1p2_step_ratio": (
            primary_step_ratio
        ),
        "refined_max_adjacent_p1p2_step_ratio": (
            refined_step_ratio
        ),
        "spatial_max_primary_refined_p1p2_delta_hz": (
            spatial_max_delta_hz
        ),
        "spatial_max_primary_refined_ratio": spatial_ratio,
        "spatial_path_ratio_limit": SPATIAL_PATH_RATIO_LIMIT,
        "inherited_endpoint_spatial_separation_ratio": (
            spatial_prerequisite_ratio
        ),
        "transition_max_adjacent_sample_jump_pa": (
            transition_max_jump
        ),
        "endpoint_region_max_adjacent_sample_jump_pa": (
            endpoint_max_jump
        ),
        "transition_to_endpoint_jump_ratio": jump_ratio,
        "artifact_jump_ratio_limit": ARTIFACT_JUMP_RATIO_LIMIT,
        "temporal_normalized_rms_floor": temporal_floor,
        "temporal_stability_limit": TEMPORAL_STABILITY_LIMIT,
        "t0_vs_t1_normalized_rms_effect": transition_effect,
        "required_effect_over_temporal_floor": (
            DISCRIMINATION_MARGIN
        ),
        "effect_over_temporal_floor": (
            transition_effect / temporal_floor
            if temporal_floor > 0.0
            else math.inf
        ),
        "all_waveforms_finite": all_finite,
        "source_sha256_float64": source_hash,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": (
            "prescribed /a/->/i/ moving acoustics only; not "
            "task-level articulation, natural speech, "
            "moving-boundary FSI, or general TTS"
        ),
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-026-output"),
    )
    args = parser.parse_args()
    print(
        json.dumps(
            run(args.output_dir),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
