"""Read-only LF source via audited existing Core experiment chain."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import runpy
import numpy as np
from .prereg_binding import SAMPLE_RATE, SAMPLES, require

ROOT = Path(__file__).resolve().parents[2]


def consumed_source() -> dict:
    # Re-use OD-2 transitive-source inventory, not new LF generation logic.
    authority = runpy.run_path(str(ROOT / "tools" / "od2_body_cli.py"))
    _, exp, parent, _ = authority["_load_context"]()
    del parent
    sources, _ = exp.EXP26.EXP13.build_sources()
    src = np.ascontiguousarray(sources["lf_fixed"].source, dtype="<f8")
    require(src.shape == (SAMPLES,) and
            int(exp.EXP26.EXP13.SAMPLE_RATE_HZ) == SAMPLE_RATE and
            math.isclose(float(exp.EXP26.EXP13.BASE_F0_HZ), 100.0) and
            bool(np.all(np.isfinite(src))),
            "SOURCE_NOT_ATTESTED", "audited LF generator/source drift")
    raw = src.tobytes(order="C")
    q = np.fft.rfft(src)
    require(q.shape == (SAMPLES // 2 + 1,) and bool(np.all(np.isfinite(q))),
            "SOURCE_NOT_ATTESTED", "LF source DFT invalid")
    return {"buffer": src, "Q": q,
            "source_sha256_le_f64": hashlib.sha256(raw).hexdigest(),
            "dft_sha256_le_complex128": hashlib.sha256(
                np.ascontiguousarray(q, dtype="<c16").tobytes()).hexdigest(),
            "generator": "experiments/013_parametric_source_prosody/run.py::build_sources/lf_fixed",
            "source_status": "RECOMPUTED_PENDING_IN_RUN_CHAIN_ATTESTATION",
            "transitive_pins": dict(authority["PINS"])}
