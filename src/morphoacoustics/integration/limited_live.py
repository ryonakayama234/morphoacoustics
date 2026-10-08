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

SCHEMA_VERSION = "morpho-live/v1"
COMPILER_VERSION = "frozen-v3a-task-3/v1"
PRONUNCIATION_ID = "v3a-a-to-i-like/v1"
BODY_ID = "v3c-M_plus/v1"
SOURCE_ID = "lf_fixed"
BACKEND_VERSION = "x2a-experimental-1"
AUDITED_EXP29_GIT_BLOB = "8d911d6a9d7f2dce556b1fd57439e74b3ff07269"
AUDITED_EXP28_GIT_BLOB = "a5bb9a70a58f5ec0f61c3c5f4df1e4dd9bc3e686"
AUDITED_EXP28_REFERENCE_GIT_BLOB = "7810dfbb72cb6c41af007db6e9d51c58cad9a522"
SAMPLE_RATE_HZ = 48000
DURATION_S = 0.5
SAMPLES = 24000
LISTENING_PEAK = 0.90
ROOT = Path(__file__).resolve().parents[3]
# Frozen package sources used to prepare the Experiment 029 runtime.
# Pinning the entire Python package is deliberately conservative: the eager
# package initializers import domain, preparation, simulation, and related
# modules. Any addition/removal/change invalidates this adopted research
# environment until separately audited; limited_live.py is the reviewed
# integration adapter itself, and is intentionally not self-hashed.
AUDITED_PACKAGE_GIT_BLOBS: dict[str, str] = {
    "src/morphoacoustics/__init__.py": "be995aa23576776986a42aafc8dafeb1eac195a1",
    "src/morphoacoustics/acoustics/__init__.py": "8a4f37d163767f40bedbcbb52310775c6c1d3467",
    "src/morphoacoustics/acoustics/backend.py": "92768d16c9f13274f2fdf37eeb0884d35882adaa",
    "src/morphoacoustics/acoustics/protocol.py": "9812980b517ae4398dda15bfda179fd89a620182",
    "src/morphoacoustics/acoustics/segmented_tube.py": "e51957e292b7f46a7ecb29b500ae054fbae7c1ed",
    "src/morphoacoustics/acoustics/uniform_tube.py": "8bceaf1426c2aec56eea91e2148cd402998516f2",
    "src/morphoacoustics/domain/__init__.py": "0d8803276fdf28c08db84f03c376d497f9f8fa49",
    "src/morphoacoustics/domain/creature.py": "94afb311ef59d04369f43b4b45c184770ca0ddf6",
    "src/morphoacoustics/domain/gesture.py": "782d3bdde829d0a3506beed490a78cc82dc13d0d",
    "src/morphoacoustics/domain/result.py": "3408f6f0ff2a745511e8705360e28204fc6e5ba1",
    "src/morphoacoustics/integration/__init__.py": "2de45bcad613f6c643906d7b8336863fd8e37b4e",
    "src/morphoacoustics/integration/body_presets.py": "1402393208fa4b1b154d6b18a20f9ca8dbddc1cd",
    "src/morphoacoustics/integration/shared_timeline.py": "a1ed908352fd7f9ed8f67bb251399b73f955a2f7",
    "src/morphoacoustics/physical/__init__.py": "7eb2eb01dab33256dd6b289c42a4545f6ba4a496",
    "src/morphoacoustics/physical/tract1d.py": "62f3ddf6d3cbf2e43072f9d8b2be6ee84f4c3ca7",
    "src/morphoacoustics/preparation/__init__.py": "26e992bba685d989861361120be6f64d38accb3e",
    "src/morphoacoustics/preparation/protocol.py": "72a6a536e5dd1800aac1328c3b84026bacad896e",
    "src/morphoacoustics/preparation/tract1d.py": "90860b19a6b181ba88ff3d4a01379c10ab23e226",
    "src/morphoacoustics/realization/__init__.py": "469760748767b788f051a50dc152d513cb704c58",
    "src/morphoacoustics/realization/protocol.py": "63f999fbda3ba0197ee585897e2253007731665a",
    "src/morphoacoustics/realization/tract1d.py": "87adb91ebe3ca2a3e2b36931f9d12d94c2ee7e0b",
    "src/morphoacoustics/simulation/__init__.py": "6d65e6e2eb2d4a02275073a607608c0736b77b92",
    "src/morphoacoustics/simulation/snapshot.py": "8c3da24a1fd40a82c95bbd2b38d9e3aa6a65f2a9",
}
EXP29_PATH = ROOT / "experiments" / "029_task_field_embodied_infeasibility" / "run.py"
EXP28_PATH = ROOT / "experiments" / "028_task_field_morphology_transfer" / "run.py"
EXP28_REFERENCE_PATH = ROOT / "experiments" / "028_task_field_morphology_transfer" / "frozen_reference.json"
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


def _git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def _verify_frozen_sources_before_import() -> None:
    """Check the frozen runtime source identity before dynamic experiment import.

    The Experiment 028 transitive manifest alone omits Experiment 029 imports
    from the domain and preparation packages. Verify the complete frozen
    morphoacoustics package inventory and each Git blob as an additional gate.
    This is a trusted-checkout consistency check, not a malicious-code sandbox.
    """
    package_root = ROOT / "src" / "morphoacoustics"
    actual_paths = {
        path.relative_to(ROOT).as_posix()
        for path in package_root.rglob("*.py")
        if path != package_root / "integration" / "limited_live.py"
    }
    if actual_paths != AUDITED_PACKAGE_GIT_BLOBS.keys():
        added = sorted(actual_paths - AUDITED_PACKAGE_GIT_BLOBS.keys())
        removed = sorted(AUDITED_PACKAGE_GIT_BLOBS.keys() - actual_paths)
        raise RuntimeError(
            f"audited package source inventory changed: added={added}, removed={removed}"
        )
    for relative, expected_blob in AUDITED_PACKAGE_GIT_BLOBS.items():
        if _git_blob_sha(ROOT / relative) != expected_blob:
            raise RuntimeError(f"audited package Git blob changed before import: {relative}")
    for path, expected in (
        (EXP29_PATH, AUDITED_EXP29_GIT_BLOB),
        (EXP28_PATH, AUDITED_EXP28_GIT_BLOB),
        (EXP28_REFERENCE_PATH, AUDITED_EXP28_REFERENCE_GIT_BLOB),
    ):
        if _git_blob_sha(path) != expected:
            raise RuntimeError(f"audited frozen Git blob changed before import: {path}")
    frozen = json.loads(EXP28_REFERENCE_PATH.read_text(encoding="utf-8"))
    manifest = frozen["implementation"]["files_sha256"]
    if not isinstance(manifest, dict) or not manifest:
        raise RuntimeError("audited source manifest invalid")
    for relative, expected_sha256 in manifest.items():
        if not isinstance(relative, str) or not isinstance(expected_sha256, str):
            raise RuntimeError("audited source manifest has invalid item")
        source_path = ROOT / relative
        # Relative paths come from a pinned trust root, not the user request.
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != expected_sha256:
            raise RuntimeError(f"transitive audited source changed before import: {relative}")


def _load_audited_experiment() -> ModuleType:
    """Refuse modified experiment sources *before* any experiment import."""
    _verify_frozen_sources_before_import()
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
    # Directory freshness applies even to INVALID/UNSUPPORTED results: an
    # existing directory may contain an earlier successful WAV or manifest.
    if output_dir.exists():
        raise FileExistsError(f"requires a new output directory: {output_dir}")
    rejected = validate(request)
    if rejected is not None:
        return rejected
    assert isinstance(request, dict)
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
    if feasibility.status is not exp.FeasibilityStatus.FEASIBLE:
        return _response(
            request, feasibility.status.value,
            feasibility.issues[0].code if feasibility.issues else "FEASIBILITY",
            "prepared body cannot realize the frozen task",
        )
    sources, _ = exp.EXP26.EXP13.build_sources()
    pressure_source = np.asarray(sources[SOURCE_ID].source, dtype=np.float64)
    result = exp.evaluate_condition(body, pressure_source, label="m_plus")
    if (
        result.feasibility.status is not exp.FeasibilityStatus.FEASIBLE
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
        if args.output_dir.exists():
            raise FileExistsError(f"requires a new output directory: {args.output_dir}")
        try:
            request = json.loads(args.request.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            result = _response(None, "INVALID", "REQUEST_JSON", f"invalid JSON/UTF-8: {exc}")
            result["provenance"]["request_sha256"] = None
        else:
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
