"""WG2 Creator bridge: real prepared body + inherited SV1 source -> fresh mouth-port WAV.

A source-checkout CLI, intentionally separate from frozen X2a/CC-A2 backends.
Static sustained /a/-like *prescribed source*, NOT CC-A2 moving /ai/ or microphone.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SV1_PATH = ROOT / "experiments" / "042_sv1_sustained_vowel" / "run.py"
BODY_PRESETS = ("v3b-axial-M0", "v3b-axial-M1")
DURATIONS = (0.25, 0.50)
VERSION = "wg2-creator-static-a-sustain/v0"
ARTIFACTS = (
    "source_flow_48k.npy",
    "mouth_pressure_native_pa.npy",
    "mouth_flow_native_m3_s.npy",
    "mouth_pressure_monitor_48k_pa.npy",
    "audio.wav",
)
CHARACTER_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _npy(values: object) -> bytes:
    output = io.BytesIO()
    np.save(output, np.asarray(values, dtype="<f8"), allow_pickle=False)
    return output.getvalue()


def _core_commit() -> str:
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()
    if not re.fullmatch(r"[a-f0-9]{40}", head):
        raise RuntimeError("invalid Core source revision")
    # The Git commit alone does NOT attest local source bytes. In particular
    # SV1, CC-A2 and the new waveguide can change without changing HEAD.
    dirty = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain=v1",
         "--untracked-files=all", "--"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if dirty:
        raise RuntimeError("WG2_CORE_SOURCE_DIRTY: refuses modified or untracked files")
    flags = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-v", "-z"],
        check=True, capture_output=True,
    ).stdout.split(b"\x00")
    if any(entry and entry[:1] != b"H" for entry in flags):
        raise RuntimeError("WG2_CORE_UNSAFE_GIT_INDEX_FLAGS")
    # Ignored executable source may not show in status; empty bytecode caches
    # from the present run are not a new source module.
    ignored = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--others", "--ignored",
         "--exclude-standard", "-z", "--", "src", "tools", "experiments"],
        check=True, capture_output=True,
    ).stdout.decode("utf-8").split("\x00")
    for filename in ignored:
        if (re.search(r"\.(py|pyw|pyc|pyo|pth|so|pyd|dll|dylib)$", filename, re.I)
                and not re.search(r"(^|/)__pycache__/[^/]+\.pyc$", filename)):
            raise RuntimeError("WG2_CORE_IGNORED_EXECUTABLE_SOURCE")
    return head


def validate_request(preset_id: str, revision: int, character_id: str,
                     duration_s: float) -> None:
    if (preset_id not in BODY_PRESETS or type(revision) is not int
            or revision != 1 or type(character_id) is not str
            or not CHARACTER_ID.fullmatch(character_id)
            or type(duration_s) is not float or duration_s not in DURATIONS):
        raise ValueError("UNSUPPORTED_WG2_BODY_SOURCE_OR_DURATION")


def _prepared_body(preset_id: str, revision: int, character_id: str,
                   sv1: dict[str, object]) -> tuple[object, object]:
    # Authentication in generate() must precede ANY local Core source import.
    from morphoacoustics.integration.body_presets import CharacterBodyBinding, BindingStatus
    # This inherited adapter independently pins its transitive audited
    # Experiment028/029 frozen source; do not reimplement the registry.
    cc = runpy.run_path(str(ROOT / "tools" / "cc_a2_live.py"))
    frozen = cc["_load_frozen_adapter"]()
    exp = frozen._load_audited_experiment()
    registry = cc["prepared_registry"](exp)
    resolved = registry.resolve(
        CharacterBodyBinding(character_id, preset_id, revision),
        required_backend_id=exp.TRACT1D_BACKEND_ID,
    )
    if (resolved.status is not BindingStatus.BOUND
            or resolved.preset is None or resolved.snapshot is None):
        raise ValueError("UNSUPPORTED_WG2_BODY_BINDING")
    report = exp.capability_report(resolved.preset.prepared)
    if report.status != exp.FeasibilityStatus.FEASIBLE:
        raise ValueError("INFEASIBLE_WG2_PREPARED_BODY")
    geom = resolved.preset.prepared.rest_state
    if len(geom.sections) != 16:
        raise RuntimeError("audited 16-section body changed")
    length = 0.010 if preset_id == BODY_PRESETS[0] else 0.011
    expected_m0 = exp.EXP26.EXP23.primary_geometry("a")
    if any(abs(x.length_m - length) > 1e-15 or
           x.area_m2 != y.area_m2
           for x, y in zip(geom.sections, expected_m0.sections, strict=True)):
        raise RuntimeError("CC-A2 anatomy deviates from frozen M0/M1 source")
    return exp, resolved


def generate(output_dir: Path, *, preset_id: str,
             revision: int, character_id: str, duration_s: float) -> dict:
    validate_request(preset_id, revision, character_id, duration_s)
    output_dir = Path(output_dir)
    if os.path.lexists(output_dir):
        raise FileExistsError("new exclusive WG2 Take directory required")
    if not output_dir.parent.is_dir():
        raise FileNotFoundError("WG2 parent directory does not exist")
    # Refuse local changes BEFORE any executable source is imported.
    authenticated_head = _core_commit()
    from morphoacoustics_waveguide import PassiveWaveguideConfig, render_mouth_port_monitor
    sv1 = runpy.run_path(str(SV1_PATH))
    exp, resolution = _prepared_body(preset_id, revision, character_id, sv1)
    source, cycles, envelope = sv1["_source_for_duration"](exp, duration_s)
    if (source.shape != (int(duration_s * 48_000),)
            or not np.isfinite(source).all() or
            cycles[0] != 0 or not np.all(np.diff(cycles) > 0)):
        raise RuntimeError("inherited source invariant failed")
    if duration_s == 0.50:
        # Same exact old approved source flow. Never reuse its completed WAV.
        previous = exp.EXP26.EXP23.EXP13.build_sources()[0]["lf_fixed"].source
        if not np.array_equal(source, previous):
            raise RuntimeError("SV1 source no longer matches frozen LF flow")
    config = PassiveWaveguideConfig(
        resolution.preset.prepared.rest_state, cells_per_section=2,
        termination="b0"
    )
    fresh = render_mouth_port_monitor(config, source)
    if fresh.output_samples != len(source) or not np.isfinite(
        np.asarray(fresh.mouth_pressure_physics_pa)
    ).all():
        raise RuntimeError("invalid actual physical outcome")
    contents = {
        "source_flow_48k.npy": _npy(source),
        "mouth_pressure_native_pa.npy": _npy(fresh.mouth_pressure_physics_pa),
        "mouth_flow_native_m3_s.npy": _npy(fresh.mouth_flow_physics_m3_s),
        "mouth_pressure_monitor_48k_pa.npy": _npy(fresh.mouth_port_pressure_monitor_pa),
        "audio.wav": fresh.wav_pcm16_mono_48k,
    }
    artifact_receipts = {
        key: {"sha256": sha256(data).hexdigest(), "bytes": len(data)}
        for key, data in contents.items()
    }
    result = {
        "schema_version": VERSION, "status": "SUCCEEDED",
        "task": "static-/a/-like-sustained-vowel",
        "is_calibrated_microphone": False,
        "physical_walls": "fixed",
        "source": {"id": "sv1-prescribed-100hz-lf-rd1",
                   "role": "externally-prescribed-volume-flow",
                   "duration_s": duration_s,
                   "sha256_f64": fresh.source_flow_sha256},
        "body": {"character_id": character_id,
                 "preset_id": resolution.snapshot.preset_id,
                 "revision": resolution.snapshot.preset_revision,
                 "backend_id": resolution.snapshot.backend_id,
                 "preparation_digest": resolution.snapshot.preparation_digest,
                 "length_m": config.geometry.total_length_m},
        "core_commit": _core_commit(),
        "observer": fresh.provenance(),
        "artifacts": artifact_receipts,
    }
    if result["core_commit"] != authenticated_head:
        raise RuntimeError("WG2_CORE_REVISION_CHANGED_DURING_RENDER")
    # Reuse SV1's reviewed exclusive/no-follow, fsync-before-final-marker publisher.
    sv1["_publish_new_bundle"](output_dir, contents, result)
    return result


def verify(output_dir: Path) -> dict:
    """Fail closed on local artifact corruption (source authenticity still SHA-pinned by Studio)."""
    folder = Path(output_dir)
    manifest = json.loads((folder / "manifest.json").read_text("utf-8"))
    if (manifest.get("schema_version") != VERSION or manifest.get("status") != "SUCCEEDED"
        or set(manifest.get("artifacts", {})) != set(ARTIFACTS)
        or manifest.get("core_commit") != _core_commit()
        or manifest.get("body", {}).get("preset_id") not in BODY_PRESETS
        or manifest.get("body", {}).get("revision") != 1
        or manifest.get("observer", {}).get("observation_point") !=
           "mouth-port-pressure-not-external-microphone"):
        raise ValueError("INVALID_WG2_CREATOR_MANIFEST")
    for key in ARTIFACTS:
        data = (folder / key).read_bytes()
        entry = manifest["artifacts"][key]
        if (sha256(data).hexdigest() != entry["sha256"]
            or len(data) != entry["bytes"]):
            raise ValueError("TAMPERED_WG2_PHYSICAL_ARTIFACT")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--body", choices=BODY_PRESETS)
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--character-id")
    parser.add_argument("--duration", type=float, default=0.25)
    args = parser.parse_args()
    if args.verify:
        result = verify(args.output_dir)
    else:
        result = generate(args.output_dir, preset_id=args.body, revision=args.revision,
                          character_id=args.character_id, duration_s=args.duration)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
