"""Experiment 033 explicit scientific tests, run via unittest discovery in CI."""
from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest

from coupled import GlottalParameters, StrongCoupling, Geometry, PassiveTract, make_model, monotone_root
from run import run, simulate, relative_flow_rms, energy_summary


ORACLE = json.loads(
    (Path(__file__).parent / "wolfram" / "oracle.json").read_text(encoding="utf-8")
)


class TestStrongCoupling(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.summary = run(Path(cls.temp.name) / "result")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_wolfram_first_one_cell_strong_step(self) -> None:
        c = ORACLE["one_cell_fixture"]
        g = Geometry(lengths_m=(c["tract_length_m"],), areas_m2=(c["tract_area_m2"],))
        tract = PassiveTract(geometry=g, subdivisions=1, dt_s=1 / c["sample_rate_hz"])
        coupled = StrongCoupling(tract, feedback=True)
        self.assertAlmostEqual(
            coupled.port_slope_pa_s_m3,
            ORACLE["one_cell_port_slope_pa_s_m3"],
            delta=1e-6,
        )
        result = coupled.step(
            area_m2=c["glottal_area_m2"],
            subglottal_pressure_pa=c["subglottal_pressure_pa"],
        )
        self.assertAlmostEqual(
            result.flow_m3_s, ORACLE["one_cell_first_flow_new_m3_s"], delta=1e-15
        )
        self.assertAlmostEqual(
            result.inlet_pressure_mid_pa,
            ORACLE["one_cell_first_port_pressure_mid_pa"],
            delta=1e-7,
        )
        self.assertLess(abs(result.energy_residual_j), 1e-16)

    def test_all_frozen_gates(self) -> None:
        self.assertTrue(self.summary["all_eligible_gates_pass"], self.summary["gates"])
        self.assertEqual(self.summary["gates"]["G4_exact_closure"], "UNSUPPORTED")
        self.assertEqual(self.summary["gates"]["G4_listening_and_naturalness"], "NOT_TESTED")

    def test_open_loop_geometry_has_identical_source(self) -> None:
        self.assertEqual(
            self.summary["comparisons"]["C0_geometry_relative_flow_rms"], 0.0
        )
        self.assertGreater(
            self.summary["comparisons"]["C1_geometry_relative_flow_rms"], 0.001
        )
        self.assertGreater(
            self.summary["comparisons"]["C0_C1_feedback_relative_flow_rms"], 0.001
        )

    def test_no_early_noncausal_geometry_effect(self) -> None:
        self.assertLess(
            self.summary["comparisons"]["early_geometry_max_abs_flow_difference_m3_s"],
            1e-7,
        )

    def test_midpoint_energy_and_port_equations(self) -> None:
        for key in ("C1_strong_uniform", "C1_strong_constricted"):
            stat = self.summary["conditions"][key]
            self.assertTrue(stat["all_losses_nonnegative"])
            self.assertLess(stat["energy_max_residual_over_total_drive_work"], 1e-9)
            self.assertLess(stat["energy_max_abs_residual_j"], 1e-13)
            self.assertLess(stat["peak_abs_glottal_equation_residual_pa"], 1e-5)

    def test_time_step_refinement(self) -> None:
        self.assertTrue(self.summary["convergence"]["convergence_improves"])
        self.assertLess(
            self.summary["convergence"]["relative_48k_to_96k"],
            self.summary["convergence"]["relative_24k_to_48k"],
        )

    def test_negative_and_zero_drive(self) -> None:
        self.assertTrue(self.summary["gates"]["G2_zero_drive_quiescent"])
        self.assertTrue(self.summary["gates"]["G2_reverse_drive_finite_and_backward"])

    def test_closure_rejected_not_silently_projected(self) -> None:
        model = make_model(feedback=True)
        with self.assertRaisesRegex(NotImplementedError, "CLOSED_GLOTTIS_UNSUPPORTED"):
            model.step(area_m2=0, subglottal_pressure_pa=800)
        with self.assertRaises(ValueError):
            model.step(area_m2=-1, subglottal_pressure_pa=800)
        with self.assertRaises(ValueError):
            model.step(area_m2=3e-5, subglottal_pressure_pa=float("nan"))

    def test_invalid_coefficient_and_root(self) -> None:
        with self.assertRaises(ValueError):
            GlottalParameters(inertance_pa_s2_m3=-1)
        with self.assertRaises(ValueError):
            monotone_root(-1, 1, 3)
        self.assertAlmostEqual(monotone_root(1., 2., -6.), -1.5, delta=1e-14)
        self.assertEqual(monotone_root(2., 0., 4.), 2.)

    def test_existing_core_geometry_adapter(self) -> None:
        from morphoacoustics.physical import Tract1DGeometry, TubeSection

        physical = Tract1DGeometry(
            cavity_id="oral",
            sections=tuple(
                TubeSection(length_m=.017, area_m2=.00015 if k == 5 else .0003)
                for k in range(10)
            ),
        )
        geometry = Geometry.from_tract1d(physical)
        self.assertEqual(geometry, Geometry.middle_constriction())
        self.assertEqual(geometry.total_length_m, .17)

    def test_trace_artifacts_and_replay_prevention(self) -> None:
        path = Path(self.temp.name) / "result"
        self.assertTrue((path / "summary.json").exists())
        self.assertEqual(len(list(path.glob("*.csv"))), 4)
        with self.assertRaisesRegex(ValueError, "fresh empty"):
            run(path)

    def test_matched_parent_exp032_solver_unchanged(self) -> None:
        model = make_model(constricted=True, feedback=True)
        self.assertIsInstance(model.tract, PassiveTract)
        self.assertGreater(model.port_slope_pa_s_m3, 0)
        self.assertAlmostEqual(model.tract.geometry.total_length_m, .17, places=12)


if __name__ == "__main__":
    unittest.main()
