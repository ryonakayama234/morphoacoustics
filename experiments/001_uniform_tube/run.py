"""Experiment 001: compare uniform-tube resonances with analytic predictions."""

from __future__ import annotations

import numpy as np

from morphoacoustics.acoustics import UniformTube


def estimate_resonance_hz(tube: UniformTube, expected_hz: float) -> tuple[float, float]:
    half_width_hz = min(40.0, expected_hz * 0.08)
    frequencies = np.linspace(
        expected_hz - half_width_hz,
        expected_hz + half_width_hz,
        20_000,
    )
    impedance = tube.input_impedance(frequencies)
    measured_hz = frequencies[int(np.argmax(np.abs(impedance)))]
    resolution_hz = frequencies[1] - frequencies[0]
    return float(measured_hz), float(resolution_hz)


def main() -> None:
    tube = UniformTube(length_m=0.17, area_m2=3.0e-4)
    predictions = tube.quarter_wave_resonances_hz(3)

    print("fidelity-0 uniform tube")
    print(f"length: {tube.length_m:.3f} m")
    print(f"area:   {tube.area_m2:.3e} m^2")
    print()
    print("mode  analytic_hz  numerical_hz  abs_error_hz  grid_hz")

    for mode, predicted_hz in enumerate(predictions, start=1):
        measured_hz, resolution_hz = estimate_resonance_hz(tube, float(predicted_hz))
        error_hz = abs(measured_hz - predicted_hz)
        print(
            f"{mode:>4}  {predicted_hz:>11.3f}  {measured_hz:>12.3f}"
            f"  {error_hz:>12.6f}  {resolution_hz:>7.4f}"
        )


if __name__ == "__main__":
    main()
