"""OG-AUD1 experiment-local, bandlimited source-port pressure monitor.

Research prototype, NOT verified OG-4 continuous API, radiated speech or
accepted physical waveform. Read PROTOCOL_CANDIDATE.md before running.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
from pathlib import Path
import struct
import sys
import tempfile
import wave

import numpy as np

SAMPLE_RATE = 48_000
N_SAMPLES = 48_000
NFFT = 131_072
C_AREAS_M2 = (0.00015, 0.00060)
MAX_HZ = 4_000.0
RHO = 1.2
SOUND_SPEED = 343.0
L_A = 0.08
AREA_A = 0.0003
AREA_B = 0.0003
L_B = 0.09
L_C = 0.06
FREQUENCIES = (233.0, 733.0, 997.0, 1801.0, 2801.0)
WEIGHTS = (0.35, 0.30, 0.25, 0.18, 0.10)
PHASES = (0.0, 0.17, 0.41, 0.29, 0.63)
STATUS = 'EXPLORATORY_ENGINEERING_ONLY_NOT_GATE_B'


def sha256(b: bytes) -> str:
    return 'sha256:' + hashlib.sha256(b).hexdigest()


def array_npy_bytes(a: np.ndarray) -> bytes:
    out = io.BytesIO()
    np.save(out, np.asarray(a, dtype='<f8'), allow_pickle=False)
    return out.getvalue()


def source() -> np.ndarray:
    t = np.arange(N_SAMPLES, dtype=np.float64) / SAMPLE_RATE
    x = np.zeros(N_SAMPLES, dtype=np.float64)
    mask = (t >= 0.10) & (t < 0.40)
    tau = t[mask] - 0.10
    s = tau / 0.30
    carrier = np.zeros_like(tau)
    for f, weight, phase in zip(FREQUENCIES, WEIGHTS, PHASES):
        carrier += weight * np.sin(2.0 * np.pi * f * tau + phase)
    x[mask] = 1.0e-6 * np.sin(np.pi * s) ** 6 * carrier
    return x


def transfer(area_c: float, freqs_hz: np.ndarray) -> tuple[np.ndarray, float]:
    # A fixed, typed three-port matched 1D graph, not a universal organ editor.
    if type(area_c) not in (float, int) or area_c not in C_AREAS_M2:
        raise ValueError('UNSUPPORTED:C_AREA_OUTSIDE_FIXED_FIXTURE')
    freqs_hz = np.asarray(freqs_hz)
    if freqs_hz.ndim != 1 or not np.all(np.isfinite(freqs_hz)) or np.any(freqs_hz < 0):
        raise ValueError('INVALID:FREQUENCY_GRID')
    z0 = RHO * SOUND_SPEED / AREA_A
    zb = RHO * SOUND_SPEED / AREA_B
    zc = RHO * SOUND_SPEED / area_c
    zj = 1.0 / (1.0 / zb + 1.0 / zc)
    reflection = (zj - z0) / (zj + z0)
    travel = np.exp(-4j * np.pi * freqs_hz * L_A / SOUND_SPEED)
    zin = z0 * (1.0 + reflection * travel) / (1.0 - reflection * travel)
    if (not np.all(np.isfinite(zin))) or np.any(zin.real <= 0.0):
        raise ArithmeticError('NUMERICALLY_UNRESOLVED:IMPEDANCE')
    return zin, reflection


def render_pressure(u: np.ndarray, area_c: float) -> tuple[np.ndarray, dict]:
    if u.shape != (N_SAMPLES,) or u.dtype != np.float64 or not np.all(np.isfinite(u)):
        raise ValueError('INVALID:SOURCE_SAMPLES')
    if not np.array_equal(u[:4800], np.zeros(4800)) or not np.array_equal(u[19200:], np.zeros(N_SAMPLES-19200)):
        raise ValueError('UNSUPPORTED:SOURCE_ENVELOPE')
    freq = np.fft.rfftfreq(NFFT, 1.0/SAMPLE_RATE)
    spectrum_u = np.fft.rfft(u, n=NFFT)
    band = freq <= MAX_HZ
    highband = float(np.sum(np.abs(spectrum_u[~band])**2) / np.sum(np.abs(spectrum_u[1:])**2))
    if highband >= 1e-8:
        raise ArithmeticError(f'NUMERICALLY_UNRESOLVED:SOURCE_HIGHBAND:{highband}')
    impedance, reflection = transfer(area_c, freq[band])
    spectrum_p = np.zeros_like(spectrum_u)
    spectrum_p[band] = spectrum_u[band] * impedance
    p_full = np.fft.irfft(spectrum_p, n=NFFT)
    p = np.array(p_full[:N_SAMPLES], dtype=np.float64)
    amp = float(np.max(np.abs(p)))
    if not np.isfinite(amp) or amp <= 0.0:
        raise ArithmeticError('NUMERICALLY_UNRESOLVED:ZERO_PRESSURE')
    pre_guard = float(np.max(np.abs(p[:2400]))/amp)
    tail_guard = float(np.max(np.abs(p_full[40800:]))/amp)
    assert np.isfinite(pre_guard) and np.isfinite(tail_guard)
    if pre_guard >= 1e-5 or tail_guard >= 1e-5:
        raise ArithmeticError(f'NUMERICALLY_UNRESOLVED:WINDOW:{pre_guard}:{tail_guard}')
    passed_power = float(np.dot(p, u) / SAMPLE_RATE)
    if passed_power < -1e-12:
        raise ArithmeticError('NUMERICALLY_UNRESOLVED:NEGATIVE_PASSIVE_ENERGY')
    # all-frequency output is truly lowpass in padded FFT; inverse roundoff tolerated.
    high_output = float(np.sum(np.abs(np.fft.rfft(p_full, n=NFFT)[~band])**2) /
                        np.sum(np.abs(spectrum_p[band])**2))
    if high_output >= 1e-20:
        raise ArithmeticError('NUMERICALLY_UNRESOLVED:HIGHBAND_LEAK')
    return p, {'c_area_m2': area_c, 'junction_reflection': reflection,
               'highband_input_energy_ratio': highband, 'highband_output_energy_ratio': high_output,
               'prestart_peak_fraction': pre_guard, 'tail_peak_fraction': tail_guard,
               'source_pressure_work_J': passed_power, 'peak_pressure_Pa': amp,
               'impedance_real_min': float(np.min(impedance.real)),
               'sample_rate_hz': SAMPLE_RATE, 'fft_length': NFFT,
               'spectral_bin_step_hz': SAMPLE_RATE/NFFT,
               'band_max_hz': MAX_HZ}


def pcm_wav_bytes(p: np.ndarray, shared_gain_inverse_pa: float) -> bytes:
    scaled = np.rint(p * shared_gain_inverse_pa * 32767.0)
    if not np.all(np.isfinite(scaled)) or np.max(np.abs(scaled)) > 32767:
        raise ArithmeticError('FAILED:PCM_OVERFLOW')
    pcm = scaled.astype('<i2')
    target = io.BytesIO()
    with wave.open(target, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm.tobytes())
    return target.getvalue()


def compute_pair() -> tuple[dict, dict[str, bytes]]:
    u = source()
    pa, da = render_pressure(u, C_AREAS_M2[0])
    pb, db = render_pressure(u, C_AREAS_M2[1])
    relative_difference = float(np.sqrt(np.mean((pa-pb)**2)) /
                                max(np.sqrt(np.mean(pa**2)), 1e-30))
    if relative_difference <= 1e-3:
        raise AssertionError('NUMERICALLY_UNRESOLVED:NO_CAUSAL_DIFFERENCE')
    gain = 0.8 / max(float(np.max(np.abs(pa))), float(np.max(np.abs(pb))))
    files: dict[str, bytes] = {'raw_U_m3_s.npy': array_npy_bytes(u)}
    records = []
    for label, pressure, diag in (('small_C', pa, da), ('large_C', pb, db)):
        pressure_path = f'{label}/raw_p_Ain_Pa.npy'
        wav_path = f'{label}/monitor_48k_pcm16.wav'
        files[pressure_path] = array_npy_bytes(pressure)
        files[wav_path] = pcm_wav_bytes(pressure, gain)
        records.append({'label':label, 'pressure_path':pressure_path, 'wav_path':wav_path,
                        'raw_pressure_sha256':sha256(files[pressure_path]),
                        'wav_sha256':sha256(files[wav_path]), 'diagnostic':diag})
    manifest = {
        'schema': 'og-aud1.monitor.experiment.v0', 'status': STATUS,
        'physical_claim': 'PRESCRIBED_SOURCE_PORT_PRESSURE_BANDLIMITED_NOT_RADIATED',
        'forbidden_claims': ['natural speech','mouth radiation','calibrated SPL','adopted Core OG-4 broadband API'],
        'source_kind': 'prescribed_volume_flow', 'source_plane': 'A.in',
        'monitor_plane': 'A.in', 'source_unit':'m3/s', 'pressure_unit':'Pa',
        'sample_rate_hz':SAMPLE_RATE, 'frames':N_SAMPLES, 'nfft':NFFT,
        'band_hz':[0,4000], 'length_A_m':L_A, 'area_A_m2':AREA_A,
        'length_B_m':L_B, 'area_B_m2':AREA_B, 'length_C_m':L_C,
        'rho_kg_m3':RHO, 'c_m_s':SOUND_SPEED,
        'junction_law':'ideal.branch3.p_u', 'terminations':['matched','matched'],
        'source_sha256':sha256(files['raw_U_m3_s.npy']),
        'source_tones_hz':list(FREQUENCIES), 'source_weights':list(WEIGHTS),
        'source_phases_rad':list(PHASES),
        'pair_playback_gain_inverse_pa':gain,
        'relative_raw_pressure_rms_difference':relative_difference,
        'fft_policy':'exact analytic Zin evaluated at every <=4000Hz RFFT bin, >4000Hz zero; zero-padded spectral projection with possible acausal pre-ringing',
        'playback_normalization':'common pair peak 0.8, PCM16 rint',
        'experiment_gate':'EXPLORATORY_UNREVIEWED',
        'code_identity':'experiment/044_og_aud1_monitor/monitor.py',
        'records':records,
    }
    return manifest, files


def run(output_dir: Path) -> dict:
    manifest, files = compute_pair()
    # Stage to a temp sibling and atomically publish a new, nonexisting directory.
    if output_dir.exists():
        raise FileExistsError(f'IMMUTABILITY:OUTPUT_ALREADY_EXISTS:{output_dir}')
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.og-aud1-stage-', dir=output_dir.parent) as tmp:
        root = Path(tmp)
        for relative, data in files.items():
            path = root/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if sha256(path.read_bytes()) != sha256(data):
                raise OSError('FAILED:READBACK_MISMATCH')
        # Receipt saved last. Scope includes all archived byte hashes.
        manifest['artifact_sha256'] = {rel:sha256(data) for rel,data in sorted(files.items())}
        receipt = json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False).encode('utf-8') + b'\n'
        (root/'manifest.json').write_bytes(receipt)
        root.rename(output_dir)
    return manifest


if __name__ == '__main__':
    dest = Path(sys.argv[1] if len(sys.argv)>1 else 'og_aud1_out')
    print(json.dumps(run(dest),ensure_ascii=False,indent=2))
