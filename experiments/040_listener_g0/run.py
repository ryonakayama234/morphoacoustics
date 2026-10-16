"""EL-G0: auditable free-field two-probe acoustic receiver null.

Standalone research experiment. This does not implement ListenerSpec or HRTFs.
SI units everywhere. Complex phasors use exp(-i omega t).
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path


MODEL_ID = "EL-G0-ideal-monopole-3d-v0"
PREREG_ID = "EL-G0-PREREG"
LEFT = (-0.09, 0.0, 0.0)
RIGHT = (+0.09, 0.0, 0.0)
SOURCES = {
    "center": (0.0, 0.20, 0.0),
    "offset": (0.12, 0.20, 0.0),
    "mirror": (-0.12, 0.20, 0.0),
}


def xyz(value: tuple[float, float, float]) -> tuple[float, float, float]:
    if len(value) != 3 or not all(math.isfinite(float(v)) for v in value):
        raise ValueError("INVALID: expected three finite SI coordinates")
    return tuple(float(v) for v in value)


def point_pressure(
    source: tuple[float, float, float],
    receiver: tuple[float, float, float],
    *,
    frequency_hz: float = 1000.0,
    sound_speed_m_s: float = 343.0,
    density_kg_m3: float = 1.2,
    volume_velocity_m3_s: float = 1e-6,
) -> dict:
    """Free-space monopole pressure p = i*w*rho*Q*exp(-i*k*r)/(4*pi*r).

    p uses Pa; Q is volume velocity in m^3/s. No boundaries or scattering.
    """
    s, rec = xyz(source), xyz(receiver)
    scalars = (frequency_hz, sound_speed_m_s, density_kg_m3, volume_velocity_m3_s)
    if not all(math.isfinite(float(a)) for a in scalars):
        raise ValueError("INVALID: non-finite scalar")
    if any(a <= 0 for a in (frequency_hz, sound_speed_m_s, density_kg_m3)):
        raise ValueError("INVALID: frequency, speed and density must be positive")
    radius = math.dist(s, rec)
    if radius == 0.0:
        raise ValueError("INVALID: singular source/receiver coincidence")
    w = 2 * math.pi * frequency_hz
    pressure = (1j * w * density_kg_m3 * volume_velocity_m3_s
                / (4 * math.pi * radius)
                * cmath.exp(-1j * w * radius / sound_speed_m_s))
    return {
        "position_m": list(rec),
        "distance_m": radius,
        "travel_time_s": radius / sound_speed_m_s,
        "complex_pressure_pa": {"real": pressure.real, "imag": pressure.imag},
        "pressure_magnitude_pa": abs(pressure),
    }


def observe(source: tuple[float, float, float]) -> dict:
    left = point_pressure(source, LEFT)
    right = point_pressure(source, RIGHT)
    return {
        "source_position_m": list(source),
        "left_probe": left,
        "right_probe": right,
        "right_minus_left_delay_s": right["travel_time_s"] - left["travel_time_s"],
        "right_over_left_level_db": 20 * math.log10(
            right["pressure_magnitude_pa"] / left["pressure_magnitude_pa"]
        ),
    }


def generate_report() -> dict:
    cases = {name: observe(source) for name, source in SOURCES.items()}
    ctr, off, mir = cases["center"], cases["offset"], cases["mirror"]
    oracle_delay_ms = -0.2558673931149656
    oracle_level_db = 3.1307268779057047
    checks = {
        "center_delay_null": abs(ctr["right_minus_left_delay_s"]) < 1e-12,
        "center_level_null": abs(ctr["right_over_left_level_db"]) < 1e-12,
        "offset_left_distance": abs(off["left_probe"]["distance_m"] - 0.29) < 1e-12,
        "offset_right_distance": abs(off["right_probe"]["distance_m"] - math.sqrt(0.0409)) < 1e-12,
        "wolfram_delay_ms": abs(off["right_minus_left_delay_s"] * 1000 - oracle_delay_ms) < 1e-9,
        "wolfram_level_db": abs(off["right_over_left_level_db"] - oracle_level_db) < 1e-9,
        "mirror_delay": abs(off["right_minus_left_delay_s"] + mir["right_minus_left_delay_s"]) < 1e-12,
        "mirror_level": abs(off["right_over_left_level_db"] + mir["right_over_left_level_db"]) < 1e-12,
        "finite_pressures": all(
            math.isfinite(item[f"{side}_probe"]["pressure_magnitude_pa"])
            for item in cases.values() for side in ("left", "right")
        ),
    }
    source_digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {
        "schema_version": "el-g0-result-v0",
        "hypothesis_id": "EL-H02/NF-0",
        "model_id": MODEL_ID,
        "preregistration_id": PREREG_ID,
        "source_sha256": source_digest,
        "physics": {
            "sound_speed_m_s": 343.0,
            "air_density_kg_m3": 1.2,
            "frequency_hz": 1000.0,
            "volume_velocity_m3_s": 1e-6,
            "phasor_convention": "exp(-i omega t)",
            "environment": "unbounded linear 3D free field",
        },
        "receiver_type": "ideal_pressure_point_probe_NOT_anatomical_ear",
        "observations": cases,
        "gates": checks,
        "decision": ("PROVISIONAL_ANALYTIC_BASELINE" if all(checks.values()) else "FAILED"),
        "claim_limit": "No pinna, head, canal, contact, HRTF, cartilage or ASMR validity.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="Fresh result JSON path")
    args = parser.parse_args()
    report = generate_report()
    serialized = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            parser.error("refusing to overwrite existing evidence")
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0 if report["decision"] == "PROVISIONAL_ANALYTIC_BASELINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
