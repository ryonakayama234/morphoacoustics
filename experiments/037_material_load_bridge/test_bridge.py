"""Research EM-1 probes frozen causality, negative control and source isolation."""
import importlib.util
import math
import sys
import unittest
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("em1_bridge",HERE/"run.py")
assert SPEC and SPEC.loader
M=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=M
SPEC.loader.exec_module(M)


class MaterialBridgeTests(unittest.TestCase):
    def test_pinned_reduced_material_fixture(self):
        a,qa,ca=M.realized_body("baseline")
        b,qb,cb=M.realized_body("stiff")
        self.assertEqual(qa.shape,(10,))
        self.assertEqual(cb,ca)
        self.assertGreater(np.linalg.norm(qa-qb),1e-6)
        self.assertTrue(all(sec.area_m2>0 for sec in a.sections))
        self.assertEqual(len(b.sections),10)
        with self.assertRaises(ValueError):
            M.realized_body("new unvalidated preset")

    def test_physical_same_geometry_null(self):
        a,_,_=M.realized_body("baseline")
        r1=M.simulate(a,feedback=True)
        r2=M.simulate(a,feedback=True)
        for key in ("flow_m3_s","inlet_pressure_mid_pa","total_energy_j"):
            self.assertEqual(M.field_bytes(r1,key),M.field_bytes(r2,key))
        energy,passed=M.energy_gate(r1)
        self.assertTrue(passed)
        self.assertLess(energy,1e-10)

    def test_static_oracle(self):
        self.assertAlmostEqual(343/(4*.17),504.4117647058824,places=11)


if __name__=="__main__":
    unittest.main()
