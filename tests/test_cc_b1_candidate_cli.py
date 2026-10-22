"""Fail-closed outer CLI candidate tests; negative cases never run synthesis."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "cc_b1_candidate_cli.py"
V = "cc-b1-core-limited-performer/v1"
OPT = ["--protocol-version", V]


def invoke(*args: object) -> tuple[int, dict[str, object], str]:
    p = subprocess.run(
        [sys.executable, str(CLI), *(str(a) for a in args)],
        cwd=ROOT, capture_output=True, text=True, timeout=60, check=False,
    )
    assert p.stdout.count("\n") == 1, p.stdout
    out = json.loads(p.stdout)
    assert isinstance(out, dict)
    assert out["schema_version"] == V
    return p.returncode, out, p.stderr


def expect_failure(args: list[object], code: str) -> None:
    rc, value, stderr = invoke(*args)
    assert rc != 0, value
    assert value["status"] != "SUCCEEDED"
    assert value["artifacts"] == []
    assert value["error"]["code"] == code
    assert "Traceback" not in stderr


@pytest.mark.parametrize("argv,code", [
    (["--inspect"], "CLI_ARGUMENT_INVALID"),
    (["--protocol-version", "v999", "--inspect"], "SCHEMA_VERSION_UNSUPPORTED"),
    ([*OPT], "CLI_ARGUMENT_INVALID"),
    ([*OPT, "--inspect", "--verify"], "CLI_ARGUMENT_INVALID"),
    ([*OPT, "--inspect", "--request", "x"], "CLI_ARGUMENT_INVALID"),
    ([*OPT, "--perform"], "CLI_ARGUMENT_INVALID"),
    ([*OPT, "--verify"], "CLI_ARGUMENT_INVALID"),
    ([*OPT, "--verify", "--archive-dir", "x", "--output-dir", "y"], "CLI_ARGUMENT_INVALID"),
    ([*OPT, "--fake-flag", "--inspect"], "CLI_ARGUMENT_INVALID"),
])
def test_command_contract_rejects_ambiguity(argv: list[str], code: str) -> None:
    expect_failure(argv, code)


@pytest.mark.parametrize("bytestr", [
    b'{"parent":{"preparation_digest":"x","preparation_digest":"y"}}',
    b'{"edit":{"rest_area_ratio":"0.90","rest_area_ratio":"1.10"}}',
    b'{"something":NaN}',
    b'{"something":Infinity}',
    b'{"something":-Infinity}',
    b'{"broken":',
    b'{"a":"\xff"}',
    b'x' * 4097,
])
def test_bad_json_never_produces_an_archive(tmp_path: Path, bytestr: bytes) -> None:
    request = tmp_path / "request.json"
    request.write_bytes(bytestr)
    output = tmp_path / "out"
    expect_failure([*OPT, "--perform", "--request", request,
                    "--output-dir", output], "REQUEST_JSON_INVALID")
    assert not output.exists()


def test_file_and_parent_symlinks_refuse_before_synthesis(tmp_path: Path) -> None:
    actual = tmp_path / "real.json"
    actual.write_text("{}", "utf-8")
    link = tmp_path / "request.json"
    try:
        link.symlink_to(actual)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is unavailable")
    expect_failure([*OPT, "--perform", "--request", link,
                    "--output-dir", tmp_path / "out"], "REQUEST_JSON_INVALID")
    alias = tmp_path / "linked-parent"
    alias.symlink_to(tmp_path, target_is_directory=True)
    expect_failure([*OPT, "--perform", "--request", actual,
                    "--output-dir", alias / "out"], "OUTPUT_PATH_UNSAFE")


def test_existing_output_refuses_before_loading_core(tmp_path: Path) -> None:
    request = tmp_path / "request.json"
    request.write_text("{}", "utf-8")
    output = tmp_path / "already-exists"
    output.mkdir()
    expect_failure([*OPT, "--perform", "--request", request,
                    "--output-dir", output], "OUTPUT_PATH_UNSAFE")


def test_corrupt_archive_rejected_before_receipt_replay(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    result = archive / "result.json"
    # Manifest duplicate-key attacks must not reach the inherited nonstrict parser.
    result.write_text('{"status":"SUCCEEDED","status":"FAILED"}', "utf-8")
    expect_failure([*OPT, "--verify", "--archive-dir", archive], "ARCHIVE_JSON_INVALID")
    result.write_text('{"status":NaN}', "utf-8")
    expect_failure([*OPT, "--verify", "--archive-dir", archive], "ARCHIVE_JSON_INVALID")
    result.write_bytes(b"x" * 65537)
    expect_failure([*OPT, "--verify", "--archive-dir", archive], "ARCHIVE_JSON_INVALID")
    result.unlink()
    expect_failure([*OPT, "--verify", "--archive-dir", archive], "ARCHIVE_JSON_INVALID")


def test_unverified_archive_is_never_a_success(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "result.json").write_text('{"status":"SUCCEEDED"}', "utf-8")
    expect_failure([*OPT, "--verify", "--archive-dir", archive],
                   "ARCHIVE_VERIFICATION_FAILED")


@pytest.mark.skipif(os.environ.get("CC_B1_GATE_C_PHYSICAL") != "1",
                    reason="Dedicated job executes two real Core physical pairs")
def test_actual_two_physical_pairs_via_cli(tmp_path: Path) -> None:
    rc, base, _ = invoke(*OPT, "--inspect")
    assert rc == 0
    assert base["editable"]["section_index"] == 8
    for ratio in ("0.90", "1.10"):
        req = {
            "schema_version": V,
            "parent": base["parent"],
            "edit": {
                "cavity_id": base["editable"]["cavity_id"],
                "section_index": 8,
                "rest_area_ratio": ratio,
            },
        }
        request = tmp_path / ("request-" + ratio + ".json")
        request.write_text(json.dumps(req), "utf-8")
        output = tmp_path / ("pair-" + ratio)
        rc, receipt, _ = invoke(
            *OPT, "--perform", "--request", request, "--output-dir", output
        )
        assert rc == 0 and receipt["status"] == "SUCCEEDED"
        assert receipt["acoustic_calls_per_body"] == 102
        assert output.joinpath("result.json").is_file()
        rc, verified, _ = invoke(*OPT, "--verify", "--archive-dir", output)
        assert rc == 0
        assert verified == receipt
