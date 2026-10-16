"""OG-4 Gate B: new Core API exercised against inherited independent oracles."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from morphoacoustics.acoustics.uniform_tube import UniformTube
from morphoacoustics_graph.branch3 import (
    Branch3Error, _digest, _system, prepare_branch3, restore_branch3,
)

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / "docs/research/og4-branch3-api-golden.json").read_text())
ORACLE = json.loads((ROOT / "experiments/038_og1_passive_branch/wolfram/oracle.json").read_text())
BASE = GOLDEN["snapshot_example"]["blueprint"]
PORTS = ["A.in", "A.out", "B.in", "B.out", "C.in", "C.out"]
FREQ = [80, 250, 400, 733, 997, 1200, 2000, 4000]
LOADS = ["matched", "pressure_release", "rigid_closed", "fixed_impedance"]
RATIOS = [0.5, 1, 2]
SCALES = [1, .5, -1]


def reference():
    location = ROOT / "experiments/038_og1_passive_branch/reference.py"
    spec = importlib.util.spec_from_file_location("frozen_og1_reference", location)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def blueprint(ratio: float = 1, load: str = "matched", scale: float = 1):
    b = deepcopy(BASE)
    b["organs"][2]["area_m2"] = 3e-4 * ratio
    b["source"]["scale"] = scale
    b["loads"][1] = {"kind": load, "port": "C.out"}
    if load == "fixed_impedance":
        b["loads"][1]["impedance_pa_s_m3"] = {"real": 1372000, "imag": 0}
    return b


def states(obs, i=0):
    return {pid: (complex(**obs["pressure_pa"][i][j]),
                  complex(**obs["volume_flow_m3_s"][i][j]))
            for j, pid in enumerate(obs["port_ids"])}


def test_exact_snapshot_and_canonical_golden():
    p = prepare_branch3(deepcopy(BASE))
    example = GOLDEN["snapshot_example"]
    assert p.blueprint_digest == example["blueprint_digest"]
    assert p.preparation_digest == example["preparation_digest"]
    assert p.to_snapshot() == example
    restored = restore_branch3(p.to_snapshot())
    assert restored.response([733, 997, 733]) == p.response([733, 997, 733])
    reversed_inputs = deepcopy(BASE)
    reversed_inputs["organs"].reverse()
    reversed_inputs["loads"].reverse()
    assert prepare_branch3(reversed_inputs).blueprint_digest == p.blueprint_digest
    assert _digest("blueprint", blueprint(1, "fixed_impedance")) != p.blueprint_digest
    assert p.response([733])["observation_digest"] != p.response([997])["observation_digest"]


def test_288_new_backend_vs_inherited_python():
    ref = reference()
    checked = 0
    peak = 0.
    for ratio in RATIOS:
        for load in LOADS:
            for scale in SCALES:
                result = prepare_branch3(blueprint(ratio, load, scale)).response(FREQ)
                for i, f in enumerate(FREQ):
                    actual = states(result, i)
                    expected = ref.port_states(ratio, f, load, scale)
                    error = ref.state_error(actual, expected, p_ref=1.372, u_ref=1e-6)
                    peak = max(peak, error)
                    assert error <= 1e-10, (ratio, load, scale, f, error)
                    for diagnostic in (result["diagnostics"][i],):
                        assert diagnostic["condition_2"] <= 1e8
                        assert diagnostic["backward_error"] <= 1e-12
                        assert diagnostic["junction_pressure_error"] <= 1e-10
                        assert diagnostic["junction_flow_error"] <= 1e-10
                        assert diagnostic["power_error"] <= 1e-10
                    checked += 1
    assert checked == 288
    print("branch3_vs_inherited_python_288", checked, peak)


def test_24_new_backend_vs_frozen_wolfram():
    checked = 0
    peak = 0.
    for r in ORACLE["records"]:
        result = prepare_branch3(blueprint(r["area_ratio"], r["load_c"])).response([r["frequency_hz"]])
        actual = states(result)
        for port in PORTS:
            for k, normalization in ((0, 1.372), (1, 1e-6)):
                ref = complex(*r["ports"][port][k])
                error = abs(actual[port][k] - ref) / normalization
                peak = max(peak, error)
                assert error <= 1e-10, (r["area_ratio"], r["frequency_hz"], port, error)
        for index, expected_power in zip((0, 3, 5), r["powers_input_B_C_w"]):
            error = abs(result["mean_power_w"][0][index] - expected_power) / (.5 * 1.372e-6)
            peak = max(peak, error)
            assert error <= 1e-10
        checked += 1
    assert checked == 24
    print("branch3_vs_frozen_wolfram_24", checked, peak)


@pytest.mark.parametrize("ratio", RATIOS)
def test_scattering_weighted_energy_and_wrong_particle_velocity(ratio):
    y = np.array([1., 1., ratio])
    s = 2 * np.tile(y / np.sum(y), (3, 1)) - np.eye(3)
    d = np.diag(y)
    assert np.max(np.abs(s.T @ d @ s - d)) <= 1e-12
    assert np.max(np.abs(d @ s - (d @ s).T)) <= 1e-12
    if ratio == 2:
        assert np.allclose(y * abs(s[:, 0])**2, [.25, .25, .5], atol=1e-12)


@pytest.mark.parametrize("mutate,code", [
    (lambda b: b["organs"][0].update({"length_m": 0.0801}), "FROZEN_GEOMETRY"),
    (lambda b: b["organs"][0].update({"air_density_kg_m3": 1.21}), "FROZEN_MEDIUM"),
    (lambda b: b["source"].update({"scale": 0}), "FROZEN_SOURCE"),
    (lambda b: b["loads"][1].update({"kind": "matched", "impedance_pa_s_m3": {"real":1, "imag":0}}), "BLUEPRINT_STRUCTURE"),
])
def test_fails_closed_before_solver(mutate, code):
    b = blueprint()
    mutate(b)
    with pytest.raises(Branch3Error) as exc:
        prepare_branch3(b)
    assert exc.value.code == code


def test_frequency_validation_priority_and_atomic_refusal():
    p = prepare_branch3(blueprint())
    cases = [
        ([], "INVALID", "FREQUENCY_SHAPE"),
        ([[733]], "INVALID", "FREQUENCY_SHAPE"),
        ([733, True], "INVALID", "FREQUENCY_VALUE"),
        ([733, float("nan")], "INVALID", "FREQUENCY_VALUE"),
        ([733] * 257 + [True], "INVALID", "FREQUENCY_VALUE"),
        ([733] * 257, "UNSUPPORTED", "FREQUENCY_POINT_LIMIT"),
        ([0] * 257, "UNSUPPORTED", "FREQUENCY_POINT_LIMIT"),
        ([733, 0], "UNSUPPORTED", "FREQUENCY_NOT_YET_VERIFIED"),
    ]
    for grid, status, code in cases:
        with pytest.raises(Branch3Error) as exc:
            p.response(grid)
        assert (exc.value.status, exc.value.code) == (status, code)
    assert len(p.response([733] * 256)["pressure_pa"]) == 256


def test_snapshot_forgery_and_immutable_rebuild():
    p = prepare_branch3(blueprint())
    snap = p.to_snapshot()
    snap["blueprint"]["organs"][0]["length_m"] = .09
    with pytest.raises(Branch3Error):
        restore_branch3(snap)
    assert p.response([733])["status"] == "OK"
    snap2 = p.to_snapshot()
    snap2["preparation_digest"] = "sha256:" + "0" * 64
    with pytest.raises(Branch3Error) as exc:
        restore_branch3(snap2)
    assert exc.value.code == "SNAPSHOT_DIGEST_MISMATCH"
    object.__setattr__(p, "blueprint_digest", "sha256:" + "0"*64)
    with pytest.raises(Branch3Error) as exc:
        p.response([733])
    assert exc.value.code == "PREPARED_BINDING_MISMATCH"


def test_singular_diagnostic_test_only_harness():
    tubes = tuple(UniformTube(.08, .0003, sound_speed_m_s=343., air_density_kg_m3=1.2)
                  for _ in range(3))
    loads = {"B.out": {"port": "B.out", "kind": "pressure_release"},
             "C.out": {"port": "C.out", "kind": "pressure_release"}}
    m, _ = _system(tubes, loads, 1e-6*(1+.4j), 2143.75)
    assert np.linalg.cond(m) > 1e8


def test_duplicate_port_and_invalid_subpart_before_capability():
    b = blueprint()
    b["organs"][2]["inlet"]["id"] = "B.in"
    with pytest.raises(Branch3Error) as exc:
        prepare_branch3(b)
    assert exc.value.status == "INVALID"
    b = blueprint()
    b["organs"][2]["area_m2"] = .00030001
    with pytest.raises(Branch3Error) as exc:
        prepare_branch3(b)
    assert (exc.value.status, exc.value.code) == ("UNSUPPORTED", "FROZEN_GEOMETRY")


def test_response_complex_shapes_and_power():
    o = prepare_branch3(blueprint(2, "matched")).response([733, 997, 733])
    assert o["port_ids"] == PORTS
    assert len(o["pressure_pa"]) == len(o["volume_flow_m3_s"]) == 3
    assert all(len(row) == 6 for row in o["pressure_pa"])
    assert o["pressure_pa"][0] == o["pressure_pa"][2]
    for row in o["mean_power_w"]:
        assert abs(row[0] - row[3] - row[5]) <= 1e-15


@pytest.mark.parametrize("mutation", ["wrong_signed_flow", "wrong_particle_velocity", "wrong_pressure_sign"])
def test_mutated_junction_law_is_detected_by_independent_reference(mutation):
    """Falsifiers deliberately corrupt one row; production solver stays immutable."""
    ref = reference()
    b = blueprint(2, "matched")
    p = prepare_branch3(b)
    loads = {row["port"]: row for row in b["loads"]}
    m, rhs = _system(p._tubes, loads, 1e-6 * (1 + .4j), 733.)
    if mutation == "wrong_signed_flow":
        m[8, 5] = 1.
        m[8, 9] = 1.
    elif mutation == "wrong_particle_velocity":
        # Enforcing U/A rather than volumetric-flow continuity at unequal area.
        m[8, 9] = -.5
    else:
        m[6, 4] = 1.
    x = np.linalg.solve(m, rhs)
    pvals = x[0::2] * 1.372
    uvals = x[1::2] * 1e-6
    actual = {pid: (pvals[i], uvals[i]) for i, pid in enumerate(PORTS)}
    error = ref.state_error(actual, ref.port_states(2, 733, "matched"), 1.372, 1e-6)
    assert error > 1e-3, (mutation, error)


def test_iterative_long_valid_graph_refusal_and_invalid_precedence():
    base = blueprint()
    previous = "B.out"
    for i in range(1205):
        name = f"D{i:04d}"
        base["organs"].append({
            "id": name, "revision": "v1", "length_m": .08, "area_m2": .0003,
            "sound_speed_m_s": 343, "air_density_kg_m3": 1.2,
            "inlet": {"id": name+".in", "kind": "acoustic.p_u", "direction": "inlet"},
            "outlet": {"id": name+".out", "kind": "acoustic.p_u", "direction": "outlet"}})
        base["junctions"].append({"id": f"E{i:04d}", "law": "ideal.series.p_u",
                                  "ports": [previous, name+".in"]})
        previous = name+".out"
    base["loads"][0]["port"] = previous
    with pytest.raises(Branch3Error) as exc:
        prepare_branch3(base)
    assert (exc.value.status, exc.value.code) == ("UNSUPPORTED", "BRANCH3_TOPOLOGY_ONLY")
    base["organs"][-1]["area_m2"] = -1
    with pytest.raises(Branch3Error) as exc:
        prepare_branch3(base)
    assert exc.value.status == "INVALID"


def test_all_golden_digests_against_production_encoder():
    for vector in GOLDEN["vectors"]:
        assert _digest(vector["kind"], vector["input"]) == vector["digest"], vector["name"]


def test_revisions_and_source_identity_and_loaded_boundary_identity():
    p = prepare_branch3(blueprint())
    edited = blueprint()
    edited["organs"][0]["revision"] = "another-revision"
    assert prepare_branch3(edited).blueprint_digest != p.blueprint_digest
    fixed = prepare_branch3(blueprint(1, "fixed_impedance"))
    assert p.blueprint_digest != fixed.blueprint_digest
    assert p.response([733])["pressure_pa"] == fixed.response([733])["pressure_pa"]
