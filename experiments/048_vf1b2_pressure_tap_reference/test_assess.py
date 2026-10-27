"""Adversarial Gate-0 tests: passing means NO false p(z) validation."""
import copy
import json
import unittest

from assess import SOURCE, assess_inventory, assess_source


class PressureReferenceGate0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(SOURCE.read_text(encoding="utf-8"))

    def test_known_sources_all_remain_unqualified(self):
        results = assess_inventory(self.inventory)
        self.assertEqual(3, len(results["results"]))
        self.assertEqual("SOURCE_INVENTORY_ONLY", results["gate0"])
        self.assertEqual("VOICE_NO_GO", results["g4"])
        self.assertTrue(all(row["gate0_status"] == "HOLD_NO_NUMERIC_MEASURED_PRESSURE_PROFILE"
                            for row in results["results"]))
        self.assertIn("INDETERMINATE", results["g2"])

    def test_m6_flow_accuracy_cannot_be_pressure_profile(self):
        source = copy.deepcopy(self.inventory["sources"][1])
        self.assertEqual("transverse", source["tap_axis"])
        source["tap_axis"] = "axial"  # would silently conflate M6 with M5
        with self.assertRaises(ValueError):
            assess_source(source)

    def test_forged_doi_rejected(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        source["doi"] = "10.1121/not-original"
        with self.assertRaises(ValueError):
            assess_source(source)

    def test_merely_renaming_flags_cannot_elevate_missing_data(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        for flag in ("tap_coordinate_map_audited", "reference_and_sign_audited",
                     "geometry_and_boundary_matched_to_candidate",
                     "uncertainty_and_digitization_audited"):
            source[flag] = True
        self.assertEqual("HOLD_NO_NUMERIC_MEASURED_PRESSURE_PROFILE",
                         assess_source(source)["gate0_status"])

    def test_invented_unattributed_sample_rejected(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        source["measured_pressure_samples"] = [{"tap_id": "6", "position_m": 0.00211,
                                                "pressure_pa": -150}]
        with self.assertRaises(ValueError):
            assess_source(source)

    def test_nonfinite_pressure_rejected(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        source["measured_pressure_samples"] = [self.sample(6, pressure=float("nan"))]
        with self.assertRaises(ValueError):
            assess_source(source)

    def test_nonpositive_uncertainty_rejected(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        source["measured_pressure_samples"] = [self.sample(6, uncertainty=0)]
        with self.assertRaises(ValueError):
            assess_source(source)

    def test_two_coordinate_anchors_do_not_make_pressure_profile(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        source["measured_pressure_samples"] = [self.sample(6), self.sample(13)]
        self.assertEqual("HOLD_INSUFFICIENT_TAP_PROFILE",
                         assess_source(source)["gate0_status"])

    def test_model_geometry_unqualified_cannot_be_silently_accepted(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        source["measured_pressure_samples"] = [self.sample(6), self.sample(7), self.sample(8)]
        self.assertEqual("HOLD_UNQUALIFIED_COORDINATE_BOUNDARY_OR_UNCERTAINTY",
                         assess_source(source)["gate0_status"])

    def test_even_fully_declared_samples_are_not_physical_validation(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        source["measured_pressure_samples"] = [self.sample(6), self.sample(7), self.sample(8)]
        for flag in ("tap_coordinate_map_audited", "reference_and_sign_audited",
                     "geometry_and_boundary_matched_to_candidate",
                     "uncertainty_and_digitization_audited"):
            source[flag] = True
        result = assess_source(source)
        self.assertEqual("CANDIDATE_READY_FOR_INDEPENDENT_SOURCE_AUDIT", result["gate0_status"])
        self.assertIn("INDETERMINATE", result["g2"])

    def test_duplicate_tap_on_same_wall_rejected(self):
        source = copy.deepcopy(self.inventory["sources"][0])
        source["measured_pressure_samples"] = [self.sample(6), self.sample(6)]
        with self.assertRaises(ValueError):
            assess_source(source)

    def test_incomplete_inventory_rejected(self):
        source = copy.deepcopy(self.inventory)
        source["sources"].pop()
        with self.assertRaises(ValueError):
            assess_inventory(source)

    @staticmethod
    def sample(tap, pressure=-100, uncertainty=1):
        return {"tap_id": str(tap), "position_m": 0.00211 + (tap - 6) * 0.0001,
                "pressure_pa": pressure, "uncertainty_pa": uncertainty,
                "wall_side": "fixed", "original_source_ref": "SYNTHETIC_TEST_ONLY"}


if __name__ == "__main__":
    unittest.main()
