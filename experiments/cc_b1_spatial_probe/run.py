"""CC-B1 independent spatial intervention follow-up: EXPLORATORY, not adopted.

Triggered by one informal creator listening report: section-0 variants were
not distinguishable to that listener. This is a site-selective follow-up
*after* the Wolfram location scan, therefore NOT prospective confirmatory data.
The adopted source, task plan, physics and public APIs are never rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import runpy

import numpy as np
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d

ROOT = Path(__file__).resolve().parents[2]
PILOT = runpy.run_path(str(ROOT / "experiments/cc_b1_rest_area_pilot/run.py"),
                      run_name="cc_b1_pilot_reference_for_spatial")
POSITIONS = (0, 2, 4)  # zero-based from glottis; selected post-hoc by Wolfram
RATIOS = (0.90, 1.10)
SAMPLES = 24000
EXPECTED_WOLFRAM_F2 = {
    (0, 0.90): 2110., (0, 1.10): 2095.,
    (2, 0.90): 2130., (2, 1.10): 2075.,
    (4, 0.90): 2065., (4, 1.10): 2130.,
}
ORACLE_TOLERANCE_HZ = 7.5


def edit(reference: Tract1DGeometry, site: int, ratio: float) -> Tract1DGeometry:
    if type(site) is not int or site not in POSITIONS:
        raise ValueError("UNSUPPORTED: only site 0, 2 or 4")
    if type(ratio) is not float or ratio not in RATIOS:
        raise ValueError("UNSUPPORTED: only multiplier 0.90 or 1.10")
    if len(reference.sections) != 16 or any(
        not math.isclose(s.length_m, 0.01, abs_tol=1e-14, rel_tol=0)
        for s in reference.sections
    ):
        raise ValueError("UNSUPPORTED: only exact 16x10mm reference")
    return Tract1DGeometry(
        cavity_id=reference.cavity_id,
        sections=tuple(
            TubeSection(length_m=s.length_m,
                        area_m2=s.area_m2*ratio if j == site else s.area_m2)
            for j, s in enumerate(reference.sections)
        ),
    )


def prepare(exp, baseline, *, site: int, ratio: float):
    new = edit(baseline, site, ratio)
    return prepare_tract1d(
        exp.creature_for(cavity_id=new.cavity_id, oral_reachable_end=0.75), new,
        provenance=PreparationProvenance(
            source="cc-b1-spatial-probe-research-only",
            model="single-section-rest-area-screen/v0",
            notes=(f"section0_based={site}", f"ratio={ratio:.2f}",
                   "no-motor-edit", "post-hoc-spatial-selection", "not-BodyRevision"),
        ),
    )


def run(output: Path):
    if output.exists():
        raise FileExistsError("research output must be a new directory")
    cc_a2 = runpy.run_path(str(ROOT / "tools/cc_a2_live.py"),
                         run_name="cc_b1_spatial_source")
    frozen = cc_a2["_load_frozen_adapter"]()
    exp = frozen._load_audited_experiment()
    if np.__version__ != exp.AUDITED_NUMPY_VERSION:
        raise RuntimeError("audited NumPy ABI mismatch")
    baseline = exp.EXP26.EXP23.primary_geometry("a")
    sources, _ = exp.EXP26.EXP13.build_sources()
    source = np.asarray(sources[frozen.SOURCE_ID].source, dtype=np.float64)
    if source.shape != (SAMPLES,) or not np.isfinite(source).all():
        raise RuntimeError("pinned physical source invalid")

    null = PILOT["prepare_condition"](exp, baseline, 1.0)
    conditions = [("base", None, 1.00, null)]
    for site in POSITIONS:
        for ratio in RATIOS:
            conditions.append(
                (f"s{site:02d}_{round(ratio*100):03d}", site, ratio,
                 prepare(exp, baseline, site=site, ratio=ratio)))

    snapshots = []
    for label, site, ratio, body in conditions:
        if exp.capability_report(body).status is not exp.FeasibilityStatus.FEASIBLE:
            raise RuntimeError(f"{label} is not physically feasible")
        result = exp.evaluate_condition(body, source, label=f"cc_b1_spatial_{label}")
        raw = np.asarray(result.waveform, dtype=np.float64) if result.waveform is not None else None
        if (result.feasibility.status is not exp.FeasibilityStatus.FEASIBLE
            or result.acoustic_call_count != 102 or result.endpoint is None
            or raw is None or raw.shape != (SAMPLES,) or not np.isfinite(raw).all()):
            raise RuntimeError(f"{label}: physical run failed")
        if label == "base" and (
            exp.quantized_waveform_sha256(raw)
            != exp.AUDITED_QUANTIZED_WAVEFORM_SHA256):
            raise RuntimeError("baseline physical waveform oracle drift")
        if site is not None:
            for t in (0., .2, .35, .50):
                check = exp.EXP27.task_geometry_for_time(
                    body.rest_state, t,
                    control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,
                    cavity_id="spatial-check")
                base_check = exp.EXP27.task_geometry_for_time(
                    baseline, t,
                    control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,
                    cavity_id="spatial-null")
                q = np.asarray([s.area_m2 for s in check.sections]) / np.asarray(
                    [s.area_m2 for s in base_check.sections])
                expected = np.ones(16); expected[site] = ratio
                if not np.allclose(q, expected, rtol=1e-11, atol=1e-11):
                    raise RuntimeError("intervention did not survive task-field motion")
        peaks = np.asarray(exp.EXP26.peak_array(result.endpoint, count=2))
        if site is not None and abs(float(peaks[1]) - EXPECTED_WOLFRAM_F2[(site, ratio)]) > ORACLE_TOLERANCE_HZ:
            raise RuntimeError("independent exploratory Wolfram 16-section F2 mismatch")
        snapshots.append((label, site, ratio, body, result, raw, peaks))

    norm = np.linalg.norm(snapshots[0][5])
    if not math.isfinite(float(norm)) or norm == 0:
        raise RuntimeError("invalid baseline waveform norm")
    gain = 0.90 / max(float(np.max(np.abs(x[5]))) for x in snapshots)
    if not math.isfinite(gain) or gain <= 0:
        raise RuntimeError("invalid global single listening gain")

    rows = []
    # Only publish after successful causal/oracle/source proof for all cases.
    output.mkdir(parents=True, exist_ok=False)
    for label, site, ratio, body, result, raw, peaks in snapshots:
        deviation = float(np.linalg.norm(raw - snapshots[0][5]) / norm)
        if site is not None and deviation < 1e-8:
            raise RuntimeError(f"{label}: unexpected waveform identity")
        wav = PILOT["preview_wav_bytes"](raw, gain)
        with (output / f"{label}.npy").open("wb") as fd:
            np.save(fd, raw, allow_pickle=False)
        (output / f"{label}.wav").write_bytes(wav)
        rows.append({
            "condition": label, "zero_based_section": site,
            "rest_area_ratio": ratio, "f1_end_hz": float(peaks[0]),
            "f2_end_hz": float(peaks[1]),
            "relative_raw_pressure_l2_vs_base": deviation,
            "raw_le_float64_sha256": PILOT["sha_array"](raw),
            "quantized_raw_sha256": exp.quantized_waveform_sha256(raw),
            "preview_pcm16_sha256": hashlib.sha256(wav).hexdigest(),
            "acoustic_calls": result.acoustic_call_count,
        })
    report = {
        "decision": "POSTHOC_SPATIAL_EXPLORATION_NOT_AUDIBILITY",
        "source": frozen.SOURCE_ID,
        "source_raw_sha256": PILOT["sha_array"](source),
        "source_reused_across_all_conditions": True,
        "task_plan_sha256": exp.sha256_json(exp.task_plan_payload()),
        "sample_rate_hz": 48000, "sample_count": SAMPLES,
        "preview_gain_common_for_all_conditions": gain,
        "Wolfram_assumption": "16x10mm serial impedance, ideal pressure-release outlet; 5Hz grid",
        "Wolfram_peak_tolerance_hz": ORACLE_TOLERANCE_HZ,
        "conditions": rows,
        "limitations": [
            "sites 0/2/4 deliberately chosen after a 16-site sensitivity scan",
            "NOT confirmatory, NOT a listening test, NOT improved voice quality",
            "no free-form editor, no immutable Studio Take, no calibrated SPL",
            "listening is unblinded with descriptive filenames",
        ],
    }
    (output / "decision.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+"\n",
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    options = parser.parse_args()
    result = run(options.output_dir)
    print(json.dumps({
        "decision": result["decision"],
        "condition_differences": {
            x["condition"]: x["relative_raw_pressure_l2_vs_base"]
            for x in result["conditions"]
        }}, ensure_ascii=False))
