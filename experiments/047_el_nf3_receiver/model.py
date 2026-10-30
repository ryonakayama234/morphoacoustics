"""EL-NF3 static binaural receiver research models; NOT a production API.

Only relative measured-head HRIRs; no ear-drum Pa or perceptual guarantee.
Use the original SOFA and verify its measurement plane separately.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path

import numpy as np
from scipy.spatial import Delaunay, cKDTree, QhullError


class Unsupported(ValueError):
    """A query cannot be safely evaluated; no silent nearest fallback."""


def _label(value):
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return _label(value.flat[0])
        return ", ".join(_label(x) for x in value.flat)
    return str(value)


def spherical_to_xyz(position):
    pos = np.asarray(position, dtype=float)
    az, el, r = np.deg2rad(pos[:, 0]), np.deg2rad(pos[:, 1]), pos[:, 2]
    return np.column_stack((r * np.cos(el) * np.cos(az),
                            r * np.cos(el) * np.sin(az), r * np.sin(el)))


def xyz_to_spherical(position):
    pos = np.asarray(position, dtype=float).reshape(-1, 3)
    r = np.linalg.norm(pos, axis=1)
    az = (np.rad2deg(np.arctan2(pos[:, 1], pos[:, 0])) + 360) % 360
    el = np.rad2deg(np.arctan2(pos[:, 2], np.hypot(pos[:, 0], pos[:, 1])))
    return np.column_stack((az, el, r))


@dataclass(frozen=True)
class HeadData:
    xyz: np.ndarray
    ir: np.ndarray
    fs: float
    source_sha256: str = "SYNTHETIC"
    reference_plane: str = "UNVERIFIED"

    def __post_init__(self):
        p, h = np.asarray(self.xyz), np.asarray(self.ir)
        if p.ndim != 2 or p.shape[1] != 3 or h.ndim != 3 or h.shape[0] != len(p) or h.shape[1] != 2 or h.shape[2] < 32:
            raise ValueError("Require Mx3 source positions and Mx2xN FIR")
        if not (np.all(np.isfinite(p)) and np.all(np.isfinite(h))):
            raise ValueError("Nonfinite geometry or IR")
        if np.any(np.linalg.norm(p, axis=1) < .001) or not (self.fs > 16000):
            raise ValueError("Invalid distance or sampling rate")
        if np.any(np.max(np.abs(h), axis=2) <= 0):
            raise ValueError("Zero-channel HRIR")
        if len(np.unique(np.round(p, 5), axis=0)) != len(p):
            raise ValueError("Duplicate positions")


def load_sofa(path, expected_md5=None):
    """Strict original SOFA reader; nonzero Data.Delay must be resolved first."""
    import h5py
    path = Path(path)
    md5, sha = hashlib.md5(), hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            md5.update(chunk)
            sha.update(chunk)
    if expected_md5 is not None and md5.hexdigest().lower() != expected_md5.lower():
        raise ValueError("Original file MD5 mismatch")
    with h5py.File(path, "r") as f:
        convention = _label(f.attrs.get("SOFAConventions", ""))
        if convention != "SimpleFreeFieldHRIR":
            raise ValueError("Unsupported SOFA convention: " + convention)
        src = f["SourcePosition"]
        units = _label(src.attrs.get("Units", "")).replace(" ", "").lower()
        typ = _label(src.attrs.get("Type", "")).lower()
        p = np.asarray(src[:], dtype=float)
        if p.ndim != 2 or p.shape[1] != 3:
            raise ValueError("Invalid SourcePosition shape")
        if typ == "spherical" and units in ("degree,degree,metre", "degree,degree,meter"):
            xyz = spherical_to_xyz(p)
        elif typ == "cartesian" and units in ("metre", "meter"):
            xyz = p
        else:
            raise ValueError("Unverified SourcePosition Type/Units: " + typ + " " + units)
        ir = np.asarray(f["Data.IR"][:], dtype=np.float32)
        fs_values = np.asarray(f["Data.SamplingRate"][:], dtype=float).ravel()
        if len(fs_values) < 1 or not np.allclose(fs_values, fs_values[0]):
            raise ValueError("Inconsistent Data.SamplingRate")
        if "Data.Delay" in f and np.any(np.asarray(f["Data.Delay"][:], dtype=float) != 0):
            raise ValueError("Nonzero Data.Delay requires explicit sample-domain alignment")
        receiver_plane = "UNVERIFIED"
        if "ReceiverPosition" in f:
            receiver_plane = "RECEIVER_POSITION_PRESENT_PLANE_UNVERIFIED"
        return HeadData(xyz, ir, float(fs_values[0]), sha.hexdigest(), receiver_plane)


def block_roles(xyz, seed=20261030):
    """Deterministic geometry-only contiguous angular-block allocation."""
    a = xyz_to_spherical(xyz)
    if np.any((a[:, 1] < -25.001) | (a[:, 1] > 35.001)):
        raise Unsupported("Outside preregistered elevation domain")
    bins = np.column_stack((np.floor(a[:, 0] / 20).astype(int),
                            np.floor((a[:, 1] + 25) / 10).astype(int)))
    keys = sorted(set(map(tuple, bins)))
    if len(keys) < 20:
        raise Unsupported("Insufficient independent angular blocks")
    ordered = sorted(keys, key=lambda k: hashlib.sha256(
        (str(seed) + ":" + str(k[0]) + ":" + str(k[1])).encode()).digest())
    n = len(keys)
    n20 = int(.2 * n)
    mapping = {}
    for i, k in enumerate(ordered):
        mapping[k] = ("final" if i < n20 else "calibration" if i < 2*n20 else
                      "selection" if i < 3*n20 else "train")
    roles = np.array([mapping[tuple(k)] for k in bins], dtype="U16")
    # Exclude all non-final coordinates within 5° of a final block boundary.
    final = [k for k in keys if mapping[k] == "final"]
    az = a[:, 0]
    el = a[:, 1]
    boundary = np.zeros(len(az), dtype=bool)
    for x, y in final:
        center_az = 20*x + 10
        center_el = 10*y - 20
        da = np.abs((az - center_az + 180) % 360 - 180)
        de = np.abs(el - center_el)
        boundary |= (da <= 15) & (de <= 10)
    roles[(roles != "final") & boundary] = "buffer"
    return roles, bins


def _shift(signal, delay):
    t = np.arange(len(signal), dtype=float)
    return np.interp(t - delay, t, signal, left=0., right=0.)


def _arrivals(ir, mode):
    if mode == "peak":
        return np.argmax(np.abs(ir), axis=1).astype(float)
    peak = np.max(np.abs(ir), axis=1)
    mask = (np.abs(ir) >= .12 * peak[:, None])
    if np.any(~np.any(mask, axis=1)):
        raise Unsupported("No stable arrival onset")
    return np.argmax(mask, axis=1).astype(float)


def _aligned_blend(hrirs, weights, mode):
    if not np.isclose(weights.sum(), 1., atol=1e-6) or np.any(weights < -1e-9):
        raise Unsupported("Invalid or extrapolating weights")
    delay = np.array([_arrivals(h, mode) for h in hrirs])
    if np.any(np.abs(delay[:, 0] - delay[:, 1]) > .0015 * 48000):
        raise Unsupported("Training bilateral arrival mismatch")
    pred_delay = weights @ delay
    out = np.zeros_like(hrirs[0], dtype=np.float64)
    for ear in range(2):
        aligned = np.array([_shift(h[ear], -d[ear]) for h, d in zip(hrirs, delay)])
        out[ear] = _shift(weights @ aligned, pred_delay[ear])
    return out


class Predictor:
    """All constructors accept TRAIN data only; no hidden fallback."""
    def __init__(self, data, indices, method="C2"):
        self.data = data
        self.indices = np.asarray(indices, dtype=int)
        self.method = method.upper()
        if len(self.indices) == 0:
            raise Unsupported("Empty training set")
        if len(np.unique(self.indices)) != len(self.indices):
            raise ValueError("Repeated train indices")
        self.xyz = data.xyz[self.indices]
        self.tree = cKDTree(self.xyz)
        self.tri3 = None
        self.shell_cache = {}
        self.sph = xyz_to_spherical(self.xyz)
        self.radii = np.unique(np.round(self.sph[:, 2], 3))
        if self.method == "B2":
            # Prespecified geometry-only stable decimation, not error-driven.
            local = np.arange(len(self.indices))
            if len(local) > 5000:
                order = sorted(local, key=lambda i: hashlib.sha256(
                    ("20261030:"+",".join(format(x, ".5f") for x in self.xyz[i])).encode()
                ).digest())
                local = np.array(order[:5000], dtype=int)
            self.tri_ids = local
            try:
                self.tri3 = Delaunay(self.xyz[local])
            except QhullError as err:
                raise Unsupported("Invalid 3D simplex geometry") from err

    def _shell(self, r):
        key = float(r)
        if key in self.shell_cache:
            return self.shell_cache[key]
        ids = np.flatnonzero(np.abs(self.sph[:, 2] - r) <= .0006)
        if len(ids) < 4:
            raise Unsupported("Insufficient same-radius angle points")
        ang = self.sph[ids, :2]
        expanded = np.concatenate((ang, ang + [360, 0], ang - [360, 0]))
        original = np.tile(ids, 3)
        try:
            tri = Delaunay(expanded)
        except QhullError as err:
            raise Unsupported("Degenerate angular shell") from err
        self.shell_cache[key] = tri, expanded, original
        return self.shell_cache[key]

    def _triangle(self, r, q):
        tri, expanded, ids = self._shell(r)
        target = xyz_to_spherical(q)[0, :2]
        simplex = int(tri.find_simplex(target))
        if simplex < 0:
            raise Unsupported("Outside angular convex hull")
        vertices = tri.simplices[simplex]
        transform = tri.transform[simplex]
        b = transform[:2].dot(target - transform[2])
        w = np.array((b[0], b[1], 1 - b.sum()))
        if np.any(w < -1e-7):
            raise Unsupported("Angular extrapolation")
        pts = expanded[vertices]
        span = np.max(np.linalg.norm(pts[:,None,:] - pts[None,:,:],axis=-1))
        if span > 25.:
            raise Unsupported("Angular simplex exceeds 25 degrees")
        w = np.maximum(w, 0)
        return ids[vertices], w / w.sum(), float(span)

    def predict(self, query):
        q = np.asarray(query, dtype=float).reshape(3)
        radius = np.linalg.norm(q)
        if not np.all(np.isfinite(q)) or not (.20 - 1e-5 <= radius <= .50 + 1e-5):
            raise Unsupported("Outside 0.20–0.50 m research support")
        if self.method == "B0":
            ix = int(self.tree.query(q)[1])
            return np.array(self.data.ir[self.indices[ix]], dtype=float), {"method":"B0"}
        if self.method in ("B1","C1"):
            k = min(4, len(self.indices))
            d, ix = self.tree.query(q, k=k)
            d, ix = np.atleast_1d(d), np.atleast_1d(ix)
            if np.any(d < 1e-8):
                w = (d < 1e-8).astype(float)
            else:
                w = 1 / np.maximum(d, 1e-6)
            w /= w.sum()
            irs = self.data.ir[self.indices[ix]]
            if self.method == "B1":
                return np.tensordot(w, irs, axes=(0,0)), {"method":"B1"}
            return _aligned_blend(irs, w, "peak"), {"method":"C1", "arrival":"peak_proxy"}
        if self.method == "B2":
            simplex = int(self.tri3.find_simplex(q))
            if simplex < 0:
                raise Unsupported("Outside Cartesian 3D convex hull")
            verts = self.tri_ids[self.tri3.simplices[simplex]]
            mat = self.tri3.transform[simplex]
            b = mat[:3].dot(q - mat[3])
            w = np.r_[b, 1. - b.sum()]
            if np.any(w < -1e-7):
                raise Unsupported("Invalid simplex weights")
            w = np.maximum(w, 0); w /= w.sum()
            return np.tensordot(w, self.data.ir[self.indices[verts]], axes=(0,0)), {"method":"B2"}
        if self.method not in ("C2","C2A","C2B","C2C"):
            raise ValueError("Unknown method")
        lower = self.radii[self.radii <= radius + .0006]
        upper = self.radii[self.radii >= radius - .0006]
        if len(lower) == 0 or len(upper) == 0:
            raise Unsupported("No radial bracketing")
        lo, hi = float(lower[-1]),float(upper[0])
        if hi - lo > .301:
            raise Unsupported("Excessive radial gap")
        q = q.reshape(1,3)
        il, wl, sl = self._triangle(lo, q)
        if hi == lo:
            ids, w, span = il, wl, sl
        else:
            ih, wh, sh = self._triangle(hi, q)
            a = (radius - lo) / (hi - lo)
            ids = np.r_[il, ih]
            w = np.r_[wl*(1-a), wh*a]
            span = max(sl,sh)
        irs = self.data.ir[self.indices[ids]]
        if self.method in ("C2A","C2B"):
            out = np.tensordot(w, irs, axes=(0,0)) if self.method == "C2A" else _aligned_blend(irs,w,"peak")
        else:
            out = _aligned_blend(irs,w,"onset")
        return out, {"method":self.method, "angular_span_deg":span, "radial_gap_m":hi-lo,
                     "max_weight":float(w.max()), "reference_plane":self.data.reference_plane}


def band_ild(ir, fs):
    if len(ir[0]) < 32:
        raise ValueError("Short IR")
    freq = np.fft.rfftfreq(ir.shape[-1], 1. / fs)
    f = np.fft.rfft(ir, axis=-1)
    out = []
    for lo, hi in ((500,1000),(1000,2000),(2000,4000),(4000,8000)):
        mask=(freq>=lo)&(freq<hi)
        if not mask.any():
            raise ValueError("Band unresolved")
        energy = np.sum(np.abs(f[:,mask])**2,axis=1)
        if np.any(energy <= 1e-24):
            raise Unsupported("Zero band energy")
        out.append(float(10*np.log10(energy[0]/energy[1])))
    return np.asarray(out)


def band_ild_error(pred, truth, fs):
    return np.abs(band_ild(pred,fs)-band_ild(truth,fs))


def deterministic_split_hash(xyz, roles):
    payload = sorted((list(map(float,np.round(p,6))), str(s)) for p,s in zip(xyz,roles))
    return hashlib.sha256(repr(payload).encode()).hexdigest()
