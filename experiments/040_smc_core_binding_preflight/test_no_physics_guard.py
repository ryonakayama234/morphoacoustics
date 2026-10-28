"""A09 independent boundary checks, added after Codex P2 review of original Gate A.

Source scanner + instrumented execution for both read-only preflight and CLI.
Not a security sandbox for arbitrary Python; the scoped guarantee is that
THIS source and this frozen fixture do not execute Core physics or write output.
"""
from __future__ import annotations

import ast
import builtins
from contextlib import contextmanager
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import wave
from typing import Iterator

import pytest

HERE = Path(__file__).resolve().parent
SMC_TESTS = HERE.parents[1] / "packages" / "speech-motor-compiler" / "tests"
sys.path.insert(0, str(SMC_TESTS))
sys.path.insert(0, str(HERE))
from test_smc5_preregistered import encoded, valid
from binding_preflight import audit_smc_core_binding

SCAN_FILES = (HERE / "binding_preflight.py", HERE / "run.py")
ALLOWED_IMPORT_ROOTS = {
    "__future__", "dataclasses", "fractions", "pathlib", "json", "sys",
    "morphoacoustics_smc", "test_smc5_preregistered", "binding_preflight",
}
NO_WRITE_CALLS = {
    "open", "write_text", "write_bytes", "mkdir", "makedirs", "touch", "unlink",
    "rename", "replace", "remove", "rmdir", "dump", "dumps_file",
    "save", "savez", "savez_compressed", "wave", "wavfile", "writeframes",
    "system", "popen", "run", "call", "check_call", "check_output",
    "exec", "eval", "__import__", "import_module",
}


def _call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def test_a09_source_scanner_rejects_physics_imports_and_output_calls() -> None:
    """Inspect both entrypoints; no unexamined external executor may appear."""
    for source in SCAN_FILES:
        root = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(root):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] in ALLOWED_IMPORT_ROOTS, (
                        source.name, node.lineno, alias.name)
            if isinstance(node, ast.ImportFrom):
                assert node.level == 0, (source.name, node.lineno, "relative import")
                assert (node.module or "").split(".")[0] in ALLOWED_IMPORT_ROOTS, (
                    source.name, node.lineno, node.module)
            if isinstance(node, ast.Call):
                assert _call_name(node.func) not in NO_WRITE_CALLS, (
                    source.name, node.lineno, _call_name(node.func))
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                assert "morphoacoustics.realization" not in ast.unparse(node)
                assert "morphoacoustics.acoustics" not in ast.unparse(node)


@contextmanager
def _no_physics_no_write(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Instrument ordinary Python file/physics paths during actual CLI invocation.

    Subprocesses, unrestricted native libraries and arbitrary hostile code are
    out of scope; the AST source scanner forbids constructing these paths.
    """
    with monkeypatch.context() as m:
        original_import = builtins.__import__
        original_open = builtins.open
        original_io_open = io.open
        original_path_open = Path.open
        original_os_open = os.open

        def guarded_import(name: str, *args: object, **kwargs: object) -> object:
            if name == "morphoacoustics" or name.startswith("morphoacoustics."):
                raise AssertionError("FORBIDDEN_CORE_PHYSICS_IMPORT:" + name)
            return original_import(name, *args, **kwargs)

        def guarded_open(file: object, mode: str = "r", *args: object, **kwargs: object) -> object:
            if any(char in str(mode) for char in ("w", "a", "x", "+")):
                raise AssertionError("FORBIDDEN_FILE_WRITE")
            return original_open(file, mode, *args, **kwargs)

        def guarded_io_open(file: object, mode: str = "r", *args: object, **kwargs: object) -> object:
            if any(char in str(mode) for char in ("w", "a", "x", "+")):
                raise AssertionError("FORBIDDEN_FILE_WRITE")
            return original_io_open(file, mode, *args, **kwargs)

        def guarded_path_open(self: Path, mode: str = "r", *args: object, **kwargs: object) -> object:
            if any(char in str(mode) for char in ("w", "a", "x", "+")):
                raise AssertionError("FORBIDDEN_FILE_WRITE")
            return original_path_open(self, mode, *args, **kwargs)

        def guarded_os_open(file: object, flags: int, *args: object, **kwargs: object) -> int:
            mask = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
            if flags & mask:
                raise AssertionError("FORBIDDEN_OS_WRITE")
            return original_os_open(file, flags, *args, **kwargs)

        def refuse(*args: object, **kwargs: object) -> None:
            raise AssertionError("FORBIDDEN_OUTPUT_OR_PROCESS")

        m.setattr(builtins, "__import__", guarded_import)
        m.setattr(builtins, "open", guarded_open)
        m.setattr(io, "open", guarded_io_open)
        m.setattr(Path, "open", guarded_path_open)
        m.setattr(Path, "write_text", refuse)
        m.setattr(Path, "write_bytes", refuse)
        m.setattr(os, "open", guarded_os_open)
        m.setattr(os, "mkdir", refuse)
        m.setattr(os, "makedirs", refuse)
        m.setattr(os, "system", refuse)
        m.setattr(subprocess, "run", refuse)
        m.setattr(subprocess, "Popen", refuse)
        m.setattr(wave, "open", refuse)
        yield


def test_a09_guard_really_detects_injected_physics_and_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Prove the instrument would fail even if a STOP receipt were returned."""
    with _no_physics_no_write(monkeypatch):
        with pytest.raises(AssertionError, match="FORBIDDEN_CORE_PHYSICS_IMPORT"):
            __import__("morphoacoustics.realization")
        with pytest.raises(AssertionError, match="FORBIDDEN_OUTPUT_OR_PROCESS"):
            (tmp_path / "fake-voice.wav").write_bytes(b"RIFF")
        with pytest.raises(AssertionError, match="FORBIDDEN_FILE_WRITE"):
            with open(tmp_path / "fake-take.json", "wb"):
                pass


def test_a09_real_valid_and_rejected_adapter_and_cli_have_no_side_effects(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    with _no_physics_no_write(monkeypatch):
        valid_receipt = audit_smc_core_binding(encoded(valid()))
        rejected_receipt = audit_smc_core_binding(b"not-json")
        # Run the ACTUAL CLI source, including its own main function.
        namespace = runpy.run_path(str(HERE / "run.py"), run_name="cvi1_preflight_guard")
        exit_code = namespace["main"]()
    out = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert valid_receipt.stage_a == "FORMAL_AUTHENTICATED"
    assert valid_receipt.stage_b == "UNMAPPED_SEMANTICS"
    assert rejected_receipt.stage_a == "REJECTED"
    assert rejected_receipt.tasks == ()
    assert out["stage_a"] == "FORMAL_AUTHENTICATED"
    assert out["stage_b"] == "UNMAPPED_SEMANTICS"
    assert out["physical_coverage"] == {"supported": 0, "required": 3}
    assert out["physical_trace"] is None
    assert out["acoustic_trace"] is None
    assert out["take"] is None
    assert all(event["NOT_a_measured_articulator_event"] for event in out["exact_smc_events"])
