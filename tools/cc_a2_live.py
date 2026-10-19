"""CC-A2 bounded, source-checkout-only two-body physical performance adapter.

Only the audited Experiment 028 M0/M1 *axial geometry* intervention is exposed.
The frozen X2a live adapter and its source hash inventory are never changed.
This is a candidate integration, not a new phonetic or biomechanical validation.
"""
from __future__ import annotations

import hashlib
import importlib
import argparse
import csv
import io
import json
import math
import os
from pathlib import Path
import runpy
from typing import Any

import numpy as np
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from morphoacoustics.integration.body_presets import BodyPresetRegistry, make_body_preset
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "performance"
SEMANTICS = runpy.run_path(str(CONTRACT / "v1" / "semantic_validation.py"))
VERSION = "cc-a2-axial-live/1"
PRESETS = {"v3b-axial-M0": 0.010, "v3b-axial-M1": 0.011}
EXPECTED_PEAKS_HZ = {
    "v3b-axial-M0": (275.00, 2101.75),
    "v3b-axial-M1": (249.75, 1910.75),
}
SAMPLE_RATE = 48000
SAMPLES = 24000

# Git blob of adopted source at Core a7541877; the X2a module deliberately
# excludes its own bytes from its frozen transitive source inventory. CC-A2
# cannot trust source/WAV/receipt/publication helpers unless separately pinned.
FROZEN_LIMITED_LIVE_BLOB_SHA1 = "aa729fb644043b80056a000f9ed5d302fe39125a"


def _load_frozen_adapter() -> Any:
    source = ROOT / "src" / "morphoacoustics" / "integration" / "limited_live.py"
    raw = source.read_bytes()
    observed = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if observed != FROZEN_LIMITED_LIVE_BLOB_SHA1:
        raise RuntimeError("CC-A2 frozen limited_live dependency changed; no synthesis permitted")
    # Import only *after* exact source bytes match; this is a trusted checkout,
    # not a malicious-import sandbox. Existing Experiment028/029 transitive
    # source pin/oracles will be checked separately by the imported adapter.
    return importlib.import_module("morphoacoustics.integration.limited_live")


def schema_validator(name: str) -> Draft202012Validator:
    """Read canonical upstream v0+v1 schemas, never a Studio-side shadow schema."""
    resources = []
    for version, names in (
        ("v0", ("common", "character", "script", "direction", "performance-request", "performance-result")),
        ("v1", ("common", "performance-request", "performance-result")),
    ):
        for n in names:
            obj = json.loads((CONTRACT / version / (n + ".schema.json")).read_text("utf-8"))
            Draft202012Validator.check_schema(obj)
            resources.append((obj["$id"], Resource.from_contents(obj)))
    registry = Registry().with_resources(resources)
    schema = json.loads((CONTRACT / "v1" / (name + ".schema.json")).read_text("utf-8"))
    return Draft202012Validator(schema, registry=registry)


def prepared_registry(exp: Any) -> BodyPresetRegistry:
    """Prepare exact two frozen geometries, with honest new provenance."""
    m0 = exp.EXP26.EXP23.primary_geometry("a")
    m1 = exp.EXP28.with_section_length(
        m0, exp.EXP28.M1_SECTION_LENGTH_M, cavity_id=m0.cavity_id
    )
    a0 = np.asarray([section.area_m2 for section in m0.sections])
    a1 = np.asarray([section.area_m2 for section in m1.sections])
    if (
        len(m0.sections) != 16
        or not np.array_equal(a0, a1)
        or any(section.length_m != 0.010 for section in m0.sections)
        or any(section.length_m != 0.011 for section in m1.sections)
        or not math.isclose(m1.total_length_m / m0.total_length_m, 1.10, abs_tol=1e-12)
    ):
        raise RuntimeError("Experiment 028 frozen single-axis morphology intervention drift")
    presets = []
    for name, geom in (("v3b-axial-M0", m0), ("v3b-axial-M1", m1)):
        creature = exp.creature_for(cavity_id=geom.cavity_id, oral_reachable_end=0.75)
        prepared = prepare_tract1d(
            creature, geom,
            provenance=PreparationProvenance(
                source="experiment-028/cc-a2", model="frozen-v3b-axial-scale/v1",
                notes=("same-three-task-plan", "fixed-oral-shaper-reach-0.75",
                       "frozen-source-lf_fixed", "only-axial-section-length-varies",
                       f"preset={name}"),
            ),
        )
        presets.append(make_body_preset(preset_id=name, revision=1, prepared=prepared))
    return BodyPresetRegistry(tuple(presets))


def trace_bytes(exp: Any, start: Any) -> bytes:
    """Body-specific realized geometry and task activations; no inferred anatomy."""
    out = io.StringIO(newline="")
    keys = ["time_s", "sample_index", "task0", "task1", "task2",
            "total_length_m", "min_area_m2", "max_area_m2"]
    writer = csv.DictWriter(out, fieldnames=keys, lineterminator="\n")
    writer.writeheader()
    for i in range(51):
        t = i / 100
        acts = exp.EXP27.task_activations_at_time(
            t, control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S
        )
        geometry = exp.EXP27.task_geometry_for_time(
            start, t, control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,
            cavity_id=start.cavity_id + "-cc-a2",
        )
        areas = [s.area_m2 for s in geometry.sections]
        writer.writerow({
            "time_s": f"{t:.2f}", "sample_index": round(t * SAMPLE_RATE),
            "task0": f"{acts[0]:.17g}", "task1": f"{acts[1]:.17g}",
            "task2": f"{acts[2]:.17g}", "total_length_m": f"{geometry.total_length_m:.17g}",
            "min_area_m2": f"{min(areas):.17g}",
            "max_area_m2": f"{max(areas):.17g}",
        })
    return out.getvalue().encode("utf-8")


def diagnostics(code: str, message: str) -> list[dict[str, str]]:
    return [{"code": code, "severity": "warning", "message": message}]


def make_result(request: dict[str, Any], resolution: Any, input_digest: str,
                backend_id: str, *, outcome: str, artifacts: list[dict[str, Any]] | None = None,
                timeline: list[dict[str, Any]] | None = None,
                issues: list[dict[str, str]] | None = None) -> dict[str, Any]:
    rid = request["request_id"]
    result = {
        "schema_version": "performance-contract/v1",
        "performance_id": "performance_" + rid,
        "request_id": rid, "take_id": "take_" + rid,
        "job_status": "SUCCEEDED", "realization_outcome": outcome,
        "artifacts": artifacts or [], "diagnostics": issues or [],
        "timeline": timeline or [],
        "embodiment": SEMANTICS["v1_resolved_embodiment"](resolution),
        "provenance": {
            "backend": backend_id, "backend_version": VERSION,
            "contract_version": "performance-contract/v1",
            "seed": request["seed"], "input_digest": input_digest,
            "input_digest_algorithm": "sha256-canonical-json-v1",
        },
    }
    schema_validator("performance-result").validate(result)
    SEMANTICS["verify_v1_result_pair"](
        request, result, resolution, backend_id=backend_id, backend_version=VERSION
    )
    return result


def perform(request: object, output_dir: Path) -> dict[str, Any]:
    """Never publish cached or mislabeled audio; only two bounded physical bodies."""
    if os.path.lexists(output_dir):
        raise FileExistsError("Take output directory must not exist")
    schema_validator("performance-request").validate(request)
    assert isinstance(request, dict)
    frozen = _load_frozen_adapter()
    exp = frozen._load_audited_experiment()  # frozen source hashes + both Wolfram preflights
    if np.__version__ != exp.AUDITED_NUMPY_VERSION:
        raise RuntimeError("audited NumPy version changed")
    registry = prepared_registry(exp)
    backend_id = exp.TRACT1D_BACKEND_ID
    resolution, input_digest = SEMANTICS["resolve_v1_binding"](
        request, registry, required_backend_id=backend_id, backend_version=VERSION
    )
    if resolution.status.value != "BOUND":
        return make_result(request, resolution, input_digest, backend_id,
                           outcome="UNSUPPORTED",
                           issues=diagnostics(resolution.physical.issues[0].code,
                                              resolution.physical.issues[0].message))
    segments = request["script"]["segments"]
    direction = request["direction"]
    if (len(segments) != 1
        or segments[0]["speaker_character_id"] != request["character"]["character_id"]
        or segments[0]["text"] != "あい" or request["seed"] != 0
        or direction.get("controls")
        or direction.get("segment_overrides")
        or direction.get("note", "").strip()
        or any(c not in {"audio", "timeline", "diagnostics", "physical_trace"}
               for c in request.get("requested_capabilities", []))):
        return make_result(request, resolution, input_digest, backend_id,
                           outcome="UNSUPPORTED",
                           issues=diagnostics("CC_A2_FIXTURE_ONLY",
                               "Only one frozen あい segment, no Direction, seed 0 is supported"))
    body = resolution.physical.preset.prepared
    feas = exp.capability_report(body)
    if feas.status is not exp.FeasibilityStatus.FEASIBLE:
        return make_result(
            request, resolution, input_digest, backend_id,
            outcome=feas.status.value,
            issues=diagnostics(feas.issues[0].code, feas.issues[0].message)
                   if feas.issues else diagnostics("FEASIBILITY", "Cannot realize task"),
        )
    sources, _ = exp.EXP26.EXP13.build_sources()
    source = np.asarray(sources[frozen.SOURCE_ID].source, dtype=np.float64)
    result = exp.evaluate_condition(body, source, label="cc_a2_" + body.creature.name)
    if (result.feasibility.status is not exp.FeasibilityStatus.FEASIBLE
        or result.waveform is None or result.endpoint is None
        or result.acoustic_call_count != 102):
        raise RuntimeError("CC-A2 causal solver failed its expected 102 evaluations")
    pressure = np.asarray(result.waveform, dtype=np.float64)
    if pressure.shape != (SAMPLES,) or not np.all(np.isfinite(pressure)):
        raise RuntimeError("nonfinite / unexpected acoustic pressure")
    name = request["embodiment"]["preset_id"]
    peaks = exp.EXP26.peak_array(result.endpoint, count=2)
    if not np.allclose(peaks, EXPECTED_PEAKS_HZ[name], rtol=0.0, atol=0.25):
        raise RuntimeError("independent Experiment028 Wolfram endpoint peaks differ")
    quantized = exp.quantized_waveform_sha256(pressure)
    if name == "v3b-axial-M0" and quantized != exp.AUDITED_QUANTIZED_WAVEFORM_SHA256:
        raise RuntimeError("M0 no longer reproduces adopted Experiment029 pressure oracle")
    raw_out = io.BytesIO()
    np.save(raw_out, pressure, allow_pickle=False)
    payloads = [
        ("audio", "audio.wav", "audio/wav", frozen._wav_bytes(pressure)),
        ("raw-pressure", "raw_pressure_pa.npy", "application/x-npy", raw_out.getvalue()),
        ("dynamic-trace", "physical_trace.csv", "text/csv", trace_bytes(exp, body.rest_state)),
    ]
    receipt = {
        "claim_limit": "Experiment028 exact axial M0/M1, task-level /a/-to-/i/-like only",
        "body": {"preset_id": name, "revision": 1,
                 "length_m": body.rest_state.total_length_m,
                 "section_length_m": PRESETS[name],
                 "preparation_digest": resolution.snapshot.preparation_digest},
        "source": {"id": frozen.SOURCE_ID, "f0_hz": 100},
        "task_plan_sha256": exp.sha256_json(exp.task_plan_payload()),
        "endpoint_peak_hz": [float(x) for x in peaks],
        "independent_oracle": "Experiment028 frozen Wolfram v3b peaks at 0.25Hz",
        "raw_pressure": {"samples": SAMPLES, "sample_rate_hz": SAMPLE_RATE,
                         "quantization_pa": 1e-9, "quantized_sha256": quantized},
        "acoustic_calls": result.acoustic_call_count,
        "numpy_version": np.__version__,
        "playback_peak_normalization": frozen.LISTENING_PEAK,
    }
    payloads.append(("physical-receipt", "physical_receipt.json", "application/json",
                     frozen.canonical_bytes(receipt) + b"\n"))
    artifacts = [
        {"kind": kind, "ref": filename, "media_type": media,
         "segment_id": segments[0]["segment_id"]} for kind, filename, media, _ in payloads
    ]
    answer = make_result(
        request, resolution, input_digest, backend_id, outcome="FEASIBLE",
        artifacts=artifacts,
        timeline=[{"segment_id": segments[0]["segment_id"],
                   "start_seconds": 0.0, "end_seconds": 0.5}],
        issues=[{"code": "CC_A2_LIMITED", "severity": "info",
                 "message": "Computational axial-body comparison; human phonetic identity unverified"}],
    )
    if not output_dir.parent.is_dir():
        raise FileNotFoundError("output parent must exist")
    # Immutable completion-marker publication is reused from X2a.
    frozen._publish_new_take(output_dir, tuple(payloads), answer)
    return answer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        raw = json.loads(args.request.read_text(encoding="utf-8"))
        result = perform(raw, args.output_dir)
    except Exception as exc:
        # Nonzero process exit carries a *separate* versioned transport error;
        # never pretend that missing request identity is a v1 PerformanceResult.
        result = {"schema_version": "cc-a2-transport-error/v1",
                  "error": {"code": "CC_A2_EXECUTION_FAILED", "message": str(exc)}}
    print(json.dumps(result, ensure_ascii=False))
    if result.get("schema_version") == "cc-a2-transport-error/v1":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
