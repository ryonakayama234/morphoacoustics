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

ONSET_S = 0.05
OFFSET_S = 0.35
RAMP_S = 0.05
LOCATION = 0.55
TARGET_AREA_M2 = 5e-5
SAMPLE_FREQUENCY_HZ = 500.0
EVAL_START_S = 0.0
EVAL_END_S = 0.4
EVAL_STEP_S = 0.0001
SAMPLE_STEPS_S = (0.01, 0.005, 0.0025, 0.00125)

ORACLE_PATH = Path(__file__).with_name("wolfram") / "interpolation_oracle.json"


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
                parameters=(
                    TaskParameter("target_area", TARGET_AREA_M2, "m2"),
                ),
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
    eval_times_s: np.ndarray,
    *,
    mode: ActivationMode,
    step_s: float,
    phase: GridPhase,
) -> np.ndarray:
    sample_times = sampling_grid(step_s, phase)
    sample_values = np.asarray(
        [analytic_activation(float(t), mode) for t in sample_times],
        dtype=np.float64,
    )
    return np.interp(eval_times_s, sample_times, sample_values)


def effective_score_for_activation(
    score: GestureScore,
    rest_geometry: Tract1DGeometry,
    activation: float,
) -> GestureScore:
    """Translate one sampled activation into a snapshot target.

    The gesture is intentionally active over the whole evaluation interval.
    This removes exact onset/offset event knowledge from the realization step:
    Experiment 007 is testing whether a sampled trajectory *alone* preserves
    the temporal information needed downstream.
    """

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
    request = ImpedanceRequest(np.asarray([SAMPLE_FREQUENCY_HZ], dtype=np.float64))

    areas = np.empty_like(eval_times_s)
    impedances = np.empty_like(eval_times_s)

    for index, (time_s, activation) in enumerate(zip(eval_times_s, activations, strict=True)):
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
        impedances[index] = abs(acoustics.input_impedance_pa_s_m3[0])

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
            "mean_abs_error": math.nan,
            "integrated_abs_error": math.nan,
            "max_relative_error": math.nan,
            "mean_relative_error": math.nan,
            "nonfinite_reference_count": nonfinite_reference,
            "nonfinite_reconstructed_count": nonfinite_reconstructed,
        }

    abs_error = np.abs(reference[finite] - reconstructed[finite])
    reference_finite = np.abs(reference[finite])
    relative_error = abs_error / np.maximum(reference_finite, 1e-30)

    if np.all(finite):
        integrated = float(
            np.trapezoid(np.abs(reference - reconstructed), eval_times_s)
        )
    else:
        integrated = math.nan

    return {
        "max_abs_error": float(np.max(abs_error)),
        "mean_abs_error": float(np.mean(abs_error)),
        "integrated_abs_error": integrated,
        "max_relative_error": float(np.max(relative_error)),
        "mean_relative_error": float(np.mean(relative_error)),
        "nonfinite_reference_count": nonfinite_reference,
        "nonfinite_reconstructed_count": nonfinite_reconstructed,
    }


def load_oracle() -> dict[str, object]:
    return json.loads(ORACLE_PATH.read_text(encoding="utf-8"))


def theoretical_bound(oracle: dict[str, object], step_s: float) -> float:
    bounds = oracle["smoothstep_linear_interpolation_abs_error_bounds"]
    if not isinstance(bounds, dict):
        raise TypeError("oracle bounds must be an object")
    key = f"{step_s * 1000:g}"
    return float(bounds[key])


def pairwise_orders(rows: list[dict[str, object]]) -> list[float]:
    ordered = sorted(rows, key=lambda row: float(row["step_s"]), reverse=True)
    result: list[float] = []
    for coarse, fine in zip(ordered, ordered[1:]):
        h1 = float(coarse["step_s"])
        h2 = float(fine["step_s"])
        e1 = float(coarse["activation_max_abs_error"])
        e2 = float(fine["activation_max_abs_error"])
        if e1 > 0.0 and e2 > 0.0:
            result.append(math.log(e1 / e2) / math.log(h1 / h2))
    return result


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-007-output"),
        help="Directory for timeseries.csv, summary.csv, and decision.json",
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
                body,
                eval_times_s,
                reference_activation,
            )
            reference_cache[(mode, body.name)] = (
                reference_activation,
                reference_area,
                reference_impedance,
            )

    timeseries_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for mode in ("step", "smoothstep"):
        for body in BODIES:
            reference_activation, reference_area, reference_impedance = reference_cache[
                (mode, body.name)
            ]
            for step_s in SAMPLE_STEPS_S:
                for phase in ("aligned", "shifted"):
                    reconstructed = reconstructed_activation(
                        eval_times_s,
                        mode=mode,
                        step_s=step_s,
                        phase=phase,
                    )
                    reconstructed_area, reconstructed_impedance = observe_series(
                        body,
                        eval_times_s,
                        reconstructed,
                    )

                    activation_metrics = error_metrics(
                        reference_activation,
                        reconstructed,
                        eval_times_s,
                    )
                    area_metrics = error_metrics(
                        reference_area,
                        reconstructed_area,
                        eval_times_s,
                    )
                    impedance_metrics = error_metrics(
                        reference_impedance,
                        reconstructed_impedance,
                        eval_times_s,
                    )

                    activation_abs_error = np.abs(
                        reference_activation - reconstructed
                    )
                    area_abs_error = np.abs(reference_area - reconstructed_area)
                    expected_area_abs_error = (
                        abs(TARGET_AREA_M2 - body.rest_area_m2)
                        * activation_abs_error
                    )
                    area_invariant_residual = float(
                        np.max(np.abs(area_abs_error - expected_area_abs_error))
                    )

                    bound = (
                        theoretical_bound(oracle, step_s)
                        if mode == "smoothstep" and phase == "aligned"
                        else math.nan
                    )
                    within_bound = (
                        bool(
                            float(activation_metrics["max_abs_error"])
                            <= bound + 1e-12
                        )
                        if math.isfinite(bound)
                        else ""
                    )

                    summary_rows.append(
                        {
                            "mode": mode,
                            "body": body.name,
                            "step_s": step_s,
                            "phase": phase,
                            "sample_count": int(len(sampling_grid(step_s, phase))),
                            "activation_max_abs_error": activation_metrics["max_abs_error"],
                            "activation_mean_abs_error": activation_metrics["mean_abs_error"],
                            "activation_integrated_abs_error_s": activation_metrics[
                                "integrated_abs_error"
                            ],
                            "smoothstep_theoretical_bound": bound,
                            "smoothstep_within_bound": within_bound,
                            "area_max_abs_error_m2": area_metrics["max_abs_error"],
                            "area_integrated_abs_error_m2_s": area_metrics[
                                "integrated_abs_error"
                            ],
                            "area_invariant_max_residual_m2": area_invariant_residual,
                            "impedance_max_abs_error_pa_s_m3": impedance_metrics[
                                "max_abs_error"
                            ],
                            "impedance_mean_abs_error_pa_s_m3": impedance_metrics[
                                "mean_abs_error"
                            ],
                            "impedance_integrated_abs_error_pa_s_m3_s": impedance_metrics[
                                "integrated_abs_error"
                            ],
                            "impedance_max_relative_error": impedance_metrics[
                                "max_relative_error"
                            ],
                            "impedance_nonfinite_reference_count": impedance_metrics[
                                "nonfinite_reference_count"
                            ],
                            "impedance_nonfinite_reconstructed_count": impedance_metrics[
                                "nonfinite_reconstructed_count"
                            ],
                        }
                    )

                    for index, time_s in enumerate(eval_times_s):
                        reference_z = reference_impedance[index]
                        reconstructed_z = reconstructed_impedance[index]
                        abs_z_error = abs(reference_z - reconstructed_z)
                        relative_z_error = (
                            abs_z_error / max(abs(reference_z), 1e-30)
                            if math.isfinite(reference_z)
                            and math.isfinite(reconstructed_z)
                            else math.nan
                        )
                        timeseries_rows.append(
                            {
                                "mode": mode,
                                "body": body.name,
                                "step_s": step_s,
                                "phase": phase,
                                "time_s": float(time_s),
                                "activation_reference": float(reference_activation[index]),
                                "activation_reconstructed": float(reconstructed[index]),
                                "activation_abs_error": float(activation_abs_error[index]),
                                "area_reference_m2": float(reference_area[index]),
                                "area_reconstructed_m2": float(reconstructed_area[index]),
                                "area_abs_error_m2": float(area_abs_error[index]),
                                "impedance_reference_pa_s_m3": float(reference_z),
                                "impedance_reconstructed_pa_s_m3": float(reconstructed_z),
                                "impedance_abs_error_pa_s_m3": float(abs_z_error),
                                "impedance_relative_error": float(relative_z_error),
                            }
                        )

    write_csv(args.output_dir / "timeseries.csv", timeseries_rows)
    write_csv(args.output_dir / "summary.csv", summary_rows)

    smooth_aligned = [
        row
        for row in summary_rows
        if row["mode"] == "smoothstep"
        and row["phase"] == "aligned"
        and row["body"] == "wide-body"
    ]
    convergence_orders = pairwise_orders(smooth_aligned)
    smooth_within_oracle = all(
        row["smoothstep_within_bound"] is True for row in smooth_aligned
    )
    area_invariant_ok = all(
        float(row["area_invariant_max_residual_m2"]) <= 1e-15
        for row in summary_rows
    )
    impedance_finite = all(
        int(row["impedance_nonfinite_reference_count"]) == 0
        and int(row["impedance_nonfinite_reconstructed_count"]) == 0
        for row in summary_rows
    )

    step_shifted = sorted(
        [
            row
            for row in summary_rows
            if row["mode"] == "step"
            and row["phase"] == "shifted"
            and row["body"] == "wide-body"
        ],
        key=lambda row: float(row["step_s"]),
        reverse=True,
    )
    step_max_stays_large = min(
        float(row["activation_max_abs_error"]) for row in step_shifted
    ) >= 0.45
    step_integrated_decreases = all(
        float(coarse["activation_integrated_abs_error_s"])
        > float(fine["activation_integrated_abs_error_s"])
        for coarse, fine in zip(step_shifted, step_shifted[1:])
    )

    continuous_candidate_supported = (
        smooth_within_oracle
        and min(convergence_orders, default=0.0) >= 1.7
        and area_invariant_ok
    )
    discontinuity_requires_event_semantics = (
        step_max_stays_large and step_integrated_decreases
    )

    decision = {
        "decision": "MORE_DATA",
        "continuous_sampled_trajectory_candidate": (
            "SUPPORTED" if continuous_candidate_supported else "NOT_ESTABLISHED"
        ),
        "discontinuous_event_semantics": (
            "REQUIRED"
            if discontinuity_requires_event_semantics
            else "NOT_ESTABLISHED"
        ),
        "core_temporal_api_promotion": "DEFER",
        "smoothstep_pairwise_observed_orders": convergence_orders,
        "smoothstep_aligned_within_wolfram_bound": smooth_within_oracle,
        "area_error_invariant_holds": area_invariant_ok,
        "impedance_observations_all_finite": impedance_finite,
        "reason": (
            "Continuous smooth activation is a viable sampled-trajectory candidate, "
            "but discontinuous onset/offset timing is not faithfully represented by "
            "linear interpolation alone. Test an explicit event + continuous-trajectory "
            "representation before promoting a temporal API."
            if continuous_candidate_supported and discontinuity_requires_event_semantics
            else "One or more pre-registered checks did not establish the proposed representation."
        ),
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Experiment 007 complete")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
