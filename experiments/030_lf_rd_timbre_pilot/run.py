"""Experiment 030: one-axis LF Rd intervention through the frozen V3 acoustic path.

Run only in a trusted full Core checkout pinned to the X2a audited stack.
The X2a integration/source files are NOT modified. This is not a TTS API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import wave

import numpy as np

from morphoacoustics.integration import limited_live as live


RD_S0 = 1.0
RD_P1 = 1.4
AUDITED_REF_WAV_SHA_DIAGNOSTIC = "18031e89cc7469ac299fcb7fc5930e8bd7e9b26a37363c5143295ad9304d5220"
WINDOWS_S = {"a_like": (0.12, 0.22), "i_like": (0.32, 0.42)}
BANDS_HZ = ((80, 600), (600, 1500), (1500, 3000), (3000, 6000), (6000, 10000))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_float64(values: np.ndarray) -> str:
    return digest(np.asarray(values, dtype="<f8").tobytes())


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(np.asarray(values, dtype=np.float64)))))


def source_for_rd(exp13: object, rd: float) -> tuple[np.ndarray, dict[str, float]]:
    """Only the Rd-dependent LF pulse shape differs across these two sources."""
    n = live.SAMPLES
    params = exp13.lf_parameters(rd)
    phase, flow = exp13.lf_flow_shape(params)
    f0 = np.full(n, exp13.BASE_F0_HZ, dtype=np.float64)
    cycles = exp13.cycles_from_f0(f0)
    gain = exp13.common_file_envelope(n)
    source = exp13.normalize_peak(np.interp(np.mod(cycles, 1.0), phase, flow) * gain)
    assert source.shape == (n,) and np.isfinite(source).all()
    return source, {
        key: float(getattr(params, key))
        for key in ("rd", "ra", "rk", "rg", "tp", "te", "ta", "alpha", "balance")
    }


def band_powers(values: np.ndarray, start_s: float, end_s: float) -> dict[str, float]:
    """Energy in fixed, nonoverlapping bands of a Hann-windowed 0.10-s segment."""
    start = round(start_s * live.SAMPLE_RATE_HZ)
    stop = round(end_s * live.SAMPLE_RATE_HZ)
    clip = np.asarray(values[start:stop], dtype=np.float64)
    assert len(clip) == 4800
    windowed = clip * np.hanning(len(clip))
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(clip), 1.0 / live.SAMPLE_RATE_HZ)
    powers = np.square(np.abs(fft))
    return {
        f"{low}-{high}": float(np.sum(powers[(freqs >= low) & (freqs < high)]))
        for low, high in BANDS_HZ
    }


def db_ratio(p1: float, s0: float) -> float:
    if s0 <= 0 or p1 <= 0:
        raise RuntimeError("zero spectrum power prevents dB contrast")
    return float(10.0 * math.log10(p1 / s0))


def spectrum_contrast(s0: np.ndarray, p1: np.ndarray) -> dict[str, object]:
    output: dict[str, object] = {}
    for name, (start, end) in WINDOWS_S.items():
        base = band_powers(s0, start, end)
        alternative = band_powers(p1, start, end)
        output[name] = {
            "start_s": start, "end_s": end,
            "s0_band_power": base,
            "p1_band_power": alternative,
            "p1_over_s0_db": {
                key: db_ratio(alternative[key], base[key])
                for key in base
            },
        }
    return output


def pcm_wav(values: np.ndarray) -> tuple[bytes, dict[str, float]]:
    if not np.isfinite(values).all() or np.max(np.abs(values)) > 0.86:
        raise RuntimeError("invalid or excessive audition playback amplitude")
    pcm = np.rint(values * 32767).astype("<i2")
    import io
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(live.SAMPLE_RATE_HZ)
        target.writeframes(pcm.tobytes())
    recon = pcm.astype(np.float64) / 32767.0
    return buffer.getvalue(), {
        "peak_normalized": float(np.max(np.abs(recon))),
        "rms_normalized": rms(recon),
        "rms_dbfs": 20.0 * math.log10(rms(recon)),
    }


def run(output_dir: Path) -> dict[str, object]:
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"refuse to replace experiment evidence: {output_dir}")
    if np.__version__ != "2.4.6":
        raise RuntimeError(f"need audited NumPy 2.4.6; got {np.__version__}")
    exp = live._load_audited_experiment()
    exp13 = exp.EXP26.EXP13
    if (exp13.BASE_F0_HZ != 100.0 or exp13.RD != RD_S0
            or live.SAMPLES != 24000 or live.SAMPLE_RATE_HZ != 48000):
        raise RuntimeError("frozen source/time contract changed")
    reference_source = np.asarray(
        exp13.build_sources()[0][live.SOURCE_ID].source, dtype=np.float64
    )
    s0, s0_params = source_for_rd(exp13, RD_S0)
    p1, p1_params = source_for_rd(exp13, RD_P1)
    if not np.array_equal(reference_source, s0):
        raise RuntimeError("S0 reconstructed source differs from frozen adopted source")
    if np.array_equal(s0, p1):
        raise RuntimeError("Rd intervention produced no distinct source")
    if not math.isclose(float(np.max(s0)), float(np.max(p1)), rel_tol=1e-12):
        raise RuntimeError("source peak-volume-velocity changed")

    start = exp.EXP26.EXP23.primary_geometry("a")
    prepared = exp.prepared_for(
        creature=exp.creature_for(
            cavity_id=start.cavity_id, oral_reachable_end=0.75
        ), geometry=start, condition="M_plus",
    )
    if exp.capability_report(prepared).status != exp.FeasibilityStatus.FEASIBLE:
        raise RuntimeError("prepared morphology not feasible")

    results = {}
    for condition, source in (("s0", s0), ("p1", p1)):
        # Identical label keeps even acoustic geometry IDs identical.
        result = exp.evaluate_condition(prepared, source, label="m_plus")
        if (result.feasibility.status != exp.FeasibilityStatus.FEASIBLE
                or result.acoustic_call_count != 102
                or result.endpoint is None or result.waveform is None):
            raise RuntimeError(f"{condition}: failed physical feasibility")
        pressure = np.asarray(result.waveform, dtype=np.float64)
        if pressure.shape != (live.SAMPLES,) or not np.isfinite(pressure).all():
            raise RuntimeError(f"{condition}: invalid physical pressure")
        results[condition] = (pressure, result.endpoint)

    s0_pressure, s0_endpoint = results["s0"]
    p1_pressure, p1_endpoint = results["p1"]
    if (exp.quantized_waveform_sha256(s0_pressure)
            != exp.AUDITED_QUANTIZED_WAVEFORM_SHA256):
        raise RuntimeError("S0 failed X2a frozen waveform scientific gate")
    if not exp.geometry_physics_equal(s0_endpoint, p1_endpoint):
        raise RuntimeError("phonation experiment changed the articulation endpoint")
    if np.array_equal(s0_pressure, p1_pressure):
        raise RuntimeError("Rd intervention produced no distinct output pressure")

    # Only uniform scalar playback gains, no EQ, pitch shift, compression, etc.
    # Limit each peak to <=0.85, and match *RMS* to <=0.25; RMS != perceived loudness.
    amplitudes = {
        c: {"peak": float(np.max(np.abs(results[c][0]))),
            "rms": rms(results[c][0])} for c in ("s0", "p1")
    }
    target_rms = min(0.25, *(0.85 * v["rms"] / v["peak"] for v in amplitudes.values()))
    audios = {}
    audio_meta = {}
    for condition in ("s0", "p1"):
        values = results[condition][0]
        gain = target_rms / amplitudes[condition]["rms"]
        audio, info = pcm_wav(values * gain)
        audios[condition] = audio
        audio_meta[condition] = {
            **info, "physical_pa_to_playback_gain": gain,
            "raw_rms_pa": amplitudes[condition]["rms"],
            "raw_peak_pa": amplitudes[condition]["peak"],
            "wav_sha256": digest(audio),
        }
    if abs(audio_meta["s0"]["rms_dbfs"] - audio_meta["p1"]["rms_dbfs"]) > 0.005:
        raise RuntimeError("RMS not level matched within 0.005 dB")
    if audios["s0"] == audios["p1"]:
        raise RuntimeError("PCM preview not distinct")

    metrics: dict[str, object] = {
        "experiment": "030-lf-rd-timbre-pilot/v1",
        "status": "scientific-physics-output-valid; perceptual-gate-pending",
        "frozen_source_core_commit": "a75418770ed28cbd301d554171a6b60ee5a05ee9",
        "baseline_reference_quantized_raw_pressure_sha256":
            exp.AUDITED_QUANTIZED_WAVEFORM_SHA256,
        "baseline_reference_listening_wav_sha256_diagnostic":
            digest(live._wav_bytes(s0_pressure)),
        "matches_prior_reference_wav_hash_diagnostic":
            digest(live._wav_bytes(s0_pressure)) == AUDITED_REF_WAV_SHA_DIAGNOSTIC,
        "feasible_transfer_calls_per_condition": 102,
        "identical_prepared_endpoint": True,
        "same_f0_hz": exp13.BASE_F0_HZ,
        "same_f0_cycle_timing": True,
        "same_source_gain_envelope": True,
        "same_source_peak_volume_velocity_m3_s": exp13.SOURCE_PEAK_M3_S,
        "sample_rate_hz": live.SAMPLE_RATE_HZ,
        "sample_count": live.SAMPLES,
        "numpy_version": np.__version__,
        "source_params": {"s0": s0_params, "p1": p1_params},
        "source_float64_sha256": {"s0": sha_float64(s0), "p1": sha_float64(p1)},
        "pressure_float64_sha256": {
            "s0": sha_float64(s0_pressure), "p1": sha_float64(p1_pressure)
        },
        "pressure_quantized_sha256": {
            "s0": exp.quantized_waveform_sha256(s0_pressure),
            "p1": exp.quantized_waveform_sha256(p1_pressure),
        },
        "source_spectral_contrast": spectrum_contrast(s0, p1),
        "pressure_spectral_contrast": spectrum_contrast(s0_pressure, p1_pressure),
        "audition_level_matching": {
            "procedure": "per-condition linear scalar RMS match; no post-EQ",
            "target_rms_pcm_linear": target_rms,
            "not_equivalent_to_perceived_loudness_match": True,
            "conditions": audio_meta,
        },
        "scientific_claim_limit":
            "exploratory 1-body 1-task physical source intervention; listening not yet evaluated",
    }
    output_dir.mkdir(parents=True, exist_ok=False)
    artifact_bytes = {
        "s0_rd1p0.wav": audios["s0"],
        "p1_rd1p4.wav": audios["p1"],
    }
    for filename, values in (
        ("s0_source_m3s.npy", s0),
        ("p1_source_m3s.npy", p1),
        ("s0_raw_pressure_pa.npy", s0_pressure),
        ("p1_raw_pressure_pa.npy", p1_pressure),
    ):
        import io
        buffer = io.BytesIO()
        np.save(buffer, values, allow_pickle=False)
        artifact_bytes[filename] = buffer.getvalue()
    for filename, payload in artifact_bytes.items():
        (output_dir / filename).write_bytes(payload)
    metrics["artifacts_sha256"] = {
        filename: digest(payload) for filename, payload in artifact_bytes.items()
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.output_dir)
    except Exception as exc:
        print(f"EXPERIMENT030_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
    print(json.dumps({
        "status": result["status"],
        "source_deltas": result["source_spectral_contrast"]["a_like"]["p1_over_s0_db"],
        "pressure_deltas_a": result["pressure_spectral_contrast"]["a_like"]["p1_over_s0_db"],
        "pressure_deltas_i": result["pressure_spectral_contrast"]["i_like"]["p1_over_s0_db"],
        "wav_sha256": {
            c: result["audition_level_matching"]["conditions"][c]["wav_sha256"]
            for c in ("s0", "p1")
        },
    }, indent=2))
