"""Independent dissipation integral (reviewer-owned, FZ-V1).

D_int = integral over all sections of
  (1/2) Re(z) |U(x)|^2 + (1/2) Re(y) |p(x)|^2 dx,
evaluated with Gauss-Legendre rules whose nodes and weights are computed
here from Legendre-polynomial roots in arbitrary precision (no library
quadrature, no candidate helper). States inside a section are propagated
from the downstream boundary state with the oracle's own Gamma and Zc.
"""
from __future__ import annotations

from mpmath import mp, mpf, mpc, cosh, sinh


def gauss_legendre(n: int, dps: int = 60) -> tuple[list[mpf], list[mpf]]:
    """Nodes/weights on [-1, 1] via Newton iteration on P_n."""
    with mp.workdps(dps):
        nodes = [mpf(0)] * n
        weights = [mpf(0)] * n
        for i in range((n + 1) // 2):
            # initial guess from the standard cosine approximation
            x = mp.cos(mp.pi * (i + mpf("0.75")) / (n + mpf("0.5")))
            for _ in range(100):
                p_prev, p_cur = mpf(1), x
                for k in range(2, n + 1):
                    p_prev, p_cur = p_cur, \
                        ((2 * k - 1) * x * p_cur - (k - 1) * p_prev) / k
                dp = n * (x * p_cur - p_prev) / (x * x - 1)
                step = p_cur / dp
                x -= step
                if abs(step) < mpf(10) ** (-(dps - 5)):
                    break
            p_prev, p_cur = mpf(1), x
            for k in range(2, n + 1):
                p_prev, p_cur = p_cur, \
                    ((2 * k - 1) * x * p_cur - (k - 1) * p_prev) / k
            dp = n * (x * p_cur - p_prev) / (x * x - 1)
            wgt = 2 / ((1 - x * x) * dp * dp)
            nodes[i], nodes[n - 1 - i] = -x, x
            weights[i] = weights[n - 1 - i] = wgt
        return [+v for v in nodes], [+v for v in weights]


def dissipation(case_bin: dict, lengths: list[str], points: int) -> mpf:
    """D_int for one frequency bin of an evaluated oracle case."""
    nodes, weights = gauss_legendre(points)
    total = mpf(0)
    coeffs = case_bin["coeffs"]
    states = case_bin["states"]
    with mp.workdps(80):
        for sec, length_s in enumerate(lengths):
            length = mpf(length_s)
            z = coeffs[sec]["z"]
            y = coeffs[sec]["y"]
            gamma = coeffs[sec]["gamma"]
            zc = coeffs[sec]["zc"]
            p_down, u_down = states[sec + 1]
            subtotal = mpf(0)
            for node, weight in zip(nodes, weights):
                tau = length * (1 - (node + 1) / 2)  # distance downstream
                co = cosh(gamma * tau)
                si = sinh(gamma * tau)
                press = co * p_down + zc * si * u_down
                flow = si / zc * p_down + co * u_down
                dens = (mp.re(z) * abs(flow) ** 2
                        + mp.re(y) * abs(press) ** 2) / 2
                subtotal += weight * dens
            total += length * subtotal / 2
        return +total
