#!/usr/bin/env python3
"""EL-NF4 original SCUT blind-role experiment, research only.

Run only AFTER D0 401089c3 and G0 v1.1 bf8a5119 have been frozen.
Data.IR values of evaluation locations are read only AFTER the per-model
prediction buffers and SHA256 seal have been written on disk.
No measured audio, fitted coefficients, or derived HRIR distributed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from collections import defaultdict
import h5py
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import Train,Model,Unsupported,to_xyz,spherical,roles,metrics

D0="401089c3d5e25379b1a2c361d78a296092b5418b"
G0="bf8a5119032d9330afa2409669450e853e282987"
EXPECTED={1:"267819899fc548a95eed6c1fd687fc6e38aa492e55a38834431c23f7cf041b9f",
          9:"ac109e37c9bf2a8c278ee74ccf486ebe4b1e1d59d00a61ac1a2f6355384179f7"}
SEED=20261031
MODES=["B0","B1","B2"]+[
    f"{m}-o{o}-l{lam}" for m in ("B3","C3","C4")
    for o in (2,3,4) for lam in (0.03,0.10)]
RADIUS={"S1":{"train":[.20,.25,.30,.40,.50],"target":[.25,.50]},
        "S2":{"train":[.20,.50],"target":[.30,.40]}}


def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(2**20),b""):h.update(chunk)
    return h.hexdigest()


def text(x):
    if isinstance(x,bytes):return x.decode("utf-8","replace")
    if isinstance(x,np.ndarray):return text(x.item()) if x.size==1 else str(x)
    return str(x)


def inspect(path,subject):
    # This function opens NO acoustic values.
    digest=sha256(path)
    if subject in EXPECTED and digest!=EXPECTED[subject]:
        raise ValueError(f"ORIGINAL_HASH_MISMATCH subject={subject}")
    with h5py.File(path,"r") as f:
        if text(f.attrs.get("SOFAConventions",""))!="SimpleFreeFieldHRIR":
            raise ValueError("Unapproved SOFA convention")
        license_str=text(f.attrs.get("License",""))
        if license_str!="CC 3.0 BY-SA-NC":
            raise ValueError(f"Data license differs from G0: {license_str}")
        p=np.asarray(f["SourcePosition"][()],float)
        typ=text(f["SourcePosition"].attrs.get("Type","")).lower()
        units=text(f["SourcePosition"].attrs.get("Units","")).lower().replace(" ","")
        if typ!="spherical" or units not in ("degree,degree,metre","degree,degree,meter"):
            raise ValueError("Source coordinate units/type unverified")
        if p.shape!=(6048,3) or f["Data.IR"].shape!=(6048,2,512):
            raise ValueError("SCUT source geometry or measured IR shape changed")
        fs=np.asarray(f["Data.SamplingRate"][()]).ravel()
        if len(fs)!=1 or float(fs[0])!=96000:
            raise ValueError("Sampling rate inconsistent with G0")
        if "Data.Delay" not in f or np.any(f["Data.Delay"][()]!=0):
            raise ValueError("Nonzero/missing SOFA Data.Delay")
        xyz=to_xyz(p)
        o,blk=roles(xyz)
        if not all(abs(float(v)-r)<.001 for v in np.unique(np.round(p[:,2],3))
                   for r in [.2,.25,.3,.4,.5,.75,1.] if abs(v-r)<.001):
            pass
        shells=np.unique(np.round(p[:,2],3))
        if len(shells)!=7 or not np.allclose(shells,[.2,.25,.3,.4,.5,.75,1.]):
            raise ValueError("Unexpected radius shells")
        nblocks=len(set(map(tuple,blk)))
        if nblocks!=216:
            raise ValueError("Unexpected angular block count")
        # Sample and role geometry must match across ten fixed subjects.
        signature=hashlib.sha256(np.round(p,6).astype("<f8").tobytes()).hexdigest()
        return {"subject":subject,"sha256":digest,"source_geometry_sha256":signature,
                "xyz":xyz,"sph":p,"roles":o,"blocks":blk,"fs":float(fs[0]),
                "license":license_str,"reference_plane":"UNVERIFIED"}


def targets(meta,role,fold):
    """One geometry-only closest-to-block-center direction per (block,radius)."""
    pos=meta["sph"];blocks=meta["blocks"];o=meta["roles"]
    out=[]
    for radius in RADIUS[fold]["target"]:
        mask=(o==role)&(np.abs(pos[:,2]-radius)<.001)
        ids=np.flatnonzero(mask)
        keys=sorted(set(tuple(map(int,blocks[i])) for i in ids))
        for k in keys:
            ix=[int(i) for i in ids if tuple(map(int,blocks[i]))==k]
            center_a=np.deg2rad(k[0]*20+10)
            center_e=np.deg2rad(k[1]*10-30+5)
            def difficulty(i):
                a,e=np.deg2rad(pos[i,:2])
                cd=np.sin(center_e)*np.sin(e)+np.cos(center_e)*np.cos(e)*np.cos(a-center_a)
                return (round(float(np.arccos(np.clip(cd,-1,1))),12),
                        round(float(pos[i,0]),6),round(float(pos[i,1]),6),i)
            out.append({"index":min(ix,key=difficulty),"block":f"{k[0]}:{k[1]}",
                        "radius_m":radius,"fold":fold,"subject":meta["subject"]})
    return out


def train_from_original(path,meta,fold):
    if fold not in RADIUS:raise ValueError("Unknown fold")
    rset=RADIUS[fold]["train"]
    keep=(meta["roles"]=="train") & np.isin(np.round(meta["sph"][:,2],3),rset)
    indices=np.flatnonzero(keep)
    if len(indices)<200:raise Unsupported("Insufficient leak-free training positions")
    with h5py.File(path,"r") as f:
        ir=np.asarray(f["Data.IR"][indices,:,:],dtype=float)
    return Train(meta["xyz"][indices],ir,meta["fs"])


def model_for(train,name):
    if name in ("B0","B1","B2"):
        return Model(train,name)
    mode,order,lam=name.split("-")
    return Model(train,mode,order=int(order[1:]),lam=float(lam[1:]))


def all_predictions(path,meta,fold,role,names,seal_dir):
    """Seals ALL requested predicted HRIRs BEFORE any target acoustic truth read."""
    train=train_from_original(path,meta,fold)
    qs=targets(meta,role,fold)
    result={name:[] for name in names}
    hashers={name:hashlib.sha256() for name in names}
    for name in names:
        try:
            model=model_for(train,name)
        except (Unsupported,ValueError,np.linalg.LinAlgError) as exc:
            for _ in qs:result[name].append((None,{"refusal":str(exc)}))
            continue
        for q in qs:
            try:
                pred,info=model.predict(meta["xyz"][q["index"]])
                v=np.asarray(pred,dtype="<f8",order="C")
                hashers[name].update(v.tobytes())
                result[name].append((pred,info))
            except (Unsupported,ValueError,np.linalg.LinAlgError) as exc:
                hashers[name].update(("REFUSED:"+str(exc)).encode())
                result[name].append((None,{"refusal":str(exc)}))
    seal={"schema":"el-nf4.pretruth.v1","subject":meta["subject"],"fold":fold,
          "role":role,"original_sha256":meta["sha256"],
          "model_prediction_sha256":{name:h.hexdigest() for name,h in hashers.items()},
          "query_indices":[q["index"] for q in qs],
          "models":list(names),"source_geometry_sha256":meta["source_geometry_sha256"]}
    target=seal_dir/f"seal-{meta['subject']:04d}-{fold}-{role}.json"
    if target.exists():raise FileExistsError(target)
    target.write_text(json.dumps(seal,sort_keys=True,indent=2)+"\n")
    # Only now can held-out acoustic truths be indexed.
    ix=np.array(sorted(set(q["index"] for q in qs)),dtype=int)
    with h5py.File(path,"r") as f:
        truth=np.asarray(f["Data.IR"][ix,:,:],dtype=float)
    gt={int(i):truth[j] for j,i in enumerate(ix)}
    rows=[]
    for j,q in enumerate(qs):
        evidence={**q,"models":{}}
        for name in names:
            y,info=result[name][j]
            if y is None:
                evidence["models"][name]={"supported":False,"reason":info["refusal"]}
            else:
                try:
                    err=metrics(y,gt[q["index"]],meta["fs"])
                    evidence["models"][name]={"supported":True,"error":err,
                                              "nearest_train_m":info["nearest_train_m"]}
                except (Unsupported,ValueError) as exc:
                    evidence["models"][name]={"supported":False,"reason":str(exc)}
        rows.append(evidence)
    return rows,seal


def errors_on(rows,name,key):
    return [float(row["models"][name]["error"][key])
            for row in rows if row["models"][name]["supported"]]


def median(rows,name):
    vals=errors_on(rows,name,"ild_median_db")
    return float(np.median(vals)) if vals else float("inf")


def choose(dev_rows):
    # Baseline eligibility requires >=80% selection coverage in each S1/S2.
    bset=["B0","B1","B2"]+[x for x in MODES if x.startswith("B3")]
    def valid(name):
        return all(sum(x["models"][name]["supported"] for x in dev_rows if x["fold"]==fold) /
                   max(1,sum(x["fold"]==fold for x in dev_rows)) >= .80
                   for fold in RADIUS)
    baselines=[x for x in bset if valid(x)]
    if not baselines:raise Unsupported("No eligible baseline")
    baseline=min(baselines,key=lambda x:(median(dev_rows,x),bset.index(x)))
    candset=[x for x in MODES if x.startswith("C3") or x.startswith("C4")]
    candidates=[x for x in candset if valid(x)]
    if not candidates:raise Unsupported("No supported candidate")
    candidate=min(candidates,key=lambda x:(median(dev_rows,x),candset.index(x)))
    return baseline,candidate,{
        "baseline_eligible":baselines,
        "development_median_ild_db":{x:(median(dev_rows,x) if np.isfinite(median(dev_rows,x)) else None)
                                        for x in MODES}
    }


def calibrate(rows,candidate):
    out={}
    for fold in RADIUS:
        part=[x for x in rows if x["fold"]==fold]
        distances=sorted(x["models"][candidate]["nearest_train_m"]
                         for x in part if x["models"][candidate]["supported"])
        if not distances:out[fold]=None;continue
        # Calibration observations on independently measured heads are the
        # ONLY source of the operational 80th percentile difficulty cutoff.
        out[fold]=float(np.percentile(distances,80))
    return out


def accepted(rows,candidate,threshold):
    return [r for r in rows if r["models"][candidate]["supported"] and
            threshold.get(r["fold"]) is not None and
            r["models"][candidate]["nearest_train_m"]<=threshold[r["fold"]]]


def paired_ci(rows,baseline,candidate):
    keys=sorted(set((r["subject"],r["block"]) for r in rows))
    if len(keys)<8:return None
    rng=np.random.default_rng(SEED)
    groups={k:[r for r in rows if (r["subject"],r["block"])==k] for k in keys}
    diff=[]
    for _ in range(2000):
        subset=[r for n in rng.integers(0,len(keys),len(keys))
                for r in groups[keys[int(n)]]]
        diff.append(np.median(errors_on(subset,baseline,"ild_median_db"))-
                    np.median(errors_on(subset,candidate,"ild_median_db")))
    return [float(x) for x in np.percentile(diff,[2.5,97.5])]


def verdict(rows,baseline,candidate,threshold):
    subset=accepted(rows,candidate,threshold)
    matched=[r for r in subset if r["models"][baseline]["supported"]]
    total=len(rows)
    cov=len(subset)/total if total else 0
    bp=median(matched,baseline);cp=median(matched,candidate)
    ci=paired_ci(matched,baseline,candidate) if matched else None
    def metric(name,key):
        vals=errors_on(matched,name,key)
        return float(np.median(vals)) if vals else None
    def ild_p95(name):
        vals=[float(v) for r in matched for v in r["models"][name]["error"]["ild_bands_abs_db"]]
        return float(np.percentile(vals,95)) if vals else None
    byfold={f:[r for r in matched if r["fold"]==f] for f in RADIUS}
    blocks={f:len(set((r["subject"],r["block"]) for r in byfold[f])) for f in RADIUS}
    base_p95=ild_p95(baseline);cand_p95=ild_p95(candidate)
    itb,itc=metric(baseline,"itd_error_us"),metric(candidate,"itd_error_us")
    spb,spc=metric(baseline,"spectral_shape_rmse_db"),metric(candidate,"spectral_shape_rmse_db")
    gates={
        "coverage_ge_80pct":cov>=.8,
        "median_ILD_15pct_improvement":bool(np.isfinite(bp) and cp<=.85*bp),
        "paired_block_95ci_positive":bool(ci and ci[0]>0),
        "both_S1_S2_improve":all(median(byfold[f],candidate)<median(byfold[f],baseline) for f in RADIUS),
        "ITD_noninferior_plus_25us":bool(itc is not None and itb is not None and itc<=itb+25),
        "spectral_noninferior_plus_0p5db":bool(spc is not None and spb is not None and spc<=spb+.5),
        "ILD_p95_noninferior_plus_1db":bool(cand_p95 is not None and base_p95 is not None and cand_p95<=base_p95+1),
        "eight_independent_blocks_per_fold":all(v>=8 for v in blocks.values())
    }
    result="PASS_LIMITED_NUMERICAL_CANDIDATE" if all(gates.values()) else "REVISE_OR_REJECT"
    if not gates["eight_independent_blocks_per_fold"] or not np.isfinite(bp) or ci is None:
        result="INDETERMINATE"
    return {"G3":result,"final_count":total,"accepted_count":len(subset),
            "matched_accepted_count":len(matched),"coverage":cov,
            "baseline":baseline,"candidate":candidate,
            "baseline_ILD_median_db":bp if np.isfinite(bp) else None,
            "candidate_ILD_median_db":cp if np.isfinite(cp) else None,
            "CI95_baseline_minus_candidate_db":ci,
            "ILD_p95_baseline_db":base_p95,"ILD_p95_candidate_db":cand_p95,
            "ITD_baseline_us":itb,"ITD_candidate_us":itc,
            "spectral_baseline_db":spb,"spectral_candidate_db":spc,
            "accepted_blocks":blocks,"gates":gates}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists():raise FileExistsError("Do not overwrite measured results")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    seals=a.output.parent/"pretruth_seals"
    seals.mkdir(exist_ok=False)
    source={i:a.input_dir/f"SCUT_NF_subject{i:04d}_measured.sofa" for i in range(1,11)}
    metadata={i:inspect(p,i) for i,p in source.items()}
    signatures={v["source_geometry_sha256"] for v in metadata.values()}
    if len(signatures)!=1:raise ValueError("Cross-subject original SOFA geometry differs")
    dev=[]
    for i in range(1,7):
        for f in RADIUS:
            rows,_=all_predictions(source[i],metadata[i],f,"selection",MODES,seals)
            dev.extend(rows)
    baseline,candidate,diagnostics=choose(dev)
    cal=[]
    for i in (7,8):
        for f in RADIUS:
            rows,_=all_predictions(source[i],metadata[i],f,"calibration",[baseline,candidate],seals)
            cal.extend(rows)
    cutoff=calibrate(cal,candidate)
    final=[]
    for i in (9,10):
        for f in RADIUS:
            rows,_=all_predictions(source[i],metadata[i],f,"final",[baseline,candidate,"B0"],seals)
            final.extend(rows)
    science=verdict(final,baseline,candidate,cutoff)
    # All rows only carry non-reconstructive numerical errors, never raw IR.
    evidence={"schema":"el-nf4.measured-relative.v1","stage":"RESEARCH_ONLY",
       "claims":"EXPLORATORY_RELATIVE_MEASURED_HRIR_ONLY_NOT_PHYSICAL_EARDRUM_OR_COMMERCIAL",
       "d0_sha":D0,"g0_v11_sha":G0,"subject_roles":{"development":list(range(1,7)),
       "calibration":[7,8],"final":[9,10]},
       "source_records":[{"subject":i,"sha256":metadata[i]["sha256"],
         "license":metadata[i]["license"],"reference_plane":metadata[i]["reference_plane"]}
         for i in range(1,11)],
       "geometry_sha256":next(iter(signatures)),
       "model_choice":diagnostics,"calibration_distance_threshold_m":cutoff,
       "pretruth_seals":[{"name":p.name,"sha256":sha256(p)}
                          for p in sorted(seals.glob("*.json"))],
       "final_scored_rows":final,"science":science,
       "independent_science_review":"PENDING",
       "license":"NONCOMMERCIAL_SCUT_EMBEDDED_CC_3_0_BY_SA_NC_NO_REDISTRIBUTION",
       "receiver_plane":"UNVERIFIED",
       "production_adoption":"NOT_ADOPTED"}
    a.output.write_text(json.dumps(evidence,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"science":science,"source_hashes":[v["sha256"] for v in metadata.values()],
                      "evidence":str(a.output)},indent=2,allow_nan=False))


if __name__=="__main__":main()
