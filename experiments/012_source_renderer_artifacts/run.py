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
from typing import Callable, Literal

import numpy as np

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "source_oracle.json"

SAMPLE_RATE_HZ = 48_000
DURATION_S = 0.50
F0_HZ = 100.0
SOURCE_PEAK_VOLUME_VELOCITY_M3_S = 1.0e-5
SOURCE_RAMP_S = 0.01
FRAME_SIZE = 1024
DEFAULT_HOP_SIZE = 256
REFERENCE_HOP_SIZE = 128
HOP_TESTS = (256, 128, 64)
CONTROL_STEP_S = 0.005
REFERENCE_CONTROL_STEP_S = 0.0025
HIGH_FREQUENCY_THRESHOLD_HZ = 2_000.0
STEADY_START_S = 0.05
STEADY_END_S = 0.45
STARTUP_END_S = 0.02
STARTUP_REFERENCE_START_S = 0.05
STARTUP_REFERENCE_END_S = 0.20
PITCH_PERIOD_SAMPLES = int(round(SAMPLE_RATE_HZ / F0_HZ))

EdgeMode = Literal["legacy_edge", "preroll_edge"]


@dataclass(frozen=True, slots=True)
class SourceCase:
    name: str
    kind: Literal["harmonic", "smooth_flow"]
    harmonics: int = 0
    exponent: float = 0.0
    open_quotient: float = 0.0


SOURCE_CASES = (
    SourceCase("current40_p1.2", "harmonic", harmonics=40, exponent=1.2),
    SourceCase("harmonic10_p1.2", "harmonic", harmonics=10, exponent=1.2),
    SourceCase("harmonic40_p2.0", "harmonic", harmonics=40, exponent=2.0),
    SourceCase("smooth_flow_oq0.6", "smooth_flow", open_quotient=0.6),
)


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP9 = load_experiment_module(
    "morpho_exp009_for_012", EXPERIMENTS / "009_fixed_tract_waveform" / "run.py"
)
EXP11 = load_experiment_module(
    "morpho_exp011_for_012",
    EXPERIMENTS / "011_gesture_coordination_overlap" / "run.py",
)


def normalize_peak(values: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(values)))
    if not math.isfinite(peak) or peak <= 0.0:
        raise RuntimeError("source core has invalid peak")
    return np.asarray(
        values * (SOURCE_PEAK_VOLUME_VELOCITY_M3_S / peak), dtype=np.float64
    )


def source_core(case: SourceCase) -> np.ndarray:
    sample_count = int(round(SAMPLE_RATE_HZ * DURATION_S))
    time_s = np.arange(sample_count, dtype=np.float64) / SAMPLE_RATE_HZ

    if case.kind == "harmonic":
        values = np.zeros(sample_count, dtype=np.float64)
        for harmonic in range(1, case.harmonics + 1):
            frequency_hz = harmonic * F0_HZ
            if frequency_hz >= SAMPLE_RATE_HZ / 2.0:
                break
            values += harmonic ** (-case.exponent) * np.sin(
                2.0 * np.pi * frequency_hz * time_s
            )
        return normalize_peak(values)

    if case.kind == "smooth_flow":
        phase = np.mod(F0_HZ * time_s, 1.0)
        values = np.zeros(sample_count, dtype=np.float64)
        active = phase < case.open_quotient
        values[active] = np.sin(
            np.pi * phase[active] / case.open_quotient
        ) ** 2
        return normalize_peak(values)

    raise AssertionError(case.kind)


def apply_common_envelope(core: np.ndarray) -> np.ndarray:
    values = np.asarray(core, dtype=np.float64).copy()
    ramp_samples = int(round(SOURCE_RAMP_S * SAMPLE_RATE_HZ))
    if ramp_samples > 0:
        phase = np.linspace(0.0, np.pi / 2.0, ramp_samples, endpoint=False)
        ramp = np.sin(phase) ** 2
        values[:ramp_samples] *= ramp
        values[-ramp_samples:] *= ramp[::-1]
    return values


def source_waveform(case: SourceCase) -> np.ndarray:
    return apply_common_envelope(source_core(case))


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(values, dtype=np.float64) ** 2)))


def one_sided_high_frequency_ratio(values: np.ndarray) -> float:
    spectrum = np.fft.rfft(values)
    power = np.abs(spectrum) ** 2
    frequencies_hz = np.fft.rfftfreq(values.size, d=1.0 / SAMPLE_RATE_HZ)
    total = float(np.sum(power))
    if total <= 0.0:
        return math.nan
    return float(np.sum(power[frequencies_hz >= HIGH_FREQUENCY_THRESHOLD_HZ]) / total)


def basic_signal_metrics(values: np.ndarray) -> dict[str, float]:
    signal_rms = rms(values)
    if signal_rms <= 0.0 or not math.isfinite(signal_rms):
        raise RuntimeError("cannot measure silent/non-finite signal")
    derivative = np.diff(values) * SAMPLE_RATE_HZ
    return {
        "rms": signal_rms,
        "crest_factor": float(np.max(np.abs(values)) / signal_rms),
        "max_abs_derivative_per_rms": float(
            np.max(np.abs(derivative)) / signal_rms
        ),
        "energy_ratio_ge_2khz": one_sided_high_frequency_ratio(values),
    }


def phase_peak_ratio(
    values: np.ndarray,
    period_samples: int,
    *,
    start_s: float = STEADY_START_S,
    end_s: float = STEADY_END_S,
) -> float:
    if period_samples <= 0:
        raise ValueError("period_samples must be positive")
    derivative = np.abs(np.diff(np.asarray(values, dtype=np.float64)))
    start = int(round(start_s * SAMPLE_RATE_HZ))
    end = min(int(round(end_s * SAMPLE_RATE_HZ)), derivative.size)
    indices = np.arange(start, end, dtype=np.int64)
    selected = derivative[start:end]
    phases = np.mod(indices, period_samples)
    sums = np.bincount(phases, weights=selected, minlength=period_samples)
    counts = np.bincount(phases, minlength=period_samples)
    valid = counts > 0
    profile = np.zeros(period_samples, dtype=np.float64)
    profile[valid] = sums[valid] / counts[valid]
    mean_value = float(np.mean(selected))
    if mean_value <= 0.0:
        return math.nan
    return float(np.max(profile) / mean_value)


def startup_peak_over_steady_rms(values: np.ndarray) -> float:
    startup_end = int(round(STARTUP_END_S * SAMPLE_RATE_HZ))
    reference_start = int(round(STARTUP_REFERENCE_START_S * SAMPLE_RATE_HZ))
    reference_end = int(round(STARTUP_REFERENCE_END_S * SAMPLE_RATE_HZ))
    reference_rms = rms(values[reference_start:reference_end])
    if reference_rms <= 0.0:
        return math.inf
    return float(np.max(np.abs(values[:startup_end])) / reference_rms)


def normalized_rms_difference(reference: np.ndarray, candidate: np.ndarray) -> float:
    denominator = rms(reference)
    if denominator <= 0.0 or not math.isfinite(denominator):
        return math.inf
    return float(rms(reference - candidate) / denominator)


def frame_render(
    source: np.ndarray,
    transfer_for_time: Callable[[float, np.ndarray], np.ndarray],
    *,
    hop_size: int,
    edge_mode: EdgeMode,
) -> np.ndarray:
    if edge_mode == "legacy_edge":
        pad = 0
        work_source = source
    elif edge_mode == "preroll_edge":
        pad = FRAME_SIZE
        work_source = np.pad(source, (pad, pad), mode="constant")
    else:
        raise AssertionError(edge_mode)

    window = np.hanning(FRAME_SIZE).astype(np.float64)
    frequencies_hz = np.fft.rfftfreq(FRAME_SIZE, d=1.0 / SAMPLE_RATE_HZ)
    output = np.zeros(work_source.size + FRAME_SIZE, dtype=np.float64)
    normalization = np.zeros_like(output)

    for start in range(0, work_source.size, hop_size):
        frame = np.zeros(FRAME_SIZE, dtype=np.float64)
        end = min(start + FRAME_SIZE, work_source.size)
        frame[: end - start] = work_source[start:end]
        center_s = (start + FRAME_SIZE / 2.0 - pad) / SAMPLE_RATE_HZ
        transfer = transfer_for_time(float(center_s), frequencies_hz)
        spectrum = np.fft.rfft(frame * window)
        rendered = np.fft.irfft(spectrum * transfer, n=FRAME_SIZE)
        output[start : start + FRAME_SIZE] += rendered * window
        normalization[start : start + FRAME_SIZE] += window**2

    rendered_work = output[: work_source.size]
    norm = normalization[: work_source.size]
    mask = norm > 1e-12
    rendered_work[mask] /= norm[mask]
    rendered_work[~mask] = 0.0

    if edge_mode == "preroll_edge":
        rendered_work = rendered_work[pad : pad + source.size]

    rendered_work = np.asarray(rendered_work, dtype=np.float64)
    if np.any(~np.isfinite(rendered_work)):
        raise RuntimeError("renderer produced non-finite samples")
    return rendered_work


def render_fixed_tract(
    source: np.ndarray, *, hop_size: int, edge_mode: EdgeMode
) -> np.ndarray:
    geometry = EXP9.uniform_geometry()

    def transfer_for_time(_: float, frequencies_hz: np.ndarray) -> np.ndarray:
        return EXP9.far_field_pressure_transfer(geometry, frequencies_hz)

    return frame_render(
        source,
        transfer_for_time,
        hop_size=hop_size,
        edge_mode=edge_mode,
    )


def render_coordination(
    condition: object,
    source: np.ndarray,
    *,
    control_step_s: float,
    hop_size: int,
    edge_mode: EdgeMode,
) -> np.ndarray:
    morphology = EXP11.EXP8.prepared(EXP11.EXP8.BODIES[0])

    def transfer_for_time(center_s: float, frequencies_hz: np.ndarray) -> np.ndarray:
        times = np.asarray([center_s], dtype=np.float64)
        activation_a, activation_b = EXP11.activations_for_condition(
            condition, times, step_s=control_step_s
        )
        safe_time_s = max(0.0, center_s)
        state = EXP11.state_for_activations(
            morphology,
            float(activation_a[0]),
            float(activation_b[0]),
            safe_time_s,
        )
        return EXP9.far_field_pressure_transfer(state, frequencies_hz)

    return frame_render(
        source,
        transfer_for_time,
        hop_size=hop_size,
        edge_mode=edge_mode,
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_oracle() -> dict[str, object]:
    return json.loads(ORACLE_PATH.read_text(encoding="utf-8"))


def oracle_map(oracle: dict[str, object]) -> dict[str, dict[str, float]]:
    entries = oracle.get("sources")
    if not isinstance(entries, list):
        raise TypeError("oracle sources must be a list")
    result: dict[str, dict[str, float]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            raise TypeError("invalid oracle source entry")
        result[str(entry["name"])] = {
            "crest_factor": float(entry["crest_factor"]),
            "max_abs_derivative_per_rms": float(
                entry["max_abs_derivative_per_rms"]
            ),
            "energy_ratio_ge_2khz": float(entry["energy_ratio_ge_2khz"]),
        }
    return result


def verify_oracle(
    core_metrics: dict[str, dict[str, float]], oracle: dict[str, object]
) -> dict[str, float]:
    expected = oracle_map(oracle)
    max_relative_errors = {
        "crest_factor": 0.0,
        "max_abs_derivative_per_rms": 0.0,
        "energy_ratio_ge_2khz": 0.0,
    }
    for name, metrics in core_metrics.items():
        ref = expected[name]
        for key in max_relative_errors:
            denominator = max(abs(ref[key]), 1e-20)
            relative = abs(metrics[key] - ref[key]) / denominator
            max_relative_errors[key] = max(max_relative_errors[key], relative)
    if max_relative_errors["crest_factor"] > 1e-6:
        raise RuntimeError("Python crest-factor values disagree with Wolfram oracle")
    if max_relative_errors["max_abs_derivative_per_rms"] > 1e-6:
        raise RuntimeError("Python derivative values disagree with Wolfram oracle")
    # Very small spectral tails are implementation-sensitive; ordering is the invariant.
    current_hf = core_metrics["current40_p1.2"]["energy_ratio_ge_2khz"]
    smooth_hf = core_metrics["smooth_flow_oq0.6"]["energy_ratio_ge_2khz"]
    if not smooth_hf < current_hf:
        raise RuntimeError("Python high-frequency ordering disagrees with Wolfram oracle")
    return max_relative_errors


def find_condition(name: str) -> object:
    for condition in EXP11.CONDITIONS:
        if condition.name == name:
            return condition
    raise KeyError(name)


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    oracle = load_oracle()

    cores: dict[str, np.ndarray] = {}
    sources: dict[str, np.ndarray] = {}
    core_metrics: dict[str, dict[str, float]] = {}
    source_metric_rows: list[dict[str, object]] = []

    for case in SOURCE_CASES:
        core = source_core(case)
        source = apply_common_envelope(core)
        cores[case.name] = core
        sources[case.name] = source
        core_measure = basic_signal_metrics(core)
        actual_measure = basic_signal_metrics(source)
        core_metrics[case.name] = core_measure
        source_metric_rows.append(
            {
                "source": case.name,
                "core_crest_factor": core_measure["crest_factor"],
                "core_max_abs_derivative_per_rms": core_measure[
                    "max_abs_derivative_per_rms"
                ],
                "core_energy_ratio_ge_2khz": core_measure["energy_ratio_ge_2khz"],
                "rendered_source_crest_factor": actual_measure["crest_factor"],
                "rendered_source_max_abs_derivative_per_rms": actual_measure[
                    "max_abs_derivative_per_rms"
                ],
                "rendered_source_energy_ratio_ge_2khz": actual_measure[
                    "energy_ratio_ge_2khz"
                ],
            }
        )

    oracle_relative_errors = verify_oracle(core_metrics, oracle)
    write_csv(output_dir / "source_metrics.csv", source_metric_rows)

    fixed_waveforms: dict[str, np.ndarray] = {}
    fixed_metrics: dict[str, dict[str, float]] = {}
    fixed_rows: list[dict[str, object]] = []
    for case in SOURCE_CASES:
        pressure = render_fixed_tract(
            sources[case.name], hop_size=DEFAULT_HOP_SIZE, edge_mode="preroll_edge"
        )
        fixed_waveforms[case.name] = pressure
        metrics = basic_signal_metrics(pressure)
        pitch_ratio = phase_peak_ratio(pressure, PITCH_PERIOD_SAMPLES)
        fixed_metrics[case.name] = {
            **metrics,
            "pitch_phase_peak_ratio": pitch_ratio,
        }
        gain = EXP9.write_listening_wav(
            output_dir / f"fixed_{case.name}_listen.wav", pressure
        )
        np.save(output_dir / f"fixed_{case.name}_raw_pressure_pa.npy", pressure)
        fixed_rows.append(
            {
                "source": case.name,
                "raw_peak_pa": float(np.max(np.abs(pressure))),
                "raw_rms_pa": rms(pressure),
                "crest_factor": metrics["crest_factor"],
                "max_abs_derivative_per_rms": metrics[
                    "max_abs_derivative_per_rms"
                ],
                "energy_ratio_ge_2khz": metrics["energy_ratio_ge_2khz"],
                "pitch_phase_peak_ratio": pitch_ratio,
                "listening_gain_fullscale_per_pa": gain,
                "finite": bool(np.all(np.isfinite(pressure))),
            }
        )
    write_csv(output_dir / "fixed_tract_metrics.csv", fixed_rows)

    current_source = sources["current40_p1.2"]
    hop_rows: list[dict[str, object]] = []
    hop_source_locked = True
    for hop in HOP_TESTS:
        pressure = render_fixed_tract(
            current_source, hop_size=hop, edge_mode="preroll_edge"
        )
        pitch_ratio = phase_peak_ratio(pressure, PITCH_PERIOD_SAMPLES)
        hop_ratio = phase_peak_ratio(pressure, hop)
        pitch_dominant = bool(pitch_ratio > hop_ratio)
        hop_source_locked = hop_source_locked and pitch_dominant
        hop_rows.append(
            {
                "hop_size_samples": hop,
                "hop_seconds": hop / SAMPLE_RATE_HZ,
                "pitch_phase_peak_ratio": pitch_ratio,
                "hop_phase_peak_ratio": hop_ratio,
                "pitch_ratio_gt_hop_ratio": pitch_dominant,
            }
        )
    write_csv(output_dir / "hop_metrics.csv", hop_rows)

    edge_waveforms: dict[str, np.ndarray] = {}
    edge_rows: list[dict[str, object]] = []
    for edge_mode in ("legacy_edge", "preroll_edge"):
        pressure = render_fixed_tract(
            current_source,
            hop_size=DEFAULT_HOP_SIZE,
            edge_mode=edge_mode,
        )
        edge_waveforms[edge_mode] = pressure
        startup_statistic = startup_peak_over_steady_rms(pressure)
        gain = EXP9.write_listening_wav(
            output_dir / f"{edge_mode}_current_listen.wav", pressure
        )
        edge_rows.append(
            {
                "edge_mode": edge_mode,
                "startup_peak_over_steady_rms": startup_statistic,
                "raw_peak_pa": float(np.max(np.abs(pressure))),
                "raw_rms_pa": rms(pressure),
                "listening_gain_fullscale_per_pa": gain,
                "finite": bool(np.all(np.isfinite(pressure))),
            }
        )
    write_csv(output_dir / "edge_metrics.csv", edge_rows)

    baseline_source_metrics = basic_signal_metrics(current_source)
    baseline_fixed_metric = fixed_metrics["current40_p1.2"]["pitch_phase_peak_ratio"]
    qualifying_sources: list[str] = []
    for case in SOURCE_CASES:
        if case.name == "current40_p1.2":
            continue
        actual_source_metrics = basic_signal_metrics(sources[case.name])
        derivative_reduction = (
            actual_source_metrics["max_abs_derivative_per_rms"]
            <= 0.5 * baseline_source_metrics["max_abs_derivative_per_rms"]
        )
        fixed_reduction = (
            fixed_metrics[case.name]["pitch_phase_peak_ratio"]
            <= 0.5 * baseline_fixed_metric
        )
        if derivative_reduction and fixed_reduction:
            qualifying_sources.append(case.name)

    selected_source_name: str | None = None
    if qualifying_sources:
        selected_source_name = min(
            qualifying_sources,
            key=lambda name: (
                fixed_metrics[name]["pitch_phase_peak_ratio"],
                fixed_metrics[name]["energy_ratio_ge_2khz"],
            ),
        )

    source_h1 = bool(qualifying_sources and hop_source_locked)
    legacy_startup = startup_peak_over_steady_rms(edge_waveforms["legacy_edge"])
    preroll_startup = startup_peak_over_steady_rms(edge_waveforms["preroll_edge"])
    edge_h2 = bool(
        math.isfinite(preroll_startup)
        and preroll_startup <= 0.5 * legacy_startup
        and np.all(np.isfinite(edge_waveforms["preroll_edge"]))
    )

    if source_h1 and edge_h2:
        attribution = "MIXED"
    elif source_h1:
        attribution = "SOURCE_CONFIRMED"
    elif edge_h2:
        attribution = "RENDERER_CONFIRMED"
    else:
        attribution = "MORE_DATA"

    cleaned_rows: list[dict[str, object]] = []
    coordination_effect = math.nan
    coordination_discretization: dict[str, float] = {}
    coordination_h3 = False
    if selected_source_name is not None:
        selected_source = sources[selected_source_name]
        cleaned_waveforms: dict[str, np.ndarray] = {}
        for condition_name in ("sequential", "overlap"):
            condition = find_condition(condition_name)
            candidate = render_coordination(
                condition,
                selected_source,
                control_step_s=CONTROL_STEP_S,
                hop_size=DEFAULT_HOP_SIZE,
                edge_mode="preroll_edge",
            )
            reference = render_coordination(
                condition,
                selected_source,
                control_step_s=REFERENCE_CONTROL_STEP_S,
                hop_size=REFERENCE_HOP_SIZE,
                edge_mode="preroll_edge",
            )
            cleaned_waveforms[condition_name] = candidate
            sensitivity = normalized_rms_difference(reference, candidate)
            coordination_discretization[condition_name] = sensitivity
            gain = EXP9.write_listening_wav(
                output_dir / f"cleaned_{condition_name}_listen.wav", candidate
            )
            np.save(
                output_dir / f"cleaned_{condition_name}_raw_pressure_pa.npy",
                candidate,
            )
            cleaned_rows.append(
                {
                    "condition": condition_name,
                    "source": selected_source_name,
                    "raw_peak_pa": float(np.max(np.abs(candidate))),
                    "raw_rms_pa": rms(candidate),
                    "startup_peak_over_steady_rms": startup_peak_over_steady_rms(
                        candidate
                    ),
                    "pitch_phase_peak_ratio": phase_peak_ratio(
                        candidate, PITCH_PERIOD_SAMPLES
                    ),
                    "discretization_normalized_rms_difference": sensitivity,
                    "listening_gain_fullscale_per_pa": gain,
                    "finite": bool(np.all(np.isfinite(candidate))),
                }
            )

        coordination_effect = normalized_rms_difference(
            cleaned_waveforms["sequential"], cleaned_waveforms["overlap"]
        )
        max_discretization = max(coordination_discretization.values())
        coordination_h3 = bool(
            coordination_effect > 0.01
            and coordination_effect > 5.0 * max_discretization
            and all(np.all(np.isfinite(x)) for x in cleaned_waveforms.values())
        )
        write_csv(output_dir / "cleaned_coordination_summary.csv", cleaned_rows)

    decision = {
        "decision": attribution,
        "h1_source_attribution_pass": source_h1,
        "h2_renderer_edge_pass": edge_h2,
        "h3_coordination_retention_pass": coordination_h3,
        "selected_source": selected_source_name,
        "qualifying_sources": qualifying_sources,
        "baseline_source_max_abs_derivative_per_rms": baseline_source_metrics[
            "max_abs_derivative_per_rms"
        ],
        "baseline_fixed_pitch_phase_peak_ratio": baseline_fixed_metric,
        "hop_pitch_dominant_for_all_hops": hop_source_locked,
        "startup_peak_over_steady_rms": {
            "legacy_edge": legacy_startup,
            "preroll_edge": preroll_startup,
            "ratio_preroll_over_legacy": preroll_startup / legacy_startup
            if legacy_startup > 0.0
            else math.inf,
        },
        "cleaned_coordination": {
            "sequential_vs_overlap_normalized_rms_difference": coordination_effect,
            "discretization_normalized_rms_difference": coordination_discretization,
        },
        "wolfram_python_max_relative_errors": oracle_relative_errors,
        "limitations": [
            "fixed prepared 1D tract and Experiment-009 acoustic surrogates",
            "source candidates are explicit comparison signals, not physiological vocal-fold models",
            "quasi-stationary short-time filtering; no carried acoustic state",
            "preroll test changes only renderer boundary context, not production API",
            "objective artifact metrics do not establish perceptual naturalness",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path, default=Path("experiment-012-output")
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
