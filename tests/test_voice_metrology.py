"""VM-0 falsification tests: pure tones, silence, integrity, and exact PCM.

Tests are measurement controls. They are not a speech-quality pass threshold.
"""
from __future__ import annotations

from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import io
import json
from pathlib import Path
import wave
import zipfile

import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "voice_metrology.py"
SPEC = spec_from_file_location("vm0_independent", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VM = module_from_spec(SPEC)
SPEC.loader.exec_module(VM)


def synthetic(harmonics: dict[int, float], samples: int = 12000) -> np.ndarray:
    t = np.arange(samples) / 48000.0
    return sum(
        (amp * np.sin(2.0 * np.pi * frequency * t)
         for frequency, amp in harmonics.items()),
        start=np.zeros(samples, dtype=np.float64),
    )


def test_known_harmonic_fraction_calibration() -> None:
    first = VM.harmonic_signature(synthetic({100: 1.0}))
    sixth = VM.harmonic_signature(synthetic({600: 1.0}))
    pair = VM.harmonic_signature(synthetic({100: 2.0, 600: 3.0}))
    assert first["fundamental_fraction"] == pytest.approx(1.0, abs=1e-12)
    assert first["sixth_fraction"] == pytest.approx(0.0, abs=1e-12)
    assert sixth["sixth_fraction"] == pytest.approx(1.0, abs=1e-12)
    assert sixth["fundamental_fraction"] == pytest.approx(0.0, abs=1e-12)
    assert pair["sixth_fraction"] == pytest.approx(9.0 / 13.0, abs=1e-11)
    assert pair["fundamental_fraction"] == pytest.approx(4.0 / 13.0, abs=1e-11)
    assert pair["sixth_relative_to_fundamental_db"] == pytest.approx(
        20 * np.log10(3 / 2), abs=1e-11
    )
    assert pair["harmonic_family_ac_fraction"] == pytest.approx(1.0, abs=1e-10)


def test_silence_never_receives_voice_or_false_numeric_fractions() -> None:
    zero = VM.harmonic_signature(np.zeros(12000))
    assert zero["state"] == "SILENCE_OR_UNRESOLVED"
    assert zero["sixth_fraction"] is None
    assert zero["sixth_relative_to_fundamental_db"] is None


def test_wrong_sampling_and_window_are_not_silent_success() -> None:
    x = synthetic({100: 1.0})
    for kwargs in ({"f0_hz": 101}, {"max_harmonic": 300},
                   {"end_s": 0.251}, {"start_s": 0.05001}):
        with pytest.raises(ValueError):
            VM.harmonic_signature(x, **kwargs)
    with pytest.raises(ValueError):
        VM.harmonic_signature(np.array([1.0, float("nan")]))


def _npy(x: np.ndarray) -> bytes:
    out = io.BytesIO()
    np.save(out, np.asarray(x, dtype="<f8"), allow_pickle=False)
    return out.getvalue()


def _wav(monitor: np.ndarray, scale: float = 8.0) -> bytes:
    pcm = np.rint(monitor / scale * 32767.0).astype("<i2")
    out = io.BytesIO()
    with wave.open(out, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(48000)
        handle.writeframes(pcm.tobytes())
    return out.getvalue()


def make_zip(path: Path, *, corrupt_pcm: bool = False, scale: float = 8.0,
             wrong_m0_clock: bool = False, mismatch_sources: bool = False) -> None:
    source = synthetic({100: 1e-6, 600: 1e-8})
    with zipfile.ZipFile(path, "w") as archive:
        for label, clock, length in [("M0", 68600., 0.16), ("M1", 343 * 2 / 0.011, 0.176)]:
            native_count = int(np.ceil(len(source) * clock / 48000))
            mon = synthetic({100: 0.1, 600: 0.02}) if label == "M0" else synthetic({100: 0.01, 600: 0.2})
            audio = _wav(mon, scale)
            if corrupt_pcm and label == "M1":
                patched = bytearray(audio)
                patched[-1] ^= 1
                audio = bytes(patched)
            body_source = source * 2.0 if mismatch_sources and label == "M1" else source
            blobs = {
                "source_flow_48k.npy": _npy(body_source),
                "mouth_pressure_native_pa.npy": _npy(np.zeros(native_count)),
                "mouth_flow_native_m3_s.npy": _npy(np.zeros(native_count)),
                "mouth_pressure_monitor_48k_pa.npy": _npy(mon),
                "audio.wav": audio,
            }
            manifest = {
                "schema_version": "wg2-creator-static-a-sustain/v0",
                "status": "SUCCEEDED",
                "body": {"preset_id": "v3b-axial-" + label, "revision": 1,
                         "preparation_digest": "sha256:" + "f" * 64,
                         "length_m": length},
                "source": {"id": "sv1-prescribed-100hz-lf-rd1",
                           "sha256_f64": VM.f64_digest(body_source)},
                "observer": {"observation_point": "mouth-port-pressure-not-external-microphone",
                             "observation_version": "wg2-mouth-port-causal-kaiser129/v1",
                             "sample_rate_hz": 48000,
                             "output_samples": len(source),
                             "termination": "b0",
                             "physics_clock_hz": (60000 if wrong_m0_clock and label == "M0" else clock),
                             "physics_ticks": native_count,
                             "playback_full_scale_pa": scale,
                             "source_flow_sha256": VM.f64_digest(body_source),
                             "physical_pressure_sha256": VM.f64_digest(np.zeros(native_count)),
                             "monitor_pressure_sha256": VM.f64_digest(mon),
                             "wav_sha256": sha256(audio).hexdigest(),
                             "max_abs_energy_residual_j": 0.0},
                "artifacts": {name: {"bytes": len(blob), "sha256": sha256(blob).hexdigest()}
                              for name, blob in blobs.items()},
            }
            for name, blob in blobs.items():
                archive.writestr(label + "/" + name, blob)
            archive.writestr(label + "/manifest.json", json.dumps(manifest).encode())


def test_end_to_end_bundle_and_binary_receipts(tmp_path: Path) -> None:
    filepath = tmp_path / "evidence.zip"
    make_zip(filepath)
    report = VM.analyze_zip(filepath, historical_fixture=False)
    assert report["quality_conclusion"] == "NONE_DIAGNOSTIC_ONLY"
    assert report["same_source_both_bodies"] is True
    for label in ("M0", "M1"):
        body = report["bodies"][label]
        assert body["measurement_validity"] == "VALID_BYTES_AND_NAMED_PORTS"
        assert body["voice_candidacy"] == "HOLD_NO_REFERENCE"
        assert body["far_field_receiver"] == "NOT_MODELED"
        assert body["wav_quantization_rmse_pa"] <= 8 / 32767 / 2 + 1e-15
    assert report["bodies"]["M0"]["mouth_monitor_harmonics"]["sixth_fraction"] < 0.1
    assert report["bodies"]["M1"]["mouth_monitor_harmonics"]["sixth_fraction"] > 0.99


def test_inconsistent_wav_bytes_are_not_accepted(tmp_path: Path) -> None:
    filepath = tmp_path / "forged.zip"
    make_zip(filepath, corrupt_pcm=True)
    with pytest.raises(ValueError, match="PCM_DOES_NOT_MATCH"):
        VM.analyze_zip(filepath, historical_fixture=False)


def test_zip_artifact_receipt_tampering_is_rejected(tmp_path: Path) -> None:
    filepath = tmp_path / "tampered.zip"
    make_zip(filepath)
    with zipfile.ZipFile(filepath, "r") as old:
        contents = {name: old.read(name) for name in old.namelist()}
    altered = bytearray(contents["M0/source_flow_48k.npy"])
    altered[-1] ^= 1
    contents["M0/source_flow_48k.npy"] = bytes(altered)
    with zipfile.ZipFile(filepath, "w") as new:
        for key, val in contents.items():
            new.writestr(key, val)
    with pytest.raises(ValueError, match="EVIDENCE_HASH_MISMATCH"):
        VM.analyze_zip(filepath)


def test_nyquist_is_not_mislabeled_as_harmonic_coverage() -> None:
    n = np.arange(12000)
    mixed = synthetic({100: 1.0}) + (-1.0) ** n
    record = VM.harmonic_signature(mixed)
    assert record["harmonic_family_ac_fraction"] == pytest.approx(1.0/3.0, abs=1e-9)
    assert record["fundamental_fraction"] == pytest.approx(1.0, abs=1e-11)


def test_wrong_fullscale_or_body_clock_is_rejected_even_with_valid_hashes(tmp_path: Path) -> None:
    for options in ({"scale": 16.0}, {"wrong_m0_clock": True}):
        file = tmp_path / ("fixture_" + list(options)[0] + ".zip")
        make_zip(file, **options)
        with pytest.raises(ValueError, match="INVALID_OBSERVER"):
            VM.analyze_zip(file, historical_fixture=False)


def test_different_source_is_explicitly_incomparable(tmp_path: Path) -> None:
    file = tmp_path / "noncomparable.zip"
    make_zip(file, mismatch_sources=True)
    report = VM.analyze_zip(file, historical_fixture=False)
    assert report["same_source_both_bodies"] is False
    assert report["comparator_type"] == "INCOMPARABLE_DIFFERENT_SOURCE"


def test_historical_pinned_source_cannot_be_replaced_by_coherent_synthetic_fixture(
    tmp_path: Path,
) -> None:
    file = tmp_path / "forged_historical.zip"
    make_zip(file)
    with pytest.raises(ValueError, match="HISTORICAL_FIXTURE_IDENTITY_MISMATCH"):
        VM.analyze_zip(file)
