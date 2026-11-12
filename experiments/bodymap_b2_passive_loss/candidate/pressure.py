"""FZ-O1 351-bin observation projection; native little-endian f64 Pa, no preview."""
from __future__ import annotations

import hashlib
import numpy as np
from ..prereg_binding import SAMPLE_RATE, SAMPLES, FREQUENCIES_HZ, require


def projected_pressure(source_f64: np.ndarray, hp: np.ndarray) -> dict:
    source = np.ascontiguousarray(source_f64, dtype="<f8")
    transfer = np.asarray(hp, dtype=np.complex128)
    require(source.shape == (SAMPLES,) and transfer.shape == (len(FREQUENCIES_HZ),)
            and bool(np.all(np.isfinite(source))) and bool(np.all(np.isfinite(transfer))),
            "ARTIFACT_MISMATCH", "source or Hp is not valid f64/full-grid")
    q = np.fft.rfft(source)
    p = np.zeros_like(q)
    for i, f in enumerate(FREQUENCIES_HZ):
        require(f * SAMPLES % SAMPLE_RATE == 0, "PHYSICAL_IDENTITY_MISMATCH",
                "frequency does not land on exact DFT bin")
        p[f * SAMPLES // SAMPLE_RATE] = transfer[i] * q[f * SAMPLES // SAMPLE_RATE]
    raw = np.ascontiguousarray(np.fft.irfft(p, n=SAMPLES), dtype="<f8")
    require(bool(np.all(np.isfinite(raw))) and float(np.linalg.norm(raw)) > 0,
            "NUMERICALLY_UNRESOLVED", "nonfinite or zero band pressure")
    return {"pressure_pa": raw, "P": p, "Q": q,
            "raw_sha256_le_f64": hashlib.sha256(raw.tobytes()).hexdigest(),
            "source_sha256_le_f64": hashlib.sha256(source.tobytes()).hexdigest(),
            "pressure_generation_method": "b2.direct-observables/1:100:2:800Hz-rfft-irfft-1/N",
            "observation_plane_ref": "0.20m-monopole-pressure-proxy-uncalibrated"}
