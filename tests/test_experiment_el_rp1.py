"""EL-RP1 Gate A E0/E1 tests, prereg a33c8c6. No third-party runtime deps."""
from dataclasses import replace
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "experiments/045_el_rp1_receiver_port/qualifier.py"
spec = importlib.util.spec_from_file_location("el_rp1_qualifier_under_test", path)
assert spec is not None and spec.loader is not None
rp = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rp
spec.loader.exec_module(rp)
HASH = "a"*64


def port():
    return rp.SyntheticReferencePort(1+0j, 13834333.333333334,
                                     27668666.666666668, 4e-5, .025, 2200)


class TestElRp1GateA(unittest.TestCase):
    def test_e0_independent_fraction_oracle(self):
        for zl, expected in ((Fraction(1), (Fraction(1), Fraction(1))),
                             (Fraction(2), (Fraction(1), Fraction(4,3)))):
            for (ps, zs), truth in zip(((1,0),(2,1)), expected, strict=True):
                oracle = Fraction(ps)*zl/(Fraction(zs)+zl)
                self.assertEqual(oracle, truth)
                self.assertLessEqual(abs(rp.normalized_one_port_pressure(
                    ps, zs, float(zl))-float(oracle)), 1e-14)
        delta = rp.normalized_one_port_pressure(2,1,2)-rp.normalized_one_port_pressure(1,0,2)
        self.assertAlmostEqual(delta, 1/3, places=14)

    def test_e0_full_reference_plane_still_does_not_identify_source(self):
        measured = rp.MeasuredPressureTransfer(
            HASH, "CANAL_ENTRANCE", "FREE_FIELD", "STORED_CHANNEL_RATIO", "ZL_KNOWN")
        result = rp.qualify(measured, "PREDICT_CHANGED_LOAD",
                            requested_input_plane="CANAL_ENTRANCE")
        self.assertFalse(result.accepted)
        self.assertEqual(result.code, "UNIDENTIFIABLE")
        self.assertEqual(result.field, "source_impedance_pa_s_m3")

    def test_e1_inspection_and_synthetic_eligibility(self):
        for item in (rp.MeasuredPressureTransfer(HASH),
                     rp.CalibratedAcousticPort(HASH,"CANAL_ENTRANCE","SOURCE_EQUIVALENT"),
                     rp.UnqualifiedObservation("missing microphone endpoint"),port()):
            with self.subTest(type=type(item).__name__):
                self.assertEqual(rp.qualify(item,"INSPECT_METADATA").status,
                                 "INSPECTABLE_METADATA")
        self.assertEqual(rp.qualify(port(),"PREDICT_CHANGED_LOAD").status,
                         "SYNTHETIC_GATE_B_ELIGIBLE")

    def test_e1_pressure_only_calibrated_unqualified_reject(self):
        for item, code in (
            (rp.MeasuredPressureTransfer(HASH), "UNIDENTIFIABLE"),
            (rp.CalibratedAcousticPort(HASH,"CANAL_ENTRANCE","SOURCE_EQUIVALENT"),
             "UNSUPPORTED"),
            (rp.UnqualifiedObservation("not measured"),"UNIDENTIFIABLE"),
        ):
            with self.subTest(item=repr(item)):
                self.assertEqual(rp.qualify(item,"PREDICT_CHANGED_LOAD").code,code)

    def test_e1_fourteen_mutations_and_fail_closed_reasons(self):
        s=port()
        cases=[
            ("unknown-plane",rp.MeasuredPressureTransfer(HASH),"PREDICT_CHANGED_LOAD",
             "UNIDENTIFIABLE",None),
            ("wrong-target",s,"PREDICT_CHANGED_LOAD","INVALID","DRUM_PLANE"),
            ("missing-Zs",replace(s,source_impedance_pa_s_m3=None),
             "PREDICT_CHANGED_LOAD","INVALID",None),
            ("total-instead-source",replace(s,pressure_kind="TOTAL"),
             "PREDICT_CHANGED_LOAD","UNSUPPORTED",None),
            ("incident-instead-source",replace(s,pressure_kind="INCIDENT"),
             "PREDICT_CHANGED_LOAD","UNSUPPORTED",None),
            ("normalized-Z",replace(s,impedance_kind="Z_OVER_ZC"),
             "PREDICT_CHANGED_LOAD","UNSUPPORTED",None),
            ("nan",replace(s,source_pressure_pa=complex(float("nan"),0)),
             "PREDICT_CHANGED_LOAD","INVALID",None),
            ("negative-source-impedance",replace(s,source_impedance_pa_s_m3=-1),
             "PREDICT_CHANGED_LOAD","INVALID",None),
            ("zero-terminal-impedance",replace(s,terminal_impedance_pa_s_m3=0),
             "PREDICT_CHANGED_LOAD","INVALID",None),
            ("wrong-phasor",replace(s,phasor_convention="RMS_EXP_MINUS_IWT"),
             "PREDICT_CHANGED_LOAD","UNSUPPORTED",None),
            ("wrong-flow-sign",replace(s,flow_direction="TERMINAL_TO_ENTRANCE"),
             "PREDICT_CHANGED_LOAD","UNSUPPORTED",None),
            ("3d",replace(s,model_dimension="3D"),
             "PREDICT_CHANGED_LOAD","UNSUPPORTED",None),
            ("unknown-union",{"kind":"SYNTHETIC_REFERENCE_PORT"},
             "PREDICT_CHANGED_LOAD","INVALID",None),
            ("rights",rp.MeasuredPressureTransfer(HASH),
             "EXPORT_OR_DISTRIBUTE","RIGHTS_REVIEW_REQUIRED",None),
        ]
        self.assertEqual(len(cases),14)
        for label,item,op,code,plane in cases:
            with self.subTest(mutation=label):
                result=rp.qualify(item,op,requested_input_plane=plane)
                self.assertFalse(result.accepted)
                self.assertEqual(result.code,code)
                self.assertTrue(result.field and result.reason)

    def test_rights_cannot_override_physics(self):
        cleared=rp.MeasuredPressureTransfer(HASH,rights_status="REUSE_CLEARED")
        self.assertEqual(rp.qualify(cleared,"PREDICT_CHANGED_LOAD").code,"UNIDENTIFIABLE")
        self.assertEqual(rp.qualify(cleared,"EXPORT_OR_DISTRIBUTE").code,"UNSUPPORTED")
        self.assertEqual(rp.qualify(cleared,"REPRODUCE_MEASURED_CHANNEL").code,"UNSUPPORTED")
        self.assertEqual(rp.qualify(port(),"AUTO_HRTF_MULTIPLY").code,"INVALID")

    def test_invalid_unqualified_and_bounded_domain(self):
        for item,code in (
            (rp.MeasuredPressureTransfer("short"),"INVALID"),
            (rp.UnqualifiedObservation(""),"INVALID"),
            (replace(port(),frequency_hz=0),"INVALID"),
            (replace(port(),frequency_hz=9000),"UNSUPPORTED"),
            (replace(port(),source_impedance_pa_s_m3=1j),"INVALID"),
        ):
            with self.subTest(item=repr(item)):
                self.assertEqual(rp.qualify(item,"INSPECT_METADATA").code,code)

    def test_dimensionless_analytic_input_refusals(self):
        for args in ((1,-1,2),(1,0,0),(float("nan"),0,1),
                     (1,0,float("inf")),(True,0,1)):
            with self.subTest(args=args),self.assertRaises(rp.ResearchRefusal):
                rp.normalized_one_port_pressure(*args)


if __name__=="__main__":
    unittest.main()
