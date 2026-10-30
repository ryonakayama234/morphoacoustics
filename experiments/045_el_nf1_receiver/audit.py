"""EL-NF1 independent evidence arithmetic and holdout integrity audit.

Checks numerical reports from stored observations, NOT physics against raw SOFA.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from statistics import median

import numpy as np

def check(e:dict)->dict:
    if e.get('schema_version')!='el-nf1-evidence-v1' or e.get('adoption')!='NOT_ADOPTED':
        raise ValueError('INVALID: research evidence identity or adoption')
    n=e.get('directions')
    if type(n) is not int or not 10<=n<=49:raise ValueError('INVALID: directions count')
    rows=e.get('records')
    if not isinstance(rows,list) or len(rows)!=n*2*3:
        raise ValueError('INVALID: incomplete direction/fold/model records')
    lookup={}
    for row in rows:
        key=(row['direction'],row['fold'],row['model'])
        if key in lookup or not 0<=row['direction']<n or row['fold'] not in ('F30','F40') or row['model'] not in ('B','C0','C1'):
            raise ValueError('INVALID: duplicate/missing model or fold identity')
        target=row['target_measurement_index']
        train=row['training_measurement_indices']
        ref=row['baseline_measurement_index']
        if len(train)!=2 or len({target,*train})!=3:
            raise ValueError('INVALID: training/target holdout leakage')
        if row['fold']=='F30' and ref in (target,*train):
            raise ValueError('INVALID: F30 0.5m reference not independent')
        if row['fold']=='F40' and ref!=train[1]:
            raise ValueError('INVALID: F40 0.5m reference mismatch')
        errors=row['absolute_ild_errors_db']
        if len(errors)!=4 or not all(math.isfinite(x) and x>=0 for x in errors):
            raise ValueError('INVALID: four finite nonnegative ILD errors')
        itd=row['abs_itd_error_us']
        if not math.isfinite(itd) or itd<0:
            raise ValueError('INVALID: nonnegative finite ITD error')
        lookup[key]=row
    for d in range(n):
        for fold in ('F30','F40'):
            group=[lookup.get((d,fold,m)) for m in ('B','C0','C1')]
            if any(x is None for x in group):
                raise ValueError('INVALID: missing paired model observations')
            if len({tuple([x['target_measurement_index'],*x['training_measurement_indices'],x['baseline_measurement_index']]) for x in group})!=1:
                raise ValueError('INVALID: paired models use inconsistent measurements')
        x=lookup[(d,'F30','B')]
        y=lookup[(d,'F40','B')]
        if x['target_measurement_index']!=y['training_measurement_indices'][0] or x['training_measurement_indices'][1]!=y['target_measurement_index'] or x['baseline_measurement_index']!=y['baseline_measurement_index']:
            raise ValueError('INVALID: cross-fold direction mapping leaked or disagrees')
    def med(model,fold=None,field='absolute_ild_errors_db'):
        selected=[v for v in rows if v['model']==model and (fold is None or v['fold']==fold)]
        return float(median(q for v in selected for q in (v[field] if isinstance(v[field],list) else [v[field]])))
    summary={m:dict(median_ild_error_db=med(m),
                    F30_median_ild_error_db=med(m,'F30'),
                    F40_median_ild_error_db=med(m,'F40'),
                    median_abs_itd_error_us=med(m,field='abs_itd_error_us')) for m in ('B','C0','C1')}
    for m in summary:
        for field,value in summary[m].items():
            if not math.isclose(value,e['statistics'][m][field],rel_tol=0,abs_tol=1e-10):
                raise ValueError('INVALID: score summary does not match raw observations')
    array={m:np.asarray([[v for fold in ('F30','F40') for v in lookup[(d,fold,m)]['absolute_ild_errors_db']]
                         for d in range(n)]) for m in ('B','C1')}
    rng=np.random.default_rng(20261030)
    diffs=[]
    for _ in range(2000):
        sampled=rng.integers(0,n,size=n)
        diffs.append(float(np.median(array['B'][sampled])-np.median(array['C1'][sampled])))
    ci=np.percentile(diffs,[2.5,97.5])
    if not np.allclose(ci,e['ild_improvement_ci95_db'],atol=1e-10,rtol=0):
        raise ValueError('INVALID: bootstrap CI does not reproduce')
    b,c=summary['B'],summary['C1']
    go=(c['median_ild_error_db']<=.8*b['median_ild_error_db'] and ci[0]>0
        and c['F30_median_ild_error_db']<b['F30_median_ild_error_db']
        and c['F40_median_ild_error_db']<b['F40_median_ild_error_db']
        and c['median_abs_itd_error_us']<=b['median_abs_itd_error_us']+25)
    verdict='GO_LIMITED_NUMERICAL_CANDIDATE' if go else 'REVISE_OR_REJECT'
    if e.get('numerical_verdict')!=verdict:
        raise ValueError('INVALID: reported verdict does not follow frozen gates')
    if e.get('g4_listening')!='PENDING' or e.get('g5_independent_review')!='PENDING':
        raise ValueError('INVALID: numeric CI cannot authorize subjective/adoption gates')
    return dict(audit='EVIDENCE_ARITHMETIC_VERIFIED_ONLY',directions=n,verdict=verdict,
                medians=summary,ci95=ci.tolist())

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--evidence',required=True,type=Path)
    args=ap.parse_args()
    def reject(token:str):
        raise ValueError('INVALID: nonfinite JSON token '+token)
    evidence=json.loads(args.evidence.read_text(encoding='utf-8'),parse_constant=reject)
    print(json.dumps(check(evidence),sort_keys=True,allow_nan=False))

if __name__=='__main__':
    main()
