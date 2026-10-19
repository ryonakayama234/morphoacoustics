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


def test_m_bad_junction_particle_velocity_equation_is_falsified():
    """Solve a genuinely wrong global LAW, rather than merely corrupting output.

    This is a TEST-ONLY injected mutant in an existing diagnostic matrix.
    It is not used as the experimental M solver or as the Wolfram oracle.
    """
    import numpy as np
    from morphoacoustics.acoustics.uniform_tube import UniformTube
    from morphoacoustics_graph.branch3 import _system

    tubes = tuple(UniformTube(length, area, sound_speed_m_s=nr1a.SPEED,
                              air_density_kg_m3=nr1a.RHO)
                  for length, area in zip(nr1a.LENGTHS, nr1a.AREAS))
    bp = nr1a.blueprint("M")
    loads = {row["port"]: row for row in bp["loads"]}
    physical, source = _system(tubes, loads, nr1a.SOURCE, 733)
    wrong = physical.copy()
    # WRONG: enforce velocity equality weighted by the mouth/nose area ratio,
    # instead of the sum of signed VOLUME FLOWS at the junction.
    wrong[8, 9] = -nr1a.AREAS[1] / nr1a.AREAS[2]
    result = np.linalg.solve(wrong, source)
    record = nr1a.load_oracle()["records"][19]  # M at 733Hz
    err = max(
        max(abs(result[2*j]*nr1a.P_REF - complex(*record["pressure_pa"][j]))
            / nr1a.P_REF for j in range(6)),
        max(abs(result[2*j+1]*nr1a.U_REF -
                complex(*record["volume_flow_m3_s"][j])) / nr1a.U_REF
            for j in range(6)),
    )
    assert err > 1e-3, "an actually wrong conservation law must be detected"
    assert abs(result[3] - result[5] - result[9]) > 1e-3


def test_all_research_derived_transfers_and_input_impedances_present():
    data = nr1a.load_oracle()
    for index, (case, f) in enumerate(
            (case, hz) for case in "NOM" for hz in nr1a.FREQUENCIES):
        obs = nr1a.observe(case)
        derived = obs["derived_observables"][nr1a.FREQUENCIES.index(f)]
        assert derived["frequency_hz"] == f
        z = nr1a.unpack(derived["input_impedance_pa_s_m3"])
        z_wl = complex(*data["records"][index]["input_impedance_pa_s_m3"])
        assert abs(z - z_wl) / (nr1a.P_REF / nr1a.U_REF) <= 1e-10
        for end in ("B", "C"):
            assert all(math.isfinite(x) for x in
                       derived[f"transfer_p_{end}_out_over_p_A_in"].values())

@pytest.mark.parametrize("case", ["N", "O", "M"])
@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("field,port,component", [
    ("pressure_pa", 3, "real"), ("pressure_pa", 0, "imag"),
    ("volume_flow_m3_s", 4, "real"), ("volume_flow_m3_s", 2, "imag"),
])
def test_nonfinite_full_state_fails_closed(case, bad_value, field, port, component):
    observations, _ = nr1a.execute()
    observations[case]["response"][field][3][port][component] = bad_value
    with pytest.raises(AssertionError):
        nr1a.compare(observations)


@pytest.mark.parametrize("case", ["N", "O", "M"])
@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("target", ["power", "zin", "transfer", "diagnostic"])
def test_nonfinite_derived_power_and_diagnostics_fail_closed(case, bad_value, target):
    observations, _ = nr1a.execute()
    obs = observations[case]
    if target == "power":
        obs["response"]["mean_power_w"][3][3] = bad_value
    elif target == "zin":
        obs["derived_observables"][3]["input_impedance_pa_s_m3"]["imag"] = bad_value
    elif target == "transfer":
        obs["derived_observables"][3]["transfer_p_B_out_over_p_A_in"]["real"] = bad_value
    else:
        key = next(iter(obs["response"]["diagnostics"][3]))
        obs["response"]["diagnostics"][3][key] = bad_value
    with pytest.raises(AssertionError):
        nr1a.compare(observations)


@pytest.mark.parametrize("case", ["N", "O", "M"])
@pytest.mark.parametrize("target", [
    "case", "blueprint", "physical_digest", "backend",
    "derived_frequency", "source_digest", "observation_digest",
])
def test_stale_identity_cannot_pass_with_unchanged_numeric_states(case, target):
    observations, _ = nr1a.execute()
    obs = observations[case]
    if target == "case":
        obs["case"] = "O" if case != "O" else "N"
    elif target == "blueprint":
        obs["physical_blueprint"]["organs"][0]["length_m"] += 0.001
    elif target == "physical_digest":
        obs["physical_blueprint_research_digest"] = "sha256:" + "0" * 64
    elif target == "backend":
        obs["response"]["backend_id"] = "wrong.backend"
    elif target == "derived_frequency":
        obs["derived_observables"][3]["frequency_hz"] = 734
    elif target == "source_digest":
        key = ("blueprint_research_digest" if case == "M" else "blueprint_digest")
        obs["binding"][key] = "sha256:" + "0" * 64
    else:
        if case == "M":
            obs["binding"]["observation_research_digest"] = "sha256:" + "0" * 64
        else:
            obs["response"]["observation_digest"] = "sha256:" + "0" * 64
    with pytest.raises(AssertionError):
        nr1a.compare(observations)


@pytest.mark.parametrize("case", ["N", "O", "M"])
@pytest.mark.parametrize("target", ["power", "zin", "transfer"])
def test_finite_but_stale_derived_values_cannot_pass(case, target):
    observations, _ = nr1a.execute()
    obs = observations[case]
    if target == "power":
        obs["response"]["mean_power_w"][3][3] += 1e-7
    elif target == "zin":
        obs["derived_observables"][3]["input_impedance_pa_s_m3"]["real"] += 1e5
    else:
        obs["derived_observables"][3]["transfer_p_C_out_over_p_A_in"]["imag"] += 0.1
    with pytest.raises(AssertionError):
        nr1a.compare(observations)


def test_m_oral_closed_local_admittance_pole_is_not_global_singularity():
    """Research stress-only: frozen M API remains the original eight frequencies.

    The independent Wolfram 12-equation solution at f*=c/(4 L_B) has
    p_A.in=-3.112399462606199+7.780998656515497j Pa,
    p_B.out=3.160413241149226-7.901033102873065j Pa and p_J=0.
    """
    import numpy as np
    from morphoacoustics.acoustics.uniform_tube import UniformTube
    from morphoacoustics_graph.branch3 import _system

    tubes = tuple(UniformTube(length, area, sound_speed_m_s=nr1a.SPEED,
                              air_density_kg_m3=nr1a.RHO)
                  for length, area in zip(nr1a.LENGTHS, nr1a.AREAS))
    loads = {row["port"]: row for row in nr1a.blueprint("M")["loads"]}
    fstar = nr1a.SPEED / (4 * nr1a.LENGTHS[1])
    baseline = None
    for f in (fstar - 1e-6, fstar, fstar + 1e-6):
        matrix, rhs = _system(tubes, loads, nr1a.SOURCE, f)
        assert np.linalg.matrix_rank(matrix) == 12
        condition = float(np.linalg.cond(matrix))
        assert np.isfinite(condition) and condition < 1e4
        x = np.linalg.solve(matrix, rhs)
        backward = np.linalg.norm(matrix @ x - rhs, np.inf) / (
            np.linalg.norm(matrix, np.inf)*np.linalg.norm(x, np.inf) +
            np.linalg.norm(rhs, np.inf))
        assert backward < 1e-12
        p = x[0::2] * nr1a.P_REF
        u = x[1::2] * nr1a.U_REF
        assert abs(p[0] - complex(-3.112399462606199, 7.780998656515497)) < 1e-5
        assert abs(p[3] - complex(3.160413241149226, -7.901033102873065)) < 1e-5
        assert abs(p[1]) < 1e-6
        assert abs(u[3]) < 1e-12
        if f == fstar:
            baseline = x
        elif baseline is not None:
            assert np.linalg.norm(x - baseline, np.inf) < 1e-5
    assert baseline is not None
    with pytest.raises(ValueError, match="UNSUPPORTED:RESEARCH_SCOPE"):
        nr1a.recursive_mouth_closed("M", [fstar])


@pytest.mark.parametrize("mutant", ["tube_sign", "wrong_mouth_load", "phasor_sign"])
def test_m_733Hz_additional_law_level_mutants_are_detected(mutant):
    """True matrix-law changes, checked against the independent Wolfram record."""
    import numpy as np
    from morphoacoustics.acoustics.uniform_tube import UniformTube
    from morphoacoustics_graph.branch3 import _system

    tubes = tuple(UniformTube(length, area, sound_speed_m_s=nr1a.SPEED,
                              air_density_kg_m3=nr1a.RHO)
                  for length, area in zip(nr1a.LENGTHS, nr1a.AREAS))
    loads = {row["port"]: row for row in nr1a.blueprint("M")["loads"]}
    matrix, rhs = _system(tubes, loads, nr1a.SOURCE, 733)
    wrong = matrix.copy()
    if mutant == "tube_sign":
        wrong[0, 3] *= -1
        wrong[1, 2] *= -1
    elif mutant == "wrong_mouth_load":
        wrong[9, :] = 0
        wrong[9, 6], wrong[9, 7] = 1, -1
    else:
        wrong = np.conjugate(wrong)
    candidate = np.linalg.solve(wrong, rhs)
    record = nr1a.load_oracle()["records"][19]
    err = max(
        max(abs(candidate[2*j] * nr1a.P_REF -
                complex(*record["pressure_pa"][j])) / nr1a.P_REF for j in range(6)),
        max(abs(candidate[2*j+1] * nr1a.U_REF -
                complex(*record["volume_flow_m3_s"][j])) / nr1a.U_REF for j in range(6)),
    )
    assert err > 1e-5, f"undetected law mutant {mutant}: {err}"


def test_wolfram_numeric_regeneration_verifier_is_fail_closed():
    """Independent-source comparison tool must detect changes in all result types."""
    from importlib import util

    verifier_path = EXP / "wolfram" / "verify_regeneration.py"
    spec = util.spec_from_file_location("nr1a_verify_regeneration", verifier_path)
    assert spec and spec.loader
    verifier = util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    golden = verifier.read_json(
        (EXP / "wolfram" / "global12_oracle.json").read_text(encoding="utf-8"))
    assert verifier.compare_candidate_oracles(golden, deepcopy(golden)) == 0
    for field, index, magnitude in (
        ("pressure_pa", (0, 0), 1e-4),
        ("volume_flow_m3_s", (4, 1), 1e-10),
        ("mean_power_w", (3,), 1e-10),
        ("input_impedance_pa_s_m3", (0,), 1e3),
    ):
        bad = deepcopy(golden)
        item = bad["records"][4][field]
        if len(index) == 2:
            item[index[0]][index[1]] += magnitude
        else:
            item[index[0]] += magnitude
        with pytest.raises(AssertionError, match="differs"):
            verifier.compare_candidate_oracles(golden, bad)
    wrong_case = deepcopy(golden)
    wrong_case["records"][0]["case"] = "O"
    with pytest.raises(AssertionError, match="case/order"):
        verifier.compare_candidate_oracles(golden, wrong_case)
    for bad_value in (float("nan"), float("inf"), float("-inf")):
        bad = deepcopy(golden)
        bad["records"][0]["pressure_pa"][0][0] = bad_value
        with pytest.raises(AssertionError, match="nonfinite"):
            verifier.compare_candidate_oracles(golden, bad)
    bad_metadata = deepcopy(golden)
    bad_metadata["status"] = "ADOPTED"
    with pytest.raises(AssertionError, match="metadata"):
        verifier.compare_candidate_oracles(golden, bad_metadata)
