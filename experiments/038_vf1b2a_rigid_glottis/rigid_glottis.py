"""VF-1B2a fixed-wall glottal-flow *proxy*; strictly NOT an FSI/phonation solver.

This deliberately ad-hoc, incompressible, quasi-steady Bernoulli core closure
is restricted to rigid, one-dimensional symmetric channels and forward drive.
Empirical 1.2*Amin separation area is predeclared, not a CFD prediction.
See docs/research/vf1b2a/{SYSTEM,DATA,EXPERIMENT}.md, committed BEFORE source.
"""
from __future__ import annotations
from dataclasses import dataclass
import math


class UnsupportedReverseFlow(ValueError):
    """Reverse flow requires independently declared reverse separation law."""


@dataclass(frozen=True)
class RigidGeometry:
    entry_area_m2: float
    exit_area_m2: float
    length_m: float = 0.006

    def __post_init__(self):
        for v in (self.entry_area_m2, self.exit_area_m2, self.length_m):
            if isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) or v<=0:
                raise ValueError("INVALID_POSITIVE_RIGID_GEOMETRY")

    def area(self,z_m:float)->float:
        if not math.isfinite(z_m) or z_m<0 or z_m>self.length_m:
            raise ValueError("INVALID_SAMPLE_POSITION")
        return (self.entry_area_m2
                +(self.exit_area_m2-self.entry_area_m2)*(z_m/self.length_m))


@dataclass(frozen=True)
class RigidObservation:
    z_m:float
    area_m2:float
    pressure_pa:float
    attached:bool
    flow_m3_s:float


@dataclass(frozen=True)
class RigidResult:
    input_geometry:RigidGeometry
    p_up_pa:float
    p_down_pa:float
    rho_kg_m3:float
    discharge_coefficient:float
    geometric_separation_z_m:float
    separation_area_m2:float
    separation_active:bool
    volume_flow_m3_s:float
    reservoir_power_w:float
    declared_farfield_dissipation_w:float
    fixed_wall_power_w:float
    bookkeeping_residual_w:float
    samples:tuple[RigidObservation,...]


def geometric_separation(geom:RigidGeometry)->tuple[float,float]:
    """Pre-registered linear geometry 1.2-throat area closure, forward only.

    For expanding channel, use the first position reaching 1.2*Amin,
    or the exit if ratio isn't reached. For equal/converging, exit.
    No flow present? Caller must explicitly mark separation_active=False.
    """
    a0,al=geom.entry_area_m2,geom.exit_area_m2
    if al<=a0:
        return geom.length_m,al
    target=1.2*a0
    if al<target:
        return geom.length_m,al
    z=geom.length_m*(target-a0)/(al-a0)
    return z,target


def solve(geom:RigidGeometry, *, p_up_pa:float=800., p_down_pa:float=0.,
          rho_kg_m3:float=1.21, discharge_coefficient:float=0.7,
          sample_count:int=41) -> RigidResult:
    for value in (p_up_pa,p_down_pa,rho_kg_m3,discharge_coefficient):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            raise ValueError("INVALID_NONFINITE_OR_BOOLEAN_FLOW_PARAMETER")
    if rho_kg_m3<=0:
        raise ValueError("INVALID_DENSITY")
    if discharge_coefficient<=0 or discharge_coefficient>1:
        raise ValueError("INVALID_DISCHARGE_COEFFICIENT")
    if type(sample_count) is not int or sample_count<3:
        raise ValueError("INVALID_SAMPLE_COUNT")
    dp=float(p_up_pa-p_down_pa)
    if dp<0:
        raise UnsupportedReverseFlow("UNSUPPORTED_REVERSE_FLOW_SEPARATION")
    zs,asep=geometric_separation(geom)
    q=discharge_coefficient*asep*math.sqrt(2*dp/rho_kg_m3)
    if not math.isfinite(q):
        raise ValueError("NONFINITE_FLOW")
    # Use the inviscid pressure profile until a toy separation point;
    # downstream is clamped to downstream reservoir (zero recovery).
    # This formulation does NOT resolve viscous dissipation locally.
    points=[]
    for i in range(sample_count):
        z=geom.length_m*i/(sample_count-1)
        a=geom.area(z)
        attached=z<=zs+1e-15
        p=(p_down_pa + 0.5*rho_kg_m3*q*q*(1/(asep*asep)-1/(a*a))
           if attached else p_down_pa)
        points.append(RigidObservation(z,a,p,attached,q))
    incoming=dp*q
    # Far-field jet/entry power loss is DECLARED, not independently solved.
    dissipation=dp*q
    return RigidResult(geom,float(p_up_pa),float(p_down_pa),float(rho_kg_m3),
                       float(discharge_coefficient),zs,asep,dp>0,q,
                       incoming,dissipation,0.,incoming-dissipation,
                       tuple(points))
