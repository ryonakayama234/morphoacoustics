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
    @staticmethod
    def passing_checks():
        return {name: True for name in (
            "frozen_B0", "source_identity", "analytic_schedule",
            "same_three_tasks", "realized_geometry", "trajectory_step",
            "pressure_and_hop_stability", "single_phase_source",
            "single_run_counts",
        )}

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
                    Path(d), np.ones(16), self.passing_checks())
                self.assertEqual(gain, 1.5)
                self.assertEqual(digest, __import__("hashlib").sha256(
                    b"diagnostic-test-only").hexdigest())
                writer.assert_called_once()

    def test_execution_provenance_binds_actual_sources(self):
        receipt = M.source_provenance()
        self.assertRegex(receipt["git_head"], r"^[0-9a-f]{40}$")
        self.assertIs(receipt["tracked_worktree_clean"], True)
        files = receipt["source_sha256"]
        self.assertIn("experiments/036_v4a_one_run_roundtrip/run.py", files)
        self.assertIn("experiments/029_task_field_embodied_infeasibility/run.py", files)
        for digest in files.values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_frozen_upstream_gate_rechecks_reference_blobs_and_task(self):
        receipt = M.upstream_scientific_preflight()
        self.assertTrue(receipt["pass"], receipt)
        self.assertTrue(all(receipt["frozen_blob_checks"].values()))
        self.assertTrue(all(receipt["v3b_frozen_preflight_checks"].values()))
        self.assertTrue(all(receipt["v3c_frozen_preflight_checks"].values()))
        self.assertTrue(receipt["v3a_task_oracle_match"])

    def test_no_fallback_for_unreachable_task(self):
        start = M.body().rest_state
        creature = M.EXP29.creature_for(
            cavity_id=start.cavity_id, oral_reachable_end=0.70)
        invalid_body = M.EXP29.prepared_for(
            creature=creature, geometry=start, condition="M_minus")
        with mock.patch.object(M.EXP29, "render_with_counter") as render:
            result = M.EXP29.evaluate_condition(invalid_body,
                np.zeros(M.EXP29.AUDITED_WAVEFORM_SAMPLES), label="negative")
            render.assert_not_called()
            self.assertIs(result.feasibility.status,
                          M.EXP29.FeasibilityStatus.INFEASIBLE)
            self.assertEqual(result.acoustic_call_count, 0)
            self.assertIsNone(result.waveform)
            self.assertIsNone(result.endpoint)

    def test_reference_normalized_hop_gate(self):
        candidate = np.array([2.0, -2.0])
        finer_reference = np.array([1.0, -1.0])
        self.assertAlmostEqual(M.hop_stability_ratio(candidate, finer_reference), 1.0)
        # The historical argument order would wrongly normalize against 2x RMS.
        self.assertAlmostEqual(M.EXP12.normalized_rms_difference(
            candidate, finer_reference), 0.5)

    def test_gate_failure_has_registered_scientific_decision(self):
        passing = self.passing_checks()
        self.assertEqual(M.research_decision(passing), "SUPPORT_ONE_RUN_ROUNDTRIP")
        cases = {
            "frozen_B0": "REFERENCE_DRIFT",
            "analytic_schedule": "REPRESENTATION_OR_SCHEDULE_MISMATCH",
            "same_three_tasks": "REPRESENTATION_OR_SCHEDULE_MISMATCH",
            "realized_geometry": "PHYSICAL_ENDPOINT_FAILURE",
            "trajectory_step": "NUMERICALLY_UNSTABLE",
            "pressure_and_hop_stability": "NUMERICALLY_UNSTABLE",
            "source_identity": "SOURCE_OR_PROVENANCE_FAILURE",
            "single_phase_source": "SOURCE_OR_PROVENANCE_FAILURE",
            "single_run_counts": "SOURCE_OR_PROVENANCE_FAILURE",
        }
        for key, expected in cases.items():
            with self.subTest(failed=key):
                checks = passing.copy()
                checks[key] = False
                self.assertEqual(M.research_decision(checks), expected)
        self.assertEqual(M.research_decision({"frozen_B0": False}),
                         "REFERENCE_DRIFT")
        self.assertEqual(M.research_decision({}), "SOURCE_OR_PROVENANCE_FAILURE")
        self.assertEqual(M.research_decision({"frozen_B0": True}),
                         "SOURCE_OR_PROVENANCE_FAILURE")
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(M.EXP26.EXP9, "write_listening_wav") as writer:
                digest, gain = M.publish_listening_wav(
                    Path(d), np.ones(16), {"frozen_B0": True})
                self.assertIsNone(digest)
                self.assertIsNone(gain)
                writer.assert_not_called()

    def test_dirty_tracked_checkout_refuses_physical_execution(self):
        with mock.patch.object(M.subprocess, "run",
                               return_value=mock.Mock(stdout=" M src/morphoacoustics/physical/fake.py\\n")):
            with self.assertRaisesRegex(RuntimeError, "clean Git checkout"):
                M.verified_git_checkout()

    def test_frozen_preflight_failure_writes_gate_receipt_without_audio(self):
        with tempfile.TemporaryDirectory() as d, \\
             mock.patch.object(M, "upstream_scientific_preflight",
                               return_value={"pass": False, "checks": {"oracle": False}}), \\
             mock.patch.object(M, "body") as body, \\
             mock.patch.object(M, "render") as renderer, \\
             mock.patch.object(M.np, "__version__", M.EXP29.AUDITED_NUMPY_VERSION):
            out = Path(d) / "new"
            result = M.run(out)
            self.assertEqual(result["decision"], "REFERENCE_DRIFT")
            self.assertEqual(result["failed_checks"], ["frozen_B0"])
            self.assertFalse(result["preview_available"])
            self.assertEqual(json.loads((out / "summary.json").read_text()), result)
            self.assertFalse((out / "R1_listen.wav").exists())
            self.assertFalse((out / "R1_raw_pressure_pa.npy").exists())
            body.assert_not_called()
            renderer.assert_not_called()

    def test_final_dirty_checkout_never_publishes_playable_wav(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(M, "source_provenance",
                side_effect=RuntimeError("dirty tracked checkout")), \\
                 mock.patch.object(M.EXP26.EXP9, "write_listening_wav") as writer:
                with self.assertRaisesRegex(RuntimeError, "dirty tracked checkout"):
                    M.verified_preview(Path(d), np.ones(16), self.passing_checks())
                writer.assert_not_called()
                self.assertFalse((Path(d) / "R1_listen.wav").exists())

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
