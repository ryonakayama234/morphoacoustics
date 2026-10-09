"""Package Experiment 030's already-rendered WAVs for a one-listener blind A/B pilot.

This changes file names and ordering ONLY. It never processes PCM or physical data.
Keep the separate answer-key artifact away from listeners until ratings are locked.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import random
import secrets
import sys
import uuid
import wave


SOURCES = {"s0": "s0_rd1p0.wav", "p1": "p1_rd1p4.wav"}
RMS_DB_TOLERANCE = 0.005


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_wav(path: Path) -> tuple[bytes, float]:
    data = path.read_bytes()
    with wave.open(str(path), "rb") as reader:
        if (reader.getnchannels(), reader.getsampwidth(), reader.getframerate(),
                reader.getnframes(), reader.getcomptype()) != (1, 2, 48000, 24000, "NONE"):
            raise ValueError("Unexpected WAV format: " + path.name)
        samples = reader.readframes(reader.getnframes())
    if len(samples) != 48000:
        raise ValueError("Unexpected PCM payload size: " + path.name)
    values = array("h")
    values.frombytes(samples)
    if sys.byteorder != "little":
        values.byteswap()
    rms = math.sqrt(sum(float(x) * x for x in values) / len(values)) / 32767.0
    if not math.isfinite(rms) or rms <= 0:
        raise ValueError("Silent or invalid preview: " + path.name)
    return data, 20.0 * math.log10(rms)


def _separate_outputs(evidence: Path, packet: Path, key: Path) -> None:
    roots = [evidence.resolve(), packet.resolve(), key.resolve()]
    if len(set(roots)) != 3:
        raise ValueError("Evidence, blind packet, and answer key must be separate")
    for out in (roots[1], roots[2]):
        if out.is_relative_to(roots[0]) or roots[0].is_relative_to(out):
            raise ValueError("Output must not overlap the named source evidence")
    if roots[1].is_relative_to(roots[2]) or roots[2].is_relative_to(roots[1]):
        raise ValueError("Do not nest the answer key within the blind packet")
    if packet.exists() or packet.is_symlink() or key.exists() or key.is_symlink():
        raise FileExistsError("Refuse to overwrite a blind packet or answer key")


def build_packet(evidence: Path, packet: Path, key: Path, seed: int | None = None) -> dict:
    _separate_outputs(evidence, packet, key)
    metrics_bytes = (evidence / "metrics.json").read_bytes()
    metrics = json.loads(metrics_bytes)
    if metrics.get("experiment") != "030-lf-rd-timbre-pilot/v1" or metrics.get("status") != (
        "scientific-physics-output-valid; perceptual-gate-pending"
    ):
        raise ValueError("Not the expected preregistered physical pilot output")
    matching = metrics["audition_level_matching"]
    if matching["procedure"] != "per-condition linear scalar RMS match; no post-EQ":
        raise ValueError("Only untouched scalar-level-matched physical WAVs are allowed")
    assets: dict[str, bytes] = {}
    levels: dict[str, float] = {}
    for condition, filename in SOURCES.items():
        data, dbfs = inspect_wav(evidence / filename)
        if sha256(data) != metrics["artifacts_sha256"][filename]:
            raise ValueError("Input WAV digest differs from experimental evidence")
        if sha256(data) != matching["conditions"][condition]["wav_sha256"]:
            raise ValueError("Input WAV digest differs from audition metadata")
        if abs(dbfs - matching["conditions"][condition]["rms_dbfs"]) > 0.002:
            raise ValueError("RMS measurement differs from evidence")
        assets[condition], levels[condition] = data, dbfs
    if abs(levels["s0"] - levels["p1"]) > RMS_DB_TOLERANCE:
        raise ValueError("WAVs are not RMS-matched within the preregistered tolerance")
    if assets["s0"] == assets["p1"]:
        raise ValueError("Two identical WAVs cannot form an A/B trial")

    actual_seed = secrets.randbits(64) if seed is None else seed
    if actual_seed < 0:
        raise ValueError("Seed must be nonnegative")
    flip = random.Random(actual_seed).randrange(2)
    mapping = {"A": "p1", "B": "s0"} if flip else {"A": "s0", "B": "p1"}
    trial_id = uuid.uuid4().hex
    public = {
        "schema": "morpho-blind-ab/v1", "trial_id": trial_id,
        "status": "listener-ratings-pending",
        "stimuli": [
            {"slot": slot, "file": slot + ".wav", "sha256": sha256(assets[condition]),
             "rms_dbfs": levels[condition]}
            for slot, condition in mapping.items()
        ],
        "sample_rate_hz": 48000, "sample_count": 24000,
        "rms_difference_db": abs(levels["s0"] - levels["p1"]),
        "note": "Unaltered PCM copied from two independently rendered physical conditions; equal RMS is not equal perceived loudness.",
    }
    private = {
        "schema": "morpho-blind-ab-key/v1", "trial_id": trial_id,
        "mapping": mapping, "randomization_seed": actual_seed,
        "source_metrics_sha256": sha256(metrics_bytes),
        "source_wav_sha256": {
            condition: sha256(assets[condition]) for condition in SOURCES
        },
        "note": "Withhold this file until free identification and preference ratings are locked.",
    }
    packet.mkdir(parents=True, exist_ok=False)
    key.mkdir(parents=True, exist_ok=False)
    for slot, condition in mapping.items():
        (packet / (slot + ".wav")).write_bytes(assets[condition])
    (packet / "trial.json").write_text(
        json.dumps(public, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (packet / "LISTEN_FIRST.txt").write_text(
        "Blind physical voice audition — do not open the separately stored answer key.\n"
        "Listen to A.wav and B.wav using the same headphones, player, and volume.\n"
        "You may replay freely. Do not inspect the original condition-named WAVs.\n"
        "Before revealing the key, record independently:\n"
        "1. Free transcription: what sounds do you hear in A and B?\n"
        "2. Transition continuity, each 1 (bad) to 5 (good).\n"
        "3. Buzziness or metallic sharpness, each 1 (none) to 5 (strong).\n"
        "4. Perceived loudness: A louder / B louder / about equal.\n"
        "5. Which sounds more enjoyable: A / B / neither, and why?\n"
        "Record trial_id from trial.json, then lock your response BEFORE opening the key.\n"
        "This is one subjective pilot, not a blinded population study or TTS validation.\n",
        encoding="utf-8",
    )
    (key / "answer_key.json").write_text(
        json.dumps(private, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return public


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--packet-dir", type=Path, required=True)
    parser.add_argument("--answer-key-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=None,
                        help="Deterministic test/debug only; omit for random assignment")
    args = parser.parse_args()
    result = build_packet(args.evidence_dir, args.packet_dir, args.answer_key_dir, args.seed)
    print(json.dumps({"trial_id": result["trial_id"], "status": result["status"],
                      "stimulus_labels": ["A", "B"], "mapping_withheld": True}))
