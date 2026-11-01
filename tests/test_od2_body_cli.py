"""OD-2 source-pinned revision/replay tests. Physics proof only in opt-in CI."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import runpy
import shutil
import tempfile

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = runpy.run_path(str(ROOT / "tools" / "od2_body_cli.py"))

# This test module executes the existing audited LF source. Generic CI matrices
# use newer NumPy and must not bypass the inherited scientific version gate.
# All six tests run under pinned NumPy 2.4.6 in the dedicated OD-2 workflow.
pytestmark = pytest.mark.skipif(
    np.__version__ != "2.4.6",
    reason="OD-2 source and numerical physics are frozen to NumPy 2.4.6",
)


@pytest.fixture(scope="module")
def context():
    return CLI["_load_context"]()


def test_exact_source_inventory_and_envelope(context):
    runner, exp, parent, registry = context
    CLI["verify_pins"]()
    assert parent.preset_id == "v3b-axial-M0" and parent.revision == 1
    assert parent.preparation_digest.startswith("sha256:")
    for c in (4, 8):
        for r in ("0.90", "1.00", "1.10"):
            receipt = CLI["_receipt"](runner, exp, parent, c, r)
            assert receipt["family"] == CLI["FAMILY"]
            assert len(receipt["rest_areas_hex"]) == 16
    for c, r in ((True, "1.10"), (4.0, "1.10"), (0, "1.10"),
                 (9, "0.90"), (4, True), (4, 1.1), (4, "1.0"),
                 (8, "nan"), (4, "0.95")):
        with pytest.raises(CLI["RevisionError"]):
            CLI["_require_case"](c, r)


def test_null_is_original_reference_not_six_new_bodies(context):
    run, exp, parent, registry = context
    null4 = CLI["_receipt"](run, exp, parent, 4, "1.00")
    null8 = CLI["_receipt"](run, exp, parent, 8, "1.00")
    assert null4["revision_id"] == null8["revision_id"] == "v3b-axial-M0@1"
    assert null4["preparation_digest"] == null8["preparation_digest"] == parent.preparation_digest
    assert null4["rest_areas_hex"] == null8["rest_areas_hex"]
    assert null4["null_alias"] is True and null8["null_alias"] is True
    revisions = [CLI["_receipt"](run, exp, parent, c, r) for c in (4, 8)
                 for r in ("0.90", "1.10")]
    assert len({rev["revision_id"] for rev in revisions}) == 4
    assert len({rev["preparation_digest"] for rev in revisions}) == 4
    assert all(rev["preparation_digest"] != parent.preparation_digest for rev in revisions)
    assert revisions == [CLI["_receipt"](run, exp, parent, c, r)
                         for c in (4, 8) for r in ("0.90", "1.10")]


def test_geometry_independent_od1_oracle(context):
    runner, exp, parent, registry = context
    oracle = runpy.run_path(str(ROOT / "experiments" / "od1_local_shape" / "oracle.py"))
    for c in (4, 8):
        for r in ("0.90", "1.00", "1.10"):
            receipt = CLI["_receipt"](runner, exp, parent, c, r)
            areas = np.array([float.fromhex(a) for a in receipt["rest_areas_hex"]])
            expected = oracle["reference_areas"](c, float(r))
            assert max(abs(np.log(areas / expected))) < 1e-12
            volume = sum(float.fromhex(length) * area for length, area in
                         zip(receipt["lengths_hex"], areas))
            assert volume == pytest.approx(oracle["static_volume"](expected), rel=1e-12)
            if r != "1.00":
                changed = [i for i, (a, b) in enumerate(zip(areas, oracle["published_areas"]()))
                           if a != b]
                assert changed == list(range(c-2,c+3))


def test_replay_receipt_canonical_hexfloat_and_legacy_separation(context):
    runner, exp, parent, registry = context
    receipt = CLI["_receipt"](runner, exp, parent, 8, "1.10")
    recipe = receipt["recipe"]
    assert recipe["identity_version"] == CLI["IDENTITY_ALGORITHM"]
    assert receipt["revision_id"] == "od2-" + CLI["digest"](CLI["canonical"](recipe))
    assert recipe["rest_area_ratio"] == "1.10"
    assert recipe["rest_areas_hex"][8].startswith("0x")
    assert receipt["revision_id"] != "v3b-axial-M0@1"
    assert not receipt["revision_id"].startswith("cc-b1-")


def test_duplicate_json_nonfinite_and_source_tampering(tmp_path, context, monkeypatch):
    p = tmp_path / "bad.json"
    for bad in ('{"a":1,"a":2}', '{"a":{"c":1,"c":2}}', '{"a":NaN}'):
        p.write_text(bad, "utf-8")
        with pytest.raises(CLI["RevisionError"]):
            CLI["_strict_parse"](p)
    pins = CLI["PINS"]
    old = pins["experiments/od1_local_shape/run.py"]
    monkeypatch.setitem(pins, "experiments/od1_local_shape/run.py", "0" * 40)
    with pytest.raises(CLI["RevisionError"], match="source changed"):
        CLI["verify_pins"]()
    monkeypatch.setitem(pins, "experiments/od1_local_shape/run.py", old)


@pytest.mark.skipif(os.environ.get("OD2_REAL_PHYSICS") != "1",
                    reason="opt-in pinned physical run only")
def test_real_physics_archive_restart_and_adversarial_readback(tmp_path):
    root = tmp_path / "od2-study"
    a = CLI["perform_suite"](root)
    assert a["status"] == "GO_LIMITED_OD2_RESEARCH_REVISION_REPLAY"
    assert a["verified_revisions"] == 4
    assert a["verified_null_aliases"] == 2
    assert a == CLI["verify_archive"](root)
    with pytest.raises(CLI["RevisionError"], match="overwrite"):
        CLI["perform_suite"](root)

    marker = root / "manifest.json"
    good = marker.read_bytes()
    try:
        data = json.loads(good)
        data["receipts"][0]["revision_id"] = "od2-" + "0" * 64
        marker.write_bytes(CLI["canonical"](data))
        with pytest.raises(CLI["RevisionError"], match="receipt mismatch"):
            CLI["verify_archive"](root)
    finally:
        marker.write_bytes(good)

    try:
        data = json.loads(good)
        data["receipts"][0]["rest_areas_hex"][4] = float(0.999).hex()
        marker.write_bytes(CLI["canonical"](data))
        with pytest.raises(CLI["RevisionError"], match="receipt mismatch"):
            CLI["verify_archive"](root)
    finally:
        marker.write_bytes(good)

    raw = root / "physics" / "c04_r090.npy"
    original = raw.read_bytes()
    try:
        raw.write_bytes(original[:-10] + b"0000000000")
        with pytest.raises(CLI["RevisionError"], match="altered"):
            CLI["verify_archive"](root)
    finally:
        raw.write_bytes(original)

    wav = root / "physics" / "c08_r110.wav"
    original = wav.read_bytes()
    try:
        wav.write_bytes(original[:-2] + b"\x00\x00")
        with pytest.raises(CLI["RevisionError"], match="altered"):
            CLI["verify_archive"](root)
    finally:
        wav.write_bytes(original)

    decision = root / "physics" / "decision.json"
    original = decision.read_bytes()
    try:
        decision.write_bytes(original.replace(b'"samples": 24000', b'"samples": 24001'))
        with pytest.raises(CLI["RevisionError"], match="receipt mismatch"):
            CLI["verify_archive"](root)
    finally:
        decision.write_bytes(original)

    link = root / "physics" / "c04_r110.wav"
    original = link.read_bytes()
    link.unlink()
    try:
        link.symlink_to("c04_r090.wav")
        with pytest.raises(CLI["RevisionError"], match="symlink"):
            CLI["verify_archive"](root)
    finally:
        link.unlink()
        link.write_bytes(original)

    assert CLI["verify_archive"](root) == a
