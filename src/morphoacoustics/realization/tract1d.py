from __future__ import annotations

from math import isfinite

from morphoacoustics.domain.creature import CreatureSpec
from morphoacoustics.domain.gesture import Gesture, GestureScore, Task
from morphoacoustics.domain.result import (
    FeasibilityIssue,
    FeasibilityReport,
    FeasibilityStatus,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import TRACT1D_BACKEND_ID, PreparedMorphology

from .protocol import RealizationResult


class Tract1DRealizer:
    """Realize Fidelity-0 CONSTRICT tasks on a prepared serial 1D tract.

    The realizer is an algorithm, not a body container.  Backend-specific rest
    geometry arrives through ``PreparedMorphology`` so the numerical body and
    the ``CreatureSpec`` it represents are explicitly bound and inspectable.

    Failure classification is phase-ordered across the entire active gesture
    set: invalid requests are reported before backend capability failures, and
    capability failures are reported before morphology-dependent infeasibility.
    This keeps the status independent of gesture tuple order.
    """

    def realize_snapshot(
        self,
        morphology: PreparedMorphology[Tract1DGeometry],
        score: GestureScore,
        time_s: float,
    ) -> RealizationResult[Tract1DGeometry]:
        if not isfinite(time_s) or time_s < 0.0:
            raise ValueError("time_s must be finite and >= 0")

        creature = morphology.creature
        rest_geometry = morphology.rest_state
        active = [
            (index, gesture)
            for index, gesture in enumerate(score.gestures)
            if gesture.onset_s <= time_s < gesture.offset_s
        ]

        invalid_issues = self._validate_prepared_state(morphology)
        invalid_issues += self._validate_requests(
            creature,
            rest_geometry,
            active,
        )
        if invalid_issues:
            return _failed_many(FeasibilityStatus.INVALID, invalid_issues)

        unsupported_issues = self._check_capability(
            morphology,
            active,
        )
        if unsupported_issues:
            return _failed_many(FeasibilityStatus.UNSUPPORTED, unsupported_issues)

        infeasible_issues = self._check_reachability(
            creature,
            rest_geometry,
            active,
        )
        if infeasible_issues:
            return _failed_many(FeasibilityStatus.INFEASIBLE, infeasible_issues)

        sections = list(rest_geometry.sections)
        for _, gesture in active:
            self._apply_validated_constriction(
                gesture,
                rest_geometry,
                sections,
            )

        return RealizationResult(
            state=Tract1DGeometry(
                cavity_id=rest_geometry.cavity_id,
                sections=tuple(sections),
            ),
            feasibility=FeasibilityReport(status=FeasibilityStatus.FEASIBLE),
        )

    def _validate_prepared_state(
        self,
        morphology: PreparedMorphology[Tract1DGeometry],
    ) -> tuple[FeasibilityIssue, ...]:
        issues: list[FeasibilityIssue] = []
        creature = morphology.creature
        rest_geometry = morphology.rest_state

        if morphology.backend_id != TRACT1D_BACKEND_ID:
            issues.append(
                FeasibilityIssue(
                    code="PREPARED_BACKEND_MISMATCH",
                    message=(
                        f"Tract1DRealizer requires backend_id {TRACT1D_BACKEND_ID!r}, "
                        f"got {morphology.backend_id!r}"
                    ),
                )
            )

        known_cavities = {cavity.id for cavity in creature.cavities}
        cavity_id = rest_geometry.cavity_id
        if cavity_id not in known_cavities:
            issues.append(
                FeasibilityIssue(
                    code="PREPARED_GEOMETRY_CAVITY_UNKNOWN",
                    message=(
                        f"prepared 1D geometry cavity {cavity_id!r} is not in creature"
                    ),
                )
            )

        return tuple(issues)

    def _validate_requests(
        self,
        creature: CreatureSpec,
        rest_geometry: Tract1DGeometry,
        active: list[tuple[int, Gesture]],
    ) -> tuple[FeasibilityIssue, ...]:
        issues: list[FeasibilityIssue] = []
        known_cavities = {cavity.id for cavity in creature.cavities}

        for gesture_index, gesture in active:
            target_cavity = gesture.target or rest_geometry.cavity_id
            if target_cavity not in known_cavities:
                issues.append(
                    FeasibilityIssue(
                        code="UNKNOWN_TARGET_CAVITY",
                        message=f"gesture targets unknown cavity {target_cavity!r}",
                        gesture_index=gesture_index,
                    )
                )
                continue

            if gesture.task is not Task.CONSTRICT:
                continue

            location = gesture.location
            if location is None:
                issues.append(
                    FeasibilityIssue(
                        code="MISSING_LOCATION",
                        message="CONSTRICT requires a normalized location",
                        gesture_index=gesture_index,
                    )
                )

            target_area = gesture.parameter("target_area")
            if target_area is None:
                issues.append(
                    FeasibilityIssue(
                        code="MISSING_TARGET_AREA",
                        message="CONSTRICT requires target_area",
                        gesture_index=gesture_index,
                    )
                )
                continue

            if target_area.unit != "m2":
                issues.append(
                    FeasibilityIssue(
                        code="UNSUPPORTED_TARGET_AREA_UNIT",
                        message="fidelity-0 CONSTRICT requires target_area in m2",
                        gesture_index=gesture_index,
                    )
                )
                continue

            if target_area.value <= 0.0:
                issues.append(
                    FeasibilityIssue(
                        code="NONPOSITIVE_TARGET_AREA",
                        message="target_area must be > 0",
                        gesture_index=gesture_index,
                    )
                )
                continue

            if location is None:
                continue

            section_index = rest_geometry.section_index_at(location)
            rest_section = rest_geometry.sections[section_index]
            if target_area.value > rest_section.area_m2:
                issues.append(
                    FeasibilityIssue(
                        code="TARGET_AREA_NOT_CONSTRICTIVE",
                        message=(
                            f"target area {target_area.value:g} m2 exceeds rest area "
                            f"{rest_section.area_m2:g} m2"
                        ),
                        gesture_index=gesture_index,
                    )
                )

        return tuple(issues)

    def _check_capability(
        self,
        morphology: PreparedMorphology[Tract1DGeometry],
        active: list[tuple[int, Gesture]],
    ) -> tuple[FeasibilityIssue, ...]:
        issues: list[FeasibilityIssue] = []
        creature = morphology.creature
        cavity_id = morphology.rest_state.cavity_id

        connected = [
            connection
            for connection in creature.connections
            if connection.source_id == cavity_id or connection.target_id == cavity_id
        ]
        if connected:
            issues.append(
                FeasibilityIssue(
                    code="CONNECTED_CAVITY_UNSUPPORTED",
                    message=(
                        f"fidelity-0 supports an isolated serial cavity; {cavity_id!r} "
                        "participates in a cavity connection"
                    ),
                )
            )

        for gesture_index, gesture in active:
            if gesture.task is not Task.CONSTRICT:
                issues.append(
                    FeasibilityIssue(
                        code="TASK_UNSUPPORTED",
                        message=(
                            "fidelity-0 realizer does not support active task "
                            f"{gesture.task.value}"
                        ),
                        gesture_index=gesture_index,
                    )
                )
                continue

            target_cavity = gesture.target or cavity_id
            if target_cavity != cavity_id:
                issues.append(
                    FeasibilityIssue(
                        code="CAVITY_UNSUPPORTED_BY_REALIZER",
                        message=(
                            f"1D realizer owns cavity {cavity_id!r}, "
                            f"not {target_cavity!r}"
                        ),
                        gesture_index=gesture_index,
                    )
                )

        return tuple(issues)

    def _check_reachability(
        self,
        creature: CreatureSpec,
        rest_geometry: Tract1DGeometry,
        active: list[tuple[int, Gesture]],
    ) -> tuple[FeasibilityIssue, ...]:
        issues: list[FeasibilityIssue] = []

        for gesture_index, gesture in active:
            location = gesture.location
            if location is None:
                raise RuntimeError("validated CONSTRICT gesture must have location")

            target_cavity = gesture.target or rest_geometry.cavity_id
            compatible = [
                articulator
                for articulator in creature.articulators
                if articulator.cavity_id == target_cavity
                and articulator.reachable_start <= location <= articulator.reachable_end
            ]
            if not compatible:
                issues.append(
                    FeasibilityIssue(
                        code="LOCATION_UNREACHABLE",
                        message=(
                            f"no articulator in cavity {target_cavity!r} can reach "
                            f"location {location:.3f}"
                        ),
                        gesture_index=gesture_index,
                    )
                )

        return tuple(issues)

    def _apply_validated_constriction(
        self,
        gesture: Gesture,
        rest_geometry: Tract1DGeometry,
        sections: list[TubeSection],
    ) -> None:
        location = gesture.location
        target_area = gesture.parameter("target_area")
        if location is None or target_area is None:
            raise RuntimeError("validated CONSTRICT gesture is incomplete")

        section_index = rest_geometry.section_index_at(location)
        current = sections[section_index]
        sections[section_index] = TubeSection(
            length_m=current.length_m,
            area_m2=min(current.area_m2, target_area.value),
        )


def _failed_many(
    status: FeasibilityStatus,
    issues: tuple[FeasibilityIssue, ...],
) -> RealizationResult[Tract1DGeometry]:
    return RealizationResult(
        state=None,
        feasibility=FeasibilityReport(status=status, issues=issues),
    )
