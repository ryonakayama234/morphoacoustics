"""Mutation regressions for independent numerical evidence audit."""
import copy
import importlib.util
import sys
from pathlib import Path
import pytest
from test_experiment_045_el_nf1 import synthetic,nf

SRC=Path(__file__).resolve().parents[1]/'experiments/045_el_nf1_receiver/audit.py'
spec=importlib.util.spec_from_file_location('el_nf1_audit',SRC)
audit=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=audit
spec.loader.exec_module(audit)

@pytest.fixture(scope='module')
def sample(tmp_path_factory):
    p=tmp_path_factory.mktemp('el-nf1-audit')/'synthetic.sofa'
    synthetic(p)
    return nf.score(nf.load_sofa(p,require_original=False))

def test_independent_arithmetic_and_holdout_reconstruction(sample):
    assert audit.check(sample)['audit']=='EVIDENCE_ARITHMETIC_VERIFIED_ONLY'

def test_forged_summary_is_rejected(sample):
    v=copy.deepcopy(sample)
    v['statistics']['C1']['median_ild_error_db']=0.
    with pytest.raises(ValueError,match='summary'):audit.check(v)

def test_target_leakage_is_rejected(sample):
    v=copy.deepcopy(sample)
    v['records'][0]['training_measurement_indices'][0]=v['records'][0]['target_measurement_index']
    with pytest.raises(ValueError,match='leakage'):audit.check(v)

def test_forged_verdict_and_nonfinite_error_are_rejected(sample):
    v=copy.deepcopy(sample)
    v['numerical_verdict']='FORGED_PASS'
    with pytest.raises(ValueError,match='verdict'):audit.check(v)
    v=copy.deepcopy(sample)
    v['records'][4]['absolute_ild_errors_db'][0]=float('nan')
    with pytest.raises(ValueError,match='finite'):audit.check(v)
