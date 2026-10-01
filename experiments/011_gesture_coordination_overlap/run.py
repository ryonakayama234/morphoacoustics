from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import numpy as np

from morphoacoustics import Gesture, GestureScore, Task, TaskParameter, simulate_snapshot
from morphoacoustics.acoustics import ImpedanceRequest, SegmentedTubeBackend
from morphoacoustics.physical import Tract1DGeometry
from morphoacoustics.realization import Tract1DRealizer

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "coordination_oracle.json"

SAMPLE_RATE_HZ = 48_000
DURATION_S = 0.50
RAMP_S = 0.03
TARGET_AREA_M2 = 5e-5
LOCATION_A = 0.25
LOCATION_B = 0.75
A_ON_S = 0.08
A_OFF_S = 0.26
B_SEQUENTIAL_ON_S = 0.26
B_SEQUENTIAL_OFF_S = 0.44
B_OVERLAP_ON_S = 0.20
B_OVERLAP_OFF_S = 0.38
CONTROL_STEP_S = 0.005
REFERENCE_CONTROL_STEP_S = 0.0025
FRAME_SIZE = 1024
HOP_SIZE = 256
REFERENCE_HOP_SIZE = 128
TRACE_FREQUENCIES_HZ = np.asarray([500.0, 1500.0, 2500.0], dtype=np.float64)


@dataclass(frozen=True, slots=True)
class Condition:
    name: str
    include_a: bool
    include_b: bool
    b_on_s: float
    b_off_s: float


CONDITIONS = (
    Condition("A_only", True, False, B_SEQUENTIAL_ON_S, B_SEQUENTIAL_OFF_S),
    Condition("B_only", False, True, B_SEQUENTIAL_ON_S, B_SEQUENTIAL_OFF_S),
    Condition("sequential", True, True, B_SEQUENTIAL_ON_S, B_SEQUENTIAL_OFF_S),
    Condition("overlap", True, True, B_OVERLAP_ON_S, B_OVERLAP_OFF_S),
)


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP8 = load_experiment_module("morpho_exp008_for_011", EXPERIMENTS / "008_event_trajectory" / "run.py")
EXP9 = load_experiment_module("morpho_exp009_for_011", EXPERIMENTS / "009_fixed_tract_waveform" / "run.py")


def smoothstep01(x: float) -> float:
    u = min(1.0, max(0.0, x))
    return u * u * (3.0 - 2.0 * u)


def analytic_activation(time_s: float, onset_s: float, offset_s: float) -> float:
    if time_s < onset_s or time_s >= offset_s:
        return 0.0
    return smoothstep01((time_s - onset_s) / RAMP_S) * smoothstep01(
        (offset_s - time_s) / RAMP_S
    )


def sampling_grid(step_s: float) -> np.ndarray:
    first = math.floor(-step_s / step_s) - 1
    last = math.ceil((DURATION_S + step_s) / step_s) + 1
    return np.arange(first, last + 1, dtype=np.float64) * step_s


def reconstructed_activation(
    times_s: np.ndarray, *, onset_s: float, offset_s: float, step_s: float
) -> np.ndarray:
    sample_times = sampling_grid(step_s)
    sample_values = np.asarray(
        [analytic_activation(float(t), onset_s, offset_s) for t in sample_times],
        dtype=np.float64,
    )
    interpolated = np.interp(times_s, sample_times, sample_values)
    active = (times_s >= onset_s) & (times_s < offset_s)
    return np.where(active, interpolated, 0.0)


def activations_for_condition(
    condition: Condition, times_s: np.ndarray, *, step_s: float
) -> tuple[np.ndarray, np.ndarray]:
    if condition.include_a:
        a = reconstructed_activation(
            times_s,
            onset_s=A_ON_S,
            offset_s=A_OFF_S,
            step_s=step_s,
        )
    else:
        a = np.zeros_like(times_s)

    if condition.include_b:
        b = reconstructed_activation(
            times_s,
            onset_s=condition.b_on_s,
            offset_s=condition.b_off_s,
            step_s=step_s,
        )
    else:
        b = np.zeros_like(times_s)
    return a, b


def effective_area(rest_area_m2: float, activation: float) -> float:
    if not 0.0 <= activation <= 1.0:
        raise ValueError(f"activation outside [0,1]: {activation!r}")
    return rest_area_m2 + activation * (TARGET_AREA_M2 - rest_area_m2)


def effective_score(
    rest_geometry: Tract1DGeometry, activation_a: float, activation_b: float
) -> GestureScore:
    gestures: list[Gesture] = []
    for location, activation in (
        (LOCATION_A, activation_a),
        (LOCATION_B, activation_b),
    ):
        section_index = rest_geometry.section_index_at(location)
        rest_area = rest_geometry.sections[section_index].area_m2
        area = effective_area(rest_area, activation)
        gestures.append(
            Gesture(
                task=Task.CONSTRICT,
                onset_s=0.0,
                offset_s=DURATION_S + 1.0,
                target="oral",
                location=location,
                parameters=(TaskParameter("target_area", area, "m2"),),
            )
        )
    return GestureScore(tuple(gestures))


def area_at_location(state: Tract1DGeometry, location: float) -> float:
    return state.sections[state.section_index_at(location)].area_m2


def state_for_activations(
    morphology: object,
    activation_a: float,
    activation_b: float,
    time_s: float,
) -> Tract1DGeometry:
    score = effective_score(morphology.rest_state, activation_a, activation_b)
    result = simulate_snapshot(
        morphology=morphology,
        score=score,
        realizer=Tract1DRealizer(),
        acoustic_backend=SegmentedTubeBackend(),
        acoustic_request=ImpedanceRequest(TRACE_FREQUENCIES_HZ),
        time_s=time_s,
    )
    state = result.realization.state
    if state is None or result.acoustics is None:
        raise RuntimeError(
            f"unexpected non-feasible realization at t={time_s:g}: "
            f"{result.realization.feasibility.status}"
        )
    return state


def synthesize_quasistatic(
    condition: Condition,
    source: np.ndarray,
    *,
    control_step_s: float,
    hop_size: int,
) -> tuple[np.ndarray, list[dict[str, float]]]:
    morphology = EXP8.prepared(EXP8.BODIES[0])
    sample_count = source.size
    window = np.hanning(FRAME_SIZE).astype(np.float64)
    frequencies_hz = np.fft.rfftfreq(FRAME_SIZE, d=1.0 / SAMPLE_RATE_HZ)
    output = np.zeros(sample_count + FRAME_SIZE, dtype=np.float64)
    normalization = np.zeros_like(output)
    trace: list[dict[str, float]] = []

    starts = list(range(0, sample_count, hop_size))
    center_times = np.asarray(
        [(start + FRAME_SIZE / 2.0) / SAMPLE_RATE_HZ for start in starts],
        dtype=np.float64,
    )
    activation_a, activation_b = activations_for_condition(
        condition, center_times, step_s=control_step_s
    )

    rest_area_a = area_at_location(morphology.rest_state, LOCATION_A)
    rest_area_b = area_at_location(morphology.rest_state, LOCATION_B)

    for start, center_s, a, b in zip(
        starts, center_times, activation_a, activation_b, strict=True
    ):
        state = state_for_activations(morphology, float(a), float(b), float(center_s))
        frame = np.zeros(FRAME_SIZE, dtype=np.float64)
        end = min(start + FRAME_SIZE, sample_count)
        frame[: end - start] = source[start:end]
        spectrum = np.fft.rfft(frame * window)
        transfer = EXP9.far_field_pressure_transfer(state, frequencies_hz)
        rendered = np.fft.irfft(spectrum * transfer, n=FRAME_SIZE)
        output[start : start + FRAME_SIZE] += rendered * window
        normalization[start : start + FRAME_SIZE] += window**2

        area_a = area_at_location(state, LOCATION_A)
        area_b = area_at_location(state, LOCATION_B)
        trace_transfer = np.abs(EXP9.far_field_pressure_transfer(state, TRACE_FREQUENCIES_HZ))
        trace.append(
            {
                "time_s": float(center_s),
                "activation_a": float(a),
                "activation_b": float(b),
                "area_a_m2": float(area_a),
                "area_b_m2": float(area_b),
                "both_constricted": float(
                    area_a < rest_area_a - 1e-12 and area_b < rest_area_b - 1e-12
                ),
                "transfer_500_abs": float(trace_transfer[0]),
                "transfer_1500_abs": float(trace_transfer[1]),
                "transfer_2500_abs": float(trace_transfer[2]),
            }
        )

    pressure = output[:sample_count]
    norm = normalization[:sample_count]
    mask = norm > 1e-12
    pressure[mask] /= norm[mask]
    pressure[~mask] = 0.0
    if np.any(~np.isfinite(pressure)):
        raise RuntimeError(f"{condition.name}: non-finite waveform")
    return pressure, trace


def normalized_rms_difference(reference: np.ndarray, candidate: np.ndarray) -> float:
    denominator = float(np.sqrt(np.mean(reference * reference)))
    if denominator <= 0.0 or not math.isfinite(denominator):
        return math.inf
    return float(np.sqrt(np.mean((reference - candidate) ** 2)) / denominator)


def write_trace(path: Path, rows: list[dict[str, float]]) -> None:
    if not rows:
        raise ValueError("cannot write empty trace")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def activation_metrics(
    condition: Condition, *, step_s: float
) -> dict[str, float]:
    times = np.linspace(0.0, DURATION_S, 50_001, dtype=np.float64)
    reconstructed_a, reconstructed_b = activations_for_condition(
        condition, times, step_s=step_s
    )
    analytic_a = np.asarray(
        [
            analytic_activation(float(t), A_ON_S, A_OFF_S)
            if condition.include_a
            else 0.0
            for t in times
        ],
        dtype=np.float64,
    )
    analytic_b = np.asarray(
        [
            analytic_activation(float(t), condition.b_on_s, condition.b_off_s)
            if condition.include_b
            else 0.0
            for t in times
        ],
        dtype=np.float64,
    )

    overlap_integral = float(np.trapezoid(reconstructed_a * reconstructed_b, times))
    energy_a = float(np.trapezoid(reconstructed_a * reconstructed_a, times))
    energy_b = float(np.trapezoid(reconstructed_b * reconstructed_b, times))
    denominator = math.sqrt(energy_a * energy_b)
    overlap_coefficient = overlap_integral / denominator if denominator > 0.0 else 0.0

    return {
        "activation_a_integral_s": float(np.trapezoid(reconstructed_a, times)),
        "activation_b_integral_s": float(np.trapezoid(reconstructed_b, times)),
        "activation_a_squared_integral_s": energy_a,
        "activation_b_squared_integral_s": energy_b,
        "overlap_integral_s": overlap_integral,
        "normalized_overlap": overlap_coefficient,
        "activation_a_max_abs_error": float(
            np.max(np.abs(analytic_a - reconstructed_a))
        ),
        "activation_b_max_abs_error": float(
            np.max(np.abs(analytic_b - reconstructed_b))
        ),
    }


def physical_simultaneous_duration(trace: list[dict[str, float]], hop_size: int) -> float:
    count = sum(row["both_constricted"] > 0.5 for row in trace)
    return float(count * hop_size / SAMPLE_RATE_HZ)


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    _, source = EXP9.source_volume_velocity()
    if source.size != int(round(SAMPLE_RATE_HZ * DURATION_S)):
        raise RuntimeError("Experiment-009 source constants no longer match Experiment 011")

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    bound_5ms = float(
        oracle["linear_interpolation_activation_max_abs_error_bounds"]["5ms"]
    )

    candidate_waveforms: dict[str, np.ndarray] = {}
    discretization: dict[str, float] = {}
    summary: list[dict[str, object]] = []
    condition_metrics: dict[str, dict[str, float]] = {}
    physical_durations: dict[str, float] = {}

    for condition in CONDITIONS:
        pressure, trace = synthesize_quasistatic(
            condition,
            source,
            control_step_s=CONTROL_STEP_S,
            hop_size=HOP_SIZE,
        )
        candidate_waveforms[condition.name] = pressure
        metrics = activation_metrics(condition, step_s=CONTROL_STEP_S)
        condition_metrics[condition.name] = metrics
        physical_duration = physical_simultaneous_duration(trace, HOP_SIZE)
        physical_durations[condition.name] = physical_duration

        sensitivity = math.nan
        if condition.name in {"sequential", "overlap"}:
            reference, _ = synthesize_quasistatic(
                condition,
                source,
                control_step_s=REFERENCE_CONTROL_STEP_S,
                hop_size=REFERENCE_HOP_SIZE,
            )
            sensitivity = normalized_rms_difference(reference, pressure)
            discretization[condition.name] = sensitivity

        gain = EXP9.write_listening_wav(
            output_dir / f"{condition.name}_listen.wav", pressure
        )
        np.save(output_dir / f"{condition.name}_raw_pressure_pa.npy", pressure)
        write_trace(output_dir / f"{condition.name}_trace.csv", trace)

        summary.append(
            {
                "condition": condition.name,
                "raw_peak_pa": float(np.max(np.abs(pressure))),
                "raw_rms_pa": float(np.sqrt(np.mean(pressure * pressure))),
                "listening_gain_fullscale_per_pa": gain,
                "activation_a_integral_s": metrics["activation_a_integral_s"],
                "activation_b_integral_s": metrics["activation_b_integral_s"],
                "overlap_integral_s": metrics["overlap_integral_s"],
                "normalized_overlap": metrics["normalized_overlap"],
                "physical_simultaneous_duration_s": physical_duration,
                "discretization_normalized_rms_difference": sensitivity,
                "finite": bool(np.all(np.isfinite(pressure))),
            }
        )

    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    effect = normalized_rms_difference(
        candidate_waveforms["sequential"], candidate_waveforms["overlap"]
    )
    max_discretization = max(discretization.values())

    sequential_metrics = condition_metrics["sequential"]
    overlap_metrics = condition_metrics["overlap"]
    expected_overlap = float(oracle["overlap_normalized_overlap"])

    activation_errors = [
        metrics[key]
        for metrics in condition_metrics.values()
        for key in ("activation_a_max_abs_error", "activation_b_max_abs_error")
    ]
    activation_bound_ok = all(error <= bound_5ms + 1e-12 for error in activation_errors)
    sequential_overlap_ok = abs(sequential_metrics["normalized_overlap"]) <= 1e-12
    overlap_oracle_ok = (
        abs(overlap_metrics["normalized_overlap"] - expected_overlap) <= 1e-3
    )
    physical_overlap_ok = (
        physical_durations["sequential"] == 0.0
        and physical_durations["overlap"] > 0.0
    )
    all_finite = all(bool(row["finite"]) for row in summary)
    acoustic_effect_ok = effect > 0.01
    discrimination_ok = effect > 5.0 * max_discretization

    supported = all(
        (
            all_finite,
            activation_bound_ok,
            sequential_overlap_ok,
            overlap_oracle_ok,
            physical_overlap_ok,
            acoustic_effect_ok,
            discrimination_ok,
        )
    )
    decision_name = "ADOPT" if supported else "MORE_DATA"

    decision = {
        "decision": decision_name,
        "research_question": "whether relative timing/overlap between two spatially distinct CONSTRICT gestures is an independently observable compiler-relevant variable",
        "model_class": "quasi-stationary time-varying transfer filter; no acoustic state propagation between frames",
        "intervention": "Gesture B relative timing only: sequential 0.26-0.44 s vs overlap 0.20-0.38 s",
        "gesture_a_window_s": [A_ON_S, A_OFF_S],
        "gesture_locations_normalized": {"A": LOCATION_A, "B": LOCATION_B},
        "target_area_m2": TARGET_AREA_M2,
        "activation_metrics": condition_metrics,
        "wolfram_oracle": oracle,
        "activation_bound_ok": activation_bound_ok,
        "sequential_overlap_ok": sequential_overlap_ok,
        "overlap_oracle_ok": overlap_oracle_ok,
        "physical_simultaneous_duration_s": physical_durations,
        "physical_overlap_ok": physical_overlap_ok,
        "sequential_vs_overlap_normalized_rms_difference": effect,
        "discretization_normalized_rms_difference": discretization,
        "max_discretization_normalized_rms_difference": max_discretization,
        "acoustic_effect_gt_0_01": acoustic_effect_ok,
        "effect_gt_5x_discretization": discrimination_ok,
        "all_outputs_finite": all_finite,
        "limitations": [
            "manual prepared 1D geometry",
            "two CONSTRICT tasks only",
            "experiment-local activation reconstruction; no production coordination API",
            "quasi-stationary short-time filtering; no carried acoustic state",
            "no articulator competition or task-dynamic controller",
            "periodic explicit source; no self-oscillating vocal folds",
            "no source-filter back-coupling",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if not all_finite:
        raise RuntimeError("non-finite waveform output")
    if not activation_bound_ok:
        raise RuntimeError("activation reconstruction exceeded Wolfram bound")
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-011-output"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
