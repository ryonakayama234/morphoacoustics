"""VM-0: traceable narrowband diagnostics of *mouth-port* WAV evidence.

This module does not generate, resynthesize, optimize, color or rate voice.
Requires real source/native/monitor/WAV arrays and hash-attested manifest.
Its 100Hz, 50..200ms harmonic window is ONLY the preregistered SV1 CI fixture.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from math import isfinite, log10, sqrt
from pathlib import Path
import wave
import zipfile

import numpy as np

SCHEMA = "voice-metrology/v0"
REFERENCE_ARTIFACT = "wg2-prepared-m0-m1-native-physics"
WINDOW_START_S = 0.05
WINDOW_END_S = 0.20
REFERENCE_F0_HZ = 100
SAMPLE_RATE_HZ = 48000
MAX_HARMONIC = 80
EXPECTED_FILES = (
    "source_flow_48k.npy",
    "mouth_pressure_native_pa.npy",
    "mouth_flow_native_m3_s.npy",
    "mouth_pressure_monitor_48k_pa.npy",
    "audio.wav",
)
MAX_BYTES_PER_FILE = 3_000_000


def f64_digest(x: np.ndarray) -> str:
    return sha256(np.ascontiguousarray(x, dtype="<f8").tobytes()).hexdigest()


def harmonic_signature(
    x: np.ndarray,
    *,
    fs_hz: int = SAMPLE_RATE_HZ,
    f0_hz: int = REFERENCE_F0_HZ,
    start_s: float = WINDOW_START_S,
    end_s: float = WINDOW_END_S,
    max_harmonic: int = MAX_HARMONIC,
) -> dict[str, object]:
    """Exact-integer-period DFT projection of AC energy to known harmonics.

    No F0 estimation and no formant estimator: this test conditions on an
    *externally fixed* 100Hz excitation and exact 15 period 0.15s window.
    """
    if not isinstance(x, np.ndarray) or x.ndim != 1 or not np.isfinite(x).all():
        raise ValueError("INVALID_SIGNAL")
    if type(fs_hz) is not int or type(f0_hz) is not int or fs_hz <= 0 or f0_hz <= 0:
        raise ValueError("INVALID_SAMPLING")
    if type(max_harmonic) is not int or max_harmonic <= 0:
        raise ValueError("INVALID_HARMONICS")
    if max_harmonic * f0_hz >= fs_hz / 2:
        raise ValueError("HARMONICS_REACH_NYQUIST")
    a, b = round(start_s * fs_hz), round(end_s * fs_hz)
    if a < 0 or b <= a or b > len(x):
        raise ValueError("INSUFFICIENT_WINDOW")
    if abs(a - start_s * fs_hz) > 1e-8 or abs(b - end_s * fs_hz) > 1e-8:
        raise ValueError("NONINTEGER_SAMPLE_WINDOW")
    segment = np.asarray(x[a:b], dtype=np.float64)
    count = len(segment)
    cycles = count * f0_hz / fs_hz
    if abs(cycles - round(cycles)) > 1e-10:
        raise ValueError("NONINTEGER_PERIOD_WINDOW")
    harmonic_bins = np.arange(1, max_harmonic + 1, dtype=np.int64) * round(cycles)
    spectrum = np.fft.rfft(segment - float(np.mean(segment)))
    powers = np.square(np.abs(spectrum))
    ac_power = float(np.sum(powers[1:-1])) if count % 2 == 0 else float(np.sum(powers[1:]))
    energy = powers[harmonic_bins]
    total = float(np.sum(energy))
    if total <= 1e-30 or ac_power <= 1e-30:
        return {
            "state": "SILENCE_OR_UNRESOLVED",
            "window_s": [start_s, end_s],
            "harmonics_hz": [f0_hz, max_harmonic * f0_hz],
            "sixth_fraction": None,
            "fundamental_fraction": None,
            "sixth_relative_to_fundamental_db": None,
            "harmonic_family_ac_fraction": None,
            "effective_harmonic_count": None,
        }
    ratios = energy / total
    one = float(energy[0])
    six = float(energy[5]) if max_harmonic >= 6 else 0.0
    rel_db = 10 * log10(six / one) if six > 0 and one > 0 else None
    return {
        "state": "MEASURED",
        "window_s": [start_s, end_s],
        "harmonics_hz": [f0_hz, max_harmonic * f0_hz],
        "sixth_fraction": float(ratios[5]) if max_harmonic >= 6 else None,
        "fundamental_fraction": float(ratios[0]),
        "sixth_relative_to_fundamental_db": rel_db,
        "harmonic_family_ac_fraction": min(1.0, total / ac_power),
        "effective_harmonic_count": 1.0 / float(np.sum(ratios**2)),
        "top_harmonics": [
            {"hz": int((int(i) + 1) * f0_hz), "fraction": float(ratios[i])}
            for i in np.argsort(-ratios)[:10]
        ],
    }


def _limited_read(archive: zipfile.ZipFile, member: str) -> bytes:
    info = archive.getinfo(member)
    if info.is_dir() or info.file_size > MAX_BYTES_PER_FILE or info.file_size <= 0:
        raise ValueError("UNSUPPORTED_EVIDENCE_FILE_SIZE")
    return archive.read(member)


def _verified_array(data: bytes, length: int, name: str) -> np.ndarray:
    try:
        array = np.load(io.BytesIO(data), allow_pickle=False)
    except (OSError, ValueError) as exc:
        raise ValueError("INVALID_NUMPY_TRACE: " + name) from exc
    if (array.dtype != np.dtype("<f8") or array.shape != (length,)
            or not np.isfinite(array).all()):
        raise ValueError("INVALID_NUMPY_TRACE_SHAPE_OR_FINITE: " + name)
    return array


def _pcm_data(wav_bytes: bytes, frames: int) -> np.ndarray:
    with wave.open(io.BytesIO(wav_bytes), "rb") as handle:
        if (handle.getnchannels() != 1 or handle.getsampwidth() != 2
                or handle.getframerate() != SAMPLE_RATE_HZ
                or handle.getcomptype() != "NONE" or handle.getnframes() != frames):
            raise ValueError("INVALID_PCM_WAV_CONTRACT")
        pcm = handle.readframes(frames)
    if len(pcm) != 2 * frames:
        raise ValueError("TRUNCATED_PCM_WAV")
    return np.frombuffer(pcm, dtype="<i2")


def analyze_body(archive: zipfile.ZipFile, body: str) -> dict[str, object]:
    if body not in ("M0", "M1"):
        raise ValueError("UNSUPPORTED_BODY_LABEL")
    header = _limited_read(archive, body + "/manifest.json")
    try:
        manifest = json.loads(header)
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_MANIFEST") from exc
    b = manifest.get("body", {})
    o = manifest.get("observer", {})
    source = manifest.get("source", {})
    if (manifest.get("schema_version") != "wg2-creator-static-a-sustain/v0"
            or manifest.get("status") != "SUCCEEDED"
            or b.get("preset_id") != "v3b-axial-" + body
            or b.get("revision") != 1
            or source.get("id") != "sv1-prescribed-100hz-lf-rd1"
            or o.get("observation_point") != "mouth-port-pressure-not-external-microphone"
            or o.get("sample_rate_hz") != SAMPLE_RATE_HZ
            or o.get("output_samples") not in (12000, 24000)
            or o.get("termination") != "b0"
            or o.get("observation_version") != "wg2-mouth-port-causal-kaiser129/v1"):
        raise ValueError("UNSUPPORTED_FIXTURE_OR_SENSOR")
    sample_count = o["output_samples"]
    native_count = o.get("physics_ticks")
    full_scale = o.get("playback_full_scale_pa")
    clock = o.get("physics_clock_hz")
    if (type(native_count) is not int or native_count < sample_count
            or type(full_scale) not in (int, float) or not isfinite(full_scale)
            or full_scale <= 0 or type(clock) not in (int, float)
            or not isfinite(clock) or not 60000 <= clock <= 75000):
        raise ValueError("INVALID_OBSERVER_UNITS_OR_CLOCK")
    files = {}
    receipts = manifest.get("artifacts", {})
    if set(receipts) != set(EXPECTED_FILES):
        raise ValueError("MISSING_EVIDENCE_ARTIFACT")
    for name in EXPECTED_FILES:
        data = _limited_read(archive, body + "/" + name)
        rec = receipts[name]
        if not isinstance(rec, dict) or rec.get("bytes") != len(data) or rec.get("sha256") != sha256(data).hexdigest():
            raise ValueError("EVIDENCE_HASH_MISMATCH: " + name)
        files[name] = data
    u = _verified_array(files["source_flow_48k.npy"], sample_count, "source")
    native_p = _verified_array(files["mouth_pressure_native_pa.npy"], native_count, "native_p")
    native_u = _verified_array(files["mouth_flow_native_m3_s.npy"], native_count, "native_u")
    monitor = _verified_array(files["mouth_pressure_monitor_48k_pa.npy"], sample_count, "monitor")
    wav_pcm = _pcm_data(files["audio.wav"], sample_count)
    if (f64_digest(u) != source.get("sha256_f64")
            or f64_digest(u) != o.get("source_flow_sha256")
            or f64_digest(native_p) != o.get("physical_pressure_sha256")
            or f64_digest(monitor) != o.get("monitor_pressure_sha256")
            or sha256(files["audio.wav"]).hexdigest() != o.get("wav_sha256")):
        raise ValueError("RAW_OBSERVER_SOURCE_CROSS_HASH_MISMATCH")
    if np.max(np.abs(monitor)) > full_scale:
        raise ValueError("MONITOR_WOULD_CLIP")
    expected_pcm = np.rint(monitor / full_scale * 32767).astype("<i2")
    if not np.array_equal(wav_pcm, expected_pcm):
        raise ValueError("PCM_DOES_NOT_MATCH_PHYSICAL_MONITOR")
    reconstructed_pa = wav_pcm.astype(np.float64) * full_scale / 32767.0
    src_sig = harmonic_signature(u)
    out_sig = harmonic_signature(monitor)
    a = src_sig["sixth_relative_to_fundamental_db"]
    bdb = out_sig["sixth_relative_to_fundamental_db"]
    return {
        "body_preset_id": b["preset_id"], "body_revision": b["revision"],
        "prepared_digest": b.get("preparation_digest"),
        "sample_rate_hz": SAMPLE_RATE_HZ, "physics_clock_hz": float(clock),
        "observation_point": o["observation_point"],
        "source_id": source["id"], "source_sha256": source["sha256_f64"],
        "native_pressure_sha256": o["physical_pressure_sha256"],
        "monitor_sha256": o["monitor_pressure_sha256"],
        "wav_sha256": o["wav_sha256"],
        "source_harmonics": src_sig, "mouth_monitor_harmonics": out_sig,
        "sixth_vs_fundamental_selectivity_change_db": (
            float(bdb) - float(a) if a is not None and bdb is not None else None
        ),
        "wav_quantization_rmse_pa": sqrt(float(np.mean((monitor - reconstructed_pa)**2))),
        "wav_pcm_peak_abs": int(np.max(np.abs(wav_pcm.astype(np.int32)))),
        "native_pressure_rms_pa": sqrt(float(np.mean(native_p**2))),
        "native_mouth_flow_rms_m3_s": sqrt(float(np.mean(native_u**2))),
        "observer_max_abs_energy_residual_j": o.get("max_abs_energy_residual_j"),
        "measurement_validity": "VALID_BYTES_AND_NAMED_PORTS",
        "acoustic_reference_validity": "NOT_TESTED",
        "voice_candidacy": "HOLD_NO_REFERENCE",
        "creator_acceptance": "NOT_ASKED_FOR_THIS_FIXTURE",
        "far_field_receiver": "NOT_MODELED",
    }


def analyze_zip(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        bodies = {name: analyze_body(archive, name) for name in ("M0", "M1")}
    sources_equal = bodies["M0"]["source_sha256"] == bodies["M1"]["source_sha256"]
    return {
        "schema_version": SCHEMA,
        "method": "fixed-15-cycle-100hz-dft-50to200ms-mouth-port",
        "reference_artifact": REFERENCE_ARTIFACT,
        "quality_conclusion": "NONE_DIAGNOSTIC_ONLY",
        "comparator_type": "ANATOMY_SENSITIVITY_NOT_OLD_NEW_VOICE",
        "same_source_both_bodies": sources_equal,
        "native_receiver": "MOUTH_PORT_NOT_FAR_FIELD",
        "bodies": bodies,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", type=Path, required=True, dest="archive")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    record = analyze_zip(args.archive)
    output = json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output_json:
        args.output_json.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
