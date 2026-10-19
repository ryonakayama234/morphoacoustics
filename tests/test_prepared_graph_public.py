"""Gate B fixed-two-tube public candidate: clean-room production imports only."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
import pytest

from morphoacoustics.acoustics.uniform_tube import UniformTube
from morphoacoustics_graph.model import (
    SCHEMA, AcousticPort, PassiveTubeOrgan, AcousticJunction,
    OrganGraphBlueprint, SERIES_LAW, BRANCH_LAW, graph_to_dict,
)
from morphoacoustics_graph.preparation import (
    GraphError, validate_graph, prepare_graph, restore_prepared, observe_transfer,
)

ROOT = Path(__file__).resolve().parents[1]
ORACLE = json.loads((ROOT / "experiments/039_og2_prepared_graph/wolfram/og2_oracle.json").read_text())
FS = ORACLE["frequencies_hz"]


def fixture(*, b_area: float = 6e-4, b_revision: str = "r1",
            termination: str = "matched") -> OrganGraphBlueprint:
    a = PassiveTubeOrgan("organ-A", "r1", 0.08, 3e-4,
                         AcousticPort("organ-A.in", "inlet"),
                         AcousticPort("organ-A.out", "outlet"))
    b = PassiveTubeOrgan("organ-B", b_revision, 0.09, b_area,
                         AcousticPort("organ-B.in", "inlet"),
                         AcousticPort("organ-B.out", "outlet"))
    edge = AcousticJunction("edge-AB", SERIES_LAW, ("organ-A.out", "organ-B.in"))
    return OrganGraphBlueprint(SCHEMA, (a, b), (edge,), "organ-A.in",
                               ("organ-B.out",), termination)


def oracle_matrix() -> np.ndarray:
    data = np.array(ORACLE["normalized_matrix_rowmajor_re_im"], dtype=float)
    return (data[..., 0] + 1j * data[..., 1]).reshape(7, 2, 2)


def test_clean_room_full_complex_wolfram_and_independent_identities():
    prepared = prepare_graph(fixture())
    got = observe_transfer(prepared, FS)
    assert [o.id for o in prepared.organs_in_path_order] == ["organ-A", "organ-B"]
    assert prepared.port_mapping == (
        ("organ-A", "organ-A.in", "organ-A.out"),
        ("organ-B", "organ-B.in", "organ-B.out"),
    )
    assert prepared.junction.ports == ("organ-A.out", "organ-B.in")
    assert got.kind == "unloaded_full_complex_two_port"
    assert got.matrix_numpy().shape == (7, 2, 2)
    assert np.max(np.abs(got.matrix_numpy() - oracle_matrix())) <= 1e-10
    assert all(len(row) == 4 for row in got.to_dict()["transfer_matrix_rowmajor_re_im"])


def test_equal_area_equivalent_single_17cm_and_area_change():
    base = prepare_graph(fixture(b_area=3e-4))
    other = prepare_graph(fixture())
    got = observe_transfer(base, FS).matrix_numpy()
    single = UniformTube(length_m=0.17, area_m2=3e-4)
    z = 1.21 * 343 / 3e-4
    expected = np.diag([1, z]) @ single.transfer_matrix(FS) @ np.diag([1, 1/z])
    assert np.max(np.abs(got - expected)) <= 1e-10
    assert base.organs_in_path_order[0] == other.organs_in_path_order[0]
    assert base.blueprint_digest != other.blueprint_digest
    assert base.preparation_digest != other.preparation_digest
    assert np.max(np.abs(got - observe_transfer(other, FS).matrix_numpy())) > 1e-3


def test_energy_flux_law_kills_particle_velocity_mutation():
    prepared = prepare_graph(fixture())
    good = observe_transfer(prepared, FS).matrix_numpy()
    j = np.array([[0., 1.], [1., 0.]])
    pwr = np.conjugate(good.transpose(0, 2, 1)) @ j @ good
    analytic = json.loads((ROOT / "docs/research/og3-wolfram-gate-a-result.json").read_text())
    assert np.max(np.abs(pwr - j)) <= analytic["flux_control"]["absolute_tolerance"]
    assert np.max(np.abs(np.linalg.det(good) - 1)) < 1e-10
    a, b = prepared.tubes_in_path_order
    z = a.characteristic_impedance_pa_s_m3
    wrong = (np.diag([1, z]) @ a.transfer_matrix(FS) @
             np.diag([1, a.area_m2 / b.area_m2]) @
             b.transfer_matrix(FS) @ np.diag([1, 1/z]))
    wrong_pwr = np.conjugate(wrong.transpose(0, 2, 1)) @ j @ wrong
    defects = np.max(np.abs(wrong_pwr - j), axis=(1, 2))
    assert np.all(defects > 1e-3)
    assert np.all(np.abs(defects - 0.5) <= 1e-12)
    swapped = (np.diag([1, z]) @ b.transfer_matrix(FS) @
               a.transfer_matrix(FS) @ np.diag([1, 1/z]))
    assert np.max(np.abs(swapped - good)) > 1e-3


def test_canonical_identity_roundtrip_exact_revision_and_terminal_metadata():
    bp = fixture()
    p = prepare_graph(bp)
    assert p.blueprint_digest == prepare_graph(replace(bp, organs=tuple(reversed(bp.organs)))).blueprint_digest
    assert p.preparation_digest == prepare_graph(replace(bp, organs=tuple(reversed(bp.organs)))).preparation_digest
    assert p.preparation_digest != prepare_graph(fixture(b_revision="r2")).preparation_digest
    assert p.blueprint_digest != prepare_graph(fixture(b_revision="r2")).blueprint_digest
    old = observe_transfer(p, FS)
    loaded = prepare_graph(fixture(termination="pressure_release"))
    assert p.preparation_digest != loaded.preparation_digest
    assert np.array_equal(observe_transfer(loaded, FS).matrix_numpy(), old.matrix_numpy())
    snapshot = json.loads(json.dumps(p.to_snapshot()))
    restored = restore_prepared(snapshot)
    assert restored.preparation_digest == p.preparation_digest
    assert observe_transfer(restored, FS).observation_digest == old.observation_digest
    assert p.preparation_digest == old.preparation_digest
    with pytest.raises(GraphError, match="SNAPSHOT_DIGEST_MISMATCH"):
        restore_prepared({**snapshot, "preparation_digest": "sha256:wrong"})


def test_signed_zero_same_bytes_response_and_observation_hash():
    p = prepare_graph(fixture())
    plus = observe_transfer(p, [0.0, 80.0])
    minus = observe_transfer(p, [-0.0, 80.0])
    assert minus.frequencies_hz == plus.frequencies_hz
    assert minus.observation_digest == plus.observation_digest
    assert np.array_equal(minus.matrix_numpy(), plus.matrix_numpy())
    assert np.array_equal(minus.matrix_numpy()[0], np.eye(2))
    assert observe_transfer(p, [80.0, 0.0]).observation_digest != plus.observation_digest
    # Rebuild the specified hash bytes using public results and a literal zero
    # encoding; equal Python floats alone would not detect negative-zero bits.
    for frequency in (0.0, -0.0):
        result = observe_transfer(p, [frequency])
        assert struct.pack(">d", result.frequencies_hz[0]).hex() == "0000000000000000"
        payload = {
            "domain": "morphoacoustics.og3.observation.v1",
            "backend": result.backend_id, "prepared": p.preparation_digest,
            "kind": "unloaded_full_complex_two_port",
            "frequencies_be64": ["0000000000000000"],
            "matrix_re_im_be64": [
                [[struct.pack(">d", re).hex(), struct.pack(">d", im).hex()]
                 for re, im in row] for row in result.rows_re_im
            ],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        assert result.observation_digest == "sha256:" + hashlib.sha256(encoded).hexdigest()


def test_frequency_refusal_outside_explicit_capability_not_plausible_matrix():
    p = prepare_graph(fixture())
    for values, status in [
        ([4000.0001], "UNSUPPORTED"), ([100000.0], "UNSUPPORTED"),
        ([-1.0], "INVALID"), ([float("nan")], "INVALID"),
        ([float("inf")], "INVALID"), ([], "INVALID"),
        ([[80.0]], "INVALID"), (80.0, "INVALID"),
        (["80"], "INVALID"), ([True], "INVALID"),
        ([0.0] * 4097, "UNSUPPORTED"),
        ([True, 80.0], "INVALID"), ([80.0, np.bool_(False)], "INVALID"),
        ([80.0, "200"], "INVALID"), ([80.0, 200j], "INVALID"),
        ([5000.0, float("nan")], "INVALID"),
        ([0.0] * 4096 + [-1.0], "INVALID"),
    ]:
        with pytest.raises(GraphError) as e:
            observe_transfer(p, values)
        assert e.value.status == status
    assert observe_transfer(p, [4000.0]).matrix_numpy().shape == (1, 2, 2)


@pytest.mark.parametrize("grid", [[733.0], [4000.0, 80.0, 4000.0], FS,
                                  np.linspace(0, 4000, 4096)])
def test_arbitrary_accepted_grid_preserves_every_requested_matrix(grid):
    p = prepare_graph(fixture())
    result = observe_transfer(p, grid)
    assert result.matrix_numpy().shape == (len(grid), 2, 2)
    assert list(result.frequencies_hz) == list(grid)
    for index in (0, len(grid)-1):
        assert np.array_equal(result.matrix_numpy()[index],
                              observe_transfer(p, [grid[index]]).matrix_numpy()[0])


@pytest.mark.parametrize("grid,code", [
    ([0.] * 4097, "FREQUENCY_RESOURCE_LIMIT"),
    ([5000.] * 4097, "FREQUENCY_RESOURCE_LIMIT"),
    ([5000.], "FREQUENCY_CAPABILITY"),
])
def test_resource_then_frequency_capability_diagnostics(grid, code):
    with pytest.raises(GraphError) as ex:
        observe_transfer(prepare_graph(fixture()), grid)
    assert ex.value.status == "UNSUPPORTED"
    assert ex.value.code == code


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("field", ["length_m", "area_m2", "air_density_kg_m3", "sound_speed_m_s"])
def test_each_off_fixture_positive_quantity_is_unsupported(index, field):
    bp = fixture()
    organs = list(bp.organs)
    value = float(getattr(organs[index], field))
    organs[index] = replace(organs[index], **{field: float(np.nextafter(value, np.inf))})
    changed = replace(bp, organs=tuple(organs))
    validate_graph(changed)  # legal geometry, outside this backend's profile
    with pytest.raises(GraphError) as ex:
        prepare_graph(changed)
    assert ex.value.status == "UNSUPPORTED"


def test_large_area_shared_medium_and_reversed_physical_path_are_unsupported():
    bp = fixture()
    a, b = bp.organs
    cases = [
        replace(bp, organs=(a, replace(b, area_m2=0.1))),
        replace(bp, organs=(replace(a, sound_speed_m_s=350.), replace(b, sound_speed_m_s=350.))),
        replace(bp, organs=(replace(a, air_density_kg_m3=1.2), replace(b, air_density_kg_m3=1.2))),
        replace(bp, source_port=b.inlet.id, load_ports=(a.outlet.id,),
                junctions=(replace(bp.junctions[0], ports=(b.outlet.id, a.inlet.id)),)),
    ]
    for changed in cases:
        validate_graph(changed)
        with pytest.raises(GraphError) as ex:
            prepare_graph(changed)
        assert ex.value.status == "UNSUPPORTED"


def test_profile_uses_resolved_path_not_names_and_both_terminations_work():
    for area in (3e-4, 6e-4):
        for terminal in ("matched", "pressure_release"):
            bp = fixture(b_area=area, b_revision="historical-r7", termination=terminal)
            a, b = bp.organs
            renamed = replace(bp, organs=(replace(b, id="named-last"), replace(a, id="named-first")))
            prepared = prepare_graph(renamed)
            assert prepared.organs_in_path_order[0].id == "named-first"
            assert np.array_equal(observe_transfer(prepared, FS).matrix_numpy(),
                                  observe_transfer(prepare_graph(bp), FS).matrix_numpy())


def test_snapshot_and_prepared_constructor_cannot_bypass_profile(monkeypatch):
    import morphoacoustics_graph.preparation as api
    p = prepare_graph(fixture())
    bp = replace(p.blueprint, organs=(p.blueprint.organs[0],
                 replace(p.blueprint.organs[1], area_m2=0.1)))
    snapshot = p.to_snapshot()
    snapshot["blueprint"] = graph_to_dict(bp)
    def no_transfer(*args, **kwargs):
        pytest.fail("refused input reached the numerical transfer primitive")
    monkeypatch.setattr(UniformTube, "transfer_matrix", no_transfer)
    with pytest.raises(GraphError) as ex:
        restore_prepared(snapshot)
    assert ex.value.status == "UNSUPPORTED"
    with pytest.raises(GraphError) as ex:
        observe_transfer(replace(p, blueprint=bp), FS)
    assert ex.value.status == "UNSUPPORTED"
    bad = replace(p, tubes_in_path_order=(p.tubes_in_path_order[0],
                                        replace(p.tubes_in_path_order[1], area_m2=0.1)))
    with pytest.raises(GraphError, match="PREPARED_BINDING_MISMATCH"):
        observe_transfer(bad, FS)
    with pytest.raises(GraphError) as ex:
        restore_prepared({**p.to_snapshot(), "backend_id": "og3.fixed.passive.serial2.pu.v1"})
    assert ex.value.status == "UNSUPPORTED"


@pytest.mark.parametrize("mutate,code", [
    (lambda p: replace(p, schema="other"), "UNKNOWN_SCHEMA"),
    (lambda p: replace(p, organs=(p.organs[0],p.organs[0])), "DUPLICATE_ORGAN"),
    (lambda p: replace(p, organs=(replace(p.organs[0],area_m2=0),p.organs[1])), "NONPOSITIVE_OR_NONFINITE"),
    (lambda p: replace(p, organs=(replace(p.organs[0],area_m2=1e-320),p.organs[1])), "NONFINITE_DERIVED_IMPEDANCE"),
    (lambda p: replace(p, organs=(replace(p.organs[0],area_m2=float("nan")),p.organs[1])), "NONPOSITIVE_OR_NONFINITE"),
    (lambda p: replace(p, organs=(replace(p.organs[0],area_m2=True),p.organs[1])), "BAD_NUMERIC_TYPE"),
    (lambda p: replace(p, organs=(replace(p.organs[1], inlet=replace(p.organs[1].inlet,kind="mechanical.force_velocity")),p.organs[0])), "WRONG_PORT_KIND"),
    (lambda p: replace(p, organs=(replace(p.organs[1], inlet=replace(p.organs[1].inlet,direction="outlet")),p.organs[0])), "WRONG_PORT_DIRECTION"),
    (lambda p: replace(p, source_port="missing"), "UNKNOWN_SOURCE_PORT"),
    (lambda p: replace(p, load_ports=("missing",)), "UNKNOWN_LOAD_PORT"),
    (lambda p: replace(p, junctions=(replace(p.junctions[0],ports=("organ-B.in","organ-A.out")),)), "WRONG_EDGE_DIRECTION"),
    (lambda p: replace(p, junctions=(replace(p.junctions[0],ports=("organ-A.out","organ-A.in")),)), "DUPLICATE_CONNECTION"),
    (lambda p: replace(p, junctions=(replace(p.junctions[0],law="mechanical"),)), "UNKNOWN_LAW"),
])
def test_invalid_topology_or_physics_fails_closed(mutate, code):
    with pytest.raises(GraphError) as ex:
        prepare_graph(mutate(fixture()))
    assert ex.value.status == "INVALID"
    assert ex.value.code == code


def test_legal_three_port_branch_is_unsupported_not_invalid():
    p = fixture()
    c = PassiveTubeOrgan("organ-C", "r1", 0.07, 4e-4,
                         AcousticPort("organ-C.in", "inlet"),
                         AcousticPort("organ-C.out", "outlet"))
    branch = replace(
        p, organs=(*p.organs, c),
        junctions=(AcousticJunction("branch-ABC", BRANCH_LAW,
                                  ("organ-A.out", "organ-B.in", "organ-C.in")),),
        load_ports=("organ-B.out", "organ-C.out")
    )
    validate_graph(branch)
    with pytest.raises(GraphError) as ex:
        prepare_graph(branch)
    assert ex.value.status == "UNSUPPORTED"


def test_mixed_medium_unsupported():
    p = fixture()
    b = replace(p.organs[1], sound_speed_m_s=350.0)
    with pytest.raises(GraphError) as ex:
        prepare_graph(replace(p, organs=(p.organs[0], b)))
    assert ex.value.status == "UNSUPPORTED"


def test_production_module_has_no_experiment_runtime_import():
    from morphoacoustics_graph import preparation as pg
    assert "experiments/039" not in pg.__file__


def test_long_valid_graph_refuses_typed_unsupported_without_recursion_failure():
    """Codex P1 regression: long valid graph may be unsupported, never crash."""
    length = 1205  # exceeds the usual Python recursion limit; small runtime cost
    nodes = tuple(
        PassiveTubeOrgan(
            f"long-node-{i}", "r1", 0.08, 3e-4,
            AcousticPort(f"long-node-{i}.in", "inlet"),
            AcousticPort(f"long-node-{i}.out", "outlet"),
        )
        for i in range(length)
    )
    edges = tuple(
        AcousticJunction(
            f"long-edge-{i}", SERIES_LAW,
            (nodes[i].outlet.id, nodes[i + 1].inlet.id),
        )
        for i in range(length - 1)
    )
    graph = OrganGraphBlueprint(
        SCHEMA, nodes, edges, nodes[0].inlet.id,
        (nodes[-1].outlet.id,), "matched",
    )
    validate_graph(graph)
    with pytest.raises(GraphError) as ex:
        prepare_graph(graph)
    assert (ex.value.status, ex.value.code) == ("UNSUPPORTED", "FIXED2_SERIAL_ONLY")

    # Still check all structural data before the unsupported-capability refusal.
    malformed = replace(
        graph,
        organs=nodes[:-1] + (replace(nodes[-1], area_m2=-3e-4),),
    )
    with pytest.raises(GraphError) as ex:
        prepare_graph(malformed)
    assert ex.value.status == "INVALID"
    assert ex.value.code == "NONPOSITIVE_OR_NONFINITE"
