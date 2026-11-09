"""SA-2A — research-only physically coherent baffled-piston lip radiation.

No Core solver replacement, no waveform renderer, no causal FSI boundary claim.
SciPy is intentionally experiment-local and installed explicitly in SA-2 CI.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import runpy
from pathlib import Path

import numpy as np
from scipy.special import j1, struve

ROOT = Path(__file__).resolve().parents[2]
RHO = 1.21
C = 343.0
R_RECEIVER = 1.0  # metres; FORMAL FAR FIELD, not actual microphone calibration
X_GRID = np.array([0., .005, .02, .1, .25, .55, .8], dtype=np.float64)
X_MAX = .8
ORACLE_ABS_ERROR = 2e-9
POWER_REL_ERROR = 2e-8
PORT_IDENTITY_REL_ERROR = 2e-10
AIR_FREQUENCIES = np.array([200., 1000., 3000.], dtype=np.float64)
GEO_RADII = (.005, .010)
QUAD_NODES = 256
LEGACY_BASE_SHA = "6869cfec04041393eae44485ce2fc91f002114f5"
PREREG_SHA = "38f27596b91c47f7307d34af225f8293afb6268a"


def _positive(name: str, x: float) -> float:
    if isinstance(x, bool) or not np.isscalar(x) or not np.isfinite(x) or x <= 0:
        raise ValueError(f"{name} must be finite positive")
    return float(x)


def _freq(frequencies_hz: np.ndarray | float) -> np.ndarray:
    f = np.asarray(frequencies_hz, dtype=np.float64)
    if not np.isfinite(f).all():
        raise ValueError("nonfinite frequency")
    return f


def _normalized_nonnegative(x: np.ndarray | float) -> np.ndarray:
    """Exact R+iX, with series at origin, for x=ka>=0."""
    x = np.asarray(x, dtype=np.float64)
    if np.any(~np.isfinite(x)) or np.any(x < 0):
        raise ValueError("ka must be finite and nonnegative")
    # Protect catastrophic 1-J1(2x)/x cancellation at x→0.
    small = x < .001
    safe = np.where(small, 1., x)
    r = 1. - j1(2*safe)/safe
    im = struve(1, 2*safe)/safe
    r = np.where(small, x*x/2. - x**4/12. + x**6/144., r)
    im = np.where(small, 8*x/(3*math.pi) - 32*x**3/(45*math.pi), im)
    return np.asarray(r+1j*im, dtype=np.complex128)


def radiation_impedance(
    frequencies_hz: np.ndarray | float,
    radius_m: float,
    *,
    rho: float = RHO,
    c: float = C,
) -> np.ndarray:
    """Acoustic load p_lip/U_lip, Pa*s/m³; exp(+iωt), outward U positive."""
    a = _positive("radius", radius_m)
    rho = _positive("rho", rho)
    c = _positive("c", c)
    f = _freq(frequencies_hz)
    x = np.abs(2.*np.pi*f*a/c)
    zn = _normalized_nonnegative(x)
    # Hermitian physical impedance: Z(-f)=conj(Z(+f)).
    zn = np.where(f < 0., np.conj(zn), zn)
    return (rho*c/(math.pi*a*a))*zn


def normalized_overlap_oracle(x: np.ndarray | float) -> np.ndarray:
    """Independent Rayleigh double-area overlap quadrature; no Bessel/Struve."""
    x = np.asarray(x, dtype=np.float64)
    if np.any(~np.isfinite(x)) or np.any(x < 0):
        raise ValueError("invalid ka")
    nodes, weights = np.polynomial.legendre.leggauss(QUAD_NODES)
    t = .5*(nodes+1.)
    weights = .5*weights
    disk_overlap = np.arccos(t)-t*np.sqrt(1.-t*t)
    flat = x.ravel()
    osc = np.exp(-2j*flat[:, None]*t[None, :])
    result = (4j*flat/math.pi)*((osc*disk_overlap[None, :])@weights)
    return result.reshape(x.shape)


def directivity(ka: np.ndarray | float, theta_rad: np.ndarray | float) -> np.ndarray:
    x = np.asarray(ka, dtype=np.float64)
    theta = np.asarray(theta_rad, dtype=np.float64)
    if (np.any(~np.isfinite(x)) or np.any(x < 0)
        or np.any(~np.isfinite(theta)) or np.any(theta < 0)
        or np.any(theta > math.pi/2)):
        raise ValueError("invalid ka or forward-hemisphere angle")
    q = x*np.sin(theta)
    safe = np.where(abs(q)<1e-7, 1., q)
    value = 2.*j1(safe)/safe
    return np.where(abs(q)<1e-7, 1. - q*q/8. + q**4/192., value)


def farfield_observer_per_volume_flow(
    frequencies_hz: np.ndarray | float,
    radius_m: float,
    *,
    theta_rad: float = 0.,
    distance_m: float = R_RECEIVER,
    rho: float = RHO,
    c: float = C,
) -> np.ndarray:
    """Formal baffled-piston FAR-FIELD p(r,theta)/U_lip, Pa*s/m³.

    Hemisphere 2*pi geometry, NOT legacy full-space point monopole 4*pi.
    Use only with a verified farfield regime, never as nearfield p at a lip.
    """
    a = _positive("radius", radius_m)
    distance_m = _positive("distance", distance_m)
    rho = _positive("rho", rho)
    c = _positive("c", c)
    theta = float(theta_rad)
    f = _freq(frequencies_hz)
    if not np.isfinite(theta) or not 0 <= theta <= math.pi/2:
        raise ValueError("only forward-hemisphere theta supported")
    k = 2.*np.pi*f/c
    d = directivity(np.abs(k)*a,theta)
    return 1j*(2.*np.pi*f)*rho/(2.*np.pi*distance_m)*np.exp(-1j*k*distance_m)*d


def hemisphere_resistance_quadrature(x: np.ndarray | float) -> np.ndarray:
    """INDEPENDENT far-field power -> dimensionless radiation resistance.

    Integrates power over forward hemisphere, not just a single observer Pa.
    R = (ka)^2/2 * ∫_0^1 D(acos(u))^2 du.
    """
    x = np.asarray(x, dtype=np.float64)
    if np.any(~np.isfinite(x)) or np.any(x < 0):
        raise ValueError("invalid ka")
    nodes, weights = np.polynomial.legendre.leggauss(QUAD_NODES)
    u = .5*(nodes+1.)
    weights = .5*weights
    y = x.reshape(-1,1)*np.sqrt(1.-u[None,:]**2)
    safe = np.where(abs(y)<1e-7,1.,y)
    direct = np.where(abs(y)<1e-7,1.-y*y/8.+y**4/192.,2.*j1(safe)/safe)
    return ((x.reshape(-1,1)**2/2.) * (direct**2 @ weights).reshape(-1,1)).reshape(x.shape)


def _complex_number(value: complex) -> dict[str, float]:
    return {"real":float(np.real(value)),"imag":float(np.imag(value))}


def _npy(array: np.ndarray) -> bytes:
    b = io.BytesIO()
    np.save(b, np.asarray(array), allow_pickle=False)
    return b.getvalue()


def analytic_gates() -> dict[str, object]:
    x = X_GRID
    ref = _normalized_nonnegative(x)
    quad = normalized_overlap_oracle(x)
    err = float(np.max(abs(ref-quad)))
    if err > ORACLE_ABS_ERROR:
        raise AssertionError(("independent Rayleigh overlap oracle",err))
    power_ref = hemisphere_resistance_quadrature(x)
    rel = float(np.max(abs(power_ref[2:]-ref[2:].real)/ref[2:].real))
    if rel > POWER_REL_ERROR:
        raise AssertionError(("hemispherical power mismatch",rel))
    r_small = float(np.max(abs(ref[1:3].real/(x[1:3]**2/2.)-1.)))
    im_small = float(np.max(abs(ref[1:3].imag/(8.*x[1:3]/(3.*math.pi))-1.)))
    if not (r_small<.001 and im_small<.001):
        raise AssertionError(("low-ka asymptotes",r_small,im_small))
    if np.any(ref.real < -1e-12) or np.any(ref[1:].imag < -1e-12):
        raise AssertionError("nonpassive radiation impedance")
    f = np.array([-1000.,0.,1000.])
    z = radiation_impedance(f,.01)
    if abs(z[0]-np.conj(z[2]))>1e-12 or z[1]!=0:
        raise AssertionError("real-valued time-kernel conjugate symmetry")
    theta=np.array([0.,math.pi/6.,math.pi/3.])
    if not np.isclose(directivity(.5,theta)[0],1.,atol=1e-12,rtol=0):
        raise AssertionError("on-axis directivity")
    return {"oracle_max_abs_error":err,"hemisphere_max_relative_power_error":rel,
            "small_ka_R_relative_error":r_small,"small_ka_X_relative_error":im_small,
            "minimum_R":float(np.min(ref.real)),
            "negative_frequency_conjugate":True,
            "onaxis_D":float(directivity(.5,0.)),
            "ka_grid":x.tolist()}


def body_frequency_study() -> tuple[dict[str, object], dict[str,np.ndarray]]:
    """Genuine frozen CC-A2 M0 static body; port spectra, NOT rendered WAV."""
    sv=runpy.run_path(str(ROOT/"experiments/042_sv1_sustained_vowel/run.py"))
    _,exp,res=sv["_validated_context"]()
    geom=res.preset.prepared.rest_state
    exp9=exp.EXP26.EXP23.EXP9
    if exp9.OBSERVATION_DISTANCE_M != .2:
        raise AssertionError("legacy comparison changed")
    lip_area=geom.sections[-1].area_m2
    a=math.sqrt(lip_area/math.pi)
    f=AIR_FREQUENCIES.copy()
    x=2.*np.pi*f*a/C
    mask=x<=X_MAX
    if not np.any(mask):
        raise AssertionError("no M0 frequency within registered ka domain")
    valid_f=f[mask]
    m=exp9.lossy_transfer_matrix(geom,valid_f)
    aa,bb,cc,dd=m[...,0,0],m[...,0,1],m[...,1,0],m[...,1,1]
    zl=radiation_impedance(valid_f,a)
    denominator=cc*zl+dd
    if (np.any(~np.isfinite(denominator))
        or np.any(abs(denominator)<1e-12)):
        raise AssertionError("ill-conditioned tube/loaded mouth")
    tu=1./denominator
    zin=(aa*zl+bb)/denominator
    # Compute port state from a single declared hypothetical peak volume flow.
    u_in=1e-6
    u_lip=tu*u_in
    p_lip=zl*u_lip
    p_in=zin*u_in
    port_identity = np.max(abs((cc*p_lip+dd*u_lip)-u_in))/u_in
    p_identity = np.max(abs(aa*p_lip+bb*u_lip-p_in))/max(np.max(abs(p_in)),1e-20)
    identity=float(max(port_identity,p_identity))
    if identity>PORT_IDENTITY_REL_ERROR: raise AssertionError(("port identities",identity))
    power_in=.5*np.real(p_in*np.conj(u_in))
    power_lip=.5*np.real(p_lip*np.conj(u_lip))
    min_diss=float(np.min(power_in-power_lip))
    if min_diss< -1e-12: raise AssertionError(("nonpassive tract",min_diss))
    receiver=farfield_observer_per_volume_flow(valid_f,a,theta_rad=0.)*u_lip
    legacy=exp9.far_field_pressure_transfer(geom,valid_f)*u_in
    entries=[]
    for i,frequency in enumerate(valid_f):
        entries.append({"frequency_hz":float(frequency),"ka":float(x[mask][i]),
            "zin_pa_s_m3":_complex_number(zin[i]),"zrad_pa_s_m3":_complex_number(zl[i]),
            "lip_u_over_glottal_u":_complex_number(tu[i]),
            "raw_observer_formal_farfield_pa":_complex_number(receiver[i]),
            "legacy_exp009_observer_pa_at_0p2m":_complex_number(legacy[i]),
            "power_in_w":float(power_in[i]),"power_lip_w":float(power_lip[i]),
            "declared_observer_m":R_RECEIVER,"legacy_observer_m":.2})
    result={"real_prepared_body":"CC-A2 M0 /a/-like adopted through SV-1",
       "lip_area_m2":float(lip_area),"lip_radius_m":float(a),
       "total_length_m":float(geom.total_length_m),
       "section_count":len(geom.sections),
       "rejected_frequencies_hz":f[~mask].tolist(),
       "ka_limit":X_MAX,"port_identity_max_rel":identity,
       "minimum_power_dissipated_w":min_diss,
       "state":"FREQUENCY_ONLY_NO_CAUSAL_TIME_DOMAIN",
       "traces":entries}
    arrays={"m0_f_hz.npy":valid_f,"m0_zrad_pa_s_m3.npy":zl,
       "m0_zin_pa_s_m3.npy":zin,"m0_U_lips_per_U_in.npy":tu,
       "m0_observer_formal_pa.npy":receiver,"m0_legacy_observer_pa.npy":legacy,
       "m0_geometry_areas_m2.npy":np.array([z.area_m2 for z in geom.sections]),
       "m0_geometry_lengths_m.npy":np.array([z.length_m for z in geom.sections])}
    return result,arrays


def execute(out: Path) -> dict[str, object]:
    if out.exists(): raise FileExistsError("SA-2A evidence output already exists")
    gates=analytic_gates()
    body,body_arrays=body_frequency_study()
    geometry_sensitivity=[]
    for a in GEO_RADII:
        for f in (1000.,3000.):
            x=2*math.pi*f*a/C
            if x>X_MAX:continue
            z=radiation_impedance(f,a)
            zc=RHO*C/(math.pi*a*a)
            normalized=z/zc
            oracle=_normalized_nonnegative(x)
            if abs(normalized-oracle)>2e-10:
                raise AssertionError("radius scaling failed")
            geometry_sensitivity.append({"radius_m":a,"frequency_hz":f,"ka":x,
                "zrad_pa_s_m3":_complex_number(complex(z)),
                "normalized_zrad":_complex_number(complex(normalized))})
    refs=_normalized_nonnegative(X_GRID)
    arrays={"ka_grid.npy":X_GRID,"normalized_analytic.npy":refs,
            "normalized_overlap_reference.npy":normalized_overlap_oracle(X_GRID),
            "hemisphere_resistance.npy":hemisphere_resistance_quadrature(X_GRID),
            **body_arrays}
    out.mkdir(parents=True)
    file_sha={}
    for filename,array in sorted(arrays.items()):
        data=_npy(array)
        (out/filename).write_bytes(data)
        file_sha[filename]=hashlib.sha256(data).hexdigest()
    result={"schema":"research.sa2a.v0","adoption":"NOT_ADOPTED",
            "result":"SA2A_ANALYTIC_REFERENCE_VERIFIED",
            "sa2b":"SA2B_TIME_DOMAIN_NOT_RUN",
            "exact_executed_head":"SEE_GITHUB_ACTIONS_CI_RECEIPT_NOT_THIS_PLACEHOLDER",
            "preregistration_sha":PREREG_SHA,"baseline_main_sha":LEGACY_BASE_SHA,
            "reference_model":"infinite rigid baffle + uniform circular piston",
            "phasor_convention":"exp(+iwt), outgoing exp(-ikr), outward volume flow",
            "air":{"rho_kg_m3":RHO,"sound_speed_m_s":C},
            "observer":{"r_m":R_RECEIVER,"field":"formal farfield on axis, not a microphone claim"},
            "gates":gates,"body_frequency_study":body,
            "calibration_radius_study":geometry_sensitivity,
            "artifact_sha256":file_sha}
    (out/"manifest.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    arg=parser.parse_args()
    result=execute(arg.out)
    print(json.dumps({"result":result["result"],"sa2b":result["sa2b"],
                      "gates":result["gates"],"body":result["body_frequency_study"]},
                     indent=2,sort_keys=True))
