"""Independent research observer: re-derives SI state and RK4 face/force laws.

Never imports solver.py or its receipts. Reconstructs all stage physics from raw
states, face flux, ghost states and cell volume, checks independent updates.
"""
from __future__ import annotations
import math
import numpy as np

class AuditError(AssertionError):
    pass


def must(test, why):
    if not bool(test): raise AuditError(why)


def clos(a,b,atol=1e-12,rtol=1e-10):
    return np.allclose(np.asarray(a),np.asarray(b),atol=atol,rtol=rtol)


def audit(trace):
    must(trace.get('schema')=='vf1b2.c1open.research-trace.v0','SCHEMA')
    f=trace['fixture']; n=f['n']; dt=trace['dt']; steps=trace['steps']
    must(type(n) is int and 2<=n<=64 and type(steps) is int and steps>0 and dt>0,'HEADER')
    rows=trace['rows']; must(len(rows)==steps+1,'TRUNCATED_TRACE')
    must(f['outlet_pa']==101325. and f['upstream_delta_pa'] in (0.,10.,50.),'FIXTURE')
    must(f['locked'] is False or f['locked'] is True,'LOCKED')
    Lg=.01; ell=.01; h0=.0002; Patm=101325.; gam=1.4; R=287.05; T0=293.15
    z=np.linspace(0,Lg,n+1); dz=Lg/n
    face_basis=np.array([1-z/Lg,z/Lg]).T
    g=np.column_stack((2*ell*(dz-(z[1:]**2-z[:-1]**2)/(2*Lg)),
                       2*ell*((z[1:]**2-z[:-1]**2)/(2*Lg))))
    vol0=2*ell*h0*dz
    M=np.array([1e-4,1e-4]); K=np.array([[190.,-40.],[-40.,260.]])
    D=np.array([.02,.03]); baseV=n*vol0
    rho0=Patm/(R*T0); Et0=Patm/(gam-1.)
    def split(y):
        y=np.asarray(y,dtype=float)
        must(y.shape==(3*n+4,) and np.all(np.isfinite(y)),'BAD_STATE')
        return y[:n],y[n:2*n],y[2*n:3*n],y[3*n:3*n+2],y[3*n+2:]
    def thermo(y):
        mm,qq,ee,x,v=split(y)
        vols=vol0+g@x; areas=2*ell*(h0+face_basis@x)
        must(np.all(vols>0) and np.all(areas>2*ell*.0001),'CONTACT_OR_VOLUME')
        must(np.all(mm>0) and np.all(ee>0),'NEGATIVE_FLUID')
        rho=mm/vols; u=qq/mm; p=(gam-1)*(ee-.5*qq*qq/mm)/vols
        must(np.all(p>0) and np.all(np.isfinite(p)),'INVALID_EOS')
        c=np.sqrt(gam*p/rho)
        must(np.max(abs(u)/c)<.1+1e-12,'MACH')
        return vols,areas,rho,u,p,c
    def henergy(y):
        mm,q,E,x,v=split(y); vols,*_=thermo(y)
        return float(np.sum(E)+.5*(v*(M*v)).sum()+.5*x@(K@x)+Patm*(vols.sum()-baseV))
    def flux_side(ri,ui,pi):
        energy=pi/(gam-1)+.5*ri*ui*ui
        return (np.array([ri,ri*ui,energy]),np.array([ri*ui,ri*ui*ui+pi,ui*(energy+pi)]))
    def independent_stage(stage):
        y=np.asarray(stage['y']); mm,qq,ee,x,v=split(y)
        vol,area,rho,u,p,c=thermo(y)
        must(clos(p,stage['pressure'],atol=1e-9,rtol=1e-12),'PRESSURE_FIELD')
        l=tuple(stage['ghost_left']); r=tuple(stage['ghost_right'])
        must(min(l[0],l[2],r[0],r[2])>0,'INVALID_GHOST')
        # Independent characteristic boundary compatibility checks.
        c0=math.sqrt(gam*R*T0); cl=math.sqrt(gam*l[2]/l[0]); cr=math.sqrt(gam*r[2]/r[0])
        must(abs(l[1]-2*cl/(gam-1)-(u[0]-2*c[0]/(gam-1)))<=1e-7,'INLET_CHARACTERISTIC')
        must(abs(l[2]*(T0/(cl*cl/(gam*R)))**(gam/(gam-1))-(Patm+f['upstream_delta_pa']))<=1e-4,'INLET_TOTAL_P')
        must(abs(r[2]-f['outlet_pa'])<=1e-8,'OUTLET_STATIC_P')
        must(abs(r[1]+2*cr/(gam-1)-(u[-1]+2*c[-1]/(gam-1)))<=1e-7,'OUTLET_CHARACTERISTIC')
        must(abs(r[0]-rho[-1]*(r[2]/p[-1])**(1/gam))<=1e-9,'OUTLET_ENTROPY')
        states=[l]+list(zip(rho,u,p))+[r]
        flux=np.zeros((n+1,3))
        for j in range(n+1):
            qa,fa=flux_side(*states[j]); qb,fb=flux_side(*states[j+1]);
            alpha=max(abs(states[j][1])+math.sqrt(gam*states[j][2]/states[j][0]),
                      abs(states[j+1][1])+math.sqrt(gam*states[j+1][2]/states[j+1][0]))
            flux[j]=area[j]*(0.5*(fa+fb)-0.5*alpha*(qb-qa))
        must(clos(flux,stage['face_flux'],atol=1e-7,rtol=2e-11),'FACE_FLUX')
        rate=g@v if not f['locked'] else np.zeros(n)
        force=g.T@(p-Patm)
        must(clos(rate,stage['vol_rate'],atol=1e-12,rtol=1e-12),'WALL_MOTION')
        must(clos(force,stage['force'],atol=1e-11,rtol=1e-11),'BODY_FORCE')
        change=np.zeros(3*n+4)
        div=-(flux[1:]-flux[:-1])
        change[:n]=div[:,0]
        change[n:2*n]=div[:,1]+p*(area[1:]-area[:-1])
        change[2*n:3*n]=div[:,2]-p*rate
        if not f['locked']:
            change[3*n:3*n+2]=v
            change[3*n+2:]=(force-K@x-D*v)/M
        obs={
            'mass_flux':flux[0,0]-flux[-1,0],
            'momentum_flux':flux[0,1]-flux[-1,1],
            'energy_flux':flux[0,2]-flux[-1,2],
            'geom_mom':np.dot(p,area[1:]-area[:-1]),
            'wall_work_fluid':-np.dot(p,rate),
            'damping':np.dot(D*v,v) if not f['locked'] else 0.,
            'body_force_work':np.dot(force,v) if not f['locked'] else 0.}
        return change,obs
    initial=np.asarray(rows[0]['y']); m0,q0,E0,x0,v0=split(initial)
    must(rows[0]['step']==0 and rows[0]['time']==0.0,'INITIAL_TIME')
    must(clos(x0,f['x0'],atol=0,rtol=0) and clos(v0,f['v0'],atol=0,rtol=0),'INITIAL_TISSUE')
    vinit,*_=thermo(initial)
    must(clos(m0,rho0*vinit,atol=1e-16,rtol=1e-12),'INITIAL_MASS')
    must(clos(q0,0,atol=1e-16,rtol=0),'INITIAL_MOMENTUM')
    must(clos(E0,Et0*vinit,atol=1e-13,rtol=1e-12),'INITIAL_ENERGY')
    t0h=henergy(initial); y0=initial
    totals={k:0. for k in ('mass_flux','momentum_flux','energy_flux','geom_mom','wall_work_fluid','damping','body_force_work')}
    max_energy=0.; max_mass=0.; max_mom=0.
    for j in range(1,len(rows)):
        row=rows[j]
        must(row['step']==j and abs(row['time']-j*dt)<=1e-14,'MISSING_OR_REORDERED_TIME')
        must(len(row.get('stages',[]))==4,'MISSING_STAGE')
        stages=[np.asarray(t['y']) for t in row['stages']]
        deriv=[];obs=[]
        for s in row['stages']:
            d,o=independent_stage(s);deriv.append(d);obs.append(o)
        must(clos(stages[0],y0,atol=1e-15,rtol=1e-14),'STAGE0_BINDING')
        must(clos(stages[1],y0+dt*.5*deriv[0],atol=1e-14,rtol=1e-12),'STAGE1_KINEMATICS')
        must(clos(stages[2],y0+dt*.5*deriv[1],atol=1e-14,rtol=1e-12),'STAGE2_KINEMATICS')
        must(clos(stages[3],y0+dt*deriv[2],atol=1e-14,rtol=1e-12),'STAGE3_KINEMATICS')
        predicted=y0+dt*(deriv[0]+2*deriv[1]+2*deriv[2]+deriv[3])/6
        y1=np.asarray(row['y']);must(clos(y1,predicted,atol=1e-14,rtol=1e-11),'INDEPENDENT_STEP_DYNAMICS')
        for k in totals:
            weighted=(obs[0][k]+2*obs[1][k]+2*obs[2][k]+obs[3][k])/6
            must(abs(float(row['interval'][k])-weighted)<=max(1e-9,abs(weighted)*1e-10),'INTERVAL_'+k)
            totals[k]+=dt*weighted
            must(abs(float(row['cumulative'][k])-totals[k])<=max(1e-11,abs(totals[k])*1e-10),'CUMULATIVE_'+k)
        prevm,prevq,prevE,_,_=split(y0); mm,qq,EE,_,_=split(y1)
        r_mass=mm.sum()-prevm.sum()-dt*row['interval']['mass_flux']
        r_mom=qq.sum()-prevq.sum()-dt*(row['interval']['momentum_flux']+row['interval']['geom_mom'])
        r_energy=henergy(y1)-henergy(y0)-dt*(row['interval']['energy_flux']-row['interval']['damping'])
        max_mass=max(max_mass,abs(r_mass));max_mom=max(max_mom,abs(r_mom));max_energy=max(max_energy,abs(r_energy))
        y0=y1
    for k in totals:
        must(abs(totals[k]-trace['integrals'][k])<=max(1e-11,abs(totals[k])*1e-10),'TOTAL_'+k)
    m_end,q_end,_,_,_=split(y0)
    r_mass=float(np.sum(m_end)-np.sum(m0)-totals['mass_flux'])
    r_mom=float(np.sum(q_end)-np.sum(q0)-totals['momentum_flux']-totals['geom_mom'])
    r_energy=henergy(y0)-t0h-totals['energy_flux']+totals['damping']
    E_scale=max(abs(t0h),abs(henergy(y0)),abs(totals['energy_flux']),1e-10)
    relE=abs(r_energy)/E_scale
    must(abs(r_mass)<=1e-9*max(np.sum(m0),abs(totals['mass_flux']),1e-12),'MASS_LEDGER')
    must(abs(r_mom)<=1e-6*max(abs(totals['momentum_flux']),abs(totals['geom_mom']),1e-12),'MOMENTUM_LEDGER')
    must(abs(r_energy)<=1e-10 and relE<=1e-5,'ENERGY_LEDGER')
    return {'decision':'G1_NUMERICAL_CONTROL_PASS','steps':steps,'mass_residual_kg':r_mass,
            'momentum_residual_kg_m_s':r_mom,'energy_residual_j':r_energy,
            'energy_relative':relE,'max_step_mass_kg':max_mass,
            'max_step_momentum_kg_m_s':max_mom,'max_step_energy_j':max_energy,
            'tissue_final_x_m':y0[3*n:3*n+2].tolist()}
