"""Independent raw-observation audit: does not import solver or its energy functions."""
from __future__ import annotations
import math


def audit(trace: dict) -> dict:
    if trace.get("schema") != "vf1b2.c1r0.sealed.v0-research":
        raise ValueError("SCHEMA_MISMATCH")
    f = trace["fixture"]
    samples = trace["samples"]
    dt = trace["dt_s"]
    if len(samples) < 2 or not math.isfinite(dt) or dt <= 0:
        raise ValueError("INVALID_SAMPLES")
    length, depth, half_gap = (f[k] for k in ("L_g_m", "ell_m", "half_gap_m"))
    v0 = 2 * length * depth * half_gap
    g = length * depth
    p0 = f["P0_abs_Pa"]
    pext = f["Pext_abs_Pa"]
    gamma = f["gamma"]
    rho0 = f["rho0_kg_m3"]
    mass_expected = rho0 * v0
    energies = []
    dissipation = []
    max_p_rel = 0.0
    max_mass_abs = 0.0
    max_vol_rel = 0.0
    for i, s in enumerate(samples):
        if abs(s["t_s"] - dt * i) > max(1e-13, dt * 1e-8):
            raise ValueError("BAD_TIME_CLOCK")
        xl, xu = s["x_m"]
        vl, vu = s["v_m_s"]
        if not all(map(math.isfinite, (xl, xu, vl, vu, s["p_abs_Pa"], s["rho_kg_m3"], s["V_m3"]))):
            raise ValueError("NONFINITE")
        if min(half_gap + xl, half_gap + xu) <= 0:
            raise ValueError("UNSUPPORTED_CONTACT")
        volume = v0 + g * (xl + xu)
        if volume <= 0:
            raise ValueError("INVALID_VOLUME")
        p_expected = p0 * (v0 / volume) ** gamma
        max_p_rel = max(max_p_rel, abs(s["p_abs_Pa"] - p_expected) / p_expected)
        max_mass_abs = max(max_mass_abs, abs(s["rho_kg_m3"] * volume - mass_expected))
        max_vol_rel = max(max_vol_rel, abs(s["V_m3"] - volume) / volume)
        # Independent total relative energy: fluid internal, external pressure, kinetic and elastic.
        ratio_delta = (volume - v0) / v0
        gas_delta = (p0 * v0 / (gamma - 1)) * math.expm1((1 - gamma) * math.log1p(ratio_delta))
        external = pext * (volume - v0)
        kinetic = (f["m_L_kg"] * vl * vl + f["m_U_kg"] * vu * vu) / 2
        elastic = (f["k_L_N_m"] * xl * xl + f["k_U_N_m"] * xu * xu
                   + f["k_c_N_m"] * (xl - xu) ** 2) / 2
        energies.append(gas_delta + external + kinetic + elastic)
        dissipation.append(f["d_L_Ns_m"] * vl * vl + f["d_U_Ns_m"] * vu * vu)
    total_loss = sum(dt * (dissipation[i] + dissipation[i + 1]) / 2 for i in range(len(samples) - 1))
    residual = energies[-1] + total_loss - energies[0]
    if max_p_rel > 2e-12 or max_mass_abs > 1e-16 or max_vol_rel > 2e-12:
        raise ValueError("RAW_TRACE_CONTRADICTS_PHYSICS")
    if abs(residual) > 3e-10 or abs(residual) / max(abs(energies[0]), 1e-8) > 5e-4:
        raise ValueError("ENERGY_LEDGER_FAIL")
    return {"pressure_relative_error_max": max_p_rel, "gas_mass_error_max_kg": max_mass_abs,
            "volume_relative_error_max": max_vol_rel, "H_initial_J": energies[0],
            "H_final_J": energies[-1], "loss_trapezoid_J": total_loss,
            "energy_residual_J": residual,
            "energy_residual_relative": abs(residual) / max(abs(energies[0]), 1e-8)}
