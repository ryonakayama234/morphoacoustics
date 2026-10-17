"""Research-only NR-1a candidate checks. No new public OG-4 capability."""
from __future__ import annotations

from copy import deepcopy
from importlib import util
from pathlib import Path
import json
import math

import pytest
from morphoacoustics_graph.branch3 import Branch3Error, prepare_branch3

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "041_nr1_static_oral_nasal_route"
SPEC = util.spec_from_file_location("nr1a_trial", EXP / "run.py")
assert SPEC and SPEC.loader
nr1a = util.module_from_spec(SPEC)
SPEC.loader.exec_module(nr1a)


def _state(observation, frequency_index=3):
    r = observation["response"]
    return [(nr1a.unpack(r["pressure_pa"][frequency_index][i]),
             nr1a.unpack(r["volume_flow_m3_s"][frequency_index][i]))
            for i in range(6)]


def test_all_24_cases_full_complex_Wolfram_reference():
    outputs, result = nr1a.execute()
    assert result["total"] == 24
    assert set(result["per_case"]) == {"N", "O", "M"}
    assert max(row["max_scaled_endpoint_error"]
               for row in result["per_case"].values()) <= nr1a.MAX_STATE
    assert outputs["N"]["binding"]["source"] == "adopted-core"
    assert outputs["O"]["binding"]["source"] == "adopted-core"
    assert outputs["M"]["binding"]["source"] == "experiment-only"


def test_733Hz_terminal_power_and_reactive_nose_side_cavity():
    o = {case: nr1a.observe(case) for case in "NOM"}
    expected = {
        "N": (5.3130604780595185e-7, 0.0),
        "O": (6.1987007903649672e-7, 3.0993503951824836e-7),
        "M": (0.0, 8.6128929520173005e-8),
    }
    for case, (mouth, nose) in expected.items():
        r = o[case]["response"]
        assert abs(r["mean_power_w"][3][3]-mouth) < 1e-14
        assert abs(r["mean_power_w"][3][5]-nose) < 1e-14
        assert abs(r["mean_power_w"][3][0] - mouth - nose) < 1e-14
    p, u = _state(o["N"])[4]
    assert abs(u) > 1e-10, "closed distal nasal outlet must retain coupled cavity"


def test_m_scope_refusal_from_adopted_core_and_no_leakage():
    b = nr1a.blueprint("M")
    with pytest.raises(Branch3Error) as ex:
        prepare_branch3(deepcopy(b))
    assert (ex.value.status, ex.value.code, ex.value.path) == (
        "UNSUPPORTED", "FROZEN_LOAD", "/loads")
    obs = nr1a.observe("M")
    assert obs["response"]["backend_id"] == nr1a.EXPERIMENT_BACKEND
    assert obs["response"]["schema"] == "nr1a.research.only.response.v0"
    with pytest.raises(ValueError, match="UNSUPPORTED:RESEARCH_SCOPE"):
        nr1a.recursive_mouth_closed("O", nr1a.FREQUENCIES)
    with pytest.raises(ValueError, match="UNSUPPORTED:RESEARCH_SCOPE"):
        nr1a.recursive_mouth_closed("M", [733])


def test_only_one_terminal_law_changes_against_common_reference():
    base = nr1a.blueprint("O")
    for case, changed_port in (("N", "C.out"), ("M", "B.out")):
        mutant = nr1a.blueprint(case)
        assert mutant["organs"] == base["organs"]
        assert mutant["junctions"] == base["junctions"]
        assert mutant["source"] == base["source"]
        diff = [a["port"] for a, b in zip(mutant["loads"], base["loads"]) if a != b]
        assert diff == [changed_port]
        assert nr1a.canonical_sha(mutant) != nr1a.canonical_sha(base)


def test_wrong_law_and_swapped_id_mutants_are_detected_by_full_state():
    oracle = nr1a.load_oracle()
    for case in ("N", "O", "M"):
        obs = nr1a.observe(case)
        rec = oracle["records"][list("NOM").index(case) * 8 + 3]
        assert nr1a.endpoint_error(obs, rec, 3) < nr1a.MAX_STATE
        # Wrong law: incorrectly halve C.in volumetric flow at unequal area.
        wrong = deepcopy(obs)
        wrong["response"]["volume_flow_m3_s"][3][4]["real"] *= 0.5
        wrong["response"]["volume_flow_m3_s"][3][4]["imag"] *= 0.5
        assert nr1a.endpoint_error(wrong, rec, 3) > 1e-4
        # Reversing orientation for C.in must not pass.
        reverse = deepcopy(obs)
        reverse["response"]["volume_flow_m3_s"][3][4]["real"] *= -1
        reverse["response"]["volume_flow_m3_s"][3][4]["imag"] *= -1
        assert nr1a.endpoint_error(reverse, rec, 3) > 1e-4
        # Data/port label mixup: swaps full B.out and C.out states.
        swap = deepcopy(obs)
        for fld in ("pressure_pa", "volume_flow_m3_s"):
            row = swap["response"][fld][3]
            row[3], row[5] = row[5], row[3]
        assert nr1a.endpoint_error(swap, rec, 3) > 1e-4


@pytest.mark.parametrize("mutation,expected_code", [
    (lambda b: b["organs"][2]["inlet"].update({"id":"B.in"}), "BLUEPRINT_STRUCTURE"),
    (lambda b: b["organs"][0].update({"length_m":-0.1}), "BLUEPRINT_STRUCTURE"),
    (lambda b: b["organs"][0].update({"area_m2":0}), "BLUEPRINT_STRUCTURE"),
    (lambda b: b["loads"][1].update({"port":"B.out"}), "BLUEPRINT_STRUCTURE"),
    (lambda b: b["junctions"][0].update({"ports":["A.out","B.in","A.in"]}), "BLUEPRINT_STRUCTURE"),
    (lambda b: b["organs"][0].update({"length_m":0.081}), "FROZEN_GEOMETRY"),
])
def test_existing_core_rejects_unlawful_or_unsupported_inputs(mutation, expected_code):
    bp = nr1a.blueprint("O")
    mutation(bp)
    with pytest.raises(Branch3Error) as exc:
        prepare_branch3(bp)
    assert exc.value.code == expected_code


def test_experimental_identities_revisions_or_load_changes():
    a = nr1a.blueprint("M")
    b = deepcopy(a)
    b["organs"][0]["revision"] = "nr1a.r1"
    assert nr1a.canonical_sha(a) != nr1a.canonical_sha(b)
    assert nr1a.canonical_sha(nr1a.blueprint("M")) == nr1a.canonical_sha(a)


def test_oracle_is_full_state_and_generated_from_Wolfram_source():
    oracle = nr1a.load_oracle()
    assert len(oracle["records"]) == 24
    for record in oracle["records"]:
        assert len(record["pressure_pa"]) == len(record["volume_flow_m3_s"]) == 6
        assert len(record["mean_power_w"]) == 6
        for field in ("pressure_pa", "volume_flow_m3_s"):
            assert all(len(x) == 2 and all(math.isfinite(v) for v in x)
                       for x in record[field])
    source = (EXP / "wolfram" / "global12_oracle.wl").read_text(encoding="utf-8")
    assert "Solve[eqs,unknowns]" in source
    assert "from morphoacoustics" not in source


def test_repeated_runs_are_stable_without_silent_fallback():
    first, first_report = nr1a.execute()
    second, second_report = nr1a.execute()
    assert first_report == second_report
    assert nr1a.canonical_sha(first) == nr1a.canonical_sha(second)
