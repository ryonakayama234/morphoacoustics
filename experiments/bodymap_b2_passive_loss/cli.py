"""Explicit engineering gate; no run-study default or scientific evaluation mode."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
from .prereg_binding import (Refusal,require,PREREG_CONTENT_SHA256,
                              PLAN_CONTENT_SHA256)

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
LOCK=ROOT/"requirements"/"bodymap-b2-physical-py311.lock.txt"
CASES=HERE/"fixtures"/"engineering-cases-v1.json"

def gate(review_receipt:Path|None)->dict:
    require(sys.version_info[:2]==(3,11),"DEPENDENCY_LOCK_UNRESOLVED",
            "requires exact Python 3.11 patch")
    require(LOCK.is_file() and LOCK.stat().st_size>0,
            "DEPENDENCY_LOCK_UNRESOLVED","no reviewer-frozen hashed wheel closure")
    require(review_receipt is not None and review_receipt.is_file(),
            "REVIEWER_UNRESOLVED","independent oracle/lock receipt absent")
    rc=json.loads(review_receipt.read_text(encoding="utf-8"))
    require(rc.get("reviewer_signoff") is True
            and rc.get("lock_sha256")==hashlib.sha256(LOCK.read_bytes()).hexdigest()
            and rc.get("candidate_author") and rc.get("oracle_author")
            and rc.get("candidate_commit_sha") and rc.get("oracle_commit_sha")
            and rc["candidate_commit_sha"]!=rc["oracle_commit_sha"],
            "REVIEWER_UNRESOLVED","independent author/commit/lock record absent")
    import numpy,scipy,mpmath
    require(numpy.__version__=="2.4.6"
            and rc.get("python_patch")==platform.python_version()
            and rc.get("numpy")==numpy.__version__
            and rc.get("scipy")==scipy.__version__
            and rc.get("mpmath")==mpmath.__version__,
            "DEPENDENCY_LOCK_UNRESOLVED","runtime not reviewer-locked")
    manifest=json.loads(CASES.read_text())
    require(manifest.get("engineering_only") is True
            and manifest.get("study_evaluations_authorized")==0
            and len(manifest.get("cases",[]))==8
            and manifest.get("max_separate_process_repeats")==1
            and manifest.get("plan_content_sha256")==PLAN_CONTENT_SHA256
            and manifest.get("prereg_content_sha256")==PREREG_CONTENT_SHA256,
            "INVALID_FIXTURE","engineering manifest changed")
    return {"lock_sha256":rc["lock_sha256"],
            "case_manifest_sha256":hashlib.sha256(CASES.read_bytes()).hexdigest(),
            "engineering_only":True,"study_runs":0}

def main()->int:
    p=argparse.ArgumentParser(description="B2 research engineering, no study mode")
    p.add_argument("operation",choices=("preflight","verify-engineering"))
    p.add_argument("--reviewer-receipt",type=Path)
    a=p.parse_args()
    try:
        result=gate(a.reviewer_receipt)
        if a.operation=="verify-engineering":
            raise Refusal("REVIEWER_UNRESOLVED",
                          "reviewer oracle runner and end-to-end acceptance not yet integrated")
        print(json.dumps({"status":"PREFLIGHT_ONLY",**result},sort_keys=True))
        return 0
    except Refusal as exc:
        print(json.dumps({"status":"STOP","code":exc.code,"message":str(exc),
                          "scientific_runs":0},sort_keys=True))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
