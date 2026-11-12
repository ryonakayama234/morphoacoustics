"""Frozen BODYMAP-B2-PREREG/1 constants. Research-only; no study entry point."""
from __future__ import annotations

import math

PROTOCOL = "BODYMAP-B2-PREREG/1"
PREREG_CONTENT_SHA256 = "9a022469264b4789c2d677d163470c4f7f393451635b264920463e6d70d3e41e"
PREREG_COMMIT = "2f7d9546cc888ca43e54a20cf04d3708c95c416f"
PLAN_COMMIT = "f63b4bf933df4e351f25a8565c463f2f3e81b29f"
PLAN_CONTENT_SHA256 = "1705c3bfd63b2d9ffa78f39a0ecba155ed9055e3cba989a376122d3b94ae64b8"
LAW = "b2.lrf.circular-rigid-isothermal/1"
OBSERVATION = "b2.direct-observables/1"
RHO, C, MU, KAPPA, CP, GAMMA, T_REF = 1.21, 343.0, 1.81e-5, 0.0257, 1005.0, 1.40, 293.15
LENGTH_M, R_PROXY_M = 0.010, 0.20
SAMPLE_RATE, SAMPLES = 48000, 24000
FREQUENCIES_HZ = tuple(range(100, 801, 2))
LAMBDAS = (0.0, 1e-6, 0.5, 1.0)
M0_DIGEST = "sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de"
M0_DIAMETERS_MM = (12, 12, 26, 16, 12, 14, 20, 26, 30, 34, 38, 34, 34, 30, 28, 32)
SCIENTIFIC_CASES_AUTHORIZED = False
OLD_UNIFORM_ATTENUATION_NP_M = 0.0


class Refusal(ValueError):
    def __init__(self, code: str, reason: str):
        self.code = code
        super().__init__(reason)


def require(condition: bool, code: str, reason: str) -> None:
    if not condition:
        raise Refusal(code, reason)


def validate_lambda(value: object) -> float:
    require(type(value) in (float, int) and math.isfinite(value) and 0.0 <= value <= 1.0,
            "INVALID_LOSS_PARAMETER", "loss factor must be a finite scalar in [0,1], not bool")
    require(float(value) in LAMBDAS, "INVALID_LOSS_PARAMETER",
            "only preregistered engineering lambdas are available")
    return float(value)


def validate_envelope(radii: tuple[float, ...], lengths: tuple[float, ...]) -> None:
    require(len(radii) == len(lengths) and len(radii) in (1, 16),
            "PHYSICAL_IDENTITY_MISMATCH", "expected one 160 mm or sixteen 10 mm sections")
    require(all(math.isfinite(a) and .006 <= a <= .019 for a in radii)
            and all(math.isfinite(l) and l > 0 for l in lengths),
            "OUT_OF_ENVELOPE", "invalid circular tube radii or lengths")
    require(len(radii) == 16 and all(l == LENGTH_M for l in lengths)
            or len(radii) == 1 and lengths == (.160,),
            "OUT_OF_ENVELOPE", "unsupported section lengths")
    require(all(math.isfinite(v) and v > 0 for v in (RHO, C, MU, KAPPA, CP, T_REF))
            and GAMMA > 1 and OLD_UNIFORM_ATTENUATION_NP_M == 0,
            "MODEL_IDENTITY_MISMATCH", "frozen nominal model drift")
    for f in FREQUENCIES_HZ:
        w = 2 * math.pi * f
        kv = w / C
        dv = math.sqrt(2 * MU / (RHO * w))
        dt = math.sqrt(2 * KAPPA / (RHO * CP * w))
        require(kv * max(radii) <= .30 and kv * dv <= .01 and kv * dt <= .01
                and max(dv, dt) / min(lengths) <= .05,
                "OUT_OF_ENVELOPE", "FZ-M1 preflight dimensionless bound failed")
