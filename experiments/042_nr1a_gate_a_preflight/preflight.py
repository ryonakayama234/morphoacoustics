"""NR-1a Gate A law-mutation preflight: exploratory design instrument only.

Independent 12-state dimensionless linear-system formulation, not the public
OG-4 implementation or a prospective confirmation of Experiment 041.
No Core imports; do not use these self-derived baseline states as a golden oracle.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

CASES = {"N": ("matched", "rigid_closed"),
         "O": ("matched", "matched"),
         "M": ("rigid_closed", "matched")}
FREQUENCIES = (80, 250, 400, 733, 997, 1200, 2000, 4000)
MUTANTS = ("tube_sign_A", "phasor_sign", "junction_particle_velocity",
           "wrong_B_terminal", "wrong_C_terminal")
LENGTHS_M = (.08, .09, .06)
AREAS_M2 = (.0003, .0003, .00015)
RHO_KG_M3 = 1.2
C_M_S = 343.0
P_REF_PA = 1.372
U_REF_M3_S = 1e-6
SOURCE_M3_S = 1e-6 + 4e-7j
PORTS = ("A.in", "A.out", "B.in", "B.out", "C.in", "C.out")


def system(case: str, frequency_hz: float, mutant: str | None = None):
    """Assemble dimensionless M x = b, x=(p/P_REF,U/U_REF) interleaved.

    p_in = cos(kL)p_out + i Z sin(kL) U_out;
    U_in = i sin(kL)/Z p_out + cos(kL) U_out.
    Ports flow positive in the A->J->(B,C) propagation direction.
    """
    if case not in CASES or (mutant is not None and mutant not in MUTANTS):
        raise ValueError("INVALID:UNKNOWN_CASE_OR_MUTANT")
    if not math.isfinite(frequency_hz) or frequency_hz <= 0:
        raise ValueError("INVALID:FREQUENCY")
    matrix = np.zeros((12, 12), dtype=np.complex128)
    rhs = np.zeros(12, dtype=np.complex128)
    impedance = [RHO_KG_M3 * C_M_S / a for a in AREAS_M2]
    for i, (length, z) in enumerate(zip(LENGTHS_M, impedance)):
        t = 2 * math.pi * frequency_hz * length / C_M_S
        phasor = -1 if mutant == "phasor_sign" else 1
        if mutant == "tube_sign_A" and i == 0:
            phasor *= -1
        row, col = 2*i, 4*i
        matrix[row, col] = 1
        matrix[row, col+2] = -math.cos(t)
        matrix[row, col+3] = -1j * phasor * math.sin(t) * z * U_REF_M3_S/P_REF_PA
        matrix[row+1, col+1] = 1
        matrix[row+1, col+2] = -1j * phasor * math.sin(t) * P_REF_PA/(z * U_REF_M3_S)
        matrix[row+1, col+3] = -math.cos(t)
    matrix[6, 2], matrix[6, 4] = 1, -1
    matrix[7, 2], matrix[7, 8] = 1, -1
    matrix[8, 3], matrix[8, 5] = 1, -1
    matrix[8, 9] = (-AREAS_M2[1] / AREAS_M2[2]
                     if mutant == "junction_particle_velocity" else -1)
    matrix[9, 1] = 1
    rhs[9] = SOURCE_M3_S/U_REF_M3_S
    load_b, load_c = CASES[case]
    if mutant == "wrong_B_terminal":
        load_b = "matched" if load_b == "rigid_closed" else "rigid_closed"
    if mutant == "wrong_C_terminal":
        load_c = "matched" if load_c == "rigid_closed" else "rigid_closed"
    for row, col, kind, z in ((10, 6, load_b, impedance[1]),
                              (11, 10, load_c, impedance[2])):
        if kind == "matched":
            matrix[row, col] = 1
            matrix[row, col+1] = -z * U_REF_M3_S/P_REF_PA
        else:
            matrix[row, col+1] = 1
    return matrix, rhs


def solve(case: str, frequency_hz: float, mutant: str | None = None):
    matrix, rhs = system(case, frequency_hz, mutant)
    cond = float(np.linalg.cond(matrix, 2))
    if not math.isfinite(cond) or cond >= 1e8:
        raise ArithmeticError("NUMERICALLY_UNRESOLVED:GLOBAL_CONDITION")
    value = np.linalg.solve(matrix, rhs)
    backward = float(np.linalg.norm(matrix @ value-rhs, np.inf) /
                     (np.linalg.norm(matrix, np.inf)*np.linalg.norm(value, np.inf)
                      + np.linalg.norm(rhs, np.inf)))
    if not math.isfinite(backward) or backward > 1e-11:
        raise ArithmeticError("NUMERICALLY_UNRESOLVED:GLOBAL_RESIDUAL")
    return value, cond, backward


def powers(state: np.ndarray):
    p = state[::2] * P_REF_PA
    u = state[1::2] * U_REF_M3_S
    return (0.5*np.real(p*np.conjugate(u))).tolist()


def run_preflight():
    """Measure candidate kill margins, NOT prospective confirmation/acceptance."""
    rows = []
    for case in CASES:
        for hz in FREQUENCIES:
            good, cond, backward = solve(case, hz)
            watts = powers(good)
            margins = {}
            for mutant in MUTANTS:
                bad, _, _ = solve(case, hz, mutant)
                margins[mutant] = float(np.max(np.abs(bad-good)))
            if not all(math.isfinite(x) for x in (*watts, *margins.values())):
                raise ArithmeticError("NUMERICALLY_UNRESOLVED:NONFINITE")
            rows.append({"case": case, "frequency_hz": hz,
                         "matrix_condition_2": cond,
                         "normalized_backward_error_inf": backward,
                         "input_power_w": watts[0],
                         "mouth_terminal_power_w": watts[3],
                         "nose_terminal_power_w": watts[5],
                         "power_residual_w": watts[0]-watts[3]-watts[5],
                         "mutant_max_scaled_state_deviation": margins})
    return {"schema": "nr1a.gate-a.exploratory-mutation-preflight.v0",
            "status": "EXPLORATORY_PRE_GATE_A_NOT_CONFIRMATORY",
            "normalization": {"p_ref_pa": P_REF_PA, "u_ref_m3_s": U_REF_M3_S},
            "ports": list(PORTS), "frequencies_hz": list(FREQUENCIES),
            "mutants": list(MUTANTS), "records": rows,
            "minimum_mutant_margins": {m: min(row["mutant_max_scaled_state_deviation"][m]
                                               for row in rows) for m in MUTANTS},
            "maximum_condition_2": max(row["matrix_condition_2"] for row in rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional exploratory JSON; NOT scientific evidence")
    args = parser.parse_args()
    report = run_preflight()
    raw = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(raw, encoding="utf-8")
    else:
        print(raw)


if __name__ == "__main__":
    main()
