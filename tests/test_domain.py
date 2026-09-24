import pytest

from morphoacoustics import (
    CavityConnection,
    CavitySpec,
    CreatureSpec,
    FeasibilityReport,
    FeasibilityStatus,
    Gesture,
    SimulationResult,
    Task,
    TaskParameter,
)


def test_creature_rejects_unknown_connection_endpoint() -> None:
    with pytest.raises(ValueError, match="unknown target cavity"):
        CreatureSpec(
            name="broken",
            cavities=(CavitySpec(id="oral"),),
            connections=(CavityConnection(source_id="oral", target_id="nasal"),),
        )


def test_creature_rejects_duplicate_cavity_ids() -> None:
    with pytest.raises(ValueError, match="cavity ids must be unique"):
        CreatureSpec(
            name="duplicate",
            cavities=(CavitySpec(id="oral"), CavitySpec(id="oral")),
        )


def test_gesture_location_is_normalized() -> None:
    with pytest.raises(ValueError, match=r"within \[0, 1\]"):
        Gesture(
            task=Task.CONSTRICT,
            onset_s=0.0,
            offset_s=0.1,
            location=1.1,
        )


def test_gesture_requires_explicit_parameter_units() -> None:
    with pytest.raises(ValueError, match="unit must be explicit"):
        TaskParameter(name="aperture_area", value=1.0e-4, unit="")


def test_infeasible_simulation_may_return_no_waveform() -> None:
    result = SimulationResult(
        waveform=(),
        sample_rate_hz=48_000,
        feasibility=FeasibilityReport(status=FeasibilityStatus.INFEASIBLE),
    )

    assert result.waveform == ()
    assert result.feasibility.status is FeasibilityStatus.INFEASIBLE
