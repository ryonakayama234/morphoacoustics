"""Audited, deliberately narrow live physics boundary for one V3 /a/→/i/-like task.

This is an integration adapter, NOT a new phonology, task or production solver.
The experiment modules are loaded only after validation and frozen-source checks.
The module is source-checkout-only until the audited research kernel is promoted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import ModuleType
from typing import Any
import wave

import numpy as np

from morphoacoustics.domain.result import FeasibilityStatus

SCHEMA_VERSION = "morpho-live/v1"
COMPILER_VERSION = "frozen-v3a-task-3/v1"
PRONUNCIATION_ID = "v3a-a-to-i-like/v1"
BODY_ID = "v3c-M_plus/v1"
SOURCE_ID = "lf_fixed"
BACKEND_VERSION = "x2a-experimental-1"
AUDITED_EXP29_GIT_BLOB = "8d911d6a9d7f2dce556b1fd57439e74b3ff07269"
SAMPLE_RATE_HZ = 48000
DURATION_S = 0.5
SAMPLES = 24000
LISTENING_PEAK = 0.90
ROOT = Path(__file__).resolve().parents[3]
EXP29_PATH = ROOT / "experiments" / "029_task_field_embodied_infeasibility" / "run.py"
REQUIRED_KEYS = frozenset({
    "schema_version", "pronunciation_id", "body_id",
    "segment_id", "text", "seed",
})
OPTIONAL_KEYS = frozenset({"direction"})


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _response(
    request: object, outcome: str, code: str, message: str,
) -> dict[str, Any]:
    try:
        request_sha256: str | None = digest(canonical_bytes(request))
    except (ValueError, TypeError):
        request_sha256 = None
    return {
        "schema_version": SCHEMA_VERSION,
        "job_status": "SUCCEEDED",
        "realization_outcome": outcome,
        "diagnostics": [{"code": code, "message": message}],
        "artifacts": [],
        "provenance": {
            "backend": "morphoacoustics-limited-live",
            "backend_version": BACKEND_VERSION,
            "compiler_version": COMPILER_VERSION,
            "request_digest_algorithm": "sha256/json-utf8-sort-keys-v1",
            "request_sha256": request_sha256,
        },
    }


def validate(request: object) -> dict[str, Any] | None:
    """Separate structurally INVALID requests from known-but-UNSUPPORTED input."""
    if not isinstance(request, dict):
        return _response(request, "INVALID", "REQUEST_SHAPE", "expected an object")
    try:
        canonical_bytes(request)
    except (ValueError, TypeError):
        return _response(request, "INVALID", "REQUEST_ENCODING", "nonfinite or non-JSON value")
    keys = set(request)
    if keys - (REQUIRED_KEYS | OPTIONAL_KEYS) or REQUIRED_KEYS - keys:
        return _response(request, "INVALID", "REQUEST_KEYS", "missing or unknown fields")
    if (
        not all(isinstance(request[key], str) and request[key]
                for key in ("schema_version", "pronunciation_id", "body_id", "segment_id", "text"))
        or type(request["seed"]) is not int
        or ("direction" in request and not isinstance(request["direction"], dict))
    ):
        return _response(request, "INVALID", "REQUEST_TYPES", "invalid field types")
    if request["schema_version"] != SCHEMA_VERSION:
        return _response(request, "UNSUPPORTED", "SCHEMA_VERSION", "unsupported request version")
    if request["pronunciation_id"] != PRONUNCIATION_ID or request["text"] != "あい":
        return _response(request, "UNSUPPORTED", "PRONUNCIATION", "only frozen /a/→/i/-like fixture is supported")
    if request["body_id"] != BODY_ID:
        return _response(request, "UNSUPPORTED", "BODY", "only audited M_plus prepared body is exposed")
    if request["seed"] != 0:
        return _response(request, "UNSUPPORTED", "SEED", "frozen source is deterministic; only seed=0 is supported")
    if request.get("direction"):
        return _response(request, "UNSUPPORTED", "DIRECTION", "creative controls have no validated mapping")
    return None


def _load_audited_experiment() -> ModuleType:
    """Fail closed on edits to the adopted scientific path, including transitive files."""
    if not EXP29_PATH.is_file():
        raise RuntimeError("audited Experiment 029 not installed; run from repository checkout")
    raw = EXP29_PATH.read_bytes()
    git_blob = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
    if git_blob != AUDITED_EXP29_GIT_BLOB:
        raise RuntimeError("audited Experiment 029 runner Git blob changed")
    spec = importlib.util.spec_from_file_location("morpho_live_exp029", EXP29_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import audited Experiment 029")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if np.__version__ != module.AUDITED_NUMPY_VERSION:
        raise RuntimeError(
            f"requires frozen NumPy {module.AUDITED_NUMPY_VERSION}, found {np.__version__}"
        )
    frozen_files = {
        module.EXP28.FROZEN_REFERENCE_PATH: module.EXP28_FROZEN_REFERENCE_GIT_BLOB_SHA,
        module.EXP28.ORACLE_PATH: module.EXP28_ORACLE_GIT_BLOB_SHA,
        module.HERE / "wolfram" / "v3c_oracle.wl": module.V3C_ORACLE_WOLFRAM_SOURCE_GIT_BLOB_SHA,
        module.ORACLE_PATH: module.ORACLE_GIT_BLOB_SHA,
    }
    for path, pinned_sha in frozen_files.items():
        if module.git_blob_sha1(path) != pinned_sha:
            raise RuntimeError(f"audited frozen file changed: {path}")
    oracle = json.loads(module.ORACLE_PATH.read_text(encoding="utf-8"))
    exp28_oracle = json.loads(module.EXP28.ORACLE_PATH.read_text(encoding="utf-8"))
    frozen = json.loads(module.EXP28.FROZEN_REFERENCE_PATH.read_text(encoding="utf-8"))
    m0_a = module.EXP26.EXP23.primary_geometry("a")
    m0_i = module.EXP26.EXP23.primary_geometry("i")
    upstream = module.EXP28.frozen_preflight(exp28_oracle, frozen, m0_a, m0_i)
    local = module.local_oracle_preflight(oracle)
    if not upstream["pass"] or not local["pass"]:
        raise RuntimeError("adopted V3a/V3b/V3c frozen preflight failed")
    return module


def _physical_trace(experiment: ModuleType, start: Any) -> bytes:
    """10-ms aligned samples of the very same frozen task trajectory."""
    rows: list[dict[str, object]] = []
    exp27 = experiment.EXP27
    for n in range(51):
        t = n / 100.0
        activations = exp27.task_activations_at_time(
            t, control_step_s=exp27.PRIMARY_CONTROL_STEP_S
        )
        geometry = exp27.task_geometry_for_time(
            start, t, control_step_s=exp27.PRIMARY_CONTROL_STEP_S,
            cavity_id=f"{start.cavity_id}-v3c-m_plus",
        )
        areas = [section.area_m2 for section in geometry.sections]
        rows.append({
            "time_s": f"{t:.2f}",
            # The final t=0.50 is an endpoint-exclusive frame boundary.
            "sample_index": round(t * SAMPLE_RATE_HZ),
            "task0_activation": f"{activations[0]:.17g}",
            "task1_activation": f"{activations[1]:.17g}",
            "task2_activation": f"{activations[2]:.17g}",
            "min_area_m2": f"{min(areas):.17g}",
            "max_area_m2": f"{max(areas):.17g}",
        })
    import io
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _wav_bytes(pressure: np.ndarray) -> bytes:
    """Playback scaling is recorded separately; never treat WAV as raw pressure."""
    import io
    peak = float(np.max(np.abs(pressure)))
    if not math.isfinite(peak) or peak <= 0:
        raise RuntimeError("cannot normalize nonfinite or zero acoustic pressure")
    scaled = np.clip(pressure * (LISTENING_PEAK / peak), -1.0, 1.0)
    pcm16 = np.rint(scaled * 32767).astype("<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE_HZ)
        handle.writeframes(pcm16.tobytes())
    return buffer.getvalue()


def perform(request: object, output_dir: Path) -> dict[str, Any]:
    """Every FEASIBLE call re-executes physical/acoustic synthesis; never cache audio."""
    rejected = validate(request)
    if rejected is not None:
        return rejected
    assert isinstance(request, dict)
    # Never reuse earlier Take bytes or delete the caller's data.
    if output_dir.exists():
        raise FileExistsError(f"requires a new output directory: {output_dir}")
    if not output_dir.parent.is_dir():
        raise FileNotFoundError(f"output parent does not exist: {output_dir.parent}")
    exp = _load_audited_experiment()
    if (
        exp.EXP27.SAMPLE_RATE_HZ != SAMPLE_RATE_HZ
        or exp.EXP27.DURATION_S != DURATION_S
        or len(exp.EXP27.TASKS) != 3
    ):
        raise RuntimeError("frozen execution schedule changed")
    start = exp.EXP26.EXP23.primary_geometry("a")
    body = exp.prepared_for(
        creature=exp.creature_for(
            cavity_id=start.cavity_id, oral_reachable_end=0.75,
        ),
        geometry=start,
        condition="M_plus",
    )
    # Feasibility MUST be established before even generating the source.
    feasibility = exp.capability_report(body)
    if feasibility.status is not FeasibilityStatus.FEASIBLE:
        return _response(
            request, feasibility.status.value,
            feasibility.issues[0].code if feasibility.issues else "FEASIBILITY",
            "prepared body cannot realize the frozen task",
        )
    sources, _ = exp.EXP26.EXP13.build_sources()
    pressure_source = np.asarray(sources[SOURCE_ID].source, dtype=np.float64)
    result = exp.evaluate_condition(body, pressure_source, label="m_plus")
    if (
        result.feasibility.status is not FeasibilityStatus.FEASIBLE
        or result.waveform is None or result.endpoint is None
        or result.acoustic_call_count != 102
    ):
        raise RuntimeError("audited live solver failed to produce a feasible 102-call trajectory")
    pressure = np.asarray(result.waveform, dtype=np.float64)
    if pressure.shape != (SAMPLES,) or not np.all(np.isfinite(pressure)):
        raise RuntimeError("unexpected raw pressure shape or nonfinite values")
    quantized = exp.quantized_waveform_sha256(pressure)
    if quantized != exp.AUDITED_QUANTIZED_WAVEFORM_SHA256:
        raise RuntimeError("new acoustic computation differs from audited numerical fixture")
    wav = _wav_bytes(pressure)
    trace = _physical_trace(exp, start)
    import io
    raw_buffer = io.BytesIO()
    np.save(raw_buffer, pressure, allow_pickle=False)
    raw = raw_buffer.getvalue()
    payloads = (
        ("audio", "audio.wav", "audio/wav", wav),
        ("raw_pressure", "raw_pressure_pa.npy", "application/x-npy", raw),
        ("physical_trace", "physical_trace.csv", "text/csv", trace),
    )
    artifacts = [
        {"kind": kind, "path": filename, "media_type": media_type,
         "sha256": digest(contents), "size_bytes": len(contents)}
        for kind, filename, media_type, contents in payloads
    ]
    answer: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "job_status": "SUCCEEDED",
        "realization_outcome": "FEASIBLE",
        "diagnostics": [],
        "segment_id": request["segment_id"],
        "timeline": [{"segment_id": request["segment_id"],
                      "start_seconds": 0.0, "end_seconds": DURATION_S}],
        "artifacts": artifacts,
        "execution": {"acoustic_transfer_calls": result.acoustic_call_count,
                      "waveform_samples": SAMPLES, "sample_rate_hz": SAMPLE_RATE_HZ},
        "provenance": {
            "backend": "morphoacoustics-limited-live",
            "backend_version": BACKEND_VERSION,
            "compiler_version": COMPILER_VERSION,
            "pronunciation_id": PRONUNCIATION_ID,
            "body_id": BODY_ID,
            "source_id": SOURCE_ID,
            "seed": request["seed"],
            "request_digest_algorithm": "sha256/json-utf8-sort-keys-v1",
            "request_sha256": digest(canonical_bytes(request)),
            "task_plan_sha256": exp.sha256_json(exp.task_plan_payload()),
            "body_rest_geometry_sha256": exp.sha256_json(exp.geometry_payload(body.rest_state)),
            "body_oral_shaper_reachable_end": 0.75,
            "source_sha256_float64_diagnostic_only": exp.EXP26.sha256_float64(pressure_source),
            "upstream_exp28_frozen_reference_git_blob": exp.EXP28_FROZEN_REFERENCE_GIT_BLOB_SHA,
            "experiment_029_git_blob": AUDITED_EXP29_GIT_BLOB,
            "adopted_evidence": ["Experiment 027 / PR #63", "Experiment 028 / PR #65",
                                 "Experiment 029 / PR #68"],
            "numpy_version": np.__version__,
            "raw_float64_sha256_diagnostic_only": exp.EXP26.sha256_float64(pressure),
            "quantization_pa": exp.AUDITED_WAVEFORM_QUANTIZATION_PA,
            "quantized_raw_pressure_sha256": quantized,
            "playback_peak_normalization": LISTENING_PEAK,
            "claim_limit": "one experimental /a/ to /i/-like utterance; no human phonetic gate",
        },
    }
    # Materialize only after all scientific gates have passed. No stale Take reuse.
    staging = Path(tempfile.mkdtemp(prefix=".morpho-live-", dir=output_dir.parent))
    try:
        for _, filename, _, contents in payloads:
            (staging / filename).write_bytes(contents)
        (staging / "result.json").write_bytes(canonical_bytes(answer) + b"\n")
        if output_dir.exists():
            raise FileExistsError(f"output appeared during generation: {output_dir}")
        os.rename(staging, output_dir)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimental frozen live physics CLI")
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"))
        result = perform(request, args.output_dir)
    except Exception as exc:
        result = {
            "schema_version": SCHEMA_VERSION,
            "job_status": "FAILED",
            "realization_outcome": None,
            "diagnostics": [{"code": "EXECUTION_FAILED", "message": str(exc)}],
            "artifacts": [],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["job_status"] == "FAILED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
