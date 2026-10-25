"""WG2: bounded physical mouth pressure preview; not a microphone or TTS."""
from __future__ import annotations

from hashlib import sha256
import io
from math import ceil
import wave

import numpy as np
import pytest

from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics_waveguide import PassiveWaveguideConfig
from morphoacoustics_waveguide.observations import (
    MONITOR_VERSION, SAMPLE_RATE_HZ, _causal_48k_monitor,
    render_mouth_port_monitor,
)


def geometry(length_m: float = 0.01) -> Tract1DGeometry:
    return Tract1DGeometry(
        "oral",
        tuple(TubeSection(length_m, 0.0008) for _ in range(16)),
    )


def test_silence_is_exact_and_wav_is_new_mono_pcm16() -> None:
    cfg = PassiveWaveguideConfig(geometry(), termination="b0")
    take = render_mouth_port_monitor(cfg, np.zeros(960))
    assert take.physics_ticks == ceil(960 * cfg.physics_clock_hz / SAMPLE_RATE_HZ)
    assert take.output_samples == 960
    assert take.observation_version == MONITOR_VERSION
    assert not any(take.mouth_pressure_physics_pa)
    assert not any(take.mouth_flow_physics_m3_s)
    assert not any(take.mouth_port_pressure_monitor_pa)
    assert take.summed_source_work_j == 0.0
    assert take.summed_outlet_dissipation_j == 0.0
    assert take.max_abs_energy_residual_j == 0.0
    assert take.wav_sha256 == sha256(take.wav_pcm16_mono_48k).hexdigest()
    with wave.open(io.BytesIO(take.wav_pcm16_mono_48k), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == 48_000
        assert wav.getnframes() == 960
        assert wav.readframes(960) == bytes(1920)


def test_first_arrival_and_causal_monitor_preserve_anatomical_length() -> None:
    results = []
    # Pulse is causal and length-dependent, not an FFT response re-render.
    source = np.zeros(480, dtype=np.float64)
    source[0] = 1e-7
    for length in (0.01, 0.011):
        cfg = PassiveWaveguideConfig(geometry(length), termination="matched")
        take = render_mouth_port_monitor(cfg, source)
        physics = np.array(take.mouth_pressure_physics_pa)
        first_native = int(np.flatnonzero(physics)[0])
        assert first_native >= 32
        first_time = (first_native + 1) / cfg.physics_clock_hz
        assert first_time >= cfg.geometry.total_length_m / cfg.sound_speed_m_s
        monitor = np.asarray(take.mouth_port_pressure_monitor_pa)
        nonzero = np.flatnonzero(monitor)
        assert nonzero.size > 0
        observed_first_time = (int(nonzero[0]) + 0.5) / SAMPLE_RATE_HZ
        assert observed_first_time >= first_time
        assert take.filter_group_latency_s > 0
        assert take.max_abs_energy_residual_j < 1e-14
        results.append((first_native, first_time, cfg.physics_clock_hz))
    assert results[0][0] == results[1][0]
    assert results[0][2] / results[1][2] == pytest.approx(1.1, rel=1e-12)
    assert results[1][1] / results[0][1] == pytest.approx(1.1, rel=1e-12)


def test_physical_take_is_reproducible_with_fixed_playback_scale() -> None:
    cfg = PassiveWaveguideConfig(geometry(), termination="b0")
    time = np.arange(960) / SAMPLE_RATE_HZ
    source = 1e-7 * np.sin(2 * np.pi * 100.0 * time)
    first = render_mouth_port_monitor(cfg, source)
    again = render_mouth_port_monitor(cfg, source)
    assert first == again
    assert max(map(abs, first.mouth_port_pressure_monitor_pa)) > 0
    assert first.provenance()["source_role"] == "externally-prescribed-piecewise-linear-volume-flow"
    assert first.provenance()["observation_point"] == "mouth-port-pressure-not-external-microphone"
    assert first.summed_source_work_j >= 0
    assert first.final_stored_energy_j >= 0
    assert abs(first.final_stored_energy_j - (
        first.summed_source_work_j - first.summed_outlet_dissipation_j
    )) < 1e-14


def test_causal_filter_low_frequency_pass_and_reject_aliased_tone() -> None:
    hz = 68_600.0
    count_native = 20_000
    native_times = (np.arange(count_native) + 1) / hz
    out_count = 10_000
    low = _causal_48k_monitor(
        np.sin(2 * np.pi * 1000 * native_times), hz, out_count,
    )
    high = _causal_48k_monitor(
        np.sin(2 * np.pi * 27_000 * native_times), hz, out_count,
    )
    # Ignore FIR startup. Attenuation should be significant above 24k Nyquist.
    rms_low = float(np.sqrt(np.mean(low[2000:] ** 2)))
    rms_high = float(np.sqrt(np.mean(high[2000:] ** 2)))
    assert 0.60 < rms_low < 0.79
    assert rms_high < rms_low * 0.05
    pulse = np.zeros(2000, dtype=np.float64)
    pulse[500] = 1.0
    out = _causal_48k_monitor(pulse, hz, 1200)
    # Causal filtering cannot emit before physical pulse; excludes zero-phase ringing.
    out_times = (np.arange(1200) + 0.5) / SAMPLE_RATE_HZ
    assert np.all(out[out_times < (501 / hz)] == 0)


@pytest.mark.parametrize("scale", [0.0, float("nan"), float("inf"), True])
def test_reject_bad_playback_scale(scale: float) -> None:
    with pytest.raises(ValueError, match="full-scale"):
        render_mouth_port_monitor(
            PassiveWaveguideConfig(geometry()), np.zeros(120),
            playback_full_scale_pa=scale,
        )


def test_reject_source_errors_and_clipping() -> None:
    cfg = PassiveWaveguideConfig(geometry())
    for source in (
        [],
        [float("nan"), 0.0],
        [float("inf"), 0.0],
        [True, False],
    ):
        with pytest.raises(ValueError):
            render_mouth_port_monitor(cfg, source)
    driven = np.zeros(480)
    driven[0] = 1e-4
    with pytest.raises(ValueError, match="clipping"):
        render_mouth_port_monitor(cfg, driven, playback_full_scale_pa=1e-8)


def test_no_implicit_physical_clock_rounding() -> None:
    source = np.zeros(240)
    for length in (0.01, 0.011):
        cfg = PassiveWaveguideConfig(geometry(length), cells_per_section=2)
        t = render_mouth_port_monitor(cfg, source)
        assert t.physics_clock_hz == pytest.approx(343 * 2 / length)
        assert t.physics_ticks == ceil(240 * t.physics_clock_hz / SAMPLE_RATE_HZ)
        assert t.output_samples == 240
