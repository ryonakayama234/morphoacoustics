"""BODYMAP B2 run/1: orchestration only; scientific functions come from clean pin.

No source/solver/oracle patching, tolerance changes, extra scientific sweeps,
overwriting, or rerunning a started study. Engineering results are isolated.
The supervisor adjudicates the study oracle and all final outcomes later.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import importlib.metadata as md
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback

PACKAGE = Path(__file__).resolve().parent
PIN = '0bb60cc227d231ec1cb67b701a849172ed92164b'
ORACLE_PIN = '71c7c89f7f86712f12aad31dfa5ee210830e536d'
GEOMS = ('M0_REST','U6_REF','U19_REF')
LEVELS = (0.,1e-6,.5,1.)
ENG = [('U6_REF',v) for v in LEVELS]+[('U19_REF',0.),('U19_REF',1.),('M0_REST',0.),('M0_REST',1.)]
STUDY = [(g,v) for g in GEOMS for v in LEVELS]+[(g,0.) for g in GEOMS]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def write(path,obj):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
def git(repo,*a): return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
def guard(repo):
    assert git(repo,'rev-parse','HEAD') == PIN
    assert not git(repo,'status','--porcelain=v1','--untracked-files=all')
    pre=json.loads((PACKAGE/'preflight-receipt.json').read_text())
    assert pre['status']=='INPUT_PREFLIGHT_PASS'
    assert platform.python_version()==pre['python']=='3.11.18'
    assert {d.metadata['Name'].lower().replace('_','-'):d.version for d in md.distributions()}==pre['packages']
    for rel,item in json.loads((PACKAGE/'pinned-inventory.json').read_text()).items():
        assert sha(repo/rel)==item['sha256']
    for rel,digest in pre['input_sha256'].items(): assert sha(PACKAGE/'inputs'/rel)==digest
    freeze=json.loads((PACKAGE/'runner-freeze.json').read_text())
    for rel,digest in freeze['files'].items(): assert sha(PACKAGE/rel)==digest
    return pre
def imports(repo):
    sys.path.insert(0,str(repo)); sys.path.insert(0,str(repo/'src'))

def oracle_engineering(c,p,g,s):
    """Read-only application of Muse's frozen oracle to the known eight cases.

    Never called for a scientific case. Primary observables + coefficients
    across all 351 bins and raw all 24000 samples, with frozen scales/tolerances.
    """
    import numpy as np
    from mpmath import mp
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.recursion import evaluate_case
    from experiments.bodymap_b2_passive_loss.reviewer_oracle.direct_pressure import direct_pressure
    obs=evaluate_case(list(range(100,801,2)),[repr(r) for r in g['radii_m']],
        [repr(l) for l in g['lengths_m']],repr(c['lambda']),bulk=True)
    zstar=c['Zstar']; hpstar=1.21*2*math.pi*800/(4*math.pi*.20)
    cv=lambda x: complex(float(mp.re(x)),float(mp.im(x)))
    ref={k:np.array([cv(b[k]) for b in obs]) for k in ('HU','Zin','Hp')}
    for k in ('z','y','gamma','zc'):
        ref[k]=np.array([[cv(x[k]) for x in b['coeffs']] for b in obs])
    report={'scope':'KNOWN_ENGINEERING_DATA_ONLY','oracle_commit':ORACLE_PIN,'all_351_bins':True}
    good=True
    for k in ref:
        scale={'HU':1.,'Zin':zstar,'Hp':hpstar,'z':zstar,'y':1/zstar,'zc':zstar}.get(k)
        if k=='gamma': scale=(np.array(range(100,801,2))*2*math.pi/343)[:,None]
        err=np.abs(c[k]-ref[k])/scale
        tol=(1e-12+1e-10*np.abs(ref[k])/scale) if c['lambda']==0 else (1e-10+1e-8*np.abs(ref[k])/scale)
        ok=bool(np.all(err<=tol)); good &= ok
        report[k]={'max_normalized_error':float(np.max(err)),
            'max_error_over_tolerance':float(np.max(err/tol)),'ok':ok}
    raw=np.empty(24000)
    for lo in range(0,24000,2000):
        ix=np.arange(lo,min(lo+2000,24000)); raw[ix]=direct_pressure(s['Q'],ref['Hp'],ix)
    err=float(np.linalg.norm(raw-p['pressure_pa'])/np.linalg.norm(p['pressure_pa']))
    raw_tol=1e-10 if c['lambda']==0 else 1e-8
    good &= err<=raw_tol
    report.update(raw_l2_vs_oracle=err,raw_tolerance=raw_tol,ok=bool(good))
    return report,ref

def make_pack(dest,case_id,g,source,loss,raw_sha,coeff_sha,status,refusal=None):
    from experiments.bodymap_b2_passive_loss.verification.pack_v0 import new_pack,write_once
    p=new_pack(evidence_id=case_id,utc=utc(),case_id=case_id,run_head=PIN,
        verification_head=None,geometry=g,
        source={'recomputed_samples_sha256':source['source_sha256_le_f64'],
            'evidence_class':'RECOMPUTED'}, raw_sha256=raw_sha,
        coefficient_ref='coefficient-manifest.json',coefficient_sha256=coeff_sha,
        loss=loss,status=status,refusal_code=refusal)
    if (dest/'arrays.npz').exists():
        p['complex_transfer']=[{'artifact_ref':'arrays.npz','artifact_sha256':sha(dest/'arrays.npz'),
            'fields':['frequency_hz','HU_re','HU_im','Zin_re','Zin_im','Hp_re','Hp_im'],
            'units':{'frequency_hz':'Hz','HU':'1','Zin':'Pa*s/m3','Hp':'Pa*s/m3'},
            'oracle_method_pin':ORACLE_PIN,'oracle_study_status':'PENDING_SUPERVISOR'}]
        p['physical_observables']=[{'artifact_ref':'arrays.npz',
            'fields':['z','y','gamma','zc','sections','T','detT','states','S',
                      'Pin','Pout','Pstar','D16','D32','balance','sigma_max'],
            'state_columns':['p_Pa','U_m3_s'],'state_normalization':'Uin=1',
            'power_units':'W','claim_scope':'BOUNDED_MODEL_ONLY'}]
    p['medium_boundary_observer']['load_R']=.05*1.21*343/(math.pi*g['radii_m'][-1]**2)
    p['source_evidence'].update(generator='Exp013::build_sources/lf_fixed',
        source_buffer_ref='../../source.le-f64',source_buffer_sha256=source['source_sha256_le_f64'],
        source_dft_ref='../../source-dft.le-c128',source_dft_sha256=source['dft_sha256_le_complex128'],
        transitive_pins=source['transitive_pins'])
    p['raw_signal']['artifact_ref']='raw-pressure.le-f64' if raw_sha else None
    # Same-run bytes are saved, but independent chain attestation is not claimed.
    return write_once(dest/'pack.json',p)

def worker(repo,group,index):
    import numpy as np
    pre=guard(repo); imports(repo)
    from experiments.bodymap_b2_passive_loss.geometry_binding import resolve_geometry
    from experiments.bodymap_b2_passive_loss.source_binding import consumed_source
    from experiments.bodymap_b2_passive_loss.candidate.transfer import compute_case
    from experiments.bodymap_b2_passive_loss.candidate.pressure import projected_pressure
    from experiments.bodymap_b2_passive_loss.verification.physics import inspect,independent_integral
    defs=ENG if group=='engineering' else STUDY
    gname,lam=defs[index]
    case_id=f'{group}-{index+1:02d}-{gname}-lambda-{lam}'
    dest=PACKAGE/group/case_id; dest.mkdir(parents=True,exist_ok=False)
    g=resolve_geometry(gname); source=consumed_source()
    assert source['buffer'].tobytes()==(PACKAGE/'source.le-f64').read_bytes()
    assert source['source_sha256_le_f64']==pre['source']['source_sha256_le_f64']
    started=time.monotonic(); receipt={'case_id':case_id,'geometry':g,'lambda':lam,
        'group':group,'started_at_utc':utc(),'pid':os.getpid(),'core_head':PIN,
        'runner_sha256':sha(__file__),'independent_process':True,
        'source_sha256':source['source_sha256_le_f64'],
        'source_evidence_class':'RECOMPUTED','full_verified_source_state':'UNKNOWN',
        'known_engineering_condition':(gname,lam) in ENG,
        'repeated_null':group=='scientific' and index>=12,
        'implementation_conformance':'UNRESOLVED','effect':'UNKNOWN',
        'oracle_study_review':'PENDING_SUPERVISOR'}
    coeff={'law':'b2.lrf.circular-rigid-isothermal/1','prereg_sha256':pre['input_sha256']['prereg.md'],
        'lambda':lam,'lambda_definition':'z0+lambda*(z1-z0), y0+lambda*(y1-y0)',
        'rho_kg_m3':1.21,'c_m_s':343.,'mu_Pa_s':1.81e-5,'kappa_W_m_K':.0257,
        'cp_J_kg_K':1005.,'gamma':1.40,'T_ref_K':293.15,
        'Pr':1.81e-5*1005/.0257,'Ks_Pa':1.21*343**2,'p_ref_Pa':1.21*343**2/1.4,
        'radii_m':g['radii_m'],'lengths_m':g['lengths_m'],
        'nominal_preset_origin':'FZ-P1 numerical verification preset; not measured air/tissue',
        'wall':'rigid/no-slip/isothermal','attenuation_np_m':0.,'phasor':'exp(+jwt)',
        'volume_velocity':'m3/s_inlet_to_outlet','load_formula':'0.05*rho*c/S_last',
        'band_hz':[100,800,2],'proxy_m':.20,'calibration_status':'UNCALIBRATED',
        'scope':'static circular serial LRF; no wall/tissue mechanics or moving tract'}
    write(dest/'coefficient-manifest.json',coeff); coeff_sha=sha(dest/'coefficient-manifest.json')
    raw_sha=None
    try:
        # This is the only candidate full-grid call in this worker.
        c=compute_case(tuple(g['radii_m']),tuple(g['lengths_m']),lam)
        p=projected_pressure(source['buffer'],c['Hp'])
        assert p['source_sha256_le_f64']==source['source_sha256_le_f64']
        with (dest/'raw-pressure.le-f64').open('xb') as f: f.write(p['pressure_pa'].tobytes())
        raw_sha=sha(dest/'raw-pressure.le-f64'); assert raw_sha==p['raw_sha256_le_f64']
        arrays={k:np.asarray(v) for k,v in c.items()}
        arrays.update(pressure_pa=p['pressure_pa'],P=p['P'],Q=p['Q'])
        for k in ('HU','Zin','Hp'):
            arrays[k+'_re']=c[k].real; arrays[k+'_im']=c[k].imag
        # Persist the completed candidate even if later diagnostics fail.
        with (dest/'candidate-before-diagnostics.npz').open('xb') as f: np.savez_compressed(f,**arrays)
        diag=inspect(c)
        states=c['states']; uin=states[:,0,1]; uout=states[:,-1,1]
        ps=.5*c['Zstar']*np.abs(uin)**2
        pin=.5*np.real(states[:,0,0]*np.conjugate(uin)); pout=.5*c['load_R']*np.abs(uout)**2
        d32=np.asarray(diag['d32_over_pstar'])*ps
        d16=np.array([independent_integral(c,i,16) for i in range(351)])
        arrays.update(Pin=pin,Pout=pout,Pstar=ps,D16=d16,D32=d32,
            balance=pin-pout-d32,sigma_max=np.array([np.linalg.svd(s,compute_uv=False)[0] for s in c['S']]))
        with (dest/'arrays.npz').open('xb') as f: np.savez_compressed(f,**arrays)
        receipt.update(candidate_physics=diag,raw_sha256=raw_sha,
            arrays_sha256=sha(dest/'arrays.npz'),status='CANDIDATE_RECORDED_REVIEW_PENDING')
        if group=='engineering':
            result,ref=oracle_engineering(c,p,g,source)
            with (dest/'engineering-oracle.npz').open('xb') as f: np.savez_compressed(f,**ref)
            write(dest/'engineering-oracle-comparison.json',result)
            assert result['ok'], 'Engineering replay differs from frozen oracle tolerances'
            receipt['status']='KNOWN_ENGINEERING_REPLAY_PASS'
        receipt['pack_sha256']=make_pack(dest,case_id,g,source,lam,raw_sha,coeff_sha,receipt['status'])
        receipt.update(completed_at_utc=utc(),wall_seconds=time.monotonic()-started)
        write(dest/'receipt.json',receipt); guard(repo)
        print(json.dumps({'case_id':case_id,'status':receipt['status'],'wall_seconds':receipt['wall_seconds']}),flush=True)
    except BaseException as exc:
        receipt.update(status='STOP_PARTIAL_RESULT',error_type=type(exc).__name__,error=str(exc),
            traceback=traceback.format_exc(),completed_at_utc=utc(),wall_seconds=time.monotonic()-started)
        if not (dest/'pack.json').exists():
            receipt['pack_sha256']=make_pack(dest,case_id,g,source,lam,raw_sha,coeff_sha,
                'STOP_PARTIAL_RESULT',getattr(exc,'code','NUMERICALLY_UNRESOLVED'))
        write(dest/'failure-receipt.json',receipt)
        raise

def read_pack(repo,path,digest):
    imports(repo)
    from experiments.bodymap_b2_passive_loss.verification.pack_v0 import old_reader
    p=old_reader(path,digest)
    assert p['outcome']['implementation_conformance']=='UNRESOLVED'
    assert p['outcome']['effect']=='UNKNOWN'
    assert p['source_evidence']['evidence_class']=='RECOMPUTED'
    assert p['source_evidence']['actual_run_samples_sha256'] is None
    print(json.dumps({'pack':path.name,'sha256':digest,'status':'FRESH_PROCESS_READBACK_PASS'}))

def negatives(repo):
    """One invocation/family of pinned, engineering-accepted candidate probes.

    They remain candidate diagnostics; independent mutation adjudication is
    expressly assigned to Muse after submission. No additional scientific solve.
    """
    import numpy as np
    guard(repo); imports(repo)
    from experiments.bodymap_b2_passive_loss.verification import mutations
    from experiments.bodymap_b2_passive_loss.geometry_binding import resolve_geometry
    from experiments.bodymap_b2_passive_loss.source_binding import consumed_source
    dest=PACKAGE/'negative'; dest.mkdir(exist_ok=False)
    g=resolve_geometry('M0_REST'); source=consumed_source()
    assert source['buffer'].tobytes()==(PACKAGE/'source.le-f64').read_bytes()
    dirs=sorted((PACKAGE/'scientific').iterdir())
    def loaded(path):
        with np.load(path,allow_pickle=False) as data:
            return {k:(v.item() if v.ndim==0 else v) for k,v in data.items()}
    null=loaded(dirs[0]/'arrays.npz'); full=loaded(dirs[3]/'arrays.npz')
    phases={'NEG-LAMBDA':'input','ACTIVE-ZY':'internal_physics','SWAP-COEFF':'internal_law',
        'SWAP-LOAD':'terminal_identity','SWAP-GEOM-PORT':'geometry_identity',
        'RAW-FORGE':'waveform_provenance','LOSS-IGNORED':'coefficient_identity',
        'OLD-ATTENUATION':'law_identity','SHA-SOURCE':'source_provenance'}
    results=[]
    for name in mutations.EXPECTED:
        result=mutations.run_one(name,case=g,null=null,full=full,
            pressure_null=null['pressure_pa'],pressure_full=full['pressure_pa'],source=source)
        result.update(phase=phases[name],invocations_this_family=1,core_pin=PIN,
            oracle_pin=ORACLE_PIN,independent_adjudication='PENDING_SUPERVISOR',
            input_artifact_refs=['../scientific/'+dirs[0].name+'/arrays.npz','../scientific/'+dirs[3].name+'/arrays.npz'])
        write(dest/(name+'.json'),result); print(json.dumps(result),flush=True); results.append(result)
        # Each refusal has its own pack and exact coefficient reference.
        pd=dest/name; pd.mkdir()
        coeff=json.loads((dirs[3]/'coefficient-manifest.json').read_text())
        write(pd/'coefficient-manifest.json',coeff)
        make_pack(pd,'negative-'+name,g,source,1.,None,sha(pd/'coefficient-manifest.json'),
            'NEGATIVE_REFUSED' if result['actual']==mutations.EXPECTED[name] else 'NEGATIVE_UNRESOLVED',result['actual'])
    write(dest/'summary.json',{'results':results,'candidate_diagnostic_only':True,
        'independent_review':'PENDING_SUPERVISOR','invocations':len(results)})
    assert all(r['actual']==mutations.EXPECTED[r['fixture']] for r in results)

def compare_study():
    import numpy as np
    dirs=sorted((PACKAGE/'scientific').iterdir())
    a=[dict(np.load(d/'arrays.npz',allow_pickle=False)) for d in dirs]
    report={'self_check_only':True,'independent_study_oracle':'PENDING_SUPERVISOR',
        'implementation_conformance':'UNRESOLVED','effect':'UNKNOWN','near_null':{},'repeated_null':{}}
    for j,g in enumerate(GEOMS):
        null=a[j*4]; near=a[j*4+1]; repeat=a[12+j]
        nz=1.21*343/(math.pi*float(null['radii_m'][0])**2); nh=1.21*2*math.pi*800/(4*math.pi*.20)
        values={}
        for k,scale in (('HU',1.),('Zin',nz),('Hp',nh)):
            v=float(np.max(np.abs(near[k]-null[k])/np.maximum(scale,np.abs(null[k]))))
            values[k]=v
        values['raw_l2']=float(np.linalg.norm(near['pressure_pa']-null['pressure_pa'])/np.linalg.norm(null['pressure_pa']))
        values['ok']=all(v<=1e-4 for v in values.values())
        report['near_null'][g]=values
        rr=float(np.linalg.norm(repeat['pressure_pa']-null['pressure_pa'])/np.linalg.norm(null['pressure_pa']))
        report['repeated_null'][g]={'raw_l2':rr,'ok':rr<=1e-12,
            'raw_sha_equal':sha(dirs[j*4]/'raw-pressure.le-f64')==sha(dirs[12+j]/'raw-pressure.le-f64')}
    zero,full=a[0],a[3]; hpstar=1.21*2*math.pi*800/(4*math.pi*.20)
    hp=float(np.max(np.abs(full['Hp']-zero['Hp'])/np.maximum(hpstar,np.abs(zero['Hp']))))
    raw=float(np.linalg.norm(full['pressure_pa']-zero['pressure_pa'])/np.linalg.norm(zero['pressure_pa']))
    d=float(np.max(full['D32']/full['Pstar']))
    report['candidate_effect_floor']={'normalized_hp_difference':hp,'raw_l2':raw,
        'max_D32_over_Pstar':d,'three_floors_exceeded':hp>1e-6 and raw>1e-6 and d>1e-10,
        'interpretation':'CANDIDATE_NUMBERS_ONLY; no EFFECT recognition before all independent checks'}
    report['null_self_checks_ok']=all(r['ok'] for r in report['near_null'].values()) and all(r['ok'] for r in report['repeated_null'].values())
    write(PACKAGE/'candidate-comparisons.json',report)
    assert report['null_self_checks_ok']

def run(repo):
    guard(repo); started=time.monotonic()
    write(PACKAGE/'attempt-start.json',{'started_at_utc':utc(),'package_attempts':1,'retries':0,
        'scientific_max':15,'wall_cap_seconds':3600,'runner_sha256':sha(__file__)})
    ledger={'engineering_started':0,'engineering_completed':0,'scientific_started':0,
        'scientific_completed':0,'negative_invocations':0,'study_attempts':0,'retries':0,'processes':[]}
    def launch(args,label):
        remaining=3600-(time.monotonic()-started)
        assert remaining>0,'WALL_CAP_EXCEEDED'
        base=PACKAGE/(label+'.stdout.log'); err=PACKAGE/(label+'.stderr.log')
        before=time.monotonic()
        with base.open('x') as out,err.open('x') as stderr:
            p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--repo',str(repo),*args],
                stdout=out,stderr=stderr,timeout=remaining)
        ledger['processes'].append({'label':label,'returncode':p.returncode,'wall_seconds':time.monotonic()-before})
        assert p.returncode==0,f'{label}: nonzero exit {p.returncode}'
    try:
        for group,defs in (('engineering',ENG),('scientific',STUDY)):
            if group=='scientific': ledger['study_attempts']=1
            for i,_ in enumerate(defs):
                ledger[group+'_started']+=1
                launch(['worker','--group',group,'--index',str(i)],f'{group}-{i+1:02d}')
                ledger[group+'_completed']+=1
                print(json.dumps({k:v for k,v in ledger.items() if k!='processes'}),flush=True)
        launch(['negative'],'negative')
        ledger['negative_invocations']=9
        compare_study()
        for pack in sorted(PACKAGE.glob('*/*/pack.json')):
            label='readback-'+pack.parent.name
            launch(['read-pack','--path',str(pack),'--digest',sha(pack)],label)
        guard(repo)
        ledger['status']='COMPLETED_CANDIDATE_SUBMISSION_REVIEW_PENDING'
    except BaseException as exc:
        ledger.update(status='STOP_PRESERVE_ALL_PARTIAL_RESULTS',error=str(exc),traceback=traceback.format_exc())
        raise
    finally:
        ledger['negative_invocations']=len(list((PACKAGE/'negative').glob('*.json')))-(1 if (PACKAGE/'negative/summary.json').exists() else 0)
        ledger.update(finished_at_utc=utc(),wall_seconds=time.monotonic()-started,
            implementation_conformance='UNRESOLVED',effect='UNKNOWN',
            full_verified_source_state='UNKNOWN',source_evidence_class='RECOMPUTED')
        write(PACKAGE/'run-receipt.json',ledger)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',type=Path,required=True)
    sub=ap.add_subparsers(dest='operation',required=True)
    sub.add_parser('run'); w=sub.add_parser('worker'); w.add_argument('--group',choices=['engineering','scientific'],required=True); w.add_argument('--index',type=int,required=True)
    sub.add_parser('negative'); r=sub.add_parser('read-pack'); r.add_argument('--path',type=Path,required=True); r.add_argument('--digest',required=True)
    args=ap.parse_args(); repo=args.repo.resolve()
    if args.operation=='run': run(repo)
    elif args.operation=='worker': worker(repo,args.group,args.index)
    elif args.operation=='negative': negatives(repo)
    elif args.operation=='read-pack': read_pack(repo,args.path,args.digest)
