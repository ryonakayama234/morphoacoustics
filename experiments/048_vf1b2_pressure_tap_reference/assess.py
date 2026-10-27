"""Gate-0 published pressure-tap reference qualification; no modeled pressures or sound.

This is a research-local evidence assessor, NOT validation of an aerodynamic
closure and NOT a new Core organ-graph / public performance API.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

CATALOG = {
    "m5_uniform_2011": ("10.1121/1.3514424", "axial"),
    "m6_nonrectangular_2010": ("10.1121/1.3455838", "transverse"),
    "m5_hemilarynx_2008": ("10.1016/j.jvoice.2008.02.005", "axial"),
}
FLAGS = (
    "tap_coordinate_map_audited",
    "reference_and_sign_audited",
    "geometry_and_boundary_matched_to_candidate",
    "uncertainty_and_digitization_audited",
)
SOURCE = Path(__file__).with_name("sources.json")


import hashlib

INVENTORY_GIT_BLOB_SHA = "1c1751a11430386497789f9955a7e64e733550bc"  # exact audited source catalog version


def read_inventory(content: bytes | None = None) -> dict:
    raw = SOURCE.read_bytes() if content is None else content
    blob = b"blob " + str(len(raw)).encode("ascii") + b"\\0" + raw
    if hashlib.sha1(blob).hexdigest() != INVENTORY_GIT_BLOB_SHA:
        raise ValueError("published-source inventory tampered / unreviewed change")
    return json.loads(raw.decode("utf-8", errors="strict"))

def _check_samples(samples: object) -> None:
    if not isinstance(samples, list):
        raise ValueError("measured_pressure_samples must be a list")
    positions: set[tuple[str, float]] = set()
    for sample in samples:
        if not isinstance(sample, dict):
            raise ValueError("sample must be an object")
        if set(sample) != {"tap_id", "position_m", "pressure_pa",
                           "uncertainty_pa", "wall_side", "original_source_ref"}:
            raise ValueError("each pressure datum requires source, side, SI coordinates and uncertainty")
        if any(not isinstance(sample[k], str) or not sample[k].strip()
               for k in ("tap_id", "wall_side", "original_source_ref")):
            raise ValueError("unattributed measured pressure")
        for k in ("position_m", "pressure_pa", "uncertainty_pa"):
            v = sample[k]
            if type(v) not in (int, float) or not math.isfinite(v):
                raise ValueError("pressure datum must be finite SI number")
        if sample["position_m"] < 0 or sample["uncertainty_pa"] <= 0:
            raise ValueError("invalid coordinate or uncertainty bound")
        key = (sample["wall_side"] + ":" + sample["tap_id"], sample["position_m"])
        if key in positions:
            raise ValueError("duplicate measured tap on same wall")
        positions.add(key)


def assess_source(source: dict) -> dict:
    """Audit declared evidence; never return 'pressure model validated'."""
    if not isinstance(source, dict):
        raise ValueError("source must be object")
    key = source.get("id")
    if key not in CATALOG:
        raise ValueError("unrecognized pressure reference")
    doi, axis = CATALOG[key]
    if source.get("doi") != doi or source.get("tap_axis") != axis:
        raise ValueError("DOI or tap-axis geometry identity mismatch")
    if not isinstance(source.get("citation"), str) or not source["citation"].strip():
        raise ValueError("citation required")
    if not isinstance(source.get("tap_layout"), str) or not source["tap_layout"].strip():
        raise ValueError("tap layout provenance required")
    for flag in FLAGS:
        if type(source.get(flag)) is not bool:
            raise ValueError("source evidence flags must be explicit booleans")
    samples = source.get("measured_pressure_samples")
    _check_samples(samples)
    if not samples:
        status = "HOLD_NO_NUMERIC_MEASURED_PRESSURE_PROFILE"
    elif len(samples) < 3:
        status = "HOLD_INSUFFICIENT_TAP_PROFILE"
    elif not all(source[f] for f in FLAGS):
        status = "HOLD_UNQUALIFIED_COORDINATE_BOUNDARY_OR_UNCERTAINTY"
    else:
        # Structural eligibility only. The declaration must still be
        # independently checked against the article before use in model tests.
        status = "CANDIDATE_READY_FOR_INDEPENDENT_SOURCE_AUDIT"
    return {"id": key, "doi": doi, "tap_axis": axis,
            "sample_count": len(samples), "gate0_status": status,
            "g2": "INDETERMINATE_NO_INDEPENDENT_PRESSURE_MODEL_COMPARISON",
            "g3": "NOT_APPLICABLE_NO_MOVING_WALL",
            "g4": "VOICE_NO_GO"}


def assess_inventory(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema") != "vf1b2-pressure-atlas/gate0-inventory-v1":
        raise ValueError("wrong inventory version")
    refs = data.get("sources")
    if not isinstance(refs, list) or len(refs) != len(CATALOG):
        raise ValueError("incomplete source inventory")
    if {row.get("id") for row in refs if isinstance(row, dict)} != set(CATALOG):
        raise ValueError("missing/duplicated/unknown pressure source")
    results = [assess_source(row) for row in refs]
    return {"results": results, "gate0": "SOURCE_INVENTORY_ONLY",
            "g2": "INDETERMINATE_NO_INDEPENDENT_PRESSURE_MODEL_COMPARISON",
            "g3": "NOT_APPLICABLE_NO_MOVING_WALL", "g4": "VOICE_NO_GO"}


def main() -> None:
    inventory = read_inventory()
    print(json.dumps(assess_inventory(inventory), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
