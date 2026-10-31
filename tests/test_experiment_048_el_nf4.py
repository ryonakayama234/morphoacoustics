"""Deterministic synthetic numerical/negative checks; NOT measured human proof."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
import pytest

p=Path(__file__).resolve().parents[1]/"experiments/048_el_nf4_receiver/model.py"
spec=importlib.util.spec_from_file_location("el_nf4_model",p)
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)


def sample(n=120):
    az=np.arange(n,dtype=float)*360/n
    el=np.resize(np.array([-20,-10,0,10,20],float),n)
    radius=np.resize(np.array([.20,.25,.30,.40,.50]),n)
    pos=m.to_xyz(np.column_stack((az,el,radius)))
    ir=np.zeros((n,2,512))
    for i,(a,e,r) in enumerate(zip(az,el,radius)):
        for ear in range(2):
            tau=60+(ear*6-3)*np.sin(np.radians(a))
            amp=(1+(2*ear-1)*.2*np.cos(np.radians(a)))/r
            t=np.arange(512)
            ir[i,ear]=amp*np.exp(-.5*((t-tau)/2.)**2)
    return m.Train(pos,ir,48000)


def test_seam_and_real_sh():
    x=m.to_xyz([[0,0,.3],[360,0,.3],[90,30,.5]])
    assert np.allclose(x[0],x[1])
    y=m.real_sh(m.spherical(x),3)
    assert y.shape==(3,16)
    assert np.allclose(y[0],y[1])


@pytest.mark.parametrize("mode",["B0","B1","B3","C3","C4"])
def test_models_on_synthetic(mode):
    d=sample()
    x=m.Model(d,mode,order=3,lam=.1)
    out,meta=x.predict(m.to_xyz([[40,0,.3]])[0])
    assert out.shape==(2,512)
    assert np.isfinite(out).all()
    assert meta["model"]==mode
    assert np.isfinite(m.band_ild(out,d.fs)).all()


def test_hard_refusal_no_silent_extrapolation():
    d=sample()
    x=m.Model(d,"C3")
    with pytest.raises(m.Unsupported,match="radial"):
        x.predict(m.to_xyz([[0,0,.6]])[0])
    with pytest.raises(m.Unsupported,match="elevation"):
        x.predict(m.to_xyz([[0,85,.3]])[0])
    with pytest.raises(m.Unsupported,match="Invalid"):
        x.predict(np.array([np.nan,0,.3]))


def test_duplicate_and_zero_energy_are_invalid():
    d=sample()
    with pytest.raises(ValueError,match="Duplicate"):
        m.Train(np.vstack((d.xyz,d.xyz[0])),np.concatenate((d.ir,d.ir[:1])),d.fs)
    ir=d.ir.copy();ir[1,0]=0
    with pytest.raises(ValueError,match="Zero"):
        m.Train(d.xyz,ir,d.fs)


def test_metrics_identity_and_gain_invariant():
    d=sample(50);h=d.ir[20]
    result=m.metrics(h,h,d.fs)
    assert result["ild_median_db"]==pytest.approx(0,abs=1e-10)
    assert result["itd_error_us"]==0
    assert result["spectral_shape_rmse_db"]==pytest.approx(0,abs=1e-10)
    assert np.allclose(m.band_ild(h,d.fs),m.band_ild(h*3,d.fs))


def test_role_allocation_is_geometry_only_and_stable():
    xyz=m.to_xyz([[a,e,.3] for a in np.arange(0,360,10)
                               for e in [-20,-10,0,10,20,30]])
    one,blocks=m.roles(xyz)
    two,blocks2=m.roles(xyz)
    assert np.array_equal(one,two)
    assert np.array_equal(blocks,blocks2)
    assert "final" in one
    assert set(one)<=set(("train","selection","calibration","final","buffer"))


def test_fir_shift_is_not_periodic():
    x=np.zeros(64);x[12]=1
    assert np.argmax(m.shift(x,5))==17
    assert np.count_nonzero(m.shift(x,-30))==0
