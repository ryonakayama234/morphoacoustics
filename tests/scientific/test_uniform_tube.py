import json
from pathlib import Path

import numpy as np

from morphoacoustics.acoustics import UniformTube


_ORACLE_PATH = Path(__file__).with_name("oracles") / "uniform_tube_quarter_wave_wolfram.json"


def _wolfram_oracle() -> dict[str, object]:
    return json.loads(_ORACLE_PATH.read_text(encoding="utf-8"))


def _estimate_pressure_release_resonance_hz(
    tube: UniformTube,
    expected_hz: float,
) -> tuple[float, float]:
    half_width_hz = min(40.0, expected_hz * 0.08)
    frequencies = np.linspace(
        expected_hz - half_width_hz,
        expected_hz + half_width_hz,
        20_000,
    )
    impedance = tube.input_impedance(frequencies)
    estimated = frequencies[int(np.argmax(np.abs(impedance)))]
    resolution = frequencies[1] - frequencies[0]
    return float(estimated), float(resolution)


def test_quarter_wave_modes_match_independent_wolfram_oracle() -> None:
    oracle = _wolfram_oracle()
    parameters = oracle["parameters"]
    assert isinstance(parameters, dict)
    tube = UniformTube(
        length_m=float(parameters["length_m"]),
        area_m2=3.0e-4,
        sound_speed_m_s=float(parameters["sound_speed_m_s"]),
    )

    np.testing.assert_allclose(
        tube.quarter_wave_resonances_hz(4),
        np.asarray(oracle["modes_hz"], dtype=np.float64),
        rtol=1.0e-14,
        atol=1.0e-12,
    )


def test_pressure_release_impedance_peaks_match_independent_wolfram_oracle() -> None:
    oracle = _wolfram_oracle()
    parameters = oracle["parameters"]
    assert isinstance(parameters, dict)
    tube = UniformTube(
        length_m=float(parameters["length_m"]),
        area_m2=3.0e-4,
        sound_speed_m_s=float(parameters["sound_speed_m_s"]),
    )

    for expected_hz in np.asarray(oracle["modes_hz"], dtype=np.float64)[:3]:
        measured_hz, resolution_hz = _estimate_pressure_release_resonance_hz(
            tube,
            float(expected_hz),
        )
        assert abs(measured_hz - expected_hz) <= resolution_hz


def test_fundamental_length_sweep_matches_independent_wolfram_oracle() -> None:
    oracle = _wolfram_oracle()
    sweep = oracle["fundamental_length_sweep"]
    assert isinstance(sweep, list)

    for point in sweep:
        assert isinstance(point, dict)
        tube = UniformTube(length_m=float(point["length_m"]), area_m2=3.0e-4)
        actual_hz = tube.quarter_wave_resonances_hz(1)[0]
        assert np.isclose(actual_hz, float(point["frequency_hz"]), rtol=1.0e-14, atol=1.0e-12)


def test_doubling_length_halves_ideal_resonances() -> None:
    short = UniformTube(length_m=0.17, area_m2=3.0e-4)
    long = UniformTube(length_m=0.34, area_m2=3.0e-4)

    np.testing.assert_allclose(
        long.quarter_wave_resonances_hz(4),
        short.quarter_wave_resonances_hz(4) / 2.0,
    )


def test_area_changes_impedance_scale_not_ideal_resonance_locations() -> None:
    narrow = UniformTube(length_m=0.17, area_m2=3.0e-4)
    wide = UniformTube(length_m=0.17, area_m2=6.0e-4)

    np.testing.assert_allclose(
        narrow.quarter_wave_resonances_hz(4),
        wide.quarter_wave_resonances_hz(4),
    )
    assert np.isclose(
        wide.characteristic_impedance_pa_s_m3,
        narrow.characteristic_impedance_pa_s_m3 / 2.0,
    )


def test_lossless_transfer_matrix_has_unit_determinant() -> None:
    tube = UniformTube(length_m=0.17, area_m2=3.0e-4)
    frequencies = np.linspace(0.0, 5_000.0, 257)

    determinant = np.linalg.det(tube.transfer_matrix(frequencies))

    np.testing.assert_allclose(determinant, 1.0, rtol=1.0e-12, atol=1.0e-12)
