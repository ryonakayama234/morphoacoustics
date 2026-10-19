"""CC-A2 scientific integration checks: fresh physics, exact body, no fallback."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import runpy

import numpy as np
import pytest

BASE = Path(__file__).resolve().parents[1]
RUNNER = runpy.run_path(str(BASE / "tools" / "cc_a2_live.py"))
perform = RUNNER["perform"]

pytestmark = pytest.mark.skipif(
    os.environ.get("CC_A2_REAL_PHYSICS") != "1",
    reason="real physics needs pinned NumPy 2.4.6 and dedicated CC-A2 CI",
)


def request(body: str = "v3b-axial-M0") -> dict:
    x = json.loads(
        (BASE / "contracts" / "performance" / "v1" / "examples" / "request.json").read_text("utf-8")
    )
    x["request_id"] = "cc_a2_" + body.replace("-", "_")
    x["script"]["segments"] = [{
        "segment_id": "s1", "speaker_character_id": x["character"]["character_id"], "text": "あい"
    }]
    x["direction"]["note"] = ""
    x["direction"]["controls"] = {}
    x["direction"]["segment_overrides"] = []
    x["seed"] = 0
    x["requested_capabilities"] = ["audio", "timeline", "physical_trace", "diagnostics"]
    x["embodiment"] = {"preset_id": body, "preset_revision": 1}
    return x


def test_both_bodies_fresh_waveforms_and_wolfram_oracle(tmp_path: Path) -> None:
    a = perform(request("v3b-axial-M0"), tmp_path / "A")
    b = perform(request("v3b-axial-M1"), tmp_path / "B")
    assert a["job_status"] == b["job_status"] == "SUCCEEDED"
    assert a["realization_outcome"] == b["realization_outcome"] == "FEASIBLE"
    assert a["embodiment"]["preparation_digest"] != b["embodiment"]["preparation_digest"]
    assert a["provenance"]["input_digest"] != b["provenance"]["input_digest"]
    r0 = json.loads((tmp_path / "A" / "physical_receipt.json").read_text("utf-8"))
    r1 = json.loads((tmp_path / "B" / "physical_receipt.json").read_text("utf-8"))
    assert r0["body"]["length_m"] == pytest.approx(0.16)
    assert r1["body"]["length_m"] == pytest.approx(0.176)
    assert r0["endpoint_peak_hz"] == pytest.approx([275.00, 2101.75], abs=0.25)
    assert r1["endpoint_peak_hz"] == pytest.approx([249.75, 1910.75], abs=0.25)
    assert r0["raw_pressure"]["quantized_sha256"] == (
        "dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e"
    )
    assert r0["raw_pressure"]["quantized_sha256"] != r1["raw_pressure"]["quantized_sha256"]
    assert r0["task_plan_sha256"] == r1["task_plan_sha256"]
    for letter in ["A", "B"]:
        assert (tmp_path / letter / "audio.wav").read_bytes().startswith(b"RIFF")
        assert (tmp_path / letter / "result.json").is_file()
        with (tmp_path / letter / "raw_pressure_pa.npy").open("rb") as f:
            raw = np.load(f, allow_pickle=False)
        assert raw.shape == (24000,) and np.isfinite(raw).all()
        trace = (tmp_path / letter / "physical_trace.csv").read_text("utf-8")
        assert trace.count("\n") == 52  # 1 header + 51 physical timestamps


def test_equal_request_is_deterministic_and_never_reuses_a_take(tmp_path: Path) -> None:
    x = request()
    a = perform(x, tmp_path / "first")
    b = perform(x, tmp_path / "second")
    assert a["provenance"]["input_digest"] == b["provenance"]["input_digest"]
    assert (tmp_path / "first" / "audio.wav").read_bytes() == (
        tmp_path / "second" / "audio.wav"
    ).read_bytes()
    with pytest.raises(FileExistsError):
        perform(x, tmp_path / "first")


def test_refusals_never_generate_fake_audio(tmp_path: Path) -> None:
    for i, (change, expected, binding) in enumerate([
        ({"embodiment": {"preset_id": "none", "preset_revision": 1}}, "UNSUPPORTED", "MISSING_PRESET"),
        ({"embodiment": {"preset_id": "v3b-axial-M0", "preset_revision": 2}}, "UNSUPPORTED", "REVISION_MISMATCH"),
        ({"seed": 4}, "UNSUPPORTED", "BOUND"),
    ]):
        item = request()
        item.update(change)
        out_dir = tmp_path / ("bad" + str(i))
        result = perform(item, out_dir)
        assert result["realization_outcome"] == expected
        assert result["embodiment"]["status"] == binding
        assert result["artifacts"] == []
        assert not out_dir.exists()


def test_invalid_body_and_creative_physics_injection_refused(tmp_path: Path) -> None:
    x = request()
    x["embodiment"]["preset_revision"] = "latest"
    with pytest.raises(Exception):
        perform(x, tmp_path / "invalid")
    assert not (tmp_path / "invalid").exists()
    y = deepcopy(request())
    y["character"]["tract_area"] = 1.5
    with pytest.raises(Exception):
        perform(y, tmp_path / "inject")
    assert not (tmp_path / "inject").exists()
