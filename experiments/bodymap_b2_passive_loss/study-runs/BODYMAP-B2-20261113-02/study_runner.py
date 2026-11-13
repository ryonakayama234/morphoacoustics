"""Frozen orchestration only; imports scientific code from exact clean Core pin.
Each case executes once in a fresh process. Append-only outputs and journal.
No independent scientific acceptance is claimed by executor.
"""
import argparse, contextlib, datetime, hashlib, io, json, math, os
from pathlib import Path
import subprocess, sys, time, traceback
PIN='0bb60cc227d231ec1cb67b701a849172ed92164b'
NAMES=('M0_REST','U6_REF','U19_REF')
LAMBDAS=(0.0,1e-6,0.5,1.0)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,o):
    with p.open('x') as f:
        json.dump(o,f,indent=2,allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
def git(repo,*a): return subprocess.check_output(['git','-C',str(repo),*a],text=True).strip()
def setup(repo):
    assert git(repo,'rev-parse','HEAD')==PIN
    assert not git(repo,'status','--porcelain=v1','--untracked-files=all')
    sys.path[:0]=[str(repo),str(repo/'src')]
def one(repo,out,name,lam,case_id):
    setup(repo)
    import numpy as np
    from experiments.bodymap_b2_passive_loss.geometry_binding import resolve_geometry
    from experiments.bodymap_b2_passive_loss.source_binding import consumed_source
    from experiments.bodymap_b2_passive_loss.candidate.transfer import compute_case
    from experiments.bodymap_b2_passive_loss.candidate.pressure import projected_pressure
    from experiments.bodymap_b2_passive_loss.verification.physics import inspect, independent_integral
    from experiments.bodymap_b2_passive_loss.verification.pack_v0 import new_pack, write_once, old_reader
    from experiments.bodymap_b2_passive_loss.prereg_binding import MU,KAPPA,CP,GAMMA,T_REF,RHO,C,LAW,PREREG_CONTENT_SHA256
    out.mkdir(); started=now()
    write(out/'request.json',{'id':case_id,'case':name,'lambda':lam,'utc':started,'pid':os.getpid(),'core_pin':PIN})
    g=resolve_geometry(name); s=consumed_source()
    source_before=hashlib.sha256(s['buffer'].tobytes()).hexdigest()
    s['buffer'].flags.writeable=False
    c=compute_case(tuple(g['radii_m']),tuple(g['lengths_m']),lam)
    p=projected_pressure(s['buffer'],c['Hp'])
    # Persist candidate outputs before diagnostics, so diagnostic failure cannot lose a result.
    arrays={k:v for k,v in c.items() if isinstance(v,np.ndarray)}
    arrays.update(source_buffer=s['buffer'],source_Q=p['Q'],output_P=p['P'],raw_pa=p['pressure_pa'])
    with (out/'arrays.npz').open('xb') as f: np.savez_compressed(f,**arrays)
    assert source_before==p['source_sha256_le_f64']==hashlib.sha256(s['buffer'].tobytes()).hexdigest()
    diag=inspect(c)
    st=c['states']; pin=.5*np.real(st[:,0,0]*np.conj(st[:,0,1])); pout=.5*c['load_R']*abs(st[:,-1,1])**2
    pstar=.5*c['Zstar']*abs(st[:,0,1])**2
    d16=np.array([independent_integral(c,i,16) for i in range(351)])
    d32=np.array(diag['d32_over_pstar'])*pstar
    with (out/'power.npz').open('xb') as f: np.savez_compressed(f,Pin=pin,Pout=pout,Pstar=pstar,D16=d16,D32=d32,residual=pin-pout-d32)
    coeff={'law':LAW,'prereg_sha256':PREREG_CONTENT_SHA256,'geometry':g,'lambda':lam,'rho':RHO,'c':C,'mu':MU,'kappa':KAPPA,'cp':CP,'gamma':GAMMA,'T_ref':T_REF,'Pr':MU*CP/KAPPA,'Ks':RHO*C*C,'p_ref':RHO*C*C/GAMMA,'load_R':c['load_R'],'attenuation_np_m':0,'nominal_preset_not_measured_air':True}
    write(out/'coefficients.json',coeff)
    source_meta={k:v for k,v in s.items() if k not in ('buffer','Q')}
    source_meta.update(actual_run_samples_sha256=None,recomputed_samples_sha256=source_before,evidence_class='RECOMPUTED',full_verified_source_state='UNKNOWN',executor_chain_buffer_sha256=source_before,independent_chain_confirmation='PENDING_SUPERVISOR')
    pack=new_pack(evidence_id=case_id,utc=started,case_id=case_id,run_head=PIN,verification_head=None,geometry=g,source=source_meta,raw_sha256=p['raw_sha256_le_f64'],coefficient_ref='coefficients.json',coefficient_sha256=sha(out/'coefficients.json'),loss=lam,status='COMPLETED_PENDING_REVIEW')
    pack['complex_transfer']=[{'artifact_ref':'arrays.npz','sha256':sha(out/'arrays.npz'),'fields':['HU','Zin','Hp'],'units':['1','Pa*s/m3','Pa*s/m3'],'complex_encoding':'complex128 Re/Im lossless','grid_hz':[100,800,2]}]
    pack['physical_observables']=[{'artifact_ref':'power.npz','sha256':sha(out/'power.npz'),'fields':['Pin','Pout','Pstar','D16','D32','residual'],'normalization':'Uin=1'}]
    pack['medium_boundary_observer']['load_R']=c['load_R']
    digest=write_once(out/'pack.json',pack); old_reader(out/'pack.json',digest)
    write(out/'receipt.json',{'id':case_id,'geometry':g,'lambda':lam,'source':source_meta,'source_chain_consistent':True,'physics':diag,'raw_sha256_le_f64':p['raw_sha256_le_f64'],'pack_sha256':digest,'arrays_sha256':sha(out/'arrays.npz'),'started_utc':started,'completed_utc':now(),'core_pin':PIN,'runner_sha256':sha(Path(__file__)),'implementation_conformance':'UNRESOLVED','effect':'UNKNOWN','reviewer_status':'PENDING'})
    assert not git(repo,'status','--porcelain')
    print(json.dumps({'id':case_id,'status':'COMPLETED_PENDING_REVIEW','raw_sha256':p['raw_sha256_le_f64']}))
def orchestrate(repo,out):
    setup(repo); out.mkdir()
    t=time.monotonic(); budget_start=(out.parent/'engineering'/'stderr.log').stat().st_mtime; write(out/'STARTED.json',{'utc':now(),'pid':os.getpid(),'runner_sha256':sha(Path(__file__)),'max_scientific_evaluations':15,'study_attempt':1,'retries':0})
    defs=[(n,l,f'{n}-L{i}') for n in NAMES for i,l in enumerate(LAMBDAS)] + [(n,0.0,f'{n}-REPEAT-NULL') for n in NAMES]
    for n,l,cid in defs:
        remaining=3600-(time.time()-budget_start)
        if remaining<=0: raise TimeoutError('60 minute cap')
        with (out/'journal.jsonl').open('a') as f: f.write(json.dumps({'id':cid,'event':'STARTED','utc':now()})+'\n'); f.flush(); os.fsync(f.fileno())
        proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'case',str(repo),str(out/cid),n,repr(l),cid],capture_output=True,text=True,timeout=remaining)
        (out/f'{cid}.stdout.log').write_text(proc.stdout); (out/f'{cid}.stderr.log').write_text(proc.stderr)
        with (out/'journal.jsonl').open('a') as f: f.write(json.dumps({'id':cid,'event':'COMPLETED' if proc.returncode==0 else 'STOP','returncode':proc.returncode,'utc':now()})+'\n'); f.flush(); os.fsync(f.fileno())
        if proc.returncode: raise RuntimeError(f'STOP {cid}; no resume/retry permitted')
    import numpy as np
    from experiments.bodymap_b2_passive_loss.verification import mutations
    from experiments.bodymap_b2_passive_loss.source_binding import consumed_source
    from experiments.bodymap_b2_passive_loss.geometry_binding import resolve_geometry
    def load(cid):
        d=out/cid; a=dict(np.load(d/'arrays.npz')); r=json.loads((d/'receipt.json').read_text()); cf=json.loads((d/'coefficients.json').read_text()); a.update(radii_m=tuple(r['geometry']['radii_m']),lengths_m=tuple(r['geometry']['lengths_m']),Zstar=RHO*C/(math.pi*r['geometry']['radii_m'][0]**2),load_R=cf['load_R'],**{'lambda':r['lambda']}); return a
    from experiments.bodymap_b2_passive_loss.prereg_binding import RHO,C
    comparisons={}
    for n in NAMES:
        null=load(n+'-L0'); near=load(n+'-L1'); repeat=load(n+'-REPEAT-NULL'); zstar=null['Zstar']; hpstar=RHO*2*math.pi*800/(4*math.pi*.20)
        vals={k:float(np.max(abs(near[k]/scale-null[k]/scale)/np.maximum(1,abs(null[k]/scale)))) for k,scale in [('HU',1),('Zin',zstar),('Hp',hpstar)]}
        vals['near_raw_l2']=float(np.linalg.norm(near['raw_pa']-null['raw_pa'])/np.linalg.norm(null['raw_pa']))
        vals['repeat_raw_l2']=float(np.linalg.norm(repeat['raw_pa']-null['raw_pa'])/np.linalg.norm(null['raw_pa']))
        vals['candidate_null_checks_pass']=all(v<=1e-4 for k,v in vals.items() if k!='repeat_raw_l2') and vals['repeat_raw_l2']<=1e-12
        comparisons[n]=vals
    m0=load('M0_REST-L0'); full=load('M0_REST-L3')
    effect_hp=float(np.max(abs(full['Hp']-m0['Hp'])/np.maximum(hpstar,abs(m0['Hp']))))
    effect_raw=float(np.linalg.norm(full['raw_pa']-m0['raw_pa'])/np.linalg.norm(m0['raw_pa']))
    dmax=max(json.loads((out/'M0_REST-L3'/'receipt.json').read_text())['physics']['d32_over_pstar'])
    write(out/'candidate-comparisons.json',{'nulls':comparisons,'effect_floor_metrics':{'Hp':effect_hp,'raw_l2':effect_raw,'max_D_over_Pstar':dmax,'numerical_floor_exceeded':effect_hp>1e-6 and effect_raw>1e-6 and dmax>1e-10},'implementation_conformance':'UNRESOLVED','effect':'UNKNOWN','reason':'Independent full study oracle and source attribution review pending; metrics are candidate diagnostics only.'})
    negdir=out/'negative'; negdir.mkdir(); source=consumed_source()
    for name in mutations.EXPECTED:
        # Nonuniform M0 makes port reversal observable, as supervisor explicitly prescribed.
        capture=io.StringIO()
        with contextlib.redirect_stdout(capture):
            r=mutations.run_one(name,case=resolve_geometry('M0_REST'),null=m0,full=full,pressure_null=m0['raw_pa'],pressure_full=full['raw_pa'],source=source)
            print(json.dumps(r))
        write(negdir/(name+'.json'),r); (negdir/(name+'.stdout.log')).write_text(capture.getvalue())
    write(out/'COMPLETE.json',{'utc':now(),'scientific_evaluations_completed':15,'negative_invocations':9,'attempts':1,'retries':0,'study_wall_seconds':time.monotonic()-t,'total_wall_seconds_since_engineering_start':time.time()-budget_start,'implementation_conformance':'UNRESOLVED','effect':'UNKNOWN','reviewer_status':'PENDING'})
if __name__=='__main__':
    mode=sys.argv[1]; repo=Path(sys.argv[2]).resolve(); out=Path(sys.argv[3]).resolve()
    try:
        if mode=='case': one(repo,out,sys.argv[4],float(sys.argv[5]),sys.argv[6])
        elif mode=='study': orchestrate(repo,out)
        else: raise ValueError(mode)
    except BaseException as e:
        if out.is_dir():
            p=out/'STOP.json'
            if not p.exists(): write(p,{'utc':now(),'error':repr(e),'traceback':traceback.format_exc(),'implementation_conformance':'UNRESOLVED','effect':'UNKNOWN','no_resume':True})
        raise
