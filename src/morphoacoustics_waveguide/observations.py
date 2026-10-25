"""CORE-WG-2: causal 48 kHz *mouth-port* pressure monitor, not a microphone.

A prescribed sampled volume-flow source drives the verified static passive
waveguide at its anatomy-derived clock. The 48 kHz playback representation
uses only a causal anti-alias FIR and past-sample readout. No phonation physics,
arbitrary timbral EQ, post-WAV pitch/gain manipulation or Studio contract here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import io
from math import ceil, isfinite
from typing import Sequence
import wave

import numpy as np

from .passive_waveguide import PassiveWaveguideConfig, PassiveWaveguideSession

SAMPLE_RATE_HZ = 48_000
FIR_TAPS = 129
FIR_CUTOFF_HZ = 19_200.0
FIR_KAISER_BETA = 8.6
MAX_DURATION_S = 0.5
MONITOR_VERSION = "wg2-mouth-port-causal-kaiser129/v1"


@dataclass(frozen=True, slots=True)
class MouthPortMonitorTake:
    """Immutable scalar metadata and sample tuples; audio is a listening monitor."""

    physics_clock_hz: float
    physics_ticks: int
    output_samples: int
    source_flow_sha256: str
    physical_pressure_sha256: str
    monitor_pressure_sha256: str
    wav_sha256: str
    mouth_pressure_physics_pa: tuple[float, ...]
    mouth_flow_physics_m3_s: tuple[float, ...]
    mouth_port_pressure_monitor_pa: tuple[float, ...]
    wav_pcm16_mono_48k: bytes
    max_abs_energy_residual_j: float
    summed_source_work_j: float
    summed_outlet_dissipation_j: float
    final_stored_energy_j: float
    playback_full_scale_pa: float
    filter_group_latency_s: float
    termination: str
    observation_version: str = MONITOR_VERSION

    def provenance(self) -> dict[str, float | int | str]:
        return {
            "observation_version": self.observation_version,
            "observation_point": "mouth-port-pressure-not-external-microphone",
            "source_role": "externally-prescribed-piecewise-linear-volume-flow",
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "physics_clock_hz": self.physics_clock_hz,
            "physics_ticks": self.physics_ticks,
            "output_samples": self.output_samples,
            "termination": self.termination,
            "fir_taps": FIR_TAPS,
            "fir_cutoff_hz": FIR_CUTOFF_HZ,
            "fir_kaiser_beta": FIR_KAISER_BETA,
            "filter_group_latency_s": self.filter_group_latency_s,
            "playback_full_scale_pa": self.playback_full_scale_pa,
            "source_flow_sha256": self.source_flow_sha256,
            "physical_pressure_sha256": self.physical_pressure_sha256,
            "monitor_pressure_sha256": self.monitor_pressure_sha256,
            "wav_sha256": self.wav_sha256,
            "max_abs_energy_residual_j": self.max_abs_energy_residual_j,
            "summed_source_work_j": self.summed_source_work_j,
            "summed_outlet_dissipation_j": self.summed_outlet_dissipation_j,
            "final_stored_energy_j": self.final_stored_energy_j,
        }


def _causal_48k_monitor(native_pa: np.ndarray, clock_hz: float, count: int) -> np.ndarray:
    """Causal antialias before downsampling, with no future-sample interpolation.

    FIR design uses windowed sinc with unity DC gain. The physically computed
    pressure first enters the filter when it exists; padding is historical
    zero, not a symmetric noncausal zero-phase filter. Reading at 48k uses the
    most recent fully available filtered physical tick (ZOH), avoiding the
    usual half-tick early lookahead of `np.interp`.
    """
    if not isfinite(clock_hz) or clock_hz <= SAMPLE_RATE_HZ:
        raise ValueError("WG2 monitor requires physical clock strictly above 48 kHz")
    if native_pa.ndim != 1 or not np.isfinite(native_pa).all():
        raise ValueError("nonfinite/invalid physical pressure")
    if type(count) is not int or count <= 0:
        raise ValueError("invalid 48k observation sample count")
    t = np.arange(FIR_TAPS, dtype=np.float64) - (FIR_TAPS - 1) / 2
    normalized_cutoff = FIR_CUTOFF_HZ / clock_hz
    kernel = (2.0 * normalized_cutoff * np.sinc(2.0 * normalized_cutoff * t)
              * np.kaiser(FIR_TAPS, FIR_KAISER_BETA))
    kernel /= np.sum(kernel)
    filtered = np.convolve(native_pa, kernel, mode="full")[:len(native_pa)]
    # k-th native pressure corresponds to the END of physics tick (k+1)/fs.
    out_times = (np.arange(count, dtype=np.float64) + 0.5) / SAMPLE_RATE_HZ
    indices = np.floor(out_times * clock_hz).astype(np.int64) - 1
    monitor = np.zeros(count, dtype=np.float64)
    valid = (indices >= 0) & (indices < len(filtered))
    monitor[valid] = filtered[indices[valid]]
    if not np.isfinite(monitor).all():
        raise FloatingPointError("nonfinite antialiased pressure monitor")
    return monitor


def _wav_pcm16(samples_pa: np.ndarray, full_scale_pa: float) -> bytes:
    if isinstance(full_scale_pa, bool) or not isfinite(full_scale_pa) or full_scale_pa <= 0:
        raise ValueError("playback full-scale pressure must be finite and positive")
    if not np.isfinite(samples_pa).all():
        raise ValueError("nonfinite playback pressure")
    if np.any(np.abs(samples_pa) > full_scale_pa):
        raise ValueError("monitor pressure exceeds fixed playback full scale; refusing clipping")
    pcm = np.rint(samples_pa / full_scale_pa * 32767.0).astype("<i2")
    out = io.BytesIO()
    with wave.open(out, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE_HZ)
        audio.writeframes(pcm.tobytes())
    return out.getvalue()


def _digest64(values: np.ndarray) -> str:
    return sha256(np.ascontiguousarray(values, dtype="<f8").tobytes()).hexdigest()


def render_mouth_port_monitor(
    config: PassiveWaveguideConfig,
    prescribed_flow_48k_m3_s: Sequence[float] | np.ndarray,
    *,
    playback_full_scale_pa: float = 8.0,
) -> MouthPortMonitorTake:
    """One fresh prescribed-flow physical run, no WAV reuse or silent fallback.

    The input values are 48 kHz *samples of a prescribed motor/source command*.
    We explicitly define the input between samples by piecewise-linear flow;
    native physical ticks never quantize the anatomy clock to 48 kHz.
    Each invocation creates one state-contiguous acoustic session.
    """
    raw_input = np.asarray(prescribed_flow_48k_m3_s)
    if raw_input.dtype.kind == "b" or raw_input.ndim != 1:
        raise ValueError("source must be a one-dimensional numeric flow sequence")
    if not 2 <= raw_input.size <= round(MAX_DURATION_S * SAMPLE_RATE_HZ):
        raise ValueError("WG2 first pilot supports at least two and at most 0.5s of source samples")
    source = np.asarray(raw_input, dtype=np.float64)
    if not np.isfinite(source).all():
        raise ValueError("nonfinite prescribed source flow")
    if isinstance(playback_full_scale_pa, bool) or not isfinite(playback_full_scale_pa) or playback_full_scale_pa <= 0:
        raise ValueError("invalid playback full-scale pressure")
    physics_hz = config.physics_clock_hz
    if not isfinite(physics_hz) or physics_hz <= SAMPLE_RATE_HZ:
        raise ValueError("unsupported native physics clock for WG2 48k monitor")
    duration_s = len(source) / SAMPLE_RATE_HZ
    count = int(ceil(duration_s * physics_hz))
    if count <= 0 or count > 1_000_000:
        raise ValueError("unsupported physical tick count")
    session = PassiveWaveguideSession(config)
    native_pressure = np.empty(count, dtype=np.float64)
    native_flow = np.empty(count, dtype=np.float64)
    source_times = np.arange(len(source) + 1, dtype=np.float64) / SAMPLE_RATE_HZ
    source_values = np.concatenate((source, np.zeros(1, dtype=np.float64)))
    max_residual = 0.0
    work = 0.0
    loss = 0.0
    for k in range(count):
        t_s = (k + 0.5) / physics_hz
        u = float(np.interp(t_s, source_times, source_values, left=0.0, right=0.0))
        result = session.step(u)
        native_pressure[k] = result.mouth_pressure_pa
        native_flow[k] = result.mouth_flow_m3_s
        max_residual = max(max_residual, abs(result.energy_residual_j))
        work += result.source_work_j
        loss += result.outlet_dissipation_j
    final_energy = sum(session.energies_j())
    if abs(final_energy - (work - loss)) > max(
        1e-10 * max(abs(work), abs(loss), abs(final_energy), 1e-20), 1e-18
    ):
        raise FloatingPointError("physical source/duct/radiation energy ledger failed")
    observed = _causal_48k_monitor(native_pressure, physics_hz, len(source))
    wav = _wav_pcm16(observed, playback_full_scale_pa)
    return MouthPortMonitorTake(
        physics_clock_hz=physics_hz,
        physics_ticks=count,
        output_samples=len(source),
        source_flow_sha256=_digest64(source),
        physical_pressure_sha256=_digest64(native_pressure),
        monitor_pressure_sha256=_digest64(observed),
        wav_sha256=sha256(wav).hexdigest(),
        mouth_pressure_physics_pa=tuple(map(float, native_pressure)),
        mouth_flow_physics_m3_s=tuple(map(float, native_flow)),
        mouth_port_pressure_monitor_pa=tuple(map(float, observed)),
        wav_pcm16_mono_48k=wav,
        max_abs_energy_residual_j=max_residual,
        summed_source_work_j=work,
        summed_outlet_dissipation_j=loss,
        final_stored_energy_j=final_energy,
        playback_full_scale_pa=float(playback_full_scale_pa),
        filter_group_latency_s=((FIR_TAPS - 1) / 2) / physics_hz,
        termination=config.termination,
    )
