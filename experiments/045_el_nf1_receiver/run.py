"""EL-NF1: relative near-field bilateral HRIR interpolation, RESEARCH_ONLY."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

import h5py
import numpy as np
from scipy.signal import butter, correlate, sosfiltfilt

RADII=(0.2,0.3,0.4,0.5)
BANDS=((500,1000),(1000,2000),(2000,4000),(4000,8000))
MD5='4ba9cc348801a6805265c7168b5b3227'
FS=48000
C=343.0

def digest(path:Path,kind:str='sha256')->str:
    h=hashlib.new(kind)
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def attr(obj,name:str)->str:
    v=obj.attrs.get(name,'')
    if isinstance(v,bytes):
        v=v.decode('utf-8')
    if isinstance(v,np.ndarray) and v.size==1:
        v=v.reshape(-1)[0]
        if isinstance(v,bytes):v=v.decode('utf-8')
    return str(v).strip()

def cartesian(position:np.ndarray,kind:str,units:str)->np.ndarray:
    if position.ndim!=2 or position.shape[1]!=3 or not np.isfinite(position).all():
        raise ValueError('INVALID: finite Mx3 source positions expected')
    u=[x.strip().lower() for x in units.split(',')]
    if kind.lower()=='spherical' and len(u)==3 and u[0] in ('degree','degrees') and u[1] in ('degree','degrees') and u[2] in ('metre','meter','m'):
        a,e,r=np.deg2rad(position[:,0]),np.deg2rad(position[:,1]),position[:,2]
        if np.any(r<=0):raise ValueError('INVALID: nonpositive source radius')
        return np.stack((r*np.cos(e)*np.cos(a),r*np.cos(e)*np.sin(a),r*np.sin(e)),axis=1)
    if kind.lower()=='cartesian' and u in (['metre'],['meter'],['m'],['metre']*3):
        return position.copy()
    raise ValueError('UNSUPPORTED: source coordinate convention or units')

def load_sofa(path:Path,require_original:bool=True)->dict:
    if not path.is_file() or not 512<=path.stat().st_size<=50_000_000:
        raise ValueError('INVALID: missing/unsafe SOFA file')
    md5=digest(path,'md5')
    if require_original and md5!=MD5:
        raise ValueError('INVALID: original Zenodo SOFA MD5 mismatch')
    with h5py.File(path,'r') as f:
        if attr(f,'SOFAConventions')!='SimpleFreeFieldHRIR' or attr(f,'DataType')!='FIR':
            raise ValueError('UNSUPPORTED: only SimpleFreeFieldHRIR FIR')
        for key in ('SourcePosition','Data.IR','Data.SamplingRate'):
            if key not in f:raise ValueError('INVALID: missing '+key)
        sp=f['SourcePosition']
        xyz=cartesian(np.asarray(sp,dtype=float),attr(sp,'Type'),attr(sp,'Units'))
        sr=np.asarray(f['Data.SamplingRate'],dtype=float).ravel()
        if sr.size!=1 or not np.isfinite(sr).all() or sr[0]!=FS:
            raise ValueError('UNSUPPORTED: 48000 Hz only; no implicit resampling')
        ir=np.asarray(f['Data.IR'],dtype=float)
        if ir.ndim!=3 or ir.shape[:2]!=(len(xyz),2) or not 32<=ir.shape[2]<=32768:
            raise ValueError('INVALID: Data.IR Mx2xN required')
        if not np.isfinite(ir).all() or np.any(np.max(abs(ir),axis=2)==0):
            raise ValueError('INVALID: nonfinite or silent ear IR')
        delay=np.zeros((len(xyz),2),dtype=float)
        if 'Data.Delay' in f:
            ds=f['Data.Delay']
            if attr(ds,'Units').lower() not in ('','sample','samples'):
                raise ValueError('UNSUPPORTED: Data.Delay must use sample units')
            raw=np.asarray(ds,dtype=float)
            if raw.shape==(1,2):
                delay=np.broadcast_to(raw,(len(xyz),2)).copy()
            elif raw.shape==(len(xyz),2):
                delay=raw.copy()
            else:
                raise ValueError('UNSUPPORTED: Data.Delay shape must be 1x2 or Mx2')
        if not np.isfinite(delay).all() or np.any(delay<0) or np.max(delay)>FS:
            raise ValueError('INVALID: nonfinite/negative/unsafe delay')
        receiver=f.get('ReceiverPosition')
        status='UNVERIFIED: ReceiverPosition absent; observation plane/ear state unknown'
        if receiver is not None:
            status=('UNVERIFIED: ReceiverPosition type='+attr(receiver,'Type')+
                    ', units='+attr(receiver,'Units')+'; open/blocked and calibration unknown')
        metadata=dict(convention=attr(f,'SOFAConventions'),version=attr(f,'SOFAConventionsVersion'),
                      receiver_status=status,source_type=attr(sp,'Type'),source_units=attr(sp,'Units'),
                      normalization='UNVERIFIED: relative L/R only, NOT physical Pa')
    pad=int(math.ceil(float(delay.max())))+4
    if pad>FS:raise ValueError('UNSUPPORTED: excessive FIR padding')
    n=ir.shape[-1]
    effective=np.zeros((len(xyz),2,n+pad),dtype=float)
    t=np.arange(n+pad,dtype=float)
    for i in range(len(xyz)):
        for e in range(2):
            effective[i,e]=np.interp(t-delay[i,e],np.arange(n),ir[i,e],left=0,right=0)
    return dict(xyz=xyz,ir=effective,sr=FS,sha256=digest(path),md5=md5,meta=metadata,
                raw_ir_length=n,max_delay_samples=float(np.max(delay)))

def matching_directions(xyz:np.ndarray)->list[tuple[int,int,int,int]]:
    radius=np.linalg.norm(xyz,axis=1)
    if np.any(radius<=0):raise ValueError('INVALID: nonpositive radius')
    unit=xyz/radius[:,None]
    bins=[]
    for r in RADII:
        group=np.flatnonzero(abs(radius-r)<=.015)
        if len(group)!=49:raise ValueError('UNSUPPORTED: exactly 49 measurements per radius required')
        bins.append(group)
    result=[]
    for origin in bins[0]:
        indices=[int(origin)]
        for group in bins[1:]:
            angle=np.rad2deg(np.arccos(np.clip(unit[group]@unit[origin],-1,1)))
            order=np.argsort(angle)
            if angle[order[0]]>2:
                raise ValueError('UNSUPPORTED: source direction mismatch >2deg')
            if angle[order[1]]-angle[order[0]]<.05:
                raise ValueError('UNSUPPORTED: ambiguous nearest source direction')
            indices.append(int(group[order[0]]))
        result.append(tuple(indices))
    if any(len(set(v[j] for v in result))!=len(result) for j in range(4)):
        raise ValueError('UNSUPPORTED: direction pairing must be one-to-one')
    if len(result)<10:raise ValueError('INDETERMINATE: too few usable directions')
    return result

def shift(h:np.ndarray,samples:float)->np.ndarray:
    t=np.arange(len(h),dtype=float)
    return np.interp(t-samples,t,h,left=0,right=0)

def models(a:np.ndarray,b:np.ndarray,reference:np.ndarray,ra:float,rb:float,
           target:float,fs:int=FS)->dict[str,np.ndarray]:
    if not (0<ra<target<rb) or a.shape!=b.shape or a.shape!=reference.shape or a.ndim!=2 or a.shape[0]!=2:
        raise ValueError('INVALID: 2xN within-range interpolation required')
    if not all(np.isfinite(z).all() for z in (a,b,reference)):
        raise ValueError('INVALID: nonfinite IR input')
    w=(target-ra)/(rb-ra)
    c0=(1-w)*a+w*b
    c1=np.zeros_like(c0)
    for ear in range(2):
        pa,pb=int(np.argmax(abs(a[ear]))),int(np.argmax(abs(b[ear])))
        anchor=max(pa,pb)+32
        ha,hb=shift(a[ear],anchor-pa),shift(b[ear],anchor-pb)
        aligned=(1-w)*ha+w*hb
        c1[ear]=shift(aligned,(1-w)*pa+w*pb-anchor)
    baseline=np.vstack([shift(reference[e]*(0.5/target),(target-0.5)*fs/C) for e in range(2)])
    return dict(B=baseline,C0=c0,C1=c1)

def band_ild(h:np.ndarray,fs:int=FS)->list[float]:
    if h.ndim!=2 or h.shape[0]!=2 or not np.isfinite(h).all():
        raise ValueError('INVALID: finite two-ear IR expected')
    spec=np.fft.rfft(h,axis=1)
    freq=np.fft.rfftfreq(h.shape[1],1/fs)
    scores=[]
    for lo,hi in BANDS:
        mask=(freq>=lo)&(freq<hi)
        if not mask.any():raise ValueError('UNSUPPORTED: FFT band resolution')
        amp=np.sqrt(np.sum(abs(spec[:,mask])**2,axis=1))
        if not np.isfinite(amp).all() or np.any(amp<=1e-12):
            raise ValueError('INDETERMINATE: zero/nonfinite band energy')
        scores.append(float(20*np.log10(amp[0]/amp[1])))
    return scores

def itd_us(h:np.ndarray,fs:int=FS)->float:
    sos=butter(4,[500,1500],btype='bandpass',fs=fs,output='sos')
    filt=sosfiltfilt(sos,h,axis=1)
    if np.min(np.sum(filt*filt,axis=1))<=1e-20:
        raise ValueError('INDETERMINATE: insufficient ITD band energy')
    cc=correlate(filt[0],filt[1],mode='full',method='fft')
    peak=int(np.argmax(cc))
    if not 0<peak<len(cc)-1:raise ValueError('INDETERMINATE: ITD boundary peak')
    a,b,c=cc[peak-1:peak+2]
    den=a-2*b+c
    frac=0. if abs(den)<1e-20 else .5*(a-c)/den
    if abs(frac)>1:raise ValueError('INDETERMINATE: unstable ITD refinement')
    return float((peak-(h.shape[1]-1)+frac)*1e6/fs)

def score(data:dict)->dict:
    groups=matching_directions(data['xyz'])
    ears=data['ir'];fs=data['sr']
    records=[]
    for direction,indices in enumerate(groups):
        for fold,j,ja,jb in (('F30',1,0,2),('F40',2,1,3)):
            truth=ears[indices[j]]
            pred=models(ears[indices[ja]],ears[indices[jb]],ears[indices[3]],
                        RADII[ja],RADII[jb],RADII[j],fs)
            target_ild=np.asarray(band_ild(truth,fs))
            target_itd=itd_us(truth,fs)
            for model,h in pred.items():
                records.append(dict(direction=direction,fold=fold,model=model,
                                    absolute_ild_errors_db=np.abs(np.asarray(band_ild(h,fs))-target_ild).tolist(),
                                    abs_itd_error_us=abs(itd_us(h,fs)-target_itd),
                                    target_measurement_index=int(indices[j]),
                                    training_measurement_indices=[int(indices[ja]),int(indices[jb])],
                                    baseline_measurement_index=int(indices[3])))
    def med(model,fold=None,field='absolute_ild_errors_db'):
        arr=[v for v in records if v['model']==model and (fold is None or v['fold']==fold)]
        return float(np.median([x for v in arr for x in (v[field] if isinstance(v[field],list) else [v[field]])]))
    matrices={}
    for model in ('B','C0','C1'):
        matrices[model]=np.asarray([[x for row in records if row['direction']==i and row['model']==model
                                    for x in row['absolute_ild_errors_db']] for i in range(len(groups))])
    rng=np.random.default_rng(20261030)
    diffs=[]
    for _ in range(2000):
        sample=rng.integers(0,len(groups),size=len(groups))
        diffs.append(float(np.median(matrices['B'][sample])-np.median(matrices['C1'][sample])))
    ci=np.percentile(diffs,[2.5,97.5]).tolist()
    stats={m:dict(median_ild_error_db=med(m),F30_median_ild_error_db=med(m,'F30'),
                  F40_median_ild_error_db=med(m,'F40'),
                  median_abs_itd_error_us=med(m,field='abs_itd_error_us')) for m in ('B','C0','C1')}
    base,pred=stats['B'],stats['C1']
    passed=(pred['median_ild_error_db']<=.8*base['median_ild_error_db'] and ci[0]>0 and
            all(pred[f'{fold}_median_ild_error_db']<base[f'{fold}_median_ild_error_db'] for fold in ('F30','F40')) and
            pred['median_abs_itd_error_us']<=base['median_abs_itd_error_us']+25)
    return dict(schema_version='el-nf1-evidence-v1',adoption='NOT_ADOPTED',
                numerical_verdict='GO_LIMITED_NUMERICAL_CANDIDATE' if passed else 'REVISE_OR_REJECT',
                scientific_claim='relative artificial-head HRTF at 0.2–0.5m only',
                directions=len(groups),records=records,statistics=stats,ild_improvement_ci95_db=ci,
                bootstrap_seed=20261030,bootstrap_directions=2000,
                g4_listening='PENDING',g5_independent_review='PENDING')

def run(sofa:Path,output:Path,require_original:bool=True)->dict:
    if output.exists():raise FileExistsError('INVALID: no evidence overwrite')
    data=load_sofa(sofa,require_original)
    result=score(data)
    result['input']={k:data[k] for k in ('sha256','md5','meta','raw_ir_length','max_delay_samples')}
    result['runner_sha256']=digest(Path(__file__))
    content=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(content,encoding='utf-8')
    return result

def main()->None:
    p=argparse.ArgumentParser(description='EL-NF1 measured near-field receiver holdout gate')
    p.add_argument('--sofa',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    result=run(args.sofa,args.output)
    print(json.dumps(dict(evidence=str(args.output),verdict=result['numerical_verdict'],
                          directions=result['directions'],
                          medians={k:v['median_ild_error_db'] for k,v in result['statistics'].items()})))

if __name__=='__main__':
    main()
