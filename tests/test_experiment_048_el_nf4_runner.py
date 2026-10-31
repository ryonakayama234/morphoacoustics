"""EL-NF4 heldout protocol tests: explicit prevention of role misuse."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
import pytest

p=Path(__file__).resolve().parents[1]/"experiments/048_el_nf4_receiver/run.py"
spec=importlib.util.spec_from_file_location("el_nf4_run",p)
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)


def make_row(subject,fold,block,d):
    def model(ild,supported=True):
        return {"supported":supported,"nearest_train_m":d,
                "error":{"ild_median_db":ild,"ild_bands_abs_db":[ild]*4,
                         "itd_error_us":10.,"spectral_shape_rmse_db":1.}}
    allmodels={name:{"supported":False,"reason":"test not selected"} for name in m.MODES}
    allmodels.update({"B0":model(1.),"C3-o3-l0.1":model(.6)})
    return {"subject":subject,"fold":fold,"block":block,"models":allmodels}


def test_model_selection_and_acceptance_without_final():
    a=[make_row(1,f,str(i),.01+i*.0001) for f in ("S1","S2") for i in range(12)]
    base,candidate,diag=m.choose(a)
    assert base=="B0"
    assert candidate=="C3-o3-l0.1"
    assert diag["baseline_eligible"][0]=="B0"
    cut=m.calibrate(a,candidate)
    assert len(m.accepted(a,candidate,cut))>=16
    assert len(m.accepted(a,candidate,cut))<len(a)


def test_ci_reproducibility_and_negative_gates():
    a=[make_row(9,f,str(i),.01) for f in ("S1","S2") for i in range(14)]
    ci=m.paired_ci(a,"B0","C3-o3-l0.1")
    assert ci[0]>0
    gate=m.verdict(a,"B0","C3-o3-l0.1",{"S1":.02,"S2":.02})
    assert gate["G3"]=="PASS_LIMITED_NUMERICAL_CANDIDATE"
    assert gate["coverage"]==1.


def test_zero_coverage_cannot_be_pass():
    a=[make_row(9,f,str(i),.3) for f in ("S1","S2") for i in range(14)]
    gate=m.verdict(a,"B0","C3-o3-l0.1",{"S1":.01,"S2":.01})
    assert gate["G3"]=="INDETERMINATE"
    assert gate["accepted_count"]==0
