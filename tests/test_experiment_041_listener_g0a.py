"""Unit + research smoke tests; synthetic SOFA is NOT human measurement evidence."""
from __future__ import annotations
import importlib.util
import json
import math
from pathlib import Path

import h5py
import numpy as np
import pytest
import soundfile as sf
from scipy.signal import fftconvolve

SRC=Path(__file__).resolve().parents[1]/'experiments/041_listener_g0a/run.py'
spec=importlib.util.spec_from_file_location('el_g0a_run',SRC)
import sys
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)


def make_fixture(path:Path, mode='valid'):
    positions=np.array([[az,0.,.3] for az in (0.,-30.,30.,60.,-60.)])
    with h5py.File(path,'w') as f:
        f.attrs['SOFAConventions']='SimpleFreeFieldHRIR'
        f.attrs['SOFAConventionsVersion']='1.0'
        f.attrs['DataType']='FIR'
        ds=f.create_dataset('SourcePosition',data=positions)
        ds.attrs['Type']='spherical';ds.attrs['Units']='degree, degree, metre'
        ds=f.create_dataset('ReceiverPosition',data=[[0,.09,0],[0,-.09,0]])
        ds.attrs['Type']='cartesian';ds.attrs['Units']='metre, metre, metre'
        f.create_dataset('Data.SamplingRate',data=[48000])
        h=np.zeros((5,2,129));h[:,0,6]=.65;h[:,1,8]=.55
        h[1,1,5]=.9;h[2,0,5]=.9
        f.create_dataset('Data.IR',data=h)
        f.create_dataset('Data.Delay',data=np.zeros((5,2)))
        if mode=='badposition':ds.attrs['Units']='furlong,furlong,furlong'


def test_coordinate_convention():
    a=module._coords(np.array([[0,0,.3],[90,0,.3],[-90,0,.3]]),'spherical','degree, degree, metre')
    np.testing.assert_allclose(a,[[.3,0,0],[0,.3,0],[0,-.3,0]],atol=1e-15)


def test_file_metadata_select(tmp_path):
    p=tmp_path/'fixture.sofa';make_fixture(p)
    d=module.load_sofa(p)
    assert d.sample_rate==48000 and d.receivers.shape==(2,3)
    assert module.select_positions(d.xyz)==dict(center=0,right=1,left=2)


def test_no_extrapolation(tmp_path):
    p=tmp_path/'bad.sofa';make_fixture(p)
    with h5py.File(p,'r+') as f:
        f['SourcePosition'][:,2]=1.1
    with pytest.raises(ValueError,match='UNSUPPORTED'):
        module.select_positions(module.load_sofa(p).xyz)


def test_reject_bad_units(tmp_path):
    p=tmp_path/'bad.sofa';make_fixture(p,'badposition')
    with pytest.raises(ValueError,match='UNSUPPORTED'):
        module.load_sofa(p)


def test_freefield_oracle_center_and_mirrors():
    q=module.source_q(.5)
    L=np.array([0.,.09,0.]);R=np.array([0.,-.09,0.])
    def props(source):return module.render_a(q,np.array(source),np.stack([L,R]))[1]
    c=props((.2,0,0)); assert abs(c['right_minus_left_delay_s'])<1e-14
    a=props((.2,-.12,0));b=props((.2,+.12,0))
    assert math.isclose(a['right_minus_left_delay_s'],-.2558673931149656e-3,abs_tol=1e-13)
    assert math.isclose(a['right_over_left_level_db'],3.1307268779057047,abs_tol=1e-9)
    assert math.isclose(a['right_minus_left_delay_s'],-b['right_minus_left_delay_s'],abs_tol=1e-13)
    assert math.isclose(a['right_over_left_level_db'],-b['right_over_left_level_db'],abs_tol=1e-13)


def test_fir_convolution_independent():
    x=np.zeros(100);x[40]=1
    h=np.zeros((2,30));h[0,7]=.6;h[1,9]=.7
    # render_b uses dQ/dt: compare to direct numpy.convolve without extra 1/r.
    y=module.render_b(x,h,module.FS,np.zeros(2))
    dx=np.gradient(x,1/module.FS,edge_order=2)
    np.testing.assert_allclose(y[:,0],np.convolve(dx,h[0]),atol=1e-10)
    np.testing.assert_allclose(y[:,1],np.convolve(dx,h[1]),atol=1e-10)


def test_time_delays_and_relative_level_preserved():
    x=np.zeros(220);x[72]=1
    y=module.delay_fir(x,68.25)
    assert abs(np.argmax(y)-140)<=1
    assert abs(y.sum()-1.)<.002


def test_synthetic_end_to_end_six_wavs(tmp_path):
    p=tmp_path/'fixture.sofa';make_fixture(p)
    output=tmp_path/'out'
    result=module.run(p,output)
    assert result['adoption']=='NOT_ADOPTED'
    assert (output/'index.html').exists()
    assert (output/'evidence.json').exists()
    assert len(list((output/'audio').glob('*.wav')))==6
    for f in (output/'audio').glob('*.wav'):
        audio,rate=sf.read(f,always_2d=True)
        assert rate==48000 and audio.shape[1]==2 and np.isfinite(audio).all()
        assert .00001<abs(audio).max()<=.701
    loaded=json.loads((output/'evidence.json').read_text())
    assert loaded['cases']['right']['azimuth_deg']<0
    assert loaded['cases']['left']['azimuth_deg']>0
    assert 'UNSUPPORTED' in loaded['cases']['center']['output']['level_conclusion']
    with pytest.raises(FileExistsError):module.run(p,output)


def test_ir_resampling_and_safety(tmp_path):
    src=np.zeros(200);src[90]=1
    dst=module._resample(src,96000)
    assert len(dst)==100 and 40<=np.argmax(abs(dst))<=50
    p=tmp_path/'evil.sofa';make_fixture(p)
    with h5py.File(p,'r+') as f:
        f['Data.IR'][0,0,0]=np.nan
    with pytest.raises(ValueError,match='nonfinite'):
        module.load_sofa(p)


def test_frequency_domain_sofa_uses_irfft_without_phase_discard(tmp_path):
    p=tmp_path/'hrtf.sofa';make_fixture(p)
    h=np.zeros((5,2,129));h[:,0,8]=.6;h[:,1,11]=.8
    with h5py.File(p,'r+') as f:
        f.attrs['SOFAConventions']='SimpleFreeFieldHRTF'
        del f['Data.IR']; del f['Data.SamplingRate']
        f.create_dataset('N', data=np.fft.rfftfreq(256,1/48000))
        tf=np.fft.rfft(h, n=256, axis=-1)
        f.create_dataset('Data.Real',data=tf.real)
        f.create_dataset('Data.Imag',data=tf.imag)
    d=module.load_sofa(p)
    assert d.meta['ir_origin'].startswith('irfft')
    np.testing.assert_allclose(d.ir[:,:,0:129],h,atol=1e-14)
    out=module.run(p,tmp_path/'render')
    assert len(out['cases'])==3


def test_delay_samples_preserves_channel_order():
    q=module.source_q(.2)
    h=np.zeros((2,50));h[0,10]=1;h[1,10]=1
    a=module.render_b(q,h,48000,np.zeros(2))
    b=module.render_b(q,h,48000,np.array([0.,8.]))
    assert np.argmax(abs(b[:,1]))-np.argmax(abs(b[:,0]))==8
    assert np.argmax(abs(a[:,1]))==np.argmax(abs(a[:,0]))
