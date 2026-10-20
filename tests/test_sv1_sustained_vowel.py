"""SV-1 bounded-duration physical and evidence-integrity tests."""
from __future__ import annotations

from hashlib import sha256
import io
import json
import os
from pathlib import Path
import runpy
import wave

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
MOD = runpy.run_path(str(ROOT / "experiments/042_sv1_sustained_vowel/run.py"))
perform = MOD["perform"]

pytestmark = []


def test_refusal_is_explicit_and_does_not_publish_audio(tmp_path: Path) -> None:
    invalid = [
        {"vowel": "i"},
        {"preset_id": "v3b-axial-M1"},
        {"revision": 2},
        {"revision": True},
        {"durations": (0.25, 0.75)},
        {"durations": (0.50, 0.25)},
        {"durations": (float("nan"), 0.50)},
        {"durations": (0.25, float("inf"))},
    ]
    for i, kwargs in enumerate(invalid):
        dest = tmp_path / f"reject_{i}"
        with pytest.raises(ValueError, match="UNSUPPORTED"):
            perform(dest, **kwargs)
        assert not dest.exists()
    with pytest.raises(FileNotFoundError):
        perform(tmp_path / "missing_parent" / "new")
    assert not (tmp_path / "missing_parent").exists()


def test_existing_and_symlink_output_never_overwritten(tmp_path: Path) -> None:
    dest = tmp_path / "existing"
    dest.mkdir()
    sentinel = dest / "valuable.txt"
    sentinel.write_text("untouched")
    with pytest.raises(FileExistsError):
        perform(dest)
    assert sentinel.read_text() == "untouched"
    link = tmp_path / "dangling"
    try:
        link.symlink_to(tmp_path / "nonexistent")
    except (NotImplementedError, OSError):
        pytest.skip("symlink not supported")
    with pytest.raises(FileExistsError):
        perform(link)


def test_directory_swap_cannot_overwrite_external_files(tmp_path: Path) -> None:
    """P2 reviewer regression: after opening dirfd, pathname is no longer trust."""
    root = tmp_path / "owned"
    moved = tmp_path / "moved"
    target = tmp_path / "target"
    root.mkdir()
    target.mkdir()
    (target / "sentinel.wav").write_bytes(b"do not alter")
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        root.rename(moved)
        root.symlink_to(target, target_is_directory=True)
        # A later pathname-based Path.write_bytes would follow the target
        # symlink; the fd-anchored writer still writes under moved/.
        MOD["_write_at"](descriptor, "sentinel.wav", b"new-bundle-bytes")
        MOD["_write_at"](descriptor, "listening/blind/trial_01.wav", b"audio")
        assert (moved / "sentinel.wav").read_bytes() == b"new-bundle-bytes"
        assert (target / "sentinel.wav").read_bytes() == b"do not alter"
        assert not (target / "listening").exists()
        with pytest.raises(FileExistsError):
            MOD["_write_at"](descriptor, "sentinel.wav", b"overwrite")
        (moved / "poison").symlink_to(target, target_is_directory=True)
        with pytest.raises(OSError):
            MOD["_write_at"](descriptor, "poison/evil.wav", b"evil")
        assert not (target / "evil.wav").exists()
    finally:
        os.close(descriptor)


@pytest.mark.skipif(
    os.environ.get("SV1_REAL_PHYSICS") != "1",
    reason="Requires adopted CC-A2 transitive source gate and NumPy==2.4.6",
)
def test_real_physics_duration_body_oracle_and_listening_trials(tmp_path: Path) -> None:
    dest = tmp_path / "evidence"
    report = perform(dest)
    assert report["status"] == "NUMERIC_GATE_PASS_CANDIDATE_NOT_ADOPTED"
    assert report["body"]["preset_id"] == "v3b-axial-M0"
    assert report["body"]["preparation_digest"].startswith("sha256:")
    assert report["body"]["static_a_rest_peak_hz"] == [720.25, 1288.5]
    assert report["listening_gate"] == "NOT_RUN_CREATOR_LISTENING_PENDING"
    assert report["independent_review"] == "PENDING"
    assert report["stimuli"]["A"]["frames"] == 12_000
    assert report["stimuli"]["B"]["frames"] == 24_000
    assert report["C"]["is_accepted_physical_take"] is False
    for letter, count in (("A", 12_000), ("B", 24_000)):
        wav = dest / f"{letter}_listen.wav"
        with wave.open(str(wav), "rb") as f:
            assert f.getnchannels() == 1
            assert f.getsampwidth() == 2
            assert f.getframerate() == 48_000
            assert f.getnframes() == count
        source = np.load(dest / f"{letter}_source_flow.npy", allow_pickle=False)
        pressure = np.load(dest / f"{letter}_raw_pressure_pa.npy", allow_pickle=False)
        assert source.shape == pressure.shape == (count,)
        assert np.isfinite(source).all() and np.isfinite(pressure).all()
        assert not np.array_equal(source, pressure)
        assert np.std(pressure) > 0
        assert report["stimuli"][letter]["nominal_source_cycles"] == count // 480
        assert report["stimuli"][letter]["source_sha256_f64"] == sha256(
            source.astype("<f8").tobytes()
        ).hexdigest()
        assert report["stimuli"][letter]["pressure_sha256_f64"] == sha256(
            pressure.astype("<f8").tobytes()
        ).hexdigest()
        # No phonetically repeated onset: every 20ms center window has energy.
        for start in range(2400, count - 2400, 960):
            assert np.sqrt(np.mean(source[start : start + 960] ** 2)) > 0
    a = np.load(dest / "A_source_flow.npy", allow_pickle=False)
    b = np.load(dest / "B_source_flow.npy", allow_pickle=False)
    assert np.array_equal(a[2400:7200], b[2400:7200])
    with wave.open(str(dest / "A_listen.wav"), "rb") as f:
        original = f.readframes(f.getnframes())
    # The C second component must exist as a separately rendered PHYSICAL
    # 0.25s source / raw-pressure pair, not just a duplicated A byte buffer.
    second_source = np.load(dest / "C_second_source_flow.npy", allow_pickle=False)
    second_pressure = np.load(dest / "C_second_raw_pressure_pa.npy", allow_pickle=False)
    assert second_source.shape == second_pressure.shape == (12_000,)
    assert np.array_equal(second_source, a)
    assert np.array_equal(second_pressure, np.load(
        dest / "A_raw_pressure_pa.npy", allow_pickle=False))
    assert report["C"]["separate_acoustic_run_count"] == 2
    assert report["C"]["component_first_pressure_sha256_f64"] == (
        report["C"]["component_second_pressure_sha256_f64"]
    )
    with wave.open(str(dest / "C_second_listen.wav"), "rb") as f:
        assert f.getnframes() == 12_000
        second = f.readframes(f.getnframes())
    with wave.open(str(dest / "C_concat_DIAGNOSTIC.wav"), "rb") as f:
        assert f.getnframes() == 24_000
        assert f.readframes(f.getnframes()) == original + second
    assert (dest / "listening/blind/trial_01.wav").read_bytes() == (
        dest / "B_listen.wav").read_bytes()
    assert (dest / "listening/blind/trial_03.wav").read_bytes() == (
        dest / "A_listen.wav").read_bytes()
    assert sorted(p.name for p in (dest / "listening/blind").iterdir()) == [
        "trial_01.wav", "trial_02.wav", "trial_03.wav"
    ]
    for file, expected_sha in report["artifact_sha256"].items():
        assert sha256((dest / file).read_bytes()).hexdigest() == expected_sha
    assert json.loads((dest / "manifest.json").read_text("utf-8")) == report


@pytest.mark.skipif(
    os.environ.get("SV1_REAL_PHYSICS") != "1",
    reason="Requires adopted CC-A2 transitive source gate and NumPy==2.4.6",
)
def test_reexecution_has_identical_bytes_and_no_overwrite(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    a = perform(first)
    b = perform(second)
    assert a == b
    for name in a["artifact_sha256"]:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    assert (first / "manifest.json").read_bytes() == (
        second / "manifest.json").read_bytes()
    with pytest.raises(FileExistsError):
        perform(first)
    assert json.loads((first / "manifest.json").read_text()) == a
