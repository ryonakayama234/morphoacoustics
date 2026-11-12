"""Direct trigonometric pressure reconstruction (reviewer-owned, FZ-V1).

Rebuilds the band-limited waveform from the oracle Hp values and the
source DFT bins by an explicit sine/cosine sum. No FFT is used anywhere
in this module: p[n] = (2/N) * sum over the 351 registered bins of
Re( P[k] * exp(2 pi i k n / N) ), P[k] = Hp(f_k) * Q[k], which is the
registered observation projection (all other bins are zero by
definition; DC and Nyquist carry no registered bin).
"""
from __future__ import annotations

import numpy as np

SAMPLE_RATE = 48000
SAMPLES = 24000
FREQUENCIES_HZ = tuple(range(100, 801, 2))


def direct_pressure(source_dft: np.ndarray, hp_oracle: np.ndarray,
                    sample_indices: np.ndarray | None = None) -> np.ndarray:
    """Waveform at the requested samples (default: all 24,000).

    ``source_dft`` is the rfft of the consumed source buffer (a shared,
    content-addressed fixture input); ``hp_oracle`` holds the reviewer's
    complex Hp at the 351 registered frequencies.
    """
    q = np.asarray(source_dft, dtype=np.complex128)
    hp = np.asarray(hp_oracle, dtype=np.complex128)
    assert q.shape == (SAMPLES // 2 + 1,) and hp.shape == (len(FREQUENCIES_HZ),)
    bins = np.array([f * SAMPLES // SAMPLE_RATE for f in FREQUENCIES_HZ])
    spectrum = hp * q[bins]
    if sample_indices is None:
        sample_indices = np.arange(SAMPLES)
    n = np.asarray(sample_indices, dtype=np.float64)
    # explicit direct sum: angles[k, j] = 2 pi * bin_k * n_j / N
    angles = 2.0 * np.pi * np.outer(bins, n) / SAMPLES
    basis = np.exp(1j * angles)
    return (2.0 / SAMPLES) * np.real(spectrum @ basis)
