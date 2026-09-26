from __future__ import annotations

from dataclasses import replace
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

ONSET_S = 0.05
OFFSET_S = 0.35
RAMP_S = 0.05
LOCATION = 0.55
TARGET_AREA_M2 = 5e-5
SAMPLE_FREQUENCY_HZ = 500.0


def smoothstep01(x: float) -> float:
    """Cubic Hermite smoothstep on [0, 1], clamped outside the interval."""

    u = min(1.0, max(0.0, x))
    return u * u * (3.0 - 2.0 * u)


def activation_at(
    time_s: float,
    *,
    mode: ActivationMode,
    onset_s: float = ONSET_S,
    offset_s: float = OFFSET_S,
    ramp_s: float = RAMP_S,
) -> float:
    """Experiment-local temporal activation hypothesis.

    ``step`` reproduces the current binary active/inactive semantics.
    ``smoothstep`` adds symmetric attack/release ramps while preserving a unit
    plateau. This function is deliberately local to the experiment: it is not
    yet a domain-level definition of gesture activation.
    """

    if time_s < onset_s or time_s >= offset_s:
        return 0.0
    if mode == "step":
        return 1.0

    duration_s = offset_s - onset_s
    effective_ramp_s = min(ramp_s, duration_s / 2.0)
    if effective_ramp_s <= 0.0:
        return 1.0

    attack_phase = (time_s - onset_s) / effective_ramp_s
    if attack_phase < 1.0:
        return smoothstep01(attack_phase)

    release_phase = (offset_s - time_s) / effective_ramp_s
    if release_phase < 1.0:
        return smoothstep01(release_phase)

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


def prepared(name: str, rest_area_m2: float):
    return prepare_tract1d(
        creature(name),
        geometry(rest_area_m2),
        provenance=PreparationProvenance(
            source="experiment",
            model="uniform-tract",
            notes=(f"rest_area_m2={rest_area_m2:g}",),
        ),
    )


def effective_score_for_snapshot(
    score: GestureScore,
    rest_geometry: Tract1DGeometry,
    *,
    time_s: float,
    mode: ActivationMode,
) -> GestureScore:
    """Map activation onto a snapshot target without changing the core API.

    The interpolation is intentionally body-specific: activation is translated
    into a temporary target between the local rest area and the canonical task
    target. The experiment tests whether this boundary is useful; it does not
    declare this interpolation to be the final temporal realization model.
    """

    effective_gestures: list[Gesture] = []
    for gesture in score.gestures:
        if gesture.task is not Task.CONSTRICT:
            effective_gestures.append(gesture)
            continue

        if not (gesture.onset_s <= time_s < gesture.offset_s):
            effective_gestures.append(gesture)
            continue

        if gesture.location is None:
            raise RuntimeError("experiment requires CONSTRICT.location")
        target_area = gesture.parameter("target_area")
        if target_area is None or target_area.unit != "m2":
            raise RuntimeError("experiment requires target_area in m2")

        section_index = rest_geometry.section_index_at(gesture.location)
        rest_area_m2 = rest_geometry.sections[section_index].area_m2
        activation = activation_at(time_s, mode=mode)
        effective_area_m2 = rest_area_m2 + activation * (
            target_area.value - rest_area_m2
        )

        parameters = tuple(
            TaskParameter(parameter.name, effective_area_m2, parameter.unit)
            if parameter.name == "target_area"
            else parameter
            for parameter in gesture.parameters
        )
        effective_gestures.append(replace(gesture, parameters=parameters))

    return GestureScore(tuple(effective_gestures))


def area_at_location(state: Tract1DGeometry, location: float = LOCATION) -> float:
    return state.sections[state.section_index_at(location)].area_m2


def run_series(
    *,
    body_name: str,
    rest_area_m2: float,
    mode: ActivationMode,
    times_s: np.ndarray,
) -> list[tuple[float, float, float, float]]:
    morphology = prepared(body_name, rest_area_m2)
    score = base_score()
    realizer = Tract1DRealizer()
    backend = SegmentedTubeBackend()
    request = ImpedanceRequest(np.array([SAMPLE_FREQUENCY_HZ]))

    rows: list[tuple[float, float, float, float]] = []
    for time_s in times_s:
        snapshot_score = effective_score_for_snapshot(
            score,
            morphology.rest_state,
            time_s=float(time_s),
            mode=mode,
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
                f"unexpected non-feasible result at t={time_s:g}: "
                f"{result.realization.feasibility.status}"
            )

        rows.append(
            (
                float(time_s),
                activation_at(float(time_s), mode=mode),
                area_at_location(state),
                float(abs(acoustics.input_impedance_pa_s_m3[0])),
            )
        )

    return rows


def assert_experiment_contract() -> None:
    # Smoothstep sanity checks: bounded endpoints, zero endpoint slope by finite
    # construction, midpoint symmetry, and the expected attack/hold/release shape.
    assert smoothstep01(0.0) == 0.0
    assert smoothstep01(0.5) == 0.5
    assert smoothstep01(1.0) == 1.0

    assert activation_at(0.0, mode="step") == 0.0
    assert activation_at(ONSET_S, mode="step") == 1.0
    assert activation_at(ONSET_S, mode="smoothstep") == 0.0
    assert np.isclose(
        activation_at(ONSET_S + RAMP_S / 2.0, mode="smoothstep"),
        0.5,
    )
    assert activation_at(ONSET_S + RAMP_S, mode="smoothstep") == 1.0
    assert activation_at((ONSET_S + OFFSET_S) / 2.0, mode="smoothstep") == 1.0
    assert np.isclose(
        activation_at(OFFSET_S - RAMP_S / 2.0, mode="smoothstep"),
        0.5,
    )
    assert activation_at(OFFSET_S, mode="smoothstep") == 0.0

    score = base_score()
    wide = prepared("wide-body", 3e-4)
    narrow = prepared("narrow-body", 2e-4)
    half_attack_s = ONSET_S + RAMP_S / 2.0

    wide_score = effective_score_for_snapshot(
        score,
        wide.rest_state,
        time_s=half_attack_s,
        mode="smoothstep",
    )
    narrow_score = effective_score_for_snapshot(
        score,
        narrow.rest_state,
        time_s=half_attack_s,
        mode="smoothstep",
    )
    wide_target = wide_score.gestures[0].parameter("target_area")
    narrow_target = narrow_score.gestures[0].parameter("target_area")
    if wide_target is None or narrow_target is None:
        raise RuntimeError("effective score lost target_area")

    assert np.isclose(wide_target.value, 1.75e-4)
    assert np.isclose(narrow_target.value, 1.25e-4)
    assert not np.isclose(wide_target.value, narrow_target.value)


def main() -> None:
    assert_experiment_contract()

    times_s = np.linspace(0.0, 0.4, 17)
    cases = (
        ("wide-body", 3e-4),
        ("narrow-body", 2e-4),
    )

    print(
        "mode,body,time_s,activation,area_at_constriction_m2,"
        "abs_input_impedance_500hz_pa_s_m3"
    )
    for mode in ("step", "smoothstep"):
        for body_name, rest_area_m2 in cases:
            for time_s, activation, area_m2, impedance_magnitude in run_series(
                body_name=body_name,
                rest_area_m2=rest_area_m2,
                mode=mode,
                times_s=times_s,
            ):
                print(
                    f"{mode},{body_name},{time_s:.3f},{activation:.6f},"
                    f"{area_m2:.9g},{impedance_magnitude:.9g}"
                )


if __name__ == "__main__":
    main()
