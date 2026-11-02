"""OD-3 bounded body revision × temporal coordination physical performance.

Research-local only. Frozen upstream Exp027/029, OD-2, source and acoustic solver
are not modified. All WAVs are derivatives of fresh, full native Pa calculations.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import runpy
import shutil
import tempfile
from typing import Any

import numpy as np

from morphoacoustics.integration.body_presets import make_body_preset
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d

ROOT = Path(__file__).resolve().parents[2]
OD2 = runpy.run_path(str(ROOT / "tools" / "od2_body_cli.py"))
SCHEMA = "od3.body-performance.v0-research"
SCHEDULE_SCHEMA = "od3.coordination-3.v0-research"
SELECTED = ((4, "1.00"), (4, "1.10"), (8, "0.90"))
SCHEDULES = ("G0", "G1")
PROBES_S = (0.0, 0.20, 0.27, 0.35, 0.40, 0.50)
DELAY_S = 0.020
SAMPLE_RATE_HZ = 48000
SAMPLES = 24000
REPLAY_TOL = 1e-12
GEOMETRY_TOL = 1e-10


class OD3Error(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def require(ok: bool, code: str, detail: str) -> None:
    if not ok:
        raise OD3Error(code, detail)


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def read_json(path: Path) -> object:
    def no_duplicates(items: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in items:
            require(key not in out, "DUPLICATE_JSON", "duplicate key: " + key)
            out[key] = value
        return out

    return json.loads(path.read_text("utf-8"), object_pairs_hook=no_duplicates,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          OD3Error("INVALID_JSON", "nonfinite JSON token " + value)))


def validate_selection(center: object, ratio: object) -> tuple[int, str]:
    require(type(center) is int and type(ratio) is str,
            "INVALID_INPUT", "expected integer center and canonical string ratio")
    require((center, ratio) in SELECTED, "UNSUPPORTED_BODY",
            "OD-3 only supports audited M0 alias, c4/r1.10, c8/r0.90")
    return center, ratio


def validate_schedule(name: object) -> str:
    require(type(name) is str and name in SCHEDULES,
            "UNSUPPORTED_SCHEDULE", "only G0 and G1 are supported")
    return name


def _context() -> tuple[Any, Any, Any]:
    runner, exp, parent, _ = OD2["_load_context"]()
    require(np.__version__ == "2.4.6",
            "NUMERICAL_ENVIRONMENT", "requires audited NumPy 2.4.6")
    return runner, exp, parent


def _receipt(runner: Any, exp: Any, parent: Any,
             center: int, ratio: str) -> dict[str, Any]:
    center, ratio = validate_selection(center, ratio)
    return OD2["_receipt"](runner, exp, parent, center, ratio)


def _prepared(parent: Any, receipt: dict[str, Any]) -> Any:
    if receipt["null_alias"]:
        require(receipt["preparation_digest"] == parent.preparation_digest,
                "REVISION_MISMATCH", "null body does not bind exact parent")
        return parent.prepared
    geom = Tract1DGeometry(
        cavity_id=parent.prepared.rest_state.cavity_id,
        sections=tuple(
            TubeSection(length_m=float.fromhex(l), area_m2=float.fromhex(a))
            for l, a in zip(receipt["lengths_hex"],
                            receipt["rest_areas_hex"], strict=True)
        ),
    )
    prepared = prepare_tract1d(
        parent.prepared.creature, geom,
        provenance=PreparationProvenance(
            source="od2-local-revision-study",
            model=OD2["FAMILY"],
            notes=(f"parent={parent.preparation_digest}",
                   f"center={receipt['center_index']}",
                   f"ratio={receipt['rest_area_ratio']}"),
        ),
    )
    selected = make_body_preset(preset_id=receipt["preset_id"],
                                revision=receipt["preset_revision"],
                                prepared=prepared)
    require(selected.preparation_digest == receipt["preparation_digest"],
            "REVISION_MISMATCH", "physical preparation differs from OD-2")
    return prepared


def _tasks(exp: Any, schedule: str) -> tuple[Any, ...]:
    validate_schedule(schedule)
    base = exp.EXP27.TASKS
    if schedule == "G0":
        return tuple(base)
    delayed: list[Any] = []
    for i, task in enumerate(base):
        if i != 1:
            delayed.append(task)
            continue
        delayed.append(exp.EXP27.CandidateTask(
            task=task.task, location=task.location, degree=task.degree,
            onset_s=task.onset_s + DELAY_S,
            offset_s=task.offset_s + DELAY_S,
        ))
    require(len(delayed) == 3, "TASK_LAYOUT", "requires three inherited tasks")
    return tuple(delayed)


def _activation(exp: Any, task: Any, time_s: float) -> float:
    return exp.EXP27.task_activation_at_time(
        task, time_s, control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S
    )


def _geometry(exp: Any, start: Tract1DGeometry, tasks: tuple[Any, ...],
              time_s: float) -> tuple[Tract1DGeometry, tuple[float, ...]]:
    alpha = tuple(_activation(exp, task, time_s) for task in tasks)
    geometry = exp.EXP27.realize_task_geometry_from_activations(
        start, alpha, cavity_id=start.cavity_id
    )
    base = np.array([section.area_m2 for section in start.sections])
    actual = np.array([section.area_m2 for section in geometry.sections])
    predicted_log_delta = sum(
        (a * exp.EXP27.task_log_diameter_delta_for(task, len(base))
         for a, task in zip(alpha, tasks, strict=True)),
        start=np.zeros(len(base)),
    )
    residual = float(np.max(np.abs(
        np.log(actual / base) - 2.0 * predicted_log_delta
    )))
    require(math.isfinite(residual) and residual <= GEOMETRY_TOL,
            "GEOMETRY_MISMATCH", "actual geometry violates inherited log-area law")
    require(np.isfinite(actual).all() and (actual > 0.0).all(),
            "INVALID_GEOMETRY", "nonpositive or nonfinite 1D area")
    return geometry, alpha


def _probe(exp: Any, start: Tract1DGeometry, tasks: tuple[Any, ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for time_s in PROBES_S:
        geometry, alpha = _geometry(exp, start, tasks, time_s)
        rows.append({
            "time_s": time_s,
            "activation": list(alpha),
            "areas_hex": [s.area_m2.hex() for s in geometry.sections],
            "volume_m3": math.fsum(s.area_m2 * s.length_m for s in geometry.sections),
        })
    return rows


def _render(exp: Any, prepared: Any, source: np.ndarray,
            schedule: str) -> tuple[np.ndarray, int, list[dict[str, Any]]]:
    feas = exp.capability_report(prepared)
    require(feas.status is exp.FeasibilityStatus.FEASIBLE, feas.status.value,
            "selected body cannot physically realize existing task goals")
    tasks = _tasks(exp, schedule)
    start = prepared.rest_state
    probe = _probe(exp, start, tasks)
    counter = exp.CountingTransfer()

    def transfer_for_time(center_s: float, frequencies_hz: np.ndarray) -> np.ndarray:
        state, _ = _geometry(exp, start, tasks, center_s)
        return counter.evaluate(state, frequencies_hz)

    raw = np.asarray(exp.EXP26.EXP12.frame_render(
        np.asarray(source, dtype=np.float64),
        transfer_for_time,
        hop_size=exp.EXP27.PRIMARY_HOP_SIZE,
        edge_mode="preroll_edge",
    ), dtype=np.float64)
    require(raw.shape == (SAMPLES,) and np.isfinite(raw).all(),
            "INVALID_PRESSURE", "model produced nonfinite/unexpected raw Pa")
    require(counter.call_count == 102, "ACOUSTIC_CALL_COUNT",
            "unexpected physical transfer evaluations")
    if schedule == "G0":
        inherited = exp.evaluate_condition(prepared, source, label="od3-G0-regression")
        require(inherited.feasibility.status is exp.FeasibilityStatus.FEASIBLE
                and inherited.waveform is not None
                and inherited.acoustic_call_count == counter.call_count,
                "G0_REGRESSION", "inherited acoustic reference unavailable")
        reference = np.asarray(inherited.waveform, dtype=np.float64)
        drift = float(np.linalg.norm(raw - reference) / np.linalg.norm(reference))
        require(math.isfinite(drift) and drift <= REPLAY_TOL,
                "G0_REGRESSION", "new schedule path changes original OD-2 physics")
    return raw, counter.call_count, probe


def _source(exp: Any, runner: Any) -> tuple[np.ndarray, str]:
    sources, _ = exp.EXP26.EXP13.build_sources()
    source = np.asarray(sources["lf_fixed"].source, dtype=np.float64)
    require(source.shape == (SAMPLES,) and np.isfinite(source).all(),
            "SOURCE_MISMATCH", "frozen source differs from experiment")
    current_sha = runner["sha_f64"](source)
    # IEEE-754 source bits may differ across CPU/library environments even at
    # pinned NumPy; preserve exact identity INSIDE the execution. CI independently
    # compares this SHA against newly generated unmodified OD-2 source bytes in
    # the SAME job, while old OD-2 quantized model regression remains mandatory.
    again, _ = exp.EXP26.EXP13.build_sources()
    require(runner["sha_f64"](np.asarray(again["lf_fixed"].source,
                                        dtype=np.float64)) == current_sha,
            "SOURCE_MISMATCH", "LF100 generator not deterministic in one environment")
    return source, current_sha


def _cases(kind: str, center: int | None = None,
           ratio: str | None = None) -> tuple[tuple[int, str], ...]:
    if kind == "suite":
        return SELECTED
    require(kind == "pair", "INVALID_MODE", "unknown archive mode")
    return (validate_selection(center, ratio),)


def _generate(kind: str, choices: tuple[tuple[int, str], ...],
              runner: Any, exp: Any, parent: Any) -> tuple[
                  dict[str, Any], dict[str, np.ndarray], dict[str, Any]]:
    source, source_sha = _source(exp, runner)
    conditions: list[dict[str, Any]] = []
    bodies: list[dict[str, Any]] = []
    waveforms: dict[str, np.ndarray] = {}
    by_body: dict[str, dict[str, Any]] = {}
    for center, ratio in choices:
        receipt = _receipt(runner, exp, parent, center, ratio)
        prepared = _prepared(parent, receipt)
        body_key = f"c{center:02d}_r{int(round(float(ratio)*100)):03d}"
        bodies.append(receipt)
        by_body[body_key] = {}
        for schedule in SCHEDULES:
            raw, calls, probe = _render(exp, prepared, source, schedule)
            name = f"{body_key}_{schedule}"
            row = {
                "id": name,
                "revision_id": receipt["revision_id"],
                "preparation_digest": receipt["preparation_digest"],
                "schedule_id": schedule,
                "acoustic_calls": calls,
                "raw_sha256_le_f64": runner["sha_f64"](raw),
                "raw_rms_pa": float(np.sqrt(np.mean(raw * raw))),
                "raw_peak_pa": float(np.max(np.abs(raw))),
                "probes": probe,
            }
            conditions.append(row)
            by_body[body_key][schedule] = row
            waveforms[name] = raw

    metrics = []
    for body_key, rows in by_body.items():
        g0, g1 = rows["G0"], rows["G1"]
        a0, a1 = waveforms[g0["id"]], waveforms[g1["id"]]
        denominator = float(np.linalg.norm(a0))
        require(denominator > 0, "EMPTY_PRESSURE", "G0 pressure cannot be silent")
        delta = float(np.linalg.norm(a1 - a0) / denominator)
        probe0, probe1 = g0["probes"], g1["probes"]
        for index in (0, 4, 5):
            require(probe0[index]["activation"] == probe1[index]["activation"]
                    and probe0[index]["areas_hex"] == probe1[index]["areas_hex"],
                    "SCHEDULE_NULL_FAILED", "unchanged endpoint/pre-onset must match")
        require(probe0[1]["activation"][1] != probe1[1]["activation"][1],
                "SCHEDULE_INTERVENTION_MISSING", "T1 activation at .20s not changed")
        require(all(probe0[1]["activation"][j] == probe1[1]["activation"][j]
                    for j in (0, 2)), "SCHEDULE_LEAK", "T0/T2 activation changed")
        areas0 = np.array([float.fromhex(v) for v in probe0[1]["areas_hex"]])
        areas1 = np.array([float.fromhex(v) for v in probe1[1]["areas_hex"]])
        log_diff = float(np.max(np.abs(np.log(areas1 / areas0))))
        require(log_diff > 1e-9 and math.isfinite(delta) and delta > 1e-8,
                "NO_CAUSAL_EFFECT", "timing intervention did not reach model acoustics")
        metrics.append({
            "body": body_key,
            "G1_vs_G0_raw_pa_relative_l2": delta,
            "G1_vs_G0_log_area_max_at_020": log_diff,
        })

    # Descriptive two-factor contrast. The log-area body × schedule
    # interaction is predicted to be zero by the chosen separable model;
    # acoustic interaction need not be zero because transmission is nonlinear.
    interactions = []
    if "c04_r100" in by_body and len(by_body) > 1:
        reference = by_body["c04_r100"]
        ref_g0 = waveforms[reference["G0"]["id"]]
        ref_g1 = waveforms[reference["G1"]["id"]]
        ref_norm = float(np.linalg.norm(ref_g0))
        for body_key, rows in by_body.items():
            if body_key == "c04_r100":
                continue
            b0 = waveforms[rows["G0"]["id"]]
            b1 = waveforms[rows["G1"]["id"]]
            contrast = (b1 - b0) - (ref_g1 - ref_g0)
            probe_b0 = rows["G0"]["probes"][1]["areas_hex"]
            probe_b1 = rows["G1"]["probes"][1]["areas_hex"]
            probe_r0 = reference["G0"]["probes"][1]["areas_hex"]
            probe_r1 = reference["G1"]["probes"][1]["areas_hex"]
            log_area_interaction = float(np.max(np.abs(
                np.log(np.array([float.fromhex(x) for x in probe_b1])
                       / np.array([float.fromhex(x) for x in probe_b0]))
                - np.log(np.array([float.fromhex(x) for x in probe_r1])
                         / np.array([float.fromhex(x) for x in probe_r0]))
            )))
            require(log_area_interaction <= GEOMETRY_TOL, "LOG_AREA_INTERACTION",
                    "rest-body change and task timing must be separable in log area")
            interactions.append({
                "body": body_key,
                "G0_body_vs_M0_relative_l2": float(np.linalg.norm(b0 - ref_g0) / ref_norm),
                "body_x_schedule_raw_pa_relative_l2": float(np.linalg.norm(contrast) / ref_norm),
                "body_x_schedule_log_area_linf_at_020": log_area_interaction,
            })

    decision = {
        "schema": SCHEMA,
        "status": "GO_LIMITED_OD3_RESEARCH_EXECUTION",
        "kind": kind,
        "model": "inherited-1d-Exp027-task-Exp029-acoustics",
        "source_id": "lf_fixed",
        "source_sha256_le_f64": source_sha,
        "task_plan_sha256": exp.sha256_json(exp.task_plan_payload()),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "samples": SAMPLES,
        "observer": "Exp009-1D-resistive-outlet-monopole-0.20m-Pa-proxy",
        "schedule_schema": SCHEDULE_SCHEMA,
        "body_receipts": bodies,
        "conditions": conditions,
        "metrics": metrics,
        "interactions": interactions,
        "limitations": [
            "not self-oscillating vocal-fold source",
            "not calibrated ear-pressure or absolute listener SPL",
            "not biologically actuated organ material or dynamic FSI",
            "not natural speech, phonetic validation or Studio Take",
        ],
    }
    peak = max(float(np.max(np.abs(x))) for x in waveforms.values())
    require(math.isfinite(peak) and peak > 0, "INVALID_GAIN", "no finite raw pressure")
    gain = float(.90 / peak)
    decision["common_preview_gain"] = gain
    return decision, waveforms, by_body


def _complete_files(physical: Path, decision: dict[str, Any],
                    waves: dict[str, np.ndarray], runner: Any) -> dict[str, str]:
    artifact_sha: dict[str, str] = {}
    for name, raw in waves.items():
        raw_path = physical / (name + ".npy")
        wav_path = physical / (name + ".wav")
        with raw_path.open("wb") as out:
            np.save(out, raw, allow_pickle=False)
        wav_path.write_bytes(runner["wav_bytes"](raw, decision["common_preview_gain"]))
        artifact_sha[raw_path.name] = sha(raw_path.read_bytes())
        artifact_sha[wav_path.name] = sha(wav_path.read_bytes())
    return artifact_sha


def _verify_files(output: Path, runner: Any, exp: Any, parent: Any) -> dict[str, Any]:
    require(output.is_dir() and not output.is_symlink(),
            "INVALID_ARCHIVE", "expected non-symlink archive directory")
    physical = output / "cases"
    require(physical.is_dir() and not physical.is_symlink(),
            "INVALID_ARCHIVE", "missing cases folder")
    marker = output / "manifest.json"
    decision_path = output / "decision.json"
    for path in (marker, decision_path):
        require(path.is_file() and not path.is_symlink(),
                "INVALID_ARCHIVE", "missing manifest/decision")
    manifest = read_json(marker)
    saved = read_json(decision_path)
    require(type(manifest) is dict and type(saved) is dict,
            "INVALID_ARCHIVE", "expected strict objects")
    require(set(manifest) == {"schema", "kind", "selection",
                              "decision_sha256", "artifact_sha256"},
            "INVALID_ARCHIVE", "unknown or missing manifest fields")
    require(manifest.get("schema") == SCHEMA
            and saved.get("schema") == SCHEMA
            and manifest.get("decision_sha256") == sha(decision_path.read_bytes()),
            "ARCHIVE_TAMPER", "decision receipt does not match bytes")
    kind = manifest.get("kind")
    if kind == "suite":
        require(manifest["selection"] is None,
                "INVALID_ARCHIVE", "suite must not select a different body")
        choices = _cases("suite")
    elif kind == "pair":
        selected = manifest.get("selection")
        require(type(selected) is dict and set(selected) == {"center", "ratio"},
                "INVALID_ARCHIVE", "pair selection missing/changed")
        choices = _cases("pair", selected["center"], selected["ratio"])
    else:
        raise OD3Error("INVALID_ARCHIVE", "unknown archive kind")
    expected, actual_waveforms, _ = _generate(kind, choices, runner, exp, parent)
    require(saved == expected,
            "PHYSICAL_REPLAY_MISMATCH",
            "fresh physics/receipts/geometry differ from recorded decision")
    expected_files = {name + suffix for name in actual_waveforms
                      for suffix in (".npy", ".wav")}
    recorded_files = manifest.get("artifact_sha256")
    require(type(recorded_files) is dict
            and set(recorded_files) == expected_files
            and {p.name for p in physical.iterdir()} == expected_files,
            "INVALID_ARCHIVE", "missing, extra or renamed case artifact")
    for name, raw in actual_waveforms.items():
        raw_path = physical / (name + ".npy")
        wav_path = physical / (name + ".wav")
        for file_path in (raw_path, wav_path):
            require(file_path.is_file() and not file_path.is_symlink(),
                    "INVALID_ARCHIVE", "artifact path absent/symlink")
            require(recorded_files[file_path.name] == sha(file_path.read_bytes()),
                    "ARTIFACT_TAMPER", "artifact digest changed")
        restored = np.load(raw_path, allow_pickle=False)
        require(restored.shape == (SAMPLES,) and np.isfinite(restored).all()
                and restored.dtype == np.dtype("<f8"),
                "INVALID_PRESSURE", "saved pressure must be finite native f64 Pa")
        matching = next((row for row in expected["conditions"] if row["id"] == name), None)
        require(matching is not None and runner["sha_f64"](restored) ==
                matching["raw_sha256_le_f64"], "RAW_PRESSURE_HASH_MISMATCH",
                "saved Pa samples do not match the model-authoritative raw SHA receipt")
        floor = float(np.linalg.norm(restored - raw) / np.linalg.norm(raw))
        require(math.isfinite(floor) and floor <= REPLAY_TOL,
                "PHYSICAL_REPLAY_MISMATCH", "saved Pa not reproduced from exact body/schedule")
        require(wav_path.read_bytes() == runner["wav_bytes"](
            raw, expected["common_preview_gain"]),
            "WAV_NOT_PHYSICAL", "preview not the one declared common-gain physics derivative")
    require(set(p.name for p in output.iterdir()) ==
            {"manifest.json", "decision.json", "cases"},
            "INVALID_ARCHIVE", "unexpected top-level files")
    return {
        "schema": SCHEMA,
        "status": "GO_LIMITED_OD3_RESEARCH_EXECUTION",
        "archive_kind": kind,
        "verified_bodies": len(choices),
        "verified_new_physical_cases": len(actual_waveforms),
        "timing_effect_l2": [row["G1_vs_G0_raw_pa_relative_l2"]
                             for row in expected["metrics"]],
        "timing_log_area_at_020": [row["G1_vs_G0_log_area_max_at_020"]
                                  for row in expected["metrics"]],
        "body_motor_interactions": expected["interactions"],
        "source_sha256_le_f64": expected["source_sha256_le_f64"],
    }


def verify_archive(output: Path) -> dict[str, Any]:
    runner, exp, parent = _context()
    return _verify_files(output, runner, exp, parent)


def perform_archive(output: Path, *, kind: str = "suite",
                    center: int | None = None, ratio: str | None = None) -> dict[str, Any]:
    require(not os.path.lexists(output),
            "OUTPUT_EXISTS", "immutable research archive must not be overwritten")
    choices = _cases(kind, center, ratio)
    runner, exp, parent = _context()
    decision, waves, _ = _generate(kind, choices, runner, exp, parent)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="od3-stage-", dir=output.parent))
    try:
        cases = stage / "cases"
        cases.mkdir()
        hashes = _complete_files(cases, decision, waves, runner)
        (stage / "decision.json").write_bytes(canonical(decision))
        receipt: dict[str, Any] = {
            "schema": SCHEMA,
            "kind": kind,
            "selection": ({"center": center, "ratio": ratio} if kind == "pair" else None),
            "decision_sha256": sha((stage / "decision.json").read_bytes()),
            "artifact_sha256": hashes,
        }
        (stage / "manifest.json").write_bytes(canonical(receipt))
        verified = _verify_files(stage, runner, exp, parent)
        os.rename(stage, output)
        return verified
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main() -> None:
    parser = argparse.ArgumentParser(description="OD-3 local real-physics body performance")
    parser.add_argument("operation", choices=("inspect", "perform-suite",
                                               "perform-pair", "verify"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--center", type=int)
    parser.add_argument("--ratio", type=str)
    args = parser.parse_args()
    try:
        if args.operation == "inspect":
            runner, exp, parent = _context()
            report: dict[str, Any] = {
                "schema": SCHEMA, "status": "RESEARCH_ONLY",
                "bodies": [{"center": c, "ratio": r,
                            "revision_id": _receipt(runner, exp, parent, c, r)["revision_id"]}
                           for c, r in SELECTED],
                "schedules": list(SCHEDULES),
                "source": "lf_fixed",
                "observer": "Exp009-0.20m-monopole-proxy",
            }
        else:
            require(args.output_dir is not None, "INVALID_INPUT", "--output-dir required")
            if args.operation == "perform-pair":
                report = perform_archive(args.output_dir, kind="pair",
                                         center=args.center, ratio=args.ratio)
            elif args.operation == "perform-suite":
                require(args.center is None and args.ratio is None,
                        "INVALID_INPUT", "suite does not accept a selected body")
                report = perform_archive(args.output_dir)
            else:
                require(args.center is None and args.ratio is None,
                        "INVALID_INPUT", "verify accepts only exact archive directory")
                report = verify_archive(args.output_dir)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False))
    except (OD3Error, ValueError, RuntimeError, FileExistsError) as exc:
        code = exc.code if isinstance(exc, OD3Error) else "CORE_REFUSED"
        print(json.dumps({"schema": SCHEMA, "status": "REFUSED",
                          "code": code, "message": str(exc)}, ensure_ascii=False))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
