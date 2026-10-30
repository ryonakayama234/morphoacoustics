"""Independent arithmetic audit tests and mutation refusal."""
import importlib.util
from pathlib import Path
import sys
import copy

import numpy as np
import pytest

pytest.importorskip("numpy")
ROOT=Path(__file__).resolve().parents[1]
file=ROOT/"experiments/047_el_nf3_receiver/audit.py"
spec=importlib.util.spec_from_file_location("el_nf3_audit",file)
audit=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=audit
spec.loader.exec_module(audit)


def make_evidence():
    rows=[]
    for j in range(10):
        for fold in ("S1","S2"):
            models={}
            for m in audit.METHODS:
                models[m]={"supported":True,
                           "ild_error_db":[2. if m=="B0" else 1. for _ in range(4)],
                           "itd_error_us":10.,
                           "spectral_rmse_db":2.,
                           "geometry":{"angular_span_deg":10.,"radial_gap_m":0.}}
            rows.append({"fold":fold,"index":j*2+(fold=="S2"),"block":str(j),"models":models})
    return {"schema_version":"el-nf3-evidence/v1","research_only":True,
        "prereg_commit":"df6addb58296e9945569ff3473aa65039ef959cb",
        "audit":{"sha256":"a"*64},
        "experiment":{"final_rows":rows,"baseline":"B0",
            "calibration_geometry_threshold":15.,
            "accepted_queries":20,"final_evaluated_queries":20,
            "accepted_coverage":1.,
            "matched_baseline_ild_median_db":2.,
            "matched_C2_ild_median_db":1.,
            "gates":{"eight_blocks_each":True},
            "numerical_verdict":"PASS_LIMITED_NUMERIC",
            "science_adoption":"NOT_ADOPTED"}}


def test_audit_true_and_mutations():
    e=make_evidence()
    assert audit.check_evidence(e)["valid"]
    for path,new in (("accepted_queries",19),
                     ("matched_C2_ild_median_db",0.5),
                     ("final_evaluated_queries",30)):
        broken=copy.deepcopy(e);broken["experiment"][path]=new
        with pytest.raises(ValueError):
            audit.check_evidence(broken)
    forged=copy.deepcopy(e)
    forged["experiment"]["final_rows"][0]["models"]["C2"]["ild_error_db"][0]=-2
    with pytest.raises(ValueError):
        audit.check_evidence(forged)
    wrong=copy.deepcopy(e)
    wrong["experiment"]["science_adoption"]="ADOPTED"
    with pytest.raises(ValueError):
        audit.check_evidence(wrong)


def test_reject_duplicate_and_nonfinite():
    e=make_evidence()
    e["experiment"]["final_rows"][1]["index"]=0
    e["experiment"]["final_rows"][1]["fold"]="S1"
    with pytest.raises(ValueError):
        audit.check_evidence(e)
    e=make_evidence()
    e["experiment"]["final_rows"][0]["models"]["C2"]["itd_error_us"]=float("nan")
    with pytest.raises(ValueError):
        audit.check_evidence(e)
