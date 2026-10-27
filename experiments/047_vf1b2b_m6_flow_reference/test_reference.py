"""Independent stdlib tests for VF-1B2b published M6 transfer sentinel."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference import (
    TABLE, TABLE_SHA256, SHAPES, PRESSURES_KPA, FLOW_ACCURACY_CM3_S,
    A_MIN_M2, RHO_KG_M3, CD_ASSUMED,
    read_m6_table, toy_flow, accuracy_interval_ratio, compare, audit_comparison,
)


class M6PublishedReference(unittest.TestCase):
    def test_original_exact_bytes_are_pinned(self):
        self.assertEqual(hashlib.sha256(TABLE.read_bytes()).hexdigest(), TABLE_SHA256)

    def test_12_published_experimental_values_are_not_cfd(self):
        # Hardcoded direct independent comparison with M6 2010 Table 2 (experimental columns).
        expected = (
            (294., (257.8, 255.6, 277.8)),
            (491., (344.4, 333.3, 366.7)),
            (981., (488.9, 477.8, 522.2)),
            (1472., (611.1, 588.9, 633.3)),
        )
        measured = read_m6_table()
        self.assertEqual(len(measured), 4)
        for row, (dp, flows_cm3_s) in zip(measured, expected):
            self.assertAlmostEqual(row["delta_p_pa"], dp, delta=1e-10)
            for shape, expected_cm3_s in zip(SHAPES, flows_cm3_s):
                self.assertAlmostEqual(
                    row["q_measured_m3_s"][shape] * 1e6, expected_cm3_s, delta=1e-9
                )
        self.assertEqual(FLOW_ACCURACY_CM3_S, 6.)
        self.assertAlmostEqual(A_MIN_M2, 1.22e-5, delta=1e-17)

    def test_one_measured_value_tamper_is_detected(self):
        changed = TABLE.read_bytes().replace(b"522.2", b"524.2")
        with self.assertRaisesRegex(ValueError, "SHA256"):
            read_m6_table(changed)

    def test_shape_swap_is_detected(self):
        changed = TABLE.read_bytes().replace(
            b"convergent_10,uniform_0,divergent_10",
            b"divergent_10,uniform_0,convergent_10"
        )
        with self.assertRaises(ValueError):
            read_m6_table(changed)

    def test_unit_confusion_is_detected(self):
        changed = TABLE.read_bytes().replace(b"0.294", b"294.0")
        with self.assertRaises(ValueError):
            read_m6_table(changed)

    def test_missing_reference_is_rejected(self):
        with self.assertRaises(ValueError):
            read_m6_table(b"")


class ToyOracle(unittest.TestCase):
    def test_analytical_sqrt_pressure_and_area_ratio(self):
        for dp in (294., 491., 981., 1472.):
            baseline = 0.7 * 1.22e-5 * (2 * dp / 1.21) ** 0.5
            self.assertAlmostEqual(toy_flow(dp, "uniform_0"), baseline, delta=1e-16)
            self.assertAlmostEqual(toy_flow(dp, "convergent_10"), baseline, delta=1e-16)
            self.assertAlmostEqual(toy_flow(dp, "divergent_10"), 1.2 * baseline, delta=1e-16)
        q294 = toy_flow(294., "uniform_0")
        self.assertAlmostEqual(toy_flow(1472., "uniform_0") / q294,
                               (1472. / 294.) ** .5, delta=1e-14)
        self.assertEqual(toy_flow(0., "uniform_0"), 0.)

    def test_invalid_drive_and_geometry_refusal(self):
        for pressure, shape, cd in (
            (-1., "uniform_0", .7),
            (float("nan"), "uniform_0", .7),
            (981., "impossible", .7),
            (981., "uniform_0", -1.),
            (981., "uniform_0", 1.1),
            (981., "uniform_0", float("inf")),
        ):
            with self.subTest(pressure=pressure, shape=shape, cd=cd):
                with self.assertRaises(ValueError):
                    toy_flow(pressure, shape, cd)

    def test_accuracy_interval_not_false_gaussian_standard_deviation(self):
        low, high = accuracy_interval_ratio(522.2e-6, 477.8e-6)
        self.assertAlmostEqual(low, (522.2 - 6) / (477.8 + 6), delta=1e-12)
        self.assertAlmostEqual(high, (522.2 + 6) / (477.8 - 6), delta=1e-12)
        self.assertLess(low, 522.2 / 477.8)
        self.assertGreater(high, 522.2 / 477.8)
        with self.assertRaises(ValueError):
            accuracy_interval_ratio(1e-6, 477.8e-6)


class NegativeReceiptControls(unittest.TestCase):
    def test_valid_comparison_does_not_claim_m6_geometry(self):
        result = compare()
        self.assertTrue(audit_comparison(result))
        self.assertIs(result["assumptions"]["geometry_match"], False)
        self.assertFalse(result["assumptions"]["pressure_tap_data_available"])
        self.assertEqual(result["g2"], "INDETERMINATE_NO_MATCHED_PRESSURE_TAP_PROFILE_OR_GEOMETRY")
        self.assertEqual(result["g3"], "NOT_APPLICABLE_NO_MOVING_WALL")
        self.assertEqual(result["g4"], "VOICE_NO_GO")
        self.assertGreaterEqual(result["mismatch_counts_out_of_four"]["divergent_10"], 2)
        self.assertEqual(result["transfer_sentinel"], "M6_SHAPE_TRANSFER_DISCREPANCY")

    def test_pressure_sign_poison_rejected(self):
        r = compare()
        r["cases"][0]["delta_p_pa"] = -r["cases"][0]["delta_p_pa"]
        self.assertFalse(audit_comparison(r))

    def test_measured_q_poison_rejected(self):
        r = compare()
        r["cases"][5]["q_measured_m3_s"] *= 1.2
        self.assertFalse(audit_comparison(r))

    def test_fake_geometry_compatibility_rejected(self):
        r = compare()
        r["assumptions"]["geometry_match"] = True
        self.assertFalse(audit_comparison(r))

    def test_forged_absolute_flow_qualification_rejected(self):
        r = compare()
        r["cases"][1]["absolute_comparison_qualified"] = True
        self.assertFalse(audit_comparison(r))

    def test_wrong_ratio_or_wrong_flow_rejected(self):
        for key, new in (("toy_flow_ratio_to_uniform", .9), ("q_toy_m3_s", 1.2)):
            r = compare()
            r["cases"][8][key] = new
            self.assertFalse(audit_comparison(r))

    def test_forged_pressure_profile_g2_rejected(self):
        r = compare()
        r["g2"] = "PASS"
        self.assertFalse(audit_comparison(r))

    def test_aggregate_mismatch_count_poison_rejected(self):
        r = compare()
        r["mismatch_counts_out_of_four"]["divergent_10"] = 0
        self.assertFalse(audit_comparison(r))

    def test_aggregate_verdict_poison_rejected(self):
        r = compare()
        r["transfer_sentinel"] = "NO_M6_DIVERGENT_DISCREPANCY_DETECTED"
        self.assertFalse(audit_comparison(r))

    def test_source_uncertainty_claim_poison_rejected(self):
        r = compare()
        r["source"]["accuracy_is_one_sigma"] = True
        self.assertFalse(audit_comparison(r))

    def test_missing_or_forged_tests_never_certified(self):
        from run import suite_status
        self.assertFalse(suite_status(None)["eligible"])
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            status = Path(folder) / "test_status.json"
            status.write_text('{"schema":"vf1b2b.unittest.v1","passed":true,"exit_code":1}')
            self.assertFalse(suite_status(status)["eligible"])
            status.write_text('{"schema":"vf1b2b.unittest.v1","passed":true,"exit_code":true}')
            self.assertFalse(suite_status(status)["eligible"])


if __name__ == "__main__":
    unittest.main()
