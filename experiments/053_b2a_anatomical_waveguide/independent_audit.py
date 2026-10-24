"""Independent B2-A audit on archived raw NPY; imports NO acoustic solver.

Reads exact archived full impulse pressure and SI energetic port samples, then
forms continuum 2-port product independently using the frozen geometry. Never
uses B2-A acoustic/scattering code, B1b, or B0 Python modules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
PREREG="46fa9a4767886428c712c6aaff263965b0351480"
FREQS=(200.,400.,600.,1000.,2600.)
BODIES=("M0_a","M1_a","M0_i")
TERMINATIONS=("closed","pressure_release","matched","b0")
COLUMN_COUNT=15
RHO,C=1.21,343.


def physical_reference(hz,areas,lengths):
    """Independent stationary continuum cascade, physical analog mouth R||M."""
    zvals=RHO*C/np.asarray(areas,dtype=np.float64)
    lengths=np.asarray(lengths,dtype=np.float64)
    transfer=np.eye(2,dtype=np.complex128)
    for z,ell in zip(zvals,lengths,strict=True):
        x=2*math.pi*hz*ell/C
        transfer=transfer@np.array([[math.cos(x),1j*z*math.sin(x)],
                                    [1j*math.sin(x)/z,math.cos(x)]])
    lip=float(areas[-1])
    radius=math.sqrt(lip/math.pi)
    inertance=8*RHO*radius/(3*math.pi*lip)
    tau=3*math.pi*radius/(16*C)
    s=2j*math.pi*hz
    load=inertance*s/(1+tau*s)
    return 1/(transfer[1,0]+transfer[1,1]/load)


def audit(folder:Path):
    manifest=json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    if manifest["prereg_sha"]!=PREREG:
        raise AssertionError("preregistration SHA mismatch")
    receipt=(folder/"CI_EVIDENCE.txt").read_text()
    pairs=dict(line.split("=",1) for line in receipt.splitlines() if "=" in line)
    source_sha=pairs["EXACT_GITHUB_SHA"]
    if not re.fullmatch(r"[0-9a-f]{40}",source_sha):
        raise AssertionError("checkout SHA must be a complete Git identity")
    if not re.fullmatch(r"\d+",pairs["GITHUB_RUN_ID"]):
        raise AssertionError("missing workflow receipt")
    ref=pairs["GITHUB_REF"]
    if ref!="refs/heads/research/sa2b-b2a-anatomical-waveguide-20261025" and not re.fullmatch(r"refs/pull/\d+/merge",ref):
        raise AssertionError("foreign branch/ref audited")
    arrays={}
    for name,digest in manifest["sha256"].items():
        raw=(folder/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:
            raise AssertionError("raw physical artifact mutated: "+name)
        arr=np.load(folder/name,allow_pickle=False)
        if not np.isfinite(arr).all():
            raise AssertionError("nonfinite physical raw artifact: "+name)
        arrays[name]=arr
    if len(arrays)!=33:
        raise AssertionError(f"expected 33 raw NPY, got {len(arrays)}")
    reference=json.loads(
        (ROOT/"experiments/028_task_field_morphology_transfer/frozen_reference.json").read_text()
    )["M0"]
    bodies=manifest["bodies"]
    if set(bodies)!=set(BODIES):
        raise AssertionError("unexpected character morphology")
    for name in BODIES:
        info=bodies[name]
        areas=np.asarray(info["areas_m2"],dtype=np.float64)
        lengths=np.asarray(info["section_lengths_m"],dtype=np.float64)
        expect=reference["i_areas_m2"] if name=="M0_i" else reference["a_areas_m2"]
        np.testing.assert_array_equal(areas,expect)
        np.testing.assert_allclose(lengths, [0.011 if name=="M1_a" else 0.01]*16,rtol=0,atol=1e-12)
        digest=hashlib.sha256(np.asarray(areas,dtype="<f8").tobytes()).hexdigest()
        assert digest==info["areas_digest_float64"],name
        assert info["lip_area_m2"]==float(areas[-1])
        assert info["length_m"]==np.sum(lengths)
        assert info["preset_id"]==("v3b-axial-M1" if name=="M1_a" else "v3b-axial-M0")
    np.testing.assert_array_equal(bodies["M0_a"]["areas_m2"],bodies["M1_a"]["areas_m2"])
    error={}
    responses={}
    energy={}
    arrivals={}
    for name in BODIES:
        info=bodies[name]
        lengths=info["section_lengths_m"]
        areas=info["areas_m2"]
        section_len=lengths[0]
        error[name]={}
        responses[name]={}
        energy[name]={}
        arrivals[name]={}
        N=32
        h=section_len/(2*C)
        for term in TERMINATIONS:
            tr=arrays[name+"_"+term+"_port.npy"]
            front=arrays[name+"_"+term+"_front.npy"]
            if tr.shape!=(768,COLUMN_COUNT) or front.shape!=(4*N+4,COLUMN_COUNT):
                raise AssertionError("wrong raw state dimensions")
            if not np.array_equal(front[:N,4],np.zeros(N)) or front[N,4]==0.:
                raise AssertionError("nonlocal pre-arrival wavefront")
            expected_return=manifest["one_way"][name][term]["first_source_reflection_tick"]
            real_ticks=np.flatnonzero(front[:,3])
            observed_return=int(real_ticks[0]) if len(real_ticks) else None
            if observed_return!=expected_return:
                raise AssertionError("first local reflection changed")
            if term in ("closed","pressure_release"):
                assert np.array_equal(front[N,5],(front[N,4] if term=="closed" else -front[N,4]))
            if term=="matched":
                assert front[N,5]==0.
            E=tr[:,9]+tr[:,10]
            before=np.r_[0.,E[:-1]]
            work=h*tr[:,6]*tr[:,1]
            loss=tr[:,12]
            delta=E-before
            res=delta-work+loss
            scale=np.maximum(1e-9*np.maximum.reduce(
                (abs(delta),abs(work),abs(loss),np.full(len(tr),1e-20))),
                1e-12*np.maximum.reduce((before,E,np.full(len(tr),1e-20))))
            if np.any(abs(res)>scale) or np.any(loss<0) or np.any(E<0):
                raise AssertionError("raw energy ledger failed "+name+"/"+term)
            np.testing.assert_allclose(tr[:,11],work,rtol=1e-10,atol=1e-19)
            if term in ("closed","pressure_release"):
                assert np.all(loss==0.)
            if term=="matched":
                assert np.all(tr[:,5]==0.)
            else:
                assert np.any(tr[:,5]!=0.)
            total=float(sum(res))
            limit=max(1e-9*max(float(sum(abs(work))+sum(loss)),1e-20),
                      1e-10*max(float(np.max(E)),1e-20))
            if abs(total)>limit:
                raise AssertionError("cumulative energy drifts "+name+"/"+term)
            energy[name][term]={
                "normalized_max_residual":float(np.max(abs(res)/scale)),
                "abs_cumulative_residual_j":abs(total),
                "signed_inlet_work_j":float(sum(work)),
                "total_loss_j":float(sum(loss))
            }
            arrivals[name][term]={"lip_tick":N,"first_any_source_echo_tick":observed_return}
        # LIP-origin echo (not the early internal scattering echoes) is 2N.
        matched=arrays[name+"_matched_front.npy"]
        closed=arrays[name+"_closed_front.npy"]
        diff=closed[:,3]-matched[:,3]
        if np.max(abs(diff[:2*N]))>1e-14 or abs(diff[2*N])<1e-10:
            raise AssertionError("first mouth-specific echo is not 2N")
        for n in (2,4,8):
            fs=C*n/section_len
            N=16*n
            pressure=arrays[name+"_b0_full_impulse_n"+str(n)+".npy"]
            if len(pressure)!=int(math.ceil(5.*fs)):
                raise AssertionError("inadequate archived impulse tail")
            if not np.array_equal(pressure[:N],np.zeros(N)) or pressure[N]==0.:
                raise AssertionError("finite-speed spatial support failed")
            times=np.arange(len(pressure),dtype=np.float64)/fs
            row={}
            for f in FREQS:
                ka=2*math.pi*f*math.sqrt(areas[-1]/math.pi)/C
                if ka>.8:
                    raise AssertionError("B0 ka domain was exceeded")
                empirical=complex(np.dot(pressure,np.exp(-2j*np.pi*f*times))/1e-6)
                oracle=physical_reference(f,areas,lengths)
                e=float(abs(empirical-oracle)/abs(oracle))
                expected=manifest["transfer"][name][str(n)][str(f)]
                if abs(e-expected["complex_relative"])>1e-10:
                    raise AssertionError("archived transfer result cannot reproduce")
                if abs(empirical-complex(*expected["empirical_complex"]))>1e-9*max(abs(empirical),1.):
                    raise AssertionError("manifest transfer values do not match raw impulse")
                row[str(f)]=e
                if n==2:
                    responses[name][str(f)]=[oracle.real,oracle.imag]
            error[name][str(n)]=row
        for f in FREQS:
            e0,e1,e2=(error[name][str(n)][str(f)] for n in (2,4,8))
            if e0>=.01 or e1>.36*e0 or e2>.36*e1:
                raise AssertionError(f"no physical continuum convergence: {name}/{f}: {e0},{e1},{e2}")
        to_seconds=section_len*16/C
        if abs(to_seconds-(.176 if name=="M1_a" else .16)/C)>1e-15:
            raise AssertionError("body-dependent time of flight wrong")
    for other in ("M1_a","M0_i"):
        changes=0
        for f in FREQS:
            A=complex(*responses["M0_a"][str(f)])
            B=complex(*responses[other][str(f)])
            if abs(A-B)/max(abs(A),abs(B))>.005:
                changes+=1
        if changes<2:
            raise AssertionError("individual character acoustic transfer collapsed "+other)
    if abs(bodies["M1_a"]["length_m"]/bodies["M0_a"]["length_m"]-1.1)>1e-14:
        raise AssertionError("axial anatomy ratio lost")
    return {
        "status":"B2A_RAW_ARTIFACT_INDEPENDENT_AUDIT_PASS",
        "exact_source_sha":source_sha,
        "workflow_run_id":pairs["GITHUB_RUN_ID"],
        "npy_files_rehashed":len(arrays),
        "complex_relative_error_by_body_and_refinement":error,
        "wavefront":arrivals,
        "energy":energy,
        "morphology_source":"frozen CC-A2 prepared M0+M1; frozen EXP028 M0/i variation",
        "audio_48k":"NOT_CONNECTED",
        "moving_anatomy":"NOT_TESTED",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--dir",required=True,type=Path)
    v=p.parse_args()
    print(json.dumps(audit(v.dir),indent=2,sort_keys=True,allow_nan=False))
