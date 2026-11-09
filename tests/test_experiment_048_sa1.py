"""SA-1 fast tests: preregistered oracle and exact JET source replay."""
import hashlib
import runpy
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
M=runpy.run_path(str(ROOT/"experiments/048_source_acoustic_port_audit/run.py"))

def test_independent_matched_tube_oracle():
    d=M["matched_oracle"]()
    assert d["flow_complex_abs_error"]<1e-10
    assert d["zin_relative_error"]<1e-10

@pytest.mark.parametrize("name",("noise_off","modal","breathy_gap","pressure_x2"))
def test_all_four_exact_historic_source_digests(name):
    s,mean,noise=M["replay_source"](*M["CASES"][name])
    assert s.shape==(24000,)
    assert np.all(np.isfinite(s))
    assert np.array_equal(s,mean+noise)
    assert hashlib.sha256(M["npy"](s)).hexdigest()==M["OLD_SOURCE_SHA"][name]

def test_zero_pressure_zero_flow_noise_even_if_leak():
    s,mean,noise=M["replay_source"](0.,1e-7,.02)
    assert not np.any(s) and not np.any(mean) and not np.any(noise)

def test_pressure_doubles_bernoulli_ratio_sqrt2():
    _,m1,_=M["replay_source"](800.,0.,0.)
    _,m2,_=M["replay_source"](1600.,0.,0.)
    assert np.allclose(m2,m1*np.sqrt(2.),rtol=2e-15,atol=0.)

def test_zero_noise_null_and_nonzero_candidate():
    a,m,z=M["replay_source"](800.,0.,0.)
    b,_,v=M["replay_source"](800.,0.,.02)
    assert np.array_equal(a,m) and not np.any(z)
    assert np.any(v) and not np.array_equal(a,b)

def test_source_input_validation():
    for x in ((-1.,0.,0.),(800.,-1e-8,0.),(800.,0.,float("nan"))):
        with pytest.raises(ValueError):M["replay_source"](*x)

def test_complex_transfer_artifact_preserves_phase():
    x=np.array([1+2j,-3-4j],dtype=np.complex128)
    import io
    y=np.load(io.BytesIO(M["npy"](x)),allow_pickle=False)
    assert np.array_equal(x,y) and y.dtype==np.complex128
