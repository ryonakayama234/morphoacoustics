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

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "lf_oracle.json"


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP12 = load_experiment_module(
    "morpho_exp012_for_013",
    EXPERIMENTS / "012_source_renderer_artifacts" / "run.py",
)

SAMPLE_RATE_HZ = EXP12.SAMPLE_RATE_HZ
DURATION_S = EXP12.DURATION_S
BASE_F0_HZ = 100.0
SOURCE_PEAK_M3_S = EXP12.SOURCE_PEAK_VOLUME_VELOCITY_M3_S
PITCH_PERIOD_SAMPLES = int(round(SAMPLE_RATE_HZ / BASE_F0_HZ))
RD = 1.0
RNG_SEED = 13013
LF_GRID_SIZE = 8193
BLOCK_S = 0.020
BLOCK_STEP_S = 0.010
STEADY_START_S = 0.05
STEADY_END_S = 0.45

F0_ANCHORS = (
    (0.00, -0.2),
    (0.05, 0.0),
    (0.14, +0.8),
    (0.22, -0.6),
    (0.25, -0.8),
    (0.285, +0.9),
    (0.38, +0.2),
    (0.47, -0.7),
    (0.50, -0.8),
)
GAIN_ANCHORS = (
    (0.00, 0.0),
    (0.02, 1.0),
    (0.20, 1.0),
    (0.245, 0.58),
    (0.28, 1.0),
    (0.47, 1.0),
    (0.50, 0.0),
)


@dataclass(frozen=True, slots=True)
class LFParameters:
    rd: float
    ra: float
    rk: float
    rg: float
    tp: float
    te: float
    ta: float
    alpha: float
    balance: float


@dataclass(frozen=True, slots=True)
class SourceResult:
    name: str
    source: np.ndarray
    deterministic: np.ndarray
    noise: np.ndarray
    cycles: np.ndarray
    planned_f0_hz: np.ndarray
    planned_gain: np.ndarray
    opening: np.ndarray


def smooth_anchor_values(
    times_s: np.ndarray, anchors: tuple[tuple[float, float], ...]
) -> np.ndarray:
    times = np.asarray(times_s, dtype=np.float64)
    result = np.empty_like(times)
    result[times <= anchors[0][0]] = anchors[0][1]
    result[times >= anchors[-1][0]] = anchors[-1][1]
    for (x0, y0), (x1, y1) in zip(anchors[:-1], anchors[1:], strict=True):
        mask = (times > x0) & (times < x1)
        if not np.any(mask):
            continue
        u = (times[mask] - x0) / (x1 - x0)
        s = u * u * (3.0 - 2.0 * u)
        result[mask] = y0 + (y1 - y0) * s
        result[times == x0] = y0
        result[times == x1] = y1
    return result


def common_file_envelope(sample_count: int) -> np.ndarray:
    envelope = np.ones(sample_count, dtype=np.float64)
    ramp_samples = int(round(EXP12.SOURCE_RAMP_S * SAMPLE_RATE_HZ))
    if ramp_samples > 0:
        phase = np.linspace(0.0, np.pi / 2.0, ramp_samples, endpoint=False)
        ramp = np.sin(phase) ** 2
        envelope[:ramp_samples] *= ramp
        envelope[-ramp_samples:] *= ramp[::-1]
    return envelope


def normalize_peak(values: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(values)))
    if not math.isfinite(peak) or peak <= 0.0:
        raise RuntimeError("cannot normalize invalid source")
    return np.asarray(values * (SOURCE_PEAK_M3_S / peak), dtype=np.float64)


def rd_mapping(rd: float) -> tuple[float, float, float, float, float, float]:
    if not math.isfinite(rd) or rd <= 0.0:
        raise ValueError("Rd must be finite and positive")
    ra = (-1.0 + 4.8 * rd) / 100.0
    rk = (22.4 + 11.8 * rd) / 100.0
    denominator = 0.11 * rd - ra * (0.5 + 1.2 * rk)
    rg = 0.25 * rk * (0.5 + 1.2 * rk) / denominator
    tp = 1.0 / (2.0 * rg)
    te = tp * (1.0 + rk)
    ta = ra
    if not (0.0 < tp < te < 1.0 and 0.0 < ta < 1.0):
        raise RuntimeError("Rd mapping produced invalid LF timing ratios")
    return ra, rk, rg, tp, te, ta


def lf_balance(alpha: float, *, tp: float, te: float, ta: float) -> float:
    omega = math.pi / tp
    exp_te = math.exp(alpha * te)
    open_integral = (
        exp_te
        * (alpha * math.sin(omega * te) - omega * math.cos(omega * te))
        + omega
    ) / (alpha * alpha + omega * omega)
    f_te = exp_te * math.sin(omega * te)
    delta = (1.0 - te) / ta
    return open_integral + f_te * ta * (1.0 - delta / math.expm1(delta))


def solve_lf_alpha(*, tp: float, te: float, ta: float) -> float:
    lo = -20.0
    hi = 20.0
    f_lo = lf_balance(lo, tp=tp, te=te, ta=ta)
    f_hi = lf_balance(hi, tp=tp, te=te, ta=ta)
    if f_lo == 0.0:
        return lo
    if f_hi == 0.0:
        return hi
    if f_lo * f_hi > 0.0:
        raise RuntimeError("failed to bracket LF alpha root")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        f_mid = lf_balance(mid, tp=tp, te=te, ta=ta)
        if abs(f_mid) < 1e-15:
            return mid
        if f_lo * f_mid <= 0.0:
            hi = mid
        else:
            lo = mid
            f_lo = f_mid
    return 0.5 * (lo + hi)


def lf_parameters(rd: float = RD) -> LFParameters:
    ra, rk, rg, tp, te, ta = rd_mapping(rd)
    alpha = solve_lf_alpha(tp=tp, te=te, ta=ta)
    balance = lf_balance(alpha, tp=tp, te=te, ta=ta)
    return LFParameters(rd, ra, rk, rg, tp, te, ta, alpha, balance)


def lf_flow_shape(params: LFParameters) -> tuple[np.ndarray, np.ndarray]:
    phase = np.linspace(0.0, 1.0, LF_GRID_SIZE, dtype=np.float64)
    derivative = np.empty_like(phase)
    omega = math.pi / params.tp
    open_mask = phase < params.te
    derivative[open_mask] = np.exp(params.alpha * phase[open_mask]) * np.sin(
        omega * phase[open_mask]
    )
    f_te = math.exp(params.alpha * params.te) * math.sin(omega * params.te)
    delta = (1.0 - params.te) / params.ta
    q = phase[~open_mask]
    derivative[~open_mask] = f_te * (
        np.exp(-(q - params.te) / params.ta) - math.exp(-delta)
    ) / (1.0 - math.exp(-delta))

    flow = np.zeros_like(phase)
    flow[1:] = np.cumsum(
        0.5 * (derivative[:-1] + derivative[1:]) * np.diff(phase)
    )
    # Remove only numerical quadrature drift. The LF integral constraint makes
    # the physical cycle integral zero independently.
    flow -= phase * flow[-1]
    flow = np.maximum(flow, 0.0)
    peak = float(np.max(flow))
    if peak <= 0.0 or not math.isfinite(peak):
        raise RuntimeError("LF flow integration failed")
    flow /= peak
    flow[0] = 0.0
    flow[-1] = 0.0
    return phase, flow


def cycles_from_f0(f0_hz: np.ndarray) -> np.ndarray:
    f0 = np.asarray(f0_hz, dtype=np.float64)
    if np.any(~np.isfinite(f0)) or np.any(f0 <= 0.0):
        raise ValueError("F0 trajectory must be finite and positive")
    cycles = np.zeros_like(f0)
    if f0.size > 1:
        cycles[1:] = np.cumsum(f0[:-1] / SAMPLE_RATE_HZ)
    return cycles


def macro_controls(times_s: np.ndarray, *, micro: bool) -> tuple[np.ndarray, np.ndarray]:
    semitones = smooth_anchor_values(times_s, F0_ANCHORS)
    if micro:
        semitones = semitones + 0.08 * np.sin(2.0 * np.pi * 7.0 * times_s)
        semitones = semitones + 0.04 * np.sin(2.0 * np.pi * 13.0 * times_s)
    f0 = BASE_F0_HZ * np.power(2.0, semitones / 12.0)
    gain = smooth_anchor_values(times_s, GAIN_ANCHORS)
    return np.asarray(f0, dtype=np.float64), np.asarray(gain, dtype=np.float64)


def build_sources() -> tuple[dict[str, SourceResult], LFParameters]:
    sample_count = int(round(DURATION_S * SAMPLE_RATE_HZ))
    times_s = np.arange(sample_count, dtype=np.float64) / SAMPLE_RATE_HZ
    params = lf_parameters()
    lf_phase, lf_flow = lf_flow_shape(params)

    sources: dict[str, SourceResult] = {}

    smooth_case = next(
        case for case in EXP12.SOURCE_CASES if case.name == "smooth_flow_oq0.6"
    )
    smooth = EXP12.source_waveform(smooth_case)
    fixed_f0 = np.full(sample_count, BASE_F0_HZ, dtype=np.float64)
    fixed_cycles = cycles_from_f0(fixed_f0)
    fixed_gain = common_file_envelope(sample_count)
    smooth_opening = np.interp(np.mod(fixed_cycles, 1.0), lf_phase, lf_flow)
    sources["smooth_fixed"] = SourceResult(
        "smooth_fixed",
        smooth,
        smooth.copy(),
        np.zeros_like(smooth),
        fixed_cycles,
        fixed_f0,
        fixed_gain,
        smooth_opening,
    )

    lf_opening_fixed = np.interp(np.mod(fixed_cycles, 1.0), lf_phase, lf_flow)
    lf_fixed_det = lf_opening_fixed * fixed_gain
    lf_fixed = normalize_peak(lf_fixed_det)
    sources["lf_fixed"] = SourceResult(
        "lf_fixed",
        lf_fixed,
        lf_fixed.copy(),
        np.zeros_like(lf_fixed),
        fixed_cycles,
        fixed_f0,
        fixed_gain,
        lf_opening_fixed,
    )

    macro_f0, macro_gain = macro_controls(times_s, micro=False)
    macro_cycles = cycles_from_f0(macro_f0)
    macro_opening = np.interp(np.mod(macro_cycles, 1.0), lf_phase, lf_flow)
    macro_det_pre = macro_opening * macro_gain
    macro = normalize_peak(macro_det_pre)
    sources["lf_macroprosody"] = SourceResult(
        "lf_macroprosody",
        macro,
        macro.copy(),
        np.zeros_like(macro),
        macro_cycles,
        macro_f0,
        macro_gain,
        macro_opening,
    )

    micro_f0, micro_gain = macro_controls(times_s, micro=True)
    micro_cycles = cycles_from_f0(micro_f0)
    micro_opening = np.interp(np.mod(micro_cycles, 1.0), lf_phase, lf_flow)
    micro_det_pre = micro_opening * micro_gain
    rng = np.random.default_rng(RNG_SEED)
    pre_peak = float(np.max(np.abs(micro_det_pre)))
    raw_noise = rng.normal(0.0, 1.0, sample_count)
    noise_pre = 0.02 * pre_peak * raw_noise * np.sqrt(np.maximum(micro_opening, 0.0))
    combined_pre = micro_det_pre + noise_pre
    combined_peak = float(np.max(np.abs(combined_pre)))
    if combined_peak <= 0.0 or not math.isfinite(combined_peak):
        raise RuntimeError("micro source normalization failed")
    scale = SOURCE_PEAK_M3_S / combined_peak
    micro_det = np.asarray(micro_det_pre * scale, dtype=np.float64)
    noise = np.asarray(noise_pre * scale, dtype=np.float64)
    micro = np.asarray(micro_det + noise, dtype=np.float64)
    sources["lf_macroprosody_micro"] = SourceResult(
        "lf_macroprosody_micro",
        micro,
        micro_det,
        noise,
        micro_cycles,
        micro_f0,
        micro_gain,
        micro_opening,
    )

    return sources, params


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(values, dtype=np.float64) ** 2)))


def fixed_lag_correlation(
    values: np.ndarray,
    *,
    lag_samples: int = PITCH_PERIOD_SAMPLES,
    start_s: float = STEADY_START_S,
    end_s: float = STEADY_END_S,
) -> float:
    start = int(round(start_s * SAMPLE_RATE_HZ))
    end = min(int(round(end_s * SAMPLE_RATE_HZ)), values.size)
    a = np.asarray(values[start : end - lag_samples], dtype=np.float64)
    b = np.asarray(values[start + lag_samples : end], dtype=np.float64)
    if a.size < 2 or rms(a) <= 0.0 or rms(b) <= 0.0:
        return math.nan
    return float(np.corrcoef(a, b)[0, 1])


def block_rms(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    size = int(round(BLOCK_S * SAMPLE_RATE_HZ))
    step = int(round(BLOCK_STEP_S * SAMPLE_RATE_HZ))
    starts = np.arange(0, max(values.size - size + 1, 1), step, dtype=np.int64)
    centers = (starts + size / 2.0) / SAMPLE_RATE_HZ
    measurements = np.asarray(
        [rms(values[start : start + size]) for start in starts], dtype=np.float64
    )
    return centers, measurements


def envelope_cv(values: np.ndarray) -> float:
    centers, envelope = block_rms(values)
    mask = (centers >= STEADY_START_S) & (centers <= STEADY_END_S)
    selected = envelope[mask]
    mean = float(np.mean(selected))
    return float(np.std(selected) / mean) if mean > 0.0 else math.nan


def spectral_flatness(values: np.ndarray) -> float:
    spectrum = np.fft.rfft(np.asarray(values, dtype=np.float64))
    power = np.abs(spectrum) ** 2
    frequencies = np.fft.rfftfreq(values.size, d=1.0 / SAMPLE_RATE_HZ)
    selected = power[(frequencies > 0.0) & (frequencies <= 8_000.0)]
    if selected.size == 0:
        return math.nan
    floor = max(float(np.max(selected)) * 1e-15, np.finfo(np.float64).tiny)
    selected = np.maximum(selected, floor)
    return float(np.exp(np.mean(np.log(selected))) / np.mean(selected))


def cycle_boundary_jump_ratio(result: SourceResult) -> float:
    cycle_index = np.floor(result.cycles).astype(np.int64)
    boundaries = np.flatnonzero(cycle_index[1:] != cycle_index[:-1]) + 1
    if boundaries.size == 0:
        return math.nan
    jumps = np.abs(result.source[boundaries] - result.source[boundaries - 1])
    denominator = rms(result.source)
    return float(np.max(jumps) / denominator) if denominator > 0.0 else math.inf


def realized_f0(result: SourceResult) -> np.ndarray:
    values = np.empty_like(result.planned_f0_hz)
    if values.size == 0:
        return values
    if values.size == 1:
        values[0] = result.planned_f0_hz[0]
        return values
    values[:-1] = np.diff(result.cycles) * SAMPLE_RATE_HZ
    values[-1] = values[-2]
    return values


def f0_rmse(result: SourceResult) -> float:
    realized = realized_f0(result)
    return float(np.sqrt(np.mean((realized - result.planned_f0_hz) ** 2)))


def envelope_correlation(result: SourceResult) -> float:
    centers, measured = block_rms(result.deterministic)
    planned = np.interp(
        centers,
        np.arange(result.planned_gain.size, dtype=np.float64) / SAMPLE_RATE_HZ,
        result.planned_gain,
    )
    mask = planned > 0.10
    measured = measured[mask]
    planned = planned[mask]
    if measured.size < 2:
        return math.nan
    measured = measured / max(float(np.max(measured)), 1e-30)
    planned = planned / max(float(np.max(planned)), 1e-30)
    return float(np.corrcoef(measured, planned)[0, 1])


def window_mean(values: np.ndarray, start_s: float, end_s: float) -> float:
    start = int(round(start_s * SAMPLE_RATE_HZ))
    end = int(round(end_s * SAMPLE_RATE_HZ))
    return float(np.mean(values[start:end]))


def window_rms(values: np.ndarray, start_s: float, end_s: float) -> float:
    start = int(round(start_s * SAMPLE_RATE_HZ))
    end = int(round(end_s * SAMPLE_RATE_HZ))
    return rms(values[start:end])


def source_metrics(result: SourceResult) -> dict[str, float]:
    basic = EXP12.basic_signal_metrics(result.source)
    return {
        **basic,
        "cycle_boundary_jump_per_rms": cycle_boundary_jump_ratio(result),
        "fixed_10ms_lag_correlation": fixed_lag_correlation(result.source),
        "rms_envelope_cv": envelope_cv(result.source),
        "spectral_flatness": spectral_flatness(result.source),
        "noise_rms": rms(result.noise),
        "noise_rms_over_source_rms": rms(result.noise) / max(rms(result.source), 1e-30),
        "f0_rmse_hz": f0_rmse(result),
        "envelope_correlation": envelope_correlation(result),
    }


def verify_oracle(params: LFParameters) -> dict[str, float]:
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    expected = {
        "ra": float(oracle["ra"]),
        "rk": float(oracle["rk"]),
        "rg": float(oracle["rg"]),
        "tp": float(oracle["tp_over_t0"]),
        "te": float(oracle["te_over_t0"]),
        "ta": float(oracle["ta_over_t0"]),
        "alpha": float(oracle["alpha_times_t0"]),
    }
    actual = {
        "ra": params.ra,
        "rk": params.rk,
        "rg": params.rg,
        "tp": params.tp,
        "te": params.te,
        "ta": params.ta,
        "alpha": params.alpha,
    }
    errors = {key: abs(actual[key] - expected[key]) for key in expected}
    dim_tol = float(oracle["tolerance"]["dimensionless_absolute"])
    alpha_tol = float(oracle["tolerance"]["alpha_times_t0_absolute"])
    if max(errors[key] for key in ("ra", "rk", "rg", "tp", "te", "ta")) > dim_tol:
        raise RuntimeError("LF Rd mapping disagrees with Wolfram oracle")
    if errors["alpha"] > alpha_tol:
        raise RuntimeError("LF alpha root disagrees with Wolfram oracle")
    if abs(params.balance) > float(
        oracle["tolerance"]["normalized_net_integral_absolute"]
    ):
        raise RuntimeError("LF integral constraint failed")
    return errors


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_controls(path: Path, sources: dict[str, SourceResult]) -> None:
    names = ("lf_macroprosody", "lf_macroprosody_micro")
    step = int(round(0.001 * SAMPLE_RATE_HZ))
    rows: list[dict[str, object]] = []
    for name in names:
        result = sources[name]
        realized = realized_f0(result)
        for index in range(0, result.source.size, step):
            rows.append(
                {
                    "condition": name,
                    "time_s": index / SAMPLE_RATE_HZ,
                    "planned_f0_hz": result.planned_f0_hz[index],
                    "realized_f0_hz": realized[index],
                    "planned_gain": result.planned_gain[index],
                    "opening": result.opening[index],
                    "source_m3_s": result.source[index],
                    "noise_m3_s": result.noise[index],
                }
            )
    write_csv(path, rows)


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    sources, params = build_sources()
    oracle_errors = verify_oracle(params)

    source_rows: list[dict[str, object]] = []
    source_metric_map: dict[str, dict[str, float]] = {}
    fixed_rows: list[dict[str, object]] = []
    fixed_waveforms: dict[str, np.ndarray] = {}
    listening_waveforms: dict[str, np.ndarray] = {}

    sequential = EXP12.find_condition("sequential")
    for name, result in sources.items():
        metrics = source_metrics(result)
        source_metric_map[name] = metrics
        np.save(output_dir / f"source_{name}.npy", result.source)
        source_rows.append({"condition": name, **metrics})

        fixed = EXP12.render_fixed_tract(
            result.source,
            hop_size=EXP12.DEFAULT_HOP_SIZE,
            edge_mode="preroll_edge",
        )
        fixed_waveforms[name] = fixed
        fixed_basic = EXP12.basic_signal_metrics(fixed)
        fixed_gain = EXP12.EXP9.write_listening_wav(
            output_dir / f"fixed_{name}_listen.wav", fixed
        )
        fixed_rows.append(
            {
                "condition": name,
                "raw_peak_pa": float(np.max(np.abs(fixed))),
                "raw_rms_pa": rms(fixed),
                "crest_factor": fixed_basic["crest_factor"],
                "max_abs_derivative_per_rms": fixed_basic[
                    "max_abs_derivative_per_rms"
                ],
                "energy_ratio_ge_2khz": fixed_basic["energy_ratio_ge_2khz"],
                "pitch_phase_peak_ratio": EXP12.phase_peak_ratio(
                    fixed, PITCH_PERIOD_SAMPLES
                ),
                "startup_peak_over_steady_rms": EXP12.startup_peak_over_steady_rms(
                    fixed
                ),
                "listening_gain_fullscale_per_pa": fixed_gain,
                "finite": bool(np.all(np.isfinite(fixed))),
            }
        )

        listening = EXP12.render_coordination(
            sequential,
            result.source,
            control_step_s=EXP12.CONTROL_STEP_S,
            hop_size=EXP12.DEFAULT_HOP_SIZE,
            edge_mode="preroll_edge",
        )
        listening_waveforms[name] = listening
        EXP12.EXP9.write_listening_wav(
            output_dir / f"listen_{name}.wav", listening
        )
        np.save(output_dir / f"listen_{name}_raw_pressure_pa.npy", listening)

    write_csv(output_dir / "source_metrics.csv", source_rows)
    write_csv(output_dir / "fixed_tract_metrics.csv", fixed_rows)
    write_controls(output_dir / "control_trajectories.csv", sources)

    control_rows: list[dict[str, object]] = []
    for name in ("lf_macroprosody", "lf_macroprosody_micro"):
        result = sources[name]
        realized = realized_f0(result)
        pre_f0 = window_mean(realized, 0.20, 0.235)
        post_f0 = window_mean(realized, 0.285, 0.320)
        pre_amp = window_rms(result.deterministic, 0.20, 0.235)
        boundary_amp = window_rms(result.deterministic, 0.242, 0.258)
        post_amp = window_rms(result.deterministic, 0.285, 0.320)
        control_rows.append(
            {
                "condition": name,
                "f0_rmse_hz": source_metric_map[name]["f0_rmse_hz"],
                "envelope_correlation": source_metric_map[name]["envelope_correlation"],
                "pre_boundary_mean_f0_hz": pre_f0,
                "post_boundary_mean_f0_hz": post_f0,
                "boundary_f0_reset_hz": post_f0 - pre_f0,
                "pre_boundary_rms": pre_amp,
                "boundary_rms": boundary_amp,
                "post_boundary_rms": post_amp,
                "boundary_rms_over_prepost_mean": boundary_amp
                / max(0.5 * (pre_amp + post_amp), 1e-30),
            }
        )
    write_csv(output_dir / "control_metrics.csv", control_rows)

    c3 = sources["lf_macroprosody_micro"].source
    coordination_rows: list[dict[str, object]] = []
    coordination_waveforms: dict[str, np.ndarray] = {}
    sensitivities: dict[str, float] = {}
    for condition_name in ("sequential", "overlap"):
        condition = EXP12.find_condition(condition_name)
        candidate = EXP12.render_coordination(
            condition,
            c3,
            control_step_s=EXP12.CONTROL_STEP_S,
            hop_size=EXP12.DEFAULT_HOP_SIZE,
            edge_mode="preroll_edge",
        )
        reference = EXP12.render_coordination(
            condition,
            c3,
            control_step_s=EXP12.REFERENCE_CONTROL_STEP_S,
            hop_size=EXP12.REFERENCE_HOP_SIZE,
            edge_mode="preroll_edge",
        )
        coordination_waveforms[condition_name] = candidate
        sensitivity = EXP12.normalized_rms_difference(reference, candidate)
        sensitivities[condition_name] = sensitivity
        EXP12.EXP9.write_listening_wav(
            output_dir / f"coordination_{condition_name}_listen.wav", candidate
        )
        coordination_rows.append(
            {
                "condition": condition_name,
                "discretization_normalized_rms_difference": sensitivity,
                "finite": bool(np.all(np.isfinite(candidate))),
            }
        )

    coordination_effect = EXP12.normalized_rms_difference(
        coordination_waveforms["sequential"], coordination_waveforms["overlap"]
    )
    for row in coordination_rows:
        row["sequential_vs_overlap_normalized_rms_difference"] = coordination_effect
    write_csv(output_dir / "coordination_retention.csv", coordination_rows)

    fixed_map = {str(row["condition"]): row for row in fixed_rows}
    control_map = {str(row["condition"]): row for row in control_rows}

    h1 = bool(
        source_metric_map["lf_fixed"]["cycle_boundary_jump_per_rms"] < 0.01
        and float(fixed_map["lf_fixed"]["startup_peak_over_steady_rms"]) < 20.0
        and bool(fixed_map["lf_fixed"]["finite"])
    )
    h2 = bool(
        source_metric_map["lf_macroprosody"]["f0_rmse_hz"] <= 0.1
        and source_metric_map["lf_macroprosody"]["envelope_correlation"] >= 0.95
        and source_metric_map["lf_macroprosody"]["fixed_10ms_lag_correlation"]
        <= source_metric_map["lf_fixed"]["fixed_10ms_lag_correlation"] - 0.01
        and float(control_map["lf_macroprosody"]["boundary_f0_reset_hz"]) >= 5.0
        and float(
            control_map["lf_macroprosody"]["boundary_rms_over_prepost_mean"]
        )
        <= 0.8
        and float(
            fixed_map["lf_macroprosody"]["startup_peak_over_steady_rms"]
        )
        < 20.0
        and bool(fixed_map["lf_macroprosody"]["finite"])
    )
    h3 = bool(
        source_metric_map["lf_macroprosody_micro"]["spectral_flatness"]
        > source_metric_map["lf_macroprosody"]["spectral_flatness"]
        and source_metric_map["lf_macroprosody_micro"]["noise_rms"] > 0.0
        and source_metric_map["lf_macroprosody_micro"][
            "cycle_boundary_jump_per_rms"
        ]
        < 0.01
        and source_metric_map["lf_macroprosody_micro"]["f0_rmse_hz"] <= 0.1
        and source_metric_map["lf_macroprosody_micro"]["envelope_correlation"]
        >= 0.95
        and bool(fixed_map["lf_macroprosody_micro"]["finite"])
    )
    max_sensitivity = max(sensitivities.values())
    h4 = bool(
        coordination_effect > 0.01
        and coordination_effect > 5.0 * max_sensitivity
        and all(np.all(np.isfinite(x)) for x in coordination_waveforms.values())
    )

    if h1 and h2 and h3 and h4:
        decision = "PARAMETRIC_CONTROLS_VALIDATED"
    else:
        decision = "REVISE"

    result = {
        "decision": decision,
        "h1_lf_pulse_capability_pass": h1,
        "h2_macroprosody_realization_pass": h2,
        "h3_micro_aspiration_realization_pass": h3,
        "h4_coordination_retention_pass": h4,
        "lf_parameters": {
            "rd": params.rd,
            "ra": params.ra,
            "rk": params.rk,
            "rg": params.rg,
            "tp_over_t0": params.tp,
            "te_over_t0": params.te,
            "ta_over_t0": params.ta,
            "alpha_times_t0": params.alpha,
            "normalized_net_derivative_integral": params.balance,
        },
        "wolfram_oracle_absolute_errors": oracle_errors,
        "source_metrics": source_metric_map,
        "macroprosody_boundary": control_map["lf_macroprosody"],
        "coordination": {
            "sequential_vs_overlap_normalized_rms_difference": coordination_effect,
            "discretization_normalized_rms_difference": sensitivities,
        },
        "limitations": [
            "LF-family source is experiment-local and not a production laryngeal API",
            "prosody contour is diagnostic rather than canonical Japanese prosody",
            "aspiration is an explicit seeded noise probe, not a physiological turbulence model",
            "quasi-stationary short-time tract filtering has no carried acoustic state",
            "objective metrics do not establish perceptual naturalness or voice-likeness",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path, default=Path("experiment-013-output")
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
