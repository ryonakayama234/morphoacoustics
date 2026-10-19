"""Controls must retain scientific semantics; an A→I→A source is NOT wave concat."""
import importlib.util
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("v4a_run",HERE/"run.py")
assert SPEC and SPEC.loader
M=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=M
SPEC.loader.exec_module(M)


class RoundtripTests(unittest.TestCase):
    def test_frozen_oracle_and_schedule(self):
        oracle=json.loads(M.ORACLE.read_text())
        self.assertEqual(oracle["sample_count"],48000)
        self.assertEqual(oracle["primary_transfer_calls"],196)
        self.assertEqual(oracle["reference_transfer_calls"],391)
        for t,v in oracle["anchors"]:
            self.assertAlmostEqual(M.analytic_activation(t),v,places=12)
            for a in M.activation_at(t,M.PRIMARY_STEP):
                self.assertAlmostEqual(a,v,places=12)
        self.assertEqual(M.analytic_activation(-.2),0)
        self.assertEqual(M.analytic_activation(1.2),0)
        with self.assertRaises(ValueError):
            M.analytic_activation(float("nan"))
        with self.assertRaises(ValueError):
            M.activation_at(.25,.123)

    def test_exclusive_output_rejects_empty_directory_and_symlink(self):
        # Must reject stale destinations before expensive physics/import checks.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaises(FileExistsError):
                M.run(existing)
            symlink = root / "link"
            symlink.symlink_to(existing, target_is_directory=True)
            with self.assertRaises(FileExistsError):
                M.run(symlink)
            dangling = root / "dangling"
            dangling.symlink_to(root / "not-there", target_is_directory=True)
            with self.assertRaises(FileExistsError):
                M.run(dangling)
            self.assertEqual(list(existing.iterdir()), [])
            self.assertFalse((root / "not-there").exists())

    def test_failed_numeric_gate_cannot_emit_playable_preview(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(M.EXP26.EXP9, "write_listening_wav") as writer:
                for checks in ({}, {"frozen_B0": False},
                               {"frozen_B0": True, "trajectory_step": False}):
                    digest, gain = M.publish_listening_wav(
                        Path(d), np.zeros(16), checks)
                    self.assertIsNone(digest)
                    self.assertIsNone(gain)
                writer.assert_not_called()
                self.assertFalse((Path(d) / "R1_listen.wav").exists())

    def test_passing_gate_preview_is_byte_hashed(self):
        with tempfile.TemporaryDirectory() as d:
            def fake_writer(path, _pressure):
                path.write_bytes(b"diagnostic-test-only")
                return 1.5
            with mock.patch.object(M.EXP26.EXP9, "write_listening_wav",
                                   side_effect=fake_writer) as writer:
                digest, gain = M.publish_listening_wav(
                    Path(d), np.ones(16), {"frozen_B0": True})
                self.assertEqual(gain, 1.5)
                self.assertEqual(digest, __import__("hashlib").sha256(
                    b"diagnostic-test-only").hexdigest())
                writer.assert_called_once()

    def test_execution_provenance_binds_actual_sources(self):
        receipt = M.source_provenance()
        self.assertRegex(receipt["git_head"], r"^[0-9a-f]{40}$")
        files = receipt["source_sha256"]
        self.assertIn("experiments/036_v4a_one_run_roundtrip/run.py", files)
        self.assertIn("experiments/029_task_field_embodied_infeasibility/run.py", files)
        for digest in files.values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_prepared_body_uses_shared_geometry(self):
        prepared=M.body()
        rest=prepared.rest_state
        peak=M.geometry_at(rest,.5,M.PRIMARY_STEP)
        expected=M.EXP27.realize_task_geometry(rest,1.0,cavity_id=rest.cavity_id)
        np.testing.assert_allclose(
            M.EXP26.geometry_areas(peak),M.EXP26.geometry_areas(expected),
            rtol=1e-12,atol=1e-15)
        for t in (0,1):
            np.testing.assert_allclose(M.EXP26.geometry_areas(
                M.geometry_at(rest,t,M.PRIMARY_STEP)),
                M.EXP26.geometry_areas(rest),rtol=1e-12,atol=1e-15)

    def test_one_uninterrupted_lf_phase(self):
        source,cycles=M.full_lf_source()
        self.assertEqual(source.shape,(48000,))
        self.assertTrue(np.isfinite(source).all())
        self.assertTrue(np.all(np.diff(cycles)>0))
        self.assertLess(M.source_cycle_jump(source),.01)
        self.assertAlmostEqual(np.max(source),M.EXP13.SOURCE_PEAK_M3_S)
        # No reset of oscillator at the reversal.
        self.assertAlmostEqual(cycles[24000],50.0,places=10)


if __name__=="__main__":
    unittest.main()
