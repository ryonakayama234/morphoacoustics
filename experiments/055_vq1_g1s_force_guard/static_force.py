"""VQ-1 G1-S: signed STATIC force algebra, never a qualified laryngeal force.

Input pressure drop D = p0 - p_wall is not wall traction by itself.
No source digitization, pressure model, dynamic coupling or audio lives here.
"""
from dataclasses import dataclass
import math
from typing import Sequence


class ScientificHold(ValueError):
    """An input is insufficient for this bounded research calculation."""


@dataclass(frozen=True)
class PressureDrop:
    tap_id: int
    wall: str
    drop_pa: float
    uncertainty_pa: float
    source_kind: str


@dataclass(frozen=True)
class SurfacePatch:
    tap_id: int
    wall: str
    area_m2: float
    projection: float  # dot(fluid-outward normal, dimensionless tissue mode)


@dataclass(frozen=True)
class PressureReference:
    tracheal_gauge_pa: float
    exterior_gauge_pa: float
    tracheal_uncertainty_pa: float
    exterior_uncertainty_pa: float


@dataclass(frozen=True)
class StaticForceInterval:
    force_n: float
    conservative_half_width_n: float
    status: str = "ALGEBRA_ONLY_NOT_SOURCE_OR_FORCE_VALIDATED"


def _finite_real(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ScientificHold(f"{label}: finite real required")
    if not math.isfinite(value):
        raise ScientificHold(f"{label}: nonfinite")
    return float(value)


def _nonnegative(value: float, label: str) -> float:
    x = _finite_real(value, label)
    if x < 0:
        raise ScientificHold(f"{label}: negative")
    return x


def _key(tap_id: int, wall: str) -> tuple[int, str]:
    if isinstance(tap_id, bool) or not isinstance(tap_id, int) or tap_id < 0:
        raise ScientificHold("tap_id must be a nonnegative integer")
    if wall not in ("FW", "NFW"):
        raise ScientificHold("wall side must be explicit FW or NFW")
    return (tap_id, wall)


def static_force(
    pressure_drops: Sequence[PressureDrop],
    surface_patches: Sequence[SurfacePatch],
    reference: PressureReference | None,
    *,
    static_only: bool = True,
) -> StaticForceInterval:
    """Return signed force [N] and a conservative *pressure-only* interval.

    This is a synthetic/conditional algebra study. Geometry, mode projection
    and measurement identity must be independently established later.
    """
    if static_only is not True:
        raise ScientificHold("G1-D moving-wall force/work is not authorized")
    if reference is None:
        raise ScientificHold("missing independently established common-gauge reference")
    if not pressure_drops or not surface_patches:
        raise ScientificHold("missing wall pressure or wetted-surface geometry")

    p0 = _finite_real(reference.tracheal_gauge_pa, "tracheal_gauge")
    pext = _finite_real(reference.exterior_gauge_pa, "exterior_gauge")
    up0 = _nonnegative(reference.tracheal_uncertainty_pa, "tracheal_uncertainty")
    ue = _nonnegative(reference.exterior_uncertainty_pa, "exterior_uncertainty")

    by_key: dict[tuple[int, str], tuple[float, float]] = {}
    for sample in pressure_drops:
        key = _key(sample.tap_id, sample.wall)
        if key in by_key:
            raise ScientificHold("duplicate pressure sample")
        if sample.source_kind not in ("synthetic_control", "observed_marker"):
            raise ScientificHold("not an observed marker or explicit synthetic control")
        drop = _finite_real(sample.drop_pa, "pressure_drop")
        unc = _nonnegative(sample.uncertainty_pa, "pressure_drop_uncertainty")
        by_key[key] = (drop, unc)

    force = 0.0
    independent_drop_bound = 0.0
    total_signed_weight = 0.0
    used: set[tuple[int, str]] = set()
    for patch in surface_patches:
        key = _key(patch.tap_id, patch.wall)
        if key in used:
            raise ScientificHold("duplicate surface patch key; no hidden tap interpolation")
        used.add(key)
        if key not in by_key:
            raise ScientificHold("pressure sample absent or wall side mismatched")
        area = _finite_real(patch.area_m2, "surface_area")
        if area <= 0:
            raise ScientificHold("wetted area must be positive")
        proj = _finite_real(patch.projection, "signed_mode_projection")
        if abs(proj) > 1:
            raise ScientificHold("mode projection outside [-1,1]")
        drop, unc = by_key[key]
        weight = area * proj
        force += (p0 - drop - pext) * weight
        independent_drop_bound += abs(weight) * unc
        total_signed_weight += weight

    if used != set(by_key):
        raise ScientificHold("unused pressure samples; explicit complete binding required")
    # p0 and p_ext are shared among all taps; do NOT independently RSS them.
    bound = (abs(total_signed_weight) * (up0 + ue)
             + independent_drop_bound)
    if not math.isfinite(force) or not math.isfinite(bound):
        raise ScientificHold("force calculation overflow")
    return StaticForceInterval(force, bound)
