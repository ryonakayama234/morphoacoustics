"""Pure request-policy tests: run under the ordinary Python version matrix."""
from morphoacoustics.integration.limited_live import (
    BODY_ID, PRONUNCIATION_ID, SCHEMA_VERSION, validate,
)


def request():
    return {
        "schema_version": SCHEMA_VERSION,
        "pronunciation_id": PRONUNCIATION_ID,
        "body_id": BODY_ID,
        "segment_id": "s1",
        "text": "あい",
        "seed": 0,
    }


def test_supported_fixture_only():
    assert validate(request()) is None
    other_segment = {**request(), "segment_id": "s2"}
    assert validate(other_segment) is None


def test_rejects_unsupported_text_without_fallback():
    result = validate({**request(), "text": "こんにちは"})
    assert result is not None
    assert result["realization_outcome"] == "UNSUPPORTED"
    assert result["artifacts"] == []
    assert result["diagnostics"][0]["code"] == "PRONUNCIATION"


def test_rejects_unknown_body_and_creative_direction():
    for changed in (
        {"body_id": "some-other-body"},
        {"direction": {"emotion": "angry"}},
        {"seed": 123},
        {"pronunciation_id": "general-japanese/v1"},
    ):
        result = validate({**request(), **changed})
        assert result is not None
        assert result["realization_outcome"] == "UNSUPPORTED"
        assert result["artifacts"] == []


def test_structural_invalidity_distinct_from_unsupported():
    for changed in (
        {"seed": True},
        {"seed": "0"},
        {"segment_id": ""},
        {"arbitrary_solver_pressure": 0.8},
        {"direction": "not-a-dictionary"},
    ):
        result = validate({**request(), **changed})
        assert result is not None
        assert result["realization_outcome"] == "INVALID"
        assert result["artifacts"] == []


def test_rejects_missing_schema_and_arrays():
    for request_value in ({}, ["あい"], None):
        result = validate(request_value)
        assert result is not None
        assert result["realization_outcome"] == "INVALID"


def test_normalized_request_digest_is_independent_of_json_key_order():
    a = validate({**request(), "text": "X"})
    b = validate(dict(reversed(list({**request(), "text": "X"}.items()))))
    assert a is not None and b is not None
    assert a["provenance"]["request_sha256"] == b["provenance"]["request_sha256"]


def test_nonfinite_and_non_json_extensions_are_invalid():
    for bad in (float("nan"), float("inf")):
        result = validate({**request(), "direction": {"energy": bad}})
        assert result is not None
        assert result["realization_outcome"] == "INVALID"
        assert result["diagnostics"][0]["code"] == "REQUEST_ENCODING"
        assert result["provenance"]["request_sha256"] is None


def test_existing_successful_take_cannot_be_reused_for_invalid_or_unsupported(tmp_path):
    import pytest
    from morphoacoustics.integration import limited_live as live
    prior = tmp_path / "old-take"
    prior.mkdir()
    audio = prior / "audio.wav"
    audio.write_bytes(b"prior-real-audio")
    for changed in ({"text": "あお"}, {"seed": "invalid"}):
        with pytest.raises(FileExistsError, match="requires a new output directory"):
            live.perform({**request(), **changed}, prior)
        assert audio.read_bytes() == b"prior-real-audio"


def test_preimport_frozen_manifest_rejects_changed_transitive_code(monkeypatch):
    import pytest
    from pathlib import Path
    from morphoacoustics.integration import limited_live as live
    path = live.ROOT / "experiments" / "027_task_field_vowel_transition" / "run.py"
    original_read = Path.read_bytes

    def tampered_read(self):
        data = original_read(self)
        return data + b"\n# deliberately tampered\n" if self == path else data

    def unsafe_import(*_args, **_kwargs):
        raise AssertionError("experiment code executed before frozen source validation")

    monkeypatch.setattr(Path, "read_bytes", tampered_read)
    monkeypatch.setattr(live.importlib.util, "module_from_spec", unsafe_import)
    with pytest.raises(RuntimeError, match="transitive audited source changed before import"):
        live._load_audited_experiment()


def test_illformed_json_file_is_invalid_not_execution_failed(tmp_path):
    import json
    import subprocess
    import sys
    from pathlib import Path
    for index, payload in enumerate((b'{"bad":', b"\xff")):
        request_file = tmp_path / f"invalid-{index}.json"
        request_file.write_bytes(payload)
        out = tmp_path / f"not-created-{index}"
        completed = subprocess.run(
            [sys.executable, "-m", "morphoacoustics.integration.limited_live",
             "--request", str(request_file), "--output-dir", str(out)],
            check=True, capture_output=True, text=True,
        )
        response = json.loads(completed.stdout)
        assert response["job_status"] == "SUCCEEDED"
        assert response["realization_outcome"] == "INVALID"
        assert response["diagnostics"][0]["code"] == "REQUEST_JSON"
        assert response["provenance"]["request_sha256"] is None
        assert not out.exists()
