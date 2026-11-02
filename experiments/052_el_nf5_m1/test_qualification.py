"""Synthetic-only unit and model-contract negative controls."""
import importlib.util
import math
from pathlib import Path
import numpy as np
import pytest
pytest.importorskip("h5py")

sp=importlib.util.spec_from_file_location("nf5_m1",Path(__file__).with_name("qualification.py"))
q=importlib.util.module_from_spec(sp)
sp.loader.exec_module(q)

def fixture():
    i=np.arange(2702)
    az=(i*137.50776405)%360
    el=np.rad2deg(np.arcsin(-1+2*(i+.5)/2702))
    return np.stack([az,el,np.full(2702,.75)],axis=1)

def test_original_hash_refusal():
    with pytest.raises(q.GateError,match="HASH"):
        q.inspect_original(b"this is not the source")

def test_wrap_and_roles():
    x=fixture()
    x[0]=[-20,0,.75];x[1]=[340.01,0,.75]
    v,c=q.normalize_source(x,.75)
    assert np.array_equal(c[0],c[1])
    assert np.isfinite(v).all()
    assert q.role(c[0])==q.role(c[1])

def test_duplicate_refusal():
    x=fixture();x[1]=x[0]
    with pytest.raises(q.GateError,match="DUPLICATE"):
        q.normalize_source(x,.75)

def test_radius_refusal():
    x=fixture();x[1,2]=.1
    with pytest.raises(q.GateError,match="radius"):
        q.normalize_source(x,.75)

def test_nonfinite_refusal():
    x=fixture();x[4,1]=np.nan
    with pytest.raises(q.GateError,match="finite"):
        q.normalize_source(x,.75)

def test_buffer_and_radial_split():
    v,c=q.normalize_source(fixture(),.75)
    result=q.partition(v,c)
    assert result["angular_block_counts"]["final"]>=8
    assert result["fit_removed_by_buffer"]>0
    assert result["s1"]["final_radius_m"] in result["s1"]["training_radii_m"]
    assert result["s2"]["final_radius_m"] not in result["s2"]["training_radii_m"]
    assert .75<result["s2"]["final_radius_m"]<1.5

def test_manifest_determinism():
    v,c=q.normalize_source(fixture(),.75)
    assert q.partition(v,c)==q.partition(v,c)

def test_log_magnitude_factorization_roundtrip():
    a,b=np.log(np.array([.4,.9,1.2])),np.log(np.array([.2,.5,1.8]))
    m,l=(a+b)/2,a-b
    np.testing.assert_allclose(m+l/2,a,atol=1e-14)
    np.testing.assert_allclose(m-l/2,b,atol=1e-14)

def test_same_linear_interpolator_has_no_magical_improvement():
    rng=np.random.default_rng(3)
    a,b=rng.normal(size=(2,7));w=rng.random(7);w/=w.sum()
    m,l=(a+b)/2,a-b
    assert np.isclose(w@(m+l/2),w@a,atol=1e-14)
    assert np.isclose(w@(m-l/2),w@b,atol=1e-14)

def test_bilateral_gain_and_swap():
    a,b=np.array([2.,1.,3.]),np.array([1.,3.,2.])
    ild=lambda l,r:10*np.log10(np.sum(l*l)/np.sum(r*r))
    assert math.isclose(ild(a,b),ild(7*a,7*b),abs_tol=1e-12)
    assert math.isclose(ild(a,b),-ild(b,a),abs_tol=1e-12)
    assert not math.isclose(ild(a,b),ild(2*a,b),abs_tol=1e-6)

def test_signed_interaural_lag_common_shift():
    l=np.zeros(100);r=np.zeros(100)
    l[40]=1;r[44]=1
    assert np.argmax(r)-np.argmax(l)==4
    assert (np.argmax(r)+3)-(np.argmax(l)+3)==4
    assert (np.argmax(r)+2)-np.argmax(l)!=4

def test_no_raw_acoustic_original_read_in_qualifier():
    src=Path(__file__).with_name("qualification.py").read_text()
    assert 'h["Data.IR"][()]' not in src
    assert 'h["Data.IR"][:]' not in src
    assert 'h["Data.Delay"][()]' not in src
    assert 'h["Data.Delay"][:]' not in src
