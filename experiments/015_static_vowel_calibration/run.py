from __future__ import annotations

import argparse
import csv
import importlib.util
import itertools
import json
import math
import platform
import sys
import time
import wave
from pathlib import Path
from types import ModuleType

import numpy as np

from morphoacoustics.physical import Tract1DGeometry, TubeSection

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "vowel_tube_oracle.json"

SAMPLE_RATE_HZ = 48_000
DURATION_S = 0.50
BASE_F0_HZ = 100.0
RD = 1.0
PRIMARY_SECTION_LENGTH_M = 0.010
REFINED_SECTION_LENGTH_M = 0.005
PRIMARY_SECTION_COUNT = 16
REFINED_SECTION_COUNT = 32
STEADY_START_S = 0.05
STEADY_END_S = 0.45
PRIMARY_TRIALS_PER_VOWEL = 10
RNG_SEED = 15015
DISCRETIZATION_MARGIN = 5.0
SOURCE_CYCLE_JUMP_LIMIT = 0.01
STARTUP_PEAK_LIMIT = 20.0

SOURCE_URL = "https://splab.net/apd/ja/g210/"
SOURCE_CITATION = (
    "T. Arai (2007), Education system in acoustics of speech production "
    "using physical models of the human vocal tract, "
    "Acoustical Science and Technology 28(3), 190-201."
)

# Published web-table order is lips -> larynx, in millimetres.
PUBLISHED_DIAMETERS_MM: dict[str, tuple[float, ...]] = {
    "a": (32, 28, 30, 34, 34, 38, 34, 30, 26, 20, 14, 12, 16, 26, 12, 12),
    "i": (24, 14, 12, 10, 10, 10, 16, 24, 32, 32, 32, 32, 32, 32, 12, 12),
    "u": (16, 14, 20, 22, 22, 24, 22, 14, 18, 26, 30, 30, 30, 30, 12, 12),
}


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP13 = load_experiment_module(
    "morpho_exp013_for_015",
    EXPERIMENTS / "013_parametric_source_prosody" / "run.py",
)
EXP12 = EXP13.EXP12
EXP9 = EXP12.EXP9


def diameter_mm_to_area_m2(diameter_mm: float) -> float:
    diameter_m = float(diameter_mm) / 1000.0
    return math.pi * (diameter_m / 2.0) ** 2


def primary_diameters_glottis_to_lips(vowel: str) -> np.ndarray:
    published = np.asarray(PUBLISHED_DIAMETERS_MM[vowel], dtype=np.float64)
    return published[::-1].copy()


def geometry_from_diameters(
    vowel: str,
    diameters_mm_glottis_to_lips: np.ndarray,
    *,
    section_length_m: float,
    suffix: str,
) -> Tract1DGeometry:
    diameters = np.asarray(diameters_mm_glottis_to_lips, dtype=np.float64)
    if np.any(~np.isfinite(diameters)) or np.any(diameters <= 0.0):
        raise ValueError(f"{vowel}: diameters must be finite and positive")
    return Tract1DGeometry(
        cavity_id=f"oral-vowel-{vowel}-{suffix}",
        sections=tuple(
            TubeSection(
                length_m=section_length_m,
                area_m2=diameter_mm_to_area_m2(float(diameter)),
            )
            for diameter in diameters
        ),
    )


def primary_geometry(vowel: str) -> Tract1DGeometry:
    return geometry_from_diameters(
        vowel,
        primary_diameters_glottis_to_lips(vowel),
        section_length_m=PRIMARY_SECTION_LENGTH_M,
        suffix="16x10mm",
    )


def regridded_diameters(vowel: str) -> np.ndarray:
    primary = primary_diameters_glottis_to_lips(vowel)
    x_primary = (np.arange(PRIMARY_SECTION_COUNT, dtype=np.float64) + 0.5) * (
        PRIMARY_SECTION_LENGTH_M
    )
    x_refined = (np.arange(REFINED_SECTION_COUNT, dtype=np.float64) + 0.5) * (
        REFINED_SECTION_LENGTH_M
    )
    return np.interp(
        x_refined,
        x_primary,
        primary,
        left=float(primary[0]),
        right=float(primary[-1]),
    )


def refined_geometry(vowel: str) -> Tract1DGeometry:
    return geometry_from_diameters(
        vowel,
        regridded_diameters(vowel),
        section_length_m=REFINED_SECTION_LENGTH_M,
        suffix="32x5mm-linear-center-regrid",
    )


def peak_frequencies(geometry: Tract1DGeometry, count: int = 5) -> np.ndarray:
    peaks = EXP9.response_peaks(geometry, count=count)
    values = np.asarray([frequency for frequency, _ in peaks], dtype=np.float64)
    if values.shape != (count,):
        raise RuntimeError(
            f"{geometry.cavity_id}: expected {count} response peaks, got {len(values)}"
        )
    return values


def render_static(source: np.ndarray, geometry: Tract1DGeometry) -> np.ndarray:
    def transfer_for_time(_: float, frequencies_hz: np.ndarray) -> np.ndarray:
        return EXP9.far_field_pressure_transfer(geometry, frequencies_hz)

    return EXP12.frame_render(
        source,
        transfer_for_time,
        hop_size=EXP12.DEFAULT_HOP_SIZE,
        edge_mode="preroll_edge",
    )


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(values, dtype=np.float64) ** 2)))


def steady_rms(values: np.ndarray) -> float:
    start = int(round(STEADY_START_S * SAMPLE_RATE_HZ))
    end = int(round(STEADY_END_S * SAMPLE_RATE_HZ))
    return rms(np.asarray(values, dtype=np.float64)[start:end])


def write_wav(path: Path, waveform_fullscale: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    values = np.asarray(waveform_fullscale, dtype=np.float64)
    if np.any(~np.isfinite(values)):
        raise RuntimeError(f"{path.name}: non-finite listening waveform")
    peak = float(np.max(np.abs(values)))
    if peak > 0.9000001:
        raise RuntimeError(f"{path.name}: listening waveform would clip ({peak})")
    pcm = np.round(values * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE_HZ)
        wav.writeframes(pcm.tobytes())


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fixture_payload(
    primary_geometries: dict[str, Tract1DGeometry],
    refined_geometries: dict[str, Tract1DGeometry],
) -> dict[str, object]:
    return {
        "reference": {
            "url": SOURCE_URL,
            "citation": SOURCE_CITATION,
            "published_order": "lips_to_larynx",
            "morphoacoustics_order": "glottis_to_lips",
            "primary_section_length_m": PRIMARY_SECTION_LENGTH_M,
            "refined_section_length_m": REFINED_SECTION_LENGTH_M,
            "regrid": (
                "linear interpolation of diameter at cell centers with endpoint "
                "clamping; 16x10mm -> 32x5mm"
            ),
        },
        "vowels": {
            vowel: {
                "published_diameters_mm_lips_to_larynx": list(
                    PUBLISHED_DIAMETERS_MM[vowel]
                ),
                "primary_diameters_mm_glottis_to_lips": (
                    primary_diameters_glottis_to_lips(vowel).tolist()
                ),
                "refined_diameters_mm_glottis_to_lips": (
                    regridded_diameters(vowel).tolist()
                ),
                "primary_total_length_m": primary_geometries[vowel].total_length_m,
                "refined_total_length_m": refined_geometries[vowel].total_length_m,
                "primary_areas_m2": [
                    section.area_m2
                    for section in primary_geometries[vowel].sections
                ],
                "refined_areas_m2": [
                    section.area_m2
                    for section in refined_geometries[vowel].sections
                ],
            }
            for vowel in PUBLISHED_DIAMETERS_MM
        },
    }


def validate_fixture(
    primary_geometries: dict[str, Tract1DGeometry],
    refined_geometries: dict[str, Tract1DGeometry],
) -> bool:
    for vowel, published in PUBLISHED_DIAMETERS_MM.items():
        if len(published) != PRIMARY_SECTION_COUNT:
            return False
        if tuple(primary_diameters_glottis_to_lips(vowel)[::-1]) != tuple(
            float(value) for value in published
        ):
            return False

        primary = primary_geometries[vowel]
        refined = refined_geometries[vowel]
        if len(primary.sections) != PRIMARY_SECTION_COUNT:
            return False
        if len(refined.sections) != REFINED_SECTION_COUNT:
            return False
        if not math.isclose(
            primary.total_length_m,
            PRIMARY_SECTION_COUNT * PRIMARY_SECTION_LENGTH_M,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            return False
        if not math.isclose(
            refined.total_length_m,
            REFINED_SECTION_COUNT * REFINED_SECTION_LENGTH_M,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            return False
        for section in (*primary.sections, *refined.sections):
            if (
                not math.isfinite(section.length_m)
                or not math.isfinite(section.area_m2)
                or section.length_m <= 0.0
                or section.area_m2 <= 0.0
            ):
                return False
    return True


def make_blind_trials(
    output_dir: Path,
    listening_waveforms: dict[str, np.ndarray],
) -> None:
    blind_dir = output_dir / "listening" / "primary_blind"
    blind_dir.mkdir(parents=True, exist_ok=True)

    targets: list[str] = []
    for vowel in ("a", "i", "u"):
        targets.extend([vowel] * PRIMARY_TRIALS_PER_VOWEL)
    rng = np.random.default_rng(RNG_SEED)
    order = list(rng.permutation(targets))

    public_rows: list[dict[str, object]] = []
    key_rows: list[dict[str, object]] = []
    for index, vowel in enumerate(order, start=1):
        trial_id = f"T{index:02d}"
        filename = f"{trial_id}.wav"
        write_wav(blind_dir / filename, listening_waveforms[str(vowel)])
        public_rows.append({"trial_id": trial_id, "file": filename})
        key_rows.append(
            {"trial_id": trial_id, "vowel": str(vowel), "file": filename}
        )

    write_csv(blind_dir / "manifest.csv", public_rows)
    write_csv(output_dir / "blind_key.csv", key_rows)
    (blind_dir / "README.txt").write_text(
        "Experiment 015 primary blind vowel identification\n"
        "For each T01..T30 choose: a, i, u, or UNIDENTIFIABLE.\n"
        "Also record confidence, click/snap, voice-like vs alarm/buzzer-like, "
        "and optional notes.\n"
        "Do not inspect blind_key.csv before all responses are frozen.\n",
        encoding="utf-8",
    )


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    tolerance_hz = float(oracle["peak_tolerance_hz"])

    primary_geometries = {
        vowel: primary_geometry(vowel) for vowel in PUBLISHED_DIAMETERS_MM
    }
    refined_geometries = {
        vowel: refined_geometry(vowel) for vowel in PUBLISHED_DIAMETERS_MM
    }
    fixture_valid = validate_fixture(primary_geometries, refined_geometries)

    fixture = fixture_payload(primary_geometries, refined_geometries)
    (output_dir / "fixture_provenance.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    primary_peaks: dict[str, np.ndarray] = {}
    refined_peaks: dict[str, np.ndarray] = {}
    peak_rows: list[dict[str, object]] = []
    oracle_errors: dict[str, list[float]] = {}
    oracle_pass = True

    for vowel in ("a", "i", "u"):
        primary = peak_frequencies(primary_geometries[vowel])
        refined = peak_frequencies(refined_geometries[vowel], count=2)
        primary_peaks[vowel] = primary
        refined_peaks[vowel] = refined

        expected = np.asarray(
            oracle["peak_frequencies_hz"][vowel], dtype=np.float64
        )
        errors = np.abs(primary - expected)
        oracle_errors[vowel] = errors.tolist()
        oracle_pass = oracle_pass and bool(np.all(errors <= tolerance_hz))

        for rank, frequency_hz in enumerate(primary, start=1):
            peak_rows.append(
                {
                    "vowel": vowel,
                    "grid": "primary_16x10mm",
                    "rank": rank,
                    "frequency_hz": float(frequency_hz),
                    "oracle_frequency_hz": float(expected[rank - 1]),
                    "oracle_abs_error_hz": float(errors[rank - 1]),
                }
            )
        for rank, frequency_hz in enumerate(refined, start=1):
            peak_rows.append(
                {
                    "vowel": vowel,
                    "grid": "refined_32x5mm",
                    "rank": rank,
                    "frequency_hz": float(frequency_hz),
                    "oracle_frequency_hz": math.nan,
                    "oracle_abs_error_hz": math.nan,
                }
            )

    write_csv(output_dir / "resonance_peaks.csv", peak_rows)

    pair_rows: list[dict[str, object]] = []
    pair_distances: list[float] = []
    for left, right in itertools.combinations(("a", "i", "u"), 2):
        distance = float(
            np.linalg.norm(primary_peaks[left][:2] - primary_peaks[right][:2])
        )
        pair_distances.append(distance)
        pair_rows.append(
            {
                "kind": "between_vowel_primary_P1P2",
                "left": left,
                "right": right,
                "distance_hz": distance,
            }
        )

    regrid_shifts: list[float] = []
    for vowel in ("a", "i", "u"):
        shift = float(
            np.linalg.norm(primary_peaks[vowel][:2] - refined_peaks[vowel][:2])
        )
        regrid_shifts.append(shift)
        pair_rows.append(
            {
                "kind": "within_vowel_primary_vs_refined_P1P2",
                "left": vowel,
                "right": vowel,
                "distance_hz": shift,
            }
        )

    min_between_vowel_distance = min(pair_distances)
    max_regrid_shift = max(regrid_shifts)
    discretization_ratio = min_between_vowel_distance / max(
        max_regrid_shift, 1e-30
    )
    discretization_pass = bool(discretization_ratio > DISCRETIZATION_MARGIN)
    write_csv(output_dir / "discretization_metrics.csv", pair_rows)

    sources, lf_params = EXP13.build_sources()
    lf_oracle_errors = EXP13.verify_oracle(lf_params)
    source_result = sources["lf_fixed"]
    if not np.allclose(
        source_result.planned_f0_hz,
        BASE_F0_HZ,
        rtol=0.0,
        atol=1e-12,
    ):
        raise RuntimeError("lf_fixed source does not preserve fixed 100 Hz F0")
    source_metrics = EXP13.source_metrics(source_result)
    source_cycle_pass = bool(
        source_metrics["cycle_boundary_jump_per_rms"] < SOURCE_CYCLE_JUMP_LIMIT
    )

    pressures: dict[str, np.ndarray] = {}
    signal_rows: list[dict[str, object]] = []
    all_finite = True
    startup_pass = True

    for vowel in ("a", "i", "u"):
        pressure = render_static(source_result.source, primary_geometries[vowel])
        pressures[vowel] = pressure
        finite = bool(np.all(np.isfinite(pressure)))
        all_finite = all_finite and finite
        if not finite:
            raise RuntimeError(f"{vowel}: non-finite pressure")

        raw_peak = float(np.max(np.abs(pressure)))
        raw_rms = rms(pressure)
        steady = steady_rms(pressure)
        startup = EXP12.startup_peak_over_steady_rms(pressure)
        startup_pass = startup_pass and bool(startup < STARTUP_PEAK_LIMIT)

        np.save(output_dir / f"{vowel}_raw_pressure_pa.npy", pressure)
        signal_rows.append(
            {
                "vowel": vowel,
                "raw_peak_pa": raw_peak,
                "raw_rms_pa": raw_rms,
                "steady_rms_pa": steady,
                "startup_peak_over_steady_rms": startup,
                "finite": finite,
            }
        )

    write_csv(output_dir / "signal_metrics.csv", signal_rows)

    level_normalized: dict[str, np.ndarray] = {}
    steady_rms_values: dict[str, float] = {}
    for vowel, pressure in pressures.items():
        value = steady_rms(pressure)
        if not math.isfinite(value) or value <= 0.0:
            raise RuntimeError(f"{vowel}: invalid steady RMS for listening")
        steady_rms_values[vowel] = value
        level_normalized[vowel] = np.asarray(pressure / value, dtype=np.float64)

    max_abs_after_rms_normalization = max(
        float(np.max(np.abs(values))) for values in level_normalized.values()
    )
    if (
        not math.isfinite(max_abs_after_rms_normalization)
        or max_abs_after_rms_normalization <= 0.0
    ):
        raise RuntimeError("invalid RMS-normalized listening waveforms")
    common_safety_gain = 0.90 / max_abs_after_rms_normalization

    listening_waveforms = {
        vowel: np.asarray(values * common_safety_gain, dtype=np.float64)
        for vowel, values in level_normalized.items()
    }
    listening_no_clipping = all(
        float(np.max(np.abs(values))) <= 0.9000001
        for values in listening_waveforms.values()
    )

    listening_rms = {
        vowel: steady_rms(values)
        for vowel, values in listening_waveforms.items()
    }
    listening_rms_spread = max(listening_rms.values()) - min(
        listening_rms.values()
    )
    level_match_pass = bool(
        listening_no_clipping and listening_rms_spread <= 1e-12
    )

    named_dir = output_dir / "listening" / "named_calibration"
    for vowel in ("a", "i", "u"):
        write_wav(named_dir / f"{vowel}.wav", listening_waveforms[vowel])
    make_blind_trials(output_dir, listening_waveforms)

    normalization = {
        "method": (
            "divide each raw pressure waveform by its own 0.05-0.45 s "
            "steady-state RMS, then apply one common safety gain"
        ),
        "steady_state_window_s": [STEADY_START_S, STEADY_END_S],
        "raw_steady_rms_pa": steady_rms_values,
        "common_safety_gain": common_safety_gain,
        "listening_steady_rms_fullscale": listening_rms,
        "listening_rms_spread_fullscale": listening_rms_spread,
        "max_abs_fullscale": {
            vowel: float(np.max(np.abs(values)))
            for vowel, values in listening_waveforms.items()
        },
    }
    (output_dir / "listening_normalization.json").write_text(
        json.dumps(normalization, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    objective_pass = all(
        (
            fixture_valid,
            oracle_pass,
            discretization_pass,
            all_finite,
            source_cycle_pass,
            startup_pass,
            level_match_pass,
        )
    )
    decision = (
        "ACOUSTIC_VOWEL_FIXTURE_VALIDATED_AWAITING_LISTENING"
        if objective_pass
        else "ACOUSTIC_CALIBRATION_FAILED"
    )

    result: dict[str, object] = {
        "decision": decision,
        "objective_gate_pass": objective_pass,
        "fixture_valid": fixture_valid,
        "wolfram_oracle_pass": oracle_pass,
        "wolfram_oracle_tolerance_hz": tolerance_hz,
        "wolfram_oracle_abs_errors_hz": oracle_errors,
        "lf_wolfram_oracle_abs_errors": lf_oracle_errors,
        "discretization_pass": discretization_pass,
        "discretization_margin_required": DISCRETIZATION_MARGIN,
        "min_between_vowel_primary_P1P2_distance_hz": min_between_vowel_distance,
        "max_primary_vs_refined_P1P2_shift_hz": max_regrid_shift,
        "discretization_effect_ratio": discretization_ratio,
        "all_pressure_outputs_finite": all_finite,
        "source_cycle_boundary_jump_per_rms": source_metrics[
            "cycle_boundary_jump_per_rms"
        ],
        "source_cycle_boundary_jump_limit": SOURCE_CYCLE_JUMP_LIMIT,
        "source_cycle_artifact_pass": source_cycle_pass,
        "startup_peak_limit": STARTUP_PEAK_LIMIT,
        "startup_artifact_pass": startup_pass,
        "level_match_pass": level_match_pass,
        "listening_rms_spread_fullscale": listening_rms_spread,
        "listening_no_clipping": listening_no_clipping,
        "primary_human_gate": {
            "trial_count": 30,
            "per_vowel": PRIMARY_TRIALS_PER_VOWEL,
            "choices": ["a", "i", "u", "UNIDENTIFIABLE"],
            "per_vowel_threshold": ">=8/10",
            "overall_threshold": ">=24/30",
            "chance_reference_per_vowel_ge_8_of_10_under_independent_unbiased_3_choice": 0.0034039526494944876,
            "chance_reference_overall_ge_24_of_30_under_independent_unbiased_3_choice": 2.090160589345676e-7,
            "interpretation": (
                "single-listener engineering repeatability only; "
                "not population-level inference"
            ),
        },
        "limitations": [
            "Arai plate model is an educational physical fixture, not a population MRI reference",
            "success does not establish arbitrary Japanese phonology",
            "manual tract fixture is not task-level Gesture realization",
            "current rendered acoustics retain the Experiment-009 experiment-local loss/load/radiation approximation",
            "current LF source is parametric and does not establish self-oscillating vocal-fold dynamics",
            "human vowel identity remains untested until blinded listening is completed",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }

    (output_dir / "decision.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-015-output"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
