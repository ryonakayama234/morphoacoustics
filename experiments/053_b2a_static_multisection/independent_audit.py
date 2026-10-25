"""Independent B2-A verifier: RAW archive only, no B0/B1/B1b/B2 imports.

Continuum 2x2 cascade derived independently of local junction/queues.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

RHO=1.21
C=343.
FREQS=(200.,400.,600.,1000.,1500.,2200.)
NS=(2,4,8)

def h_analog(f,areas,lengths):
    # Continuum exp(+j omega t) section transfer maps lip->source.
    # Independent of any discrete junction/recursion implementation.
    omega=2*math.pi*f
    mat=np.eye(2,dtype=np.complex128)
    for area,length in zip(areas,lengths):
        zc=RHO*C/area
        theta=omega*length/C
        co,si=math.cos(theta),math.sin(theta)
        section=np.array([[co,1j*zc*si],[1j*si/zc,co]],dtype=complex)
        mat=mat @ section
    lip_area=areas[-1]
    radius=math.sqrt(lip_area/math.pi)
    M=8*RHO*radius/(3*math.pi*lip_area)
    tau=3*math.pi*radius/(16*C)
    Zlip=M*(1j*omega)/(1+tau*(1j*omega))
    return 1/(mat[1,0]+mat[1,1]/Zlip)

def load(out):
    manifest=json.loads((out/"manifest.json").read_text())
    assert manifest["prereg_sha"]=="70e4875c77336df0eb3f2e2b6d4a402e209d3d6f"
    receipt=(out/"CI_EVIDENCE.txt").read_text()
    assert "EXACT_GITHUB_SHA=" in receipt and "GITHUB_RUN_ID=" in receipt
    blobs={}
    for name,sha in manifest["sha256"].items():
        data=(out/name).read_bytes()
        assert hashlib.sha256(data).hexdigest()==sha,(name,"hash failure")
        arr=np.load(out/name,allow_pickle=False)
        assert np.isfinite(arr).all()
        blobs[name]=arr
    assert len(blobs)==14
    report={}
    for body in ("M0","M1"):
        spec=manifest["bodies"][body]
        areas=np.asarray(spec["areas_m2"],float)
        lengths=np.asarray(spec["lengths_m"],float)
        assert len(areas)==16 and len(lengths)==16
        assert spec["preset_id"]=="v3b-axial-"+body
        assert spec["revision"]==1 and spec["digest"].startswith("sha256:")
        expected_section=.01 if body=="M0" else .011
        np.testing.assert_allclose(lengths,expected_section,rtol=0,atol=1e-15)
        stored_errors={}
        for n in NS:
            name=f"{body}_n{n}_b0_full_impulse.npy"
            raw=blobs[name]
            fs=C*n/expected_section
            target_ticks=int(math.ceil(2*fs))
            assert raw.shape==(target_ticks,),(name,raw.shape,target_ticks)
            expected_tick=16*n
            assert np.array_equal(raw[:expected_tick],np.zeros(expected_tick))
            assert raw[expected_tick]!=0.
            arr=manifest["arrival"][f"{body}_n{n}"]
            assert arr["tick"]==expected_tick
            assert math.isclose(arr["one_way_s"],sum(lengths)/C,rel_tol=1e-12)
            time=np.arange(len(raw),dtype=float)/fs
            this={}
            for f in FREQS:
                ka=2*math.pi*f*math.sqrt(areas[-1]/math.pi)/C
                assert ka<=.8,(body,f,"out of B0 domain")
                empirical=np.dot(raw,np.exp(-2j*math.pi*f*time))/1e-6
                reference=h_analog(f,areas,lengths)
                err=abs(empirical-reference)/abs(reference)
                this[str(f)]=float(err)
            stored_errors[n]=this
        for f in FREQS:
            es=[stored_errors[n][str(f)] for n in NS]
            assert es[0]<=.035,(body,f,es)
            if es[0]>=1e-8:
                assert es[1]<=.38*es[0],(body,f,es)
            if es[1]>=1e-8:
                assert es[2]<=.38*es[1],(body,f,es)
        for term in ("closed","pressure_release","matched","b0"):
            raw=blobs[f"{body}_{term}_signed_trace.npy"]
            assert raw.shape==(1024,15)
            cfg_dt=expected_section/(2*C)
            prev=np.r_[0.,raw[:-1,9]+raw[:-1,10]]
            current=raw[:,9]+raw[:,10]
            srcwork=cfg_dt*raw[:,6]*raw[:,1]
            loss=raw[:,12]
            assert np.all(loss>=0)
            np.testing.assert_allclose(srcwork,raw[:,11],rtol=1e-11,atol=1e-19)
            de=current-prev
            residual=de-srcwork+loss
            bound=np.maximum(
               1e-9*np.maximum.reduce((abs(de),abs(srcwork),loss,np.full(len(raw),1e-20))),
               1e-12*np.maximum.reduce((prev,current,np.full(len(raw),1e-20))))
            assert np.all(abs(residual)<=bound),(body,term,"energy mismatch")
            if term in ("closed","pressure_release"):
                assert np.array_equal(loss,np.zeros(len(loss)))
            if term=="pressure_release":
                assert np.array_equal(raw[:,7],np.zeros(len(raw)))
        report[body]={"complex_continuum_relative_errors":{str(n):stored_errors[n] for n in NS},
                      "one_way_s":float(sum(lengths)/C)}
    assert abs(report["M1"]["one_way_s"]/report["M0"]["one_way_s"]-1.1)<1e-12
    # Body-length intervention must affect the real transfer, not a body label.
    for f in FREQS:
        h0=h_analog(f,manifest["bodies"]["M0"]["areas_m2"],manifest["bodies"]["M0"]["lengths_m"])
        h1=h_analog(f,manifest["bodies"]["M1"]["areas_m2"],manifest["bodies"]["M1"]["lengths_m"])
        assert abs(h0-h1)>1e-6*abs(h0)
    return {"outcome":"B2A_INDEPENDENT_RAW_AUDIT_PASS",
            "file_count":len(blobs),"source_receipt":receipt.strip().splitlines(),
            "bodies":report}

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--dir",type=Path,required=True)
    print(json.dumps(load(ap.parse_args().dir),indent=2,sort_keys=True))
