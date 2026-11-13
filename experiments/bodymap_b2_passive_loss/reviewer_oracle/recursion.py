"""High-precision LRF network evaluation (reviewer-owned, FZ-V1).

Independently derived from BODYMAP-B2-PREREG/1 FZ-M2: for each circular
section, z0 = j w rho / S and y0 = j w S / (rho c^2); the lossy pair uses
rho_e = rho / (1 - F(qv)) and the thermal factor (1 + (gamma-1) F(qt))
with q from the reviewer power series; lambda interpolates the *series z
and shunt y* coefficients. Sections compose as ABCD matrices from inlet
to outlet; the load is R = 0.05 rho c / S_last; the pressure observable
uses the frozen 0.20 m monopole proxy, never re-coupled as a load.

Working precision for the recursion is 80 digits; the F ratios enter at
their certified 400/450-digit values, so recursion rounding (~1e-75) is
far below every FZ-T1 tolerance.
"""
from __future__ import annotations

from mpmath import mp, mpf, mpc, sqrt, cosh, sinh, exp

from .series import f_ratio, f_ratio_bulk

RHO = mpf("1.21")
C = mpf("343")
MU = mpf("1.81e-5")
KAPPA = mpf("0.0257")
CP = mpf("1005")
GAMMA = mpf("1.40")
R_PROXY = mpf("0.20")
WORK_DPS = 80

_cache: dict[tuple[str, str, str], tuple[mpc, dict]] = {}


def _f(q: mpc, bulk: bool = False) -> tuple[mpc, dict]:
    key = (str(mp.re(q)), str(mp.im(q)), "B" if bulk else "F")
    if key not in _cache:
        if bulk:
            _cache[key] = (f_ratio_bulk(key[0], key[1]),
                           {"terms": -1, "agreement_400_450": "bulk"})
        else:
            _cache[key] = f_ratio(key[0], key[1])
    return _cache[key]


def section_coefficients(f_hz: int, radius: str, lam: str,
                         bulk: bool = False) -> dict:
    """z, y, Gamma, Zc (mpc) plus lossless z0, y0 for one section."""
    with mp.workdps(WORK_DPS):
        w = 2 * mp.pi * f_hz
        a = mpf(radius)
        area = mp.pi * a * a
        lam_v = mpf(lam)
        z0 = 1j * w * RHO / area
        y0 = 1j * w * area / (RHO * C * C)
        if lam_v == 0:
            z, y = z0, y0
            info = {"terms": 0, "agreement_400_450": "0"}
        else:
            qv = a * sqrt(-1j * w * RHO / MU)
            qt = a * sqrt(-1j * w * RHO * CP / KAPPA)
            fv, info_v = _f(qv, bulk)
            ft, info_t = _f(qt, bulk)
            z1 = 1j * w * (RHO / (1 - fv)) / area
            y1 = 1j * w * area * (1 + (GAMMA - 1) * ft) / (RHO * C * C)
            z = z0 + lam_v * (z1 - z0)
            y = y0 + lam_v * (y1 - y0)
            if bulk:
                info = {"terms": -1, "agreement_400_450": "bulk"}
            else:
                info = {"terms": max(info_v["terms"], info_t["terms"]),
                        "agreement_400_450": max(
                            info_v["agreement_400_450"],
                            info_t["agreement_400_450"], key=mpf)}
        gamma = sqrt(z * y)
        if mp.re(gamma) < 0 or (abs(mp.re(gamma)) < mpf("1e-30")
                                and mp.im(gamma) < 0):
            gamma = -gamma
        zc = z / gamma
        return {"z": +z, "y": +y, "gamma": +gamma, "zc": +zc,
                "z0": +z0, "y0": +y0, "series": info}


def evaluate_case(frequencies: list[int], radii: list[str],
                  lengths: list[str], lam: str,
                  bulk: bool = False) -> list[dict]:
    """Per-frequency HU, Zin, Hp, det(T), section coefficients, states.

    States are [p, U] at section boundaries, reconstructed downstream
    from the load with U_in = 1, exactly as the frozen definitions give.
    """
    out = []
    n = len(radii)
    for f in frequencies:
        with mp.workdps(WORK_DPS):
            w = 2 * mp.pi * f
            coeffs = [section_coefficients(f, radii[i], lam, bulk)
                      for i in range(n)]
            mats = []
            for i in range(n):
                g, zc = coeffs[i]["gamma"], coeffs[i]["zc"]
                co = cosh(g * mpf(lengths[i]))
                si = sinh(g * mpf(lengths[i]))
                mats.append(((co, zc * si), (si / zc, co)))
            # total = M_1 @ M_2 @ ... @ M_n (inlet to outlet)
            (a, b), (c, d) = ((mpc(1), mpc(0)), (mpc(0), mpc(1)))
            for (ma, mb), (mc, md) in mats:
                (a, b), (c, d) = (a * ma + b * mc, a * mb + b * md), \
                                 (c * ma + d * mc, c * mb + d * md)
            det = a * d - b * c
            s_last = mp.pi * mpf(radii[-1]) ** 2
            load_r = mpf("0.05") * RHO * C / s_last
            denom = c * load_r + d
            hu = 1 / denom
            zin = (a * load_r + b) / denom
            hp = (1j * w * RHO / (4 * mp.pi * R_PROXY)) \
                * exp(-1j * w * R_PROXY / C) * hu
            states = [None] * (n + 1)
            states[n] = (load_r * hu, hu)
            for i in reversed(range(n)):
                (ma, mb), (mc, md) = mats[i]
                p_d, u_d = states[i + 1]
                states[i] = (ma * p_d + mb * u_d, mc * p_d + md * u_d)
            out.append({"f": f, "HU": +hu, "Zin": +zin, "Hp": +hp,
                        "detT": +det, "load_R": +load_r,
                        "coeffs": coeffs, "states": states})
    return out
