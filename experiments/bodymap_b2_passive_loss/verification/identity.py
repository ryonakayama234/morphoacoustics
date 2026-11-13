"""Frozen law, source and geometry identity gates, distinct from file hashes alone."""
from __future__ import annotations

import hashlib
import math
import numpy as np
from ..prereg_binding import (FREQUENCIES_HZ, LAW, RHO, C, R_PROXY_M,
                              M0_DIGEST, Refusal, require)
from ..geometry_binding import resolve_geometry


def geometry_claim(case: str, radii: tuple[float, ...], lengths: tuple[float, ...],
                   digest: str | None) -> None:
    fresh = resolve_geometry(case)
    require(tuple(radii) == tuple(fresh["radii_m"])
            and tuple(lengths) == tuple(fresh["lengths_m"])
            and digest == fresh["preparation_digest"],
            "PHYSICAL_IDENTITY_MISMATCH", "geometry identity / port ordering drift")


def source_claim(consumed: np.ndarray, claimed_sha256: str, authoritative: dict) -> None:
    actual = np.ascontiguousarray(consumed, dtype="<f8")
    raw = actual.tobytes()
    require(claimed_sha256 == hashlib.sha256(raw).hexdigest()
            and raw == authoritative["buffer"].tobytes(),
            "ARTIFACT_MISMATCH", "self-consistent forged SHA is not trusted source")


def model_claim(meta: dict, geometry: dict) -> None:
    require(meta.get("law") == LAW and meta.get("phasor") == "exp(+jwt)"
            and meta.get("volume_velocity") == "m3/s_inlet_to_outlet"
            and meta.get("attenuation_np_m") == 0
            and meta.get("band_hz") == [100, 800, 2]
            and meta.get("proxy_m") == R_PROXY_M and
            meta.get("rho") == RHO and meta.get("c") == C,
            "PHYSICAL_IDENTITY_MISMATCH", "unregistered law/units/port/plane")
    expected_r = .05 * RHO * C / (math.pi * geometry["radii_m"][-1]**2)
    require(math.isclose(meta.get("load_R", math.nan), expected_r, rel_tol=1e-14),
            "LOAD_MISMATCH", "swapped/undeclared termination")


def raw_claim(raw: np.ndarray, claimed_sha256: str, reconstructed: np.ndarray) -> None:
    data = np.ascontiguousarray(raw, dtype="<f8")
    require(hashlib.sha256(data.tobytes()).hexdigest() == claimed_sha256,
            "ARTIFACT_MISMATCH", "raw SHA not equal to bytes")
    require(data.shape == reconstructed.shape and
            float(np.linalg.norm(data-reconstructed)) /
            max(float(np.linalg.norm(reconstructed)), 1e-300) <= 1e-8,
            "WAVEFORM_ORACLE_MISMATCH", "raw must be rederived from trusted chain")
