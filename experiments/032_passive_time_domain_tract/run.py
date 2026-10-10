"""Experiment 032: reproduce passive 1D waveguide numerical gates and traces."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np

from waveguide import Geometry, PassiveTract, pressure_release_eigenfrequencies

SAMPLE_RATE = 48_000
SUBDIVISIONS = 4
PULSE_CENTER_S = 0.003
PULSE_WIDTH_S = 0.00009
ROUNDTRIP_TOL_S = 0.0002
IMPEDANCE_TOL = 0.08


def gaussian_input(t: float) -> float:
    if abs(t - PULSE_CENTER_S) >= 6 * PULSE_WIDTH_S:
        return 0.0
    return 1e-6 * math.exp(-0.5 * ((t - PULSE_CENTER_S) / PULSE_WIDTH_S)**2)


def pulse_trace(
    geometry: Geometry, load: float, duration_s: float = 0.010
) -> tuple[list[dict[str, float]], dict[str, float]]:
    solver = PassiveTract(
        geometry=geometry, subdivisions=SUBDIVISIONS,
        dt_s=1 / SAMPLE_RATE, outlet_resistance_pa_s_m3=load,
    )
    records: list[dict[str, float]] = []
    work = 0.0
    max_err = 0.0
    max_abs_pressure = 0.0
    for i in range(1, int(round(duration_s * SAMPLE_RATE)) + 1):
        t = i / SAMPLE_RATE
        y = solver.step(gaussian_input(t))
        work += abs(y.injected_work_j)
        max_err = max(max_err, abs(y.energy_residual_j))
        max_abs_pressure = max(max_abs_pressure, abs(y.inlet_pressure_pa))
        records.append({
            'time_s': t - 0.5 / SAMPLE_RATE,
            'inlet_pressure_pa': y.inlet_pressure_pa,
            'inlet_flow_m3_s': y.inlet_flow_m3_s,
            'outlet_flow_m3_s': y.outlet_flow_m3_s,
            'stored_energy_j': y.stored_energy_j,
            'injected_work_j': y.injected_work_j,
            'outlet_dissipation_j': y.dissipated_j,
            'energy_residual_j': y.energy_residual_j,
        })
    summary = {
        'max_abs_inlet_pressure_pa': max_abs_pressure,
        'max_abs_energy_residual_j': max_err,
        'max_energy_error_over_work': max_err / max(work, 1e-14),
        'absolute_drive_work_j': work,
        'outlet_load_pa_s_m3': load,
    }
    return records, summary


def matched_impedance(frequency_hz: float, geometry: Geometry) -> complex:
    solver = PassiveTract(geometry=geometry, subdivisions=SUBDIVISIONS,
                          dt_s=1 / SAMPLE_RATE)
    ps: list[float] = []
    us: list[float] = []
    ts: list[float] = []
    for i in range(1, 7201):
        t = i / SAMPLE_RATE
        drive = 1e-6 * math.sin(2 * math.pi * frequency_hz * t) * min(1, t / 0.025)**2
        y = solver.step(drive)
        if i > 4680:
            ps.append(y.inlet_pressure_pa)
            us.append(y.inlet_flow_m3_s)
            ts.append(t - 0.5 / SAMPLE_RATE)
    phase = np.exp(-2j * math.pi * frequency_hz * np.asarray(ts))
    return complex(np.sum(np.asarray(ps) * phase) / np.sum(np.asarray(us) * phase))


def run(out: Path) -> dict[str, object]:
    if out.exists() and any(out.iterdir()):
        raise ValueError('requires a fresh empty output directory')
    out.mkdir(parents=True, exist_ok=True)
    uniform = Geometry()
    constricted = Geometry.middle_constriction()
    cases = {
        'uniform_matched': (uniform, uniform.characteristic_outlet_impedance),
        'uniform_pressure_release': (uniform, 0.0),
        'constricted_matched': (constricted, constricted.characteristic_outlet_impedance),
    }
    all_rows: dict[str, list[dict[str, float]]] = {}
    summaries: dict[str, dict[str, float]] = {}
    for name, (geometry, load) in cases.items():
        rows, stats = pulse_trace(geometry, load)
        all_rows[name] = rows
        summaries[name] = stats
        with (out / f'{name}.csv').open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    times = np.asarray([r['time_s'] for r in all_rows['uniform_matched']])
    release = np.asarray([r['inlet_pressure_pa'] for r in all_rows['uniform_pressure_release']])
    matched = np.asarray([r['inlet_pressure_pa'] for r in all_rows['uniform_matched']])
    delta = release - matched
    window = (times > 0.0036) & (times < 0.0044)
    i = int(np.where(window)[0][int(np.argmin(delta[window]))])
    observed_roundtrip = float(times[i] - PULSE_CENTER_S)
    exact_roundtrip = 2 * uniform.total_length_m / uniform.sound_speed_m_s
    zc = uniform.characteristic_outlet_impedance
    oracle = json.loads(
        (Path(__file__).resolve().parent / 'wolfram' / 'oracle.json').read_text(
            encoding='utf-8'
        )
    )
    oracle_pass = (
        math.isclose(zc, oracle['characteristic_impedance_pa_s_m3'], rel_tol=1e-12)
        and math.isclose(exact_roundtrip, oracle['roundtrip_s'], rel_tol=1e-12)
    )
    impedance = {}
    for frequency in (250.0, 500.0, 1000.0):
        z = matched_impedance(frequency, uniform)
        impedance[str(int(frequency))] = {
            're_pa_s_m3': z.real,
            'im_pa_s_m3': z.imag,
            'relative_complex_error': abs(z - zc) / zc,
        }
    ideal_modes = np.asarray([1, 3, 5]) * uniform.sound_speed_m_s / (4 * uniform.total_length_m)
    oracle_pass = oracle_pass and bool(np.allclose(
        ideal_modes, np.asarray(oracle['quarter_wave_frequencies_hz']),
        rtol=1e-12, atol=1e-12,
    )) and oracle['two_cell_midpoint_energy_symbolic_residual'] == 0
    eigen = {
        str(n): pressure_release_eigenfrequencies(uniform, n, 3).tolist()
        for n in (2, 4, 8)
    }
    eigen_error = {
        str(n): (np.abs(np.asarray(eigen[str(n)]) - ideal_modes) / ideal_modes).tolist()
        for n in (2, 4, 8)
    }
    energy_pass = all(
        s['max_energy_error_over_work'] < 1e-9 and s['max_abs_energy_residual_j'] < 1e-14
        for s in summaries.values()
    )
    modes_pass = all(
        eigen_error['8'][j] < eigen_error['4'][j] < eigen_error['2'][j]
        for j in range(3)
    )
    impedance_pass = all(
        x['relative_complex_error'] < IMPEDANCE_TOL for x in impedance.values()
    )
    propagation_pass = bool(
        abs(observed_roundtrip - exact_roundtrip) < ROUNDTRIP_TOL_S and delta[i] < -0.5
    )
    early_delta = float(np.max(np.abs(delta[times < 0.00345])))
    geometry_effect = float(np.max(np.abs(
        matched - np.asarray([r['inlet_pressure_pa'] for r in all_rows['constricted_matched']])
    )))
    gates = {
        'G0_Wolfram_uniform_refs': bool(oracle_pass),
        'G1_matched_impedance_at_three_frequencies': impedance_pass,
        'G1_reflected_pulse_timing_and_sign': propagation_pass,
        'G1_no_premature_reflection': early_delta < 0.01,
        'G2_energy_accounting': energy_pass,
        'G2_mode_refinement': modes_pass,
        'G2_constriction_changes_inlet_pressure': geometry_effect > 0.001,
        'G3_glottal_feedback': 'UNSUPPORTED',
        'G4_voice_quality': 'NOT_TESTED',
    }
    summary: dict[str, object] = {
        'status': 'experiment-only fixed rigid lossless 1D acoustics; NOT glottal feedback, speech or production',
        'geometry': {
            'total_length_m': uniform.total_length_m,
            'area_m2': uniform.areas_m2,
            'density_kg_m3': uniform.air_density_kg_m3,
            'sound_speed_m_s': uniform.sound_speed_m_s,
            'subdivisions': SUBDIVISIONS,
            'sample_rate_hz': SAMPLE_RATE,
        },
        'ideal_oracle': {
            'characteristic_impedance': zc,
            'roundtrip_seconds': exact_roundtrip,
            'quarter_wave_modes_hz': ideal_modes.tolist(),
        },
        'observed_roundtrip_s': observed_roundtrip,
        'reflection_pressure_min_pa': float(delta[i]),
        'early_reflection_peak_abs_pa': early_delta,
        'matched_impedance': impedance,
        'numerical_modes_hz': eigen,
        'mode_relative_errors': eigen_error,
        'geometry_effect_max_pa': geometry_effect,
        'cases': summaries,
        'gates': gates,
        'all_eligible_gates_pass': all(value for value in gates.values() if isinstance(value, bool)),
    }
    (out / 'summary.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    summary = run(args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if not summary['all_eligible_gates_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
