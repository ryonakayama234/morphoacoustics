from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path
from types import ModuleType
import wave

import numpy as np

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "smooth_source_oracle.json"

HARMONIC_COUNT = 40
RNG_SEED = 25025
SOURCE_RATIO_TOLERANCE_DB = 0.25
RENDERED_RATIO_TOLERANCE_DB = 2.5
MIN_I_IMPROVEMENT_DB = 10.0
SOURCE_CYCLE_JUMP_LIMIT = 0.01
STARTUP_PEAK_LIMIT = 20.0

HARMONICS = {
    "a": (7, 13),
    "i": (3, 23),
    "u": (4, 15),
}


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP23 = load_module(
    "morpho_exp023_for_025",
    EXPERIMENTS / "023_static_vowel_calibration" / "run.py",
)
EXP13 = EXP23.EXP13
EXP12 = EXP23.EXP12


def diagnostic_source() -> object:
    sample_count = int(round(EXP23.DURATION_S * EXP23.SAMPLE_RATE_HZ))
    times_s = np.arange(sample_count, dtype=np.float64) / EXP23.SAMPLE_RATE_HZ
    raw = np.zeros(sample_count, dtype=np.float64)
    for harmonic in range(1, HARMONIC_COUNT + 1):
        raw += np.cos(
            2.0 * np.pi * harmonic * EXP23.BASE_F0_HZ * times_s
        ) / (harmonic * harmonic)

    gain = EXP13.common_file_envelope(sample_count)
    deterministic_pre = raw * gain
    source = EXP13.normalize_peak(deterministic_pre)
    fixed_f0 = np.full(sample_count, EXP23.BASE_F0_HZ, dtype=np.float64)
    cycles = EXP13.cycles_from_f0(fixed_f0)

    return EXP13.SourceResult(
        "diagnostic_cos_1_over_n2",
        source,
        source.copy(),
        np.zeros_like(source),
        cycles,
        fixed_f0,
        gain,
        np.zeros_like(source),
    )


def steady(values: np.ndarray) -> np.ndarray:
    start = int(round(EXP23.STEADY_START_S * EXP23.SAMPLE_RATE_HZ))
    end = int(round(EXP23.STEADY_END_S * EXP23.SAMPLE_RATE_HZ))
    return np.asarray(values[start:end], dtype=np.float64)


def harmonic_ratio_db(values: np.ndarray, n1: int, n2: int) -> float:
    selected = steady(values)
    spectrum = np.fft.rfft(selected)
    frequencies = np.fft.rfftfreq(
        selected.size, d=1.0 / EXP23.SAMPLE_RATE_HZ
    )
    f1 = n1 * EXP23.BASE_F0_HZ
    f2 = n2 * EXP23.BASE_F0_HZ
    i1 = int(np.argmin(np.abs(frequencies - f1)))
    i2 = int(np.argmin(np.abs(frequencies - f2)))
    a1 = float(np.abs(spectrum[i1]))
    a2 = float(np.abs(spectrum[i2]))
    if a1 <= 0.0 or a2 <= 0.0:
        return -math.inf
    return 20.0 * math.log10(a2 / a1)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_wav(path: Path, values: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    waveform = np.asarray(values, dtype=np.float64)
    if np.any(~np.isfinite(waveform)):
        raise RuntimeError(f"{path}: non-finite waveform")
    peak = float(np.max(np.abs(waveform)))
    if peak > 0.9000001:
        raise RuntimeError(f"{path}: would clip at {peak}")
    pcm = np.round(waveform * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(EXP23.SAMPLE_RATE_HZ)
        wav.writeframes(pcm.tobytes())


def normalize_listening(
    pressures: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], dict[str, object]]:
    normalized: dict[str, np.ndarray] = {}
    raw_rms: dict[str, float] = {}
    for vowel, values in pressures.items():
        value = EXP23.steady_rms(values)
        if not math.isfinite(value) or value <= 0.0:
            raise RuntimeError(f"{vowel}: invalid steady RMS")
        raw_rms[vowel] = value
        normalized[vowel] = np.asarray(values / value, dtype=np.float64)

    max_abs = max(float(np.max(np.abs(v))) for v in normalized.values())
    common_gain = 0.90 / max_abs
    listening = {
        vowel: np.asarray(values * common_gain, dtype=np.float64)
        for vowel, values in normalized.items()
    }
    listening_rms = {
        vowel: EXP23.steady_rms(values) for vowel, values in listening.items()
    }
    spread = max(listening_rms.values()) - min(listening_rms.values())
    no_clipping = all(
        float(np.max(np.abs(values))) <= 0.9000001
        for values in listening.values()
    )
    return listening, {
        "method": "Experiment 023 steady-RMS normalization plus one common safety gain",
        "raw_steady_rms_pa": raw_rms,
        "common_safety_gain": common_gain,
        "listening_steady_rms_fullscale": listening_rms,
        "listening_rms_spread_fullscale": spread,
        "no_clipping": no_clipping,
    }


def make_blind_set(
    output_dir: Path,
    listening: dict[str, np.ndarray],
) -> None:
    blind_dir = output_dir / "listening" / "s2_primary_blind"
    blind_dir.mkdir(parents=True, exist_ok=True)
    targets = [vowel for vowel in ("a", "i", "u") for _ in range(10)]
    rng = np.random.default_rng(RNG_SEED)
    order = list(rng.permutation(targets))

    public_rows: list[dict[str, object]] = []
    key_rows: list[dict[str, object]] = []
    for index, vowel in enumerate(order, start=1):
        trial_id = f"T{index:02d}"
        filename = f"{trial_id}.wav"
        write_wav(blind_dir / filename, listening[str(vowel)])
        public_rows.append({"trial_id": trial_id, "file": filename})
        key_rows.append(
            {"trial_id": trial_id, "vowel": str(vowel), "file": filename}
        )

    write_csv(blind_dir / "manifest.csv", public_rows)
    write_csv(
        blind_dir / "response_template.csv",
        [
            {
                "trial_id": row["trial_id"],
                "file": row["file"],
                "perceived_vowel": "",
                "confidence": "",
                "voice_quality": "",
                "notes": "",
            }
            for row in public_rows
        ],
    )
    write_csv(output_dir / "blind_key.csv", key_rows)
    (blind_dir / "README.txt").write_text(
        "Experiment 025 S2 blind vowel identification\n"
        "For T01..T30 choose a, i, u, or UNIDENTIFIABLE.\n"
        "Record quality separately from categorical identity.\n"
        "Do not inspect blind_key.csv before responses are frozen.\n",
        encoding="utf-8",
    )


def run(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))

    baseline_sources, _ = EXP13.build_sources()
    s0 = baseline_sources["lf_fixed"]
    s2 = diagnostic_source()
    sources = {"S0_lf_fixed": s0, "S2_cos_1_over_n2": s2}

    geometries = {
        vowel: EXP23.primary_geometry(vowel)
        for vowel in ("a", "i", "u")
    }

    # Re-check the Experiment 023 tract oracle without changing geometry.
    tract_oracle = json.loads(EXP23.ORACLE_PATH.read_text(encoding="utf-8"))
    tract_oracle_errors: dict[str, list[float]] = {}
    tract_oracle_pass = True
    for vowel, geometry in geometries.items():
        actual = EXP23.peak_frequencies(geometry)
        expected = np.asarray(
            tract_oracle["peak_frequencies_hz"][vowel], dtype=np.float64
        )
        errors = np.abs(actual - expected)
        tract_oracle_errors[vowel] = errors.tolist()
        tract_oracle_pass = tract_oracle_pass and bool(
            np.all(errors <= float(tract_oracle["peak_tolerance_hz"]))
        )

    source_rows: list[dict[str, object]] = []
    source_ratio_errors: dict[str, float] = {}
    for vowel, (n1, n2) in HARMONICS.items():
        s0_ratio = harmonic_ratio_db(s0.source, n1, n2)
        s2_ratio = harmonic_ratio_db(s2.source, n1, n2)
        expected = float(oracle["source_p2_over_p1_db"][vowel])
        error = abs(s2_ratio - expected)
        source_ratio_errors[vowel] = error
        source_rows.append(
            {
                "vowel": vowel,
                "n1": n1,
                "n2": n2,
                "s0_source_p2_over_p1_db": s0_ratio,
                "s2_source_p2_over_p1_db": s2_ratio,
                "s2_oracle_db": expected,
                "s2_abs_error_db": error,
            }
        )
    write_csv(output_dir / "source_harmonic_metrics.csv", source_rows)
    source_oracle_pass = all(
        error <= SOURCE_RATIO_TOLERANCE_DB
        for error in source_ratio_errors.values()
    )

    source_metrics = {
        name: EXP13.source_metrics(result)
        for name, result in sources.items()
    }
    source_artifact_pass = all(
        metrics["cycle_boundary_jump_per_rms"] < SOURCE_CYCLE_JUMP_LIMIT
        for metrics in source_metrics.values()
    )

    rendered: dict[str, dict[str, np.ndarray]] = {}
    rendered_rows: list[dict[str, object]] = []
    startup_pass = True
    finite_pass = True
    rendered_oracle_pass = True
    s0_ratios: dict[str, float] = {}
    s2_ratios: dict[str, float] = {}

    for source_name, source_result in sources.items():
        rendered[source_name] = {}
        for vowel, geometry in geometries.items():
            pressure = EXP23.render_static(source_result.source, geometry)
            rendered[source_name][vowel] = pressure
            finite = bool(np.all(np.isfinite(pressure)))
            finite_pass = finite_pass and finite
            startup = EXP12.startup_peak_over_steady_rms(pressure)
            startup_pass = startup_pass and bool(startup < STARTUP_PEAK_LIMIT)
            n1, n2 = HARMONICS[vowel]
            ratio = harmonic_ratio_db(pressure, n1, n2)

            if source_name == "S0_lf_fixed":
                s0_ratios[vowel] = ratio
                expected = math.nan
                error = math.nan
            else:
                s2_ratios[vowel] = ratio
                expected = float(
                    oracle["predicted_listening_pressure_p2_over_p1_db"][vowel]
                )
                error = abs(ratio - expected)
                rendered_oracle_pass = rendered_oracle_pass and bool(
                    error <= RENDERED_RATIO_TOLERANCE_DB
                )

            rendered_rows.append(
                {
                    "source": source_name,
                    "vowel": vowel,
                    "p2_over_p1_db": ratio,
                    "oracle_db": expected,
                    "oracle_abs_error_db": error,
                    "startup_peak_over_steady_rms": startup,
                    "finite": finite,
                }
            )
    write_csv(output_dir / "rendered_cue_metrics.csv", rendered_rows)

    i_improvement_db = s2_ratios["i"] - s0_ratios["i"]
    i_improvement_pass = bool(i_improvement_db >= MIN_I_IMPROVEMENT_DB)

    listening, normalization = normalize_listening(rendered["S2_cos_1_over_n2"])
    level_match_pass = bool(
        normalization["no_clipping"]
        and float(normalization["listening_rms_spread_fullscale"]) <= 1e-12
    )
    for vowel, values in listening.items():
        write_wav(
            output_dir / "listening" / "s2_named_calibration" / f"{vowel}.wav",
            values,
        )
    make_blind_set(output_dir, listening)
    (output_dir / "listening_normalization.json").write_text(
        json.dumps(normalization, indent=2) + "\n",
        encoding="utf-8",
    )

    objective_pass = all(
        (
            tract_oracle_pass,
            source_oracle_pass,
            source_artifact_pass,
            finite_pass,
            startup_pass,
            rendered_oracle_pass,
            i_improvement_pass,
            level_match_pass,
        )
    )

    decision = (
        "SMOOTH_SOURCE_DIAGNOSTIC_READY_FOR_LISTENING"
        if objective_pass
        else "SMOOTH_SOURCE_OBJECTIVE_GATE_FAILED"
    )

    result = {
        "decision": decision,
        "objective_gate_pass": objective_pass,
        "tract_oracle_pass": tract_oracle_pass,
        "tract_oracle_abs_errors_hz": tract_oracle_errors,
        "source_oracle_pass": source_oracle_pass,
        "source_ratio_abs_errors_db": source_ratio_errors,
        "source_cycle_artifact_pass": source_artifact_pass,
        "source_cycle_boundary_jump_per_rms": {
            name: metrics["cycle_boundary_jump_per_rms"]
            for name, metrics in source_metrics.items()
        },
        "rendered_oracle_pass": rendered_oracle_pass,
        "s0_rendered_p2_over_p1_db": s0_ratios,
        "s2_rendered_p2_over_p1_db": s2_ratios,
        "i_improvement_db": i_improvement_db,
        "minimum_i_improvement_db": MIN_I_IMPROVEMENT_DB,
        "i_improvement_pass": i_improvement_pass,
        "startup_artifact_pass": startup_pass,
        "all_rendered_finite": finite_pass,
        "level_match_pass": level_match_pass,
        "normalization": normalization,
        "human_gate": {
            "seed": RNG_SEED,
            "trials": 30,
            "per_vowel": 10,
            "choices": ["a", "i", "u", "UNIDENTIFIABLE"],
            "per_vowel_threshold": ">=8/10",
            "overall_threshold": ">=24/30",
        },
        "claim_boundary": (
            "S2 is a diagnostic excitation only; objective success does not "
            "establish a biological source model or vowel identification."
        ),
    }
    (output_dir / "decision.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-025-output"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), indent=2))


if __name__ == "__main__":
    main()
