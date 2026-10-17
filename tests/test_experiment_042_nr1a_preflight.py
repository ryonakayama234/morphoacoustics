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
        for mutant in pre.MUTANTS:
            assert row["mutant_max_scaled_state_deviation"][mutant] >= 0


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
