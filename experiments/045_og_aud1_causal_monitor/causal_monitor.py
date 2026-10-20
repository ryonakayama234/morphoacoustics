"""OG-AUD1 Experiment 045: research-only causal 3-duct pressure monitor.

Not a published Core API, radiated sound, human phonation, or scientific Gate B.
Source U: m3/s.  Pressure p: Pa.  Both downstream terminations matched.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import wave

import numpy as np

FS = 48000
FRAMES = 48000
RHO, SOUND_C = 1.2, 343.0
AREA_A = AREA_B = .0003
L_A, L_B, L_C = .08, .09, .06
AREAS_C = (.00015, .0006)
TONES = (233., 733., 997., 1801., 2801.)
WEIGHTS = (.35, .30, .25, .18, .10)
PHASES = (0., .17, .41, .29, .63)
ECHO_COUNT = 48


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def npy_bytes(x: np.ndarray) -> bytes:
    out = io.BytesIO()
    np.save(out, np.asarray(x, dtype="<f8"), allow_pickle=False)
    return out.getvalue()


def source(t: np.ndarray) -> np.ndarray:
    t = np.asarray(t, dtype=np.float64)
    if not np.all(np.isfinite(t)):
        raise ValueError("INVALID:TIME")
    u = np.zeros(t.shape, dtype=np.float64)
    active = (t >= .10) & (t < .40)
    tau = t[active] - .10
    s = tau / .30
    carrier = np.zeros_like(tau)
    for freq, weight, phase in zip(TONES, WEIGHTS, PHASES):
        carrier += weight * np.sin(2 * np.pi * freq * tau + phase)
    u[active] = 1e-6 * np.sin(np.pi * s)**6 * carrier
    return u


def physical_parameters(c_area: float) -> tuple[float, float, float]:
    if type(c_area) not in (int, float) or c_area not in AREAS_C:
        raise ValueError("UNSUPPORTED:FIXED_BODY_ONLY")
    z0 = RHO * SOUND_C / AREA_A
    z_b = RHO * SOUND_C / AREA_B
    z_c = RHO * SOUND_C / c_area
    z_j = 1 / (1 / z_b + 1 / z_c)
    reflection = (z_j - z0) / (z_j + z0)
    return z0, reflection, 2 * L_A / SOUND_C


def forward(t: np.ndarray, c_area: float) -> np.ndarray:
    z0, reflection, delay = physical_parameters(c_area)
    result = np.zeros(t.shape, dtype=np.float64)
    for k in range(ECHO_COUNT + 1):
        result += reflection**k * source(t - k * delay)
    return z0 * result


def ports(t: np.ndarray, c_area: float) -> tuple[dict, dict]:
    """Signed volume flow positive A.in->A.out and J->B/C."""
    t = np.asarray(t, dtype=np.float64)
    if t.ndim != 1 or not np.all(np.isfinite(t)):
        raise ValueError("INVALID:TIME_VECTOR")
    z0, r, delay = physical_parameters(c_area)
    f0 = forward(t, c_area)
    fj = forward(t - L_A / SOUND_C, c_area)
    pj = (1 + r) * fj
    bout = (1 + r) * forward(t - L_A / SOUND_C - L_B / SOUND_C, c_area)
    cout = (1 + r) * forward(t - L_A / SOUND_C - L_C / SOUND_C, c_area)
    zb = RHO * SOUND_C / AREA_B
    zc = RHO * SOUND_C / c_area
    states = {
        "A.in": (2 * f0 - z0 * source(t), source(t)),
        "A.out": (pj, (1 - r) * fj / z0),
        "B.in": (pj, pj / zb),
        "B.out": (bout, bout / zb),
        "C.in": (pj, pj / zc),
        "C.out": (cout, cout / zc),
    }
    work = lambda port: float(np.sum(states[port][0] * states[port][1]) / FS)
    energy_in = work("A.in")
    energy_out = work("B.out") + work("C.out")
    flow_residual = float(np.max(np.abs(states["A.out"][1] - states["B.in"][1] - states["C.in"][1])))
    energy_rel = abs(energy_in - energy_out) / max(abs(energy_in), 1e-30)
    source_bound = 1e-6 * sum(abs(w) for w in WEIGHTS)
    omitted_echo_pa = 2*z0*source_bound*abs(r)**(ECHO_COUNT+1)/(1-abs(r))
    if (energy_in <= 0 or energy_out <= 0 or energy_rel >= 1e-6
        or flow_residual >= 1e-15 or omitted_echo_pa >= 1e-10):
        raise ArithmeticError("NUMERICALLY_UNRESOLVED:PASSIVITY_OR_ECHO_BOUND")
    if not np.all(states["A.in"][0][t < .10] == 0):
        raise ArithmeticError("NUMERICALLY_UNRESOLVED:PRE_ECHO")
    diag = {
        "reflection": r, "roundtrip_s": delay, "echo_order": ECHO_COUNT,
        "omitted_echo_pressure_upper_bound_pa": omitted_echo_pa,
        "energy_in_j": energy_in, "energy_out_j": energy_out,
        "relative_energy_imbalance": energy_rel,
        "max_junction_flow_residual_m3s": flow_residual,
        "junction_pressure_residual_pa": 0.0,
        "source_prestart_pressure_exact_zero": True,
    }
    return states, diag


def wav_bytes(pressure: np.ndarray, gain: float) -> bytes:
    pcm = np.rint(pressure * gain * 32767)
    if not np.all(np.isfinite(pcm)) or np.max(np.abs(pcm)) > 32767:
        raise ArithmeticError("FAILED:PCM_CLIPPING")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(FS)
        out.writeframes(pcm.astype("<i2").tobytes())
    return buffer.getvalue()


def compute() -> tuple[dict, dict[str, bytes]]:
    t = np.arange(FRAMES, dtype=np.float64) / FS
    u = source(t)
    states_a, diag_a = ports(t, AREAS_C[0])
    states_b, diag_b = ports(t, AREAS_C[1])
    pressure_a, pressure_b = states_a["A.in"][0], states_b["A.in"][0]
    effect = float(np.sqrt(np.mean((pressure_a-pressure_b)**2)) /
                   np.sqrt(np.mean(pressure_a**2)))
    if effect <= 1e-3:
        raise ArithmeticError("NUMERICALLY_UNRESOLVED:NO_BODY_EFFECT")
    gain = float(.8 / max(np.max(np.abs(pressure_a)), np.max(np.abs(pressure_b))))
    files = {"raw_U_m3_s.npy": npy_bytes(u)}
    records = []
    for name, area, p, diag in (
        ("small_C", AREAS_C[0], pressure_a, diag_a),
        ("large_C", AREAS_C[1], pressure_b, diag_b),
    ):
        p_path, w_path = f"{name}/raw_p_Ain_Pa.npy", f"{name}/monitor_48k_pcm16.wav"
        files[p_path] = npy_bytes(p)
        files[w_path] = wav_bytes(p, gain)
        records.append({"body": name, "c_area_m2": area,
                        "raw_pressure_path": p_path, "wave_path": w_path,
                        "diagnostic": diag})
    receipt = {
        "schema": "og-aud1.causal.experiment.v0",
        "status": "EXPLORATORY_NOT_ADOPTED",
        "physical_claim": "CAUSAL_SOURCE_PORT_PRESSURE_NON_RADIATED",
        "source_plane": "A.in", "monitor_plane": "A.in",
        "source_unit": "m3/s", "pressure_unit": "Pa",
        "sample_rate_hz": FS, "frames": FRAMES,
        "rho_kg_m3": RHO, "c_m_s": SOUND_C,
        "lengths_abc_m": [L_A, L_B, L_C],
        "areas_ab_m2": [AREA_A, AREA_B],
        "junction_law": "ideal.branch3.p_u", "both_distal_terminations": "matched",
        "source_sha256": sha256(files["raw_U_m3_s.npy"]),
        "echo_policy": "continuous-time analytic fractional delay; 48 causal echoes; no FFT cutoff",
        "relative_raw_pressure_rms_difference": effect,
        "shared_playback_gain_inverse_pa": gain,
        "records": records,
        "sha256_by_relative_path": {path:sha256(data) for path,data in sorted(files.items())},
        "code_sha256": sha256(Path(__file__).read_bytes()),
        "runtime": {"python":sys.version.split()[0], "numpy":np.__version__},
        "forbidden_claims": ["actual speech", "radiated audio", "calibrated SPL", "general graph editor", "Gate B passed"],
    }
    return receipt, files


def run(destination: Path) -> dict:
    receipt, files = compute()
    if destination.exists():
        raise FileExistsError("IMMUTABLE:OUTPUT_EXISTS")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".og-aud1-stage-") as tmp:
        stage = Path(tmp)
        for rel, raw in files.items():
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            if sha256(target.read_bytes()) != receipt["sha256_by_relative_path"][rel]:
                raise IOError("FAILED:READBACK_HASH_MISMATCH")
        (stage / "manifest.json").write_text(
            json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        stage.rename(destination)
    return receipt


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python causal_monitor.py NEW_OUTPUT_DIRECTORY")
    print(json.dumps(run(Path(sys.argv[1])), indent=2))
