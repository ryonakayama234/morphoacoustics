"""EL-RP1 B2 numerical challenge against previously frozen 16-row JS-wave oracle."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import replace
import importlib
from pathlib import Path
import subprocess
import sys
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EXPERIMENT=ROOT/"experiments/045_el_rp1_receiver_port"
sys.path.insert(0,str(EXPERIMENT))
qual=importlib.import_module("qualifier")
coupler=importlib.import_module("coupler")
audit=importlib.import_module("audit_b")


def case(row):
    a,l,f=row[:3]
    return qual.SyntheticReferencePort(
        1+0j,13834333.333333334,27668666.666666668,a,l,f)


class TestElRp1GateB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle=audit.load_oracle()

    def test_b0_frozen_git_blob_and_strict_16_by_15(self):
        self.assertEqual(len(self.oracle["rows"]),16)
        self.assertEqual(len(self.oracle["fields"]),15)
        self.assertEqual(audit.validate_oracle(self.oracle),self.oracle["rows"])

    def test_b0_generator_cross_language_byte_regeneration(self):
        # Node is an independently authored traveling-wave calculation,
        # rather than a call back into the Python Core model.
        try:
            proc=subprocess.run(
                ["node",str(EXPERIMENT/"rebuild_b0.mjs")],
                capture_output=True,check=True,timeout=20)
        except FileNotFoundError:
            self.skipTest("Node.js not present locally; GitHub CI checks it")
        self.assertEqual(proc.stdout,(EXPERIMENT/"b0_wave_oracle_16.json").read_bytes())

    def test_e2_all_sixteen_ports_match_independent_oracle_and_conserve_power(self):
        for idx,row in enumerate(self.oracle["rows"]):
            with self.subTest(fixture=idx):
                spec=case(row)
                actual=coupler.solve_port(spec)
                audit.compare_row(row,actual)
                self.assertLessEqual(abs(actual.residual_source_boundary_pa),1e-10)
                self.assertLessEqual(abs(actual.residual_terminal_boundary_pa),1e-10)
                self.assertLessEqual(abs(actual.residual_matrix_pressure_pa),1e-10)
                self.assertLessEqual(abs(actual.residual_matrix_flow_m3_s)*actual.zc_pa_s_m3,1e-10)
                power_scale=max(1e-12,abs(actual.power_source_w))
                self.assertLessEqual(abs(actual.residual_source_energy_w)/power_scale,1e-10)
                self.assertLessEqual(abs(actual.residual_tube_energy_w)/power_scale,1e-10)
                self.assertGreaterEqual(actual.power_source_w,-1e-13)
                self.assertGreaterEqual(actual.power_terminal_w,-1e-13)

    def test_e3_reference_plane_split_matches_core_original(self):
        from morphoacoustics.acoustics.uniform_tube import UniformTube
        for idx,row in enumerate(self.oracle["rows"]):
            with self.subTest(fixture=idx):
                e=case(row)
                full=coupler.solve_port(e)
                split=coupler.solve_port(e,segment_lengths_m=(.4*e.length_m,.6*e.length_m))
                audit.compare_row(row,split)
                zc=full.zc_pa_s_m3
                def normalized(m):
                    result=m.copy()
                    result[0,1]/=zc
                    result[1,0]*=zc
                    return result
                one=UniformTube(e.length_m,e.area_m2,
                                air_density_kg_m3=e.air_density_kg_m3,
                                sound_speed_m_s=e.sound_speed_m_s).transfer_matrix(e.frequency_hz)
                t1=UniformTube(.4*e.length_m,e.area_m2,
                               air_density_kg_m3=e.air_density_kg_m3,
                               sound_speed_m_s=e.sound_speed_m_s).transfer_matrix(e.frequency_hz)
                t2=UniformTube(.6*e.length_m,e.area_m2,
                               air_density_kg_m3=e.air_density_kg_m3,
                               sound_speed_m_s=e.sound_speed_m_s).transfer_matrix(e.frequency_hz)
                self.assertLessEqual(np.max(np.abs(normalized(one)-normalized(t1@t2))),1e-11)
                self.assertLessEqual(abs(full.pL_pa-split.pL_pa),1e-11)
                self.assertLessEqual(abs(full.p0_pa-split.p0_pa),1e-11)
                self.assertLessEqual(abs(full.u0_m3_s-split.u0_m3_s)*zc,1e-11)
                self.assertLessEqual(abs(full.uL_m3_s-split.uL_m3_s)*zc,1e-11)

    def test_audit_refuses_truncated_extra_and_mutated_reference(self):
        for mutation in ("truncated","long","nan","missing","wrong_impedance","duplicated"):
            with self.subTest(mutation=mutation):
                changed=deepcopy(self.oracle)
                if mutation=="truncated":
                    changed["rows"]=[r[:3] for r in changed["rows"]]
                elif mutation=="long":
                    changed["rows"][0].append(0.)
                elif mutation=="nan":
                    changed["rows"][0][4]=float("nan")
                elif mutation=="missing":
                    changed["rows"].pop()
                elif mutation=="wrong_impedance":
                    changed["fixed"]["source_impedance_pa_s_m3"]*=2
                elif mutation=="duplicated":
                    changed["rows"][0]=changed["rows"][1][:]
                with self.assertRaises(audit.OracleError):
                    audit.validate_oracle(changed)

    def test_mutated_port_and_power_observations_caught(self):
        row=self.oracle["rows"][5]
        actual=coupler.solve_port(case(row))
        mutants=[
            replace(actual,pL_pa=-actual.pL_pa),
            replace(actual,u0_m3_s=-actual.u0_m3_s),
            replace(actual,p0_pa=actual.p0_pa.conjugate()),
            replace(actual,power_source_w=actual.power_terminal_w),
            replace(actual,power_source_resistor_loss_w=0),
        ]
        for item in mutants:
            with self.subTest(item=repr(item)),self.assertRaises(audit.OracleError):
                audit.compare_row(row,item)

    def test_no_measured_human_reinterpretation_and_bad_split(self):
        with self.assertRaises(qual.ResearchRefusal) as ctx:
            coupler.solve_port(qual.MeasuredPressureTransfer("a"*64))
        self.assertEqual(ctx.exception.category,"UNIDENTIFIABLE")
        with self.assertRaises(qual.ResearchRefusal) as ctx:
            coupler.solve_port(qual.CalibratedAcousticPort(
                "a"*64,"CANAL_ENTRANCE","SOURCE_EQUIVALENT"))
        self.assertEqual(ctx.exception.category,"UNSUPPORTED")
        for lengths in ((.01,.01),(.025,0),(.01,.01,.005)):
            with self.subTest(lengths=lengths),self.assertRaises(qual.ResearchRefusal):
                coupler.solve_port(case(self.oracle["rows"][0]),segment_lengths_m=lengths)

if __name__=="__main__":
    unittest.main()
