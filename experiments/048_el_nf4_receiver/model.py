"""EL-NF4 research ONLY: static measured-relative binaural HRIR spatial field.

No human eardrum/absolute amplitude calibration, source/receiver coupling,
Core/public API, dynamic rendering, subjective ASMR or released model assets.
The caller MUST pass train-only HRIR rows; truth rows are never accepted here.
"""
from dataclasses import dataclass
import hashlib
import numpy as np
from scipy.special import lpmv, gammaln
from scipy.spatial import cKDTree, Delaunay, QhullError


class Unsupported(ValueError):
    pass


def to_xyz(s):
    x = np.asarray(s, float).reshape(-1, 3)
    a, e = np.radians(x[:, 0]), np.radians(x[:, 1])
    r = x[:, 2]
    return np.column_stack((r*np.cos(e)*np.cos(a),
                            r*np.cos(e)*np.sin(a), r*np.sin(e)))


def spherical(p):
    x = np.asarray(p, float).reshape(-1, 3)
    r = np.linalg.norm(x, axis=1)
    if not np.isfinite(x).all() or np.any(r <= 0):
        raise ValueError("Nonfinite/invalid source geometry")
    return np.column_stack((np.mod(np.degrees(np.arctan2(x[:, 1], x[:, 0])), 360),
                            np.degrees(np.arctan2(x[:, 2], np.hypot(x[:, 0], x[:, 1]))), r))


def roles(xyz):
    """Frozen geometry-only role map shared across heads and distances."""
    s = spherical(xyz)
    bins = np.column_stack((np.floor(s[:,0]/20).astype(int),
                            np.floor((s[:,1]+30)/10).astype(int)))
    keys = [tuple(map(int,k)) for k in sorted(set(map(tuple,bins)))]
    if len(keys)<60:
        raise Unsupported("Too few angular block groups")
    ordered = sorted(keys,key=lambda k:hashlib.sha256(
        f"EL-NF4-20261031:{k[0]}:{k[1]}".encode()).digest())
    step=len(keys)//5
    lookup={k:("final" if i<step else "calibration" if i<2*step
               else "selection" if i<3*step else "train")
            for i,k in enumerate(ordered)}
    o=np.array([lookup[tuple(k)] for k in bins],dtype="U16")
    # Exclude the 5-degree halo around *final directions* from nonfinal fits.
    final_dirs=np.unique(np.round(s[o=="final",:2],6),axis=0)
    def unit(x):
        a,e=np.radians(x[:,0]),np.radians(x[:,1])
        return np.column_stack((np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)))
    if len(final_dirs):
        d,_=cKDTree(unit(final_dirs)).query(unit(s[:,:2]))
        o[(o!="final") & (d<2*np.sin(np.deg2rad(5)/2)-1e-10)]="buffer"
    return o,bins


@dataclass(frozen=True)
class Train:
    xyz: np.ndarray
    ir: np.ndarray
    fs: float

    def __post_init__(self):
        p,y=np.asarray(self.xyz),np.asarray(self.ir)
        if p.ndim!=2 or p.shape[1]!=3 or y.ndim!=3 or y.shape[0]!=len(p) or y.shape[1]!=2 or y.shape[2]<32:
            raise ValueError("Require Nx3 positions and Nx2xT FIR")
        if len(p)<8 or not np.isfinite(p).all() or not np.isfinite(y).all():
            raise ValueError("Insufficient/nonfinite samples")
        if np.any(np.linalg.norm(p,axis=1)<.05) or float(self.fs)<=16000:
            raise ValueError("Invalid radius/fs")
        if np.any(np.max(np.abs(y),axis=2)<=0):
            raise ValueError("Zero response channel")
        if len(np.unique(np.round(p,5),axis=0))!=len(p):
            raise ValueError("Duplicate training positions")


def real_sh(s,order):
    s=np.asarray(s,float).reshape(-1,3)
    az=np.deg2rad(s[:,0]); u=np.sin(np.deg2rad(s[:,1]))
    columns=[]
    for ell in range(order+1):
        for m in range(-ell,ell+1):
            a=abs(m)
            norm=np.sqrt((2*ell+1)/(4*np.pi)*np.exp(
                gammaln(ell-a+1)-gammaln(ell+a+1)))
            p=norm*lpmv(a,ell,u)
            columns.append(p if m==0 else np.sqrt(2)*p*(
                np.sin(a*az) if m<0 else np.cos(m*az)))
    return np.column_stack(columns)


def shift(y,delay):
    t=np.arange(len(y),dtype=float)
    return np.interp(t-delay,t,y,left=0.,right=0.)


class Field:
    def __init__(self,points,order):
        self.order=order
        z=np.log(spherical(points)[:,2])
        self.center=float((z.min()+z.max())/2)
        self.scale=max(float((z.max()-z.min())/2),1e-5)

    def __call__(self,points):
        s=spherical(points)
        sh=real_sh(s,self.order)
        z=np.clip((np.log(s[:,2])-self.center)/self.scale,-3,3)
        return np.stack((sh,sh*z[:,None]),axis=2).reshape(len(s),-1)


def fit(x,y,lam,order):
    d=[]
    for ell in range(order+1):
        for _ in range(2*ell+1):
            d.extend((1+.2*ell*(ell+1),2+.2*ell*(ell+1)))
    gram=x.T@x
    w=max(float(np.trace(gram))/len(d),1e-8)*lam
    return np.linalg.solve(gram+w*np.diag(d),x.T@y)


class Model:
    def __init__(self,train,mode="C3",order=3,lam=.1):
        self.data=train
        self.mode=mode.upper()
        self.order=int(order);self.lam=float(lam)
        self.tree=cKDTree(train.xyz)
        s=spherical(train.xyz)
        self.s=s;self.rmin=float(s[:,2].min());self.rmax=float(s[:,2].max())
        self.emin=float(s[:,1].min());self.emax=float(s[:,1].max())
        if self.mode=="B2":
            idx=np.arange(len(s))
            if len(idx)>1800:
                idx=np.array(sorted(idx,key=lambda i:hashlib.sha256(
                    np.asarray(train.xyz[i],dtype="<f8").tobytes()).digest())[:1800])
            self.tri_ids=idx
            try:self.tri=Delaunay(train.xyz[idx])
            except QhullError as e:raise Unsupported("Degenerate Delaunay") from e
        elif self.mode in ("B3","C3","C4"):
            self.basis=Field(train.xyz,self.order)
            x=self.basis(train.xyz)
            if self.mode=="B3":
                self.coef=fit(x,train.ir.reshape(len(x),-1),self.lam,self.order)
            else:
                peak=np.argmax(np.abs(train.ir),axis=-1)
                aligned=np.empty_like(train.ir,dtype=float)
                for i in range(len(x)):
                    for ear in range(2):
                        aligned[i,ear]=shift(train.ir[i,ear],-float(peak[i,ear]))
                self.coef=fit(x,aligned.reshape(len(x),-1),self.lam,self.order)
                self.delay_coef=fit(x,peak.astype(float),self.lam,self.order)
                if self.mode=="C4":
                    self.residual=aligned.reshape(len(x),-1)-x@self.coef
        elif self.mode not in ("B0","B1"):
            raise ValueError("Unknown mode")

    def predict(self,position):
        q=np.asarray(position,float).reshape(3)
        try:s=spherical(q)[0]
        except ValueError as e:raise Unsupported("Invalid query") from e
        if s[2]<self.rmin-1e-5 or s[2]>self.rmax+1e-5:
            raise Unsupported("Outside measured radial support")
        if s[1]<self.emin-1e-5 or s[1]>self.emax+1e-5:
            raise Unsupported("Outside measured elevation support")
        dist,ind=self.tree.query(q,k=min(8,len(self.data.xyz)))
        dd=np.atleast_1d(dist); ii=np.atleast_1d(ind)
        if self.mode=="B0":
            out=self.data.ir[int(ii[0])].astype(float)
        elif self.mode=="B1":
            d=dd[:4]; k=len(d)
            w=np.zeros(k)
            if d[0]<1e-9:w[0]=1.
            else:
                w=1/np.maximum(d,1e-8);w/=w.sum()
            out=np.tensordot(w,self.data.ir[ii[:k]],axes=(0,0))
        elif self.mode=="B2":
            j=int(self.tri.find_simplex(q))
            if j<0:raise Unsupported("Outside tetrahedral convex hull")
            transform=self.tri.transform[j]
            w0=transform[:3]@(q-transform[3])
            w=np.r_[w0,1-w0.sum()]
            if np.min(w)<-1e-7:raise Unsupported("Negative barycentric weight")
            w=np.maximum(w,0);w/=w.sum()
            out=np.tensordot(w,self.data.ir[self.tri_ids[self.tri.simplices[j]]],axes=(0,0))
        else:
            x=self.basis(q)[0]
            y=x@self.coef
            if self.mode in ("C3","C4"):
                if self.mode=="C4":
                    # A bounded, train-only, locally fading correction.
                    ang=np.deg2rad(self.s[ii,:2]);qa,qe=np.deg2rad(s[:2])
                    dangle=np.arccos(np.clip(
                        np.sin(ang[:,1])*np.sin(qe)+
                        np.cos(ang[:,1])*np.cos(qe)*np.cos(ang[:,0]-qa),-1,1))
                    radial=np.abs(np.log(self.s[ii,2]/s[2]))
                    norm=np.sqrt((dangle/np.deg2rad(20))**2+(radial/.4)**2)
                    w=np.exp(-.5*norm**2);w/=max(float(w.sum()),1e-15)
                    y=y+np.exp(-float(norm.min())**2)*(w@self.residual[ii])
                delay=np.clip(x@self.delay_coef,0,self.data.ir.shape[-1]-1)
                y=y.reshape(2,-1)
                out=np.stack([shift(y[e],float(delay[e])) for e in range(2)])
            else:out=y.reshape(2,-1)
        if not np.isfinite(out).all():raise Unsupported("Nonfinite predicted HRIR")
        return out,{"model":self.mode,"nearest_train_m":float(dd[0]),
                    "order":self.order,"ridge":self.lam}


def band_ild(h,fs):
    x=np.fft.rfft(np.asarray(h,float),axis=-1)
    f=np.fft.rfftfreq(h.shape[-1],1/float(fs))
    result=[]
    for a,b in ((500,1000),(1000,2000),(2000,4000),(4000,8000)):
        mask=(f>=a)&(f<b)
        en=np.sum(np.abs(x[:,mask])**2,axis=-1)
        if np.any(en<=1e-22):raise Unsupported("No energy in ILD band")
        result.append(float(10*np.log10(en[0]/en[1])))
    return np.array(result)


def itd_proxy(h,fs):
    cc=np.correlate(h[0],h[1],mode="full")
    return float((np.argmax(cc)-(h.shape[-1]-1))*1e6/fs)


def centered_spectrum(h,fs):
    x=np.fft.rfft(h,axis=-1)
    f=np.fft.rfftfreq(h.shape[-1],1/fs)
    z=20*np.log10(np.maximum(np.abs(x[:,(f>=500)&(f<8000)]),1e-12))
    return z-z.mean(axis=-1,keepdims=True)


def metrics(pred,truth,fs):
    err=np.abs(band_ild(pred,fs)-band_ild(truth,fs))
    return {"ild_bands_abs_db":err.tolist(),
            "ild_median_db":float(np.median(err)),
            "itd_error_us":abs(itd_proxy(pred,fs)-itd_proxy(truth,fs)),
            "spectral_shape_rmse_db":float(np.sqrt(np.mean(
                (centered_spectrum(pred,fs)-centered_spectrum(truth,fs))**2)))}
