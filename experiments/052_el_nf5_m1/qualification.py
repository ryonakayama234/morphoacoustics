"""NF5 M1 source-pinned geometry-only G0-B. Does not read Data.IR or Data.Delay values."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

import h5py
import numpy as np

EXPECTED_MD5 = "1310d2b015c82272cc27d10d680b6bb4"
EXPECTED_SHA = "5f3a4c6df0f0c0bbbce6639f41129a20bc03603d19316db74637f70bfa1ff5f9"
SHELLS = {0.5:"HRIR_L2702_NF050.sofa", 0.75:"HRIR_L2702_NF075.sofa",
          1.0:"HRIR_L2702_NF100.sofa", 1.5:"HRIR_L2702_NF150.sofa"}
SEED = "nf5-m1-g0b-v1"

class GateError(ValueError):
    pass

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def string_attr(obj, name: str) -> str:
    v = obj.attrs.get(name, "")
    if isinstance(v, bytes):
        return v.decode("utf8")
    if isinstance(v, np.ndarray) and v.size == 1:
        v = v.reshape(-1)[0]
        if isinstance(v, bytes):
            return v.decode("utf8")
    return str(v)

def normalize_source(p: np.ndarray, radius: float) -> tuple[np.ndarray,np.ndarray]:
    """Convert original spherical SOFA positions to unit direction and 20x10 cells."""
    p = np.asarray(p,dtype=float)
    if p.shape != (2702,3) or not np.isfinite(p).all():
        raise GateError("INVALID_SOURCE: finite [2702,3] required")
    az,el,r = p.T
    if np.any(np.abs(r-radius) >= .03) or np.any((el < -90-1e-6)|(el > 90+1e-6)):
        raise GateError("INVALID_SOURCE: radius/elevation")
    az=np.mod(np.round(az,6),360.0)
    el=np.round(np.clip(el,-90,90),6)
    az[np.isclose(np.abs(el),90,atol=1e-6)]=0.0
    a,e=np.deg2rad(az),np.deg2rad(el)
    v=np.stack([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)],axis=1)
    if len(np.unique(np.round(v,6),axis=0)) != 2702:
        raise GateError("DUPLICATE_DIRECTION")
    cells=np.stack([np.floor(az/20).astype(int),
                    np.floor((el+90)/10).astype(int)],axis=1)
    return v,cells

def role(cell) -> str:
    i,j=map(int,cell)
    n=int.from_bytes(hashlib.sha256(f"{SEED}|{i}|{j}".encode()).digest()[:8],"big")%100
    return "fit" if n<55 else "selection" if n<75 else "calibration" if n<85 else "final"

def partition(directions: np.ndarray, cells: np.ndarray) -> dict:
    assert directions.shape == (2702,3) and cells.shape == (2702,2)
    roles=np.array([role(c) for c in cells])
    fit0=np.flatnonzero(roles=="fit")
    blocked=np.flatnonzero(roles!="fit")
    final=np.flatnonzero(roles=="final")
    if not len(fit0) or not len(blocked) or not len(final):
        raise GateError("INSUFFICIENT_SPLIT")
    # 5 degree exclusion from fit to ALL disjoint acoustic target roles.
    cutoff=math.cos(math.radians(5))
    keep=[]
    for chunk in np.array_split(fit0, max(1,math.ceil(len(fit0)/256))):
        closest=np.max(np.clip(directions[chunk]@directions[blocked].T,-1,1),axis=1)
        keep.extend(chunk[closest <= cutoff+1e-12].tolist())
    fit=np.array(keep,dtype=int)
    if not len(fit):
        raise GateError("NO_FIT_AFTER_BUFFER")
    if np.any(directions[fit]@directions[blocked].T > cutoff+1e-10):
        raise GateError("ANGULAR_LEAK")
    block_count={k:len(set(map(tuple,cells[roles==k]))) for k in
                 ("fit","selection","calibration","final")}
    if block_count["final"]<8:
        raise GateError("INSUFFICIENT_FINAL_BLOCKS")
    role_count={k:int(np.sum(roles==k)) for k in block_count}
    role_data=[(int(i),str(k)) for i,k in enumerate(roles.tolist())]
    # S1 observed-distance/final-direction at .75m; S2 new distance 1.0m excluded
    # from S2 *fit, selection, and calibration*; .75m/1.5m bracket S2.
    return dict(role_counts=role_count, angular_block_counts=block_count,
        fit_direction_count_after_buffer=len(fit),
        fit_removed_by_buffer=len(fit0)-len(fit),
        angular_buffer_degrees=5,
        roles_sha256=sha(json.dumps(role_data,separators=(",",":")).encode()),
        fit_ids_sha256=sha(json.dumps(fit.tolist(),separators=(",",":")).encode()),
        s1=dict(final_query_count=len(final),final_radius_m=.75,
                training_radii_m=[.5,.75,1.0,1.5]),
        s2=dict(final_query_count=len(final),final_radius_m=1.0,
                training_radii_m=[.5,.75,1.5],bracketing_m=[.75,1.5]),
        potential_b0_geometric_support="CANDIDATE_ONLY",
        actual_model_coverage="NOT_MEASURED", independent_head_count=1)

def inspect_original(data: bytes) -> dict:
    if hashlib.md5(data).hexdigest()!=EXPECTED_MD5 or sha(data)!=EXPECTED_SHA:
        raise GateError("ORIGINAL_HASH_MISMATCH")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            contents=[i for i in z.infolist() if not i.is_dir()]
            if len(contents)!=4 or set(i.filename for i in contents)!=set(SHELLS.values()):
                raise GateError("UNEXPECTED_ARCHIVE_MEMBERS")
            if any(i.file_size>30_000_000 or i.compress_size>20_000_000 or
                   i.flag_bits&1 or "/" in i.filename or "\\" in i.filename
                   for i in contents):
                raise GateError("UNSAFE_ARCHIVE")
            directions=None
            cells=None
            files=[]
            for radius,filename in SHELLS.items():
                blob=z.read(filename)
                with h5py.File(io.BytesIO(blob),"r") as h:
                    if string_attr(h,"SOFAConventions")!="SimpleFreeFieldHRIR":
                        raise GateError("UNSUPPORTED_CONVENTION")
                    if ("Data.IR" not in h or "Data.Delay" not in h or
                        h["Data.IR"].shape!=(2702,2,128) or
                        h["Data.Delay"].shape!=(1,2)):
                        raise GateError("UNSUPPORTED_RESPONSE_SHAPES")
                    fs=np.asarray(h["Data.SamplingRate"][()]).reshape(-1)
                    if len(fs)!=1 or float(fs[0])!=48000:
                        raise GateError("UNSUPPORTED_SAMPLE_RATE")
                    src=h["SourcePosition"]
                    units=string_attr(src,"Units").strip().lower()
                    if (string_attr(src,"Type").strip().lower()!="spherical" or
                        units not in ("degree, degree, metre","degree, degree, meter")):
                        raise GateError("UNSUPPORTED_SOURCE_UNITS")
                    v,c=normalize_source(src[()],radius) # ONLY per-position numeric read
                    if directions is not None and (np.max(np.linalg.norm(v-directions,axis=1))>5e-4
                                                    or not np.array_equal(c,cells)):
                        raise GateError("INCONSISTENT_SHELL_GEOMETRY")
                    directions,cells=v,c
                    files.append(dict(file=filename,sha256=sha(blob),radius_m=radius,
                                      ir_shape=[2702,2,128],delay_shape=[1,2],
                                      license_notice=string_attr(h,"License")))
            return dict(schema="EL-NF5-M1-G0B-v1",
                        geometric_verdict="G0B_GEOMETRY_FEASIBLE",
                        complete_scientific_verdict="MEASURAND_AND_RIGHTS_UNVERIFIED",
                        original_md5=EXPECTED_MD5,original_sha256=EXPECTED_SHA,
                        original_data_ir_values_read=False,
                        original_data_delay_values_read=False,
                        final_acoustic_truth_access="SEALED_NOT_READ",
                        file_metadata=files, geometry=partition(directions,cells),
                        rights_status="SOFA_CC_3_BY_SA_VS_PAPER_CC_BY_SA_4_REVIEW_REQUIRED",
                        physical_TOF="UNVERIFIED", recording_plane="UNVERIFIED",
                        low_band_fidelity="UNVERIFIED", model_g3b="NOT_RUN")
    except (zipfile.BadZipFile,OSError,KeyError) as exc:
        raise GateError(f"INVALID_SOURCE_CONTAINER: {exc}") from exc

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.archive.stat().st_size>30_000_000 or args.output.exists():
        raise GateError("UNSAFE_INPUT_OR_OVERWRITE")
    receipt=inspect_original(args.archive.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
