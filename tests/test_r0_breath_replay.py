"""Operational checks; these do not confer scientific adoption on NV1.

Optional real-render integration uses the unchanged source bytes in a temporary
Git repository. Only the wrapper PIN is patched to that fixture repository's
commit, so it is not a replay of the historical Git checkout.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


DRIVER = Path(__file__).resolve().parents[1] / "tools/r0_breath_replay.py"
SPEC = importlib.util.spec_from_file_location("r0_breath_replay", DRIVER)
assert SPEC and SPEC.loader
r0 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r0)


class OperationsTests(unittest.TestCase):
    def test_probe_is_serializable_without_synthesis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = r0.environment(root)
            json.dumps(result, allow_nan=False)
            self.assertEqual(list(root.iterdir()), [])
            self.assertEqual(result["gpu"], "NOT_PROBED_CPU_ONLY_JOB")

    def test_rejects_different_source_before_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Pinned source bytes"):
                r0.qualified_source(Path(tmp))

    def test_missing_or_partial_completion_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "Missing"):
                r0.verify(root)
            r0.dump(root / "complete.json", {"schema": r0.SCHEMA, "expected_source_pin": r0.PIN, "files": {}})
            with self.assertRaisesRegex(ValueError, "Completion record"):
                r0.verify(root)

    def test_changed_result_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stdout.txt").write_text("changed")
            r0.dump(root / "complete.json", {"schema": r0.SCHEMA,
                     "expected_source_pin": r0.PIN, "files": {"stdout.txt": "0" * 64}})
            with self.assertRaisesRegex(ValueError, "Saved replay file changed"):
                r0.verify(root)

    def test_artifacts_cannot_escape_or_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real").write_text("data")
            for name in ("../outside", str(root / "real")):
                with self.assertRaises(ValueError):
                    r0.safe_file(root, name)
            try:
                (root / "link").symlink_to(root / "real")
            except OSError:
                return
            with self.assertRaises(ValueError):
                r0.safe_file(root, "link")

    def test_existing_output_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            output = root / "result"
            output.mkdir()
            with self.assertRaisesRegex(ValueError, "new output"):
                r0.run(source, output)
            self.assertEqual(list(output.iterdir()), [])

    def test_output_cannot_dirty_source_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            with self.assertRaisesRegex(ValueError, "outside"):
                r0.run(source, source / "result")

    def test_timeout_keeps_failure_log_without_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            output = root / "result"
            with patch.object(r0, "qualified_source", return_value={"test": True}), \
                 patch.object(r0, "environment", return_value={"packages": r0.VERSIONS}), \
                 patch.object(r0.subprocess, "run", side_effect=subprocess.TimeoutExpired("fixture", .1)):
                with self.assertRaises(subprocess.TimeoutExpired):
                    r0.run(source, output, .1)
            self.assertTrue((output / "failed.json").is_file())
            self.assertFalse((output / "complete.json").exists())
            self.assertTrue((output / "stderr.txt").is_file())


@unittest.skipUnless(os.environ.get("R0_TEST_SOURCE_ROOT"), "Set R0_TEST_SOURCE_ROOT for unchanged-source render integration")
class RenderIntegrationTests(unittest.TestCase):
    def test_render_verify_archive_and_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            original = Path(os.environ["R0_TEST_SOURCE_ROOT"])
            for name, expected in r0.SOURCE_HASHES.items():
                src = original / name
                self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(), expected)
                target = source / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, target)
            def git(*args):
                return subprocess.check_output(["git", "-C", str(source), *args],
                                               text=True, stderr=subprocess.PIPE).strip()
            git("init")
            git("add", ".")
            git("-c", "user.name=R0 fixture", "-c", "user.email=r0-fixture@example.invalid",
                "commit", "-m", "Temporary operational test fixture")
            fixture_pin = git("rev-parse", "HEAD")
            output = root / "result"
            with patch.object(r0, "PIN", fixture_pin):
                result = r0.run(source, output)
                self.assertEqual(result["cases"], list(r0.PRESETS))
                self.assertEqual(result["status"], "ARTIFACT_CHECKS_PASSED")
                self.assertEqual(git("status", "--porcelain"), "")
                with zipfile.ZipFile(output / "bundle.zip") as archive:
                    self.assertIn("complete.json", archive.namelist())
                    archive.extractall(root / "returned")
                self.assertEqual(r0.verify(root / "returned")["status"], "ARTIFACT_CHECKS_PASSED")
                evidence_path = output / "render/evidence.json"
                evidence = json.loads(evidence_path.read_text())
                evidence["playback_gain"] = 71
                r0.dump(evidence_path, evidence)
                with self.assertRaisesRegex(ValueError, "evidence field"):
                    r0.inspect_render(output / "render")
                evidence["playback_gain"] = 70
                r0.dump(evidence_path, evidence)
                trace = output / "render" / evidence["cases"]["P0"]["trace"]
                trace.write_bytes(b"corrupt")
                with self.assertRaisesRegex(ValueError, "digest differs"):
                    r0.inspect_render(output / "render")
                (source / "unexpected.txt").write_text("untracked input")
                with self.assertRaisesRegex(ValueError, "clean"):
                    r0.qualified_source(source)
                (source / "unexpected.txt").unlink()
                with patch.object(r0, "PIN", "0" * 40):
                    with self.assertRaisesRegex(ValueError, "documented pin"):
                        r0.qualified_source(source)
                model = source / r0.EXPERIMENT / "source.py"
                model.write_bytes(model.read_bytes() + b"\n# source drift\n")
                refused_output = root / "refused"
                with self.assertRaisesRegex(ValueError, "Pinned source bytes"):
                    r0.run(source, refused_output)
                self.assertFalse(refused_output.exists())


if __name__ == "__main__":
    unittest.main()
