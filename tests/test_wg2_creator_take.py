"""WG2-Creator: standalone source/body/monitor publication and reject controls."""
from __future__ import annotations

from hashlib import sha256
import io
from pathlib import Path
import runpy
import json
import os
import wave

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = runpy.run_path(str(ROOT / "tools/wg2_creator_take.py"))
GENERATE = CLI["generate"]
VERIFY = CLI["verify"]
VALIDATE = CLI["validate_request"]


@pytest.mark.parametrize("bad", [
    dict(preset_id="v3b-axial-M9"),
    dict(revision=2),
    dict(revision=True),
    dict(character_id="../../outside"),
    dict(character_id=""),
    dict(duration_s=0.75),
    dict(duration_s=float("nan")),
])
def test_reject_invalid_prepared_identity_before_any_file(tmp_path: Path, bad: dict) -> None:
    arguments = dict(preset_id="v3b-axial-M0", revision=1,
                     character_id="example_1", duration_s=0.25)
    arguments.update(bad)
    dest = tmp_path / "no-audio"
    with pytest.raises(ValueError, match="UNSUPPORTED"):
        GENERATE(dest, **arguments)
    assert not dest.exists()


def test_bundle_verifier_rejects_modified_raw_evidence(tmp_path: Path) -> None:
    from pathlib import Path
    artifacts = {}
    for item in CLI["ARTIFACTS"]:
        blob = b"content" + item.encode("ascii")
        (tmp_path / item).write_bytes(blob)
        artifacts[item] = dict(sha256=sha256(blob).hexdigest(), bytes=len(blob))
    manifest = {
        "schema_version": CLI["VERSION"], "status": "SUCCEEDED",
        "core_commit": CLI["_core_commit"](),
        "body": {"preset_id": "v3b-axial-M0", "revision": 1},
        "observer": {"observation_point": "mouth-port-pressure-not-external-microphone"},
        "artifacts": artifacts,
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    assert VERIFY(tmp_path) == manifest
    (tmp_path / "audio.wav").write_bytes(b"forged")
    with pytest.raises(ValueError, match="TAMPERED"):
        VERIFY(tmp_path)


@pytest.mark.skipif(os.environ.get("WG2_CREATOR_REAL") != "1",
                    reason="requires frozen SV1+CC-A2 provenance, locked NumPy and physics")
def test_fresh_cc_a2_m0_m1_static_physical_takes(tmp_path: Path) -> None:
    bodies = []
    for preset_id in ("v3b-axial-M0", "v3b-axial-M1"):
        out = tmp_path / preset_id
        result = GENERATE(out, preset_id=preset_id, revision=1,
                          character_id="creator-test", duration_s=0.25)
        assert VERIFY(out) == result
        assert result["status"] == "SUCCEEDED"
        assert result["body"]["preset_id"] == preset_id
        assert result["body"]["preparation_digest"].startswith("sha256:")
        assert result["observer"]["output_samples"] == 12000
        assert result["observer"]["max_abs_energy_residual_j"] < 1e-12
        with wave.open(str(out / "audio.wav"), "rb") as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate(),
                    w.getnframes()) == (1, 2, 48000, 12000)
        source = np.load(out / "source_flow_48k.npy", allow_pickle=False)
        p = np.load(out / "mouth_pressure_native_pa.npy", allow_pickle=False)
        monitor = np.load(out / "mouth_pressure_monitor_48k_pa.npy", allow_pickle=False)
        assert source.shape == monitor.shape == (12000,)
        assert p.shape == (result["observer"]["physics_ticks"],)
        assert np.any(monitor != 0)
        assert np.all(np.isfinite(p))
        bodies.append((result, source, p))
    assert np.array_equal(bodies[0][1], bodies[1][1])
    assert bodies[0][0]["body"]["preparation_digest"] != bodies[1][0]["body"]["preparation_digest"]
    assert bodies[0][0]["observer"]["physics_clock_hz"] != bodies[1][0]["observer"]["physics_clock_hz"]
    assert bodies[0][0]["observer"]["physical_pressure_sha256"] != bodies[1][0]["observer"]["physical_pressure_sha256"]
    with pytest.raises(FileExistsError):
        GENERATE(tmp_path / "v3b-axial-M0", preset_id="v3b-axial-M0",
                 revision=1, character_id="creator-test", duration_s=0.25)
