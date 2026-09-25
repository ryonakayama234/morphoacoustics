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

from .protocol import RealizationResult


class Tract1DRealizer:
    """Realize Fidelity-0 CONSTRICT tasks onto a prepared serial 1D tract.

    ``rest_geometry`` is a backend-specific prepared physical representation;
    it is deliberately separate from ``CreatureSpec`` so the domain schema does
    not become a 1D tube schema. This realizer validates that the selected
    cavity exists and is not connected to another cavity before solving it.

    Active tasks outside Fidelity-0 capability are ``UNSUPPORTED``. Requests
    that violate the task contract are ``INVALID``. A valid task that this
    creature cannot physically reach is ``INFEASIBLE``.
    """

    def __init__(self, rest_geometry: Tract1DGeometry) -> None:
        self.rest_geometry = rest_geometry

    def realize_snapshot(
        self,
        creature: CreatureSpec,
        score: GestureScore,
        time_s: float,
    ) -> RealizationResult[Tract1DGeometry]:
        if not isfinite(time_s) or time_s < 0.0:
            raise ValueError("time_s must be finite and >= 0")

        capability_failure = self._validate_creature_capability(creature)
        if capability_failure is not None:
            return capability_failure

        sections = list(self.rest_geometry.sections)
        active = [
            (index, gesture)
            for index, gesture in enumerate(score.gestures)
            if gesture.onset_s <= time_s < gesture.offset_s
        ]

        for gesture_index, gesture in active:
            if gesture.task is not Task.CONSTRICT:
                return _failed(
                    FeasibilityStatus.UNSUPPORTED,
                    "TASK_UNSUPPORTED",
                    f"fidelity-0 realizer does not support active task {gesture.task.value}",
                    gesture_index,
                )

            failure = self._apply_constriction(
                creature=creature,
                gesture=gesture,
                gesture_index=gesture_index,
                sections=sections,
            )
            if failure is not None:
                status, issue = failure
                return RealizationResult(
                    state=None,
                    feasibility=FeasibilityReport(
                        status=status,
                        issues=(issue,),
                    ),
                )

        return RealizationResult(
            state=Tract1DGeometry(
                cavity_id=self.rest_geometry.cavity_id,
                sections=tuple(sections),
            ),
            feasibility=FeasibilityReport(status=FeasibilityStatus.FEASIBLE),
        )

    def _validate_creature_capability(
        self,
        creature: CreatureSpec,
    ) -> RealizationResult[Tract1DGeometry] | None:
        known_cavities = {cavity.id for cavity in creature.cavities}
        cavity_id = self.rest_geometry.cavity_id
        if cavity_id not in known_cavities:
            return _failed(
                FeasibilityStatus.INVALID,
                "PREPARED_GEOMETRY_CAVITY_UNKNOWN",
                f"prepared 1D geometry cavity {cavity_id!r} is not in creature",
            )

        connected = [
            connection
            for connection in creature.connections
            if connection.source_id == cavity_id or connection.target_id == cavity_id
        ]
        if connected:
            return _failed(
                FeasibilityStatus.UNSUPPORTED,
                "CONNECTED_CAVITY_UNSUPPORTED",
                (
                    f"fidelity-0 supports an isolated serial cavity; {cavity_id!r} "
                    "participates in a cavity connection"
                ),
            )
        return None

    def _apply_constriction(
        self,
        creature: CreatureSpec,
        gesture: Gesture,
        gesture_index: int,
        sections: list[TubeSection],
    ) -> tuple[FeasibilityStatus, FeasibilityIssue] | None:
        known_cavities = {cavity.id for cavity in creature.cavities}
        target_cavity = gesture.target or self.rest_geometry.cavity_id
        if target_cavity not in known_cavities:
            return _issue(
                FeasibilityStatus.INVALID,
                "UNKNOWN_TARGET_CAVITY",
                f"gesture targets unknown cavity {target_cavity!r}",
                gesture_index,
            )
        if target_cavity != self.rest_geometry.cavity_id:
            return _issue(
                FeasibilityStatus.UNSUPPORTED,
                "CAVITY_UNSUPPORTED_BY_REALIZER",
                (
                    f"1D realizer owns cavity {self.rest_geometry.cavity_id!r}, "
                    f"not {target_cavity!r}"
                ),
                gesture_index,
            )

        if gesture.location is None:
            return _issue(
                FeasibilityStatus.INVALID,
                "MISSING_LOCATION",
                "CONSTRICT requires a normalized location",
                gesture_index,
            )

        compatible = [
            articulator
            for articulator in creature.articulators
            if articulator.cavity_id == target_cavity
            and articulator.reachable_start <= gesture.location <= articulator.reachable_end
        ]
        if not compatible:
            return _issue(
                FeasibilityStatus.INFEASIBLE,
                "LOCATION_UNREACHABLE",
                (
                    f"no articulator in cavity {target_cavity!r} can reach "
                    f"location {gesture.location:.3f}"
                ),
                gesture_index,
            )

        target_area = gesture.parameter("target_area")
        if target_area is None:
            return _issue(
                FeasibilityStatus.INVALID,
                "MISSING_TARGET_AREA",
                "CONSTRICT requires target_area",
                gesture_index,
            )
        if target_area.unit != "m2":
            return _issue(
                FeasibilityStatus.INVALID,
                "UNSUPPORTED_TARGET_AREA_UNIT",
                "fidelity-0 CONSTRICT requires target_area in m2",
                gesture_index,
            )
        if target_area.value <= 0.0:
            return _issue(
                FeasibilityStatus.INVALID,
                "NONPOSITIVE_TARGET_AREA",
                "target_area must be > 0",
                gesture_index,
            )

        section_index = self.rest_geometry.section_index_at(gesture.location)
        rest_section = self.rest_geometry.sections[section_index]
        if target_area.value > rest_section.area_m2:
            return _issue(
                FeasibilityStatus.INVALID,
                "TARGET_AREA_NOT_CONSTRICTIVE",
                (
                    f"target area {target_area.value:g} m2 exceeds rest area "
                    f"{rest_section.area_m2:g} m2"
                ),
                gesture_index,
            )

        current = sections[section_index]
        sections[section_index] = TubeSection(
            length_m=current.length_m,
            area_m2=min(current.area_m2, target_area.value),
        )
        return None


def _issue(
    status: FeasibilityStatus,
    code: str,
    message: str,
    gesture_index: int,
) -> tuple[FeasibilityStatus, FeasibilityIssue]:
    return (
        status,
        FeasibilityIssue(
            code=code,
            message=message,
            gesture_index=gesture_index,
        ),
    )


def _failed(
    status: FeasibilityStatus,
    code: str,
    message: str,
    gesture_index: int | None = None,
) -> RealizationResult[Tract1DGeometry]:
    return RealizationResult(
        state=None,
        feasibility=FeasibilityReport(
            status=status,
            issues=(
                FeasibilityIssue(
                    code=code,
                    message=message,
                    gesture_index=gesture_index,
                ),
            ),
        ),
    )
