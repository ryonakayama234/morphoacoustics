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

from morphoacoustics import simulate_snapshot
from morphoacoustics.acoustics import ImpedanceRequest, SegmentedTubeBackend
from morphoacoustics.physical import Tract1DGeometry
from morphoacoustics.realization import Tract1DRealizer

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "activation_oracle.json"

ONSET_S = 0.08
OFFSET_S = 0.42
CONTROL_STEP_S = 0.005
REFERENCE_CONTROL_STEP_S = 0.0025
FRAME_SIZE = 1024
HOP_SIZE = 256
REFERENCE_HOP_SIZE = 128
TRACE_FREQUENCIES_HZ = np.asarray([500.0, 1500.0, 2500.0], dtype=np.float64)


@dataclass(frozen=True, slots=True)
class MotionCase:
    name: str
    ramp_s: float


MOTIONS = (MotionCase("fast", 0.03), MotionCase("slow", 0.09))


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP8 = load_experiment_module("morpho_exp008", EXPERIMENTS / "008_event_trajectory" / "run.py")
EXP9 = load_experiment_module("morpho_exp009", EXPERIMENTS / "009_fixed_tract_waveform" / "run.py")


def smoothstep01(x: float) -> float:
    u = min(1.0, max(0.0, x))
    return u * u * (3.0 - 2.0 * u)


def analytic_activation(time_s: float, ramp_s: float) -> float:
    if time_s < ONSET_S or time_s >= OFFSET_S:
        return 0.0
    if time_s < ONSET_S + ramp_s:
        return smoothstep01((time_s - ONSET_S) / ramp_s)
    if time_s > OFFSET_S - ramp_s:
        return smoothstep01((OFFSET_S - time_s) / ramp_s)
    return 1.0


def sampling_grid(step_s: float) -> np.ndarray:
    first = math.floor(-step_s / step_s) - 1
    last = math.ceil((EXP9.DURATION_S + step_s) / step_s) + 1
    return np.arange(first, last + 1, dtype=np.float64) * step_s


def reconstructed_activation(
    times_s: np.ndarray, *, ramp_s: float, step_s: float
) -> np.ndarray:
    sample_times = sampling_grid(step_s)
    sample_values = np.asarray(
        [analytic_activation(float(t), ramp_s) for t in sample_times],
        dtype=np.float64,
    )
    interpolated = np.interp(times_s, sample_times, sample_values)
    active = (times_s >= ONSET_S) & (times_s < OFFSET_S)
    return np.where(active, interpolated, 0.0)


def state_for_activation(body: object, activation: float, time_s: float) -> Tract1DGeometry:
    morphology = EXP8.prepared(body)
    score = EXP8.effective_score_for_activation(
        EXP8.base_score(), morphology.rest_state, activation
    )
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
            f"unexpected non-feasible realization for {body.name} at t={time_s:g}: "
            f"{result.realization.feasibility.status}"
        )
    return state


def synthesize_quasistatic(
    body: object,
    motion: MotionCase,
    source: np.ndarray,
    *,
    control_step_s: float,
    hop_size: int,
) -> tuple[np.ndarray, list[dict[str, float]]]:
    sample_count = source.size
    window = np.hanning(FRAME_SIZE).astype(np.float64)
    frequencies_hz = np.fft.rfftfreq(FRAME_SIZE, d=1.0 / EXP9.SAMPLE_RATE_HZ)
    output = np.zeros(sample_count + FRAME_SIZE, dtype=np.float64)
    normalization = np.zeros_like(output)
    trace: list[dict[str, float]] = []

    starts = list(range(0, sample_count, hop_size))
    center_times = np.asarray(
        [(start + FRAME_SIZE / 2.0) / EXP9.SAMPLE_RATE_HZ for start in starts],
        dtype=np.float64,
    )
    activations = reconstructed_activation(
        center_times, ramp_s=motion.ramp_s, step_s=control_step_s
    )

    for start, center_s, activation in zip(
        starts, center_times, activations, strict=True
    ):
        state = state_for_activation(body, float(activation), float(center_s))
        frame = np.zeros(FRAME_SIZE, dtype=np.float64)
        end = min(start + FRAME_SIZE, sample_count)
        frame[: end - start] = source[start:end]
        spectrum = np.fft.rfft(frame * window)
        transfer = EXP9.far_field_pressure_transfer(state, frequencies_hz)
        rendered = np.fft.irfft(spectrum * transfer, n=FRAME_SIZE)
        output[start : start + FRAME_SIZE] += rendered * window
        normalization[start : start + FRAME_SIZE] += window**2
        trace.append(
            {
                "time_s": float(center_s),
                "activation": float(activation),
                "area_m2": float(EXP8.area_at_location(state)),
            }
        )

    pressure = output[:sample_count]
    norm = normalization[:sample_count]
    mask = norm > 1e-12
    pressure[mask] /= norm[mask]
    pressure[~mask] = 0.0
    if np.any(~np.isfinite(pressure)):
        raise RuntimeError(f"{body.name}/{motion.name}: non-finite waveform")
    return pressure, trace


def normalized_rms_difference(reference: np.ndarray, candidate: np.ndarray) -> float:
    denominator = float(np.sqrt(np.mean(reference * reference)))
    if denominator <= 0.0 or not math.isfinite(denominator):
        return math.inf
    return float(np.sqrt(np.mean((reference - candidate) ** 2)) / denominator)


def write_trace(path: Path, rows: list[dict[str, float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time_s", "activation", "area_m2"])
        writer.writeheader()
        writer.writerows(rows)


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    _, source = EXP9.source_volume_velocity()
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))

    summary: list[dict[str, object]] = []
    waveforms: dict[tuple[str, str], np.ndarray] = {}
    discretization: dict[str, float] = {}

    for body in EXP8.BODIES:
        for motion in MOTIONS:
            pressure, trace = synthesize_quasistatic(
                body,
                motion,
                source,
                control_step_s=CONTROL_STEP_S,
                hop_size=HOP_SIZE,
            )
            reference, _ = synthesize_quasistatic(
                body,
                motion,
                source,
                control_step_s=REFERENCE_CONTROL_STEP_S,
                hop_size=REFERENCE_HOP_SIZE,
            )
            key = (body.name, motion.name)
            waveforms[key] = pressure
            sensitivity = normalized_rms_difference(reference, pressure)
            discretization[f"{body.name}/{motion.name}"] = sensitivity
            gain = EXP9.write_listening_wav(
                output_dir / f"{body.name}_{motion.name}_listen.wav", pressure
            )
            np.save(
                output_dir / f"{body.name}_{motion.name}_raw_pressure_pa.npy",
                pressure,
            )
            write_trace(output_dir / f"{body.name}_{motion.name}_trace.csv", trace)
            summary.append(
                {
                    "body": body.name,
                    "motion": motion.name,
                    "ramp_s": motion.ramp_s,
                    "raw_peak_pa": float(np.max(np.abs(pressure))),
                    "raw_rms_pa": float(np.sqrt(np.mean(pressure * pressure))),
                    "listening_gain_fullscale_per_pa": gain,
                    "discretization_normalized_rms_difference": sensitivity,
                    "finite": bool(np.all(np.isfinite(pressure))),
                }
            )

    motion_differences = {
        body.name: normalized_rms_difference(
            waveforms[(body.name, "slow")], waveforms[(body.name, "fast")]
        )
        for body in EXP8.BODIES
    }
    morphology_differences = {
        motion.name: normalized_rms_difference(
            waveforms[("wide-body", motion.name)],
            waveforms[("narrow-body", motion.name)],
        )
        for motion in MOTIONS
    }

    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    bounds = oracle["linear_interpolation_activation_max_abs_error_bounds"]
    observed_activation_error: dict[str, float] = {}
    times = np.linspace(0.0, EXP9.DURATION_S, 5001)
    for motion in MOTIONS:
        analytic = np.asarray(
            [analytic_activation(float(t), motion.ramp_s) for t in times],
            dtype=np.float64,
        )
        reconstructed = reconstructed_activation(
            times, ramp_s=motion.ramp_s, step_s=CONTROL_STEP_S
        )
        error = float(np.max(np.abs(analytic - reconstructed)))
        observed_activation_error[motion.name] = error
        bound = float(bounds[motion.name]["5ms"])
        if error > bound + 1e-12:
            raise RuntimeError(
                f"{motion.name}: activation error {error:g} exceeds Wolfram bound {bound:g}"
            )

    all_finite = all(bool(row["finite"]) for row in summary)
    motion_effect = all(value > 0.01 for value in motion_differences.values())
    morphology_effect = all(value > 0.01 for value in morphology_differences.values())
    stable = all(value < 0.20 for value in discretization.values())
    decision_name = (
        "SUPPORTED" if all_finite and motion_effect and morphology_effect and stable else "MORE_DATA"
    )

    decision = {
        "decision": decision_name,
        "model_class": "quasi-stationary time-varying transfer filter; no acoustic state propagation between frames",
        "temporal_representation": "explicit onset/offset events + sampled continuous trajectory",
        "event_window_s": {"onset": ONSET_S, "offset": OFFSET_S},
        "intervention": "gesture ramp duration only: fast=30 ms, slow=90 ms",
        "observed_activation_max_abs_error": observed_activation_error,
        "wolfram_activation_error_bounds": bounds,
        "motion_normalized_rms_difference": motion_differences,
        "morphology_normalized_rms_difference": morphology_differences,
        "discretization_normalized_rms_difference": discretization,
        "all_outputs_finite": all_finite,
        "motion_effect_present": motion_effect,
        "morphology_effect_present": morphology_effect,
        "discretization_stable": stable,
        "limitations": [
            "manual prepared 1D geometries",
            "quasi-stationary short-time filtering; no carried acoustic state",
            "Experiment-009 attenuation/load/radiation surrogates",
            "periodic explicit source; no self-oscillating vocal folds",
            "no source-filter back-coupling",
            "one CONSTRICT gesture and one motion-axis intervention only",
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
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("experiment-010-output"))
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
