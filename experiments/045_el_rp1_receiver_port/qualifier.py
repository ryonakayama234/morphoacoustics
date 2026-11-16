"""EL-RP1 Gate A — research-only evidence classification and identifiability refusal.

D0 preregistered at a33c8c68879f732cd830b2caab6b8024b5322297.
No physical HRTF/ear solver, source impedance inversion, or product ASMR API.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Literal

Refusal = Literal["INVALID", "UNSUPPORTED", "UNIDENTIFIABLE",
                  "NUMERICALLY_UNRESOLVED", "RIGHTS_REVIEW_REQUIRED"]
Rights = Literal["NOT_ASSESSED", "RESEARCH_REVIEW", "REUSE_CLEARED", "BLOCKED"]


class ResearchRefusal(ValueError):
    def __init__(self, category: Refusal, field: str, reason: str):
        super().__init__(f"{category} {field}: {reason}")
        self.category, self.field, self.reason = category, field, reason


@dataclass(frozen=True, slots=True)
class MeasuredPressureTransfer:
    source_sha256: str
    receiver_reference_plane: str = "UNKNOWN"
    source_reference_plane: str = "UNKNOWN"
    pressure_kind: str = "STORED_CHANNEL_RATIO"
    terminal_condition: str = "FIXED_UNKNOWN"
    rights_status: Rights = "NOT_ASSESSED"


@dataclass(frozen=True, slots=True)
class SyntheticReferencePort:
    source_pressure_pa: complex
    source_impedance_pa_s_m3: float
    terminal_impedance_pa_s_m3: float
    area_m2: float
    length_m: float
    frequency_hz: float
    air_density_kg_m3: float = 1.21
    sound_speed_m_s: float = 343.
    source_reference_plane: str = "SOURCE_EQUIVALENT"
    receiver_input_plane: str = "CANAL_ENTRANCE"
    receiver_output_plane: str = "TERMINAL_SIDE"
    pressure_kind: str = "SOURCE_EQUIVALENT"
    phasor_convention: str = "PEAK_EXP_PLUS_IWT"
    flow_direction: str = "ENTRANCE_TO_TERMINAL"
    impedance_kind: str = "ABSOLUTE_PA_S_M3"
    model_dimension: str = "1D"
    rights_status: Rights = "NOT_ASSESSED"


@dataclass(frozen=True, slots=True)
class CalibratedAcousticPort:
    calibration_sha256: str
    receiver_reference_plane: str
    source_reference_plane: str
    rights_status: Rights = "NOT_ASSESSED"


@dataclass(frozen=True, slots=True)
class UnqualifiedObservation:
    reason: str
    rights_status: Rights = "NOT_ASSESSED"


@dataclass(frozen=True, slots=True)
class Decision:
    accepted: bool
    status: str
    code: Refusal | None = None
    field: str | None = None
    reason: str | None = None


def _real(value: object, name: str, *, positive=False, nonnegative=False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ResearchRefusal("INVALID", name, "finite real scalar required")
    try:
        x = float(value)
    except (ValueError, OverflowError):
        raise ResearchRefusal("INVALID", name, "unrepresentable scalar") from None
    if not isfinite(x) or (positive and x <= 0) or (nonnegative and x < 0):
        raise ResearchRefusal("INVALID", name, "nonfinite or out of sign bounds")
    return x


def _sha(value: object, field: str) -> None:
    if (not isinstance(value, str) or len(value) != 64 or
            any(c not in "0123456789abcdef" for c in value)):
        raise ResearchRefusal("INVALID", field, "lowercase SHA256 required")


def _validate(e: object) -> None:
    if type(e) not in (MeasuredPressureTransfer, SyntheticReferencePort,
                       CalibratedAcousticPort, UnqualifiedObservation):
        raise ResearchRefusal("INVALID", "evidence", "unknown union variant")
    if e.rights_status not in ("NOT_ASSESSED", "RESEARCH_REVIEW", "REUSE_CLEARED", "BLOCKED"):
        raise ResearchRefusal("INVALID", "rights_status", "unknown rights classification")
    if isinstance(e, MeasuredPressureTransfer):
        _sha(e.source_sha256, "source_sha256")
        if e.pressure_kind != "STORED_CHANNEL_RATIO":
            raise ResearchRefusal("UNSUPPORTED", "pressure_kind",
                                  "measured pressure ratio is not an incident/source pressure")
        for name in ("receiver_reference_plane", "source_reference_plane", "terminal_condition"):
            value = getattr(e, name)
            if not isinstance(value, str) or not value:
                raise ResearchRefusal("INVALID", name, "missing measurement tag")
    elif isinstance(e, CalibratedAcousticPort):
        _sha(e.calibration_sha256, "calibration_sha256")
        for name in ("receiver_reference_plane", "source_reference_plane"):
            value = getattr(e, name)
            if not isinstance(value, str) or value in ("", "UNKNOWN"):
                raise ResearchRefusal("INVALID", name, "explicit calibrated plane required")
    elif isinstance(e, UnqualifiedObservation):
        if not isinstance(e.reason, str) or not e.reason.strip():
            raise ResearchRefusal("INVALID", "reason", "explain missing qualification")
    else:
        assert isinstance(e, SyntheticReferencePort)
        pressure = e.source_pressure_pa
        if isinstance(pressure, bool) or not isinstance(pressure, (Real, complex)):
            raise ResearchRefusal("INVALID", "source_pressure_pa", "complex peak pressure required")
        if not (isfinite(complex(pressure).real) and isfinite(complex(pressure).imag)):
            raise ResearchRefusal("INVALID", "source_pressure_pa", "nonfinite pressure")
        for name, predicate in (
            ("source_impedance_pa_s_m3", "nonnegative"),
            ("terminal_impedance_pa_s_m3", "positive"),
            ("area_m2", "positive"), ("length_m", "positive"),
            ("frequency_hz", "positive"), ("air_density_kg_m3", "positive"),
            ("sound_speed_m_s", "positive"),
        ):
            _real(getattr(e, name), name, positive=predicate == "positive",
                  nonnegative=predicate == "nonnegative")
        for name, expected in (
            ("source_reference_plane", "SOURCE_EQUIVALENT"),
            ("receiver_input_plane", "CANAL_ENTRANCE"),
            ("receiver_output_plane", "TERMINAL_SIDE"),
            ("pressure_kind", "SOURCE_EQUIVALENT"),
            ("phasor_convention", "PEAK_EXP_PLUS_IWT"),
            ("flow_direction", "ENTRANCE_TO_TERMINAL"),
            ("impedance_kind", "ABSOLUTE_PA_S_M3"),
        ):
            if getattr(e, name) != expected:
                raise ResearchRefusal("UNSUPPORTED", name, f"requires {expected}")
        if e.model_dimension != "1D":
            raise ResearchRefusal("UNSUPPORTED", "model_dimension", "1D only")
        if not (0.01 <= e.length_m <= 0.05 and 1e-5 <= e.area_m2 <= 1e-4
                and 0 < e.frequency_hz <= 8000):
            raise ResearchRefusal("UNSUPPORTED", "synthetic_domain", "outside R2 bounded envelope")
        scale = e.air_density_kg_m3 * e.sound_speed_m_s ** 2
        if not isfinite(scale) or scale <= 0:
            raise ResearchRefusal("NUMERICALLY_UNRESOLVED", "air", "nonfinite pressure scale")
        if abs(complex(pressure))/scale > 1e-3:
            raise ResearchRefusal("UNSUPPORTED", "source_pressure_pa", "outside small signal bound")


def qualify(evidence: object, operation: str,
            *, requested_input_plane: str | None = None) -> Decision:
    """Eligibility ONLY; no data synthesis, prediction or inference of Zs."""
    try:
        _validate(evidence)
        if operation not in ("INSPECT_METADATA", "PREDICT_CHANGED_LOAD",
                             "REPRODUCE_MEASURED_CHANNEL", "EXPORT_OR_DISTRIBUTE"):
            raise ResearchRefusal("INVALID", "operation", "unknown operation")
        if operation == "INSPECT_METADATA":
            return Decision(True, "INSPECTABLE_METADATA")
        if operation == "EXPORT_OR_DISTRIBUTE":
            if evidence.rights_status != "REUSE_CLEARED":
                raise ResearchRefusal("RIGHTS_REVIEW_REQUIRED", "rights_status",
                                      "redistribution not qualified")
            raise ResearchRefusal("UNSUPPORTED", "operation", "no distribution runtime")
        if operation == "REPRODUCE_MEASURED_CHANNEL":
            raise ResearchRefusal("UNSUPPORTED", "operation", "no reproduction runtime")
        if isinstance(evidence, MeasuredPressureTransfer):
            raise ResearchRefusal("UNIDENTIFIABLE", "source_impedance_pa_s_m3",
                                  "fixed-load pressure only lacks source impedance and flow")
        if isinstance(evidence, UnqualifiedObservation):
            raise ResearchRefusal("UNIDENTIFIABLE", "evidence", "unqualified observation")
        if isinstance(evidence, CalibratedAcousticPort):
            raise ResearchRefusal("UNSUPPORTED", "evidence", "Gate C not authorized")
        if requested_input_plane is not None and requested_input_plane != evidence.receiver_input_plane:
            raise ResearchRefusal("INVALID", "requested_input_plane", "port plane mismatch")
        return Decision(True, "SYNTHETIC_GATE_B_ELIGIBLE")
    except ResearchRefusal as exc:
        return Decision(False, "REFUSED", exc.category, exc.field, exc.reason)


def normalized_one_port_pressure(ps: float, zs: float, zl: float) -> float:
    """E0 dimensionless analytic toy ONLY; NOT a measured HRTF port solver."""
    a = _real(ps, "source_pressure")
    b = _real(zs, "source_impedance", nonnegative=True)
    c = _real(zl, "load_impedance", positive=True)
    output = a * (c / (b + c))
    if not isfinite(output):
        raise ResearchRefusal("NUMERICALLY_UNRESOLVED", "toy_pressure", "nonfinite result")
    return output
