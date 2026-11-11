"""EL-RP1 Gate B: conditional synthetic source/load connection via existing Core tube.

Requires Gate A eligibility. NEVER accepts pressure-only measured HRTF,
calibrated real-ear data, unqualified observation or production ASMR output.
Pre-reg: D0 a33c8c6. Independent wave oracle frozen B0 624ce156 before this code.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isclose, isfinite
from numbers import Real
from sys import float_info

from morphoacoustics.acoustics.uniform_tube import UniformTube
from qualifier import ResearchRefusal, SyntheticReferencePort, qualify


@dataclass(frozen=True, slots=True)
class PortObservation:
    p0_pa: complex
    u0_m3_s: complex
    pL_pa: complex
    uL_m3_s: complex
    zc_pa_s_m3: float
    power_source_w: float
    power_entrance_w: float
    power_terminal_w: float
    power_source_resistor_loss_w: float
    residual_source_boundary_pa: complex
    residual_terminal_boundary_pa: complex
    residual_matrix_pressure_pa: complex
    residual_matrix_flow_m3_s: complex
    residual_source_energy_w: float
    residual_tube_energy_w: float


def _complete_transfer(port: SyntheticReferencePort,
                       segment_lengths_m: tuple[float, ...] | None):
    lengths = (port.length_m,) if segment_lengths_m is None else segment_lengths_m
    if not isinstance(lengths, tuple) or len(lengths) not in (1, 2):
        raise ResearchRefusal("UNSUPPORTED", "segment_lengths_m",
                              "only one tube or two explicit serial segments")
    for length in lengths:
        if (isinstance(length, bool) or not isinstance(length, Real)
                or not isfinite(float(length)) or length <= 0):
            raise ResearchRefusal("INVALID", "segment_lengths_m",
                                  "segments must be positive finite lengths")
    if not isclose(sum(lengths), port.length_m, rel_tol=1e-12, abs_tol=1e-12):
        raise ResearchRefusal("INVALID", "segment_lengths_m",
                              "split lengths must equal declared physical tube length")
    # Transfer law remains OWNED by existing Core. The order is physical upstream
    # to downstream, T(total)=T(segment_1)@T(segment_2).
    matrices = [
        UniformTube(length_m=float(L), area_m2=port.area_m2,
                    air_density_kg_m3=port.air_density_kg_m3,
                    sound_speed_m_s=port.sound_speed_m_s)
        .transfer_matrix(port.frequency_hz) for L in lengths
    ]
    matrix = matrices[0]
    for additional in matrices[1:]:
        matrix = matrix @ additional
    return matrix


def solve_port(evidence: object, *,
               segment_lengths_m: tuple[float, ...] | None = None) -> PortObservation:
    decision = qualify(evidence, "PREDICT_CHANGED_LOAD")
    if not decision.accepted:
        raise ResearchRefusal(decision.code or "INVALID", decision.field or "evidence",
                              decision.reason or "qualification failed")
    if not isinstance(evidence, SyntheticReferencePort):
        raise ResearchRefusal("UNSUPPORTED", "evidence", "Gate B synthetic port only")
    port = evidence
    matrix = _complete_transfer(port, segment_lengths_m)
    a, b, c, d = (complex(matrix[0, 0]), complex(matrix[0, 1]),
                  complex(matrix[1, 0]), complex(matrix[1, 1]))
    ps, zs, zt = (complex(port.source_pressure_pa),
                  port.source_impedance_pa_s_m3, port.terminal_impedance_pa_s_m3)
    den = (a + zs*c)*zt + b + zs*d
    den_scale = max(1.0, abs(a*zt), abs(b), abs(zs*c*zt), abs(zs*d))
    if not (isfinite(den.real) and isfinite(den.imag)) or abs(den) <= 64*float_info.epsilon*den_scale:
        raise ResearchRefusal("NUMERICALLY_UNRESOLVED", "coupling_denominator",
                              "ill-conditioned or nonfinite boundary solve")
    uL = ps/den
    pL = zt*uL
    p0 = (a*zt+b)*uL
    u0 = (c*zt+d)*uL
    if not all(isfinite(z.real) and isfinite(z.imag) for z in (p0,u0,pL,uL)):
        raise ResearchRefusal("NUMERICALLY_UNRESOLVED", "ports", "nonfinite end-port prediction")
    psource = (ps*u0.conjugate()).real/2
    pentrance = (p0*u0.conjugate()).real/2
    pterminal = (pL*uL.conjugate()).real/2
    ploss = zs*abs(u0)**2/2
    if not all(isfinite(v) for v in (psource,pentrance,pterminal,ploss)):
        raise ResearchRefusal("NUMERICALLY_UNRESOLVED", "powers", "nonfinite power ledger")
    return PortObservation(
        p0_pa=p0, u0_m3_s=u0, pL_pa=pL, uL_m3_s=uL,
        zc_pa_s_m3=port.air_density_kg_m3*port.sound_speed_m_s/port.area_m2,
        power_source_w=psource, power_entrance_w=pentrance,
        power_terminal_w=pterminal, power_source_resistor_loss_w=ploss,
        residual_source_boundary_pa=ps-p0-zs*u0,
        residual_terminal_boundary_pa=pL-zt*uL,
        residual_matrix_pressure_pa=p0-a*pL-b*uL,
        residual_matrix_flow_m3_s=u0-c*pL-d*uL,
        residual_source_energy_w=psource-pentrance-ploss,
        residual_tube_energy_w=pentrance-pterminal,
    )
