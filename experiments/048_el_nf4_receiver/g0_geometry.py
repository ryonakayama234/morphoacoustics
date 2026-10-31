#!/usr/bin/env python3
"""EL-NF4 G0: only geometry and SOFA headers; NEVER access Data.IR values.
Research-only; G0 metadata must precede the G0->G1 v1.1 allocation freeze.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import h5py


def _txt(x):
    if isinstance(x, bytes):
        return x.decode("utf-8", "replace")
    if isinstance(x, np.ndarray):
        return _txt(x.item()) if x.size == 1 else [_txt(y) for y in x.ravel()]
    return str(x)


def fingerprint(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(2**20), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect(path: Path) -> dict:
    with h5py.File(path, "r") as f:
        # Data.IR must never be read or indexed in this G0 code; shape only.
        shape = tuple(int(x) for x in f["Data.IR"].shape)
        src = f["SourcePosition"]
        p = np.asarray(src[()], dtype=np.float64)
        typ = _txt(src.attrs.get("Type", "MISSING")).lower().strip()
        units = _txt(src.attrs.get("Units", "MISSING")).lower().replace(" ", "")
        if p.ndim != 2 or p.shape[1] != 3:
            raise ValueError(f"unsupported coordinates shape={p.shape}")
        if typ == "spherical" and units in ("degree,degree,metre", "degree,degree,meter"):
            a = np.mod(p[:, 0], 360.)
            e = p[:, 1]
            r = p[:, 2]
        elif typ == "cartesian" and units in ("metre", "meter"):
            r = np.linalg.norm(p, axis=1)
            a = np.mod(np.rad2deg(np.arctan2(p[:, 1], p[:, 0])), 360.)
            e = np.rad2deg(np.arctan2(p[:, 2], np.hypot(p[:, 0], p[:, 1])))
        else:
            raise ValueError(f"unsupported Type/Units: {typ} / {units}")
        if not (np.isfinite(p).all() and (r > 0).all()):
            raise ValueError("invalid coordinates")
        radii, counts = np.unique(np.round(r, 3), return_counts=True)
        dirs = np.column_stack((np.round(a, 3), np.round(e, 3)))
        conv = _txt(f.attrs.get("SOFAConventions", "MISSING"))
        receivers = None
        if "ReceiverPosition" in f:
            receivers = {"shape": list(f["ReceiverPosition"].shape),
                         "Type": _txt(f["ReceiverPosition"].attrs.get("Type", "MISSING")),
                         "Units": _txt(f["ReceiverPosition"].attrs.get("Units", "MISSING"))}
        delay = None
        if "Data.Delay" in f:
            delay = {"shape": list(f["Data.Delay"].shape),
                     "zero": bool(np.all(np.asarray(f["Data.Delay"][()]) == 0))}
        return {
            "name": path.name,
            "sha256": fingerprint(path),
            "SOFAConventions": conv,
            "global_attrs": {str(k): _txt(v)[:300] if isinstance(_txt(v), str) else str(_txt(v))[:300]
                             for k, v in f.attrs.items()
                             if k in ("DatabaseName", "ListenerShortName", "Title", "Organization", "References", "RoomType", "DataType", "Version", "SOFAConventionsVersion", "License", "Comment", "Origin")},
            "source_type": typ, "source_units": units,
            "shape": list(shape),
            "sampling_rate": np.asarray(f["Data.SamplingRate"][()]).ravel().tolist(),
            "data_delay": delay, "receiver_position": receivers,
            "listener_view": (np.asarray(f["ListenerView"][()]).tolist() if "ListenerView" in f else None),
            "listener_up": (np.asarray(f["ListenerUp"][()]).tolist() if "ListenerUp" in f else None),
            "minmax": {"radius_m": [float(r.min()), float(r.max())],
                       "azimuth_deg": [float(a.min()), float(a.max())],
                       "elevation_deg": [float(e.min()), float(e.max())]},
            "distance_shells_m": [[float(x), int(n)] for x, n in zip(radii, counts)],
            "unique_directions_0.001deg": int(len(np.unique(dirs, axis=0))),
            "unique_positions_1e-4m": int(len(np.unique(np.round(p, 4), axis=0))),
            "acoustic_values_read": False,
            "license_status": "UNVERIFIED",
            "receiver_plane_status": "UNVERIFIED"
        }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="+", type=Path)
    args = p.parse_args()
    print(json.dumps({"schema": "el-nf4.g0-geometry.v1",
                      "files": [inspect(x) for x in args.paths]}, indent=2))


if __name__ == "__main__":
    main()
