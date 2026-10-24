"""Standalone source-independent audit of archived SA-2B B1b physical wave traces.

Only consumes the archived raw NPY + manifest. NEVER imports experiment 052
solver, original B0 solver or old B1. Numerically recomputes continuum
transfer from SI physical constants and actual emitted time traces.

Run: python experiments/052_b1b_local_waveguide/independent_audit.py --dir PATH
Research evidence tool, not part of the production Core audio engine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

LENGTH_M = 0.16
AREA_M2 = 0.000804247719318987
RHO = 1.21
C = 343.0
SOURCE_IMPULSE_M3_S = 1e-6
FREQS = (200., 400., 600., 1000., 2600.)
N_VALUES = (2, 4, 8)


def analog_lip_pressure_per_source_flow(hz):
    # Independently written continuum transfer: wave propagation over
    # a physical 2-port, terminated by the original small-signal mouth R||M.
    radius = math.sqrt(AREA_M2 / math.pi)
    zc = RHO*C/AREA_M2
    inertance = 8*RHO*radius/(3*math.pi*AREA_M2)
    tau = 3*math.pi*radius/(16*C)
    zw = 1j*2*math.pi*hz
    zm = inertance*zw/(1+tau*zw)
    kL = 2*math.pi*hz*LENGTH_M/C
    return 1/(1j*math.sin(kL)/zc+math.cos(kL)/zm)


def read_and_audit(directory: Path):
    manifest = json.loads((directory/"manifest.json").read_text())
    assert manifest["preregistration_git_sha"] == (
        "ef7d74cbbafeca5113db9e4b34bbb0d220b228c4")
    receipt = (directory/"CI_EVIDENCE.txt").read_text()
    assert "EXACT_GITHUB_SHA=" in receipt
    assert "GITHUB_RUN_ID=" in receipt
    assert "GITHUB_REF=refs/heads/research/sa2b-b1b-local-waveguide-20261024" in receipt
    data={}
    for name,sha in manifest["sha256"].items():
        raw=(directory/name).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==sha,(name,"SHA mismatch")
        arr=np.load(directory/name,allow_pickle=False)
        assert np.isfinite(arr).all(),name
        data[name]=arr
    assert len(data)==14, (len(data),sorted(data))
    expected_T = LENGTH_M/C
    assert math.isclose(manifest["one_way_seconds"],expected_T,rel_tol=1e-14)
    assert math.isclose(manifest["48k_equivalent_samples"],expected_T*48000,rel_tol=1e-14)
    error_by_clock={}
    independent_empirical_complex={}
    for n in N_VALUES:
        fs=C*n/.01
        N=16*n
        assert abs(manifest["physics_clock_hz"][str(n)]-fs)<1e-9
        raw=data["b0_full_impulse_"+str(n)+".npy"]
        prefix=data["b0_impulse_prefix_"+str(n)+".npy"]
        assert raw.shape==(int(math.ceil(5.*fs)),)
        np.testing.assert_array_equal(raw[:4*N],prefix)
        assert np.array_equal(raw[:N],np.zeros(N))
        assert raw[N]!=0.0
        time=np.arange(len(raw),dtype=np.float64)/fs
        per={}
        for f in FREQS:
            h=complex(np.dot(raw,np.exp(-2j*np.pi*f*time))/SOURCE_IMPULSE_M3_S)
            analog=analog_lip_pressure_per_source_flow(f)
            error=abs(h-analog)/abs(analog)
            recorded=manifest["complex_transfer"][str(n)][str(f)]
            assert abs(error-recorded["empirical_vs_analog_complex_relative"])<1e-10,(n,f,error)
            assert abs(np.angle(h)-recorded["empirical_phase_rad"])<1e-10,(n,f)
            per[f]=float(error)
            independent_empirical_complex[str(n)+"/"+str(f)]=[h.real,h.imag]
        error_by_clock[n]=per
    for f in FREQS:
        first,second,third=(error_by_clock[n][f] for n in N_VALUES)
        assert first<.005,(f,first)
        assert second<=.32*first,(f,first,second)
        assert third<=.32*second,(f,second,third)
    for terminal in ("closed","pressure_release","matched","b0"):
        front=data[terminal+"_wavefront_trace.npy"]
        si=data[terminal+"_port_trace.npy"]
        assert front.shape==(130,15)
        assert si.shape==(1152,15)
        assert np.array_equal(front[:32,4],np.zeros(32))
        assert front[32,4]!=0.
        assert np.array_equal(front[:64,3],np.zeros(64))
        if terminal=="matched":
            assert np.array_equal(front[:,3],np.zeros(130))
        else:
            assert front[64,3]!=0.
        lip_a=front[32,4]
        lip_b=front[32,5]
        if terminal=="closed":
            assert lip_a==lip_b
        if terminal=="pressure_release":
            assert lip_a==-lip_b
        if terminal=="matched":
            assert lip_b==0.
        if terminal=="pressure_release":
            assert np.array_equal(si[:,7],np.zeros(len(si)))  # pressure release p=0
        # Recompute signed inlet work and passive energy balance from RAW SI,
        # not from the manifest's own printed residual.
        dt=.01/(2*C)
        work=dt*si[:,6]*si[:,1]
        np.testing.assert_allclose(si[:,11],work,rtol=1e-11,atol=1e-19)
        E=si[:,9]+si[:,10]
        before=np.r_[0.,E[:-1]]
        delta=E-before
        loss=si[:,12]
        residual=delta-work+loss
        bound=np.maximum(
            1e-9*np.maximum.reduce((abs(delta),abs(work),loss,np.full(len(si),1e-20))),
            1e-12*np.maximum.reduce((before,E,np.full(len(si),1e-20))))
        assert np.all(abs(residual)<=bound)
        assert np.all(loss>=0.)
        if terminal in ("closed","pressure_release"):
            assert np.array_equal(loss,np.zeros_like(loss))
        if terminal=="matched":
            assert np.all(si[:,5]==0.)
        if terminal=="b0":
            assert np.all(si[:,10]>=0)
    matched=data["matched_wavefront_trace.npy"]
    p=matched[:,7]
    tick=np.arange(len(p))
    delays={}
    for f in FREQS:
        df=.25
        hm=np.dot(p,np.exp(-2j*np.pi*(f-df)*tick/(2*C/.01)))
        hp=np.dot(p,np.exp(-2j*np.pi*(f+df)*tick/(2*C/.01)))
        delay=-np.angle(hp/hm)/(4*math.pi*df)
        assert abs(delay-expected_T)<1e-9,(f,delay,expected_T)
        delays[str(f)]=float(delay)
    return {
        "files_rehashed":len(data),
        "source_receipt":receipt.strip().splitlines(),
        "arrival_ticks":{s:manifest["first_arrival"][s] for s in
                         ("closed","pressure_release","matched","b0")},
        "empirical_complex_errors":{str(n):{str(f):error_by_clock[n][f]
                                           for f in FREQS} for n in N_VALUES},
        "measured_matched_group_delay_seconds":delays,
        "nominal_one_way_seconds":expected_T,
        "max_normalized_step_energy_residual_raw":max(
            manifest["energy"][t]["max_normalized_step_residual"] for t in
            ("closed","pressure_release","matched","b0")),
        "outcome":"INDEPENDENT_RAW_EVIDENCE_AUDIT_PASS",
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir",required=True,type=Path)
    args=ap.parse_args()
    print(json.dumps(read_and_audit(args.dir),indent=2,sort_keys=True))
