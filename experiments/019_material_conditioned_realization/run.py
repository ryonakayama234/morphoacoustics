"""Experiment 019: reduced material-conditioned quasi-static realization."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from morphoacoustics import (
    ArticulatorSpec,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    FeasibilityIssue,
    FeasibilityReport,
    FeasibilityStatus,
    Gesture,
    GestureScore,
    Task,
    TaskParameter,
)
from morphoacoustics.acoustics import SegmentedTube
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import (
    PreparationProvenance,
    PreparedMorphology,
    prepare_tract1d,
)
from morphoacoustics.realization import RealizationResult, Tract1DRealizer

TRACT_LENGTH_M = 0.17
SECTION_COUNT = 10
REST_AREA_M2 = 3.0e-4
GESTURE_LOCATION = 0.65
TARGET_SECTION_INDEX = 6
LEFT_NEIGHBOR_INDEX = 5
RIGHT_NEIGHBOR_INDEX = 7
TARGET_AREA_M2 = 5.0e-5
EVALUATION_TIME_S = 0.1

SMOOTHNESS_LAMBDA = 1.0
BASELINE_LEFT_RELATIVE_STIFFNESS = 1.0
CANDIDATE_LEFT_RELATIVE_STIFFNESS = 4.0

CANDIDATE_GRID_STEP_HZ = 0.05
REFERENCE_GRID_STEP_HZ = 0.01
MODE_WINDOWS_HZ = (
    (350.0, 430.0),
    (1580.0, 1790.0),
    (1980.0, 2260.0),
)
FREQUENCY_ORACLE_TOLERANCE_HZ = 0.05
REFERENCE_FREQUENCY_ORACLE_TOLERANCE_HZ = 0.01
STATE_ORACLE_TOLERANCE = 1.0e-10
TASK_AREA_TOLERANCE_M2 = 1.0e-18
RIGHT_SIDE_LOCALITY_TOLERANCE = 1.0e-12
MIN_PHYSICAL_L2_EFFECT = 1.0e-3
DISCRIMINATION_MARGIN = 5.0

SUPPORT_DECISION = "SUPPORT_MATERIAL_CONDITIONED_REALIZATION"
ORACLE_PATH = (
    Path(__file__).with_name("wolfram") / "material_realization_oracle.json"
)


@dataclass(frozen=True, slots=True)
class ReducedMaterialProfile:
    """Experiment-local dimensionless stiffness field."""

    relative_stiffness: tuple[float, ...]
    smoothness_lambda: float

    def __post_init__(self) -> None:
        if len(self.relative_stiffness) != SECTION_COUNT:
            raise ValueError("material profile must match section count")
        if any(
            not math.isfinite(value) or value <= 0.0
            for value in self.relative_stiffness
        ):
            raise ValueError("relative stiffness values must be finite and > 0")
        if (
            not math.isfinite(self.smoothness_lambda)
            or self.smoothness_lambda < 0.0
        ):
            raise ValueError("smoothness_lambda must be finite and >= 0")


class QuasiStaticMinimumEnergyRealizer:
    """Experiment-local R1 candidate.

    Production Tract1DRealizer remains the R0 hard-projector baseline.
    Request/capability/reachability validation is delegated to R0, then this
    candidate replaces hard projection with a reduced convex minimum-energy
    solution in normalized area-ratio coordinates.
    """

    def __init__(self, profile: ReducedMaterialProfile) -> None:
        self.profile = profile
        self._validator = Tract1DRealizer()

    def realize_snapshot(
        self,
        morphology: PreparedMorphology[Tract1DGeometry],
        score: GestureScore,
        time_s: float,
    ) -> RealizationResult[Tract1DGeometry]:
        validated = self._validator.realize_snapshot(
            morphology,
            score,
            time_s,
        )
        if validated.feasibility.status is not FeasibilityStatus.FEASIBLE:
            return validated

        active = [
            gesture
            for gesture in score.gestures
            if gesture.onset_s <= time_s < gesture.offset_s
        ]
        if not active:
            return RealizationResult(
                state=morphology.rest_state,
                feasibility=FeasibilityReport(
                    status=FeasibilityStatus.FEASIBLE
                ),
            )

        if len(active) != 1 or active[0].task is not Task.CONSTRICT:
            return RealizationResult(
                state=None,
                feasibility=FeasibilityReport(
                    status=FeasibilityStatus.UNSUPPORTED,
                    issues=(
                        FeasibilityIssue(
                            code="REDUCED_MATERIAL_SINGLE_CONSTRICT_ONLY",
                            message=(
                                "experiment-019 R1 supports exactly one active "
                                "CONSTRICT gesture"
                            ),
                        ),
                    ),
                ),
            )

        gesture = active[0]
        target_area = gesture.parameter("target_area")
        if gesture.location is None or target_area is None:
            raise RuntimeError("validated CONSTRICT is incomplete")

        rest = morphology.rest_state
        target_index = rest.section_index_at(gesture.location)
        target_ratio = (
            target_area.value / rest.sections[target_index].area_m2
        )
        ratios = self._solve_ratios(
            target_index=target_index,
            target_ratio=target_ratio,
        )

        if np.any(~np.isfinite(ratios)) or np.any(ratios <= 0.0):
            return RealizationResult(
                state=None,
                feasibility=FeasibilityReport(
                    status=FeasibilityStatus.UNSUPPORTED,
                    issues=(
                        FeasibilityIssue(
                            code="REDUCED_MATERIAL_POSITIVITY_BOUND_ACTIVE",
                            message=(
                                "unconstrained KKT optimum leaves the positive "
                                "area domain; active-set handling is outside "
                                "experiment-019 scope"
                            ),
                        ),
                    ),
                ),
            )

        state = Tract1DGeometry(
            cavity_id=rest.cavity_id,
            sections=tuple(
                TubeSection(
                    length_m=section.length_m,
                    area_m2=section.area_m2 * float(ratios[index]),
                )
                for index, section in enumerate(rest.sections)
            ),
        )
        return RealizationResult(
            state=state,
            feasibility=FeasibilityReport(
                status=FeasibilityStatus.FEASIBLE
            ),
        )

    def _solve_ratios(
        self,
        *,
        target_index: int,
        target_ratio: float,
    ) -> np.ndarray:
        n = SECTION_COUNT
        stiffness = np.asarray(
            self.profile.relative_stiffness,
            dtype=np.float64,
        )
        difference = np.zeros((n - 1, n), dtype=np.float64)
        for index in range(n - 1):
            difference[index, index] = -1.0
            difference[index, index + 1] = 1.0

        hessian = (
            np.diag(stiffness)
            + self.profile.smoothness_lambda
            * (difference.T @ difference)
        )
        target_vector = np.zeros(n, dtype=np.float64)
        target_vector[target_index] = 1.0

        kkt = np.zeros((n + 1, n + 1), dtype=np.float64)
        kkt[:n, :n] = hessian
        kkt[:n, n] = target_vector
        kkt[n, :n] = target_vector

        rhs = np.concatenate((stiffness, np.array([target_ratio])))
        solution = np.linalg.solve(kkt, rhs)
        return np.asarray(solution[:n], dtype=np.float64)


def _creature() -> CreatureSpec:
    return CreatureSpec(
        name="g1m-reduced-material-body",
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
        articulators=(
            ArticulatorSpec(
                id="tongue",
                cavity_id="oral",
                kind="tongue",
                reachable_start=0.30,
                reachable_end=0.80,
            ),
        ),
    )


def _geometry() -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(
                length_m=TRACT_LENGTH_M / SECTION_COUNT,
                area_m2=REST_AREA_M2,
            )
            for _ in range(SECTION_COUNT)
        ),
    )


def _prepared(creature: CreatureSpec) -> PreparedMorphology[Tract1DGeometry]:
    return prepare_tract1d(
        creature,
        _geometry(),
        provenance=PreparationProvenance(
            source="experiment-019",
            model="uniform-rest-tract-with-experiment-local-material-profile",
            notes=(
                "production morphology/material schema intentionally unchanged",
            ),
        ),
    )


def _canonical_score() -> GestureScore:
    return GestureScore(
        (
            Gesture(
                task=Task.CONSTRICT,
                onset_s=0.0,
                offset_s=0.3,
                target="oral",
                location=GESTURE_LOCATION,
                parameters=(
                    TaskParameter("target_area", TARGET_AREA_M2, "m2"),
                ),
            ),
        )
    )


def _score_payload(score: GestureScore) -> dict[str, Any]:
    return {
        "gestures": [
            {
                "task": gesture.task.value,
                "onset_s": gesture.onset_s,
                "offset_s": gesture.offset_s,
                "target": gesture.target,
                "location": gesture.location,
                "parameters": [
                    {
                        "name": parameter.name,
                        "value": parameter.value,
                        "unit": parameter.unit,
                    }
                    for parameter in gesture.parameters
                ],
            }
            for gesture in score.gestures
        ]
    }


def _score_sha256(score: GestureScore) -> str:
    payload = json.dumps(
        _score_payload(score),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _material_profile(left_relative_stiffness: float) -> ReducedMaterialProfile:
    stiffness = [1.0] * SECTION_COUNT
    stiffness[LEFT_NEIGHBOR_INDEX] = left_relative_stiffness
    return ReducedMaterialProfile(
        relative_stiffness=tuple(stiffness),
        smoothness_lambda=SMOOTHNESS_LAMBDA,
    )


def _frequency_grid(
    start_hz: float,
    stop_hz: float,
    step_hz: float,
) -> np.ndarray:
    intervals = int(round((stop_hz - start_hz) / step_hz))
    if not math.isclose(
        start_hz + intervals * step_hz,
        stop_hz,
        rel_tol=0.0,
        abs_tol=1.0e-10,
    ):
        raise ValueError("frequency window must be divisible by grid step")
    return np.linspace(start_hz, stop_hz, intervals + 1, dtype=np.float64)


def _measure_resonances(
    state: Tract1DGeometry,
    grid_step_hz: float,
) -> tuple[float, ...]:
    tube = SegmentedTube.from_geometry(state)
    peaks: list[float] = []
    for start_hz, stop_hz in MODE_WINDOWS_HZ:
        frequencies = _frequency_grid(start_hz, stop_hz, grid_step_hz)
        impedance = tube.input_impedance(frequencies)
        magnitude = np.abs(impedance)
        peaks.append(float(frequencies[int(np.nanargmax(magnitude))]))
    return tuple(peaks)


def _state_ratios(
    rest: Tract1DGeometry,
    state: Tract1DGeometry,
) -> np.ndarray:
    return np.asarray(
        [
            realized.area_m2 / prepared.area_m2
            for prepared, realized in zip(
                rest.sections,
                state.sections,
                strict=True,
            )
        ],
        dtype=np.float64,
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _failure_decision(
    *,
    representation_ok: bool,
    baseline_null_ok: bool,
    task_ok: bool,
    state_oracle_ok: bool,
    physical_effect_ok: bool,
    locality_ok: bool,
    acoustic_oracle_ok: bool,
    acoustic_effect_ok: bool,
) -> str:
    if not representation_ok:
        return "REPRESENTATION_LEAK"
    if not baseline_null_ok:
        return "BASELINE_NULL_FAILED"
    if not task_ok:
        return "TASK_REALIZATION_FAILED"
    if not state_oracle_ok:
        return "MATERIAL_STATE_ORACLE_MISMATCH"
    if not physical_effect_ok:
        return "MATERIAL_EFFECT_UNRESOLVED"
    if not locality_ok:
        return "CAUSAL_TRACE_INCONSISTENT"
    if not acoustic_oracle_ok:
        return "ACOUSTIC_ORACLE_MISMATCH"
    if not acoustic_effect_ok:
        return "NUMERICALLY_UNRESOLVED"
    return SUPPORT_DECISION


def run(output_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename in (
        "states.csv",
        "resonances.csv",
        "effects.csv",
        "decision.json",
    ):
        path = output_dir / filename
        if path.exists():
            path.unlink()

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    creature = _creature()
    morphology = _prepared(creature)
    score = _canonical_score()
    score_hash_before = _score_sha256(score)

    baseline_profile = _material_profile(
        BASELINE_LEFT_RELATIVE_STIFFNESS
    )
    candidate_profile = _material_profile(
        CANDIDATE_LEFT_RELATIVE_STIFFNESS
    )

    r0 = Tract1DRealizer()
    r0_baseline = r0.realize_snapshot(
        morphology,
        score,
        EVALUATION_TIME_S,
    )
    r0_candidate = r0.realize_snapshot(
        morphology,
        score,
        EVALUATION_TIME_S,
    )

    r1_baseline = QuasiStaticMinimumEnergyRealizer(
        baseline_profile
    ).realize_snapshot(
        morphology,
        score,
        EVALUATION_TIME_S,
    )
    r1_candidate = QuasiStaticMinimumEnergyRealizer(
        candidate_profile
    ).realize_snapshot(
        morphology,
        score,
        EVALUATION_TIME_S,
    )

    results = {
        "r0_baseline": r0_baseline,
        "r0_candidate": r0_candidate,
        "r1_baseline": r1_baseline,
        "r1_candidate": r1_candidate,
    }

    score_hash_after = _score_sha256(score)
    representation_ok = (
        score_hash_before == score_hash_after
        and score_hash_before
        == _score_sha256(_canonical_score())
    )

    realization_statuses = {
        name: result.feasibility.status.value
        for name, result in results.items()
    }
    missing_state_conditions = [
        name
        for name, result in results.items()
        if result.state is None
    ]
    task_realization_ok = all(
        result.feasibility.status is FeasibilityStatus.FEASIBLE
        and result.state is not None
        for result in results.values()
    )
    if not task_realization_ok:
        decision_name = _failure_decision(
            representation_ok=representation_ok,
            baseline_null_ok=True,
            task_ok=False,
            state_oracle_ok=True,
            physical_effect_ok=True,
            locality_ok=True,
            acoustic_oracle_ok=True,
            acoustic_effect_ok=True,
        )
        decision: dict[str, Any] = {
            "decision": decision_name,
            "issue": 40,
            "experiment": 19,
            "research_question": (
                "whether an experiment-local reduced stiffness intervention "
                "changes body-specific quasi-static realization while the exact "
                "same task target remains achieved"
            ),
            "claim_scope": (
                "reduced dimensionless stiffness field in a 10-section "
                "Fidelity-0 tract; not biological tissue mechanics"
            ),
            "canonical_score_sha256": score_hash_before,
            "representation_ok": representation_ok,
            "baseline_null_ok": None,
            "task_ok": False,
            "state_oracle_ok": None,
            "physical_effect_ok": None,
            "locality_ok": None,
            "acoustic_oracle_ok": None,
            "acoustic_effect_ok": None,
            "realization_statuses": realization_statuses,
            "missing_state_conditions": missing_state_conditions,
            "parameters": {
                "tract_length_m": TRACT_LENGTH_M,
                "section_count": SECTION_COUNT,
                "rest_area_m2": REST_AREA_M2,
                "gesture_location": GESTURE_LOCATION,
                "target_section_index": TARGET_SECTION_INDEX,
                "target_area_m2": TARGET_AREA_M2,
                "smoothness_lambda": SMOOTHNESS_LAMBDA,
                "left_neighbor_index": LEFT_NEIGHBOR_INDEX,
                "baseline_left_relative_stiffness": (
                    BASELINE_LEFT_RELATIVE_STIFFNESS
                ),
                "candidate_left_relative_stiffness": (
                    CANDIDATE_LEFT_RELATIVE_STIFFNESS
                ),
            },
            "environment": {
                "python": platform.python_version(),
                "numpy": np.__version__,
            },
            "elapsed_s": time.perf_counter() - started,
        }
        (output_dir / "decision.json").write_text(
            json.dumps(decision, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return decision

    r0_base_state = r0_baseline.state
    r0_candidate_state = r0_candidate.state
    r1_base_state = r1_baseline.state
    r1_candidate_state = r1_candidate.state
    if (
        r0_base_state is None
        or r0_candidate_state is None
        or r1_base_state is None
        or r1_candidate_state is None
    ):
        raise RuntimeError("unexpected missing realized state")

    r0_base_ratios = _state_ratios(
        morphology.rest_state,
        r0_base_state,
    )
    r0_candidate_ratios = _state_ratios(
        morphology.rest_state,
        r0_candidate_state,
    )
    r1_base_ratios = _state_ratios(
        morphology.rest_state,
        r1_base_state,
    )
    r1_candidate_ratios = _state_ratios(
        morphology.rest_state,
        r1_candidate_state,
    )

    r0_oracle = np.asarray(
        oracle["r0_hard_projector_state_ratio"],
        dtype=np.float64,
    )
    r1_base_oracle = np.asarray(
        oracle["r1_baseline_state_ratio"],
        dtype=np.float64,
    )
    r1_candidate_oracle = np.asarray(
        oracle["r1_candidate_state_ratio"],
        dtype=np.float64,
    )

    baseline_null_ok = bool(
        np.array_equal(r0_base_ratios, r0_candidate_ratios)
        and np.max(np.abs(r0_base_ratios - r0_oracle))
        <= STATE_ORACLE_TOLERANCE
    )

    target_area_residuals = {
        "r0_baseline": abs(
            r0_base_state.sections[TARGET_SECTION_INDEX].area_m2
            - TARGET_AREA_M2
        ),
        "r0_candidate": abs(
            r0_candidate_state.sections[TARGET_SECTION_INDEX].area_m2
            - TARGET_AREA_M2
        ),
        "r1_baseline": abs(
            r1_base_state.sections[TARGET_SECTION_INDEX].area_m2
            - TARGET_AREA_M2
        ),
        "r1_candidate": abs(
            r1_candidate_state.sections[TARGET_SECTION_INDEX].area_m2
            - TARGET_AREA_M2
        ),
    }
    task_ok = all(
        residual <= TASK_AREA_TOLERANCE_M2
        for residual in target_area_residuals.values()
    )

    base_state_error = float(
        np.max(np.abs(r1_base_ratios - r1_base_oracle))
    )
    candidate_state_error = float(
        np.max(np.abs(r1_candidate_ratios - r1_candidate_oracle))
    )
    state_oracle_ok = (
        base_state_error <= STATE_ORACLE_TOLERANCE
        and candidate_state_error <= STATE_ORACLE_TOLERANCE
    )

    physical_l2 = float(
        np.linalg.norm(r1_candidate_ratios - r1_base_ratios)
    )
    oracle_physical_l2 = float(
        oracle["r1_candidate_minus_baseline_l2"]
    )
    physical_effect_ok = (
        physical_l2 > MIN_PHYSICAL_L2_EFFECT
        and abs(physical_l2 - oracle_physical_l2)
        <= STATE_ORACLE_TOLERANCE
    )

    left_delta = float(
        r1_candidate_ratios[LEFT_NEIGHBOR_INDEX]
        - r1_base_ratios[LEFT_NEIGHBOR_INDEX]
    )
    right_delta = float(
        r1_candidate_ratios[RIGHT_NEIGHBOR_INDEX]
        - r1_base_ratios[RIGHT_NEIGHBOR_INDEX]
    )
    locality_ok = (
        left_delta > 0.0
        and abs(right_delta) <= RIGHT_SIDE_LOCALITY_TOLERANCE
    )

    state_rows: list[dict[str, Any]] = []
    states = {
        "r0_baseline": r0_base_ratios,
        "r0_candidate": r0_candidate_ratios,
        "r1_baseline": r1_base_ratios,
        "r1_candidate": r1_candidate_ratios,
    }
    for model_condition, ratios in states.items():
        for index, ratio in enumerate(ratios):
            state_rows.append(
                {
                    "model_condition": model_condition,
                    "section_index": index,
                    "area_ratio": float(ratio),
                    "area_m2": float(
                        morphology.rest_state.sections[index].area_m2
                        * ratio
                    ),
                    "score_sha256": score_hash_before,
                }
            )
    _write_csv(output_dir / "states.csv", state_rows)

    acoustic_states = {
        "r0": r0_base_state,
        "r1_baseline": r1_base_state,
        "r1_candidate": r1_candidate_state,
    }
    oracle_keys = {
        "r0": "r0_resonances_hz",
        "r1_baseline": "r1_baseline_resonances_hz",
        "r1_candidate": "r1_candidate_resonances_hz",
    }

    resonance_rows: list[dict[str, Any]] = []
    measured: dict[str, tuple[float, ...]] = {}
    floors: dict[tuple[str, int], float] = {}
    acoustic_oracle_ok = True

    for condition, state in acoustic_states.items():
        candidate_peaks = _measure_resonances(
            state,
            CANDIDATE_GRID_STEP_HZ,
        )
        reference_peaks = _measure_resonances(
            state,
            REFERENCE_GRID_STEP_HZ,
        )
        measured[condition] = candidate_peaks
        oracle_peaks = tuple(
            float(value) for value in oracle[oracle_keys[condition]]
        )

        for mode, (
            candidate_hz,
            reference_hz,
            oracle_hz,
        ) in enumerate(
            zip(
                candidate_peaks,
                reference_peaks,
                oracle_peaks,
                strict=True,
            ),
            start=1,
        ):
            candidate_error = abs(candidate_hz - oracle_hz)
            reference_error = abs(reference_hz - oracle_hz)
            floor_hz = max(
                CANDIDATE_GRID_STEP_HZ,
                abs(candidate_hz - reference_hz),
            )
            floors[(condition, mode)] = floor_hz
            resonance_rows.append(
                {
                    "model_condition": condition,
                    "mode": mode,
                    "candidate_peak_hz": candidate_hz,
                    "reference_peak_hz": reference_hz,
                    "oracle_peak_hz": oracle_hz,
                    "candidate_abs_error_hz": candidate_error,
                    "reference_abs_error_hz": reference_error,
                    "numerical_floor_hz": floor_hz,
                }
            )
            acoustic_oracle_ok = (
                acoustic_oracle_ok
                and candidate_error <= FREQUENCY_ORACLE_TOLERANCE_HZ
                and reference_error
                <= REFERENCE_FREQUENCY_ORACLE_TOLERANCE_HZ
            )
    _write_csv(output_dir / "resonances.csv", resonance_rows)

    effect_rows: list[dict[str, Any]] = []
    acoustic_effect_ok = True
    for mode in range(1, 4):
        baseline_hz = measured["r1_baseline"][mode - 1]
        candidate_hz = measured["r1_candidate"][mode - 1]
        effect_hz = abs(candidate_hz - baseline_hz)
        floor_hz = max(
            floors[("r1_baseline", mode)],
            floors[("r1_candidate", mode)],
        )
        ratio = effect_hz / floor_hz
        oracle_shift = float(
            oracle["r1_candidate_minus_baseline_resonance_hz"][mode - 1]
        )
        observed_shift = candidate_hz - baseline_hz
        effect_rows.append(
            {
                "mode": mode,
                "baseline_hz": baseline_hz,
                "candidate_hz": candidate_hz,
                "observed_shift_hz": observed_shift,
                "oracle_shift_hz": oracle_shift,
                "absolute_effect_hz": effect_hz,
                "numerical_floor_hz": floor_hz,
                "effect_over_floor": ratio,
            }
        )
        acoustic_effect_ok = (
            acoustic_effect_ok
            and ratio > DISCRIMINATION_MARGIN
            and math.copysign(1.0, observed_shift)
            == math.copysign(1.0, oracle_shift)
        )
    _write_csv(output_dir / "effects.csv", effect_rows)

    decision_name = _failure_decision(
        representation_ok=representation_ok,
        baseline_null_ok=baseline_null_ok,
        task_ok=task_ok,
        state_oracle_ok=state_oracle_ok,
        physical_effect_ok=physical_effect_ok,
        locality_ok=locality_ok,
        acoustic_oracle_ok=acoustic_oracle_ok,
        acoustic_effect_ok=acoustic_effect_ok,
    )

    decision: dict[str, Any] = {
        "decision": decision_name,
        "issue": 40,
        "experiment": 19,
        "research_question": (
            "whether an experiment-local reduced stiffness intervention "
            "changes body-specific quasi-static realization while the exact "
            "same task target remains achieved"
        ),
        "claim_scope": (
            "reduced dimensionless stiffness field in a 10-section "
            "Fidelity-0 tract; not biological tissue mechanics"
        ),
        "canonical_score_sha256": score_hash_before,
        "representation_ok": representation_ok,
        "baseline_null_ok": baseline_null_ok,
        "task_ok": task_ok,
        "state_oracle_ok": state_oracle_ok,
        "physical_effect_ok": physical_effect_ok,
        "locality_ok": locality_ok,
        "acoustic_oracle_ok": acoustic_oracle_ok,
        "acoustic_effect_ok": acoustic_effect_ok,
        "target_area_residuals_m2": target_area_residuals,
        "r1_state_max_abs_error": {
            "baseline": base_state_error,
            "candidate": candidate_state_error,
        },
        "r1_material_physical_l2": physical_l2,
        "r1_material_physical_l2_oracle": oracle_physical_l2,
        "left_neighbor_ratio_delta": left_delta,
        "right_neighbor_ratio_delta": right_delta,
        "minimum_acoustic_effect_over_floor": min(
            float(row["effect_over_floor"]) for row in effect_rows
        ),
        "parameters": {
            "tract_length_m": TRACT_LENGTH_M,
            "section_count": SECTION_COUNT,
            "rest_area_m2": REST_AREA_M2,
            "gesture_location": GESTURE_LOCATION,
            "target_section_index": TARGET_SECTION_INDEX,
            "target_area_m2": TARGET_AREA_M2,
            "smoothness_lambda": SMOOTHNESS_LAMBDA,
            "left_neighbor_index": LEFT_NEIGHBOR_INDEX,
            "baseline_left_relative_stiffness": (
                BASELINE_LEFT_RELATIVE_STIFFNESS
            ),
            "candidate_left_relative_stiffness": (
                CANDIDATE_LEFT_RELATIVE_STIFFNESS
            ),
            "candidate_grid_step_hz": CANDIDATE_GRID_STEP_HZ,
            "reference_grid_step_hz": REFERENCE_GRID_STEP_HZ,
            "discrimination_margin": DISCRIMINATION_MARGIN,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "elapsed_s": time.perf_counter() - started,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-019-output"),
    )
    args = parser.parse_args()
    decision = run(args.output_dir)
    print(json.dumps(decision, indent=2, sort_keys=True))
    if decision["decision"] != SUPPORT_DECISION:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
