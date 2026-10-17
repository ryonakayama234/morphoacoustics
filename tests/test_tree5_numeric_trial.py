"""Gate B1 internal physical numerical tests; NOT full Gate B acceptance."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from morphoacoustics_graph import tree5

ROOT = Path(__file__).resolve().parents[1]
FROZEN_EIGHT = ROOT / "docs/research/og5-wolfram-gate-a-result.json"


def test_144_positive_trial_conditions() -> None:
    trials = []
    for area in (.00015, .0003, .0006):
        for load in ("matched", "rigid_closed"):
            for scale in (1., .5, -1.):
                for f in (80, 250, 400, 733, 997, 1200, 2000, 4000):
                    out = tree5._solve_fixture(area, load, scale, f)
                    assert len(out.port_ids) == len(out.pressure_pa) == len(out.volume_flow_m3_s) == 10
                    assert out.scaled_linear_residual <= 1e-12
                    assert out.condition_number_2 <= 1e4
                    assert out.relative_power_defect <= 1e-10
                    assert max(out.j1_scaled_pressure_residual, out.j2_scaled_pressure_residual,
                               out.j1_scaled_flow_residual, out.j2_scaled_flow_residual) <= 1e-10
                    trials.append((area, load, scale, f))
    assert len(set(trials)) == 144


def test_eight_frozen_wolfram_full_port_records() -> None:
    """Eight known, NOT blind, Wolfram full-complex-state vectors."""
    rows = json.loads(FROZEN_EIGHT.read_text(encoding="utf-8"))["records"]
    assert len(rows) == 8
    for row in rows:
        load = "rigid_closed" if row["c_load"] == "closed" else row["c_load"]
        out = tree5._solve_fixture(row["c_area_m2"], load, row["source_scale"],
                                   row["frequency_hz"])
        assert tuple(row["port_states"]) == out.port_ids
        for k, port in enumerate(out.port_ids):
            ref = row["port_states"][port]
            assert abs(out.pressure_pa[k] - complex(*ref["p_pa"])) / tree5.P_REF <= 1e-10
            assert abs(out.volume_flow_m3_s[k] - complex(*ref["u_m3_s"])) / tree5.U_REF <= 1e-10


def test_wrong_junction_laws_fail_full_port_comparison() -> None:
    tubes = tree5._fixture_tubes(.00015)
    m, rhs = tree5._system(tubes, "matched", 1., 733.)
    correct = tree5._certified_solution(m, rhs)[0]
    edits = (
        (12, 9, +1.), (15, 17, +1.),
        (12, 9, -tubes[0].area_m2 / tubes[2].area_m2),
        (15, 17, -tubes[1].area_m2 / tubes[4].area_m2),
        (10, 4, +1.),
        (17, 11, m[17, 11] / 2),
    )
    for row, col, incorrect in edits:
        bad = m.copy()
        bad[row, col] = incorrect
        x = tree5._certified_solution(bad, rhs)[0]
        assert float(np.max(np.abs(x - correct))) > 1e-6


def test_numerical_matrix_rank_condition_nonfinite() -> None:
    m, rhs = tree5._system(tree5._fixture_tubes(.00015), "matched", 1., 733.)
    bad = m.copy()
    bad[-1] = bad[-2]
    rb = rhs.copy()
    rb[-1] = rb[-2]
    with pytest.raises(tree5.Tree5NumericalError, match="MATRIX_RANK_DEFICIENT"):
        tree5._certified_solution(bad, rb)
    ill = np.diag(np.array([1.] * 19 + [1e-5])).astype(np.complex128)
    with pytest.raises(tree5.Tree5NumericalError, match="MATRIX_ILL_CONDITIONED"):
        tree5._certified_solution(ill, np.ones(20, dtype=np.complex128))
    ill[0, 0] = float("nan")
    with pytest.raises(tree5.Tree5NumericalError, match="NUMERIC_NONFINITE"):
        tree5._certified_solution(ill, rhs)


def test_source_scales_linearly_and_power_quadratically() -> None:
    base = tree5._solve_fixture(.00015, "matched", 1., 733.)
    for scale in (.5, -1.):
        out = tree5._solve_fixture(.00015, "matched", scale, 733.)
        assert max(abs(x-scale*y) for x,y in zip(out.pressure_pa,base.pressure_pa)) < 1e-11
        assert max(abs(x-scale*y) for x,y in zip(out.volume_flow_m3_s,base.volume_flow_m3_s)) < 1e-15
        assert max(abs(x-scale*scale*y) for x,y in zip(out.mean_power_w,base.mean_power_w)) < 1e-14
