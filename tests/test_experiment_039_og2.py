"""Independent gates for OG-2 experiment-local physics; no public API changes."""
from __future__ import annotations

from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

from morphoacoustics.acoustics import UniformTube


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "039_og2_prepared_graph"
spec = importlib.util.spec_from_file_location("experiment_039_og2", EXP / "og2.py")
assert spec is not None and spec.loader is not None
og2 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = og2
spec.loader.exec_module(og2)

ORACLE = json.loads((EXP / "wolfram" / "og2_oracle.json").read_text(encoding="utf-8"))
GRID = np.asarray(ORACLE["frequencies_hz"], dtype=float)
DIMENSIONLESS_TOL = 1e-10
POWER_TOL = 1e-12


def expected_wolfram_matrices() -> np.ndarray:
    value = np.asarray(ORACLE["normalized_matrix_rowmajor_re_im"], dtype=float)
    return (value[..., 0] + 1j * value[..., 1]).reshape(-1, 2, 2)


def test_equal_area_complex_transfer_and_preserved_identities() -> None:
    prepared = og2.prepare(og2.fixture(area_b=0.0003))
    assert prepared.backend_id == og2.BACKEND_ID
    assert [n.id for n in prepared.organs_in_path_order] == ["organ-A", "organ-B"]
    assert prepared.junction.id == "edge-AB"
    assert prepared.junction.ports == ("organ-A.out", "organ-B.in")
    assert prepared.port_mapping == (
        ("organ-A", "organ-A.in", "organ-A.out"),
        ("organ-B", "organ-B.in", "organ-B.out"),
    )
    single = UniformTube(length_m=0.17, area_m2=0.0003)
    z = prepared.reference_impedance
    d = np.diag([1.0, z])
    di = np.diag([1.0, 1.0 / z])
    expected = d @ single.transfer_matrix(GRID) @ di
    measured = prepared.scaled_transfer_matrix(GRID)
    assert measured.shape == (7, 2, 2)
    assert np.max(np.abs(measured - expected)) <= DIMENSIONLESS_TOL


def test_mismatch_matches_independently_frozen_wolfram_full_complex_ports() -> None:
    prepared = og2.prepare(og2.fixture())
    measured = prepared.scaled_transfer_matrix(GRID)
    assert np.max(np.abs(measured - expected_wolfram_matrices())) <= DIMENSIONLESS_TOL


def test_matched_isolated_interface_scattering_power_with_separate_B_area() -> None:
    prepared = og2.prepare(og2.fixture())
    obtained = prepared.interface_scattering()
    wanted = (-1.0 / 3.0, 2.0 / 3.0, 1.0 / 9.0, 8.0 / 9.0)
    assert max(abs(a - b) for a, b in zip(obtained, wanted)) <= POWER_TOL
    assert abs(obtained[2] + obtained[3] - 1.0) <= POWER_TOL
    assert prepared.organs_in_path_order[0].area_m2 == 0.0003
    assert prepared.organs_in_path_order[1].area_m2 == 0.0006


def test_wrong_particle_velocity_coupling_is_killed_by_wolfram_oracle() -> None:
    prepared = og2.prepare(og2.fixture())
    a, b = prepared.tubes_in_path_order
    z = prepared.reference_impedance
    d = np.diag([1.0, z])
    di = np.diag([1.0, 1.0 / z])
    wrong_junction = np.diag([1.0, a.area_m2 / b.area_m2])
    wrong = d @ (a.transfer_matrix(GRID) @ wrong_junction @ b.transfer_matrix(GRID)) @ di
    assert np.max(np.abs(wrong - expected_wolfram_matrices())) > 1e-3
    # An incorrect particle-velocity junction predicts r=0, not -1/3.
    assert abs(0.0 - prepared.interface_scattering()[0]) > 1e-3


def test_reversing_mismatch_tube_order_is_killed() -> None:
    prepared = og2.prepare(og2.fixture())
    a, b = prepared.tubes_in_path_order
    z = prepared.reference_impedance
    d = np.diag([1.0, z])
    di = np.diag([1.0, 1.0 / z])
    wrong = d @ (b.transfer_matrix(GRID) @ a.transfer_matrix(GRID)) @ di
    assert np.max(np.abs(wrong - expected_wolfram_matrices())) > 1e-3


@pytest.mark.parametrize(
    ("bad", "code"),
    [
        (lambda p: replace(p, schema="unknown"), "UNKNOWN_SCHEMA"),
        (lambda p: replace(p, organs=(p.organs[0], p.organs[0])), "DUPLICATE_ORGAN"),
        (lambda p: replace(p, organs=(replace(p.organs[0], area_m2=0.0),p.organs[1])), "NONPOSITIVE_OR_NONFINITE"),
        (lambda p: replace(p, organs=(replace(p.organs[0], area_m2=float("nan")),p.organs[1])), "NONPOSITIVE_OR_NONFINITE"),
        (lambda p: replace(p, organs=(replace(p.organs[1], length_m=float("inf")),p.organs[0])), "NONPOSITIVE_OR_NONFINITE"),
        (lambda p: replace(p, organs=(replace(p.organs[1], sound_speed_m_s=-343.0),p.organs[0])), "NONPOSITIVE_OR_NONFINITE"),
        (lambda p: replace(p, organs=(replace(p.organs[1], inlet=replace(p.organs[1].inlet, kind="mechanical.force_velocity")),p.organs[0])), "WRONG_PORT_KIND"),
        (lambda p: replace(p, organs=(replace(p.organs[1], inlet=replace(p.organs[1].inlet, direction="outlet")),p.organs[0])), "WRONG_PORT_DIRECTION"),
        (lambda p: replace(p, source_port="unknown.in"), "UNKNOWN_SOURCE_PORT"),
        (lambda p: replace(p, load_ports=()), "MISSING_LOAD"),
        (lambda p: replace(p, load_ports=("organ-B.in",)), "WRONG_LOAD_DIRECTION"),
        (lambda p: replace(p, junctions=(replace(p.junctions[0], ports=("organ-B.in", "organ-A.out")),)), "WRONG_EDGE_DIRECTION"),
        (lambda p: replace(p, junctions=(replace(p.junctions[0], ports=("organ-A.out", "ghost.in")),)), "UNKNOWN_EDGE_PORT"),
        (lambda p: replace(p, junctions=(replace(p.junctions[0], law="unknown"),)), "UNKNOWN_JUNCTION_LAW"),
        (lambda p: replace(p, junctions=(p.junctions[0], p.junctions[0])), "DUPLICATE_JUNCTION"),
        (lambda p: replace(p, load_ports=("organ-B.out","organ-B.out")), "DUPLICATE_CONNECTION"),
        (lambda p: replace(p, termination="fictional"), "UNKNOWN_TERMINATION"),
    ],
)
def test_invalid_structure_is_rejected_with_diagnostic(bad, code: str) -> None:
    with pytest.raises(og2.GraphError) as caught:
        og2.prepare(bad(og2.fixture()))
    assert caught.value.status == "INVALID"
    assert caught.value.code == code
    assert caught.value.path
    assert caught.value.status != "INFEASIBLE"


def test_missing_port_is_invalid_not_silently_repaired() -> None:
    base = og2.fixture()
    broken = replace(base, junctions=(replace(base.junctions[0], ports=("organ-A.out", "organ-A.in")),))
    with pytest.raises(og2.GraphError) as caught:
        og2.prepare(broken)
    assert caught.value.status == "INVALID"


def test_valid_three_way_branch_is_unsupported_not_invalid_or_infeasible() -> None:
    valid_branch = og2.branch_fixture()
    og2.validate(valid_branch)
    with pytest.raises(og2.GraphError) as caught:
        og2.prepare(valid_branch)
    assert caught.value.status == "UNSUPPORTED"
    assert caught.value.code == "SERIAL_BACKEND_ONLY"


def test_mixed_medium_is_unsupported_not_auto_converted() -> None:
    base = og2.fixture()
    b = replace(base.organs[1], air_density_kg_m3=1.2)
    with pytest.raises(og2.GraphError) as caught:
        og2.prepare(replace(base, organs=(base.organs[0], b)))
    assert caught.value.status == "UNSUPPORTED"
    assert caught.value.code == "MIXED_MEDIUM"


def test_prepared_graph_digest_determinism_and_independent_intervention() -> None:
    original = og2.fixture()
    first = og2.prepare(original)
    again = og2.prepare(og2.fixture())
    reversed_input_tuple = og2.prepare(replace(original, organs=tuple(reversed(original.organs))))
    assert first.preparation_digest == again.preparation_digest
    assert first.preparation_digest == reversed_input_tuple.preparation_digest
    assert np.array_equal(first.transfer_matrix(GRID), again.transfer_matrix(GRID))
    changed_b = og2.prepare(og2.fixture(area_b=0.0005))
    changed_revision = og2.prepare(og2.fixture(revision_b="r2"))
    assert first.preparation_digest != changed_b.preparation_digest
    assert first.preparation_digest != changed_revision.preparation_digest
    assert first.organs_in_path_order[0] == changed_b.organs_in_path_order[0]
    assert first.organs_in_path_order[0] == changed_revision.organs_in_path_order[0]
    assert first.organs_in_path_order[1].area_m2 == 0.0006
    assert changed_b.organs_in_path_order[1].area_m2 == 0.0005
    assert og2.prepare(original).preparation_digest == first.preparation_digest


def test_outlet_boundary_is_explicit_not_confused_with_matched_power() -> None:
    matched = og2.prepare(og2.fixture())
    release = og2.prepare(og2.fixture(termination="pressure_release"))
    assert matched.outlet_load_impedance() == matched.tubes_in_path_order[-1].characteristic_impedance_pa_s_m3
    assert release.outlet_load_impedance() == 0.0
    assert matched.preparation_digest != release.preparation_digest
    assert np.array_equal(matched.transfer_matrix(GRID), release.transfer_matrix(GRID))
    assert abs(matched.interface_scattering()[2] + matched.interface_scattering()[3] - 1.0) < POWER_TOL
