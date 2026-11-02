"""Prospective controls from EXPERIMENT.md; standard-library unittest."""
from __future__ import annotations
from dataclasses import replace
import copy
import math
import unittest
from solver import Fixture, midpoint_linear_force, simulate
from audit import audit


class R0Tests(unittest.TestCase):
    def test_frozen_fixture_passive_and_lossless(self):
        for f in (Fixture(), replace(Fixture(), d_L_Ns_m=0, d_U_Ns_m=0)):
            report = audit(simulate(f, 1e-6))
            self.assertLessEqual(abs(report["energy_residual_J"]), 3e-10)
            self.assertLessEqual(report["energy_residual_relative"], 5e-4)

    def test_identically_static(self):
        f = replace(Fixture(), x_L0_m=0, x_U0_m=0)
        a = simulate(f, 4e-6)
        audit(a)
        for s in a["samples"]:
            self.assertLessEqual(max(abs(i) for i in s["x_m"]), 1e-14)
            self.assertLessEqual(max(abs(i) for i in s["v_m_s"]), 1e-9)
            self.assertAlmostEqual(s["p_abs_Pa"], f.P0_abs_Pa, places=8)

    def test_raw_trace_tampering_rejected(self):
        a = simulate(Fixture(), 2e-6)
        b = copy.deepcopy(a)
        b["samples"][len(b["samples"]) // 2]["p_abs_Pa"] += 1e-4
        with self.assertRaisesRegex(ValueError, "RAW_TRACE"):
            audit(b)
        c = copy.deepcopy(a)
        c["samples"][len(c["samples"]) // 2]["rho_kg_m3"] *= 1.0001
        with self.assertRaisesRegex(ValueError, "RAW_TRACE"):
            audit(c)

    def test_domain_refusals(self):
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_CONTACT"):
            simulate(replace(Fixture(), x_L0_m=-0.00021), 1e-6)
        with self.assertRaisesRegex(ValueError, "INVALID_MATERIAL"):
            simulate(replace(Fixture(), d_L_Ns_m=-0.01), 1e-6)
        with self.assertRaisesRegex(ValueError, "INVALID_TIME"):
            simulate(Fixture(), -1e-6)

    def test_spatial_force_oracle(self):
        f = Fixture()
        expect_L = f.ell_m*f.L_g_m*(100+120/3)
        expect_U = f.ell_m*f.L_g_m*(100+2*120/3)
        errs = []
        for n in [8, 16, 32]:
            fl, fu = midpoint_linear_force(n, 100, 120, f.L_g_m, f.ell_m)
            errs.append(max(abs(fl-expect_L), abs(fu-expect_U)))
            self.assertLessEqual(abs((fl-fu) + f.ell_m*f.L_g_m*120/3), 2*errs[-1]+1e-14)
        self.assertGreaterEqual(errs[0]/errs[1], 3)
        self.assertGreaterEqual(errs[1]/errs[2], 3)
        fl, fu = midpoint_linear_force(16, 100, -120, f.L_g_m, f.ell_m)
        self.assertLessEqual(abs((fl-fu) - f.ell_m*f.L_g_m*120/3), 2*errs[1]+1e-14)

    def test_convergence(self):
        f = Fixture()
        x4 = simulate(f, 4e-6)["samples"][-1]
        x2 = simulate(f, 2e-6)["samples"][-1]
        x1 = simulate(f, 1e-6)["samples"][-1]
        resolved = 0
        for k, floor in [("x_m", 1e-14), ("v_m_s", 1e-9)]:
            for i in [0, 1]:
                d4 = abs(x4[k][i] - x2[k][i])
                d2 = abs(x2[k][i] - x1[k][i])
                if d4 > floor:
                    resolved += 1
                    self.assertLessEqual(d2, d4/8)
        self.assertGreater(resolved, 0, "No convergent components above floor")


if __name__ == "__main__":
    unittest.main()
