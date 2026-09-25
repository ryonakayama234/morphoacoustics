"""morphoacoustics research kernel."""

from .domain import (
    ArticulatorSpec,
    CavityConnection,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    FeasibilityIssue,
    FeasibilityReport,
    FeasibilityStatus,
    Gesture,
    GestureScore,
    Provenance,
    SimulationResult,
    SourceOrganSpec,
    Task,
    TaskParameter,
    TraceSeries,
)
from .simulation import SnapshotSimulationResult, simulate_snapshot

__all__ = [
    "ArticulatorSpec",
    "CavityConnection",
    "CavityKind",
    "CavitySpec",
    "CreatureSpec",
    "FeasibilityIssue",
    "FeasibilityReport",
    "FeasibilityStatus",
    "Gesture",
    "GestureScore",
    "Provenance",
    "SimulationResult",
    "SnapshotSimulationResult",
    "SourceOrganSpec",
    "Task",
    "TaskParameter",
    "TraceSeries",
    "simulate_snapshot",
]

__version__ = "0.1.0"
