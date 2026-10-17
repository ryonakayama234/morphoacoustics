"""Exploratory Gate A instrument checks; never a prospectively approved Gate B."""
from importlib import util
from pathlib import Path

import numpy as np
import pytest

FILE = Path(__file__).resolve().parents[1] / "experiments/042_nr1a_gate_a_preflight/preflight.py"
spec = util.spec_from_file_location("nr1a_gate_a_preflight", FILE)
assert spec and spec.loader
pre = util.module_from_spec(spec)
spec.loader.exec_module(pre)


def test_full_matrix_12_by_12_and_finite_solution_for_24_fixtures():
    report = pre.run_preflight()
    assert report["status"] == "EXPLORATORY_PRE_GATE_A_NOT_CONFIRMATORY"
    assert len(report["records"]) == 24
    assert report["maximum_condition_2"] < 1e8
    for row in report["records"]:
        assert abs(row["power_residual_w"]) < 1e-12
        assert row["normalized_backward_error_inf"] < 1e-11
        assert set(row["mutant_max_scaled_state_deviation"]) == set(pre.MUTANTS)
        assert set(row["mutant_junction_diagnostics"]) == set(pre.MUTANTS)
        assert row["junction_diagnostics"]["volume_flow_conservation_m3_s"] < 1e-15
        assert row["junction_diagnostics"]["pressure_continuity_pa"] < 1e-10


def test_closed_distal_branch_stays_coupled_upstream():
    state, _, _ = pre.solve("N", 733)
    assert abs(state[11]) < 1e-11  # C.out closed
    assert abs(state[9]) > 1e-3    # C.in remains reactive
    state_m, _, _ = pre.solve("M", 733)
    assert abs(state_m[7]) < 1e-11  # B.out closed
    assert abs(state_m[5]) > 1e-3    # B.in remains reactive


def test_reference_733hz_terminal_powers_exploratory_wolfram_probe():
    target = {"N": (5.3130604780595185e-7, 0),
              "O": (6.1987007903649672e-7, 3.0993503951824836e-7),
              "M": (0, 8.6128929520173005e-8)}
    for case, (mouth, nose) in target.items():
        state, _, _ = pre.solve(case, 733)
        ps = pre.powers(state)
        assert abs(ps[3] - mouth) < 2e-14
        assert abs(ps[5] - nose) < 2e-14


def test_true_mutant_changes_equations_not_merely_output_labels():
    base, rhs = pre.system("O", 733)
    for mutant in pre.MUTANTS:
        altered, altered_rhs = pre.system("O", 733, mutant)
        assert not np.array_equal(base, altered), mutant
        assert np.array_equal(rhs, altered_rhs)


def test_local_quarter_wave_pole_is_not_global_singularity():
    fstar = pre.C_M_S/(4*pre.LENGTHS_M[1])
    state, cond, residual = pre.solve("M", fstar)
    assert np.all(np.isfinite(state))
    assert cond < 1e4
    assert residual < 1e-11
    assert abs(state[4]) < 1e-6  # pressure at junction -> node
    assert abs(state[7]) < 1e-12


@pytest.mark.parametrize("case,f,mutant", [("Z",733,None),("N",-1,None),("N",733,"unlisted")])
def test_unknown_case_frequency_and_mutant_refuse(case, f, mutant):
    with pytest.raises(ValueError):
        pre.system(case, f, mutant)


@pytest.mark.parametrize("case", list(pre.CASES))
@pytest.mark.parametrize("frequency_hz", pre.FREQUENCIES)
@pytest.mark.parametrize("mutant", pre.MUTANTS)
def test_all_120_law_mutations_are_numerically_distinguishable(
    case, frequency_hz, mutant
):
    """Exploratory roundoff-only guard, not Gate A preregistered kill margin."""
    baseline, _, _ = pre.solve(case, frequency_hz)
    corrupted, _, _ = pre.solve(case, frequency_hz, mutant)
    assert pre.state_distinction_passes(baseline, corrupted), (
        case, frequency_hz, mutant
    )


def test_smoke_check_rejects_an_identical_or_nonfinite_mutant():
    baseline, _, _ = pre.solve("N", 80)
    assert not pre.state_distinction_passes(baseline, baseline.copy())
    altered = baseline.copy()
    altered[0] = np.nan
    assert not pre.state_distinction_passes(baseline, altered)


@pytest.mark.parametrize("case", list(pre.CASES))
@pytest.mark.parametrize("frequency_hz", pre.FREQUENCIES)
def test_unmutated_junction_complex_flow_and_pressure(case, frequency_hz):
    state, _, _ = pre.solve(case, frequency_hz)
    checks = pre.junction_diagnostics(state)
    assert checks["pressure_continuity_pa"] < 1e-10
    assert checks["volume_flow_conservation_m3_s"] < 1e-15
    assert abs(checks["junction_mean_power_imbalance_w"]) < 1e-12
    assert checks["junction_complex_power_imbalance_va"] < 1e-12


def test_wrong_velocity_law_can_pass_mean_power_but_fail_complex_flow():
    state, _, _ = pre.solve("N", 80, "junction_particle_velocity")
    checks = pre.junction_diagnostics(state)
    assert checks["pressure_continuity_pa"] < 1e-10
    assert checks["volume_flow_conservation_m3_s"] > 1e-9
    assert checks["junction_complex_power_imbalance_va"] > 1e-10
    # A reactive conservation violation can be invisible to mean-power checks.
    assert abs(checks["junction_mean_power_imbalance_w"]) < 1e-15


def test_wrong_mean_power_factor_requires_absolute_oracle_not_balance_alone():
    state, _, _ = pre.solve("O", 733)
    correct = pre.powers(state)
    wrong = [2 * value for value in correct]  # omitted 1/2 peak-phasor factor
    assert abs(correct[0] - correct[3] - correct[5]) < 1e-12
    assert abs(wrong[0] - wrong[3] - wrong[5]) < 1e-12
    # Conservation alone cannot catch a uniformly wrong factor of two.
    assert abs(wrong[3] - 6.1987007903649672e-7) > 1e-7


def test_metadata_guard_rejects_stale_missing_or_malformed_headers():
    expected = {
        "git_head_sha": "a" * 40,
        "source_sha256": "b" * 64,
        "fixture_sha256": "c" * 64,
        "oracle_sha256": "d" * 64,
    }
    pre.check_evidence_headers(dict(expected), expected)
    for key in expected:
        stale = dict(expected)
        stale[key] = "f" * len(stale[key])
        with pytest.raises(ValueError, match="MISMATCH"):
            pre.check_evidence_headers(stale, expected)
        missing = dict(expected)
        del missing[key]
        with pytest.raises(ValueError, match="MISSING"):
            pre.check_evidence_headers(missing, expected)
        invalid = dict(expected)
        invalid[key] = "not-a-digest"
        with pytest.raises(ValueError, match="FORMAT"):
            pre.check_evidence_headers(invalid, expected)
