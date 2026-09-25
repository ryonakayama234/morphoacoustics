import pytest

from morphoacoustics.physical import Tract1DGeometry, TubeSection


def test_tract1d_geometry_tracks_length_and_axial_sections() -> None:
    geometry = Tract1DGeometry(
        cavity_id="oral",
        sections=(
            TubeSection(length_m=0.02, area_m2=3e-4),
            TubeSection(length_m=0.03, area_m2=2e-4),
            TubeSection(length_m=0.05, area_m2=1e-4),
        ),
    )

    assert geometry.total_length_m == pytest.approx(0.10)
    assert geometry.axial_position_m(0.40) == pytest.approx(0.04)
    assert geometry.section_index_at(0.0) == 0
    assert geometry.section_index_at(0.40) == 1
    assert geometry.section_index_at(1.0) == 2


def test_internal_boundaries_belong_to_downstream_section() -> None:
    geometry = Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=0.25, area_m2=3e-4)
            for _ in range(4)
        ),
    )

    assert geometry.section_index_at(0.249999) == 0
    assert geometry.section_index_at(0.25) == 1
    assert geometry.section_index_at(0.50) == 2
    assert geometry.section_index_at(0.75) == 3
    assert geometry.section_index_at(1.0) == 3


def test_tube_section_rejects_nonphysical_dimensions() -> None:
    with pytest.raises(ValueError):
        TubeSection(length_m=0.0, area_m2=1e-4)
    with pytest.raises(ValueError):
        TubeSection(length_m=0.01, area_m2=0.0)
