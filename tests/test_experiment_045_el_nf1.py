"""Synthetic numerical tests are not measured HRTF validation."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

h5py=pytest.importorskip('h5py')
pytest.importorskip('scipy')
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'experiments/045_el_nf1_receiver/run.py'
spec=importlib.util.spec_from_file_location('el_nf1',SRC)
nf=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=nf
spec.loader.exec_module(nf)

def synthetic(path,mode='valid'):
    N=512
    dirs=np.linspace(-.6,.6,49)
    positions=[];irs=[]
    for radius in (.2,.3,.4,.5):
        for angle in dirs:
            positions.append([np.rad2deg(angle),0.,radius])
            h=np.zeros((2,N))
            for ear in range(2):
                delay=int(round(60+radius*60+ear*(8+7*np.sin(angle)+radius*2)))
                mag=(.5/radius)*(1+.15*(1 if ear==0 else -1)*np.sin(angle)*(1-radius))
                h[ear,delay]=mag
                h[ear,delay+3]=-.17*mag
                h[ear,delay+9]=.09*mag
            irs.append(h)
    with h5py.File(path,'w') as f:
        f.attrs['SOFAConventions']='SimpleFreeFieldHRIR'
        f.attrs['DataType']='FIR'
        f.attrs['SOFAConventionsVersion']='1.0'
        sp=f.create_dataset('SourcePosition',data=positions)
        sp.attrs['Type']='spherical'
        sp.attrs['Units']='degree, degree, metre'
        f.create_dataset('Data.IR',data=np.asarray(irs))
        f.create_dataset('Data.SamplingRate',data=[48000])
        ds=f.create_dataset('Data.Delay',data=[[0.,0.]])
        ds.attrs['Units']='sample'
        rec=f.create_dataset('ReceiverPosition',data=[[0.,0.,0.],[0.,0.,0.]])
        rec.attrs['Type']='spherical'
        rec.attrs['Units']='metre'
        if mode=='badunit':sp.attrs['Units']='furlong,furlong,foot'
        if mode=='nonsense':f['Data.IR'][0,0,0]=np.nan

def test_data_audit_geometry(tmp_path):
    p=tmp_path/'s.sofa';synthetic(p)
    data=nf.load_sofa(p,require_original=False)
    assert len(nf.matching_directions(data['xyz']))==49
    assert data['ir'].shape[:2]==(196,2)
    assert 'UNVERIFIED' in data['meta']['receiver_status']

def test_original_dataset_integrity_gate(tmp_path):
    p=tmp_path/'s.sofa';synthetic(p)
    with pytest.raises(ValueError,match='MD5'):nf.load_sofa(p)

def test_invalid_sofa_rejected(tmp_path):
    for mode,match in [('badunit','UNSUPPORTED'),('nonsense','INVALID')]:
        p=tmp_path/(mode+'.sofa');synthetic(p,mode)
        with pytest.raises(ValueError,match=match):nf.load_sofa(p,require_original=False)

def test_shift_preserves_absolute_channel_ratio_and_no_wraparound():
    h=np.zeros(256);h[100]=1
    assert np.argmax(nf.shift(h,8))==108
    assert np.argmax(nf.shift(h,-8))==92
    h[255]=1
    assert nf.shift(h,10)[:20].sum()==0
    np.testing.assert_allclose(nf.band_ild(np.array([2*h,h])),
                               [20*np.log10(2)]*4,atol=1e-9)

def test_c1_realigns_synthetic_arrivals_without_mixing_ears():
    a=np.zeros((2,400));b=a.copy();base=a.copy()
    a[0,110]=2;a[1,120]=1
    b[0,130]=2;b[1,140]=1
    base[0,140]=2;base[1,150]=1
    result=nf.models(a,b,base,.2,.4,.3)
    assert np.argmax(result['C1'][0])==120
    assert np.argmax(result['C1'][1])==130
    assert result['C1'][0].max()==2 and result['C1'][1].max()==1
    with pytest.raises(ValueError,match='INVALID'):nf.models(a,b,base,.2,.4,.8)

def test_duplicate_direction_is_rejected(tmp_path):
    p=tmp_path/'s.sofa';synthetic(p)
    with h5py.File(p,'r+') as f:
        f['SourcePosition'][49,:]=f['SourcePosition'][50,:]
    data=nf.load_sofa(p,require_original=False)
    with pytest.raises(ValueError,match='UNSUPPORTED'):nf.matching_directions(data['xyz'])

def test_refuse_delay_units_not_in_samples(tmp_path):
    p=tmp_path/'s.sofa';synthetic(p)
    with h5py.File(p,'r+') as f:f['Data.Delay'].attrs['Units']='seconds'
    with pytest.raises(ValueError,match='UNSUPPORTED'):nf.load_sofa(p,require_original=False)

def test_full_synthetic_holdout_and_provenance(tmp_path):
    p=tmp_path/'s.sofa';synthetic(p)
    out=tmp_path/'evidence.json'
    result=nf.run(p,out,require_original=False)
    assert len(result['records'])==49*2*3
    assert set(result['statistics'])=={'B','C0','C1'}
    assert result['adoption']=='NOT_ADOPTED'
    assert result['g4_listening']=='PENDING'
    assert all(np.isfinite(x['median_ild_error_db']) for x in result['statistics'].values())
    assert len(result['ild_improvement_ci95_db'])==2
    with pytest.raises(FileExistsError):nf.run(p,out,require_original=False)
