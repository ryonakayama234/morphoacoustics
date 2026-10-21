"""Render W1 new breath source traces and ideal stereo receiver only; B/Studio are W2+.
Run: python experiments/042_nv1_breath_ear/run.py --output /tmp/nv1-w1-first
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import soundfile as sf

from source import (FS, N, PRESETS, RHO, C, SEED, SCHEMA,
                    realize_exhale, source_from_flow, describe_spectrum)

# Fixed two-probe free-field A geometry, 30cm front, research-only.
SOURCE_XYZ = np.array([0.30, 0.0, 0.0], dtype=np.float64)
RECEIVERS_LR = np.array([[0.0, .09, 0.0], [0.0, -.09, 0.0]])
# One disclosed gain across all presets. It is presentation-only, not calibrated SPL.
PLAYBACK_GAIN = 70.0


def git_receipt() -> dict:
    root = Path(__file__).resolve().parents[2]
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                      stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root,
                                             stderr=subprocess.DEVNULL).strip())
        return {"core_commit_sha": sha, "git_dirty": dirty}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"core_commit_sha": None, "git_dirty": None}


def render_a(source) -> np.ndarray:
    """Analytic monopole L/R p(r,t) in Pa, with fractional travel delay."""
    from scipy.signal import fftconvolve
    d = np.linalg.norm(RECEIVERS_LR - SOURCE_XYZ, axis=1)
    taps = np.arange(-48, 49)
    out = []
    for distance in d:
        delays = distance / C * FS
        i = int(np.floor(delays))
        frac = delays - i
        kernel = np.sinc(taps - frac) * np.kaiser(len(taps), 9)
        kernel /= kernel.sum()
        # Preserve causal fractional-delay kernel's group-delay convention.
        full = fftconvolve(source.dq_dt_m3_s2, kernel, mode="full")
        padded = np.pad(full, (max(i-48, 0), 0)) if i >= 48 else np.pad(full[48:], (i, 0))
        out.append((RHO / (4 * np.pi * distance)) * padded)
    raw = np.zeros((max(len(v) for v in out), 2), dtype=np.float64)
    for k, x in enumerate(out):
        raw[:len(x), k] = x
    return raw


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output: Path, preset_names: tuple[str, ...] = ("P0", "P2", "A2", "Z0")) -> dict:
    if output.exists():
        raise FileExistsError("INVALID: output path already exists; no overwrite")
    if not preset_names or len(set(preset_names)) != len(preset_names) or any(p not in PRESETS for p in preset_names):
        raise ValueError("INVALID: unsupported or repeated preset")
    output.mkdir(parents=True, exist_ok=False)
    (output / "audio").mkdir()
    (output / "traces").mkdir()
    result = {"schema": SCHEMA, "claim": "EXPERIMENTAL_NOT_ADOPTED",
              "scope": "W0_W1_IDEAL_A_ONLY", "rate_hz": FS, "seed": SEED,
              "render": "analytic_monopole_ideal_A", "receiver_units": "modeled_Pa",
              "receiver_xyz_l_r_m": RECEIVERS_LR.tolist(),
              "source_xyz_m": SOURCE_XYZ.tolist(),
              "playback_gain": PLAYBACK_GAIN,
              "limitations": ["uncalibrated stochastic closure", "no vocal folds or oral tract",
                              "no measured HRTF and no human naturalness verdict"],
              **git_receipt(), "cases": {}}
    for preset in preset_names:
        pressure, aperture = PRESETS[preset]
        flow = realize_exhale(pressure, aperture)
        source = source_from_flow(flow)
        acoustic_pa = render_a(source)
        playback = acoustic_pa * PLAYBACK_GAIN
        if not np.isfinite(playback).all() or np.max(abs(playback)) > 0.95:
            raise ValueError(f"INVALID: clipping or nonfinite presentation in {preset}")
        wav = output / "audio" / f"{preset}_ideal_A_48k_stereo.wav"
        sf.write(wav, playback, FS, subtype="PCM_24")
        trace = output / "traces" / f"{preset}.npz"
        np.savez_compressed(trace, pressure_pa=flow.pressure_pa, aperture_m2=flow.aperture_m2,
            q_mean_m3_s=flow.q_mean_m3_s, jet_speed_m_s=flow.jet_speed_m_s,
            reynolds=flow.reynolds, pneumatic_power_w=flow.pneumatic_power_w,
            q_ac_m3_s=source.q_ac_m3_s, dq_dt_m3_s2=source.dq_dt_m3_s2,
            spectral_knee_hz=source.spectral_knee_hz, receiver_raw_A_pa=acoustic_pa)
        result["cases"][preset] = {
            "pressure_peak_pa": pressure, "effective_aperture_m2": aperture,
            "mean_flow_peak_l_s": float(np.max(flow.q_mean_m3_s)) * 1000,
            "reynolds_peak": float(np.max(flow.reynolds)),
            "pressure_power_peak_w": float(np.max(flow.pneumatic_power_w)),
            "source_sha256": source.source_sha256,
            "source_spectrum": describe_spectrum(source.q_ac_m3_s),
            "mean_pneumatic_power_w": source.mean_pneumatic_power_w,
            "ideal_monopole_acoustic_power_w": source.ideal_acoustic_power_w,
            "ideal_monopole_efficiency": source.efficiency,
            "raw_pa_peak": float(np.max(abs(acoustic_pa))),
            "playback_peak": float(np.max(abs(playback))),
            "wav": str(wav.relative_to(output)), "wav_sha256": sha(wav),
            "trace": str(trace.relative_to(output)), "trace_sha256": sha(trace)}
    (output / "evidence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = run(args.output)
    print(json.dumps({"output": str(args.output),
                      "case_spectra": {k: v["source_spectrum"] for k,v in evidence["cases"].items()}},
                      indent=2))
