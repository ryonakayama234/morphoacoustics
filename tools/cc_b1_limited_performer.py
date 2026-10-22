"""Gate C candidate: opt-in, versioned CC-B1 Core-owned limited physical performer.

Not yet a released Python import API or Studio Take. This is an additive
Core checkout adapter whose hard capability is exactly the Gate B site08
0.90/1.10 body rest-area experiment. It never changes audited CC-A2/v0/v1
contracts or the inherited physics solver.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys
import wave
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VERSION = "cc-b1-core-limited-performer/v1"
BASE_ID = "v3b-axial-M0"
BASE_REVISION = 1
SITE = 8
RATIOS = {"0.90": 0.9, "1.10": 1.1}
SAMPLES = 24000
RATE = 48000
FROZEN_GATE_A_SHA = "ca8bf64c8525a9cf59cb1332c4819763a0f9197e"
ADOPTED_GATE_B_SHA = "b6aa1bed340cbd81d90b46bf16639b3fa47a3bb6"
EXPECTED_EDIT_QUANTIZED = {
    "0.90": "a5f34b795b886f67f88716be53ebf50dd68731e5b4bd03f2c189a1a17a752aa1",
    "1.10": "9f359add71f68ce66a2306d7b5dd66a658b3676d54f66369269eadc71c2c8db6",
}


def refusal(status: str, code: str, message: str) -> dict[str, object]:
    return {"schema_version": VERSION, "status": status,
            "error": {"code": code, "message": message}, "artifacts": []}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_sha(value: np.ndarray) -> str:
    return sha256_bytes(np.asarray(value, dtype="<f8").tobytes())


def checkout_sha() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout.strip()


def check_request(request: object) -> dict[str, object] | None:
    """Reject unknown controls instead of silently ignoring untrusted fields."""
    if type(request) is not dict or set(request) != {"schema_version", "parent", "edit"}:
        return refusal("INVALID", "REQUEST_SHAPE_INVALID", "Exact v1 keys are required")
    if request["schema_version"] != VERSION:
        return refusal("UNSUPPORTED", "SCHEMA_VERSION_UNSUPPORTED", "Unsupported Core capability version")
    parent = request["parent"]
    edit = request["edit"]
    if type(parent) is not dict or set(parent) != {"preset_id", "revision", "preparation_digest"}:
        return refusal("INVALID", "BASE_SHAPE_INVALID", "Invalid parent reference")
    if type(edit) is not dict or set(edit) != {"cavity_id", "section_index", "rest_area_ratio"}:
        return refusal("INVALID", "EDIT_SHAPE_INVALID", "Invalid SI rest-area edit")
    if (type(parent["preset_id"]) is not str or parent["preset_id"] != BASE_ID
        or type(parent["revision"]) is not int or parent["revision"] != BASE_REVISION):
        return refusal("UNSUPPORTED", "BASE_CAPABILITY_UNSUPPORTED", "Only audited CC-A2 M0/r1 supported")
    digest = parent["preparation_digest"]
    if (type(digest) is not str or len(digest) != 71
        or not digest.startswith("sha256:")
        or any(x not in "0123456789abcdef" for x in digest[7:])):
        return refusal("INVALID", "BASE_DIGEST_INVALID", "Require a full lowercase sha256 digest")
    if (type(edit["cavity_id"]) is not str or edit["cavity_id"] != "oral-vowel-a-16x10mm"
        or type(edit["section_index"]) is not int or edit["section_index"] != SITE
        or type(edit["rest_area_ratio"]) is not str
        or edit["rest_area_ratio"] not in RATIOS):
        return refusal("UNSUPPORTED", "EDIT_CAPABILITY_UNSUPPORTED",
                       "Only oral zero-based section 8, ratio 0.90 or 1.10 is validated")
    return None


def common_gain_wav(pressure: np.ndarray, gain: float) -> bytes:
    """Equal playback gain for each body; physical SI Pa remains untouched."""
    if (pressure.shape != (SAMPLES,) or not np.all(np.isfinite(pressure))
        or not math.isfinite(gain) or gain <= 0):
        raise ValueError("INVALID_PHYSICAL_AUDIO")
    values = pressure * gain
    if not np.all(np.isfinite(values)) or np.max(np.abs(values)) > 0.90000001:
        raise ValueError("WAV_CLIPPING")
    pcm = np.rint(values * 32767).astype("<i2")
    stream = io.BytesIO()
    with wave.open(stream, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(pcm.tobytes())
    return stream.getvalue()


def checked_physical_result(exp: Any, result: Any, label: str) -> np.ndarray:
    if (result.feasibility.status is not exp.FeasibilityStatus.FEASIBLE
        or result.endpoint is None or result.waveform is None
        or result.acoustic_call_count != 102):
        raise RuntimeError("FAILED_PHYSICAL_REALIZATION: " + label)
    raw = np.asarray(result.waveform, dtype=np.float64)
    if raw.shape != (SAMPLES,) or not np.all(np.isfinite(raw)):
        raise RuntimeError("FAILED_NONFINITE_PRESSURE: " + label)
    peaks = np.asarray(exp.EXP26.peak_array(result.endpoint, count=3))
    if peaks.shape != (3,) or not np.all(np.isfinite(peaks)):
        raise RuntimeError("FAILED_NONFINITE_RESONANCE: " + label)
    return raw


def inspect_baseline() -> dict[str, object]:
    """Read-only discovery for a caller that must supply exact baseline digest."""
    from morphoacoustics.integration.body_presets import CharacterBodyBinding
    cc_a2 = runpy.run_path(str(ROOT / "tools/cc_a2_live.py"))
    frozen = cc_a2["_load_frozen_adapter"]()
    exp = frozen._load_audited_experiment()
    registry = cc_a2["prepared_registry"](exp)
    resolution = registry.resolve(
        CharacterBodyBinding(character_id="cc-b1", preset_id=BASE_ID,
                             preset_revision=BASE_REVISION),
        required_backend_id=exp.TRACT1D_BACKEND_ID)
    if not resolution.is_bound or resolution.preset is None:
        raise RuntimeError("BASE_PRESET_NOT_RESOLVED")
    body = resolution.preset
    from morphoacoustics.integration.body_presets import preparation_digest
    if preparation_digest(body.prepared) != body.preparation_digest:
        raise RuntimeError("BASE_PRESET_DIGEST_CHANGED")
    return {
        "schema_version": VERSION,
        "parent": {"preset_id": body.preset_id, "revision": body.revision,
                   "preparation_digest": body.preparation_digest},
        "editable": {"cavity_id": body.prepared.rest_state.cavity_id,
                     "section_index": SITE,
                     "original_area_m2": body.prepared.rest_state.sections[SITE].area_m2,
                     "allowed_ratios": sorted(RATIOS)},
        "capability": "rigid-16x10mm-serial-tract; fixed LF three-task",
        "source_gate": ADOPTED_GATE_B_SHA,
    }


def perform(request: object, output_dir: Path) -> dict[str, object]:
    """Create *two* new raw-Pa physical realizations; publish only complete evidence."""
    if os.path.lexists(output_dir):
        raise FileExistsError("OUTPUT_EXISTS: cannot overwrite a physical observation")
    rejected = check_request(request)
    if rejected is not None:
        return rejected
    if not output_dir.parent.is_dir():
        raise FileNotFoundError("OUTPUT_PARENT_MISSING")
    assert isinstance(request, dict)
    assert isinstance(request["parent"], dict)
    assert isinstance(request["edit"], dict)
    cc_a2 = runpy.run_path(str(ROOT / "tools/cc_a2_live.py"))
    frozen = cc_a2["_load_frozen_adapter"]()
    exp = frozen._load_audited_experiment()
    if np.__version__ != exp.AUDITED_NUMPY_VERSION:
        raise RuntimeError("FAILED_NUMPY_VERSION_DRIFT")
    from morphoacoustics.integration.body_presets import CharacterBodyBinding, preparation_digest
    registry = cc_a2["prepared_registry"](exp)
    resolved = registry.resolve(
        CharacterBodyBinding("cc-b1", BASE_ID, BASE_REVISION),
        required_backend_id=exp.TRACT1D_BACKEND_ID)
    if not resolved.is_bound or resolved.preset is None:
        raise RuntimeError("FAILED_BASE_RESOLUTION")
    base = resolved.preset
    if base.preparation_digest != request["parent"]["preparation_digest"]:
        return refusal("REVISION_MISMATCH", "BASE_REVISION_MISMATCH",
                       "Exact authenticated baseline preparation digest does not match")
    if preparation_digest(base.prepared) != base.preparation_digest:
        raise RuntimeError("FAILED_TAMPERED_BASE")
    proto = runpy.run_path(str(ROOT / "tools/cc_b1_revision.py"))
    ratio_key = request["edit"]["rest_area_ratio"]
    assert isinstance(ratio_key, str)
    ratio = RATIOS[ratio_key]
    edit = proto["RestAreaEditIntent"](
        base_preset_id=base.preset_id, base_revision=base.revision,
        base_preparation_digest=base.preparation_digest,
        cavity_id="oral-vowel-a-16x10mm", section_index=SITE,
        area_m2=base.prepared.rest_state.sections[SITE].area_m2 * ratio)
    bound = proto["prepare_rest_area_revision"](base, edit)
    if not bound.accepted or bound.revision is None:
        return refusal(bound.status.value, bound.code or "EDIT_REFUSED",
                       bound.message or "Body was not prepared")
    rev = bound.revision
    bgeom = base.prepared.rest_state
    egeom = rev.prepared.rest_state
    if (len(bgeom.sections) != 16 or len(egeom.sections) != 16
        or any(bgeom.sections[j] != egeom.sections[j] for j in range(16) if j != SITE)
        or any(bgeom.sections[j].length_m != 0.01 for j in range(16))
        or egeom.sections[SITE].area_m2 <= 0):
        raise RuntimeError("FAILED_GEOMETRY_INTERVENTION")
    for t in (0.0, 0.20, 0.35, 0.50):
        before = exp.EXP27.task_geometry_for_time(
            bgeom, t, control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,
            cavity_id="cc-b1-baseline")
        after = exp.EXP27.task_geometry_for_time(
            egeom, t, control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,
            cavity_id="cc-b1-edited")
        actual = np.asarray([s.area_m2 for s in after.sections]) / np.asarray(
            [s.area_m2 for s in before.sections])
        expected = np.ones(16)
        expected[SITE] = ratio
        if not np.allclose(actual, expected, rtol=2e-12, atol=2e-12):
            raise RuntimeError("FAILED_GESTURE_GEOMETRY_DRIFT")
    if (exp.capability_report(base.prepared).status is not exp.FeasibilityStatus.FEASIBLE
        or exp.capability_report(rev.prepared).status is not exp.FeasibilityStatus.FEASIBLE):
        return refusal("INFEASIBLE", "BODY_TASK_INFEASIBLE",
                       "Frozen gesture cannot be performed by this body")
    source_list, _ = exp.EXP26.EXP13.build_sources()
    source = np.asarray(source_list[frozen.SOURCE_ID].source, dtype=np.float64)
    if source.shape != (SAMPLES,) or not np.all(np.isfinite(source)):
        raise RuntimeError("FAILED_SOURCE_INVALID")
    frozen_source_sha = source_sha(source)
    frozen_task_sha = exp.sha256_json(exp.task_plan_payload())
    baseline_result = exp.evaluate_condition(base.prepared, source, label="cc_b1_v1_base")
    edited_result = exp.evaluate_condition(rev.prepared, source, label="cc_b1_v1_" + ratio_key)
    baseline = checked_physical_result(exp, baseline_result, "baseline")
    edited = checked_physical_result(exp, edited_result, "edited")
    if (source_sha(source) != frozen_source_sha
        or exp.sha256_json(exp.task_plan_payload()) != frozen_task_sha):
        raise RuntimeError("FAILED_SOURCE_OR_TASK_MUTATION")
    baseline_sha = exp.quantized_waveform_sha256(baseline)
    edited_sha = exp.quantized_waveform_sha256(edited)
    if baseline_sha != exp.AUDITED_QUANTIZED_WAVEFORM_SHA256:
        raise RuntimeError("FAILED_BASELINE_ORACLE_DRIFT")
    if edited_sha != EXPECTED_EDIT_QUANTIZED[ratio_key]:
        raise RuntimeError("FAILED_EDITED_ORACLE_DRIFT")
    l2 = float(np.linalg.norm(edited - baseline) / np.linalg.norm(baseline))
    if not math.isfinite(l2) or l2 <= 1e-8:
        return refusal("NUMERICALLY_UNRESOLVED", "PRESSURE_NOT_DISTINCT",
                       "Edited model produced no numerically resolved raw pressure difference")
    maxabs = max(float(np.max(np.abs(baseline))), float(np.max(np.abs(edited))))
    if not math.isfinite(maxabs) or maxabs <= 0:
        raise RuntimeError("FAILED_ZERO_PRESSURE")
    gain = 0.9 / maxabs
    def npy_bytes(value: np.ndarray) -> bytes:
        buffer = io.BytesIO()
        np.save(buffer, value, allow_pickle=False)
        return buffer.getvalue()
    payloads = (
        ("baseline-pressure", "baseline_pa.npy", "application/x-npy", npy_bytes(baseline)),
        ("edited-pressure", "edited_pa.npy", "application/x-npy", npy_bytes(edited)),
        ("baseline-audio", "baseline.wav", "audio/wav", common_gain_wav(baseline, gain)),
        ("edited-audio", "edited.wav", "audio/wav", common_gain_wav(edited, gain)),
        ("baseline-trace", "baseline_trace.csv", "text/csv", cc_a2["trace_bytes"](exp, bgeom)),
        ("edited-trace", "edited_trace.csv", "text/csv", cc_a2["trace_bytes"](exp, egeom)),
    )
    items = [{"kind": k, "path": name, "media_type": media, "size_bytes": len(data),
              "sha256": sha256_bytes(data)} for k, name, media, data in payloads]
    receipt: dict[str, object] = {
        "schema_version": VERSION, "status": "SUCCEEDED",
        "capability": "site08-one-section-rest-area-0.90-or-1.10/v1",
        "claim_limit": "fixed LF and three-task, 16x10mm 1D computational physical model",
        "parent": request["parent"], "body_revision": rev.receipt(),
        "source": {"id": frozen.SOURCE_ID, "sha256_le_f64": frozen_source_sha},
        "task_plan_sha256": frozen_task_sha,
        "baseline_quantized_sha256": baseline_sha,
        "edited_quantized_sha256": edited_sha,
        "relative_raw_pa_l2": l2, "acoustic_calls_per_body": 102,
        "sample_rate_hz": RATE, "sample_count": SAMPLES,
        "shared_playback_gain": gain, "artifacts": items,
        "provenance": {"core_checkout_sha": checkout_sha(),
                       "gate_a_freeze_sha": FROZEN_GATE_A_SHA,
                       "gate_b_limited_decision_sha": ADOPTED_GATE_B_SHA,
                       "numpy_version": np.__version__,
                       "python_version": sys.version.split()[0]},
        "limitations": ["research candidate, not installed/published stable API",
                        "no stable Studio Take yet", "no audible voice identity claim",
                        "digest is integrity evidence, not cryptographic origin signature"]
    }
    frozen._publish_new_take(output_dir, payloads, receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect-base", action="store_true")
    parser.add_argument("--request", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.inspect_base:
        if args.request is not None or args.output_dir is not None:
            parser.error("--inspect-base cannot be combined with --request/--output-dir")
        print(json.dumps(inspect_baseline(), sort_keys=True, ensure_ascii=False))
        return
    if args.request is None or args.output_dir is None:
        parser.error("--request and --output-dir must be specified together")
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"),
                             parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
        result = perform(request, args.output_dir)
    except Exception as exc:
        result = refusal("FAILED", "CORE_GATE_C_RUNTIME_FAILURE", str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["status"] != "SUCCEEDED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
