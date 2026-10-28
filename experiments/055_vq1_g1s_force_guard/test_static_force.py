"""Independent small analytic and adversarial oracles for G1-S algebra."""
import math
import unittest
from dataclasses import replace
from static_force import (
    PressureDrop, SurfacePatch, PressureReference,
    ScientificHold, static_force,
)

S = "synthetic_control"
def d(tap, wall, drop, unc=0):
    return PressureDrop(tap, wall, drop, unc, S)
def p(tap, wall, area, projection):
    return SurfacePatch(tap, wall, area, projection)
def ref(p0=100, ext=0, u0=0, ue=0):
    return PressureReference(p0, ext, u0, ue)


class StaticForceTests(unittest.TestCase):
    def test_single_patch_signed_traction(self):
        z = static_force([d(6, "FW", 25)], [p(6, "FW", .1, 1)], ref())
        self.assertAlmostEqual(z.force_n, 7.5)
        self.assertEqual(z.status, "ALGEBRA_ONLY_NOT_SOURCE_OR_FORCE_VALIDATED")
        reverse = static_force([d(6, "FW", 25)], [p(6, "FW", .1, -1)], ref())
        self.assertAlmostEqual(reverse.force_n, -7.5)

    def test_equal_pressure_opposing_patches_cancel(self):
        z = static_force(
            [d(6, "FW", 10), d(6, "NFW", 10)],
            [p(6, "FW", .1, 1), p(6, "NFW", .1, -1)], ref()
        )
        self.assertAlmostEqual(z.force_n, 0)

    def test_separate_wall_drops_have_signed_effect(self):
        z = static_force(
            [d(6, "FW", 10), d(6, "NFW", 20)],
            [p(6, "FW", .1, 1), p(6, "NFW", .1, -1)], ref()
        )
        self.assertAlmostEqual(z.force_n, 1)

    def test_common_gauge_shift(self):
        samples = [d(6, "FW", 21)]
        walls = [p(6, "FW", .01, .5)]
        a = static_force(samples, walls, ref(100, 3))
        b = static_force(samples, walls, ref(107, 10))
        self.assertEqual(a.force_n, b.force_n)

    def test_common_mode_reference_bound_not_rss(self):
        z = static_force([d(6, "FW", 0, 2), d(7, "FW", 0, 4)],
                         [p(6, "FW", .1, 1), p(7, "FW", .2, 1)],
                         ref(100, 0, 3, 5))
        self.assertAlmostEqual(z.conservative_half_width_n,
                               .3*(3+5)+.1*2+.2*4)

    def test_opposite_weights_cancel_shared_gauge_uncertainty(self):
        z = static_force([d(6, "FW", 10, 2), d(6, "NFW", 10, 2)],
                         [p(6, "FW", .1, 1), p(6, "NFW", .1, -1)],
                         ref(100, 0, 10, 10))
        self.assertAlmostEqual(z.conservative_half_width_n, .4)

    def test_missing_reference_and_empty_measurements(self):
        for data, surfaces, reference in [
            ([d(6,"FW",2)], [p(6,"FW",1,1)], None),
            ([], [p(6,"FW",1,1)], ref()),
            ([d(6,"FW",2)], [], ref()),
        ]:
            with self.subTest(data=data, reference=reference), self.assertRaises(ScientificHold):
                static_force(data, surfaces, reference)

    def test_tap_wall_mismatch_and_unused_data(self):
        for data, surfaces in [
            ([d(6,"FW",1)], [p(6,"NFW",.1,1)]),
            ([d(6,"FW",1)], [p(7,"FW",.1,1)]),
            ([d(6,"FW",1),d(7,"FW",3)], [p(6,"FW",.1,1)]),
            ([d(6,"FW",1),d(6,"FW",1)], [p(6,"FW",.1,1)]),
            ([d(6,"FW",1)], [p(6,"FW",.1,1),p(6,"FW",.1,1)]),
        ]:
            with self.subTest(data=data, surfaces=surfaces), self.assertRaises(ScientificHold):
                static_force(data, surfaces, ref())

    def test_invalid_dimensions_geometry_and_units(self):
        original_d = d(6, "FW", 2)
        original_p = p(6, "FW", .1, 1)
        bad_d = [
            replace(original_d, drop_pa=float("nan")),
            replace(original_d, uncertainty_pa=-1),
            replace(original_d, source_kind="model_reconstruction"),
            replace(original_d, tap_id=True),
            replace(original_d, wall="UNKNOWN"),
        ]
        bad_p = [
            replace(original_p, area_m2=0),
            replace(original_p, area_m2=-1),
            replace(original_p, projection=1.1),
            replace(original_p, area_m2=float("inf")),
            replace(original_p, projection=True),
        ]
        for sample in bad_d:
            with self.subTest(sample=sample), self.assertRaises(ScientificHold):
                static_force([sample], [original_p], ref())
        for patch in bad_p:
            with self.subTest(patch=patch), self.assertRaises(ScientificHold):
                static_force([original_d], [patch], ref())

    def test_bad_gauge_uncertainty_or_nonfinite(self):
        for invalid in [ref(float("inf")), ref(100, 0, -1), ref(100, float("nan"))]:
            with self.subTest(invalid=invalid), self.assertRaises(ScientificHold):
                static_force([d(6,"FW",1)], [p(6,"FW",1,1)], invalid)

    def test_moving_wall_explicitly_refused(self):
        with self.assertRaisesRegex(ScientificHold, "G1-D"):
            static_force([d(6,"FW",1)], [p(6,"FW",1,1)], ref(), static_only=False)

    def test_missing_real_pressure_is_scientific_hold(self):
        with self.assertRaises(ScientificHold):
            static_force([], [p(6,"FW",1,1)], ref())

    def test_parameterized_analytic_controls(self):
        # No implicit mass, stiffness, imposed frequency or waveform.
        for base in [-500, 0, 100, 800]:
            with self.subTest(base=base):
                for drop in [0, 10, 100]:
                    z = static_force([d(11, "NFW", drop)],
                                     [p(11, "NFW", .03, -.25)],
                                     ref(base, -50))
                    self.assertAlmostEqual(z.force_n, (base-drop+50)*(-.0075))


if __name__ == "__main__":
    unittest.main()
