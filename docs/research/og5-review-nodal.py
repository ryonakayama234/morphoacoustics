"""Independent design review: six pressure nodes vs 20-state/frozen oracle.
No production Core imports; fixed nonzero-sin frequency anchors only.
"""
import copy, hashlib, itertools, json, struct
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
u_ref=1e-6
z_ref=1.2*343/.0003
p_ref=z_ref*u_ref
names='ABCDE'
lengths=dict(zip(names,[.08,.09,.06,.07,.05]))
nodes={'A':(0,1),'B':(1,2),'C':(1,3),'D':(2,4),'E':(2,5)}

def nodal(f,area,load,scale):
    # Pressure-only Dirichlet-to-Neumann assembly, six node unknowns;
    # not the archived 20-state system or its impedance recursion.
    areas=dict(zip(names,[.0003,.0003,area,.0003,.0006]))
    y=np.zeros((6,6),complex)
    coeff={}
    for organ,(a,b) in nodes.items():
        th=2*np.pi*f*lengths[organ]/343
        z=(1.2*343/areas[organ])/z_ref
        d=1/(1j*z*np.sin(th)); c=np.cos(th)
        y[a,a]+=c*d; y[a,b]-=d
        y[b,a]-=d; y[b,b]+=c*d
        coeff[organ]=(c,d)
    for organ,node in [('C',3),('D',4),('E',5)]:
        if organ!='C' or load=='matched':
            y[node,node]+=z_ref/(1.2*343/areas[organ])
    rhs=np.zeros(6,complex); rhs[0]=scale*(1+.4j)
    ps=np.linalg.solve(y,rhs)
    state={}
    for organ,(a,b) in nodes.items():
        c,d=coeff[organ]
        state[organ+'.in']=np.array([ps[a],d*(c*ps[a]-ps[b])])
        state[organ+'.out']=np.array([ps[b],d*(ps[a]-c*ps[b])])
    return state

def global20(f,area,load,scale):
    areas=dict(zip(names,[.0003,.0003,area,.0003,.0006]))
    m=np.zeros((20,20),complex); rhs=np.zeros(20,complex)
    idx={n+'.'+e:(4*i+2*j,4*i+2*j+1) for i,n in enumerate(names) for j,e in enumerate(['in','out'])}
    row=0
    for n in names:
        pi,ui=idx[n+'.in']; po,uo=idx[n+'.out']
        th=2*np.pi*f*lengths[n]/343; c=np.cos(th); s=np.sin(th)
        z=(1.2*343/areas[n])/z_ref
        m[row,[pi,po,uo]]=[1,-c,-1j*z*s]; row+=1
        m[row,[ui,po,uo]]=[1,-1j*s/z,-c]; row+=1
    for parent,c1,c2 in [('A.out','B.in','C.in'),('B.out','D.in','E.in')]:
        for child in [c1,c2]:
            m[row,[idx[parent][0],idx[child][0]]]=[1,-1]; row+=1
        m[row,[idx[parent][1],idx[c1][1],idx[c2][1]]]=[1,-1,-1]; row+=1
    m[row,idx['A.in'][1]]=1; rhs[row]=scale*(1+.4j); row+=1
    for n in 'CDE':
        pi,ui=idx[n+'.out']
        if n=='C' and load=='closed': m[row,ui]=1
        else: m[row,[pi,ui]]=[1,-(1.2*343/areas[n])/z_ref]
        row+=1
    assert row==20
    x=np.linalg.solve(m,rhs)
    return {k:x[list(v)] for k,v in idx.items()}

def encode(x):
    if isinstance(x,(float,int)) and not isinstance(x,bool): return b'd'+struct.pack('>d',0.0 if x==0 else float(x))
    if isinstance(x,str):
        b=x.encode('ascii'); return b's'+struct.pack('>I',len(b))+b
    if isinstance(x,list): return b'l'+struct.pack('>I',len(x))+b''.join(map(encode,x))
    if isinstance(x,dict): return b'm'+struct.pack('>I',len(x))+b''.join(encode(k)+encode(x[k]) for k in sorted(x))
    raise TypeError(type(x))

gold=json.loads((ROOT/'og5-blueprint-goldens.json').read_text())
hashes={}
for key in gold['expected']:
    b=copy.deepcopy(gold['baseline_blueprint'])
    if key=='c_area_0006': b['organs'][2]['area_m2']=.0006
    if key=='c_revision_r2': b['organs'][2]['revision']='r2'
    if key=='reversed_collection_order':
        for c in ['organs','junctions','loads']: b[c].reverse()
    for c,k in [('organs','id'),('junctions','id'),('loads','port')]: b[c].sort(key=lambda v:v[k])
    hashes[key]='sha256:'+hashlib.sha256(gold['domain'].encode('ascii')+b'\0'+encode(b)).hexdigest()
    assert hashes[key]==gold['expected'][key]

frozen=json.loads((ROOT/'og5-wolfram-gate-a-result.json').read_text())
frozen_error=0
for r in frozen['records']:
    st=nodal(r['frequency_hz'],r['c_area_m2'],r['c_load'],r['source_scale'])
    assert all(np.isfinite(v).all() for v in st.values())
    for k,v in r['port_states'].items():
        want=np.array([complex(*v['p_pa'])/p_ref,complex(*v['u_m3_s'])/u_ref])
        frozen_error=max(frozen_error,float(np.max(np.abs(st[k]-want))))
all_error=0
for f,a,l,s in itertools.product([80,250,400,733,997,1200,2000,4000],[.00015,.0003,.0006],['matched','closed'],[1,.5,-1]):
    one=nodal(f,a,l,s); two=global20(f,a,l,s)
    assert all(np.isfinite(v).all() for v in [*one.values(),*two.values()])
    all_error=max(all_error,max(float(np.max(np.abs(one[k]-two[k]))) for k in one))
assert frozen_error <= 1e-10 and all_error <= 1e-10, (frozen_error,all_error)
print(json.dumps({'archived_8_vs_independent_nodal_max_scaled_error':frozen_error,'all_144_nodal_vs_global20_max_scaled_error':all_error,'golden_hashes_python':hashes},indent=2))
