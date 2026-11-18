"""Research-only C1-Open: two-DOF tissue + quasi-1D moving-volume Euler.

Smooth noncontact, rightward subsonic, ideal-gas fixtures ONLY. No source voice,
biology, tract, contact, separation, audio, released ABI or negative damping.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

GAMMA = 1.4
R = 287.05
T0 = 293.15
P_AMB = 101325.0
LG = 0.010
ELL = 0.010
H0 = 0.0002
H_FLOOR = 0.0001
MASS = np.array([1e-4, 1e-4])
STIFF = np.array([[190., -40.], [-40., 260.]])
DAMP = np.array([.02, .03])
C0 = math.sqrt(GAMMA*R*T0)


class DomainError(ValueError):
    pass


@dataclass(frozen=True)
class Fixture:
    n: int = 8
    upstream_delta_pa: float = 10.0
    outlet_pa: float = P_AMB
    locked: bool = False
    x0: tuple[float,float] = (0., 0.)
    v0: tuple[float,float] = (0., 0.)

    def __post_init__(self):
        if type(self.n) is not int or self.n < 2 or self.n > 64:
            raise DomainError("INVALID_N")
        if not math.isfinite(self.upstream_delta_pa) or self.upstream_delta_pa not in (0., 10., 50.):
            raise DomainError("UNSUPPORTED_DELTA_PRESSURE")
        if self.outlet_pa != P_AMB:
            raise DomainError("UNSUPPORTED_OUTLET")
        if len(self.x0)!=2 or len(self.v0)!=2 or not all(math.isfinite(float(v)) for v in (*self.x0,*self.v0)):
            raise DomainError("INVALID_TISSUE_STATE")
        if max(abs(float(v)) for v in self.x0) >= H0-H_FLOOR:
            raise DomainError("UNSUPPORTED_CONTACT")


class Model:
    def __init__(self, fixture: Fixture):
        self.f = fixture
        self.n = fixture.n
        self.dz = LG/self.n
        self.centers = (np.arange(self.n)+0.5)*self.dz
        self.faces = np.arange(self.n+1)*self.dz
        # g[j,i] is the EXACT volume derivative dV_j/dx_i, not an extra valve law.
        z1=self.faces[:-1]; z2=self.faces[1:]
        self.g = np.column_stack((2*ELL*((z2-z1)-(z2*z2-z1*z1)/(2*LG)),
                                   2*ELL*(z2*z2-z1*z1)/(2*LG)))
        self.v0_cell = np.full(self.n, 2*ELL*H0*self.dz)
        self.initial_total_volume=float(np.sum(self.v0_cell))
        self.rho0=P_AMB/(R*T0)
        self.e0=P_AMB/(GAMMA-1.)
        self.mass0=np.full(self.n,self.rho0*2*ELL*H0*self.dz)
        self.ener0=np.full(self.n,self.e0*2*ELL*H0*self.dz)

    def initial(self):
        x=np.array(self.f.x0,dtype=float)
        y=np.zeros(3*self.n+4)
        vcell,_=self.geometry(x)
        y[:self.n]=self.rho0*vcell
        y[2*self.n:3*self.n]=self.e0*vcell
        y[3*self.n:3*self.n+2]=x
        y[3*self.n+2:]=np.array(self.f.v0,dtype=float)
        return y

    def split(self,y):
        n=self.n
        return y[:n],y[n:2*n],y[2*n:3*n],y[3*n:3*n+2],y[3*n+2:]

    def geometry(self,x):
        areas=2*ELL*(H0+(1-self.faces/LG)*x[0]+(self.faces/LG)*x[1])
        if np.min(areas)<=2*ELL*H_FLOOR:
            raise DomainError("UNSUPPORTED_CONTACT")
        vols=self.v0_cell+self.g@x
        if np.min(vols)<=0:raise DomainError("INVALID_VOLUME")
        return vols,areas

    def primitive(self,y):
        m,q,E,x,v=self.split(y)
        vol,area=self.geometry(x)
        if np.min(m)<=0 or np.min(E)<=0:
            raise DomainError("INVALID_THERMODYNAMIC_STATE")
        rho=m/vol; u=q/m
        p=(GAMMA-1.)*(E-q*q/(2*m))/vol
        if not (np.all(np.isfinite(y)) and np.all(p>0)):
            raise DomainError("INVALID_THERMODYNAMIC_STATE")
        c=np.sqrt(GAMMA*p/rho)
        if np.max(np.abs(u)/c)>0.1:
            raise DomainError("UNSUPPORTED_MACH")
        if np.min(u)<-1e-4: # interior transient reverse characteristic excluded
            raise DomainError("UNSUPPORTED_REVERSE")
        return vol,area,rho,u,p,c

    @staticmethod
    def eulerflux(state):
        rho,u,p=state
        Et=p/(GAMMA-1.) + 0.5*rho*u*u
        Q=np.array([rho,rho*u,Et])
        F=np.array([rho*u,rho*u*u+p,u*(Et+p)])
        return Q,F

    def ghosts(self,rho,u,p,c):
        # Left: stagnation p0,T0 supplies two incoming subsonic invariants;
        # outgoing Jminus inherited from adjacent cell.
        jminus=u[0]-2*c[0]/(GAMMA-1.)
        uleft=max(-10.,min(10.,jminus+2*C0/(GAMMA-1.)))
        for _ in range(30):
            csq=C0*C0-0.5*(GAMMA-1.)*uleft*uleft
            if csq<=0:raise DomainError("LEFT_CHARACTERISTIC_FAILED")
            nextu=jminus+2*math.sqrt(csq)/(GAMMA-1.)
            if abs(nextu-uleft)<1e-12:break
            uleft=nextu
        cleft=math.sqrt(C0*C0-0.5*(GAMMA-1.)*uleft*uleft)
        tleft=cleft*cleft/(GAMMA*R)
        pleft=(P_AMB+self.f.upstream_delta_pa)*(tleft/T0)**(GAMMA/(GAMMA-1.))
        rholeft=pleft/(R*tleft)
        # Right: prescribed static p, outgoing Jplus and extrapolated entropy.
        pright=self.f.outlet_pa
        rhoright=rho[-1]*(pright/p[-1])**(1./GAMMA)
        cright=math.sqrt(GAMMA*pright/rhoright)
        uright=u[-1]+2*(c[-1]-cright)/(GAMMA-1.)
        if uleft<-1e-4 or uright<-1e-4:
            raise DomainError("UNSUPPORTED_REVERSE_BOUNDARY")
        if max(abs(uleft/cleft),abs(uright/cright))>0.1:
            raise DomainError("UNSUPPORTED_MACH_BOUNDARY")
        return (rholeft,uleft,pleft),(rhoright,uright,pright)

    def rhs(self,y):
        vol,area,rho,u,p,c=self.primitive(y)
        m,q,E,x,v=self.split(y)
        ghostL,ghostR=self.ghosts(rho,u,p,c)
        states=[ghostL]+list(zip(rho,u,p))+[ghostR]
        flux=np.empty((self.n+1,3))
        for j in range(self.n+1):
            qa,fa=self.eulerflux(states[j]); qb,fb=self.eulerflux(states[j+1])
            sa=abs(states[j][1])+math.sqrt(GAMMA*states[j][2]/states[j][0])
            sb=abs(states[j+1][1])+math.sqrt(GAMMA*states[j+1][2]/states[j+1][0])
            flux[j]=area[j]*(0.5*(fa+fb)-0.5*max(sa,sb)*(qb-qa))
        source=np.zeros_like(y)
        advect=-(flux[1:]-flux[:-1])
        source[:self.n]=advect[:,0]
        source[self.n:2*self.n]=advect[:,1]+p*(area[1:]-area[:-1])
        # One common fluid->tissue pressure-work operator (same p and geometry g).
        vol_rate=self.g@v if not self.f.locked else np.zeros(self.n)
        source[2*self.n:3*self.n]=advect[:,2]-p*vol_rate
        force=self.g.T@(p-P_AMB)
        if not self.f.locked:
            source[3*self.n:3*self.n+2]=v
            source[3*self.n+2:]=(force-STIFF@x-DAMP*v)/MASS
        stage={"flux_in":flux[0].tolist(),"flux_out":flux[-1].tolist(),
               "momentum_geom":float(np.dot(p,area[1:]-area[:-1])),
               "wall_power_fluid":float(-np.dot(p,vol_rate)),
               "force":force.tolist(),"v":v.tolist(),"body_power":float(np.dot(force,v)) if not self.f.locked else 0.,
               "damping":float(np.dot(DAMP*v,v)) if not self.f.locked else 0.,
               "face_flux":flux.tolist(),"pressure":p.tolist(),"vol_rate":vol_rate.tolist(),
               "ghost_left":list(ghostL),"ghost_right":list(ghostR)}
        return source,stage

    def conserved_h(self,y):
        m,q,E,x,v=self.split(y)
        vol,_=self.geometry(x)
        return (float(np.sum(E))+0.5*float(v@(MASS*v))+0.5*float(x@(STIFF@x))
                +P_AMB*(float(np.sum(vol))-self.initial_total_volume))

    def step(self,y,dt):
        if not (0<dt<1e-4):raise DomainError("INVALID_DT")
        ys1=y
        k1,s1=self.rhs(ys1)
        ys2=y+dt*k1/2
        k2,s2=self.rhs(ys2)
        ys3=y+dt*k2/2
        k3,s3=self.rhs(ys3)
        ys4=y+dt*k3
        k4,s4=self.rhs(ys4)
        new=y+dt*(k1+2*k2+2*k3+k4)/6
        self.primitive(new)
        scalar_keys=("flux_in","flux_out","momentum_geom","wall_power_fluid","force","v","body_power","damping")
        weighted={k: (np.array(s1[k])+2*np.array(s2[k])+2*np.array(s3[k])+np.array(s4[k]))/6
                 for k in scalar_keys}
        stages=[{"y":sy.tolist(),"face_flux":ss["face_flux"],"pressure":ss["pressure"],
                 "vol_rate":ss["vol_rate"], "ghost_left":ss["ghost_left"],
                 "ghost_right":ss["ghost_right"], "force":ss["force"]}
                 for sy,ss in zip((ys1,ys2,ys3,ys4),(s1,s2,s3,s4))]
        return new,weighted,stages

    def run(self, duration=0.0003, dt=None, record_every=1):
        if dt is None:dt=0.2*self.dz/C0
        if duration<=0 or record_every<1:raise DomainError("INVALID_DURATION")
        y=self.initial()
        steps=math.ceil(duration/dt)
        actual=duration/steps
        records=[{"step":0,"time":0.,"y":y.tolist()}]
        aggregate={"mass_flux":0.,"momentum_flux":0.,"energy_flux":0.,"geom_mom":0.,
                   "wall_work_fluid":0.,"damping":0.,"body_force_work":0.}
        intermediate=[]
        for n in range(1,steps+1):
            ynew,st,stages=self.step(y,actual)
            d={"mass_flux":float(st["flux_in"][0]-st["flux_out"][0]),
               "momentum_flux":float(st["flux_in"][1]-st["flux_out"][1]),
               "energy_flux":float(st["flux_in"][2]-st["flux_out"][2]),
               "geom_mom":float(st["momentum_geom"]),
               "wall_work_fluid":float(st["wall_power_fluid"]),
               "damping":float(st["damping"])}
            d["body_force_work"]=float(st["body_power"])
            for k in aggregate:aggregate[k]+=actual*d[k]
            if n%record_every==0 or n==steps:
                records.append({"step":n,"time":n*actual,"y":ynew.tolist(),
                                "interval":d,"cumulative":dict(aggregate),"stages":stages})
            y=ynew
        return {"schema":"vf1b2.c1open.research-trace.v0", "fixture":vars(self.f).copy(),
                "n":self.n,"dt":actual,"steps":steps,"duration":duration,
                "rows":records,"integrals":aggregate}
