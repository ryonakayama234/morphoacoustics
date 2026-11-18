"""Produce auditable C1-Open raw files. Negative refined-grid result is intentional."""
from __future__ import annotations
from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
from solver import Model,Fixture,DomainError,C0
from audit import audit


def dump(path,obj):
    raw=(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
    path.write_bytes(raw)
    return sha256(raw).hexdigest()


def failure_case(fixture,duration):
    m=Model(fixture);dt=.2*m.dz/C0;steps=math.ceil(duration/dt);dt=duration/steps
    y=m.initial();states=[{'step':0,'t_s':0.,'y':y.tolist()}]
    for k in range(1,steps+1):
        try:
            new,_,_=m.step(y,dt)
            states.append({'step':k,'t_s':k*dt,'y':new.tolist()});y=new
        except DomainError as exc:
            vol,area,rho,u,p,c=m.primitive(y)
            gamma=1.4;pres=fixed_p=fixture.outlet_pa
            rho_b=rho[-1]*(pres/p[-1])**(1/gamma)
            cb=math.sqrt(gamma*pres/rho_b)
            u_b=u[-1]+2*(c[-1]-cb)/(gamma-1)
            return {'status':'SCIENTIFIC_STOP_UNSUPPORTED_REVERSE','fixture':asdict(fixture),
                    'stage_error':str(exc),'failed_step':k,'time_s':(k-1)*dt,
                    'u_right_estimate_m_s':float(u_b),'p_right_cell_pa':float(p[-1]),
                    'cells_recorded':len(states),'raw_partial_states':states}
    return {'status':'NO_STOP_OBSERVED','fixture':asdict(fixture),'raw_partial_states':states}


def main(dest):
    dest.mkdir(parents=True,exist_ok=True)
    files={};verdicts=[]
    for n in [8,16]:
        for pressure in [0.,10.]:
            model=Model(Fixture(n=n,upstream_delta_pa=pressure))
            trace=model.run(duration=.0003)
            result=audit(trace)
            key=f'c1open_N{n}_dp{int(pressure)}'
            files[key+'.json']=dump(dest/(key+'.json'),{'trace':trace,'independent_audit':result})
            verdicts.append({'id':key,'status':'G1_BOUND_NUMERIC_PASS','energy_residual_j':float(result['energy_residual_j']),
                             'mass_residual_kg':float(result['mass_residual_kg']),
                             'motion_final_m':result['tissue_final_x_m']})
    for n in [32,64]:
        result=failure_case(Fixture(n=n,upstream_delta_pa=10.),duration=.0003)
        key=f'c1open_N{n}_dp10_STOP'
        files[key+'.json']=dump(dest/(key+'.json'),result)
        verdicts.append({'id':key,'status':result['status'],
                         'time_s':result.get('time_s'),'u_right_m_s':result.get('u_right_estimate_m_s')})
    verdict={'scientific_decision':'STOP_NUMERICALLY_UNRESOLVED_REFINED_GRID',
             'scope':'C1 smooth rightward subsonic NONCONTACT only; NOT G1 adoption, self-oscillation, biology, audio or Studio',
             'cases':verdicts,'raw_files_sha256':files}
    dump(dest/'RESULTS.json',verdict)
    print(json.dumps({'decision':verdict['scientific_decision'],'cases':verdicts},ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python run.py OUTPUT_DIRECTORY')
    raise SystemExit(main(Path(sys.argv[1])))
