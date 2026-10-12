"""Controls must retain scientific semantics; an A→I→A source is NOT wave concat."""
import importlib.util
import json
import sys
import unittest
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
