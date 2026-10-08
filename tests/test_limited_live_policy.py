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




def test_frozen_package_source_inventory_is_complete_and_matches_checkout():
    from morphoacoustics.integration import limited_live as live

    live._verify_frozen_sources_before_import()
    expected = set(live.AUDITED_PACKAGE_GIT_BLOBS)
    actual = {
        path.relative_to(live.ROOT).as_posix()
        for path in (live.ROOT / "src" / "morphoacoustics").rglob("*.py")
        if path != live.ROOT / "src/morphoacoustics/integration/limited_live.py"
    }
    assert expected == actual
    assert "src/morphoacoustics/domain/creature.py" in expected
    assert "src/morphoacoustics/preparation/tract1d.py" in expected


def test_preimport_rejects_changed_experiment_029_package_dependencies(monkeypatch):
    import pytest
    from pathlib import Path
    from morphoacoustics.integration import limited_live as live

    real_read = Path.read_bytes
    paths = (
        "src/morphoacoustics/domain/creature.py",
        "src/morphoacoustics/domain/result.py",
        "src/morphoacoustics/preparation/tract1d.py",
    )

    def import_must_not_run(*_args, **_kwargs):
        raise AssertionError("executed experiment before auditing its package dependencies")

    monkeypatch.setattr(live.importlib.util, "module_from_spec", import_must_not_run)
    for relative in paths:
        target = live.ROOT / relative

        def tampered_read(self, *, _target=target):
            data = real_read(self)
            return data + b"\\n# tampered package dependency\\n" if self == _target else data

        with monkeypatch.context() as patcher:
            patcher.setattr(Path, "read_bytes", tampered_read)
            with pytest.raises(RuntimeError, match="audited package Git blob changed before import"):
                live._load_audited_experiment()


def test_preimport_rejects_unregistered_package_module(monkeypatch):
    import pytest
    from pathlib import Path
    from morphoacoustics.integration import limited_live as live

    root = live.ROOT / "src" / "morphoacoustics"
    original_rglob = Path.rglob

    def with_added_file(self, pattern):
        paths = list(original_rglob(self, pattern))
        return paths + [root / "domain" / "unexpected_unreviewed.py"] if self == root else paths

    def import_must_not_run(*_args, **_kwargs):
        raise AssertionError("executed experiment before source inventory verification")

    monkeypatch.setattr(Path, "rglob", with_added_file)
    monkeypatch.setattr(live.importlib.util, "module_from_spec", import_must_not_run)
    with pytest.raises(RuntimeError, match="audited package source inventory changed"):
        live._load_audited_experiment()


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


def test_dangling_symlink_destination_is_never_reused(tmp_path):
    import pytest
    from morphoacoustics.integration import limited_live as live

    destination = tmp_path / "take"
    destination.symlink_to(tmp_path / "missing-directory", target_is_directory=True)
    assert destination.is_symlink()
    assert not destination.exists()
    for req in (request(), {**request(), "text": "unsupported"}):
        with pytest.raises(FileExistsError, match="requires a new output directory"):
            live.perform(req, destination)
        assert destination.is_symlink()
    assert not (tmp_path / "missing-directory").exists()


def test_cli_rejects_existing_dangling_symlink_even_for_invalid_json(tmp_path):
    import json
    import subprocess
    import sys

    from morphoacoustics.integration import limited_live as live

    destination = tmp_path / "take"
    destination.symlink_to(tmp_path / "missing", target_is_directory=True)
    request_path = tmp_path / "invalid.json"
    request_path.write_text("{invalid", encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "morphoacoustics.integration.limited_live",
         "--request", str(request_path), "--output-dir", str(destination)],
        capture_output=True, text=True,
    )
    assert completed.returncode == 1
    response = json.loads(completed.stdout)
    assert response["job_status"] == "FAILED"
    assert response["artifacts"] == []
    assert destination.is_symlink()
    assert not (tmp_path / "missing").exists()


def test_publish_cannot_replace_racing_empty_directory(tmp_path, monkeypatch):
    import pytest
    from pathlib import Path
    from morphoacoustics.integration import limited_live as live

    output = tmp_path / "raced-take"
    real_mkdir = Path.mkdir

    def race_mkdir(self, *args, **kwargs):
        if self == output:
            real_mkdir(self, *args, **kwargs)
            (self / "another-producer.txt").write_text("owner", encoding="utf-8")
        return real_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", race_mkdir)
    with pytest.raises(FileExistsError, match="requires a new output directory"):
        live._publish_new_take(
            output, (("audio", "audio.wav", "audio/wav", b"new"),),
            {"job_status": "SUCCEEDED"},
        )
    assert (output / "another-producer.txt").read_text(encoding="utf-8") == "owner"
    assert not (output / "audio.wav").exists()
    assert not list(tmp_path.glob(".morpho-live-*"))


def test_publish_writes_manifest_last_as_completion_marker(tmp_path, monkeypatch):
    import json
    import os
    from morphoacoustics.integration import limited_live as live

    output = tmp_path / "new-take"
    real_replace = os.replace
    order = []

    def observe_replace(source, target):
        if target == output / "result.json":
            assert (output / "audio.wav").read_bytes() == b"wav"
            assert (output / "physical_trace.csv").read_bytes() == b"trace"
            assert not (output / "result.json").exists()
        order.append(target.name)
        return real_replace(source, target)

    monkeypatch.setattr(live.os, "replace", observe_replace)
    live._publish_new_take(
        output,
        (("audio", "audio.wav", "audio/wav", b"wav"),
         ("physical_trace", "physical_trace.csv", "text/csv", b"trace")),
        {"job_status": "SUCCEEDED", "realization_outcome": "FEASIBLE"},
    )
    assert order == ["audio.wav", "physical_trace.csv", "result.json"]
    assert json.loads((output / "result.json").read_text(encoding="utf-8")) == {
        "job_status": "SUCCEEDED", "realization_outcome": "FEASIBLE",
    }
    assert not list(tmp_path.glob(".morpho-live-*"))


def test_failed_publish_removes_partial_uncommitted_output(tmp_path, monkeypatch):
    import os
    import pytest
    from morphoacoustics.integration import limited_live as live

    output = tmp_path / "partial-take"
    real_replace = os.replace

    def fail_second_file(source, target):
        if target == output / "raw_pressure_pa.npy":
            raise OSError("simulated interrupted publish")
        return real_replace(source, target)

    monkeypatch.setattr(live.os, "replace", fail_second_file)
    with pytest.raises(OSError, match="simulated interrupted publish"):
        live._publish_new_take(
            output,
            (("audio", "audio.wav", "audio/wav", b"wav"),
             ("raw_pressure", "raw_pressure_pa.npy", "application/x-npy", b"raw")),
            {"job_status": "SUCCEEDED"},
        )
    assert not os.path.lexists(output)
    assert not list(tmp_path.glob(".morpho-live-*"))
