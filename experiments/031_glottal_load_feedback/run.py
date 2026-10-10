"""Execute preregistered C0/C1 passive chamber load intervention (Exp 031).

Usage: python experiments/031_glottal_load_feedback/run.py --output-dir /tmp/sfi1-exp031
No output WAV: this lumped load is NOT a vocal tract or validated sound synthesis.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, replace
import json
import math
from pathlib import Path

from glottal_valve import PrescribedValve
from passive_load import Parameters, State, step

SAMPLE_RATE_HZ = 48_000
DURATION_S = 0.24
OUTLET_LOW = 2.0e6
OUTLET_HIGH = 8.0e6
ENERGY_REL_TOL = 1.0e-9
UPSTREAM_DIFF_MIN = 0.01


def simulate(
    *,
    parameters: Parameters,
    valve: PrescribedValve,
    feedback: bool,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    duration_s: float = DURATION_S,
) -> list[dict[str, float | bool]]:
    if sample_rate_hz <= 0 or not math.isfinite(duration_s) or duration_s <= 0:
        raise ValueError("invalid sample rate or duration")
    dt = 1.0 / sample_rate_hz
    state = State()
    records: list[dict[str, float | bool]] = []
    for index in range(1, int(round(sample_rate_hz * duration_s)) + 1):
        t = index * dt
        area = valve.area_at(t)
        result = step(
            state,
            parameters=parameters,
            dt_s=dt,
            area_m2=area,
            subglottal_pressure_pa=valve.subglottal_pressure_pa,
            feedback=feedback,
        )
        state = result.state
        records.append(
            {
                "time_s": t,
                "area_m2": area,
                "subglottal_pressure_pa": valve.subglottal_pressure_pa,
                "flow_m3_s": state.flow_m3_s,
                "supraglottal_pressure_pa": state.chamber_pressure_pa,
                "closure": result.aperture_closed,
                **asdict(result.budget),
            }
        )
    return records


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value**2 for value in values) / len(values))


def relative_rms_difference(
    baseline: list[dict[str, float | bool]],
    candidate: list[dict[str, float | bool]],
) -> float:
    if len(baseline) != len(candidate):
        raise ValueError("simulation lengths differ")
    reference = [float(row["flow_m3_s"]) for row in baseline]
    changed = [float(row["flow_m3_s"]) for row in candidate]
    denominator = rms(reference)
    if denominator <= 0.0:
        raise ValueError("baseline flow is silent")
    return rms([a - b for a, b in zip(reference, changed, strict=True)]) / denominator


def check_energy(rows: list[dict[str, float | bool]]) -> dict[str, float | bool]:
    residual_max = max(abs(float(row["residual_j"])) for row in rows)
    total_input = sum(abs(float(row["pressure_work_j"])) for row in rows)
    max_nonreciprocal = max(abs(float(row["nonreciprocal_work_j"])) for row in rows)
    normalized = residual_max / max(total_input, 1e-12)
    all_dissipations_nonnegative = all(
        float(row[key]) >= 0.0
        for row in rows
        for key in (
            "glottal_linear_loss_j",
            "glottal_quadratic_loss_j",
            "outlet_loss_j",
            "numerical_flow_loss_j",
            "numerical_chamber_loss_j",
            "closure_projection_loss_j",
        )
    )
    return {
        "max_abs_energy_residual_j": residual_max,
        "residual_over_total_absolute_input_work": normalized,
        "all_loss_terms_nonnegative": all_dissipations_nonnegative,
        "max_abs_nonreciprocal_work_j": max_nonreciprocal,
        "pass_residual": normalized <= ENERGY_REL_TOL,
    }


def run(output_dir: Path | None = None) -> dict[str, object]:
    controls = PrescribedValve()
    params = Parameters()
    cases: dict[str, list[dict[str, float | bool]]] = {}
    summaries: dict[str, dict[str, float | bool]] = {}
    for feedback in (False, True):
        for label, r_out in (("low", OUTLET_LOW), ("high", OUTLET_HIGH)):
            name = f"{'C1_coupled' if feedback else 'C0_open_loop'}_{label}"
            configured = replace(params, outlet_resistance_pa_s_m3=r_out)
            rows = simulate(parameters=configured, valve=controls, feedback=feedback)
            cases[name] = rows
            flow = [float(row["flow_m3_s"]) for row in rows]
            pressure = [float(row["supraglottal_pressure_pa"]) for row in rows]
            summaries[name] = {
                "flow_rms_m3_s": rms(flow),
                "chamber_pressure_rms_pa": rms(pressure),
                "flow_peak_m3_s": max(flow),
                "flow_min_m3_s": min(flow),
                "closure_samples": sum(bool(row["closure"]) for row in rows),
                "all_finite": all(
                    math.isfinite(float(value))
                    for row in rows for value in row.values()
                ),
                **check_energy(rows),
            }
            if output_dir is not None:
                output_dir.mkdir(parents=True, exist_ok=True)
                with (output_dir / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)

    c0_low = cases["C0_open_loop_low"]
    c0_high = cases["C0_open_loop_high"]
    c1_low = cases["C1_coupled_low"]
    c1_high = cases["C1_coupled_high"]
    negative_control = relative_rms_difference(c0_low, c0_high)
    feedback_effect = relative_rms_difference(c0_low, c1_low)
    load_effect = relative_rms_difference(c1_low, c1_high)
    all_case_finite = all(bool(x["all_finite"]) for x in summaries.values())
    c1_energy = all(
        bool(summaries[name]["pass_residual"])
        and bool(summaries[name]["all_loss_terms_nonnegative"])
        and float(summaries[name]["max_abs_nonreciprocal_work_j"]) == 0.0
        for name in ("C1_coupled_low", "C1_coupled_high")
    )
    gates = {
        "G0_finite": all_case_finite,
        "G0_coupled_passive_balance": c1_energy,
        "G1_open_loop_load_null": negative_control <= 1e-12,
        "G1_feedback_changes_upstream_flow": feedback_effect > UPSTREAM_DIFF_MIN,
        "G1_passive_load_changes_upstream_flow": load_effect > UPSTREAM_DIFF_MIN,
        "G2_real_tract_geometry": "UNSUPPORTED",
        "G3_listening_naturalness": "NOT_TESTED",
    }
    summary: dict[str, object] = {
        "experiment": "031_glottal_load_feedback",
        "status": "experiment-local toy model; NOT production or biologically calibrated",
        "model": "prescribed-area, lumped passive chamber with flow-pressure feedback",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "duration_s": DURATION_S,
        "parameters": asdict(params),
        "prescribed_valve": asdict(controls),
        "conditions": summaries,
        "comparisons": {
            "negative_control_C0_low_vs_high_relative_flow_rms": negative_control,
            "C0_low_vs_C1_low_relative_flow_rms": feedback_effect,
            "C1_low_vs_high_relative_flow_rms": load_effect,
        },
        "gates": gates,
        "pass_all_eligible_gates": all(x for x in gates.values() if isinstance(x, bool)),
    }
    if output_dir is not None:
        with (output_dir / "summary.json").open("w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, sort_keys=True, indent=2)
            f.write("\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    summary = run(args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if not summary["pass_all_eligible_gates"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
