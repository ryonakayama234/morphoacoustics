"""VF-1B2a research-only independent + adversarial tests (stdlib unittest).

These tests verify this *specified* 1D rigid proxy, not glottal CFD/biology.
"""
from __future__ import annotations
from dataclasses import replace
import json
import math
from pathlib import Path
import tempfile
import unittest

from rigid_glottis import RigidGeometry,UnsupportedReverseFlow,solve
from run import audit_independent,suite_receipt

L=0.006
A=3e-5
P=800.
RHO=1.21


class RigidGlottisTests(unittest.TestCase):
    def test_parallel_exact_analytic_volume_flow(self):
        r=solve(RigidGeometry(A,A),p_up_pa=P,discharge_coefficient=0.7)
        q=0.7*A*math.sqrt(2*P/RHO)
        self.assertAlmostEqual(r.volume_flow_m3_s,q,delta=1e-15)
        self.assertAlmostEqual(r.geometric_separation_z_m,L,delta=1e-15)
        self.assertAlmostEqual(r.separation_area_m2,A,delta=1e-15)
        self.assertTrue(audit_independent(r)["passed"])

    def test_divergent_analytic_separation_is_one_fifth_of_channel(self):
        r=solve(RigidGeometry(A,2*A))
        self.assertAlmostEqual(r.geometric_separation_z_m,L/5,delta=1e-15)
        self.assertAlmostEqual(r.separation_area_m2,1.2*A,delta=1e-15)
        self.assertLess(r.samples[0].pressure_pa,0.)
        self.assertEqual(r.samples[-1].pressure_pa,0.)
        self.assertTrue(audit_independent(r)["passed"])

    def test_convergent_separation_at_exit(self):
        r=solve(RigidGeometry(2*A,A))
        self.assertEqual(r.geometric_separation_z_m,L)
        self.assertEqual(r.separation_area_m2,A)
        self.assertGreater(r.samples[0].pressure_pa,0.)

    def test_zero_drive_has_no_active_separation_and_no_flow(self):
        r=solve(RigidGeometry(A,2*A),p_up_pa=0)
        self.assertFalse(r.separation_active)
        self.assertEqual(r.volume_flow_m3_s,0)
        self.assertTrue(all(s.pressure_pa==0 and s.flow_m3_s==0 for s in r.samples))
        self.assertEqual(r.declared_farfield_dissipation_w,0)
        self.assertTrue(audit_independent(r)["passed"])

    def test_flow_scales_as_sqrt_pressure_and_linear_discharge(self):
        geom=RigidGeometry(A,A)
        qa=solve(geom,p_up_pa=400).volume_flow_m3_s
        qb=solve(geom,p_up_pa=800).volume_flow_m3_s
        qc=solve(geom,p_up_pa=800,discharge_coefficient=1).volume_flow_m3_s
        self.assertAlmostEqual(qa/qb,math.sqrt(0.5),delta=1e-14)
        self.assertAlmostEqual(qc/qb,1/0.7,delta=1e-14)

    def test_refining_profile_grid_does_not_change_flow_or_analytic_sep(self):
        geom=RigidGeometry(A,2*A)
        r41=solve(geom,sample_count=41)
        r161=solve(geom,sample_count=161)
        self.assertEqual(r41.volume_flow_m3_s,r161.volume_flow_m3_s)
        self.assertEqual(r41.geometric_separation_z_m,r161.geometric_separation_z_m)
        self.assertEqual(r41.separation_area_m2,r161.separation_area_m2)

    def test_at_separation_pressure_matches_outlet(self):
        r=solve(RigidGeometry(A,2*A),p_down_pa=15.,p_up_pa=815.)
        at_sep=next(s for s in r.samples if abs(s.z_m-L/5)<1e-12)
        self.assertAlmostEqual(at_sep.pressure_pa,15.,delta=1e-8)
        self.assertTrue(all(abs(s.pressure_pa-15.)<1e-8
                            for s in r.samples if s.z_m>r.geometric_separation_z_m))
        self.assertTrue(audit_independent(r)["passed"])

    def test_fixed_wall_does_zero_work_power_bookkeeping_is_named_assumption(self):
        r=solve(RigidGeometry(A,2*A))
        self.assertEqual(r.fixed_wall_power_w,0)
        self.assertEqual(r.bookkeeping_residual_w,0)
        self.assertAlmostEqual(r.reservoir_power_w,800*r.volume_flow_m3_s,delta=1e-12)
        self.assertEqual(r.declared_farfield_dissipation_w,r.reservoir_power_w)

    def test_upstream_offset_pressure_is_not_reinterpreted_as_outlet(self):
        r=solve(RigidGeometry(A,2*A),p_down_pa=30,p_up_pa=830)
        self.assertAlmostEqual(r.volume_flow_m3_s,
             solve(RigidGeometry(A,2*A),p_down_pa=0,p_up_pa=800).volume_flow_m3_s,
             delta=1e-15)
        self.assertAlmostEqual(r.samples[0].pressure_pa,
             solve(RigidGeometry(A,2*A)).samples[0].pressure_pa+30,
             delta=1e-10)

    def test_adversarial_pressure_tamper_is_detected(self):
        r=solve(RigidGeometry(A,2*A))
        points=list(r.samples)
        points[3]=replace(points[3],pressure_pa=points[3].pressure_pa+1.)
        fake=replace(r,samples=tuple(points))
        self.assertFalse(audit_independent(fake)["passed"])

    def test_adversarial_flow_tamper_is_detected(self):
        r=solve(RigidGeometry(A,A))
        fake=replace(r,volume_flow_m3_s=r.volume_flow_m3_s*1.1)
        self.assertFalse(audit_independent(fake)["passed"])
        pts=list(r.samples)
        pts[0]=replace(pts[0],flow_m3_s=pts[0].flow_m3_s+1e-5)
        self.assertFalse(audit_independent(replace(r,samples=tuple(pts)))["passed"])

    def test_adversarial_power_tamper_is_detected(self):
        r=solve(RigidGeometry(A,2*A))
        self.assertFalse(audit_independent(replace(r,declared_farfield_dissipation_w=0))["passed"])
        self.assertFalse(audit_independent(replace(r,fixed_wall_power_w=1e-3))["passed"])
        self.assertFalse(audit_independent(replace(r,bookkeeping_residual_w=1e-3))["passed"])

    def test_reverse_flow_is_explicitly_unsupported(self):
        with self.assertRaisesRegex(UnsupportedReverseFlow,"UNSUPPORTED_REVERSE_FLOW"):
            solve(RigidGeometry(A,A),p_up_pa=0,p_down_pa=100)

    def test_parameter_refusals_nonpositive_nonfinite_and_bool(self):
        for invalid in (0.,-1.,float("nan"),float("inf"),True,False):
            with self.assertRaises(ValueError):
                RigidGeometry(invalid,A)
            with self.assertRaises(ValueError):
                RigidGeometry(A,invalid)
            with self.assertRaises(ValueError):
                RigidGeometry(A,A,invalid)
            with self.assertRaises(ValueError):
                solve(RigidGeometry(A,A),rho_kg_m3=invalid)
            with self.assertRaises(ValueError):
                solve(RigidGeometry(A,A),discharge_coefficient=invalid)
            with self.assertRaises(ValueError):
                solve(RigidGeometry(A,A),p_up_pa=invalid)
        for invalid in (1.1,2.):
            with self.assertRaises(ValueError):
                solve(RigidGeometry(A,A),discharge_coefficient=invalid)

    def test_invalid_grid_and_sample_location_refused(self):
        for n in (0,1,2,-1,3.5,True):
            with self.assertRaises(ValueError):
                solve(RigidGeometry(A,A),sample_count=n)
        geom=RigidGeometry(A,A)
        for z in (-1,geom.length_m+0.001,float("nan")):
            with self.assertRaises(ValueError):
                geom.area(z)

    def test_independent_pytest_like_receipt_refuses_false_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"status.json"
            self.assertFalse(suite_receipt(p)["eligible"])
            for o in (
              {"schema":"vf1b2a.unittest.v1","passed":True,"exit_code":False},
              {"schema":"vf1b2a.unittest.v1","passed":1,"exit_code":0},
              {"schema":"vf1b2a.unittest.v1","passed":True,"exit_code":1},
              {"schema":"vf1a.science-pytest.v1","passed":True,"exit_code":0},
              {"schema":"vf1b2a.unittest.v1","passed":False,"exit_code":0},
            ):
                p.write_text(json.dumps(o),encoding="utf-8")
                self.assertFalse(suite_receipt(p)["eligible"])
            p.write_text("not json",encoding="utf-8")
            self.assertFalse(suite_receipt(p)["eligible"])
            p.write_text(json.dumps({"schema":"vf1b2a.unittest.v1",
                                     "passed":True,"exit_code":0}),encoding="utf-8")
            self.assertTrue(suite_receipt(p)["eligible"])


if __name__=="__main__":
    unittest.main()
