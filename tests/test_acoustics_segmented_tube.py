import numpy as np

from morphoacoustics.acoustics import SegmentedTube, UniformTube


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
