"""M5 Figure 2B two-reader source metrology: research-only, fail-closed.

Does NOT authenticate that uploaded image actually comes from the publication.
No source-qualified pressure values, tissue force, FSI, or voice are produced.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

CASE_ID = "M5_UNIFORM_FIG2B_D002CM_DP10CMH2O"
DOI = "10.1121/1.3514424"
KNOWN_Z_M = {6: 0.00211, 11: 0.00413, 13: 0.00511}
REQUIRED_FW = set(range(6, 14))
CMH2O_TO_PA = 98.0665
ALLOWED_SIDES = {"FW", "NFW", "AMBIGUOUS"}
S0 = "S0_SOURCE_UNQUALIFIED"
PARTIAL = "S1_PARTIAL_CANDIDATE_FOR_EXTERNAL_AUDIT"
COMPLETE = "S1_COMPLETE_CANDIDATE_FOR_EXTERNAL_AUDIT"


class SourceHold(ValueError):
    """Invalid or unqualified source information; no numeric observation."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SourceHold(message)


def real(value: object, label: str, *, nonnegative: bool = False) -> float:
    require(type(value) in (int, float), f"{label}: real finite numeric required")
    require(math.isfinite(value), f"{label}: nonfinite")
    require(not nonnegative or value >= 0, f"{label}: negative")
    return float(value)


def exact_fields(item: object, keys: set[str], label: str) -> dict:
    require(isinstance(item, dict), f"{label}: object expected")
    require(set(item) == keys, f"{label}: missing/extra fields {sorted(set(item) ^ keys)}")
    return item


def case_check(case: object) -> None:
    c = exact_fields(case, {"id", "doi", "figure", "d_life_m", "dp_life_cmH2O",
                            "scale", "reference_tap", "drop_sign"}, "case")
    require(c["id"] == CASE_ID and c["doi"] == DOI and c["figure"] == "2B",
            "DOI, panel or primary case mismatch")
    require(real(c["d_life_m"], "d") == .0002, "wrong d")
    require(real(c["dp_life_cmH2O"], "drive") == 10, "wrong pressure condition")
    require(real(c["scale"], "rig scale") == 7.5, "wrong rig scale")
    require(c["reference_tap"] == 0 and type(c["reference_tap"]) is int,
            "tracheal tap0 required")
    require(c["drop_sign"] == "p0_minus_pi", "pressure drop sign reversed")


def axis_interval(axis: object, pixel: object, marker_radius: object, unit: str) -> tuple[float, float]:
    a = exact_fields(axis, {"unit", "tick1_pixel", "tick1_value", "tick2_pixel",
                            "tick2_value", "tick_radius_pixel"}, "axis")
    require(a["unit"] == unit, "wrong axis unit or rig/life scale (source axes must be inspected)")
    t1 = real(a["tick1_pixel"], "tick1")
    t2 = real(a["tick2_pixel"], "tick2")
    v1 = real(a["tick1_value"], "tick1 value")
    v2 = real(a["tick2_value"], "tick2 value")
    r = real(a["tick_radius_pixel"], "tick radius", nonnegative=True)
    px = real(pixel, "marker pixel")
    mr = real(marker_radius, "marker radius", nonnegative=True)
    require(t1 != t2 and v1 != v2, "degenerate axis calibration")
    require(abs(t2-t1) > 2*r, "axis tick uncertainty overlaps")
    # No assumption of independent Gaussian calibration errors. Interval
    # extremum is attained at an endpoint of each bounded pixel coordinate.
    values = []
    for x, p1, p2 in itertools.product((px-mr, px+mr),
                                       (t1-r, t1+r), (t2-r, t2+r)):
        values.append(v1+(x-p1)*(v2-v1)/(p2-p1))
    lo, hi = min(values), max(values)
    require(math.isfinite(lo) and math.isfinite(hi), "axis conversion overflow")
    return (lo, hi)


def read_marker(marker: object, xaxis: dict, yaxis: dict) -> dict:
    m = exact_fields(marker, {"tap", "side", "observation", "pixel_x", "pixel_y",
                              "radius_px", "z_life_m", "z_unc_m", "z_source"}, "marker")
    require(type(m["tap"]) is int and m["tap"] in REQUIRED_FW, "invalid M5 tap")
    require(m["side"] in ALLOWED_SIDES, "FW/NFW must be flow-attachment class")
    require(m["observation"] in {"VISIBLE", "OCCLUDED", "AMBIGUOUS"},
            "unknown visibility status")
    require(m["side"] != "AMBIGUOUS" or m["observation"] == "AMBIGUOUS",
            "unknown attachment class cannot be a resolved numeric marker")
    key = (m["tap"], m["side"])
    if m["observation"] != "VISIBLE":
        require(m["pixel_x"] is None and m["pixel_y"] is None and
                m["radius_px"] is None, "nonvisible marker cannot carry numeric pixels")
        return {"key": key, "status": m["observation"], "z_m": None, "z_source": None}
    require(isinstance(m["z_source"], str) and m["z_source"].strip(),
            "independent tap-position source required")
    z = real(m["z_life_m"], "tap coordinate", nonnegative=True)
    uz = real(m["z_unc_m"], "tap z uncertainty", nonnegative=True)
    if m["tap"] in KNOWN_Z_M:
        require(abs(z-KNOWN_Z_M[m["tap"]]) <= max(uz, 1e-12),
                "tap axial location inconsistent with original source")
    require(uz > 0, "zero unqualified coordinate uncertainty")
    xlo, xhi = axis_interval(xaxis, m["pixel_x"], m["radius_px"], "z_cm_life")
    # Plotted x and separately qualified physical tap coordinate must overlap.
    require(xlo*.01 <= z+uz and xhi*.01 >= z-uz,
            "marker x pixel and physically documented tap position disagree")
    ylo, yhi = axis_interval(yaxis, m["pixel_y"], m["radius_px"], "drop_cmH2O_life")
    return {"key": key, "status": "VISIBLE", "z_m": z, "z_unc_m": uz,
            "z_source": m["z_source"], "x_plot_m": [xlo*.01, xhi*.01],
            "drop_pa": [ylo*CMH2O_TO_PA, yhi*CMH2O_TO_PA]}


def audit(payload: object, figure_bytes: bytes | None = None) -> dict:
    d = exact_fields(payload, {"schema", "case", "figure_asset", "reads"}, "input")
    require(d["schema"] == "vq1-m5-gate1/v1", "unknown schema version")
    case_check(d["case"])
    receipt = {
        "case_id": CASE_ID, "figure_id": "2B", "doi": DOI,
        "figure_sha256": None, "candidate_markers": [],
        "accepted_fw_taps": [], "unresolved": [], "feature_checks": {},
        "digitization_only_checks": {},
        "instrument_uncertainty": "UNQUALIFIED_NO_ABSOLUTE_BOUND",
        "source_metrology": S0, "external_source_audit": "REQUIRED_NOT_PERFORMED",
        "source_qualified_samples": 0, "s2_reference": "HOLD",
        "s3_force": "HOLD", "g1_d": "HOLD", "voice": "NO_GO"
    }
    if d["figure_asset"] is None:
        require(d["reads"] == [], "cannot digitize without original figure bytes")
        receipt["reason"] = "SOURCE_IMAGE_NOT_ACQUIRED"
        return receipt

    asset = exact_fields(d["figure_asset"], {"uri", "sha256", "source_kind",
                                               "acquisition_note"}, "figure asset")
    require(figure_bytes is not None and len(figure_bytes) > 0,
            "original figure bytes unavailable")
    require(isinstance(asset["uri"], str) and asset["uri"].startswith("https://"),
            "original figure URI needed")
    require(asset["source_kind"] == "original_measured_figure2b",
            "computed/reconstructed source is not observed marker layer")
    require(isinstance(asset["acquisition_note"], str) and asset["acquisition_note"].strip(),
            "retrieval provenance needed")
    expected = hashlib.sha256(figure_bytes).hexdigest()
    require(asset["sha256"] == expected, "figure bytes SHA256 mismatch")
    receipt["figure_sha256"] = expected

    require(isinstance(d["reads"], list) and len(d["reads"]) == 2,
            "exactly two independent read sessions required")
    readers, read_ids, points = set(), set(), []
    for reading in d["reads"]:
        s = exact_fields(reading, {"read_id", "analyst_id", "independent", "x_axis",
                                   "y_axis", "markers"}, "reading")
        require(type(s["read_id"]) is str and bool(s["read_id"].strip()), "read id required")
        require(type(s["analyst_id"]) is str and bool(s["analyst_id"].strip()),
                "analyst id required")
        require(s["read_id"] not in read_ids and s["analyst_id"] not in readers,
                "duplicate analyst or read IDs cannot prove two independent reads")
        require(s["independent"] is True, "reader independence not declared")
        read_ids.add(s["read_id"])
        readers.add(s["analyst_id"])
        require(isinstance(s["markers"], list), "markers must be list")
        # Validate axes even when no markers were readable.
        axis_interval(s["x_axis"], 0, 0, "z_cm_life")
        axis_interval(s["y_axis"], 0, 0, "drop_cmH2O_life")
        session_points = {}
        for marker in s["markers"]:
            item = read_marker(marker, s["x_axis"], s["y_axis"])
            require(item["key"] not in session_points, "duplicate tap-side per reader")
            session_points[item["key"]] = item
        points.append(session_points)

    require(d["reads"][0] != d["reads"][1], "identical duplicated read session")
    for key in sorted(set(points[0]) | set(points[1])):
        first, second = (p.get(key) for p in points)
        kname = f"tap{key[0]}:{key[1]}"
        if first is None or second is None or first["status"] != "VISIBLE" or second["status"] != "VISIBLE":
            receipt["unresolved"].append({"point": kname, "reason": "NOT_INDEPENDENTLY_VISIBLE_BOTH_READS"})
            continue
        overlap_lo = max(first["drop_pa"][0], second["drop_pa"][0])
        overlap_hi = min(first["drop_pa"][1], second["drop_pa"][1])
        if overlap_lo > overlap_hi:
            receipt["unresolved"].append({"point": kname, "reason": "INCOMPATIBLE_INDEPENDENT_READS"})
            continue
        # Do not narrow physical uncertainty by intersecting two imperfect
        # digitizer intervals. Require overlap for consistency, report the
        # conservative ENVELOPE of both independently defensible intervals.
        lo = min(first["drop_pa"][0], second["drop_pa"][0])
        hi = max(first["drop_pa"][1], second["drop_pa"][1])
        z_overlap_lo = max(first["x_plot_m"][0], second["x_plot_m"][0],
                           first["z_m"]-first["z_unc_m"], second["z_m"]-second["z_unc_m"])
        z_overlap_hi = min(first["x_plot_m"][1], second["x_plot_m"][1],
                           first["z_m"]+first["z_unc_m"], second["z_m"]+second["z_unc_m"])
        if z_overlap_lo > z_overlap_hi:
            receipt["unresolved"].append({"point": kname, "reason": "TAP_SPATIAL_DISAGREEMENT"})
            continue
        # Graphic x is a tap-identity crosscheck, NOT a new instrument
        # measuring the manufactured physical tap location.
        zlo = min(first["z_m"]-first["z_unc_m"], second["z_m"]-second["z_unc_m"])
        zhi = max(first["z_m"]+first["z_unc_m"], second["z_m"]+second["z_unc_m"])
        receipt["candidate_markers"].append({"tap": key[0], "attachment_class": key[1],
                                               "drop_pa_interval": [lo, hi], "z_m_interval": [zlo,zhi],
                                               "reader_ids": sorted(read_ids),
                                               "provenance": "UNQUALIFIED_TWO_READER_CANDIDATE"})
        if key[1] == "FW":
            receipt["accepted_fw_taps"].append(key[0])
    receipt["accepted_fw_taps"].sort()
    by_fw = {v["tap"]: v["drop_pa_interval"] for v in receipt["candidate_markers"]
             if v["attachment_class"] == "FW"}
    for name, a, b, direction in (("H_AXIAL",6,11,"increase"),
                                   ("H_RECOVERY",11,13,"decrease")):
        if a not in by_fw or b not in by_fw:
            outcome = "INDETERMINATE_MISSING_INDEPENDENT_POINTS"
        elif direction == "increase":
            outcome = ("SUPPORT_CANDIDATE" if by_fw[b][0] > by_fw[a][1] else
                       "CONTRADICT_CANDIDATE" if by_fw[b][1] < by_fw[a][0] else
                       "INDETERMINATE_INTERVAL_OVERLAP")
        else:
            outcome = ("SUPPORT_CANDIDATE" if by_fw[b][1] < by_fw[a][0] else
                       "CONTRADICT_CANDIDATE" if by_fw[b][0] > by_fw[a][1] else
                       "INDETERMINATE_INTERVAL_OVERLAP")
        receipt["digitization_only_checks"][name] = outcome
        receipt["feature_checks"][name] = (
            "INDETERMINATE_MISSING_INDEPENDENT_POINTS" if a not in by_fw or b not in by_fw
            else "INDETERMINATE_INSTRUMENT_UNQUALIFIED")
    receipt["source_metrology"] = (COMPLETE if set(receipt["accepted_fw_taps"]) == REQUIRED_FW
                                   else PARTIAL)
    receipt["source_qualified_samples"] = 0
    receipt["reason"] = "INDEPENDENT_PUBLICATION_FIGURE_AUDIT_STILL_REQUIRED"
    return receipt


def audit_file(path: Path | None, figure: Path | None = None) -> dict:
    if path is None:
        path = Path(__file__).with_name("source_manifest.json")
    data = path.read_bytes()
    figure_data = figure.read_bytes() if figure is not None else None
    result = audit(json.loads(data), figure_data)
    result["input_sha256"] = hashlib.sha256(data).hexdigest()
    return result
