#!/usr/bin/env python3
"""EL-NF3 independent-from-predictor evidence arithmetic and tamper checks.

Not an independent scientist or new raw-SOFA reanalysis.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np

METHODS=("B0","B1","B2","C1","C2")


def _unique_pairs(pairs):
    if len(pairs)!=len(set(pairs)):
        raise ValueError("Duplicate final query identity")


def check_evidence(e):
    if e.get("schema_version")!="el-nf3-evidence/v1" or not e.get("research_only"):
        raise ValueError("Wrong evidence schema or adoption flag")
    if e.get("prereg_commit")!="df6addb58296e9945569ff3473aa65039ef959cb":
        raise ValueError("Preregistration provenance changed")
    audit=e.get("audit",{})
    if not isinstance(audit.get("sha256"),str) or len(audit["sha256"])!=64:
        raise ValueError("Missing original source SHA-256")
    exp=e.get("experiment",{})
    rows=exp.get("final_rows",[])
    if not rows:
        raise ValueError("No final measured rows")
    _unique_pairs([(r.get("fold"),r.get("index")) for r in rows])
    if not all(r.get("fold") in ("S1","S2") for r in rows):
        raise ValueError("Nonpreregistered fold")
    for r in rows:
        if set(r["models"])!=set(METHODS):
            raise ValueError("Missing model in final row")
        if r.get("index") is None or r.get("block") is None:
            raise ValueError("Missing heldout identity")
        for m,v in r["models"].items():
            if v["supported"]:
                if len(v.get("ild_error_db",[]))!=4 or not all(
                    math.isfinite(float(x)) and float(x)>=0 for x in v["ild_error_db"]):
                    raise ValueError("Invalid band errors")
                for k in ("itd_error_us","spectral_rmse_db"):
                    if not math.isfinite(float(v[k])) or v[k]<0:
                        raise ValueError("Invalid diagnostics")
            elif not v.get("reason"):
                raise ValueError("Refusal lacks reason")
    baseline=exp.get("baseline")
    if baseline not in METHODS[:-1] and baseline is not None:
        raise ValueError("Unregistered baseline")
    threshold=exp.get("calibration_geometry_threshold")
    accepted=[]
    if baseline is not None and threshold is not None:
        for row in rows:
            g=row["models"]["C2"]
            if not g["supported"] or not row["models"][baseline]["supported"]:
                continue
            feature=g["geometry"]["angular_span_deg"]+5*g["geometry"]["radial_gap_m"]
            if feature<=threshold:
                accepted.append(row)
    if len(accepted)!=exp.get("accepted_queries"):
        raise ValueError("Forged accepted count")
    if len(rows)!=exp.get("final_evaluated_queries"):
        raise ValueError("Forged final record count")
    if not math.isclose(len(accepted)/len(rows),exp["accepted_coverage"],abs_tol=1e-10):
        raise ValueError("Forged coverage")
    def median(model):
        vals=[x for row in accepted for x in row["models"][model]["ild_error_db"]]
        return float(np.median(vals)) if vals else None
    for method,name in ((baseline,"matched_baseline_ild_median_db"),
                        ("C2","matched_C2_ild_median_db")):
        actual=median(method) if method else None
        claimed=exp[name]
        if (actual is None)!=(claimed is None) or (actual is not None and
            not math.isclose(actual,claimed,abs_tol=1e-8)):
            raise ValueError("Forged pooled ILD median: "+name)
    blocks={r["block"] for r in accepted}
    if exp["gates"]["eight_blocks_each"]!=all(
        len({r["block"] for r in accepted if r["fold"]==f})>=8
        for f in ("S1","S2")):
        raise ValueError("Forged independent-block gate")
    if e.get("science_adoption")=="ADOPTED" or exp.get("science_adoption")!="NOT_ADOPTED":
        raise ValueError("Illegal science adoption")
    return {"valid":True,"final_rows":len(rows),"accepted":len(accepted),
            "accepted_independent_blocks":len(blocks),"baseline":baseline,
            "source_sha256":audit["sha256"],
            "numeric_verdict":exp["numerical_verdict"],
            "science_adoption":exp["science_adoption"]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--evidence",required=True)
    args=p.parse_args()
    with Path(args.evidence).open(encoding="utf-8") as stream:
        record=json.load(stream,parse_constant=lambda value:(_ for _ in ()).throw(
            ValueError("Nonfinite JSON constant: "+value)))
    print(json.dumps(check_evidence(record),indent=2))

if __name__=="__main__":
    main()
