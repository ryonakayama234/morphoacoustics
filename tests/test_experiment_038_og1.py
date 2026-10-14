"""Pre-implementation fixed OG-1 scientific/software gates. Research only."""
from dataclasses import replace
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/038_og1_passive_branch"


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, EXP / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


n = load("og1_network", "network.py")
r = load("og1_reference", "reference.py")
FREQUENCIES = (80, 250, 400, 733, 997, 1200, 2000, 4000)
LOADS = ("matched", "pressure_release", "rigid_closed", "fixed_impedance")


@pytest.mark.parametrize("ratio,load_c,f,scale", tuple(itertools.product((.5, 1., 2.), LOADS, FREQUENCIES, (1., .5, -1.))))
def test_fixed_full_network_gates(ratio, load_c, f, scale):
    body = n.prepare(n.fixture(ratio, load_c, scale))
    out = n.solve(body, f)
    assert r.state_error(out.ports, r.port_states(ratio, f, load_c, scale), body.p_ref) <= 1e-10
    assert out.condition <= 1e8
    assert out.backward_error <= 1e-12
    assert out.junction_pressure_error <= 1e-10
    assert out.junction_flow_error <= 1e-10
    assert out.power_error <= 1e-10
    assert all(p >= -.5 * body.p_ref * n.U_REF * 1e-10 for p in out.powers_w)
    if load_c in ("pressure_release", "rigid_closed"):
        assert abs(out.powers_w[2]) / (.5 * body.p_ref * n.U_REF * scale**2) <= 1e-10
        # Zero terminal mean power is not a zero branch field.
        assert abs(out.ports["C.in"][0]) > 0


ORACLE = json.loads((EXP / "wolfram/oracle.json").read_text())


@pytest.mark.parametrize("record", ORACLE["records"])
def test_independently_executed_wolfram_full_port_oracle(record):
    body = n.prepare(n.fixture(record["area_ratio"], record["load_c"]))
    out = n.solve(body, record["frequency_hz"])
    expected = {key: tuple(complex(*value) for value in pair)
                for key, pair in record["ports"].items()}
    assert r.state_error(out.ports, expected, body.p_ref) <= 1e-10
    assert r.state_error(r.port_states(record["area_ratio"], record["frequency_hz"], record["load_c"]),
                         expected, body.p_ref) <= 1e-10
    np.testing.assert_allclose(out.powers_w, record["powers_input_B_C_w"], atol=1e-16, rtol=1e-10)


@pytest.mark.parametrize("ratio", (.5, 1., 2.))
def test_local_all_incidence_and_weighted_power(ratio):
    areas = (3e-4, 3e-4, 3e-4 * ratio)
    basis = np.eye(3)
    actual = np.column_stack([n.local_scatter(areas, incoming) for incoming in basis])
    expected = r.scatter_matrix(areas)
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)
    y = np.array([1, 1, ratio])
    np.testing.assert_allclose(actual.conj().T @ np.diag(y) @ actual, np.diag(y), atol=1e-12, rtol=0)
    incoming = np.array([1+.4j, -.2+.7j, .6-.1j])
    outgoing = n.local_scatter(areas, incoming)
    np.testing.assert_allclose(outgoing, expected @ incoming, rtol=0, atol=1e-12)
    assert abs(np.sum(y * abs(incoming)**2) - np.sum(y * abs(outgoing)**2)) < 1e-12
    exact = {.5: [1/25, 16/25, 8/25], 1.: [1/9, 4/9, 4/9], 2.: [1/4, 1/4, 1/2]}[ratio]
    np.testing.assert_allclose(y * abs(actual[:, 0])**2, exact, atol=1e-12, rtol=0)


@pytest.mark.parametrize("mutation", ("wrong_sign", "particle_velocity"))
def test_independent_oracle_rejects_wrong_coupling(mutation):
    body = n.prepare(n.fixture(2.))
    wrong = n.solve(body, 733, _mutation=mutation)
    expected = r.port_states(2., 733, "matched")
    assert r.state_error(wrong.ports, expected, body.p_ref) > 1e-3
    assert wrong.junction_flow_error > 1e-3


def test_graph_order_and_wire_direction_do_not_change_identity_or_physics():
    graph = n.fixture(2., "fixed_impedance")
    alternate = replace(graph, tubes=tuple(reversed(graph.tubes)),
                        edges=tuple(n.Edge(e.right, e.left) for e in reversed(graph.edges)),
                        junctions=(replace(graph.junctions[0], ports=("c", "a", "b")),),
                        boundaries=tuple(reversed(graph.boundaries)))
    a, b = n.prepare(graph), n.prepare(alternate)
    assert a.graph_digest == b.graph_digest
    assert n.solve(a, 997).ports == n.solve(b, 997).ports
    changed = n.prepare(n.fixture(1., "fixed_impedance"))
    assert a.graph_digest != changed.graph_digest
    assert n.solve(a, 997).ports != n.solve(changed, 997).ports


def test_zero_excitation_and_linear_response():
    a = n.solve(n.prepare(n.fixture(scale=0)), 997)
    assert all(p == 0j and u == 0j for p, u in a.ports.values())
    assert a.power_error == 0
    base = n.prepare(n.fixture())
    flipped = n.prepare(n.fixture(scale=-1))
    assert base.graph_digest != flipped.graph_digest


def malformed_graphs():
    g = n.fixture()
    return [
        replace(g, edges=g.edges + (g.edges[0],)),
        replace(g, edges=g.edges[:-1]),
        replace(g, edges=(replace(g.edges[0], left=n.Port("missing", "out")),) + g.edges[1:]),
        replace(g, edges=(replace(g.edges[0], left=n.Port("A", "out", "mechanical")),) + g.edges[1:]),
        replace(g, boundaries=g.boundaries[:-1]),
        replace(g, boundaries=g.boundaries + (g.boundaries[0],)),
        replace(g, junctions=(replace(g.junctions[0], law="unknown"),)),
        replace(g, junctions=(replace(g.junctions[0], ports=("a", "a", "c")),)),
        replace(g, tubes=(replace(g.tubes[0], id="B"),) + g.tubes[1:]),
        replace(g, tubes=(replace(g.tubes[0], area_m2=0),) + g.tubes[1:]),
        replace(g, tubes=(replace(g.tubes[0], length_m=float("nan")),) + g.tubes[1:]),
        replace(g, rho=True),
        replace(g, speed=float("inf")),
        replace(g, boundaries=(replace(g.boundaries[0], value=float("nan")),) + g.boundaries[1:]),
        replace(g, boundaries=g.boundaries[:2] + (n.Boundary(n.Port("C", "out"), "impedance", -1),)),
        replace(g, boundaries=g.boundaries[:2] + (n.Boundary(n.Port("C", "out"), "matched", 5),)),
        replace(g, tubes=list(g.tubes)),
    ]


@pytest.mark.parametrize("graph", malformed_graphs())
def test_invalid_graphs_fail_with_correct_taxonomy(graph):
    with pytest.raises(n.InvalidGraph):
        n.prepare(graph)


def test_larger_graph_validity_precedes_unsupported_capability():
    g = n.fixture()
    larger = replace(g, tubes=g.tubes + (n.Tube("D", .03, 3e-4),),
                     edges=(g.edges[0], g.edges[2],
                            n.Edge(n.Port("J", "b"), n.Port("D", "in")),
                            n.Edge(n.Port("D", "out"), n.Port("B", "in"))))
    n.validate(larger)
    with pytest.raises(n.UnsupportedGraph):
        n.prepare(larger)
    with pytest.raises(n.InvalidGraph):
        n.prepare(replace(larger, tubes=larger.tubes[:-1] + (replace(larger.tubes[-1], area_m2=-1),)))
    # A schema-valid loop is unsupported rather than silently deleted.
    loop = n.Graph(g.tubes, (), (n.Edge(n.Port("A", "out"), n.Port("B", "in")),
                                n.Edge(n.Port("B", "out"), n.Port("C", "in")),
                                n.Edge(n.Port("C", "out"), n.Port("A", "in"))), ())
    n.validate(loop)
    with pytest.raises(n.UnsupportedGraph):
        n.prepare(loop)


def test_singular_internal_branch_mode_is_reported_not_regularized():
    graph = n.fixture(load_c="pressure_release")
    graph = replace(graph, tubes=tuple(replace(t, length_m=.08) for t in graph.tubes),
                    boundaries=(graph.boundaries[0], n.Boundary(n.Port("B", "out"), "pressure_release"),
                                graph.boundaries[2]))
    with pytest.raises(n.NumericallyUnresolved, match="condition"):
        n.solve(n.prepare(graph), 343 / (.08 * 2))


@pytest.mark.parametrize("f", (-1, float("nan"), float("inf"), True))
def test_invalid_frequency(f):
    with pytest.raises(n.InvalidGraph):
        n.solve(n.prepare(n.fixture()), f)


def test_runner_recomputes_and_rejects_stale_evidence(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    for output in (first, second):
        subprocess.run([sys.executable, str(EXP / "run.py"), "--output-dir", str(output)],
                       check=True, capture_output=True, timeout=60)
    manifest = json.loads((first / "summary.json").read_text())
    assert manifest["numeric_status"] == "PROVISIONAL_NUMERICAL_PASS"
    assert manifest["adoption_status"] == "NOT_ADOPTED"
    assert manifest["nominal_runs"] == 288
    assert manifest["wolfram_records"] == 24
    for name in ("states.csv", "metrics.json", "graphs.json", "local_scattering.json", "summary.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    stale = subprocess.run([sys.executable, str(EXP / "run.py"), "--output-dir", str(first)],
                           capture_output=True, timeout=60)
    assert stale.returncode != 0
    assert (first / "summary.json").read_bytes() == (second / "summary.json").read_bytes()


@pytest.mark.parametrize(("field", "value"), [
    ("area_m2", 1e-320),  # primitive finite and positive, but Z overflows
])
def test_extreme_positive_geometry_cannot_create_nonfinite_impedance(field, value):
    from dataclasses import replace
    original = n.fixture()
    malformed = replace(original, tubes=(original.tubes[0],
        replace(original.tubes[1], **{field: value}), original.tubes[2]))
    with pytest.raises(n.InvalidGraph, match="nonfinite derived impedance"):
        n.prepare(malformed)


@pytest.mark.parametrize(("rho", "speed"), [
    (5e-324, 343.0),
    (1.2, 5e-324),
])
def test_extreme_positive_medium_cannot_create_nonfinite_impedance(rho, speed):
    from dataclasses import replace
    with pytest.raises(n.InvalidGraph, match="nonfinite derived impedance"):
        n.prepare(replace(n.fixture(), rho=rho, speed=speed))


def test_source_checkout_attestation_rejects_spoofed_git_sha(monkeypatch):
    monkeypatch.syspath_prepend(str(EXP))
    module = load("og1_run_attestation", "run.py")
    attested = module.checkout_attestation(None)
    assert len(attested["head_sha"]) == 40
    assert attested["tracked_checkout_clean"] is True
    with pytest.raises(RuntimeError, match="HEAD_SHA_MISMATCH"):
        module.checkout_attestation("0" * 40)
