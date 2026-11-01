"""OD-1 independent model-matched 1D transfer and rest geometry observer.
No imports of candidate shape function or Core transfer verdicts.
Not an external validation of human voice or moving-wall FSI.
"""
from __future__ import annotations
import math
import numpy as np

DIAMETERS_LIPS_TO_LARYNX_MM = (32, 28, 30, 34, 34, 38, 34, 30, 26, 20, 14, 12, 16, 26, 12, 12)
RHO = 1.21
SOUND_SPEED = 343.0
ATTENUATION = 0.4
LOAD_RATIO = 0.05
DISTANCE = 0.20
SECTION_LENGTH = 0.01


def published_areas() -> np.ndarray:
    return np.array([math.pi * (d / 2000.0) ** 2
                     for d in reversed(DIAMETERS_LIPS_TO_LARYNX_MM)], dtype=np.float64)


def reference_weights(center: int) -> np.ndarray:
    return np.array([0.25 if abs(i-center) == 2 else
                     0.5 if abs(i-center) == 1 else
                     1.0 if i == center else 0.0
                     for i in range(16)], dtype=np.float64)


def reference_areas(center: int, ratio: float) -> np.ndarray:
    base = published_areas()
    if ratio == 1.0:
        return base
    weights = reference_weights(center)
    return np.array([a * math.pow(ratio, float(w))
                     for a,w in zip(base,weights,strict=True)])


def static_volume(areas: np.ndarray) -> float:
    return math.fsum(float(a) * SECTION_LENGTH for a in areas)


def volume_derivative(areas: np.ndarray, center: int) -> float:
    return math.fsum(float(a) * float(w) * SECTION_LENGTH
                     for a,w in zip(areas,reference_weights(center),strict=True))


def _segment(f: np.ndarray, area: float) -> tuple[np.ndarray,np.ndarray,np.ndarray,np.ndarray]:
    phase=(2*np.pi*f/SOUND_SPEED - 1j*ATTENUATION)*SECTION_LENGTH
    z=RHO*SOUND_SPEED/area
    cs,sn=np.cos(phase),np.sin(phase)
    return cs,1j*z*sn,1j*sn/z,cs


def direct_uout_uin(areas: np.ndarray, freq: np.ndarray) -> np.ndarray:
    f=np.asarray(freq,dtype=float)
    M=np.broadcast_to(np.eye(2,dtype=complex),(f.size,2,2)).copy()
    for a in areas:
        A,B,C,D=_segment(f,float(a))
        T=np.empty((f.size,2,2),dtype=complex)
        T[:,0,0],T[:,0,1]=A,B
        T[:,1,0],T[:,1,1]=C,D
        M=M@T
    load=LOAD_RATIO*RHO*SOUND_SPEED/float(areas[-1])
    return 1/(M[:,1,0]*load+M[:,1,1])


def recursive_uout_uin(areas: np.ndarray, freq: np.ndarray) -> np.ndarray:
    f=np.asarray(freq,dtype=float)
    down=np.full(f.size,LOAD_RATIO*RHO*SOUND_SPEED/float(areas[-1]),dtype=complex)
    gain=np.ones(f.size,dtype=complex)
    for a in areas[::-1]:
        A,B,C,D=_segment(f,float(a))
        denominator=C*down+D
        gain/=denominator
        down=(A*down+B)/denominator
    return gain


def radiated_pressure_proxy(u_ratio: np.ndarray, freq: np.ndarray) -> np.ndarray:
    f=np.asarray(freq,dtype=float)
    return (1j*2*np.pi*f*RHO/(4*np.pi*DISTANCE)
            *np.exp(-1j*2*np.pi*f*DISTANCE/SOUND_SPEED)*u_ratio)
