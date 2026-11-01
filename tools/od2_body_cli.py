"""OD-2 opt-in, source-pinned 1D body revision/replay adapter.

Research implementation only. No new mutable registry, general OrganGraph engine,
public Core ABI, biological phonator, Studio Take, or waveform editing.
"""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
import math
import os
from pathlib import Path
import runpy
import shutil
import tempfile
from typing import Any

import numpy as np

from morphoacoustics.integration.body_presets import (
    BodyPresetRegistry, CharacterBodyBinding, make_body_preset,
)
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "od2.local.revision-replay.v0-research"
FAMILY = "tract1d.local-log-area-5.v1"
IDENTITY_ALGORITHM = "sha256/od2-hexfloat-canonical-json-v1"
PARENT_ID = "v3b-axial-M0"
PARENT_REVISION = 1
RATIOS = {"0.90": .90, "1.00": 1.00, "1.10": 1.10}
CENTERS = (4, 8)
REF_L2 = {
    (4, "0.90"): .05627127292070631,
    (4, "1.10"): .05680526299910064,
    (8, "0.90"): .02659999178612523,
    (8, "1.10"): .027079007843954235,
}
PINS = {
    "experiments/od1_local_shape/run.py": "5ef1c4605a5a0e5c2490aa3e8ec79a7c23a0aaea",
    "experiments/od1_local_shape/oracle.py": "19152cf9a6a9a70b0cf251325ddacdcec1853317",
    "src/morphoacoustics/integration/body_presets.py": "1402393208fa4b1b154d6b18a20f9ca8dbddc1cd",
    "tools/cc_a2_live.py": "dd90ab5e83082c0da1b2f527288f7154bdd38aae",
}
SAMPLE_RATE_HZ = 48000
SAMPLES = 24000


class RevisionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _expect(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise RevisionError(code, message)


def canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _blob(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_pins() -> None:
    for path, expected in PINS.items():
        source = ROOT / path
        _expect(source.is_file() and _blob(source.read_bytes()) == expected,
                "SOURCE_DRIFT", f"audited source changed: {path}")


def _require_case(center: object, ratio: object) -> tuple[int, str]:
    _expect(type(center) is int and center in CENTERS,
            "UNSUPPORTED_CENTER", "only zero-based centers 4 or 8")
    _expect(type(ratio) is str and ratio in RATIOS,
            "UNSUPPORTED_RATIO", "only canonical ratio strings 0.90/1.00/1.10")
    return center, ratio


def _load_context() -> tuple[Any, Any, Any, BodyPresetRegistry]:
    verify_pins()
    runner = runpy.run_path(str(ROOT / "experiments/od1_local_shape/run.py"))
    cc_a2 = runpy.run_path(str(ROOT / "tools/cc_a2_live.py"))
    frozen = cc_a2["_load_frozen_adapter"]()
    exp = frozen._load_audited_experiment()
    _expect(np.__version__ == exp.AUDITED_NUMPY_VERSION,
            "NUMERICAL_ENVIRONMENT", "audited NumPy version differs")
    parents = cc_a2["prepared_registry"](exp)
    binding = parents.resolve(
        CharacterBodyBinding("od2-character", PARENT_ID, PARENT_REVISION),
        required_backend_id=exp.TRACT1D_BACKEND_ID,
    )
    _expect(binding.is_bound and binding.preset is not None,
            "MISSING_PRESET", "audited M0 body not available")
    return runner, exp, binding.preset, parents


def _receipt(runner: Any, exp: Any, parent: Any,
             center: int, ratio: str) -> dict[str, Any]:
    center, ratio = _require_case(center, ratio)
    base = parent.prepared.rest_state
    _expect(len(base.sections) == 16
            and all(s.length_m == .01 for s in base.sections),
            "UNSUPPORTED_BACKEND", "not the audited 16x10mm M0")
    _expect(parent.preset_id == PARENT_ID and parent.revision == PARENT_REVISION,
            "REVISION_MISMATCH", "unexpected parent revision")
    _expect(parent.preparation_digest.startswith("sha256:"),
            "REVISION_MISMATCH", "missing prepared parent digest")
    actual = runner["edit_geometry"](base, center, RATIOS[ratio])
    weights = runner["weights"](center)
    ref = np.asarray([s.area_m2 for s in base.sections], dtype=np.float64)
    area = np.asarray([s.area_m2 for s in actual.sections], dtype=np.float64)
    residual = float(np.max(np.abs(
        np.log(area / ref) - math.log(RATIOS[ratio]) * np.array(weights)
    )))
    _expect(residual <= 1e-12 and np.isfinite(area).all(),
            "GEOMETRY_MISMATCH", "shape fails cellwise log-area law")
    _expect(all(s.length_m == b.length_m for s, b in zip(actual.sections, base.sections)),
            "GEOMETRY_MISMATCH", "source tract length changed")
    if ratio == "1.00":
        _expect(actual is base, "NULL_NOT_IDENTITY", "null must return parent geometry")
        return {
            "schema": PROTOCOL, "family": FAMILY,
            "center_index": center, "rest_area_ratio": ratio,
            "null_alias": True, "revision_id": f"{PARENT_ID}@{PARENT_REVISION}",
            "preset_id": parent.preset_id, "preset_revision": parent.revision,
            "parent_preparation_digest": parent.preparation_digest,
            "preparation_digest": parent.preparation_digest,
            "backend_id": parent.prepared.backend_id,
            "rest_areas_hex": [s.area_m2.hex() for s in base.sections],
            "lengths_hex": [s.length_m.hex() for s in base.sections],
        }
    prepared = prepare_tract1d(
        parent.prepared.creature, actual,
        provenance=PreparationProvenance(
            source="od2-local-revision-study", model=FAMILY,
            notes=(f"parent={parent.preparation_digest}",
                   f"center={center}", f"ratio={ratio}"),
        ),
    )
    preset_id = f"od2-local5-c{center:02d}-r{ratio.replace('.', '')}"
    derived = make_body_preset(preset_id=preset_id, revision=1, prepared=prepared)
    # Reuse the existing exact-revision Core registry, never create an alternative
    # registry with different identity semantics.
    pool = BodyPresetRegistry((parent, derived))
    selected = pool.resolve(
        CharacterBodyBinding("od2-character", preset_id, 1),
        required_backend_id=parent.prepared.backend_id,
    )
    _expect(selected.is_bound and selected.snapshot is not None
            and selected.snapshot.preparation_digest == derived.preparation_digest,
            "REVISION_MISMATCH", "Core registry failed to bind derived body")
    recipe = {
        "identity_version": IDENTITY_ALGORITHM,
        "family": FAMILY, "parent_id": PARENT_ID,
        "parent_revision": PARENT_REVISION,
        "parent_preparation_digest": parent.preparation_digest,
        "backend_id": parent.prepared.backend_id,
        "center_index": center, "rest_area_ratio": ratio,
        "rest_areas_hex": [s.area_m2.hex() for s in actual.sections],
        "lengths_hex": [s.length_m.hex() for s in actual.sections],
        "prepared_digest": derived.preparation_digest,
    }
    revision_id = "od2-" + digest(canonical(recipe))
    return {
        "schema": PROTOCOL, "family": FAMILY, "center_index": center,
        "rest_area_ratio": ratio, "null_alias": False,
        "revision_id": revision_id, "preset_id": preset_id,
        "preset_revision": 1, "parent_preparation_digest": parent.preparation_digest,
        "preparation_digest": derived.preparation_digest,
        "backend_id": parent.prepared.backend_id,
        "rest_areas_hex": recipe["rest_areas_hex"],
        "lengths_hex": recipe["lengths_hex"],
        "recipe": recipe,
    }


def _cases(runner: Any, exp: Any, parent: Any) -> list[dict[str, Any]]:
    return [_receipt(runner, exp, parent, center, ratio)
            for center in CENTERS for ratio in RATIOS]


def _strict_parse(path: Path) -> object:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for name, value in items:
            if name in obj:
                raise RevisionError("DUPLICATE_FIELD", f"repeated key {name}")
            obj[name] = value
        return obj
    return json.loads(path.read_text("utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(
                          RevisionError("INVALID_JSON", "nonfinite JSON token")))


def _trusted_archive_files(directory: Path) -> None:
    _expect(directory.is_dir() and not directory.is_symlink(),
            "INVALID_ARCHIVE", "not a real directory")
    _expect((directory / "physics").is_dir()
            and not (directory / "physics").is_symlink(),
            "INVALID_ARCHIVE", "missing physical archive")


def verify_archive(directory: Path) -> dict[str, Any]:
    _trusted_archive_files(directory)
    runner, exp, parent, _ = _load_context()
    marker = directory / "manifest.json"
    decision = directory / "physics" / "decision.json"
    for path in (marker, decision):
        _expect(path.is_file() and not path.is_symlink(),
                "INVALID_ARCHIVE", f"missing or symlink: {path.name}")
    saved = _strict_parse(marker)
    measured = _strict_parse(decision)
    _expect(type(saved) is dict and type(measured) is dict,
            "INVALID_ARCHIVE", "manifest must be a JSON object")
    expected_receipts = _cases(runner, exp, parent)
    _expect(saved.get("schema") == PROTOCOL
            and saved.get("family") == FAMILY
            and saved.get("receipts") == expected_receipts
            and saved.get("source_pins") == PINS
            and saved.get("decision_sha256") == digest(decision.read_bytes()),
            "REVISION_MISMATCH", "body/parent/decision source receipt mismatch")
    _expect(measured.get("status") ==
            "GO_LIMITED_RESEARCH_SHAPE_AND_INHERITED_1D_ACOUSTICS"
            and measured.get("sample_rate_hz") == SAMPLE_RATE_HZ
            and measured.get("samples") == SAMPLES
            and len(measured.get("conditions", [])) == 6,
            "PHYSICAL_RESULT_MISMATCH", "unqualified physical output")
    _expect(saved.get("source_id") == measured.get("source_id")
            and saved.get("gesture_plan_sha256") == measured.get("gesture_plan_sha256"),
            "SOURCE_MISMATCH", "source/task identity changed")
    cases = measured["conditions"]
    expected_names: set[str] = set()
    nulls: list[np.ndarray] = []
    waveforms: dict[tuple[int, str], np.ndarray] = {}
    _expect(type(saved.get("artifact_sha256")) is dict,
            "INVALID_ARCHIVE", "missing artifact inventory")
    for receipt, row in zip(expected_receipts, cases, strict=True):
        c, r = receipt["center_index"], receipt["rest_area_ratio"]
        _expect(row.get("center") == c and row.get("ratio") == RATIOS[r],
                "REVISION_MISMATCH", "row does not match body")
        expect_area = np.array([float.fromhex(x) for x in receipt["rest_areas_hex"]])
        measured_area = np.asarray(row.get("rest_areas_m2"), dtype=np.float64)
        _expect(measured_area.shape == (16,)
                and np.array_equal(measured_area, expect_area),
                "GEOMETRY_MISMATCH", "physical body differs from saved revision")
        _expect(row.get("acoustic_calls") == 102,
                "PHYSICAL_RESULT_MISMATCH", "wrong physical execution calls")
        basename = f"c{c:02d}_r{round(RATIOS[r]*100):03d}"
        raw_name, wav_name = basename + ".npy", basename + ".wav"
        _expect(row.get("raw_file") == raw_name
                and row.get("preview_file") == wav_name,
                "INVALID_ARCHIVE", "physical file renamed or changed")
        for name in (raw_name, wav_name):
            path = directory / "physics" / name
            _expect(path.is_file() and not path.is_symlink(),
                    "INVALID_ARCHIVE", f"missing or symlink artifact {name}")
            _expect(saved["artifact_sha256"].get(name) == digest(path.read_bytes()),
                    "ARTIFACT_TAMPER", f"physical output altered: {name}")
            expected_names.add(name)
        raw = np.load(directory / "physics" / raw_name, allow_pickle=False)
        _expect(raw.shape == (SAMPLES,) and np.isfinite(raw).all(),
                "PHYSICAL_RESULT_MISMATCH", "raw pressure shape or finiteness")
        _expect(runner["sha_f64"](raw) == row["raw_pa_sha256_le_f64"]
                and digest((directory / "physics" / wav_name).read_bytes()) ==
                    row["preview_sha256"],
                "ARTIFACT_TAMPER", "stored native pressure/preview receipt incorrect")
        waveforms[(c, r)] = raw
        if r == "1.00":
            nulls.append(raw)
            _expect(exp.quantized_waveform_sha256(raw) ==
                    exp.AUDITED_QUANTIZED_WAVEFORM_SHA256,
                    "BASELINE_DRIFT", "audited old M0 raw pressure changed")
    _expect(len(nulls) == 2
            and exp.quantized_waveform_sha256(nulls[0]) ==
                exp.quantized_waveform_sha256(nulls[1]),
            "NULL_MISMATCH", "two independent nulls differ")
    floor = float(np.linalg.norm(nulls[0]-nulls[1])/np.linalg.norm(nulls[0]))
    for row in cases:
        c, r_float = row["center"], row["ratio"]
        ratio = f"{r_float:.2f}"
        calc = float(np.linalg.norm(waveforms[(c,ratio)]-nulls[0]) /
                     np.linalg.norm(nulls[0]))
        _expect(math.isfinite(calc)
                and abs(calc - row["raw_pa_relative_l2"]) <= 1e-12,
                "PHYSICAL_RESULT_MISMATCH", "raw Pa L2 not supported by bytes")
        if ratio != "1.00":
            _expect(abs(calc-REF_L2[(c,ratio)]) <= 2e-6
                    and calc > max(1e-4, 10*floor),
                    "PHYSICAL_RESULT_MISMATCH", "OD-1 pinned physical regression failed")
    _expect(set(saved["artifact_sha256"]) == expected_names,
            "INVALID_ARCHIVE", "invented/missing artifact receipts")
    _expect(set(p.name for p in (directory / "physics").iterdir()) ==
            expected_names | {"decision.json"},
            "INVALID_ARCHIVE", "unexpected physical archive members")
    return {"schema": PROTOCOL, "status": "GO_LIMITED_OD2_RESEARCH_REVISION_REPLAY",
            "verified_revisions": 4, "verified_null_aliases": 2,
            "source_id": measured["source_id"], "source_sha256_le_f64":
                measured["source_sha256_le_f64"],
            "gesture_plan_sha256": measured["gesture_plan_sha256"],
            "relative_raw_l2": [row["raw_pa_relative_l2"] for row in cases]}


def perform_suite(output: Path) -> dict[str, Any]:
    _expect(not os.path.lexists(output),
            "OUTPUT_EXISTS", "never overwrite earlier evidence")
    runner, exp, parent, _ = _load_context()
    receipts = _cases(runner, exp, parent)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="od2-stage-", dir=output.parent))
    try:
        measured = runner["run"](stage / "physics")
        _expect(len(measured["conditions"]) == 6,
                "PHYSICAL_RESULT_MISMATCH", "OD-1 did not perform all six cases")
        physical = stage / "physics"
        files = sorted(p for p in physical.iterdir() if p.suffix in (".npy", ".wav"))
        _expect(len(files) == 12, "PHYSICAL_RESULT_MISMATCH", "missing raw/WAV files")
        archive = {
            "schema": PROTOCOL, "family": FAMILY,
            "source_pins": PINS, "source_id": measured["source_id"],
            "gesture_plan_sha256": measured["gesture_plan_sha256"],
            "receipts": receipts,
            "decision_sha256": digest((physical / "decision.json").read_bytes()),
            "artifact_sha256": {p.name: digest(p.read_bytes()) for p in files},
        }
        (stage / "manifest.json").write_bytes(canonical(archive) + b"\n")
        result = verify_archive(stage)
        os.rename(stage, output)
        return result
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main() -> None:
    parser = argparse.ArgumentParser(description="OD-2 opt-in local research body adapter")
    parser.add_argument("operation", choices=("inspect", "derive", "perform-suite",
                                               "verify", "resolve"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--center", type=int)
    parser.add_argument("--ratio", choices=tuple(RATIOS))
    args = parser.parse_args()
    try:
        if args.operation in ("derive", "resolve"):
            c, r = _require_case(args.center, args.ratio)
            if args.operation == "resolve":
                _expect(args.output_dir is not None,
                        "INVALID_INPUT", "resolve requires --output-dir")
                verify_archive(args.output_dir)
            runner, exp, parent, _ = _load_context()
            result: dict[str, Any] = _receipt(runner, exp, parent, c, r)
        elif args.operation == "inspect":
            _, _, parent, _ = _load_context()
            result = {"schema": PROTOCOL, "status": "RESEARCH_ONLY",
                      "family": FAMILY, "centers": CENTERS,
                      "ratios": tuple(RATIOS),
                      "parent_id": parent.preset_id,
                      "parent_revision": parent.revision,
                      "parent_preparation_digest": parent.preparation_digest}
        else:
            _expect(args.output_dir is not None,
                    "INVALID_INPUT", "requires --output-dir")
            result = (perform_suite(args.output_dir) if args.operation == "perform-suite"
                      else verify_archive(args.output_dir))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    except (RevisionError, ValueError, RuntimeError, FileExistsError) as exc:
        code = exc.code if isinstance(exc, RevisionError) else "CORE_REFUSED"
        print(json.dumps({"schema": PROTOCOL, "status": "REFUSED",
                          "code": code, "message": str(exc)}, ensure_ascii=False))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
