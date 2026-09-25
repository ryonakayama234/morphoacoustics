import numpy as np
import pytest

from morphoacoustics.acoustics import (
    ImpedanceRequest,
    SegmentedTube,
    SegmentedTubeBackend,
    UniformTube,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection


def test_single_segment_matches_uniform_tube() -> None:
    uniform = UniformTube(length_m=0.17, area_m2=3e-4)
    segmented = SegmentedTube((uniform,))
    frequencies = np.array([100.0, 300.0, 700.0])

    np.testing.assert_allclose(
        segmented.transfer_matrix(frequencies),
        uniform.transfer_matrix(frequencies),
    )
    np.testing.assert_allclose(
        segmented.input_impedance(frequencies),
        uniform.input_impedance(frequencies),
    )


def test_equal_area_segments_compose_to_equivalent_uniform_tube() -> None:
    segmented = SegmentedTube(
        (
            UniformTube(length_m=0.08, area_m2=3e-4),
            UniformTube(length_m=0.09, area_m2=3e-4),
        )
    )
    equivalent = UniformTube(length_m=0.17, area_m2=3e-4)
    frequencies = np.linspace(50.0, 2000.0, 100)

    np.testing.assert_allclose(
        segmented.transfer_matrix(frequencies),
        equivalent.transfer_matrix(frequencies),
        rtol=1e-12,
        atol=1e-12,
    )


def _recursive_input_impedance(
    sections: tuple[UniformTube, ...],
    frequency_hz: float,
) -> complex:
    """Independent outlet-to-inlet impedance recursion for a pressure-release load."""

    load = 0.0j
    omega = 2.0 * np.pi * frequency_hz
    for section in reversed(sections):
        phase = omega * section.length_m / section.sound_speed_m_s
        tangent = np.tan(phase)
        zc = section.characteristic_impedance_pa_s_m3
        load = zc * (load + 1j * zc * tangent) / (zc + 1j * load * tangent)
    return complex(load)


def test_unequal_sections_preserve_inlet_to_outlet_order() -> None:
    inlet = UniformTube(length_m=0.061, area_m2=1.5e-4)
    outlet = UniformTube(length_m=0.109, area_m2=6.0e-4)
    frequency_hz = 733.0

    forward = SegmentedTube((inlet, outlet))
    reversed_tube = SegmentedTube((outlet, inlet))

    measured = forward.input_impedance(np.array([frequency_hz]))[0]
    expected = _recursive_input_impedance((inlet, outlet), frequency_hz)
    np.testing.assert_allclose(measured, expected, rtol=1e-12, atol=1e-9)

    reversed_impedance = reversed_tube.input_impedance(np.array([frequency_hz]))[0]
    assert not np.isclose(measured, reversed_impedance, rtol=1e-6, atol=1e-6)


def test_backend_response_detaches_and_freezes_observation_arrays() -> None:
    request_frequencies = np.array([500.0, 1000.0], dtype=np.float64)
    geometry = Tract1DGeometry(
        cavity_id="oral",
        sections=(TubeSection(length_m=0.17, area_m2=3e-4),),
    )

    response = SegmentedTubeBackend().simulate_snapshot(
        geometry,
        ImpedanceRequest(request_frequencies),
    )
    recorded_frequencies = response.frequencies_hz.copy()
    recorded_impedance = response.input_impedance_pa_s_m3.copy()

    request_frequencies[0] = 1234.0

    np.testing.assert_array_equal(response.frequencies_hz, recorded_frequencies)
    np.testing.assert_array_equal(
        response.input_impedance_pa_s_m3,
        recorded_impedance,
    )
    with pytest.raises(ValueError, match="read-only"):
        response.frequencies_hz[0] = 750.0
    with pytest.raises(ValueError, match="read-only"):
        response.input_impedance_pa_s_m3[0] = 0.0j
