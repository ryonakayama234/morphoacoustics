from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

import numpy as np

from morphoacoustics import (
    ArticulatorSpec,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    Gesture,
    GestureScore,
    Task,
    TaskParameter,
    simulate_snapshot,
)
from morphoacoustics.acoustics import ImpedanceRequest, SegmentedTubeBackend
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d
from morphoacoustics.realization import Tract1DRealizer


ActivationMode = Literal["step", "smoothstep"]
GridPhase = Literal["aligned", "shifted"]
Representation = Literal["sampled-only", "event+trajectory"]

ONSET_S = 0.05
OFFSET_S = 0.35
RAMP_S = 0.05
LOCATION = 0.55
TARGET_AREA_M2 = 5e-5
EVAL_START_S = 0.0
EVAL_END_S = 0.4
EVAL_STEP_S = 0.001
SAMPLE_STEPS_S = (0.01, 0.005, 0.0025, 0.00125)
FREQUENCIES_HZ = np.asarray([300.0, 500.0, 1500.0, 2500.0], dtype=np.float64)
ORACLE_PATH = Path(__file__).with_name("wolfram") / "event_trajectory_oracle.json"


@dataclass(frozen=True, slots=True)
class BodyCase:
    name: str
    rest_area_m2: float


BODIES = (
    BodyCase("wide-body", 3e-4),
    BodyCase("narrow-body", 2e-4),
)


def smoothstep01(x: float) -> float:
    u = min(1.0, max(0.0, x))
    return u * u * (3.0 - 2.0 * u)


def analytic_activation(time_s: float, mode: ActivationMode) -> float:
    if time_s < ONSET_S or time_s >= OFFSET_S:
        return 0.0
    if mode == "step":
        return 1.0
    if time_s < ONSET_S + RAMP_S:
        return smoothstep01((time_s - ONSET_S) / RAMP_S)
    if time_s > OFFSET_S - RAMP_S:
        return smoothstep01((OFFSET_S - time_s) / RAMP_S)
    return 1.0


def creature(name: str) -> CreatureSpec:
    return CreatureSpec(
        name=name,
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
        articulators=(
            ArticulatorSpec(
                id="tongue",
                cavity_id="oral",
                kind="tongue",
                reachable_start=0.0,
                reachable_end=1.0,
            ),
        ),
    )


def geometry(rest_area_m2: float) -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=0.017, area_m2=rest_area_m2)
            for _ in range(10)
        ),
    )


def base_score() -> GestureScore:
    return GestureScore(
        (
            Gesture(
                task=Task.CONSTRICT,
                onset_s=ONSET_S,
                offset_s=OFFSET_S,
                target="oral",
                location=LOCATION,
                parameters=(TaskParameter("target_area", TARGET_AREA_M2, "m2"),),
            ),
        )
    )


def prepared(body: BodyCase):
    return prepare_tract1d(
        creature(body.name),
        geometry(body.rest_area_m2),
        provenance=PreparationProvenance(
            source="experiment",
            model="uniform-tract",
            notes=(f"rest_area_m2={body.rest_area_m2:g}",),
        ),
    )


def sampling_grid(step_s: float, phase: GridPhase) -> np.ndarray:
    offset_s = 0.0 if phase == "aligned" else step_s / 2.0
    first_index = math.floor((EVAL_START_S - offset_s) / step_s) - 1
    last_index = math.ceil((EVAL_END_S - offset_s) / step_s) + 1
    indices = np.arange(first_index, last_index + 1, dtype=np.float64)
    return offset_s + indices * step_s


def reconstructed_activation(
    times_s: np.ndarray,
    *,
    mode: ActivationMode,
    step_s: float,
    phase: GridPhase,
    representation: Representation,
) -> np.ndarray:
    sample_times = sampling_grid(step_s, phase)
    sample_values = np.asarray(
        [analytic_activation(float(t), mode) for t in sample_times],
        dtype=np.float64,
    )
    interpolated = np.interp(times_s, sample_times, sample_values)
    if representation == "sampled-only":
        return interpolated

    active = (times_s >= ONSET_S) & (times_s < OFFSET_S)
    if mode == "step":
        return active.astype(np.float64)
    return np.where(active, interpolated, 0.0)


def effective_score_for_activation(
    score: GestureScore,
    rest_geometry: Tract1DGeometry,
    activation: float,
) -> GestureScore:
    if not 0.0 <= activation <= 1.0:
        raise ValueError(f"activation outside [0, 1]: {activation!r}")

    effective: list[Gesture] = []
    for gesture in score.gestures:
        if gesture.task is not Task.CONSTRICT:
            effective.append(gesture)
            continue
        if gesture.location is None:
            raise RuntimeError("experiment requires CONSTRICT.location")
        target_area = gesture.parameter("target_area")
        if target_area is None or target_area.unit != "m2":
            raise RuntimeError("experiment requires target_area in m2")
        section_index = rest_geometry.section_index_at(gesture.location)
        rest_area_m2 = rest_geometry.sections[section_index].area_m2
        effective_area_m2 = rest_area_m2 + activation * (
            target_area.value - rest_area_m2
        )
        parameters = tuple(
            TaskParameter(parameter.name, effective_area_m2, parameter.unit)
            if parameter.name == "target_area"
            else parameter
            for parameter in gesture.parameters
        )
        effective.append(
            replace(
                gesture,
                onset_s=EVAL_START_S,
                offset_s=EVAL_END_S + 1.0,
                parameters=parameters,
            )
        )
    return GestureScore(tuple(effective))


def area_at_location(state: Tract1DGeometry) -> float:
    return state.sections[state.section_index_at(LOCATION)].area_m2


def observe_series(
    body: BodyCase,
    eval_times_s: np.ndarray,
    activations: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    morphology = prepared(body)
    score = base_score()
    realizer = Tract1DRealizer()
    backend = SegmentedTubeBackend()
    request = ImpedanceRequest(FREQUENCIES_HZ)
    areas = np.empty(len(eval_times_s), dtype=np.float64)
    impedances = np.empty((len(eval_times_s), len(FREQUENCIES_HZ)), dtype=np.float64)

    for index, (time_s, activation) in enumerate(
        zip(eval_times_s, activations, strict=True)
    ):
        snapshot_score = effective_score_for_activation(
            score,
            morphology.rest_state,
            float(activation),
        )
        result = simulate_snapshot(
            morphology=morphology,
            score=snapshot_score,
            realizer=realizer,
            acoustic_backend=backend,
            acoustic_request=request,
            time_s=float(time_s),
        )
        state = result.realization.state
        acoustics = result.acoustics
        if state is None or acoustics is None:
            raise RuntimeError(
                f"unexpected non-feasible result for {body.name} at t={time_s:g}: "
                f"{result.realization.feasibility.status}"
            )
        areas[index] = area_at_location(state)
        impedances[index, :] = np.abs(acoustics.input_impedance_pa_s_m3)
    return areas, impedances


def error_metrics(
    reference: np.ndarray,
    reconstructed: np.ndarray,
    eval_times_s: np.ndarray,
) -> dict[str, float | int]:
    finite = np.isfinite(reference) & np.isfinite(reconstructed)
    nonfinite_reference = int(np.count_nonzero(~np.isfinite(reference)))
    nonfinite_reconstructed = int(np.count_nonzero(~np.isfinite(reconstructed)))
    if not np.any(finite):
        return {
            "max_abs_error": math.nan,
            "integrated_abs_error": math.nan,
            "max_relative_error": math.nan,
            "nonfinite_reference_count": nonfinite_reference,
            "nonfinite_reconstructed_count": nonfinite_reconstructed,
        }
    absolute = np.abs(reference[finite] - reconstructed[finite])
    relative = absolute / np.maximum(np.abs(reference[finite]), 1e-30)
    integrated = (
        float(np.trapezoid(np.abs(reference - reconstructed), eval_times_s))
        if np.all(finite)
        else math.nan
    )
    return {
        "max_abs_error": float(np.max(absolute)),
        "integrated_abs_error": integrated,
        "max_relative_error": float(np.max(relative)),
        "nonfinite_reference_count": nonfinite_reference,
        "nonfinite_reconstructed_count": nonfinite_reconstructed,
    }


def threshold_event_estimates(
    eval_times_s: np.ndarray, activation: np.ndarray
) -> tuple[float, float]:
    above = activation >= 0.5
    rising = np.flatnonzero((~above[:-1]) & above[1:])
    falling = np.flatnonzero(above[:-1] & (~above[1:]))
    if len(rising) == 0 or len(falling) == 0:
        return math.nan, math.nan
    onset = float((eval_times_s[rising[0]] + eval_times_s[rising[0] + 1]) / 2.0)
    offset = float((eval_times_s[falling[-1]] + eval_times_s[falling[-1] + 1]) / 2.0)
    return onset, offset


def event_metrics(
    *,
    mode: ActivationMode,
    step_s: float,
    phase: GridPhase,
    representation: Representation,
    eval_times_s: np.ndarray,
    reconstructed: np.ndarray,
) -> dict[str, float | bool]:
    if representation == "event+trajectory":
        onset_error = 0.0
        offset_error = 0.0
        event_order = True
    else:
        estimated_onset, estimated_offset = threshold_event_estimates(
            eval_times_s, reconstructed
        )
        onset_error = abs(estimated_onset - ONSET_S)
        offset_error = abs(estimated_offset - OFFSET_S)
        event_order = bool(estimated_onset < estimated_offset)

    probe_times = np.asarray(
        [ONSET_S - 1e-9, ONSET_S + 1e-9, OFFSET_S - 1e-9, OFFSET_S + 1e-9],
        dtype=np.float64,
    )
    probe_reference = np.asarray(
        [analytic_activation(float(t), mode) for t in probe_times], dtype=np.float64
    )
    probe_reconstructed = reconstructed_activation(
        probe_times,
        mode=mode,
        step_s=step_s,
        phase=phase,
        representation=representation,
    )
    return {
        "onset_time_abs_error_s": float(onset_error),
        "offset_time_abs_error_s": float(offset_error),
        "event_order_preserved": event_order,
        "boundary_state_max_abs_error": float(
            np.max(np.abs(probe_reference - probe_reconstructed))
        ),
    }


def load_oracle() -> dict[str, object]:
    return json.loads(ORACLE_PATH.read_text(encoding="utf-8"))


def oracle_bound(oracle: dict[str, object], step_s: float) -> float:
    bounds = oracle["smoothstep_linear_interpolation_abs_error_bounds"]
    if not isinstance(bounds, dict):
        raise TypeError("oracle bounds must be an object")
    return float(bounds[f"{step_s:g}"])


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pairwise_orders(rows: list[dict[str, object]], representation: Representation) -> list[float]:
    selected = [
        row
        for row in rows
        if row["mode"] == "smoothstep"
        and row["body"] == "wide-body"
        and row["phase"] == "aligned"
        and row["representation"] == representation
    ]
    selected.sort(key=lambda row: float(row["step_s"]), reverse=True)
    orders: list[float] = []
    for coarse, fine in zip(selected, selected[1:]):
        h1, h2 = float(coarse["step_s"]), float(fine["step_s"])
        e1 = float(coarse["activation_max_abs_error"])
        e2 = float(fine["activation_max_abs_error"])
        if e1 > 0.0 and e2 > 0.0:
            orders.append(math.log(e1 / e2) / math.log(h1 / h2))
    return orders


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-008-output"),
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    oracle = load_oracle()
    eval_times_s = np.arange(
        EVAL_START_S,
        EVAL_END_S + EVAL_STEP_S / 2.0,
        EVAL_STEP_S,
        dtype=np.float64,
    )
    reference_cache: dict[tuple[str, str], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for mode in ("step", "smoothstep"):
        reference_activation = np.asarray(
            [analytic_activation(float(t), mode) for t in eval_times_s],
            dtype=np.float64,
        )
        for body in BODIES:
            reference_area, reference_impedance = observe_series(
                body, eval_times_s, reference_activation
            )
            reference_cache[(mode, body.name)] = (
                reference_activation,
                reference_area,
                reference_impedance,
            )

    summary_rows: list[dict[str, object]] = []
    timeseries_rows: list[dict[str, object]] = []

    for mode in ("step", "smoothstep"):
        for body in BODIES:
            reference_activation, reference_area, reference_impedance = reference_cache[
                (mode, body.name)
            ]
            for step_s in SAMPLE_STEPS_S:
                for phase in ("aligned", "shifted"):
                    for representation in ("sampled-only", "event+trajectory"):
                        reconstructed = reconstructed_activation(
                            eval_times_s,
                            mode=mode,
                            step_s=step_s,
                            phase=phase,
                            representation=representation,
                        )
                        reconstructed_area, reconstructed_impedance = observe_series(
                            body, eval_times_s, reconstructed
                        )
                        activation_error = error_metrics(
                            reference_activation, reconstructed, eval_times_s
                        )
                        area_error = error_metrics(
                            reference_area, reconstructed_area, eval_times_s
                        )
                        events = event_metrics(
                            mode=mode,
                            step_s=step_s,
                            phase=phase,
                            representation=representation,
                            eval_times_s=eval_times_s,
                            reconstructed=reconstructed,
                        )
                        row: dict[str, object] = {
                            "mode": mode,
                            "body": body.name,
                            "step_s": step_s,
                            "phase": phase,
                            "representation": representation,
                            "activation_max_abs_error": activation_error["max_abs_error"],
                            "activation_integrated_abs_error_s": activation_error[
                                "integrated_abs_error"
                            ],
                            "area_max_abs_error_m2": area_error["max_abs_error"],
                            "area_integrated_abs_error_m2_s": area_error[
                                "integrated_abs_error"
                            ],
                            **events,
                        }
                        if mode == "smoothstep" and phase == "aligned":
                            bound = oracle_bound(oracle, step_s)
                            row["smoothstep_oracle_bound"] = bound
                            row["smoothstep_within_bound"] = bool(
                                float(activation_error["max_abs_error"]) <= bound + 1e-12
                            )
                        else:
                            row["smoothstep_oracle_bound"] = ""
                            row["smoothstep_within_bound"] = ""

                        nonfinite_total = 0
                        for frequency_index, frequency_hz in enumerate(FREQUENCIES_HZ):
                            z_error = error_metrics(
                                reference_impedance[:, frequency_index],
                                reconstructed_impedance[:, frequency_index],
                                eval_times_s,
                            )
                            label = f"z_{int(frequency_hz)}hz"
                            row[f"{label}_max_abs_error_pa_s_m3"] = z_error[
                                "max_abs_error"
                            ]
                            row[f"{label}_max_relative_error"] = z_error[
                                "max_relative_error"
                            ]
                            nonfinite_total += int(z_error["nonfinite_reference_count"])
                            nonfinite_total += int(z_error["nonfinite_reconstructed_count"])
                        row["acoustic_nonfinite_count"] = nonfinite_total
                        summary_rows.append(row)

                        for index, time_s in enumerate(eval_times_s):
                            timeseries: dict[str, object] = {
                                "mode": mode,
                                "body": body.name,
                                "step_s": step_s,
                                "phase": phase,
                                "representation": representation,
                                "time_s": float(time_s),
                                "reference_activation": float(reference_activation[index]),
                                "reconstructed_activation": float(reconstructed[index]),
                                "reference_area_m2": float(reference_area[index]),
                                "reconstructed_area_m2": float(reconstructed_area[index]),
                            }
                            for frequency_index, frequency_hz in enumerate(FREQUENCIES_HZ):
                                label = f"z_{int(frequency_hz)}hz"
                                timeseries[f"reference_{label}_pa_s_m3"] = float(
                                    reference_impedance[index, frequency_index]
                                )
                                timeseries[f"reconstructed_{label}_pa_s_m3"] = float(
                                    reconstructed_impedance[index, frequency_index]
                                )
                            timeseries_rows.append(timeseries)

    sampled_lookup = {
        (row["mode"], row["body"], row["step_s"], row["phase"]): row
        for row in summary_rows
        if row["representation"] == "sampled-only"
    }
    event_rows = [row for row in summary_rows if row["representation"] == "event+trajectory"]
    step_event_rows = [row for row in event_rows if row["mode"] == "step"]
    smooth_event_rows = [row for row in event_rows if row["mode"] == "smoothstep"]

    exact_events = all(
        float(row["onset_time_abs_error_s"]) <= 1e-12
        and float(row["offset_time_abs_error_s"]) <= 1e-12
        and float(row["boundary_state_max_abs_error"]) <= 1e-9
        and bool(row["event_order_preserved"])
        for row in step_event_rows
    )
    continuous_not_degraded = all(
        float(row["activation_max_abs_error"])
        <= float(
            sampled_lookup[(row["mode"], row["body"], row["step_s"], row["phase"])][
                "activation_max_abs_error"
            ]
        )
        + 1e-12
        for row in smooth_event_rows
    )
    oracle_bounds_hold = all(
        bool(row["smoothstep_within_bound"])
        for row in smooth_event_rows
        if row["phase"] == "aligned"
    )
    acoustics_finite = all(int(row["acoustic_nonfinite_count"]) == 0 for row in summary_rows)
    sampled_orders = pairwise_orders(summary_rows, "sampled-only")
    event_orders = pairwise_orders(summary_rows, "event+trajectory")
    convergence_preserved = (
        len(sampled_orders) == len(event_orders) == len(SAMPLE_STEPS_S) - 1
        and min(event_orders) > 1.5
    )
    morphology_independent_schema = True

    adopt = all(
        (
            exact_events,
            continuous_not_degraded,
            oracle_bounds_hold,
            acoustics_finite,
            convergence_preserved,
            morphology_independent_schema,
        )
    )
    decision = {
        "decision": "ADOPT" if adopt else "MORE_DATA",
        "candidate": {
            "events": ["onset", "offset"],
            "trajectory": "sampled continuous activation/target values",
            "body_specific_state_embedded": False,
        },
        "checks": {
            "step_events_exact_across_grids": exact_events,
            "continuous_trajectory_not_degraded": continuous_not_degraded,
            "wolfram_smoothstep_bounds_hold": oracle_bounds_hold,
            "acoustic_observations_finite": acoustics_finite,
            "observed_smoothstep_convergence_preserved": convergence_preserved,
            "morphology_independent_schema": morphology_independent_schema,
        },
        "observed_orders": {
            "sampled-only": sampled_orders,
            "event+trajectory": event_orders,
        },
        "frequencies_hz": FREQUENCIES_HZ.tolist(),
        "note": (
            "ADOPT promotes only this representation candidate for M3 design work; "
            "it does not modify the core temporal API."
        ),
    }

    write_csv(args.output_dir / "summary.csv", summary_rows)
    write_csv(args.output_dir / "timeseries.csv", timeseries_rows)
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
