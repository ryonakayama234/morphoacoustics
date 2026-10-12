"""Research-only automated checks for OG-0 (#90). NOT independently adopted."""
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from morphoacoustics.acoustics import UniformTube, SegmentedTube

HERE = Path(__file__).resolve().parents[1]
MODEL_FILE = HERE / "experiments/030_og0_passive_port_connection/port_network.py"
ORACLE_FILE = HERE / "tests/scientific/oracles/og0_wolfram.json"
m_spec = importlib.util.spec_from_file_location("og0_port_network_under_test", MODEL_FILE)
assert m_spec is not None and m_spec.loader is not None
og = importlib.util.module_from_spec(m_spec)
sys.modules[m_spec.name] = og
m_spec.loader.exec_module(og)
oracle = json.loads(ORACLE_FILE.read_text(encoding="utf-8"))
frequencies = np.asarray(oracle["frequency_grid_hz"], dtype=float)


def normalized(matrix, impedance):
    result = matrix.copy()
    result[..., 0, 1] /= impedance
    result[..., 1, 0] *= impedance
    return result


def test_equal_area_actual_port_graph_matches_existing_solvers():
    graph = og.prepare_serial_graph(og.reference_spec())
    measured = graph.transfer_matrix(frequencies)
    sections = (graph._tube(graph.upstream), graph._tube(graph.downstream))
    direct = UniformTube(length_m=0.17, area_m2=3e-4,
                         sound_speed_m_s=343., air_density_kg_m3=1.2)
    zref = 1.2*343/3e-4
    np.testing.assert_allclose(
        normalized(measured, zref), normalized(direct.transfer_matrix(frequencies), zref),
        rtol=1e-11, atol=1e-11,
    )
    np.testing.assert_allclose(
        normalized(measured, zref),
        normalized(SegmentedTube(sections).transfer_matrix(frequencies), zref),
        rtol=1e-11, atol=1e-11,
    )
    np.testing.assert_allclose(np.linalg.det(normalized(measured, zref)), 1.,
                               rtol=1e-11, atol=1e-11)
    assert direct.quarter_wave_resonances_hz(1)[0] == pytest.approx(
        oracle["equal_area"]["first_quarter_wave_hz"], abs=1e-10)


def test_unequal_area_matches_wolfram_impedance_and_independent_recursion():
    graph = og.prepare_serial_graph(og.reference_spec(downstream_area_m2=6e-4))
    actual = graph.input_impedance(np.asarray([733.0]))[0]
    expected = oracle["area_mismatch"]
    assert actual.real == pytest.approx(expected["pressure_release_733hz_input_impedance_real"], abs=1e-8)
    assert actual.imag == pytest.approx(expected["pressure_release_733hz_input_impedance_imag"], rel=1e-10, abs=1e-4)
    # Independently unwind load impedance downstream -> upstream.
    zin = 0j
    for organ in (graph.downstream, graph.upstream):
        zc = graph.air_density_kg_m3 * graph.sound_speed_m_s / organ.area_m2
        tangent = np.tan(2*np.pi*733.0*organ.length_m/graph.sound_speed_m_s)
        zin = zc * (zin + 1j*zc*tangent) / (zc + 1j*zin*tangent)
    assert actual == pytest.approx(zin, rel=1e-10, abs=1e-4)


def test_matched_junction_port_conservation_and_scattering():
    graph = og.prepare_serial_graph(og.reference_spec(downstream_area_m2=6e-4))
    expected = oracle["area_mismatch"]["matched_outlet_733hz"]
    result = graph.junction_audit(733., outlet_flow_m3_s=1e-6, outlet_load="matched")
    for k in ("pressure_residual_rel", "flow_residual_rel", "power_residual_rel"):
        assert result[k] < 1e-11
    assert result["mean_power_w"] == pytest.approx(expected["mean_power_w"], rel=1e-12, abs=1e-15)
    for k in ("junction_pressure_real_pa", "junction_pressure_imag_pa",
              "junction_flow_real_m3_s", "junction_flow_imag_m3_s"):
        assert result[k] == pytest.approx(expected[k], rel=1e-11, abs=1e-12)
    reflection = complex(result["reflection_pressure_real"], result["reflection_pressure_imag"])
    assert reflection == pytest.approx(complex(oracle["area_mismatch"]["reflection_pressure_real"]), abs=1e-12)
    za, zb = 1.2*343/3e-4, 1.2*343/6e-4
    transmission_power = 4*za*zb/(za+zb)**2
    assert abs(reflection)**2 == pytest.approx(oracle["area_mismatch"]["reflected_power_fraction"], abs=1e-12)
    assert transmission_power == pytest.approx(oracle["area_mismatch"]["transmitted_power_fraction"], abs=1e-12)
    assert abs(reflection)**2 + transmission_power == pytest.approx(1., abs=1e-12)


def test_graph_provenance_identity_and_causal_intervention():
    g1 = og.prepare_serial_graph(og.reference_spec(organ_order=("A", "B")))
    g2 = og.prepare_serial_graph(og.reference_spec(organ_order=("B", "A")))
    assert g1.graph_sha256 == g2.graph_sha256
    np.testing.assert_array_equal(g1.transfer_matrix(frequencies), g2.transfer_matrix(frequencies))
    changed = og.prepare_serial_graph(og.reference_spec(downstream_area_m2=6e-4))
    assert changed.graph_sha256 != g1.graph_sha256
    assert changed.upstream == g1.upstream
    assert not np.allclose(
        normalized(changed.transfer_matrix(frequencies), 1.372e6),
        normalized(g1.transfer_matrix(frequencies), 1.372e6),
        rtol=1e-6, atol=1e-6)


def test_bad_port_role_kind_identity_connection_and_boundary_are_invalid():
    spec = og.reference_spec()
    to = spec.connections[0].target
    from_port = spec.connections[0].source
    bad_edges = (
        og.AcousticConnection(og.AcousticPort("A", "inlet", "inlet"), to),
        og.AcousticConnection(og.AcousticPort("A", "outlet", "outlet", kind="mechanical"), to),
        og.AcousticConnection(og.AcousticPort("X", "outlet", "outlet"), to),
        og.AcousticConnection(from_port, from_port),
        og.AcousticConnection(from_port, to, law="nonphysical"),
    )
    for edge in bad_edges:
        with pytest.raises(og.InvalidGraph):
            og.prepare_serial_graph(og.PortNetworkSpec(
                spec.organs, (edge,), spec.observation_inlet, spec.pressure_release_outlet))
    with pytest.raises(og.InvalidGraph):
        og.prepare_serial_graph(og.PortNetworkSpec(
            spec.organs, (), spec.observation_inlet, spec.pressure_release_outlet))
    with pytest.raises(og.InvalidGraph):
        og.prepare_serial_graph(og.PortNetworkSpec(
            spec.organs, spec.connections*2, spec.observation_inlet, spec.pressure_release_outlet))
    with pytest.raises(og.InvalidGraph):
        og.prepare_serial_graph(og.PortNetworkSpec(
            spec.organs, spec.connections, to, spec.pressure_release_outlet))


def test_geometry_and_frequency_invalid_multi_organ_unsupported():
    for value in (0., -1., np.nan, np.inf):
        with pytest.raises(og.InvalidGraph):
            og.RigidTubeOrgan("X", 0.1, value)
    spec = og.reference_spec()
    with pytest.raises(og.InvalidGraph):
        og.prepare_serial_graph(og.PortNetworkSpec(
            (spec.organs[0], spec.organs[0]), spec.connections,
            spec.observation_inlet, spec.pressure_release_outlet))
    with pytest.raises(og.UnsupportedGraph):
        og.prepare_serial_graph(og.PortNetworkSpec(
            spec.organs + (og.RigidTubeOrgan("C", 0.1, 1e-4),), spec.connections,
            spec.observation_inlet, spec.pressure_release_outlet))
    graph = og.prepare_serial_graph(spec)
    for grid in ([], [-1.], [np.nan], [np.inf], [[100., 200.]]):
        with pytest.raises(og.InvalidGraph):
            graph.transfer_matrix(grid)
    with pytest.raises(og.InvalidGraph):
        graph.junction_audit(733., outlet_flow_m3_s=0j)


def test_rewiring_port_edge_changes_asymmetric_network_response():
    original = og.reference_spec(downstream_area_m2=6e-4)
    forward = og.prepare_serial_graph(original)
    reverse_edge = og.AcousticConnection(
        og.AcousticPort("B", "outlet", "outlet"),
        og.AcousticPort("A", "inlet", "inlet"),
    )
    reversed_network = og.prepare_serial_graph(og.PortNetworkSpec(
        original.organs,
        (reverse_edge,),
        og.AcousticPort("B", "inlet", "inlet"),
        og.AcousticPort("A", "outlet", "outlet"),
    ))
    assert forward.graph_sha256 != reversed_network.graph_sha256
    assert reversed_network.upstream.organ_id == "B"
    assert not np.allclose(
        normalized(forward.transfer_matrix(frequencies), 1.372e6),
        normalized(reversed_network.transfer_matrix(frequencies), 1.372e6),
        rtol=1e-6, atol=1e-6,
    )


def test_runner_executes_and_emits_provisional_result_json():
    import subprocess
    runner = HERE / "experiments/030_og0_passive_port_connection/run.py"
    result = subprocess.run([sys.executable, str(runner)], capture_output=True,
                            text=True, check=True, timeout=30)
    payload = json.loads(result.stdout)
    assert payload["status"] == "PROVISIONAL_NUMERICAL_PASS"
    assert payload["review_status"] == "NOT_INDEPENDENTLY_REVIEWED"
    assert payload["adoption_status"] == "NOT_ADOPTED"
    assert len(payload["run_identity_sha256"]) == 64
    assert all(payload["checks"].values())


# Amendment 01: new, separately derived traveling-wave scattering oracle.
# These tests are POST-exploratory regression checks, not preregistered evidence.
WAVE_ORACLE_FILE = HERE / "tests/scientific/oracles/og0_wave_amendment01_wolfram.json"
wave_oracle = json.loads(WAVE_ORACLE_FILE.read_text(encoding="utf-8"))


def incident_wave_states(graph, grid, incident_pressure):
    """Wave-basis oracle: never compose, invert or recurse tube matrices.

    Unit incident traveling pressure at the physical A.out junction;
    phase shifts to A.in and B.out are analytical exp(±i*k*L).
    """
    za = graph.air_density_kg_m3 * graph.sound_speed_m_s / graph.upstream.area_m2
    zb = graph.air_density_kg_m3 * graph.sound_speed_m_s / graph.downstream.area_m2
    reflection = (zb - za) / (za + zb)
    transmission = 2 * zb / (za + zb)
    phase_a = 2 * np.pi * grid * graph.upstream.length_m / graph.sound_speed_m_s
    phase_b = 2 * np.pi * grid * graph.downstream.length_m / graph.sound_speed_m_s
    incident = complex(incident_pressure)
    downstream_wave = transmission * incident * np.exp(-1j * phase_b)
    expected_inlet = np.stack((
        incident * (np.exp(1j * phase_a) + reflection * np.exp(-1j * phase_a)),
        incident * (np.exp(1j * phase_a) - reflection * np.exp(-1j * phase_a)) / za,
    ), axis=-1)
    imposed_outlet = np.stack((downstream_wave, downstream_wave / zb), axis=-1)
    return imposed_outlet, expected_inlet, za, reflection, transmission


def max_wave_residual(graph, matrices, grid, incident_pressure):
    state_out, independent_state_in, za, _, _ = incident_wave_states(
        graph, grid, incident_pressure)
    measured = np.einsum("nij,nj->ni", matrices, state_out)
    scales = np.asarray([abs(incident_pressure), abs(incident_pressure) / za])
    return float(np.max(np.abs((measured - independent_state_in) / scales)))


@pytest.mark.parametrize("area_b", [3e-4, 6e-4, 1.5e-4])
def test_independent_traveling_wave_scattering_across_frequency_grid(area_b):
    graph = og.prepare_serial_graph(og.reference_spec(downstream_area_m2=area_b))
    incident = complex(*wave_oracle["incident_pressure_pa_re_im"])
    state_out, expected_inlet, za, reflection, transmission = incident_wave_states(
        graph, frequencies, incident)
    measured = np.einsum("nij,nj->ni", graph.transfer_matrix(frequencies), state_out)
    scales = [abs(incident), abs(incident) / za]
    assert np.max(np.abs((measured - expected_inlet) / scales)) < 1e-11
    # Independent scattering identity, based on p/U port wave boundary equations.
    assert abs(reflection)**2 + za * abs(transmission)**2 / (
        graph.air_density_kg_m3 * graph.sound_speed_m_s / area_b
    ) == pytest.approx(1.0, abs=1e-12)
    if area_b == 6e-4:
        assert reflection == pytest.approx(wave_oracle["reflection_pressure"], abs=1e-12)
        assert transmission == pytest.approx(wave_oracle["transmission_pressure"], abs=1e-12)
        a_at_733 = measured[list(frequencies).index(733)]
        expected_four = wave_oracle["a_in_733_re_im_pa_and_m3_s"]
        np.testing.assert_allclose(
            [a_at_733[0].real, a_at_733[0].imag,
             a_at_733[1].real, a_at_733[1].imag],
            expected_four, atol=1e-11, rtol=1e-11)


def test_area_scaled_wrong_junction_is_killed_by_independent_wave_oracle():
    graph = og.prepare_serial_graph(og.reference_spec(downstream_area_m2=6e-4))
    incident = complex(*wave_oracle["incident_pressure_pa_re_im"])
    good_error = max_wave_residual(graph, graph.transfer_matrix(frequencies),
                                   frequencies, incident)
    assert good_error < 1e-11
    # Deliberately INVALID physical coupling: conserve particle speed instead
    # of volume velocity, via the spurious junction step J!=Identity.
    wrong_junction = np.diag([
        1.0, graph.upstream.area_m2 / graph.downstream.area_m2,
    ]).astype(np.complex128)
    ta = graph._tube(graph.upstream).transfer_matrix(frequencies)
    tb = graph._tube(graph.downstream).transfer_matrix(frequencies)
    invalid_model_matrices = np.matmul(np.matmul(ta, wrong_junction), tb)
    wrong_error = max_wave_residual(
        graph, invalid_model_matrices, frequencies, incident)
    assert wrong_error > wave_oracle["mutation_min_normalized_residual"]
    assert wrong_error > 1e8 * max(good_error, 1e-16)


def test_pressure_release_is_zero_power_at_terminal_not_matched_load():
    graph = og.prepare_serial_graph(og.reference_spec(downstream_area_m2=6e-4))
    release = graph.junction_audit(
        733., outlet_flow_m3_s=1e-6, outlet_load="pressure_release")
    matched = graph.junction_audit(
        733., outlet_flow_m3_s=1e-6, outlet_load="matched")
    # A pressure-release terminal has p=0 hence Pavg(out)=0.
    assert release["mean_power_w"] == pytest.approx(0., abs=1e-13)
    assert matched["mean_power_w"] == pytest.approx(3.43e-7, rel=1e-10)
