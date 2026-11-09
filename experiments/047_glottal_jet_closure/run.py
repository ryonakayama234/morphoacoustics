"""P0 research-only prescribed glottal aperture -> jet flow and gated aspiration.

This is NOT a vocal-fold self-oscillator or an adopted speech source.
WAV rendering uses the existing, pinned CC-A2 M0 /a/-like tract via SV-1.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import runpy
import wave

import numpy as np

SAMPLE_RATE = 48_000
SAMPLES = 24_000
F0_HZ = 100.0
RHO = 1.2  # kg/m^3
MU = 1.8e-5  # Pa*s
CD = 0.6  # dimensionless jet coefficient (hypothesis)
WIDTH_M = 1.0e-3  # characteristic shear width, uncalibrated
LENGTH_M = 2.0e-3  # turbulence correlation length, uncalibrated
RE_ONSET = 1_000.0  # phenomenological, NOT a universal turbulence threshold
OPEN_QUOTIENT = 0.6
A_MAX_M2 = 1.0e-6
SEED = 47001

CASES = {
    "modal": (800.0, 0.0, 0.02),
    "breathy_gap": (800.0, 0.15e-6, 0.02),
    "pressure_x2": (1600.0, 0.0, 0.02),
    "noise_off": (800.0, 0.0, 0.0),
}


def make_source(pressure_pa: float, leak_area_m2: float, noise_fraction: float,
                *, samples: int = SAMPLES, seed: int = SEED) -> dict[str, np.ndarray | float]:
    """Prescribed aperture and Bernoulli jet, plus narrow research stochastic closure.

    Noise is a jet-flow perturbation *before* the acoustic tube, never audio EQ.
    Physical area waveform is imposed, not solved from tissue/aerodynamics.
    """
    if (not all(math.isfinite(z) for z in (pressure_pa, leak_area_m2, noise_fraction))
            or pressure_pa < 0 or leak_area_m2 < 0 or noise_fraction < 0
            or samples < 2 or type(seed) is not int):
        raise ValueError("invalid nonnegative physical/source controls")
    phase = np.mod(np.arange(samples, dtype=np.float64) * (F0_HZ / SAMPLE_RATE), 1.0)
    aperture = np.zeros(samples, dtype=np.float64)
    open_mask = phase < OPEN_QUOTIENT
    aperture[open_mask] = np.sin(np.pi * phase[open_mask] / OPEN_QUOTIENT) ** 2
    area = leak_area_m2 + A_MAX_M2 * aperture
    velocity = CD * math.sqrt(2.0 * pressure_pa / RHO)
    flow = area * velocity
    reynolds = RHO * velocity * WIDTH_M / MU
    turbulence_gate = max(0.0, 1.0 - RE_ONSET / reynolds) if reynolds > 0.0 else 0.0
    corner_hz = velocity / (2.0 * math.pi * LENGTH_M) if velocity > 0 else 0.0
    decay = math.exp(-2.0 * math.pi * corner_hz / SAMPLE_RATE)
    xi = np.random.default_rng(seed).standard_normal(samples)
    colored = np.empty(samples, dtype=np.float64)
    previous = 0.0
    diffusion = math.sqrt(max(0.0, 1.0 - decay * decay))
    for i in range(samples):
        previous = decay * previous + diffusion * xi[i]
        colored[i] = previous
    # Single explicit file onset/offset envelope; no interior pulse reset.
    ramp = int(0.01 * SAMPLE_RATE)
    envelope = np.ones(samples, dtype=np.float64)
    if samples < 2 * ramp:
        raise ValueError("samples must accommodate the frozen edge envelope")
    fade = np.sin(np.arange(ramp) * (0.5 * np.pi / ramp)) ** 2
    envelope[:ramp] *= fade
    envelope[-ramp:] *= fade[::-1]
    voiced = flow * envelope
    aspiration = noise_fraction * turbulence_gate * flow * colored * envelope
    return {
        "source_m3_s": voiced + aspiration,
        "flow_m3_s": voiced,
        "aspiration_m3_s": aspiration,
        "glottal_area_m2": area,
        "reynolds": float(reynolds),
        "jet_velocity_m_s": float(velocity),
        "closure_corner_hz": float(corner_hz),
        "closure_gate": float(turbulence_gate),
    }


def _wav_bytes(pressure_pa: np.ndarray, gain: float) -> bytes:
    pcm = np.rint(np.clip(pressure_pa * gain, -0.999, 0.999) * 32767.0).astype("<i2")
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())
    return output.getvalue()


def _high_band_energy(x: np.ndarray, cutoff_hz: float = 2000.0) -> float:
    spectrum = np.abs(np.fft.rfft(x)) ** 2
    freq = np.fft.rfftfreq(x.size, 1.0 / SAMPLE_RATE)
    energy = float(spectrum.sum())
    return float(spectrum[freq >= cutoff_hz].sum() / energy) if energy > 0 else 0.0


def execute(output_path: Path) -> dict[str, object]:
    """New real M0 static-tract pressure for every non-null candidate."""
    root = Path(__file__).resolve().parents[2]
    sv1 = runpy.run_path(str(root / "experiments/042_sv1_sustained_vowel/run.py"))
    _, exp, resolution = sv1["_validated_context"]()
    geometry = resolution.preset.prepared.rest_state
    generated: dict[str, tuple[dict[str, np.ndarray | float], np.ndarray]] = {}
    for name, (pressure, leak, noise) in CASES.items():
        generated[name] = (source := make_source(pressure, leak, noise),
                           sv1["_render"](exp, geometry, source["source_m3_s"]))
    # ONE common playback gain preserves cross-case intensity differences.
    global_peak = max(float(np.max(np.abs(p))) for _, p in generated.values())
    if not (math.isfinite(global_peak) and global_peak > 0):
        raise RuntimeError("invalid physical pressure / common listening scale")
    gain = 0.8 / global_peak
    output_path.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, object] = {
        "schema": "research.glottal_jet_p0.v1",
        "source_head": "MUST_FILL_FROM_GITHUB_CI_OR_LOCAL_GIT_HEAD",
        "adoption": "NOT_ADOPTED_RESEARCH",
        "source_model": "prescribed_aperture_bernoulli_plus_gated_OU_closure",
        "body": "CC-A2 prepared M0@1 from pinned SV-1",
        "render": "SV-1 existing actual static Core physical pressure",
        "sample_rate_hz": SAMPLE_RATE,
        "sample_count": SAMPLES,
        "seed": SEED,
        "common_listening_gain_per_pa": gain,
        "settings": {"rho": RHO, "mu": MU, "cd": CD, "width_m": WIDTH_M,
                     "correlation_length_m": LENGTH_M, "re_onset_hypothesis": RE_ONSET,
                     "a_max_m2": A_MAX_M2, "open_quotient": OPEN_QUOTIENT},
        "cases": {},
    }
    for name, (source, pressure) in generated.items():
        f = output_path / f"{name}.wav"
        f.write_bytes(_wav_bytes(pressure, gain))
        sp = output_path / f"{name}_source.npy"
        pp = output_path / f"{name}_pressure_pa.npy"
        np.save(sp, source["source_m3_s"], allow_pickle=False)
        np.save(pp, pressure, allow_pickle=False)
        manifest["cases"][name] = {
            "inputs": dict(zip(("pressure_pa", "leak_area_m2", "noise_fraction"), CASES[name])),
            "source_hash": hashlib.sha256(sp.read_bytes()).hexdigest(),
            "raw_pressure_hash": hashlib.sha256(pp.read_bytes()).hexdigest(),
            "listening_wav_hash": hashlib.sha256(f.read_bytes()).hexdigest(),
            "reynolds": source["reynolds"],
            "closure_corner_hz": source["closure_corner_hz"],
            "closure_gate": source["closure_gate"],
            "source_2khz_fraction": _high_band_energy(source["source_m3_s"]),
            "raw_pressure_2khz_fraction": _high_band_energy(pressure),
            "raw_pressure_rms_pa": float(np.sqrt(np.mean(pressure ** 2))),
        }
    (output_path / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(execute(args.out), indent=2))
