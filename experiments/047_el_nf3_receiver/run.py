#!/usr/bin/env python3
"""EL-NF3 preregistered research evidence runner (no runtime audio product).

Usage:
    python experiments/047_el_nf3_receiver/run.py audit --sofa FILE
    python experiments/047_el_nf3_receiver/run.py evaluate --sofa FILE --output FILE
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.signal import correlate

from model import (load_sofa, block_roles, xyz_to_spherical, Predictor,
                   band_ild_error, Unsupported, deterministic_split_hash)

ORIGINAL_MD5 = "8e286f7f2ffa67973bb0eb2e37c158e2"
MODES = ("B0", "B1", "B2", "C1", "C2")
TARGET_RADII = {"S1":(.2,.3,.4,.5), "S2":(.3,.4)}
SEED = 20261030


def _distance_deg(a, b):
    return abs((a-b+180)%360-180)


def coordinate_targets(xyz, roles, bins, role, fold):
    """One target per observed angular block x radius, no acoustic inspection."""
    sph=xyz_to_spherical(xyz)
    out=[]
    for key in sorted(set(map(tuple, bins[np.asarray(roles)==role]))):
        members=np.flatnonzero((np.asarray(roles)==role) & np.all(bins==key,axis=1))
        for desired in TARGET_RADII[fold]:
            ix=members[np.abs(sph[members,2]-desired)<=.004]
            if not len(ix):
                continue
            ca=20*key[0]+10; ce=10*key[1]-20
            # Absolute radius distance dominates, then angular centrality and index.
            order=sorted(ix, key=lambda i:(round(abs(sph[i,2]-desired),8),
                round(_distance_deg(sph[i,0],ca)**2+(sph[i,1]-ce)**2,8),int(i)))
            out.append((int(order[0]),str(key)))
    return out


def _model_map(data, roles, fold):
    sph=xyz_to_spherical(data.xyz)
    keep=np.asarray(roles)=="train"
    keep &= (sph[:,2]>=.195) & (sph[:,2]<=.505)
    if fold=="S2":
        keep &= (np.abs(sph[:,2]-.20)<=.004) | (np.abs(sph[:,2]-.50)<=.004)
    ix=np.flatnonzero(keep)
    return {m:Predictor(data,ix,m) for m in MODES}


def _itd_seconds(ir,fs):
    fft=np.fft.rfft(ir,axis=-1)
    freq=np.fft.rfftfreq(ir.shape[-1],1/fs)
    fft[:,(freq<500)|(freq>1500)]=0
    filt=np.fft.irfft(fft,n=ir.shape[-1],axis=-1)
    corr=correlate(filt[0],filt[1],mode="full",method="fft")
    ix=int(np.argmax(np.abs(corr)))
    frac=0.
    if 0<ix<len(corr)-1:
        a,b,c=np.abs(corr[ix-1:ix+2])
        den=a-2*b+c
        if abs(den)>1e-15:
            frac=np.clip(.5*(a-c)/den,-1.,1.)
    return (ix-(len(ir[0])-1)+frac)/fs


def _shape_error(pred,truth,fs):
    freqs=np.fft.rfftfreq(pred.shape[-1],1/fs)
    valid=(freqs>=500)&(freqs<8000)
    if not valid.any():
        raise Unsupported("Spectral range unresolved")
    def log_spectra(arr):
        x=20*np.log10(np.maximum(np.abs(np.fft.rfft(arr,axis=-1)[:,valid]),1e-12))
        return x-x.mean(axis=-1,keepdims=True)
    dif=log_spectra(pred)-log_spectra(truth)
    return float(np.sqrt(np.mean(dif**2)))


def _one_result(data,predictor,index):
    try:
        predicted,meta=predictor.predict(data.xyz[index])
        truth=data.ir[index]
        ild=band_ild_error(predicted,truth,data.fs)
        if not np.all(np.isfinite(ild)):
            raise Unsupported("Invalid ILD")
        return {"supported":True,
                "ild_error_db":[round(float(x),8) for x in ild],
                "itd_error_us":round(abs(_itd_seconds(predicted,data.fs)-_itd_seconds(truth,data.fs))*1e6,8),
                "spectral_rmse_db":round(_shape_error(predicted,truth,data.fs),8),
                "geometry":meta}
    except (Unsupported, ValueError, FloatingPointError) as err:
        return {"supported":False, "reason":str(err)}


def _run_fold(data,roles,bins,role,fold,predictors):
    targets=coordinate_targets(data.xyz,roles,bins,role,fold)
    rows=[]
    for ix,block in targets:
        row={"index":ix,"block":block,"fold":fold,
             "radius_m":round(float(np.linalg.norm(data.xyz[ix])),5),
             "models":{m:_one_result(data,p,ix) for m,p in predictors.items()}}
        rows.append(row)
    return rows


def _median(rows,model):
    values=[v for row in rows for v in row["models"][model].get("ild_error_db",[])]
    return float(np.median(values)) if values else float("inf")


def _supported_blocks(rows,model):
    return len({row["block"] for row in rows if row["models"][model]["supported"]})


def _guard_feature(row):
    r=row["models"]["C2"]
    if not r["supported"]:
        return float("inf")
    g=r["geometry"]
    return float(g["angular_span_deg"]+5*g["radial_gap_m"])


def _paired_bootstrap(rows,baseline,draws=2000):
    groups=sorted({row["block"] for row in rows})
    if not groups:
        return None
    bygroup={b:[row for row in rows if row["block"]==b] for b in groups}
    rng=np.random.default_rng(SEED)
    improvements=[]
    for _ in range(draws):
        selected=rng.integers(0,len(groups),len(groups))
        sample=[row for i in selected for row in bygroup[groups[int(i)]]]
        improvements.append(_median(sample,baseline)-_median(sample,"C2"))
    return [float(x) for x in np.percentile(improvements,[2.5,97.5])]


def _atomic_write(path,record):
    p=Path(path)
    if p.exists():
        raise FileExistsError("Evidence file already exists: refusing overwrite")
    p.parent.mkdir(parents=True,exist_ok=True)
    serialized=json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False,sort_keys=True)
    p.write_text(serialized+"\n",encoding="utf-8")


def audit_only(data,roles,bins):
    sph=xyz_to_spherical(data.xyz)
    return {"sha256":data.source_sha256,"measurement_plane":data.reference_plane,
        "points":len(data.xyz),"hrir_length":int(data.ir.shape[-1]),"fs":data.fs,
        "min_radius_m":float(sph[:,2].min()),"max_radius_m":float(sph[:,2].max()),
        "elevation_min_max":[float(sph[:,1].min()),float(sph[:,1].max())],
        "azimuth_min_max":[float(sph[:,0].min()),float(sph[:,0].max())],
        "allocated_positions":{s:int((roles==s).sum()) for s in ("train","selection","calibration","final","buffer")},
        "distinct_angular_blocks":len(set(map(tuple,bins))),
        "split_sha256":deterministic_split_hash(data.xyz,roles),
        "license_status":"LICENSE_UNVERIFIED",
        "acoustic_reference_status":"UNVERIFIED_DO_NOT_CLAIM_ABSOLUTE_PA"}


def evaluate(data,roles,bins):
    modelsets={fold:_model_map(data,roles,fold) for fold in ("S1","S2")}
    selection=sum((_run_fold(data,roles,bins,"selection",f,modelsets[f]) for f in ("S1","S2")),[])
    calibration=sum((_run_fold(data,roles,bins,"calibration",f,modelsets[f]) for f in ("S1","S2")),[])
    final=sum((_run_fold(data,roles,bins,"final",f,modelsets[f]) for f in ("S1","S2")),[])
    # Selection-only frozen baseline decision.
    eligible=[m for m in MODES if m!="C2" and all(
        _supported_blocks([row for row in selection if row["fold"]==f],m)>=8 for f in ("S1","S2"))]
    baseline=min(eligible,key=lambda m:(_median(selection,m),MODES.index(m))) if eligible else None
    candidates=[_guard_feature(row) for row in calibration if np.isfinite(_guard_feature(row))]
    threshold=float(np.percentile(candidates,80)) if len(candidates)>=8 else None
    accepted=[row for row in final if baseline is not None and threshold is not None
        and row["models"][baseline]["supported"] and
        _guard_feature(row)<=threshold]
    byfold={f:[row for row in accepted if row["fold"]==f] for f in ("S1","S2")}
    paired_ci=_paired_bootstrap(accepted,baseline) if baseline and accepted else None
    med_b=_median(accepted,baseline) if (baseline and accepted) else None
    med_c=_median(accepted,"C2")
    def _diag(m,key):
        vals=[row["models"][m][key] for row in accepted]
        return float(np.median(vals)) if vals else None
    base_band=[e for row in accepted for e in row["models"][baseline].get("ild_error_db",[])] if baseline else []
    c2_band=[e for row in accepted for e in row["models"]["C2"].get("ild_error_db",[])]
    p95_b=float(np.percentile(base_band,95)) if base_band else None
    p95_c=float(np.percentile(c2_band,95)) if c2_band else None
    coverage=len(accepted)/len(final) if final else 0.
    gates={
        "baseline_selected_on_selection_only":baseline is not None,
        "median_15pct_better":bool(med_b and np.isfinite(med_c) and med_c<=.85*med_b),
        "block_CI_positive":bool(paired_ci and paired_ci[0]>0),
        "both_folds_better":bool(baseline and all(
            _median(byfold[f],"C2")<_median(byfold[f],baseline) for f in ("S1","S2"))),
        "ITD_noninferior":bool(baseline and _diag("C2","itd_error_us") is not None
            and _diag("C2","itd_error_us")<=_diag(baseline,"itd_error_us")+25),
        "spectral_noninferior":bool(baseline and _diag("C2","spectral_rmse_db") is not None
            and _diag("C2","spectral_rmse_db")<=_diag(baseline,"spectral_rmse_db")+.5),
        "upper_tail_noninferior":bool(p95_c is not None and p95_b is not None and p95_c<=p95_b+1),
        "overall_coverage_80pct":coverage>=.80,
        "eight_blocks_each":all(len({row["block"] for row in byfold[f]})>=8 for f in ("S1","S2"))
    }
    numerical="PASS_LIMITED_NUMERIC" if all(gates.values()) else "REVISE_OR_REJECT"
    if baseline is None or threshold is None or not gates["eight_blocks_each"]:
        numerical="INDETERMINATE"
    return {"baseline":baseline,"selection_medians":{m:(_median(selection,m) if np.isfinite(_median(selection,m)) else None) for m in MODES},
        "calibration_geometry_threshold":threshold,
        "final_evaluated_queries":len(final),"accepted_queries":len(accepted),
        "accepted_coverage":coverage,
        "geometric_C2_coverage":sum(row["models"]["C2"]["supported"] for row in final)/len(final) if final else 0,
        "matched_baseline_ild_median_db":(med_b if med_b is not None and np.isfinite(med_b) else None),"matched_C2_ild_median_db":med_c if np.isfinite(med_c) else None,
        "paired_block_bootstrap_95ci_baseline_minus_c2_db":paired_ci,
        "matched_baseline_ild_p95_db":p95_b,"matched_C2_ild_p95_db":p95_c,
        "gates":gates,
        "numerical_verdict":numerical,
        "science_adoption":"NOT_ADOPTED",
        "metrology_verdict":"INDETERMINATE_REFERENCE_PLANE_AND_LICENSE_PENDING",
        "final_rows":final}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=["audit","evaluate"])
    p.add_argument("--sofa",required=True)
    p.add_argument("--output")
    p.add_argument("--skip-original-md5",action="store_true",
                   help="Synthetic local tests only: cannot count as real G3 evidence")
    args=p.parse_args()
    if args.command=="evaluate" and not args.output:
        p.error("--output required to evaluate; no implicit stdout of raw results")
    data=load_sofa(args.sofa,None if args.skip_original_md5 else ORIGINAL_MD5)
    roles,bins=block_roles(data.xyz)
    evidence={"schema_version":"el-nf3-evidence/v1",
        "research_only":True,"prereg_commit":"df6addb58296e9945569ff3473aa65039ef959cb",
        "prereg_execution_version":"PREREGISTRATION_V1_1.md",
        "source_url":"https://zenodo.org/records/7626148",
        "md5_verified":not args.skip_original_md5,
        "synthetic_or_unverified_source":bool(args.skip_original_md5),
        "audit":audit_only(data,roles,bins)}
    if args.command=="evaluate":
        evidence["experiment"]=evaluate(data,roles,bins)
        _atomic_write(args.output,evidence)
        print(json.dumps({k:v for k,v in evidence["experiment"].items() if k!="final_rows"},
              indent=2,allow_nan=False))
        print("Evidence written to",args.output)
    else:
        print(json.dumps(evidence,indent=2,allow_nan=False))

if __name__=="__main__":
    main()
