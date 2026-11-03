#!/usr/bin/env python3
"""Research evidence auditor: recompute gates without importing predictor/runner.
Independence is arithmetic-only; distinct human scientist still required.
"""
import argparse
import json
from pathlib import Path
import numpy as np


def verify(e):
    assert e["schema"]=="el-nf4.measured-relative.v1"
    assert e["d0_sha"]=="401089c3d5e25379b1a2c361d78a296092b5418b"
    assert e["g0_v11_sha"]=="bf8a5119032d9330afa2409669450e853e282987"
    assert e["production_adoption"]=="NOT_ADOPTED"
    assert e["receiver_plane"]=="UNVERIFIED"
    assert len(e["source_records"])==10
    assert len(e["pretruth_seals"])==20
    assert "CC_3_0_BY_SA_NC" in e["license"]
    rows=e["final_scored_rows"]
    science=e["science"]
    candidate=science["candidate"];baseline=science["baseline"]
    assert all("hrir" not in k.lower() and "coeff" not in k.lower()
               for row in rows for k in row)
    assert len(rows)==science["final_count"]
    threshold=e["calibration_distance_threshold_m"]
    selection=[]
    for row in rows:
        m=row["models"][candidate]
        if (m["supported"] and threshold[row["fold"]] is not None
                and m["nearest_train_m"]<=threshold[row["fold"]]):
            selection.append(row)
    assert len(selection)==science["accepted_count"]
    matched=[x for x in selection if x["models"][baseline]["supported"]]
    assert len(matched)==science["matched_accepted_count"]
    assert np.isclose(len(selection)/len(rows),science["coverage"])
    def vals(name,key):
        return [x["models"][name]["error"][key] for x in matched]
    def median(name,key):
        v=vals(name,key)
        return float(np.median(v)) if v else None
    assert np.isclose(median(candidate,"ild_median_db"),science["candidate_ILD_median_db"])
    assert np.isclose(median(baseline,"ild_median_db"),science["baseline_ILD_median_db"])
    assert np.isclose(median(candidate,"itd_error_us"),science["ITD_candidate_us"])
    assert np.isclose(median(baseline,"itd_error_us"),science["ITD_baseline_us"])
    assert np.isclose(median(candidate,"spectral_shape_rmse_db"),science["spectral_candidate_db"])
    assert np.isclose(median(baseline,"spectral_shape_rmse_db"),science["spectral_baseline_db"])
    for name,key in ((candidate,"ILD_p95_candidate_db"),(baseline,"ILD_p95_baseline_db")):
        allbands=[v for x in matched for v in x["models"][name]["error"]["ild_bands_abs_db"]]
        assert np.isclose(np.percentile(allbands,95),science[key])
    blocks={f:len({(x["subject"],x["block"]) for x in matched if x["fold"]==f})
            for f in ("S1","S2")}
    assert blocks==science["accepted_blocks"]
    keys=sorted(set((x["subject"],x["block"]) for x in matched))
    if len(keys)>=8:
        grouping={k:[x for x in matched if (x["subject"],x["block"])==k] for k in keys}
        rng=np.random.default_rng(20261031)
        values=[]
        for _ in range(2000):
            sample=[x for k in rng.integers(0,len(keys),len(keys))
                    for x in grouping[keys[int(k)]]]
            values.append(np.median([x["models"][baseline]["error"]["ild_median_db"] for x in sample])-
                          np.median([x["models"][candidate]["error"]["ild_median_db"] for x in sample]))
        recomputed=list(map(float,np.percentile(values,[2.5,97.5])))
        assert np.allclose(recomputed,science["CI95_baseline_minus_candidate_db"])
    # Independent boolean logic recomputation.
    gates=science["gates"]
    assert gates["coverage_ge_80pct"]==(science["coverage"]>=.8)
    b=science["baseline_ILD_median_db"];c=science["candidate_ILD_median_db"]
    assert gates["median_ILD_15pct_improvement"]==(c<=.85*b)
    ci=science["CI95_baseline_minus_candidate_db"]
    assert gates["paired_block_95ci_positive"]==bool(ci and ci[0]>0)
    assert gates["eight_independent_blocks_per_fold"]==all(v>=8 for v in blocks.values())
    assert (science["G3"]=="PASS_LIMITED_NUMERICAL_CANDIDATE")==all(gates.values())
    return {"status":"PASS_ARITHMETIC_ONLY","final_rows":len(rows),
            "matched":len(matched),"coverage":science["coverage"],
            "science_verdict":science["G3"],
            "independent_human_review":"NOT_PERFORMED"}


def main():
    a=argparse.ArgumentParser();a.add_argument("--evidence",type=Path,required=True)
    args=a.parse_args()
    d=json.loads(args.evidence.read_text())
    print(json.dumps(verify(d),sort_keys=True))


if __name__=="__main__":main()
