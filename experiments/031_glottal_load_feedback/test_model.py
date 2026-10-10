"""Independent test suite for the experiment-local model; run unittest discover."""
from __future__ import annotations

from dataclasses import replace
import json
import math
from pathlib import Path
import unittest

from glottal_valve import PrescribedValve
from passive_load import Parameters, State, energy, signed_quadratic_root, steady_flow, step
from run import (
    check_energy,
    relative_rms_difference,
    run,
    simulate,
)

ORACLE = json.loads((Path(__file__).resolve().parent / "wolfram" / "oracle.json").read_text())


class TestExperiment031(unittest.TestCase):
    def test_prescribed_area_is_not_prescribed_flow(self) -> None:
        valve = PrescribedValve()
        self.assertEqual(valve.area_at(0), 0)
        self.assertEqual(valve.area_at(0.0065), 0)
        self.assertGreater(valve.area_at(0.00325), 0)
        with self.assertRaises(ValueError):
            valve.area_at(-0.1)

    def test_wolfram_quadratic_coefficient(self) -> None:
        self.assertAlmostEqual(
            Parameters().quadratic_loss_coefficient(3e-5),
            ORACLE["quadratic_loss_coefficient"],
            delta=1e-6,
        )

    def test_wolfram_independent_one_step_cases(self) -> None:
        fixture = ORACLE["fixture"]
        previous = State(
            flow_m3_s=fixture["old_flow_m3_s"],
            chamber_pressure_pa=fixture["old_chamber_pressure_pa"],
        )
        for feedback, family in ((False, "C0_open_loop"), (True, "C1_coupled")):
            for label, resistance in (("low", 2e6), ("high", 8e6)):
                with self.subTest(feedback=feedback, resistance=resistance):
                    params = replace(Parameters(), outlet_resistance_pa_s_m3=resistance)
                    outcome = step(
                        previous,
                        parameters=params,
                        dt_s=fixture["dt_s"],
                        area_m2=fixture["area_m2"],
                        subglottal_pressure_pa=fixture["subglottal_pressure_pa"],
                        feedback=feedback,
                    )
                    exp_flow, exp_pressure = ORACLE["backward_euler_one_step"][f"{family}_{label}"]
                    self.assertAlmostEqual(outcome.state.flow_m3_s, exp_flow, delta=1e-16)
                    self.assertAlmostEqual(outcome.state.chamber_pressure_pa, exp_pressure, delta=1e-10)
                    self.assertLess(abs(outcome.budget.residual_j), 1e-18)

    def test_steady_positive_and_negative_flow(self) -> None:
        params = Parameters()
        for label, resistance in (("low", 2e6), ("high", 8e6)):
            p = replace(params, outlet_resistance_pa_s_m3=resistance)
            state = steady_flow(area_m2=3e-5, subglottal_pressure_pa=800, parameters=p)
            reference = ORACLE["steady_coupled"][label]
            self.assertAlmostEqual(state.flow_m3_s, reference[0], delta=1e-16)
            self.assertAlmostEqual(state.chamber_pressure_pa, reference[1], delta=1e-10)
            reverse = steady_flow(area_m2=3e-5, subglottal_pressure_pa=-800, parameters=p)
            self.assertAlmostEqual(reverse.flow_m3_s, -state.flow_m3_s, delta=1e-16)
            self.assertAlmostEqual(reverse.chamber_pressure_pa, -state.chamber_pressure_pa, delta=1e-10)

    def test_signed_root_analytical_limits_and_extreme_area(self) -> None:
        self.assertEqual(signed_quadratic_root(2, 0, -10), -5)
        self.assertEqual(signed_quadratic_root(2, 1e10, 0), 0)
        self.assertAlmostEqual(signed_quadratic_root(3, 1e-15, 6), 2, delta=1e-12)
        self.assertAlmostEqual(signed_quadratic_root(3, 2, -14), -2, delta=1e-14)
        extremely_small_area = 1e-60
        p = Parameters()
        result = step(State(), parameters=p, dt_s=1/48000, area_m2=extremely_small_area,
                      subglottal_pressure_pa=800, feedback=True)
        self.assertTrue(math.isfinite(result.state.flow_m3_s))
        self.assertLess(abs(result.state.flow_m3_s), 1e-50)

    def test_exact_closure_and_projection_loss(self) -> None:
        previous = State(flow_m3_s=1.7e-5, chamber_pressure_pa=321.0)
        for feedback in (False, True):
            outcome = step(previous, parameters=Parameters(), dt_s=1/48000,
                           area_m2=0.0, subglottal_pressure_pa=800, feedback=feedback)
            self.assertTrue(outcome.aperture_closed)
            self.assertEqual(outcome.state.flow_m3_s, 0.0)
            self.assertGreater(outcome.budget.closure_projection_loss_j, 0)
            self.assertLess(abs(outcome.budget.residual_j), 1e-18)
            self.assertLess(energy(outcome.state, Parameters()), energy(previous, Parameters()))

    def test_invalid_parameters_and_inputs_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Parameters(compliance_m3_pa=-1)
        with self.assertRaises(ValueError):
            step(State(), parameters=Parameters(), dt_s=0, area_m2=1e-5,
                 subglottal_pressure_pa=800, feedback=True)
        with self.assertRaises(ValueError):
            step(State(), parameters=Parameters(), dt_s=1e-5, area_m2=-1,
                 subglottal_pressure_pa=800, feedback=True)

    def test_g1_causal_isolation_and_g0_energy(self) -> None:
        summary = run()
        self.assertTrue(summary["pass_all_eligible_gates"])
        self.assertEqual(summary["comparisons"]["negative_control_C0_low_vs_high_relative_flow_rms"], 0)
        self.assertGreater(summary["comparisons"]["C1_low_vs_high_relative_flow_rms"], 0.01)
        self.assertEqual(summary["gates"]["G2_real_tract_geometry"], "UNSUPPORTED")
        self.assertEqual(summary["gates"]["G3_listening_naturalness"], "NOT_TESTED")
        self.assertTrue(ORACLE["energy_residual_symbolic"] == 0)
        self.assertTrue(ORACLE["closure_projection_energy_residual_symbolic"] == 0)
        self.assertGreater(summary["conditions"]["C0_open_loop_high"]["max_abs_nonreciprocal_work_j"], 0)

    def test_timestep_convergence(self) -> None:
        valve, params = PrescribedValve(), Parameters()
        t = 0.08
        coarse = simulate(parameters=params, valve=valve, feedback=True,
                          sample_rate_hz=24000, duration_s=t)
        medium = simulate(parameters=params, valve=valve, feedback=True,
                          sample_rate_hz=48000, duration_s=t)
        fine = simulate(parameters=params, valve=valve, feedback=True,
                        sample_rate_hz=96000, duration_s=t)
        e1 = relative_rms_difference(coarse, medium[1::2])
        e2 = relative_rms_difference(medium, fine[1::2])
        self.assertLess(e2, e1)
        self.assertLess(e1, 0.02)
        self.assertLess(e2, 0.01)

    def test_coupled_balance_for_negative_driving_pressure(self) -> None:
        params = Parameters()
        valve = replace(PrescribedValve(), subglottal_pressure_pa=-800)
        rows = simulate(parameters=params, valve=valve, feedback=True, duration_s=0.04)
        checks = check_energy(rows)
        self.assertTrue(checks["pass_residual"])
        self.assertTrue(checks["all_loss_terms_nonnegative"])
        self.assertTrue(any(float(row["flow_m3_s"]) < 0 for row in rows))


if __name__ == "__main__":
    unittest.main()
