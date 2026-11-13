"""M0 from audited Core OD-2 authority; never issue or duplicate a BodyRevision."""
from __future__ import annotations

import math
from pathlib import Path
import runpy
from .prereg_binding import M0_DIAMETERS_MM, M0_DIGEST, Refusal, require, validate_envelope

ROOT = Path(__file__).resolve().parents[2]


def trusted_m0() -> dict:
    # OD-2 checks frozen Git blobs and loads the audited original Core body.
    authority = runpy.run_path(str(ROOT / "tools" / "od2_body_cli.py"))
    runner, exp, parent, _ = authority["_load_context"]()
    del runner, exp
    rest = parent.prepared.rest_state
    require(parent.preset_id == "v3b-axial-M0" and parent.revision == 1
            and parent.preparation_digest == M0_DIGEST,
            "PHYSICAL_IDENTITY_MISMATCH", "untrusted M0 Core rest identity")
    sections = tuple(rest.sections)
    radii = tuple(math.sqrt(s.area_m2 / math.pi) for s in sections)
    lengths = tuple(float(s.length_m) for s in sections)
    require(len(sections) == 16 and
            all(abs(2 * r * 1000 - d) <= 1e-8 for r, d in zip(radii, M0_DIAMETERS_MM, strict=True)),
            "PHYSICAL_IDENTITY_MISMATCH", "trusted 16-cell readback differs from prereg")
    validate_envelope(radii, lengths)
    return {"case": "M0_REST", "radii_m": radii, "lengths_m": lengths,
            "preparation_digest": parent.preparation_digest,
            "revision_id": "v3b-axial-M0@1",
            "source_pin_inventory": dict(authority["PINS"]),
            "core_authority": "tools/od2_body_cli.py::_load_context"}


def mathematical_ref(name: str) -> dict:
    require(name in ("U6_REF", "U19_REF"),
            "PHYSICAL_IDENTITY_MISMATCH", "unknown mathematical reference")
    r = .006 if name == "U6_REF" else .019
    radii, lengths = (r,) * 16, (.010,) * 16
    validate_envelope(radii, lengths)
    return {"case": name, "radii_m": radii, "lengths_m": lengths,
            "preparation_digest": None, "revision_id": None,
            "core_authority": "mathematical_reference_not_body_revision"}


def resolve_geometry(name: str) -> dict:
    if name == "M0_REST":
        return trusted_m0()
    return mathematical_ref(name)
