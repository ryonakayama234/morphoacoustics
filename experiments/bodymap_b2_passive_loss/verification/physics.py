"""FZ-E1/T1 candidate diagnostics. Reviewer oracle must independently recalculate."""
from __future__ import annotations

import cmath
import math
import numpy as np
from ..prereg_binding import FREQUENCIES_HZ, Refusal, require


def independent_integral(result: dict, index: int, points: int) -> float:
    """Integrate section loss from internal states, never set D=Pin-Pout."""
    nodes, weights = np.polynomial.legendre.leggauss(points)
    total = 0.0
    for sec, length in enumerate(result["lengths_m"]):
        z = complex(result["z"][index, sec])
        y = complex(result["y"][index, sec])
        gamma = complex(result["gamma"][index, sec])
        zc = complex(result["zc"][index, sec])
        p_down, u_down = result["states"][index, sec + 1]
        for node, weight in zip(nodes, weights, strict=True):
            # coordinate x from inlet; propagate l-x from downstream section state
            tau = length * (1.0 - float(node + 1) / 2)
            co, si = cmath.cosh(gamma * tau), cmath.sinh(gamma * tau)
            press = co * p_down + zc * si * u_down
            flow = si / zc * p_down + co * u_down
            d = .5 * (z.real * abs(flow)**2 + y.real * abs(press)**2)
            total += length * .5 * float(weight) * d
    return total


def inspect(result: dict) -> dict:
    """Reject every bin failure with registered maxima; no clipping/point deletion."""
    require(result["frequency_hz"].tolist() == list(FREQUENCIES_HZ),
            "PHYSICAL_IDENTITY_MISMATCH", "frequency grid drift")
    zstar = result["Zstar"]
    zreal = np.real(result["z"] / zstar)
    yreal = np.real(result["y"] * zstar)
    require(np.isfinite(zreal).all() and np.isfinite(yreal).all()
            and float(np.min(zreal)) >= -1e-12 and float(np.min(yreal)) >= -1e-12,
            "NONPASSIVE_MODEL", "negative distributed loss")
    sigma = np.array([np.linalg.svd(s, compute_uv=False)[0] for s in result["S"]])
    require(np.isfinite(sigma).all() and float(np.max(sigma)) <= 1.0 + 1e-9,
            "NONPASSIVE_MODEL", "two-port scattering gain")
    zin_min = float(np.min(np.real(result["Zin"] / zstar)))
    require(zin_min >= -1e-10, "NONPASSIVE_MODEL", "negative input real impedance")
    det_max = float(np.max(abs(result["detT"] - 1.0)))
    require(det_max <= 1e-8, "NUMERICALLY_UNRESOLVED", "reciprocity det(T) drift")
    d16, d32, balance, convergence = [], [], [], []
    for i, _ in enumerate(FREQUENCIES_HZ):
        x = result["states"][i]
        uin, uout = x[0,1], x[-1,1]
        pin = .5 * float(np.real(x[0,0] * np.conjugate(uin)))
        pout = .5 * result["load_R"] * abs(uout)**2
        pow_star = .5 * zstar * abs(uin)**2
        require(pow_star > 0 and math.isfinite(pin) and math.isfinite(pout),
                "NUMERICALLY_UNRESOLVED", "invalid power normalization")
        i16 = independent_integral(result, i, 16)
        i32 = independent_integral(result, i, 32)
        d16.append(i16 / pow_star)
        d32.append(i32 / pow_star)
        balance.append(abs(pin - pout - i32) / pow_star)
        convergence.append(abs(i32 - i16) / pow_star)
    max_bal, max_conv, min_d = max(balance), max(convergence), min(d32)
    require(max_bal <= 1e-8 and max_conv <= 1e-10 and min_d >= -1e-10,
            "NONPASSIVE_MODEL", "power balance or quadrature mismatch")
    if result["lambda"] == 0.0:
        require(max(abs(v) for v in d32) <= 1e-10,
                "NONPASSIVE_MODEL", "lossless null has nonzero internal dissipation")
    return {"status":"CANDIDATE_PHYSICS_DIAGNOSTIC_ONLY",
            "max_s_scatter":float(max(sigma)), "min_zin_norm_real":zin_min,
            "min_z_norm_real":float(np.min(zreal)),
            "min_y_norm_real":float(np.min(yreal)), "max_det_error":det_max,
            "max_balance_normalized":max_bal,
            "max_gauss16_32_difference_normalized":max_conv,
            "min_d32_normalized":min_d, "d32_over_pstar":d32,
            "all_351_bins_checked":True}
