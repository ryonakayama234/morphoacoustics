"""EL-NF2 relative spatial receiver research, static measured artificial-head HRIR only.

No Core runtime, Studio, personalization or absolute pressure representation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import h5py
import numpy as np
from scipy.signal import butter, correlate, sosfiltfilt

FS = 48000
RADII = (0.2, 0.3, 0.4, 0.5)
BANDS = ((500, 1000), (1000, 2000), (2000, 4000), (4000, 8000))
ORIGINAL_MD5 = "4ba9cc348801a6805265c7168b5b3227"
PREREG_COMMIT = "9915d101cdbba273b7c69813098d4e14a364abb7"
MAX_ANGLE_DEG = 45.0


def digest(path: Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def attr(obj, name: str) -> str:
    value = obj.attrs.get(name, "")
    if isinstance(value, np.ndarray) and value.size == 1:
        value = value.reshape(-1)[0]
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return str(value).strip()


def source_cartesian(positions: np.ndarray, kind: str, units: str) -> np.ndarray:
    positions = np.asarray(positions, dtype=float)
    if positions.ndim != 2 or positions.shape[1] != 3 or not np.isfinite(positions).all():
        raise ValueError("INVALID: finite Nx3 source positions required")
    parts = [part.strip().lower() for part in units.split(",")]
    if kind.lower() == "spherical" and len(parts) == 3 and all(x in ("degree", "degrees") for x in parts[:2]) and parts[2] in ("metre", "meter", "m"):
        a, e, rad = np.deg2rad(positions[:, 0]), np.deg2rad(positions[:, 1]), positions[:, 2]
        if np.any(rad <= 0):
            raise ValueError("INVALID: nonpositive radius")
        return np.column_stack((rad * np.cos(e) * np.cos(a), rad * np.cos(e) * np.sin(a), rad * np.sin(e)))
    if kind.lower() == "cartesian" and parts in (["m"], ["meter"], ["metre"], ["m"] * 3, ["metre"] * 3, ["meter"] * 3):
        return positions.copy()
    raise ValueError("UNSUPPORTED: source position units or coordinate system")


def load_sofa(path: Path, require_original: bool = True) -> dict:
    if not path.is_file() or not (512 <= path.stat().st_size <= 50_000_000):
        raise ValueError("INVALID: SOFA file missing or unsafe file size")
    md5 = digest(path, "md5")
    if require_original and md5 != ORIGINAL_MD5:
        raise ValueError("INVALID: original SOFA checksum mismatch")
    with h5py.File(path, "r") as obj:
        if attr(obj, "SOFAConventions") != "SimpleFreeFieldHRIR" or attr(obj, "DataType") != "FIR":
            raise ValueError("UNSUPPORTED: SOFA convention/data type")
        if any(x not in obj for x in ("SourcePosition", "Data.IR", "Data.SamplingRate")):
            raise ValueError("INVALID: missing required SOFA datasets")
        sp = obj["SourcePosition"]
        xyz = source_cartesian(np.asarray(sp), attr(sp, "Type"), attr(sp, "Units"))
        sr = np.asarray(obj["Data.SamplingRate"], dtype=float).reshape(-1)
        if sr.size != 1 or sr[0] != FS:
            raise ValueError("UNSUPPORTED: only 48 kHz")
        ir = np.asarray(obj["Data.IR"], dtype=float)
        if ir.ndim != 3 or ir.shape[0] != len(xyz) or ir.shape[1] != 2 or not (32 <= ir.shape[2] <= 32768):
            raise ValueError("INVALID: expected Mx2xN IR")
        if not np.isfinite(ir).all() or np.any(np.max(np.abs(ir), axis=2) <= 0):
            raise ValueError("INVALID: nonfinite or silent IR")
        delay = np.zeros((len(xyz), 2), dtype=float)
        if "Data.Delay" in obj:
            ds = obj["Data.Delay"]
            if attr(ds, "Units").lower() not in ("", "sample", "samples"):
                raise ValueError("UNSUPPORTED: Data.Delay must be samples")
            raw = np.asarray(ds, dtype=float)
            if raw.shape == (1, 2):
                delay = np.broadcast_to(raw, delay.shape).copy()
            elif raw.shape == delay.shape:
                delay = raw.copy()
            else:
                raise ValueError("UNSUPPORTED: Data.Delay shape")
            if not np.isfinite(delay).all() or np.any(delay < 0) or np.max(delay) > FS:
                raise ValueError("INVALID: unsafe delay")
        receiver = obj.get("ReceiverPosition")
        receiver_status = (
            "UNVERIFIED: receiver acoustic plane/pressure calibration/open-blocked status"
            if receiver is None else
            "UNVERIFIED: receiver Type=" + attr(receiver, "Type") + ", Units=" + attr(receiver, "Units")
            + "; acoustic plane/pressure calibration/open-blocked status"
        )
    max_delay = float(np.max(delay))
    pad = int(math.ceil(max_delay)) + 4
    total = ir.shape[2] + pad
    times = np.arange(total)
    effective = np.zeros((len(xyz), 2, total))
    for k in range(len(xyz)):
        for ear in range(2):
            effective[k, ear] = np.interp(
                times - delay[k, ear], np.arange(ir.shape[2]), ir[k, ear], left=0.0, right=0.0
            )
    return {
        "xyz": xyz, "ir": effective, "sr": FS, "md5": md5, "sha256": digest(path),
        "receiver_status": receiver_status, "raw_ir_len": int(ir.shape[2]),
        "max_delay_samples": max_delay,
    }


def match_directions(xyz: np.ndarray, expected_count: int = 49) -> list[tuple[int, int, int, int]]:
    xyz = np.asarray(xyz, dtype=float)
    radius = np.linalg.norm(xyz, axis=1)
    if not np.isfinite(radius).all() or np.any(radius <= 0):
        raise ValueError("INVALID: source positions")
    unit = xyz / radius[:, None]
    bins = [np.flatnonzero(np.abs(radius - r) <= 0.015) for r in RADII]
    if any(len(b) != expected_count for b in bins):
        raise ValueError("UNSUPPORTED: unexpected per-radius measurement count")
    groups = []
    for base in bins[0]:
        group = [int(base)]
        for candidates in bins[1:]:
            cosines = np.clip(unit[candidates] @ unit[base], -1, 1)
            angles = np.rad2deg(np.arccos(cosines))
            order = np.argsort(angles)
            if angles[order[0]] > 2.0 or (len(order) > 1 and angles[order[1]] - angles[order[0]] < 0.05):
                raise ValueError("UNSUPPORTED: unmatched or ambiguous direction")
            group.append(int(candidates[order[0]]))
        groups.append(tuple(group))
    if any(len({group[i] for group in groups}) != len(groups) for i in range(4)):
        raise ValueError("INVALID: nonunique directional measurement matching")
    return groups


def split_coordinates(xyz: np.ndarray, groups: list[tuple[int, int, int, int]]) -> dict[str, list[int]]:
    unit = xyz[[g[0] for g in groups]]
    unit = unit / np.linalg.norm(unit, axis=1, keepdims=True)
    az = (np.rad2deg(np.arctan2(unit[:, 1], unit[:, 0])) + 180.0) % 360.0 - 180.0
    el = np.rad2deg(np.arcsin(np.clip(unit[:, 2], -1.0, 1.0)))
    order = sorted(range(len(groups)), key=lambda i: (float(az[i]), float(el[i]), *(float(v) for v in unit[i]), int(groups[i][0])))
    return {
        "final": [i for rank, i in enumerate(order) if rank % 5 == 0],
        "validation": [i for rank, i in enumerate(order) if rank % 5 == 1],
        "training": [i for rank, i in enumerate(order) if rank % 5 in (2, 3, 4)],
    }


def blend_shift(x: np.ndarray, offset: float) -> np.ndarray:
    t = np.arange(x.size, dtype=float)
    return np.interp(t - offset, t, x, left=0.0, right=0.0)


def candidate_indices(xyz: np.ndarray, groups: list[tuple[int, int, int, int]], train_dirs: list[int], target_xyz: np.ndarray) -> tuple[list[int], np.ndarray, float]:
    if not train_dirs:
        raise ValueError("INDETERMINATE: empty training directions")
    v = np.asarray(target_xyz, dtype=float)
    if v.shape != (3,) or not np.isfinite(v).all():
        raise ValueError("INVALID: finite 3D position required")
    radius = float(np.linalg.norm(v))
    if not 0.2 - 1e-8 <= radius <= 0.5 + 1e-8:
        raise ValueError("UNSUPPORTED: position outside measured radius domain")
    source_unit = xyz[[groups[d][0] for d in train_dirs]]
    source_unit = source_unit / np.linalg.norm(source_unit, axis=1, keepdims=True)
    angle = np.rad2deg(np.arccos(np.clip(source_unit @ (v / radius), -1, 1)))
    order = np.argsort(angle, kind="stable")
    if float(angle[order[0]]) > MAX_ANGLE_DEG:
        raise ValueError("UNSUPPORTED: no training direction within 45 degrees")
    best = [train_dirs[int(idx)] for idx in order[:3]]
    small = angle[order[:3]]
    if len(best) < 3:
        raise ValueError("INDETERMINATE: fewer than 3 neighbors")
    if small[0] < 1e-10:
        weight = np.array([1.0, 0.0, 0.0])
    else:
        inv = 1.0 / np.maximum(small, 1e-8)
        weight = inv / np.sum(inv)
    return best, weight, radius


def prediction(xyz: np.ndarray, ir: np.ndarray, groups: list[tuple[int, int, int, int]],
               train_dirs: list[int], target_xyz: np.ndarray, target_radius_index: int,
               stage: str, model: str) -> np.ndarray:
    if stage not in ("S1", "S2") or model not in ("B0", "B1", "C1"):
        raise ValueError("INVALID: stage or model")
    if target_radius_index not in (0, 1, 2, 3):
        raise ValueError("INVALID: radius index")
    if stage == "S1" and target_radius_index not in (0, 3):
        raise ValueError("INVALID: S1 target radius")
    if stage == "S2" and target_radius_index not in (1, 2):
        raise ValueError("INVALID: S2 target radius")
    neighbors, angular, radius = candidate_indices(xyz, groups, train_dirs, target_xyz)
    if model == "B0":
        # S2 radial endpoint tie at 0.35m deterministically chooses 0.2m.
        radial_idx = target_radius_index if stage == "S1" else (0 if abs(radius - 0.2) <= abs(radius - 0.5) else 3)
        return ir[groups[neighbors[0]][radial_idx]].copy()
    vertices: list[tuple[np.ndarray, float]] = []
    if stage == "S1":
        vertices = [(ir[groups[d][target_radius_index]], float(w)) for d, w in zip(neighbors, angular)]
    else:
        t = (radius - 0.2) / 0.3
        for d, w in zip(neighbors, angular):
            vertices.append((ir[groups[d][0]], float(w * (1 - t))))
            vertices.append((ir[groups[d][3]], float(w * t)))
    if model == "B1":
        return sum((weight * wave for wave, weight in vertices), np.zeros_like(vertices[0][0]))
    # Per-ear delay proxy; anchor large enough for all measured candidate peak positions.
    peaks = np.array([[int(np.argmax(np.abs(wave[ear]))) for ear in range(2)] for wave, _ in vertices])
    anchor = float(np.max(peaks) + 32)
    out = np.zeros_like(vertices[0][0])
    for ear in range(2):
        aligned = sum(
            (weight * blend_shift(wave[ear], anchor - peaks[i, ear])
             for i, (wave, weight) in enumerate(vertices)),
            np.zeros(out.shape[1], dtype=float),
        )
        desired_peak = sum(weight * peaks[i, ear] for i, (_, weight) in enumerate(vertices))
        out[ear] = blend_shift(aligned, desired_peak - anchor)
    return out


def ild(h: np.ndarray) -> list[float]:
    if h.ndim != 2 or h.shape[0] != 2 or not np.isfinite(h).all():
        raise ValueError("INVALID: finite bilateral response required")
    sp = np.fft.rfft(h, axis=1)
    freq = np.fft.rfftfreq(h.shape[1], 1.0 / FS)
    out = []
    for lo, hi in BANDS:
        mask = (freq >= lo) & (freq < hi)
        amp = np.sqrt(np.sum(np.abs(sp[:, mask]) ** 2, axis=1))
        if not np.isfinite(amp).all() or np.any(amp <= 1e-12):
            raise ValueError("INDETERMINATE: zero or nonfinite band energy")
        out.append(float(20 * np.log10(amp[0] / amp[1])))
    return out


def itd_us(h: np.ndarray) -> float:
    filt = sosfiltfilt(butter(4, [500, 1500], fs=FS, btype="bandpass", output="sos"), h, axis=1)
    if np.min(np.sum(filt ** 2, axis=1)) <= 1e-20:
        raise ValueError("INDETERMINATE: ITD band energy")
    cc = correlate(filt[0], filt[1], mode="full", method="fft")
    idx = int(np.argmax(cc))
    if not 0 < idx < len(cc) - 1:
        raise ValueError("INDETERMINATE: ITD boundary peak")
    y0, y1, y2 = cc[idx - 1:idx + 2]
    denom = y0 - 2 * y1 + y2
    shift = 0.0 if abs(denom) < 1e-20 else 0.5 * (y0 - y2) / denom
    if not np.isfinite(shift) or abs(shift) > 1:
        raise ValueError("INDETERMINATE: ITD peak refinement")
    return float((idx - h.shape[1] + 1 + shift) * 1e6 / FS)


def shape_rmse_db(h: np.ndarray, measured: np.ndarray) -> list[float]:
    freq = np.fft.rfftfreq(h.shape[1], 1 / FS)
    mask = (freq >= 500) & (freq < 8000)
    out = []
    for ear in range(2):
        a = 20 * np.log10(np.maximum(np.abs(np.fft.rfft(h[ear])[mask]), 1e-12))
        b = 20 * np.log10(np.maximum(np.abs(np.fft.rfft(measured[ear])[mask]), 1e-12))
        a -= np.mean(a)
        b -= np.mean(b)
        out.append(float(np.sqrt(np.mean((a - b) ** 2))))
    return out


def summarise(records: list[dict], selected: str = "final") -> dict:
    rows = [x for x in records if x["split"] == selected]
    directions = sorted({row["direction"] for row in rows if row["supported"]})
    if len(directions) < 8:
        return {"verdict": "INDETERMINATE", "supported_directions": len(directions),
                "total_direction_count": len({r["direction"] for r in rows}), "reason": "fewer than eight supported direction groups"}
    def metric(m: str, stage: str | None = None, field: str = "abs_ild_errors_db") -> float:
        found = [row for row in rows if row["supported"] and row["model"] == m and (stage is None or row["stage"] == stage)]
        values = [v for row in found for v in (row[field] if isinstance(row[field], list) else [row[field]])]
        return float(np.median(values))
    stats = {m: {
        "median_ild_error_db": metric(m), "S1_median_ild_error_db": metric(m, "S1"),
        "S2_median_ild_error_db": metric(m, "S2"),
        "median_abs_itd_error_us": metric(m, field="abs_itd_error_us"),
        "p95_ild_error_db": float(np.percentile([
            v for row in rows if row["model"] == m and row["supported"] for v in row["abs_ild_errors_db"]
        ], 95)),
        "median_ear_shape_rmse_db": metric(m, field="ear_shape_rmse_db"),
    } for m in ("B0", "B1", "C1")}
    matrix = {}
    for model in ("B1", "C1"):
        matrix[model] = np.asarray([
            [v for row in rows if row["supported"] and row["direction"] == d and row["model"] == model
             for v in row["abs_ild_errors_db"]] for d in directions
        ])
    rng = np.random.default_rng(20261030)
    diffs = []
    for _ in range(2000):
        sample = rng.integers(0, len(directions), size=len(directions))
        diffs.append(float(np.median(matrix["B1"][sample]) - np.median(matrix["C1"][sample])))
    ci = [float(v) for v in np.percentile(diffs, [2.5, 97.5])]
    b, c = stats["B1"], stats["C1"]
    passed = bool(
        c["median_ild_error_db"] <= 0.8 * b["median_ild_error_db"]
        and ci[0] > 0
        and all(c[st + "_median_ild_error_db"] < b[st + "_median_ild_error_db"] for st in ("S1", "S2"))
        and c["median_abs_itd_error_us"] <= b["median_abs_itd_error_us"] + 25
    )
    return {"verdict": "GO_LIMITED_NUMERICAL_CANDIDATE" if passed else "REVISE_OR_REJECT",
            "statistics": stats, "ild_improvement_ci95_db": ci, "supported_directions": len(directions),
            "total_direction_count": len({r["direction"] for r in rows}),
            "bootstrap_seed": 20261030, "bootstrap_draws": 2000}


def evaluate(data: dict) -> dict:
    xyz, ir = data["xyz"], data["ir"]
    groups = match_directions(xyz)
    split = split_coordinates(xyz, groups)
    records: list[dict] = []
    # Validation is not used for tuning in v1.0, but stored as a distinct reporting set.
    for name in ("validation", "final"):
        for direction in split[name]:
            for stage, radii in (("S1", (0, 3)), ("S2", (1, 2))):
                for ri in radii:
                    target_idx = groups[direction][ri]
                    target_xyz = xyz[target_idx]
                    try:
                        # Only metadata and full training directions can determine coverage.
                        candidate_indices(xyz, groups, split["training"], target_xyz)
                    except ValueError as exc:
                        if not str(exc).startswith("UNSUPPORTED:"):
                            raise
                        for model in ("B0", "B1", "C1"):
                            records.append({"split": name, "direction": int(direction), "stage": stage, "radius_m": RADII[ri],
                                            "model": model, "supported": False, "refusal": str(exc), "target_index": int(target_idx),
                                            "train_direction_ids": split["training"]})
                        continue
                    truth = ir[target_idx]
                    ti, tt = np.asarray(ild(truth)), itd_us(truth)
                    for model in ("B0", "B1", "C1"):
                        predicted = prediction(xyz, ir, groups, split["training"], target_xyz, ri, stage, model)
                        records.append({
                            "split": name, "direction": int(direction), "stage": stage, "radius_m": RADII[ri],
                            "model": model, "supported": True, "target_index": int(target_idx),
                            "train_direction_ids": split["training"],
                            "training_radius_indices": [ri] if stage == "S1" else [0, 3],
                            "abs_ild_errors_db": np.abs(np.asarray(ild(predicted)) - ti).tolist(),
                            "abs_itd_error_us": abs(itd_us(predicted) - tt),
                            "ear_shape_rmse_db": shape_rmse_db(predicted, truth),
                        })
    return {
        "schema_version": "el-nf2-evidence-v1",
        "adoption": "NOT_ADOPTED",
        "scientific_claim": "single artificial head, relative L/R, measured 0.2-0.5m positions only",
        "preregistration_commit": PREREG_COMMIT,
        "split_direction_ids": split,
        "split_measurement_indices": {key: [[int(i) for i in groups[d]] for d in ids] for key, ids in split.items()},
        "records": records,
        "validation": summarise(records, "validation"),
        "final": summarise(records, "final"),
        "g4_blind_listening": "PENDING",
        "g5_independent_science_review": "PENDING",
    }


def run(sofa: Path, output: Path, require_original: bool = True) -> dict:
    if output.exists():
        raise FileExistsError("INVALID: evidence must not be overwritten")
    data = load_sofa(sofa, require_original)
    evidence = evaluate(data)
    evidence["measurement"] = {
        key: data[key] for key in ("sha256", "md5", "receiver_status", "raw_ir_len", "max_delay_samples")
    }
    evidence["runner_sha256"] = digest(Path(__file__))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return evidence


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sofa", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = run(args.sofa, args.output)
    print(json.dumps({"evidence": str(args.output), "final": result["final"]["verdict"],
                      "supported": result["final"]["supported_directions"]}, allow_nan=False))
