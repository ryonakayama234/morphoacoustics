"""Frozen FZ-M2 z/y LRF with SciPy scaled complex Bessel functions."""
from __future__ import annotations

import cmath
import math
from scipy.special import jve
from ..prereg_binding import RHO, C, MU, KAPPA, CP, GAMMA, Refusal, require, validate_lambda


def _f(q: complex) -> complex:
    # Both J1 and J0 carry the same exp(abs(Im(q))) scaling.
    j0, j1 = jve(0, q), jve(1, q)
    require(abs(j0) > 1e-280 and
            all(math.isfinite(v) for v in (j0.real, j0.imag, j1.real, j1.imag)),
            "NUMERICALLY_UNRESOLVED", "nonfinite or near-pole scaled Bessel")
    v = 2.0 * j1 / (q * j0)
    require(math.isfinite(v.real) and math.isfinite(v.imag),
            "NUMERICALLY_UNRESOLVED", "nonfinite Bessel ratio")
    return complex(v)


def coefficients(frequency_hz: float, radius_m: float, loss: float) -> tuple[complex, complex, complex, complex, complex, complex]:
    loss = validate_lambda(loss)
    require(math.isfinite(frequency_hz) and 100 <= frequency_hz <= 800
            and math.isfinite(radius_m) and .006 <= radius_m <= .019,
            "OUT_OF_ENVELOPE", "invalid frequency/radius")
    w = 2 * math.pi * frequency_hz
    area = math.pi * radius_m ** 2
    z0 = 1j * w * RHO / area
    y0 = 1j * w * area / (RHO * C * C)
    if loss == 0.0:
        z, y = z0, y0
    else:
        qv = radius_m * cmath.sqrt(-1j * w * RHO / MU)
        qt = radius_m * cmath.sqrt(-1j * w * RHO * CP / KAPPA)
        fv, ft = _f(qv), _f(qt)
        require(abs(1 - fv) > 1e-14, "NUMERICALLY_UNRESOLVED", "viscous pole")
        z1 = 1j * w * (RHO / (1 - fv)) / area
        y1 = 1j * w * area * (1 + (GAMMA - 1) * ft) / (RHO * C * C)
        z, y = z0 + loss * (z1 - z0), y0 + loss * (y1 - y0)
    gamma = cmath.sqrt(z * y)
    if gamma.real < 0 or (abs(gamma.real) < 1e-13 and gamma.imag < 0):
        gamma = -gamma
    require(all(math.isfinite(v) for v in (gamma.real, gamma.imag, z.real, z.imag, y.real, y.imag))
            and abs(gamma) > 0, "NUMERICALLY_UNRESOLVED", "invalid Gamma branch")
    zc = z / gamma
    require(zc.real > 0 and math.isfinite(zc.real) and math.isfinite(zc.imag),
            "NUMERICALLY_UNRESOLVED", "ambiguous characteristic impedance")
    return z, y, gamma, zc, z0, y0
