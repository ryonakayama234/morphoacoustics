from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import time
import wave
from pathlib import Path

import numpy as np

from morphoacoustics.physical import Tract1DGeometry, TubeSection

SAMPLE_RATE_HZ = 48_000
DURATION_S = 0.5
F0_HZ = 100.0
SOURCE_PEAK_VOLUME_VELOCITY_M3_S = 1.0e-5
SOURCE_HARMONICS = 40
SOURCE_RAMP_S = 0.01
SOUND_SPEED_M_S = 343.0
AIR_DENSITY_KG_M3 = 1.21
ATTENUATION_NP_M = 0.4
LOAD_FRACTION_OF_OUTLET_ZC = 0.05
OBSERVATION_DISTANCE_M = 0.20
PEAK_SCAN_START_HZ = 100.0
PEAK_SCAN_END_HZ = 5_000.0
PEAK_SCAN_STEP_HZ = 0.25
WOLFRAM_UNIFORM_REFERENCE_HZ = np.array(
    [504.5, 1513.25, 2522.0, 3531.0, 4539.75], dtype=np.float64
)
WOLFRAM_TOLERANCE_HZ = 0.5


def uniform_geometry() -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=0.017, area_m2=3.0e-4)
            for _ in range(10)
        ),
    )


def constricted_geometry() -> Tract1DGeometry:
    sections = [TubeSection(length_m=0.017, area_m2=3.0e-4) for _ in range(10)]
    sections[5] = TubeSection(length_m=0.017, area_m2=8.0e-5)
    return Tract1DGeometry(cavity_id="oral", sections=tuple(sections))


def source_volume_velocity() -> tuple[np.ndarray, np.ndarray]:
    sample_count = int(round(SAMPLE_RATE_HZ * DURATION_S))
    time_s = np.arange(sample_count, dtype=np.float64) / SAMPLE_RATE_HZ
    source = np.zeros(sample_count, dtype=np.float64)

    for harmonic in range(1, SOURCE_HARMONICS + 1):
        frequency_hz = harmonic * F0_HZ
        if frequency_hz >= SAMPLE_RATE_HZ / 2:
            break
        source += math.pow(harmonic, -1.2) * np.sin(2.0 * np.pi * frequency_hz * time_s)

    peak = float(np.max(np.abs(source)))
    if not math.isfinite(peak) or peak <= 0.0:
        raise RuntimeError("source generator produced an invalid signal")
    source *= SOURCE_PEAK_VOLUME_VELOCITY_M3_S / peak

    ramp_samples = int(round(SOURCE_RAMP_S * SAMPLE_RATE_HZ))
    if ramp_samples > 0:
        phase = np.linspace(0.0, np.pi / 2.0, ramp_samples, endpoint=False)
        ramp = np.sin(phase) ** 2
        source[:ramp_samples] *= ramp
        source[-ramp_samples:] *= ramp[::-1]

    return time_s, source


def lossy_transfer_matrix(
    geometry: Tract1DGeometry,
    frequencies_hz: np.ndarray,
) -> np.ndarray:
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    total = np.broadcast_to(
        np.eye(2, dtype=np.complex128),
        frequencies.shape + (2, 2),
    ).copy()

    complex_wavenumber = (
        2.0 * np.pi * frequencies / SOUND_SPEED_M_S
        - 1j * ATTENUATION_NP_M
    )

    for section in geometry.sections:
        phase = complex_wavenumber * section.length_m
        zc = AIR_DENSITY_KG_M3 * SOUND_SPEED_M_S / section.area_m2
        section_matrix = np.empty(frequencies.shape + (2, 2), dtype=np.complex128)
        section_matrix[..., 0, 0] = np.cos(phase)
        section_matrix[..., 0, 1] = 1j * zc * np.sin(phase)
        section_matrix[..., 1, 0] = 1j * np.sin(phase) / zc
        section_matrix[..., 1, 1] = np.cos(phase)
        total = np.matmul(total, section_matrix)

    return total


def outlet_volume_velocity_transfer(
    geometry: Tract1DGeometry,
    frequencies_hz: np.ndarray,
) -> np.ndarray:
    """Return U_out / U_in for the explicitly loaded segmented tube.

    With [p_in, U_in]^T = T [p_out, U_out]^T and p_out = Z_L U_out,
    U_out / U_in = 1 / (C Z_L + D).  This is intentionally not the input
    impedance and is the source-to-output transfer used by this experiment.
    """

    matrix = lossy_transfer_matrix(geometry, frequencies_hz)
    c = matrix[..., 1, 0]
    d = matrix[..., 1, 1]
    outlet_area_m2 = geometry.sections[-1].area_m2
    outlet_zc = AIR_DENSITY_KG_M3 * SOUND_SPEED_M_S / outlet_area_m2
    load = LOAD_FRACTION_OF_OUTLET_ZC * outlet_zc
    denominator = c * load + d
    with np.errstate(divide="ignore", invalid="ignore"):
        transfer = 1.0 / denominator
    return np.asarray(transfer, dtype=np.complex128)


def far_field_pressure_transfer(
    geometry: Tract1DGeometry,
    frequencies_hz: np.ndarray,
) -> np.ndarray:
    """Return observer pressure / inlet volume velocity in Pa / (m^3/s).

    The terminal load is a small explicit resistive surrogate used to keep the
    experiment finite.  Radiation to the observer is separately approximated
    as a free-field monopole driven by U_out.  This is an experiment-local
    approximation, not a realistic lip-radiation model and not a core API.
    """

    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    omega = 2.0 * np.pi * frequencies
    u_transfer = outlet_volume_velocity_transfer(geometry, frequencies)
    propagation = np.exp(
        -1j * omega * OBSERVATION_DISTANCE_M / SOUND_SPEED_M_S
    )
    radiation = (
        1j
        * omega
        * AIR_DENSITY_KG_M3
        / (4.0 * np.pi * OBSERVATION_DISTANCE_M)
        * propagation
    )
    radiation = np.asarray(radiation, dtype=np.complex128)
    radiation[frequencies == 0.0] = 0.0
    return radiation * u_transfer


def synthesize_pressure(
    geometry: Tract1DGeometry,
    source_m3_s: np.ndarray,
) -> np.ndarray:
    frequencies_hz = np.fft.rfftfreq(source_m3_s.size, d=1.0 / SAMPLE_RATE_HZ)
    source_spectrum = np.fft.rfft(source_m3_s)
    transfer = far_field_pressure_transfer(geometry, frequencies_hz)
    pressure_spectrum = source_spectrum * transfer
    pressure_pa = np.fft.irfft(pressure_spectrum, n=source_m3_s.size)
    return np.asarray(pressure_pa, dtype=np.float64)


def response_peaks(geometry: Tract1DGeometry, count: int = 5) -> list[tuple[float, float]]:
    frequencies = np.arange(
        PEAK_SCAN_START_HZ,
        PEAK_SCAN_END_HZ + PEAK_SCAN_STEP_HZ / 2.0,
        PEAK_SCAN_STEP_HZ,
        dtype=np.float64,
    )
    magnitude = np.abs(outlet_volume_velocity_transfer(geometry, frequencies))
    local = np.flatnonzero(
        (magnitude[1:-1] > magnitude[:-2])
        & (magnitude[1:-1] >= magnitude[2:])
    ) + 1
    return [
        (float(frequencies[index]), float(magnitude[index]))
        for index in local[:count]
    ]


def write_listening_wav(path: Path, pressure_pa: np.ndarray) -> float:
    raw_peak = float(np.max(np.abs(pressure_pa)))
    if not math.isfinite(raw_peak) or raw_peak <= 0.0:
        raise RuntimeError("cannot normalize an invalid or silent pressure waveform")
    gain = 0.90 / raw_peak
    listening = np.clip(pressure_pa * gain, -1.0, 1.0)
    pcm = np.round(listening * 32767.0).astype("<i2")

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE_HZ)
        wav.writeframes(pcm.tobytes())
    return gain


def write_raw_csv(path: Path, time_s: np.ndarray, pressure_pa: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", "pressure_pa"])
        writer.writerows(zip(time_s, pressure_pa, strict=True))


def geometry_payload(geometry: Tract1DGeometry) -> list[dict[str, float]]:
    return [
        {"length_m": section.length_m, "area_m2": section.area_m2}
        for section in geometry.sections
    ]


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    time_s, source = source_volume_velocity()
    bodies = {
        "uniform": uniform_geometry(),
        "constricted": constricted_geometry(),
    }

    summary_rows: list[dict[str, object]] = []
    peak_rows: list[dict[str, object]] = []
    body_peaks: dict[str, list[tuple[float, float]]] = {}

    for body_name, geometry in bodies.items():
        pressure = synthesize_pressure(geometry, source)
        if np.any(~np.isfinite(pressure)):
            raise RuntimeError(f"{body_name}: non-finite pressure samples")

        raw_peak_pa = float(np.max(np.abs(pressure)))
        raw_rms_pa = float(np.sqrt(np.mean(pressure * pressure)))
        listening_gain = write_listening_wav(
            output_dir / f"{body_name}_listen.wav",
            pressure,
        )
        write_raw_csv(output_dir / f"{body_name}_raw_pressure.csv", time_s, pressure)
        np.save(output_dir / f"{body_name}_raw_pressure_pa.npy", pressure)

        peaks = response_peaks(geometry)
        body_peaks[body_name] = peaks
        for rank, (frequency_hz, magnitude) in enumerate(peaks, start=1):
            peak_rows.append(
                {
                    "body": body_name,
                    "rank": rank,
                    "frequency_hz": frequency_hz,
                    "uout_per_uin_magnitude": magnitude,
                }
            )

        summary_rows.append(
            {
                "body": body_name,
                "raw_peak_pa": raw_peak_pa,
                "raw_rms_pa": raw_rms_pa,
                "listening_gain_fullscale_per_pa": listening_gain,
                "sample_count": pressure.size,
                "finite": True,
            }
        )

    uniform_peak_hz = np.array(
        [frequency for frequency, _ in body_peaks["uniform"]], dtype=np.float64
    )
    if uniform_peak_hz.shape != WOLFRAM_UNIFORM_REFERENCE_HZ.shape:
        raise RuntimeError("uniform response did not expose five expected local maxima")
    wolfram_errors_hz = np.abs(uniform_peak_hz - WOLFRAM_UNIFORM_REFERENCE_HZ)
    wolfram_pass = bool(np.all(wolfram_errors_hz <= WOLFRAM_TOLERANCE_HZ))

    uniform_normalized = uniform_peak_hz / uniform_peak_hz[0]
    constricted_peak_hz = np.array(
        [frequency for frequency, _ in body_peaks["constricted"]], dtype=np.float64
    )
    body_difference_hz = float(
        np.max(np.abs(uniform_peak_hz[: min(len(uniform_peak_hz), len(constricted_peak_hz))]
                      - constricted_peak_hz[: min(len(uniform_peak_hz), len(constricted_peak_hz))]))
    )
    not_level_only = body_difference_hz >= 10.0

    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)

    with (output_dir / "spectral_peaks.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(peak_rows[0]))
        writer.writeheader()
        writer.writerows(peak_rows)

    metadata = {
        "model": "experiment-local lossy segmented 1D tube",
        "fourier_convention": "exp(+j omega t)",
        "source": {
            "kind": "deterministic harmonic volume-velocity source",
            "f0_hz": F0_HZ,
            "harmonics": SOURCE_HARMONICS,
            "peak_volume_velocity_m3_s": SOURCE_PEAK_VOLUME_VELOCITY_M3_S,
            "ramp_s": SOURCE_RAMP_S,
        },
        "tube": {
            "sound_speed_m_s": SOUND_SPEED_M_S,
            "air_density_kg_m3": AIR_DENSITY_KG_M3,
            "attenuation_np_m": ATTENUATION_NP_M,
            "load_fraction_of_outlet_characteristic_impedance": LOAD_FRACTION_OF_OUTLET_ZC,
            "load_note": "small real terminal load surrogate; not realistic lip radiation",
        },
        "observer": {
            "kind": "free-field monopole proxy driven by outlet volume velocity",
            "distance_m": OBSERVATION_DISTANCE_M,
            "note": "observer radiation is not coupled back into the terminal load",
        },
        "render": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "duration_s": DURATION_S,
            "raw_unit": "Pa",
            "listening_wav": "per-file peak normalization to 0.90 full scale; not physical amplitude",
        },
        "prepared_body_provenance": {
            "kind": "manual fixed geometry for experiment",
            "uniform": geometry_payload(bodies["uniform"]),
            "constricted": geometry_payload(bodies["constricted"]),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    decision = {
        "wolfram_uniform_reference_hz": WOLFRAM_UNIFORM_REFERENCE_HZ.tolist(),
        "python_uniform_peaks_hz": uniform_peak_hz.tolist(),
        "wolfram_abs_errors_hz": wolfram_errors_hz.tolist(),
        "wolfram_tolerance_hz": WOLFRAM_TOLERANCE_HZ,
        "wolfram_reference_pass": wolfram_pass,
        "body_peak_difference_max_hz": body_difference_hz,
        "body_difference_not_level_only": not_level_only,
        "all_outputs_finite": all(bool(row["finite"]) for row in summary_rows),
        "unused_uniform_peak_ratios": uniform_normalized.tolist(),
        "decision": "SUPPORTED" if wolfram_pass and not_level_only else "MORE_DATA",
        "limitations": [
            "manual fixed geometries; not anatomically derived",
            "experiment-local constant attenuation",
            "small resistive terminal load surrogate",
            "free-field monopole observer without source-filter back-coupling",
            "periodic explicit source; no self-oscillating vocal-fold model",
        ],
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if not wolfram_pass:
        raise RuntimeError("uniform-tube peaks disagree with independent Wolfram reference")
    if not not_level_only:
        raise RuntimeError("body comparison changed only level within the pre-registered peak criterion")

    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("experiment-009-output"))
    args = parser.parse_args()
    decision = run(args.output_dir)
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
