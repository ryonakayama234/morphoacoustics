"""Research-only symbolic motor-task graph. NOT a physical execution API."""
from .model import (
    CouplingConstraint, Diagnostic, Event, EventAnchor, MotorTask,
    PronunciationUnit, ReportStatus, SymbolicPlan, TaskAssociation,
    TimingReport, ValidationReport,
)
from .validation import canonical_plan_json, plan_digest, resolve_timing, validate_plan

__all__ = [
    "CouplingConstraint", "Diagnostic", "Event", "EventAnchor", "MotorTask",
    "PronunciationUnit", "ReportStatus", "SymbolicPlan", "TaskAssociation",
    "TimingReport", "ValidationReport", "canonical_plan_json", "plan_digest",
    "resolve_timing", "validate_plan",
]
