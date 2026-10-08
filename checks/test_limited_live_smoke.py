"""Full on-demand physics smoke: run only with audited NumPy 2.4.6 in dedicated CI."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import wave

import numpy as np
import pytest

from morphoacoustics.domain.result import FeasibilityStatus
from morphoacoustics.integration import limited_live as live


def fixture_request() -> dict[str, object]:
    return {
        "schema_version": live.SCHEMA_VERSION,
        "pronunciation_id": live.PRONUNCIATION_ID,
        "body_id": live.BODY_ID,
        "segment_id": "s1",
        "text": "あい",
        "seed": 0,
    }


@pytest.fixture(scope="module")
def audited():
    assert np.__version__ == "2.4.6"
    return live._load_audited_experiment()


def test_feasibility_preflight_guards_acoustics(audited, monkeypatch):
    start = audited.EXP26.EXP23.primary_geometry("a")
    negative = audited.prepared_for(
        creature=audited.creature_for(
            cavity_id=start.cavity_id, oral_reachable_end=0.70,
        ),
        geometry=start, condition="M_minus",
    )
    report = audited.capability_report(negative)
    assert report.status == FeasibilityStatus.INFEASIBLE
    assert report.issues[0].code == "LOCATION_UNREACHABLE"
    assert report.issues[0].gesture_index == 1

    # The audited evaluate_condition must branch BEFORE transfer calls.
    source = np.zeros((live.SAMPLES,), dtype=np.float64)

    def forbidden(*args, **kwargs):
        raise AssertionError("infeasible fixture must not invoke acoustic transfer")
    monkeypatch.setattr(audited.EXP26.EXP9, "far_field_pressure_transfer", forbidden)
    result = audited.evaluate_condition(negative, source, label="m_minus")
    assert result.endpoint is None
    assert result.waveform is None
    assert result.acoustic_call_count == 0


def test_real_live_runs_twice_and_persists_content(audited, tmp_path):
    req = fixture_request()
    outputs = []
    for i in range(2):
        out = tmp_path / f"take-{i}"
        result = live.perform(req, out)
        assert result["job_status"] == "SUCCEEDED"
        assert result["realization_outcome"] == "FEASIBLE"
        assert result["execution"]["acoustic_transfer_calls"] == 102
        assert result["execution"]["waveform_samples"] == live.SAMPLES
        assert result["provenance"]["quantized_raw_pressure_sha256"] == audited.AUDITED_QUANTIZED_WAVEFORM_SHA256
        artifacts = {artifact["kind"]: artifact for artifact in result["artifacts"]}
        assert set(artifacts) == {"audio", "raw_pressure", "physical_trace"}
        for artifact in artifacts.values():
            contents = (out / artifact["path"]).read_bytes()
            assert hashlib.sha256(contents).hexdigest() == artifact["sha256"]
        with wave.open(str(out / "audio.wav"), "rb") as handle:
            assert handle.getnframes() == live.SAMPLES
            assert handle.getframerate() == live.SAMPLE_RATE_HZ
            assert handle.getnchannels() == 1
            assert handle.getsampwidth() == 2
        pressure = np.load(out / "raw_pressure_pa.npy", allow_pickle=False)
        assert pressure.shape == (live.SAMPLES,)
        assert audited.quantized_waveform_sha256(pressure) == audited.AUDITED_QUANTIZED_WAVEFORM_SHA256
        lines = (out / "physical_trace.csv").read_text().splitlines()
        assert len(lines) == 52
        assert json.loads((out / "result.json").read_text()) == result
        outputs.append((out, result, artifacts))
    assert outputs[0][0] != outputs[1][0]
    # Same frozen task causes same PCM bytes, yet each Take had 102 *new* acoustic calls.
    assert outputs[0][2]["audio"]["sha256"] == outputs[1][2]["audio"]["sha256"]
    assert outputs[0][2]["physical_trace"]["sha256"] == outputs[1][2]["physical_trace"]["sha256"]
    assert outputs[0][1]["provenance"]["request_sha256"] == outputs[1][1]["provenance"]["request_sha256"]
    with pytest.raises(FileExistsError):
        live.perform(req, outputs[0][0])


def test_unsupported_inputs_produce_no_artifacts(tmp_path):
    for i, updated in enumerate((
        {"text": "あお"}, {"body_id": "v3c-M_minus/v1"}, {"direction": {"energy": 0.8}},
    )):
        out = tmp_path / f"rejected-{i}"
        answer = live.perform({**fixture_request(), **updated}, out)
        assert answer["job_status"] == "SUCCEEDED"
        assert answer["realization_outcome"] == "UNSUPPORTED"
        assert not answer["artifacts"]
        assert not out.exists()
