"""OG-AUD1 *research-preview-only* versioned fixed-body acoustic monitor runner.

Trust: exact Core checkout verification is Studio's responsibility. This runner
uses public OG-4 prepared graph validation and internally computes *NEW* Exp045
full time-domain port traces: not an OG-4 broadband API, human speech or emitted sound.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from morphoacoustics_graph.branch3 import prepare_branch3, restore_branch3

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/045_og_aud1_causal_monitor/causal_monitor.py"
BLUEPRINT_FIXTURE = ROOT / "docs/research/og4-branch3-api-golden.json"
SCHEMA = "og-aud1.pinned-preview.pair.v0"
BODY = {"small_C": .00015, "large_C": .0006}
CODE_SHA = "computed-from-exact-checked-out-runner-file"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def causal_module():
    spec = importlib.util.spec_from_file_location("og_aud1_causal_fixed", EXPERIMENT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_body(area: float) -> dict:
    fixture = json.loads(BLUEPRINT_FIXTURE.read_text(encoding="utf-8"))
    bp = deepcopy(fixture["snapshot_example"]["blueprint"])
    for organ in bp["organs"]:
        if organ["id"] == "C":
            organ["area_m2"] = area
    prepared = prepare_branch3(bp)
    snapshot = prepared.to_snapshot()
    checked = restore_branch3(snapshot)
    if checked.preparation_digest != prepared.preparation_digest:
        raise AssertionError("PREPARED_BINDING_MISMATCH")
    return snapshot


def compute_pair() -> tuple[dict, dict[str, bytes]]:
    model = causal_module()
    old, files = model.compute()
    if old["schema"] != "og-aud1.causal.experiment.v0" or len(old["records"]) != 2:
        raise AssertionError("EXPERIMENT_BACKEND_MISMATCH")
    if old["status"] != "EXPLORATORY_NOT_ADOPTED":
        raise AssertionError("EXPERIMENT_ADOPTION_STATUS_MISMATCH")
    t = np.arange(model.FRAMES, dtype=np.float64) / model.FS
    records = []
    for body, area in BODY.items():
        existing = next((r for r in old["records"] if r["body"] == body), None)
        if existing is None or existing["c_area_m2"] != area:
            raise AssertionError("PHYSICAL_BODY_SUBSTITUTION")
        state, diag = model.ports(t, area)
        port_names = ["A.in", "A.out", "B.in", "B.out", "C.in", "C.out"]
        six = np.stack([np.stack(state[name]) for name in port_names])
        # Shape 6 ports x 2 observables (Pa, m^3/s) x 48000 samples.
        if six.shape != (6, 2, 48000) or not np.all(np.isfinite(six)):
            raise AssertionError("INVALID_FULL_PORT_STATES")
        if not np.array_equal(six[0, 0], np.load(
            io.BytesIO(files[existing["raw_pressure_path"]]), allow_pickle=False
        )):
            raise AssertionError("SOURCE_PRESSURE_BINDING_FAILED")
        six_name = body + "/all_six_port_p_Pa_u_m3s.npy"
        files[six_name] = model.npy_bytes(six)
        records.append({
            "body": body, "c_area_m2": area,
            "graph": prepare_body(area),
            "raw_pressure_path": existing["raw_pressure_path"],
            "wave_path": existing["wave_path"],
            "six_port_path": six_name,
            "diagnostic": diag,
        })
    rev = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=10
    ).strip()
    if len(rev) != 40:
        raise RuntimeError("CORE_REVISION_UNKNOWN")
    manifest = {
        "schema": SCHEMA, "status": "PREVIEW_UNADOPTED",
        "physical_claim": "CAUSAL_SOURCE_PORT_PRESSURE_NON_RADIATED",
        "core_commit": rev, "runner_sha256": digest(Path(__file__).read_bytes()),
        "experiment_script_sha256": digest(EXPERIMENT.read_bytes()),
        "source_program": "exp045.analytic_fixed_U_m3s.v1",
        "source_reference_plane": "A.in",
        "og4_phasor_source_policy": "blueprint_phasor_source_is_validation_only; time_source_override_is_separate_exact_program",
        "source_sha256": old["source_sha256"], "source_path": "raw_U_m3_s.npy",
        "sample_rate_hz": 48000, "frames": 48000,
        "source_unit": "m3/s", "pressure_unit": "Pa",
        "shared_playback_gain_inverse_pa": old["shared_playback_gain_inverse_pa"],
        "relative_raw_pressure_rms_difference": old["relative_raw_pressure_rms_difference"],
        "port_order": ["A.in", "A.out", "B.in", "B.out", "C.in", "C.out"],
        "port_state_order": ["pressure_Pa", "signed_volume_flow_m3s"],
        "records": records,
        "artifact_sha256": {p: digest(b) for p, b in sorted(files.items())},
        "limits": ["not spoken language", "not radiation", "not microphone SPL",
                   "not realized motor gesture", "not general graph editing",
                   "not adopted Gate B"],
    }
    if records[0]["graph"]["preparation_digest"] == records[1]["graph"]["preparation_digest"]:
        raise AssertionError("BODY_CAUSAL_ID_COLLISION")
    return manifest, files


def run(out: Path) -> dict:
    if out.exists():
        raise FileExistsError("IMMUTABLE:OUTPUT_EXISTS")
    manifest, files = compute_pair()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent, prefix=".og-aud1-preview-stage-") as tmp:
        stage = Path(tmp)
        for rel, data in files.items():
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            if digest(target.read_bytes()) != manifest["artifact_sha256"][rel]:
                raise IOError("FAILED:ARTIFACT_READBACK")
        (stage / "manifest.json").write_text(
            json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n",
            encoding="utf-8")
        stage.rename(out)
    return manifest


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python tools/og_aud1_preview.py NEW_OUTPUT_DIRECTORY")
    print(json.dumps(run(Path(sys.argv[1])), sort_keys=True))
