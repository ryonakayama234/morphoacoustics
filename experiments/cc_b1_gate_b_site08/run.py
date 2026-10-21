"""CC-B1 Gate B NEW Core physical trial, exact Gate A protocol committed beforehand.

Research-only: no public BodyRevision/Studio API and no independent scientific
ratification. This site08 was absent from earlier Core wave-trace experiments,
but present in prior theoretical whole-tract scan, and thus is not blind.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import subprocess
from pathlib import Path
import runpy
import sys
import wave

import numpy as np

from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SECTION_INDEX = 8
ALLOWED_RATIOS = (0.90, 1.00, 1.10)
WOLFRAM_GRID_HZ = 5.0
ORACLE_TOLERANCE_HZ = 7.5
SAMPLE_COUNT = 24000
SOURCE_RATE = 48000
ORACLE = ROOT / "docs/research/cc-b1-tract-edit/gate_a_site08_oracle.json"
FREEZE_COMMIT_SHA = "ca8bf64c8525a9cf59cb1332c4819763a0f9197e"
FROZEN_ORACLE_GIT_BLOB_SHA = "046a26a7baf31003244e05088a2b5d19bc7af416"


def checked_ratio(value: object) -> float:
    """Fail closed: no free-form section/ratio is accepted by this experiment."""
    if type(value) is not float or not math.isfinite(value) or value not in ALLOWED_RATIOS:
        raise ValueError("UNSUPPORTED: exactly 0.90, 1.00, or 1.10 is permitted")
    return value


def checked_section_index(value: object) -> int:
    if type(value) is not int or value != SECTION_INDEX:
        raise ValueError("UNSUPPORTED: Gate A fixes only zero-based section 8")
    return value


def verify_source_identity(expected_sha: str, actual: np.ndarray) -> None:
    if sha_array(actual) != expected_sha:
        raise ValueError("SOURCE_CHANGED: frozen LF source modified")


def exact_checkout_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          text=True, capture_output=True, check=True).stdout.strip()


def verify_frozen_oracle(path: Path) -> None:
    actual = subprocess.run(["git", "hash-object", str(path)], cwd=ROOT,
                            text=True, capture_output=True, check=True).stdout.strip()
    if actual != FROZEN_ORACLE_GIT_BLOB_SHA:
        raise RuntimeError("ORACLE_CONTENT_DRIFT: Gate A frozen oracle bytes changed")


def verify_gate_a_ancestry() -> None:
    result = subprocess.run(["git", "merge-base", "--is-ancestor",
                             FREEZE_COMMIT_SHA, "HEAD"], cwd=ROOT,
                            text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError("FREEZE_ANCESTRY_MISMATCH: Gate A commit absent")


def edit_rest_geometry(reference: Tract1DGeometry, ratio: float) -> Tract1DGeometry:
    checked_ratio(ratio)
    checked_section_index(SECTION_INDEX)
    if len(reference.sections) != 16:
        raise ValueError("UNSUPPORTED: only 16-section rest geometry")
    if any(not math.isclose(s.length_m, 0.010, rel_tol=0, abs_tol=1e-14)
           for s in reference.sections):
        raise ValueError("UNSUPPORTED: only 16 by 10-mm geometry")
    sections = tuple(
        TubeSection(
            length_m=section.length_m,
            area_m2=section.area_m2 * ratio if j == SECTION_INDEX else section.area_m2,
        )
        for j, section in enumerate(reference.sections)
    )
    return Tract1DGeometry(cavity_id=reference.cavity_id, sections=sections)


def sha_array(value: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(value, dtype="<f8").tobytes()).hexdigest()

def preview_wav_bytes(raw_pressure_pa: np.ndarray, common_gain: float) -> bytes:
    """Research preview ONLY: 48kHz mono PCM with shared gain, not calibrated SPL."""
    raw = np.asarray(raw_pressure_pa, dtype=np.float64)
    if (raw.shape != (SAMPLE_COUNT,) or not np.all(np.isfinite(raw))
        or not math.isfinite(common_gain) or common_gain <= 0.0):
        raise ValueError("invalid research preview source/gain")
    scaled = raw * common_gain
    if not np.all(np.isfinite(scaled)) or np.max(np.abs(scaled)) > 0.90000001:
        raise ValueError("preview common gain would clip")
    pcm = np.rint(scaled * 32767.0).astype("<i2")
    stream = io.BytesIO()
    with wave.open(stream, "wb") as sink:
        sink.setnchannels(1)
        sink.setsampwidth(2)
        sink.setframerate(SOURCE_RATE)
        sink.writeframes(pcm.tobytes())
    return stream.getvalue()



def prepare_condition(exp: object, reference: Tract1DGeometry, ratio: float):
    geom = edit_rest_geometry(reference, ratio)
    creature = exp.creature_for(cavity_id=geom.cavity_id, oral_reachable_end=0.75)
    return prepare_tract1d(
        creature, geom,
        provenance=PreparationProvenance(
            source="cc-b1-gate-b-site08-new-core-physical-run",
            model="frozen-one-site-rest-area-section-8/v0",
            notes=("not-an-adopted-editor", "immutable-exp029-source-plan",
                   "site8-prospective-Core-only", f"rest_area_ratio={ratio:.2f}",
                   "gate-a-commit=" + FREEZE_COMMIT_SHA),
        ),
    )


def geometry_payload(geometry: Tract1DGeometry) -> dict[str, object]:
    return {
        "section_length_m": [s.length_m for s in geometry.sections],
        "section_area_m2": [s.area_m2 for s in geometry.sections],
    }


def run(output_dir: Path) -> dict[str, object]:
    verify_gate_a_ancestry()
    verify_frozen_oracle(ORACLE)
    # Frozen source and oracle preflight precedes the experiment's new outputs.
    adapter = runpy.run_path(str(ROOT / "tools" / "cc_a2_live.py"))
    frozen = adapter["_load_frozen_adapter"]()
    exp = frozen._load_audited_experiment()
    if np.__version__ != exp.AUDITED_NUMPY_VERSION:
        raise RuntimeError("FAIL: pinned NumPy mismatch")
    if output_dir.exists():
        raise FileExistsError("refuse to overwrite experiment evidence")
    baseline = exp.EXP26.EXP23.primary_geometry("a")
    if len(baseline.sections) != 16:
        raise RuntimeError("baseline is not CC-A2 16-section geometry")
    sources, _ = exp.EXP26.EXP13.build_sources()
    source = np.asarray(sources[frozen.SOURCE_ID].source, dtype=np.float64)
    if source.shape != (SAMPLE_COUNT,) or not np.all(np.isfinite(source)):
        raise RuntimeError("source drift")

    oracle = json.loads(ORACLE.read_text("utf-8"))
    if (oracle["schema"] != "research.cc-b1.gate-a/site08-v1"
        or oracle["zero_based_section_index"] != SECTION_INDEX
        or oracle["ratio_values"] != [0.9,1.0,1.1]
        or oracle["predetermined_max_peak_error_hz"] != ORACLE_TOLERANCE_HZ):
        raise RuntimeError("FAIL: frozen Gate A oracle drift")
    source_sha = sha_array(source)
    plan_sha = exp.sha256_json(exp.task_plan_payload())
    runs: list[tuple[float, object, object, np.ndarray]] = []
    for ratio in ALLOWED_RATIOS:
        verify_source_identity(source_sha, source)
        if exp.sha256_json(exp.task_plan_payload()) != plan_sha:
            raise RuntimeError("FAIL: frozen three-task plan drift")
        prepared = prepare_condition(exp, baseline, ratio)
        if exp.capability_report(prepared).status is not exp.FeasibilityStatus.FEASIBLE:
            raise RuntimeError("edited rest shape is not capable of frozen three-task plan")
        result = exp.evaluate_condition(prepared, source, label=f"cc_b1_gate_b_site08_{ratio:.2f}")
        if (result.feasibility.status is not exp.FeasibilityStatus.FEASIBLE
            or result.waveform is None or result.endpoint is None
            or result.acoustic_call_count != 102):
            raise RuntimeError("physical execution did not complete 102 time-acoustic calls")
        raw = np.asarray(result.waveform, dtype=np.float64)
        if raw.shape != (SAMPLE_COUNT,) or not np.all(np.isfinite(raw)):
            raise RuntimeError("invalid 48kHz / 0.5-second pressure")
        if ratio == 1.0 and exp.quantized_waveform_sha256(raw) != exp.AUDITED_QUANTIZED_WAVEFORM_SHA256:
            raise RuntimeError("adopted baseline M0 raw pressure changed")

        # Holding the exact task plan fixed makes geometry intervention auditable.
        for t in (0.0, 0.20, 0.35, 0.50):
            edited = exp.EXP27.task_geometry_for_time(
                prepared.rest_state, t, control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,
                cavity_id=baseline.cavity_id + "-cc-b1-candidate",
            )
            null = exp.EXP27.task_geometry_for_time(
                baseline, t, control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,
                cavity_id=baseline.cavity_id + "-cc-b1-null",
            )
            actual_ratio = np.asarray([s.area_m2 for s in edited.sections]) / np.asarray(
                [s.area_m2 for s in null.sections])
            expected_ratio = np.ones(16)
            expected_ratio[SECTION_INDEX] = ratio
            if not np.allclose(actual_ratio, expected_ratio, rtol=2e-12, atol=2e-12):
                raise RuntimeError("rest geometry does not survive task realization")
        verify_source_identity(source_sha, source)
        if exp.sha256_json(exp.task_plan_payload()) != plan_sha:
            raise RuntimeError("FAIL: source/task changed during physical execution")
        runs.append((ratio, prepared, result, raw))

    # The second baseline is a separate fresh solver execution; it is not an array copy.
    repeat_result = exp.evaluate_condition(runs[1][1], source, label="cc_b1_gate_b_baseline_repeat")
    repeat_raw = np.asarray(repeat_result.waveform, dtype=np.float64) if repeat_result.waveform is not None else None
    if (repeat_result.feasibility.status is not exp.FeasibilityStatus.FEASIBLE
        or repeat_result.endpoint is None or repeat_result.acoustic_call_count != 102
        or repeat_raw is None or repeat_raw.shape != (SAMPLE_COUNT,)
        or not np.all(np.isfinite(repeat_raw))):
        raise RuntimeError("FAIL: independently rerun baseline did not physically complete")
    if (exp.quantized_waveform_sha256(repeat_raw) != exp.AUDITED_QUANTIZED_WAVEFORM_SHA256
        or exp.quantized_waveform_sha256(repeat_raw)
           != exp.quantized_waveform_sha256(runs[1][3])):
        raise RuntimeError("FAIL: rerun baseline disagrees with frozen quantized null")
    verify_source_identity(source_sha, source)

    baseline_raw = runs[1][3]
    comparisons = []
    for ratio, prepared, result, raw in runs:
        start = exp.EXP26.peak_array(prepared.rest_state, count=3)
        end = exp.EXP26.peak_array(result.endpoint, count=3)
        expected = oracle["frozen_peaks_hz"][f"{ratio:.2f}"]
        rest_err = float(np.max(np.abs(start - np.asarray(expected["rest"]))))
        final_err = float(np.max(np.abs(end - np.asarray(expected["terminal"]))))
        if rest_err > ORACLE_TOLERANCE_HZ or final_err > ORACLE_TOLERANCE_HZ:
            raise RuntimeError("FAIL: pre-frozen independent Wolfram oracle mismatch")
        diff = raw - baseline_raw
        diff_ratio = float(np.linalg.norm(diff) / np.linalg.norm(baseline_raw))
        if ratio == 1.0 and diff_ratio != 0.0:
            raise RuntimeError("baseline null differs from itself")
        if ratio != 1.0 and not diff_ratio > 1e-8:
            raise RuntimeError("NUMERICALLY_UNRESOLVED: edited pressure identical within frozen limit")
        comparisons.append({
            "ratio": ratio, "section": SECTION_INDEX,
            "rest_area_m2": prepared.rest_state.sections[SECTION_INDEX].area_m2,
            "rest_peaks_hz": start.tolist(), "final_peaks_hz": end.tolist(),
            "wolfram_rest_max_abs_error_hz": rest_err,
            "wolfram_final_max_abs_error_hz": final_err,
            "raw_pressure_sha256_le_f64": sha_array(raw),
            "raw_pressure_quantized_sha256": exp.quantized_waveform_sha256(raw),
            "relative_l2_difference_from_baseline": diff_ratio,
            "acoustic_calls": result.acoustic_call_count,
            "raw_pressure_file": f"pressure_{ratio:.2f}.npy",
            "geometry": geometry_payload(prepared.rest_state),
        })

    # Shared gain across ALL three conditions. Preview WAVs are auditable
    # observations of the actual raw pressure, never modified physical output.
    max_abs_pressure = max(float(np.max(np.abs(item[3]))) for item in runs)
    if not math.isfinite(max_abs_pressure) or max_abs_pressure <= 0.0:
        raise RuntimeError("no valid pressure for common preview normalization")
    common_gain = 0.9 / max_abs_pressure
    preview_wavs = {
        f"{ratio:.2f}": preview_wav_bytes(raw, common_gain)
        for ratio, _, _, raw in runs
    }
    for comparison in comparisons:
        key = f"{comparison['ratio']:.2f}"
        comparison["preview_wav_file"] = f"preview_{key}.wav"
        comparison["preview_wav_sha256"] = hashlib.sha256(preview_wavs[key]).hexdigest()

    # Research preview only: not a new public performance or Studio Take.
    output_dir.mkdir(parents=True, exist_ok=False)
    with (output_dir / "pressure_repeat_1.00.npy").open("wb") as f:
        np.save(f, repeat_raw, allow_pickle=False)
    for ratio, _, _, raw in runs:
        with (output_dir / f"pressure_{ratio:.2f}.npy").open("wb") as f:
            np.save(f, raw, allow_pickle=False)
        (output_dir / f"preview_{ratio:.2f}.wav").write_bytes(
            preview_wavs[f"{ratio:.2f}"]
        )
    payload = {
        "status": "RESEARCH_MACHINE_PASS_PENDING_INDEPENDENT_AUDIT",
        "prespecified_freeze_commit": FREEZE_COMMIT_SHA,
        "exact_checkout_sha": exact_checkout_sha(),
        "oracle_schema": oracle["schema"],
        "oracle_git_blob_sha": FROZEN_ORACLE_GIT_BLOB_SHA,
        "section_zero_based": SECTION_INDEX,
        "baseline_repeat": {
            "fresh_physical_execution": True,
            "quantized_sha256": exp.quantized_waveform_sha256(repeat_raw),
            "raw_le_f64_sha256": sha_array(repeat_raw),
            "sample_count": len(repeat_raw),
            "acoustic_calls": repeat_result.acoustic_call_count,
            "raw_pressure_file": "pressure_repeat_1.00.npy",
        },
        "source_sha256_le_f64": sha_array(source),
        "source_id": frozen.SOURCE_ID,
        "sample_rate_hz": SOURCE_RATE, "samples": SAMPLE_COUNT,
        "task_plan_sha256": plan_sha,
        "frozen_reference_m0_quantized_sha256": exp.AUDITED_QUANTIZED_WAVEFORM_SHA256,
        "model": "16x10mm segmented serial tract, prescribed LF, no FSI",
        "preview_audio": {"format": "mono_pcm16_48000hz",
                          "comparison_shared_gain": common_gain,
                          "status": "RESEARCH_PREVIEW_NOT_A_STUDIO_TAKE",
                          "physical_raw_pa_unchanged": True},
        "oracle": "Gate A SHA-fixed 5Hz ABCD and independent impedance recurrence",
        "oracle_tolerance_hz": ORACLE_TOLERANCE_HZ,
        "conditions": comparisons,
        "limitations": ["site8 existed in earlier theoretical full-tract scan",
                        "not a blind anatomical discovery", "not phonetic identity",
                        "not a natural human voice or audibility result",
                        "not a BodyRevision or Studio API",
                        "no independent physics/contract scientific ratification",
                        "ideal lossless static oracle, not full FSI or passivity proof",
                        "not a quantitative loudness comparison"],
    }
    (output_dir / "decision.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", "utf-8"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output_dir)
    print(json.dumps({
        "status": result["status"],
        "relative_l2_differences": [
            x["relative_l2_difference_from_baseline"] for x in result["conditions"]
        ],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
