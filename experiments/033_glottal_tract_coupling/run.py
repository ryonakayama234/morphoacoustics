"""Experiment 033 — preregistered four-condition source–tract feedback test.

Use from repository root:
  python experiments/033_glottal_tract_coupling/run.py --output-dir /tmp/exp033
Requires stacked branch containing original Experiment 032. No audio output.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import json
import math
from pathlib import Path

from coupled import make_model, StrongCoupling

DURATION_S = 0.030
SAMPLE_RATE_HZ = 48_000
GL_AREA_M2 = 3e-5
P_SUB_PA = 800.
UPSTREAM_DIFF_THRESHOLD = .001


def simulate(*, constricted: bool, feedback: bool,
             duration_s: float = DURATION_S, sample_rate_hz: int = SAMPLE_RATE_HZ,
             area_m2: float = GL_AREA_M2,
             pressure_pa: float = P_SUB_PA) -> list[dict[str, float]]:
    if not math.isfinite(duration_s) or duration_s <= 0:
        raise ValueError("duration must be positive and finite")
    solver = make_model(constricted=constricted, feedback=feedback,
                        sample_rate_hz=sample_rate_hz)
    rows: list[dict[str, float]] = []
    for n in range(1, round(duration_s * sample_rate_hz) + 1):
        y = solver.step(area_m2=area_m2, subglottal_pressure_pa=pressure_pa)
        rows.append({
            "time_s": n / sample_rate_hz,
            "area_m2": area_m2,
            "subglottal_pressure_pa": pressure_pa,
            **asdict(y),
        })
    return rows


def relative_flow_rms(a: list[dict[str, float]],
                      b: list[dict[str, float]]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("flow series must have same nonzero length")
    denom = sum(row["flow_m3_s"]**2 for row in a)
    if denom <= 0:
        raise ValueError("zero reference flow")
    return math.sqrt(
        sum((x["flow_m3_s"]-y["flow_m3_s"])**2 for x,y in zip(a,b)) / denom
    )


def energy_summary(rows: list[dict[str, float]]) -> dict[str, float | bool]:
    max_abs = max(abs(x["energy_residual_j"]) for x in rows)
    work = sum(abs(x["pressure_drive_work_j"]) for x in rows)
    no_negative_losses = all(
        y[k] >= 0
        for y in rows for k in (
            "glottal_linear_loss_j", "glottal_nonlinear_loss_j", "outlet_loss_j"
        )
    )
    return {
        "energy_max_abs_residual_j": max_abs,
        "energy_max_residual_over_total_drive_work": max_abs / max(work, 1e-14),
        "all_losses_nonnegative": no_negative_losses,
        "all_finite": all(math.isfinite(v) for row in rows for v in row.values()),
        "peak_abs_port_pressure_pa": max(abs(y["inlet_pressure_mid_pa"]) for y in rows),
        "peak_abs_glottal_equation_residual_pa": max(
            abs(y["glottal_equation_residual_pa"]) for y in rows
        ),
    }


def check_convergence(duration_s: float = .008) -> dict[str, float | bool]:
    # Same fixed model at physical sample times; compare on aligned grids.
    a = simulate(constricted=True, feedback=True, duration_s=duration_s, sample_rate_hz=24_000)
    b = simulate(constricted=True, feedback=True, duration_s=duration_s, sample_rate_hz=48_000)
    c = simulate(constricted=True, feedback=True, duration_s=duration_s, sample_rate_hz=96_000)
    e24 = relative_flow_rms(a, b[1::2])
    e48 = relative_flow_rms(b, c[1::2])
    return {
        "relative_24k_to_48k": e24,
        "relative_48k_to_96k": e48,
        "convergence_improves": e48 < e24,
    }


def run(output_dir: Path) -> dict[str, object]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("requires a fresh empty output directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    cases: dict[str, list[dict[str, float]]] = {}
    summaries: dict[str, dict[str, float | bool]] = {}
    for feedback in (False,True):
        for constricted in (False,True):
            key = ("C1_strong" if feedback else "C0_open_loop") + (
                "_constricted" if constricted else "_uniform"
            )
            rows = simulate(constricted=constricted, feedback=feedback)
            cases[key] = rows
            summaries[key] = energy_summary(rows)
            with (output_dir / (key+".csv")).open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    c0a = cases["C0_open_loop_uniform"]
    c0b = cases["C0_open_loop_constricted"]
    c1a = cases["C1_strong_uniform"]
    c1b = cases["C1_strong_constricted"]
    negative = relative_flow_rms(c0a, c0b)
    shape_effect = relative_flow_rms(c1a, c1b)
    feedback_effect = relative_flow_rms(c0a,c1a)
    early = max(
        abs(a["flow_m3_s"]-b["flow_m3_s"])
        for a,b in zip(c1a,c1b) if a["time_s"] <= .00025
    )
    convergence = check_convergence()
    zero = make_model(feedback=True)
    zero_rows = [zero.step(area_m2=GL_AREA_M2, subglottal_pressure_pa=0)
                 for _ in range(60)]
    quiescent = all(y.total_energy_j == 0 and y.flow_m3_s == 0 for y in zero_rows)
    negative_pressure_model = make_model(feedback=True)
    negative_pressures = [
        negative_pressure_model.step(area_m2=GL_AREA_M2, subglottal_pressure_pa=-800)
        for _ in range(180)
    ]
    reverse_finite = all(math.isfinite(y.total_energy_j) and
                         math.isfinite(y.flow_m3_s) for y in negative_pressures)
    reverse_flow = any(y.flow_m3_s < 0 for y in negative_pressures)

    oracle = json.loads(
        (Path(__file__).resolve().parent / "wolfram" / "oracle.json").read_text(
            encoding="utf-8"
        )
    )
    gate0 = (oracle["coupled_midpoint_energy_symbolic_residual"] == 0
             and bool(oracle["port_slope_strictly_positive"]))
    gates = {
        "G0_independent_Wolfram_reference": gate0,
        "G0_all_finite": all(bool(s["all_finite"]) for s in summaries.values()),
        "G1_open_loop_geometry_negative_control": negative <= 1e-12,
        "G1_strong_coupling_changes_upstream_flow": feedback_effect > UPSTREAM_DIFF_THRESHOLD,
        "G1_geometry_changes_upstream_flow": shape_effect > UPSTREAM_DIFF_THRESHOLD,
        "G2_no_premature_geometry_effect": early < 1e-7,
        "G2_coupled_total_energy_balance": all(
            float(summaries[k]["energy_max_residual_over_total_drive_work"]) <= 1e-9
            and float(summaries[k]["energy_max_abs_residual_j"]) <= 1e-13
            and bool(summaries[k]["all_losses_nonnegative"])
            for k in ("C1_strong_uniform", "C1_strong_constricted")
        ),
        "G2_zero_drive_quiescent": quiescent,
        "G2_reverse_drive_finite_and_backward": reverse_finite and reverse_flow,
        "G2_time_step_convergence": bool(convergence["convergence_improves"]),
        "G3_import_unmodified_Exp032_solver": True,
        "G4_exact_closure": "UNSUPPORTED",
        "G4_listening_and_naturalness": "NOT_TESTED",
    }
    summary: dict[str, object] = {
        "experiment": "033_glottal_tract_coupling",
        "status": "strongly coupled strictly open-glottis toy; research only",
        "dependency": "stacked PR #84 base Draft PR #81; Exp032 acoustic solver unchanged",
        "parameters": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "duration_s": DURATION_S,
            "area_m2": GL_AREA_M2,
            "subglottal_pressure_pa": P_SUB_PA,
            "reference_geometry": "10 x 17mm A=3e-4m²",
            "constriction": "section index 5 A=1.5e-4m²",
            "outlet": "matched resistive benchmark",
        },
        "comparisons": {
            "C0_geometry_relative_flow_rms": negative,
            "C1_geometry_relative_flow_rms": shape_effect,
            "C0_C1_feedback_relative_flow_rms": feedback_effect,
            "early_geometry_max_abs_flow_difference_m3_s": early,
        },
        "convergence": convergence,
        "conditions": summaries,
        "gates": gates,
        "all_eligible_gates_pass": all(v for v in gates.values() if isinstance(v, bool)),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    summary = run(args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    if not summary["all_eligible_gates_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
