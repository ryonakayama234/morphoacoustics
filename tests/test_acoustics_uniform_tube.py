import numpy as np
import pytest

from morphoacoustics.acoustics import UniformTube


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("length_m", 0.0),
        ("length_m", float("inf")),
        ("area_m2", -1.0),
        ("sound_speed_m_s", float("nan")),
        ("air_density_kg_m3", 0.0),
    ],
)
def test_uniform_tube_rejects_nonphysical_parameters(field: str, value: float) -> None:
    kwargs = {"length_m": 0.17, "area_m2": 3.0e-4, field: value}

    with pytest.raises(ValueError, match=field):
        UniformTube(**kwargs)


def test_transfer_matrix_preserves_frequency_shape() -> None:
    tube = UniformTube(length_m=0.17, area_m2=3.0e-4)

    scalar = tube.transfer_matrix(500.0)
    vector = tube.transfer_matrix(np.array([100.0, 500.0, 1000.0]))

    assert scalar.shape == (2, 2)
    assert vector.shape == (3, 2, 2)


def test_rejects_negative_frequency() -> None:
    tube = UniformTube(length_m=0.17, area_m2=3.0e-4)

    with pytest.raises(ValueError, match=">= 0"):
        tube.transfer_matrix([-1.0, 100.0])


def test_quarter_wave_count_must_be_positive_integer() -> None:
    tube = UniformTube(length_m=0.17, area_m2=3.0e-4)

    with pytest.raises(ValueError, match="positive integer"):
        tube.quarter_wave_resonances_hz(0)
