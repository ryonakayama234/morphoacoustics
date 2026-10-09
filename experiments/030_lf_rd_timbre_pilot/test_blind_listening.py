"""Non-physics tests for the condition-masked listening package."""
from __future__ import annotations

import json
from pathlib import Path
import struct
import tempfile
import unittest
import wave

from blind_listening import build_packet, inspect_wav, sha256


def wav_bytes(values: list[int], path: Path) -> bytes:
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(48000)
        writer.writeframes(struct.pack("<" + str(len(values)) + "h", *values))
    return path.read_bytes()


def fixture(folder: Path, *, mismatch: bool = False) -> Path:
    source = folder / "evidence"
    source.mkdir()
    waveforms = {
        "s0": [1000, -1000] * 12000,
        "p1": [-1000, 1000] * 12000 if not mismatch else [1200, -1200] * 12000,
    }
    info = {}
    hashes = {}
    for condition, name in (("s0", "s0_rd1p0.wav"), ("p1", "p1_rd1p4.wav")):
        values = wav_bytes(waveforms[condition], source / name)
        _, rms = inspect_wav(source / name)
        hashes[name] = sha256(values)
        info[condition] = {"wav_sha256": sha256(values), "rms_dbfs": rms}
    metrics = {
        "experiment": "030-lf-rd-timbre-pilot/v1",
        "status": "scientific-physics-output-valid; perceptual-gate-pending",
        "artifacts_sha256": hashes,
        "audition_level_matching": {
            "procedure": "per-condition linear scalar RMS match; no post-EQ",
            "conditions": info,
        },
    }
    (source / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    return source


class BlindPacketTests(unittest.TestCase):
    def test_both_orders_keep_pcm_unchanged_and_seal_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = fixture(root)
            assignments = []
            for seed in (0, 1):
                packet = root / f"packet{seed}"
                key = root / f"key{seed}"
                public = build_packet(evidence, packet, key, seed=seed)
                private = json.loads((key / "answer_key.json").read_text())
                self.assertEqual(public["trial_id"], private["trial_id"])
                self.assertEqual(set(private["mapping"].values()), {"s0", "p1"})
                assignments.append(private["mapping"]["A"])
                self.assertEqual(public["schema"], "morpho-blind-ab/v1")
                self.assertNotIn("rd1p", (packet / "trial.json").read_text())
                self.assertNotIn("source_params", (packet / "trial.json").read_text())
                self.assertEqual(len(public["stimuli"]), 2)
                for slot, condition in private["mapping"].items():
                    a = (packet / f"{slot}.wav").read_bytes()
                    original = (evidence / {
                        "s0": "s0_rd1p0.wav", "p1": "p1_rd1p4.wav"
                    }[condition]).read_bytes()
                    self.assertEqual(a, original)
                    self.assertEqual(public["stimuli"][0 if slot == "A" else 1]["sha256"],
                                     sha256(original))
                self.assertFalse((packet / "answer_key.json").exists())
                self.assertTrue((packet / "LISTEN_FIRST.txt").exists())
            self.assertNotEqual(assignments[0], assignments[1])

    def test_tampering_is_detected_before_any_packet_is_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = fixture(root)
            wav = evidence / "p1_rd1p4.wav"
            wav.write_bytes(wav.read_bytes() + b"tampering")
            with self.assertRaisesRegex(ValueError, "digest"):
                build_packet(evidence, root / "packet", root / "key", seed=2)
            self.assertFalse((root / "packet").exists())

    def test_level_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = fixture(root, mismatch=True)
            with self.assertRaisesRegex(ValueError, "RMS-matched"):
                build_packet(evidence, root / "packet", root / "key", seed=3)

    def test_refuses_overwrite_and_overlapping_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = fixture(root)
            build_packet(evidence, root / "packet", root / "key", seed=4)
            with self.assertRaises(FileExistsError):
                build_packet(evidence, root / "packet", root / "new-key", seed=4)
            with self.assertRaises(ValueError):
                build_packet(evidence, root / "nested", root / "nested" / "key", seed=4)
            with self.assertRaises(ValueError):
                build_packet(evidence, root / "evidence" / "nested", root / "third", seed=4)


if __name__ == "__main__":
    unittest.main()
