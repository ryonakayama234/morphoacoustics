"""Experiment 017: explicit embodied infeasibility at an articulator reach boundary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import time
from pathlib import Path
from typing import Any

import numpy as np

from morphoacoustics import (
    ArticulatorSpec,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    FeasibilityStatus,
    Gesture,
    GestureScore,
    Task,
    TaskParameter,
    simulate_snapshot,
)
from morphoacoustics.acoustics import (
    ImpedanceRequest,
    ImpedanceResponse,
    SegmentedTubeBackend,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import (
    PreparationProvenance,
    PreparedMorphology,
    prepare_tract1d,
)
from morphoacoustics.realization import Tract1DRealizer

TRACT_LENGTH_M = 0.17
SECTION_COUNT = 10
REST_AREA_M2 = 3.0e-4
TARGET_AREA_M2 = 2.0e-4
GESTURE_LOCATION = 0.65
REACHABLE_START = 0.30
GESTURE_ONSET_S = 0.0
GESTURE_OFFSET_S = 0.3
EVALUATION_TIME_S = 0.1
ORACLE_TOLERANCE = 1.0e-15

CONDITIONS = (
    ("M_plus", 0.70, FeasibilityStatus.FEASIBLE),
    ("M_boundary", 0.65, FeasibilityStatus.FEASIBLE),
    ("M_minus", 0.60, FeasibilityStatus.INFEASIBLE),
)

PROBE_FREQUENCIES_HZ = np.asarray(
    [431.0, 617.0, 893.0, 1279.0, 1693.0, 2111.0, 2531.0, 2897.0],
    dtype=np.float64,
)

SUPPORT_DECISION = "SUPPORT_EMBODIED_INFEASIBILITY"
ORACLE_PATH = Path(__file__).with_name("wolfram") / "reach_boundary_oracle.json"


class CountingAcousticBackend:
    """Count actual acoustic evaluations while delegating to Fidelity-0."""

    def __init__(self) -> None:
        self.call_count = 0
        self._inner = SegmentedTubeBackend()

    def simulate_snapshot(
        self,
        state: Tract1DGeometry,
        request: ImpedanceRequest,
    ) -> ImpedanceResponse:
        self.call_count += 1
        return self._inner.simulate_snapshot(state, request)


def _creature(reachable_end: float) -> CreatureSpec:
    return CreatureSpec(
        name="e1b-reach-body",
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
        articulators=(
            ArticulatorSpec(
                id="tongue",
                cavity_id="oral",
                kind="tongue",
                reachable_start=REACHABLE_START,
                reachable_end=reachable_end,
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


def _prepared(
    creature: CreatureSpec,
    geometry: Tract1DGeometry,
) -> PreparedMorphology[Tract1DGeometry]:
    return prepare_tract1d(
        creature,
        geometry,
        provenance=PreparationProvenance(
            source="experiment-017",
            model="reach-boundary-fixture",
            notes=("same-prepared-geometry-across-all-conditions",),
        ),
    )


def _canonical_score() -> GestureScore:
    return GestureScore(
        (
            Gesture(
                task=Task.CONSTRICT,
                onset_s=GESTURE_ONSET_S,
                offset_s=GESTURE_OFFSET_S,
                target="oral",
                location=GESTURE_LOCATION,
                parameters=(
                    TaskParameter(
                        "target_area",
                        TARGET_AREA_M2,
                        "m2",
                    ),
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
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _response_sha256(response: ImpedanceResponse) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(response.frequencies_hz).tobytes())
    digest.update(
        np.ascontiguousarray(response.input_impedance_pa_s_m3).tobytes()
    )
    return digest.hexdigest()


def _modified_indices(
    rest: Tract1DGeometry,
    realized: Tract1DGeometry,
) -> tuple[int, ...]:
    return tuple(
        index
        for index, (rest_section, realized_section) in enumerate(
            zip(rest.sections, realized.sections, strict=True)
        )
        if rest_section != realized_section
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _oracle_condition(
    oracle: dict[str, Any],
    reachable_end: float,
) -> dict[str, Any]:
    for condition in oracle["conditions"]:
        if math.isclose(
            float(condition["reachable_end"]),
            reachable_end,
            rel_tol=0.0,
            abs_tol=ORACLE_TOLERANCE,
        ):
            return condition
    raise KeyError(reachable_end)


def _morphology_intervention_isolated(
    creatures: dict[str, CreatureSpec],
    prepared: dict[str, PreparedMorphology[Tract1DGeometry]],
) -> bool:
    baseline = creatures["M_plus"]
    baseline_articulator = baseline.articulators[0]

    for creature in creatures.values():
        if (
            creature.name != baseline.name
            or creature.cavities != baseline.cavities
            or creature.connections != baseline.connections
            or creature.source_organs != baseline.source_organs
            or len(creature.articulators) != 1
        ):
            return False

        articulator = creature.articulators[0]
        if (
            articulator.id != baseline_articulator.id
            or articulator.cavity_id != baseline_articulator.cavity_id
            or articulator.kind != baseline_articulator.kind
            or not math.isclose(
                articulator.reachable_start,
                baseline_articulator.reachable_start,
                rel_tol=0.0,
                abs_tol=0.0,
            )
        ):
            return False

    rest_states = [morphology.rest_state for morphology in prepared.values()]
    return all(state == rest_states[0] for state in rest_states[1:])


def _failure_decision(
    *,
    representation_ok: bool,
    causal_isolation_ok: bool,
    invalid_present: bool,
    unsupported_present: bool,
    positive_feasibility_ok: bool,
    negative_infeasibility_ok: bool,
    task_residual_ok: bool,
    failure_attribution_ok: bool,
    no_fallback_ok: bool,
    null_control_ok: bool,
) -> str:
    if not representation_ok:
        return "REPRESENTATION_LEAK"
    if not causal_isolation_ok:
        return "CAUSAL_TRACE_INCONSISTENT"
    if invalid_present:
        return "INVALID_REQUEST_REGRESSION"
    if unsupported_present:
        return "BACKEND_UNSUPPORTED"
    if not positive_feasibility_ok or not task_residual_ok:
        return "TASK_REALIZATION_FAILED"
    if not negative_infeasibility_ok:
        return "FEASIBILITY_BOUNDARY_FAILED"
    if not failure_attribution_ok:
        return "FAILURE_ATTRIBUTION_INCONSISTENT"
    if not no_fallback_ok:
        return "ACOUSTIC_FALLBACK_LEAK"
    if not null_control_ok:
        return "CAPABILITY_NULL_CONTROL_FAILED"
    return SUPPORT_DECISION


def run(output_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename in (
        "conditions.csv",
        "feasible_null_control.csv",
        "decision.json",
    ):
        path = output_dir / filename
        if path.exists():
            path.unlink()

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    geometry = _geometry()
    score = _canonical_score()
    score_hash_before = _score_sha256(score)

    creatures = {
        label: _creature(reachable_end)
        for label, reachable_end, _ in CONDITIONS
    }
    prepared = {
        label: _prepared(creatures[label], geometry)
        for label, _, _ in CONDITIONS
    }

    causal_isolation_ok = _morphology_intervention_isolated(
        creatures,
        prepared,
    )

    request = ImpedanceRequest(PROBE_FREQUENCIES_HZ)
    results: dict[str, dict[str, Any]] = {}
    condition_rows: list[dict[str, Any]] = []
    oracle_ok = True

    for label, reachable_end, expected_status in CONDITIONS:
        backend = CountingAcousticBackend()
        result = simulate_snapshot(
            morphology=prepared[label],
            score=score,
            realizer=Tract1DRealizer(),
            acoustic_backend=backend,
            acoustic_request=request,
            time_s=EVALUATION_TIME_S,
        )

        status = result.realization.feasibility.status
        issues = result.realization.feasibility.issues
        state = result.realization.state
        acoustics = result.acoustics
        condition_oracle = _oracle_condition(oracle, reachable_end)

        normalized_margin = reachable_end - GESTURE_LOCATION
        physical_margin_m = TRACT_LENGTH_M * normalized_margin
        gesture_position_m = TRACT_LENGTH_M * GESTURE_LOCATION
        reach_end_position_m = TRACT_LENGTH_M * reachable_end

        oracle_match = (
            math.isclose(
                normalized_margin,
                float(condition_oracle["normalized_reach_margin"]),
                rel_tol=0.0,
                abs_tol=ORACLE_TOLERANCE,
            )
            and math.isclose(
                physical_margin_m,
                float(condition_oracle["physical_reach_margin_m"]),
                rel_tol=0.0,
                abs_tol=ORACLE_TOLERANCE,
            )
            and math.isclose(
                gesture_position_m,
                float(condition_oracle["gesture_position_m"]),
                rel_tol=0.0,
                abs_tol=ORACLE_TOLERANCE,
            )
            and math.isclose(
                reach_end_position_m,
                float(condition_oracle["reach_end_position_m"]),
                rel_tol=0.0,
                abs_tol=ORACLE_TOLERANCE,
            )
            and str(condition_oracle["expected_status"]) == expected_status.value
        )
        oracle_ok = oracle_ok and oracle_match

        if state is not None:
            selected_section_index = prepared[label].rest_state.section_index_at(
                GESTURE_LOCATION
            )
            modified_indices = _modified_indices(
                prepared[label].rest_state,
                state,
            )
            realized_area_m2 = state.sections[selected_section_index].area_m2
            area_residual_m2 = abs(realized_area_m2 - TARGET_AREA_M2)
        else:
            selected_section_index = None
            modified_indices = ()
            realized_area_m2 = None
            area_residual_m2 = None

        response_hash = (
            _response_sha256(acoustics)
            if isinstance(acoustics, ImpedanceResponse)
            else None
        )

        results[label] = {
            "status": status,
            "issues": issues,
            "state": state,
            "acoustics": acoustics,
            "backend_call_count": backend.call_count,
            "score_sha256": _score_sha256(score),
            "selected_section_index": selected_section_index,
            "modified_indices": modified_indices,
            "realized_area_m2": realized_area_m2,
            "area_residual_m2": area_residual_m2,
            "response_sha256": response_hash,
        }

        condition_rows.append(
            {
                "condition": label,
                "reachable_start": REACHABLE_START,
                "reachable_end": reachable_end,
                "gesture_location": GESTURE_LOCATION,
                "normalized_reach_margin": normalized_margin,
                "physical_reach_margin_m": physical_margin_m,
                "expected_status": expected_status.value,
                "actual_status": status.value,
                "issue_codes": ",".join(issue.code for issue in issues),
                "issue_gesture_indices": ",".join(
                    "" if issue.gesture_index is None else str(issue.gesture_index)
                    for issue in issues
                ),
                "state_present": state is not None,
                "acoustics_present": acoustics is not None,
                "acoustic_backend_call_count": backend.call_count,
                "score_sha256": results[label]["score_sha256"],
                "selected_section_index": selected_section_index,
                "modified_section_indices": ",".join(
                    str(index) for index in modified_indices
                ),
                "realized_area_m2": realized_area_m2,
                "area_residual_m2": area_residual_m2,
                "response_sha256": response_hash,
                "wolfram_oracle_match": oracle_match,
            }
        )

    _write_csv(output_dir / "conditions.csv", condition_rows)

    score_hash_after = _score_sha256(score)
    representation_ok = (
        score_hash_before == score_hash_after
        and {
            str(results[label]["score_sha256"])
            for label, _, _ in CONDITIONS
        }
        == {score_hash_before}
    )

    statuses = {
        label: results[label]["status"]
        for label, _, _ in CONDITIONS
    }
    invalid_present = any(
        status is FeasibilityStatus.INVALID for status in statuses.values()
    )
    unsupported_present = any(
        status is FeasibilityStatus.UNSUPPORTED for status in statuses.values()
    )

    positive_feasibility_ok = (
        statuses["M_plus"] is FeasibilityStatus.FEASIBLE
        and statuses["M_boundary"] is FeasibilityStatus.FEASIBLE
    )
    negative_infeasibility_ok = (
        statuses["M_minus"] is FeasibilityStatus.INFEASIBLE
    )

    task_residual_ok = positive_feasibility_ok
    if positive_feasibility_ok:
        for label in ("M_plus", "M_boundary"):
            task_residual_ok = (
                task_residual_ok
                and results[label]["selected_section_index"] == 6
                and results[label]["modified_indices"] == (6,)
                and float(results[label]["area_residual_m2"]) <= 1.0e-18
            )

    minus_issues = results["M_minus"]["issues"]
    failure_attribution_ok = (
        negative_infeasibility_ok
        and len(minus_issues) == 1
        and minus_issues[0].code == "LOCATION_UNREACHABLE"
        and minus_issues[0].gesture_index == 0
    )

    no_fallback_ok = (
        negative_infeasibility_ok
        and results["M_minus"]["state"] is None
        and results["M_minus"]["acoustics"] is None
        and results["M_minus"]["backend_call_count"] == 0
    )

    plus_state = results["M_plus"]["state"]
    boundary_state = results["M_boundary"]["state"]
    plus_acoustics = results["M_plus"]["acoustics"]
    boundary_acoustics = results["M_boundary"]["acoustics"]

    states_exactly_equal = (
        plus_state is not None
        and boundary_state is not None
        and plus_state == boundary_state
    )
    acoustics_exactly_equal = (
        isinstance(plus_acoustics, ImpedanceResponse)
        and isinstance(boundary_acoustics, ImpedanceResponse)
        and np.array_equal(
            plus_acoustics.frequencies_hz,
            boundary_acoustics.frequencies_hz,
        )
        and np.array_equal(
            plus_acoustics.input_impedance_pa_s_m3,
            boundary_acoustics.input_impedance_pa_s_m3,
            equal_nan=True,
        )
    )
    feasible_backend_calls_ok = (
        results["M_plus"]["backend_call_count"] == 1
        and results["M_boundary"]["backend_call_count"] == 1
    )

    if (
        isinstance(plus_acoustics, ImpedanceResponse)
        and isinstance(boundary_acoustics, ImpedanceResponse)
    ):
        max_acoustic_delta = float(
            np.nanmax(
                np.abs(
                    plus_acoustics.input_impedance_pa_s_m3
                    - boundary_acoustics.input_impedance_pa_s_m3
                )
            )
        )
    else:
        max_acoustic_delta = None

    null_control_ok = (
        states_exactly_equal
        and acoustics_exactly_equal
        and feasible_backend_calls_ok
        and results["M_plus"]["response_sha256"]
        == results["M_boundary"]["response_sha256"]
    )

    null_rows = [
        {
            "comparison": "M_plus_vs_M_boundary",
            "realized_states_exactly_equal": states_exactly_equal,
            "acoustic_arrays_exactly_equal": acoustics_exactly_equal,
            "response_sha256_equal": (
                results["M_plus"]["response_sha256"]
                == results["M_boundary"]["response_sha256"]
            ),
            "max_abs_impedance_delta": max_acoustic_delta,
            "M_plus_backend_calls": results["M_plus"]["backend_call_count"],
            "M_boundary_backend_calls": results["M_boundary"][
                "backend_call_count"
            ],
        }
    ]
    _write_csv(
        output_dir / "feasible_null_control.csv",
        null_rows,
    )

    decision_name = _failure_decision(
        representation_ok=representation_ok,
        causal_isolation_ok=causal_isolation_ok and oracle_ok,
        invalid_present=invalid_present,
        unsupported_present=unsupported_present,
        positive_feasibility_ok=positive_feasibility_ok,
        negative_infeasibility_ok=negative_infeasibility_ok,
        task_residual_ok=task_residual_ok,
        failure_attribution_ok=failure_attribution_ok,
        no_fallback_ok=no_fallback_ok,
        null_control_ok=null_control_ok,
    )

    decision: dict[str, Any] = {
        "decision": decision_name,
        "issue": 40,
        "experiment": 17,
        "research_question": (
            "whether one unchanged valid supported CONSTRICT task crosses from "
            "FEASIBLE to explicit INFEASIBLE when only articulator reachable_end "
            "crosses the preregistered task location"
        ),
        "claim_scope": "Fidelity-0 articulator reach-boundary fixture only",
        "canonical_gesture": _score_payload(score),
        "representation": {
            "score_sha256_before": score_hash_before,
            "score_sha256_after": score_hash_after,
            "unchanged_across_all_conditions": representation_ok,
        },
        "morphology_intervention": {
            "parameter": "tongue.reachable_end",
            "fixed_reachable_start": REACHABLE_START,
            "condition_reachable_ends": {
                label: reachable_end
                for label, reachable_end, _ in CONDITIONS
            },
            "prepared_geometry_identical": all(
                morphology.rest_state == geometry
                for morphology in prepared.values()
            ),
            "only_reach_end_changes": causal_isolation_ok,
        },
        "reach_boundary": {
            "gesture_location": GESTURE_LOCATION,
            "gesture_position_m": TRACT_LENGTH_M * GESTURE_LOCATION,
            "oracle_tolerance": ORACLE_TOLERANCE,
            "wolfram_oracle_match": oracle_ok,
        },
        "gates": {
            "representation_invariant": representation_ok,
            "morphology_intervention_isolated": causal_isolation_ok,
            "wolfram_reach_margin_oracle_match": oracle_ok,
            "no_invalid_status": not invalid_present,
            "no_unsupported_status": not unsupported_present,
            "positive_and_boundary_conditions_feasible": positive_feasibility_ok,
            "feasible_task_residuals_exact": task_residual_ok,
            "negative_condition_infeasible": negative_infeasibility_ok,
            "negative_failure_attributed_to_location_unreachable": (
                failure_attribution_ok
            ),
            "negative_condition_has_no_state_or_acoustics": no_fallback_ok,
            "feasible_capability_null_control_exact": null_control_ok,
        },
        "status_by_condition": {
            label: results[label]["status"].value
            for label, _, _ in CONDITIONS
        },
        "acoustic_backend_calls_by_condition": {
            label: results[label]["backend_call_count"]
            for label, _, _ in CONDITIONS
        },
        "causal_trace": {
            "changed_body_axis": "tongue.reachable_end only",
            "unchanged_task": "CONSTRICT oral location=0.65 target_area=2e-4 m2",
            "M_plus": (
                "positive reach margin -> FEASIBLE -> physical state -> acoustics"
            ),
            "M_boundary": (
                "zero reach margin -> FEASIBLE -> same physical state -> same acoustics"
            ),
            "M_minus": (
                "negative reach margin -> LOCATION_UNREACHABLE -> INFEASIBLE -> "
                "state=None -> acoustic backend calls=0 -> acoustics=None"
            ),
        },
        "wolfram_oracle": oracle,
        "limitations": [
            "reachability is a normalized interval constraint, not a biomechanical strength/contact model",
            "tract geometry is identical across conditions",
            "only one articulator and one CONSTRICT task are tested",
            "no claim about biological reachability realism",
            "no waveform, source, perception, naturalness, tissue mechanics, or FSI claim",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }

    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-017-output"),
    )
    args = parser.parse_args()

    decision = run(args.output_dir)
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    if decision["decision"] != SUPPORT_DECISION:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
