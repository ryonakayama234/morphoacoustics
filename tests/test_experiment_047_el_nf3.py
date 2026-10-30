"""Synthetic-only tests: never pass these as measured EL-NF3 scientific proof."""
import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

pytest.importorskip("scipy")
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "el_nf3_model", ROOT / "experiments/047_el_nf3_receiver/model.py"
)
model = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = model
SPEC.loader.exec_module(model)


def make_fixture():
    # 5 x 3 azimuth/elevation sampling, at two known radius shells.
    pts, irs = [], []
    fs, samples = 48000, 256
    for radius in (.2,.5):
        for az in (0,20,40,60,80):
            for el in (-10,0,10):
                xyz = model.spherical_to_xyz([[az,el,radius]])[0]
                h = np.zeros((2,samples))
                # Synthetic free-field-like arrival, not biological validation.
                base = 8 + round(radius * fs/343)
                for ear, direction in ((0,-1),(1,1)):
                    shift = round(direction * np.sin(np.deg2rad(az)) * 5)
                    h[ear,base+shift] = 1 / radius * (1+.08*direction*np.sin(np.deg2rad(az)))
                pts.append(xyz)
                irs.append(h)
    return model.HeadData(np.array(pts),np.array(irs),fs)


def test_xyz_roundtrip():
    p = np.array([[15,-9,.4],[355,20,.3]])
    xyz = model.spherical_to_xyz(p)
    np.testing.assert_allclose(model.xyz_to_spherical(xyz),p,atol=1e-10)


def test_all_models_predict_finite_two_ear():
    d=make_fixture()
    q=model.spherical_to_xyz([[30,3,.3]])[0]
    for algorithm in ("B0","B1","B2","C1","C2","C2A","C2B","C2C"):
        pred, meta=model.Predictor(d,np.arange(len(d.xyz)),algorithm).predict(q)
        assert pred.shape==(2,256) and np.all(np.isfinite(pred))
        assert np.any(pred) and meta["method"]==algorithm


def test_c2_rejects_extrapolation_and_degenerate_missing_shell():
    d=make_fixture()
    p=model.Predictor(d,np.arange(len(d.xyz)),"C2")
    for bad in (model.spherical_to_xyz([[150,0,.3]])[0],
                model.spherical_to_xyz([[30,5,.15]])[0],
                model.spherical_to_xyz([[30,50,.3]])[0]):
        with pytest.raises(model.Unsupported):
            p.predict(bad)
    with pytest.raises(model.Unsupported):
        model.Predictor(d,np.arange(15),"C2").predict(model.spherical_to_xyz([[30,3,.3]])[0])


def test_heldout_truth_mutation_cannot_change_prediction():
    d=make_fixture()
    train=np.arange(len(d.xyz)-1)
    last=len(d.xyz)-1
    q=model.spherical_to_xyz([[35,2,.3]])[0]
    before,_=model.Predictor(d,train,"C2").predict(q)
    altered=d.ir.copy()
    altered[last] *= 100
    d2=model.HeadData(d.xyz,altered,d.fs)
    after,_=model.Predictor(d2,train,"C2").predict(q)
    np.testing.assert_allclose(before,after,atol=0)


def test_band_metric_zero_and_nonfinite_refusal():
    d=make_fixture()
    h=d.ir[0]
    np.testing.assert_allclose(model.band_ild_error(h,h,d.fs),np.zeros(4),atol=1e-12)
    with pytest.raises(model.Unsupported):
        model.band_ild(np.zeros_like(h),d.fs)
    broken=d.ir.copy(); broken[1,0,10]=np.nan
    with pytest.raises(ValueError):
        model.HeadData(d.xyz,broken,d.fs)


def test_deterministic_angular_splits_and_buffers():
    pts=model.spherical_to_xyz([[az,el,.25] for az in range(0,360,10)
                                  for el in (-20,-10,0,10,20,30)])
    roles1,bins1=model.block_roles(pts)
    roles2,bins2=model.block_roles(pts)
    np.testing.assert_array_equal(roles1,roles2)
    np.testing.assert_array_equal(bins1,bins2)
    assert "train" in roles1 and "final" in roles1
    assert model.deterministic_split_hash(pts,roles1)==model.deterministic_split_hash(pts,roles2)


def test_sofa_integrity_and_nonzero_delay(tmp_path):
    h5py=pytest.importorskip("h5py")
    d=make_fixture()
    p=tmp_path/"tiny.sofa"
    with h5py.File(p,"w") as f:
        f.attrs["SOFAConventions"]="SimpleFreeFieldHRIR"
        ds=f.create_dataset("SourcePosition",data=model.xyz_to_spherical(d.xyz))
        ds.attrs["Type"]="spherical"
        ds.attrs["Units"]="degree, degree, metre"
        f.create_dataset("Data.IR",data=d.ir)
        f.create_dataset("Data.SamplingRate",data=np.array([d.fs]))
        f.create_dataset("Data.Delay",data=np.zeros((1,2)))
        f.create_dataset("ReceiverPosition",data=np.array([[0,.09,0],[0,-.09,0]]))
    parsed=model.load_sofa(p)
    assert parsed.source_sha256 != "SYNTHETIC"
    np.testing.assert_allclose(parsed.xyz,d.xyz,atol=1e-7)
    with pytest.raises(ValueError,match="MD5"):
        model.load_sofa(p,expected_md5="00000000000000000000000000000000")
    with h5py.File(p,"r+") as f:
        f["Data.Delay"][0,0]=1
    with pytest.raises(ValueError,match="Delay"):
        model.load_sofa(p)
