"""B1 P1 product-catalog gates: strict identity, persistence and refusals.

Full inherited model physics is covered by the opt-in OD-2 and CC-A2 gates;
no experiment/model source, Studio or v1 contract is changed by this package.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import runpy
import subprocess
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
P1 = runpy.run_path(str(ROOT / "tools" / "od2_b1_catalog.py"))
OD2 = P1["OD2"]
pytestmark = pytest.mark.skipif(
    np.__version__ != "2.4.6",
    reason="B1 P1 inherits OD-2 exact numerical dependency NumPy 2.4.6",
)


def _expect_refused(fn, code):
    with pytest.raises(OD2["RevisionError"]) as error:
        fn()
    assert error.value.code == code


@pytest.fixture(scope="module")
def released():
    return P1["catalog"]()


def test_exact_closed_catalog_rederived_from_core(released):
    assert released["schema"] == "od2.b1.core-catalog-receipt/1"
    assert released["status"] == "CORE_P1_CANDIDATE_NOT_ADOPTED"
    assert released["authorized_revisions"] == 4
    assert released["null_alias_cases"] == 2
    entries = released["entries"]
    assert len(entries) == 6
    assert [(e["body"]["center_index"], e["body"]["rest_area_ratio"])
            for e in entries] == [(4, "0.90"), (4, "1.00"), (4, "1.10"),
                                 (8, "0.90"), (8, "1.00"), (8, "1.10")]
    assert len({e["body"]["revision_id"] for e in entries}) == 5
    nulls = [e["body"] for e in entries if e["body"]["null_alias"]]
    nonnulls = [e["body"] for e in entries if not e["body"]["null_alias"]]
    assert len(nulls) == 2 and len(nonnulls) == 4
    assert all(b["revision_id"] == "v3b-axial-M0@1" for b in nulls)
    assert nulls[0]["preparation_digest"] == nulls[1]["preparation_digest"] == P1["PARENT_DIGEST"]
    assert nulls[0]["rest_areas_hex"] == nulls[1]["rest_areas_hex"]
    assert len({b["revision_id"] for b in nonnulls}) == 4
    assert len({b["preparation_digest"] for b in nonnulls}) == 4
    assert all(b["parent_preparation_digest"] == P1["PARENT_DIGEST"] for b in nonnulls)
    assert all(len(b["rest_areas_hex"]) == len(b["lengths_hex"]) == 16
               for b in nonnulls)
    assert all(e["core_pin_status"] == "CANDIDATE_UNADOPTED"
               and e["candidate_core_head"] == released["candidate_core_head"]
               and e["source_id"] == "lf_fixed"
               and len(e["recomputed_source_sha256_le_f64"]) == 64
               and e["source_digest_status"] ==
                   "RECOMPUTED_ON_THIS_HOST_NOT_ACTUAL_PERFORMER_ATTESTATION"
               and e["numerical_environment"]["numpy"] == "2.4.6"
               for e in entries)
    # Not a shortened hash masquerading as an exact release digest.
    assert all(len(b["preparation_digest"]) == 71 for b in nonnulls)
    for entry, (_, _, expected_revision, expected_anchor) in zip(
        entries, P1["LEDGER"], strict=True
    ):
        assert entry["body"]["revision_id"] == expected_revision
        assert entry["body"]["preparation_digest"].startswith(expected_anchor)
        assert entry == P1["derive"](
            entry["body"]["center_index"], entry["body"]["rest_area_ratio"])


@pytest.mark.parametrize("center,ratio", [
    (0, "0.90"), (3, "0.90"), (9, "1.10"), (-1, "1.10"),
    (4.0, "0.90"), (True, "0.90"),
    (4, "0.95"), (4, "1.0"), (8, "NaN"), (8, "1.01"),
    (8, 1.1), (8, True), (None, "1.00"), (4, None),
])
def test_disallowed_case_fail_closed(center, ratio):
    _expect_refused(lambda: P1["derive"](center, ratio),
                    "UNSUPPORTED_CENTER" if type(center) is not int or center not in (4, 8)
                    else "UNSUPPORTED_RATIO")


def test_unchanged_frozen_source_and_v1_contract():
    OD2["verify_pins"]()
    b = (ROOT / "contracts/performance/v1/common.schema.json").read_bytes()
    assert OD2["_blob"](b) == "37e4403f1192a940bc9d61fcb35fe698527c9fef"
    assert P1["_manifest"]()["entries"] == P1["_expected_manifest"]()["entries"]


@pytest.mark.parametrize("center,ratio", [(4, "1.10"), (8, "1.00")])
def test_issue_separate_process_readback_and_no_overwrite(tmp_path, center, ratio):
    target = tmp_path / "issued.json"
    saved = P1["issue"](center, ratio, target)
    assert json.loads(target.read_text("utf-8")) == saved
    revision_id = saved["body"]["revision_id"]
    cmd = [sys.executable, str(ROOT / "tools/od2_b1_catalog.py"), "resolve",
           "--receipt", str(target), "--revision-id", revision_id]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr + result.stdout
    wire = json.loads(result.stdout)
    assert wire["status"] == "VERIFIED_CANDIDATE_READBACK"
    assert wire["receipt"] == saved
    _expect_refused(lambda: P1["issue"](center, ratio, target), "OUTPUT_EXISTS")
    _expect_refused(lambda: P1["resolve"](target, revision_id + "forged"),
                    "REVISION_MISMATCH")
    assert json.loads(target.read_text("utf-8")) == saved


def test_receipt_adversarial_mutations_and_recovery(tmp_path):
    target = tmp_path / "good.json"
    saved = P1["issue"](8, "1.10", target)
    revision_id = saved["body"]["revision_id"]
    forged = tmp_path / "forged.json"
    edits = [
        lambda p: p["body"].__setitem__("revision_id", "od2-" + "0" * 64),
        lambda p: p["body"].__setitem__("preparation_digest", "sha256:" + "0" * 64),
        lambda p: p["body"].__setitem__("parent_preparation_digest", "sha256:" + "0" * 64),
        lambda p: p["body"].__setitem__("center_index", 4),
        lambda p: p["body"].__setitem__("rest_area_ratio", "0.90"),
        lambda p: p["body"].__setitem__("family", "cc-b1.site08"),
        lambda p: p["body"].__setitem__("backend_id", "wrong.backend"),
        lambda p: p["body"]["rest_areas_hex"].__setitem__(8, float(0.5).hex()),
        lambda p: p["body"]["lengths_hex"].__setitem__(8, float(0.02).hex()),
        lambda p: p.__setitem__("candidate_core_head", "0" * 40),
        lambda p: p.__setitem__("catalog_manifest_sha256", "sha256:" + "0" * 64),
        lambda p: p.__setitem__("unexpected", "not authorized"),
        lambda p: p["source_pins"].__setitem__("tools/cc_a2_live.py", "0" * 40),
        lambda p: p.__setitem__("source_id", "fake-source"),
        lambda p: p.__setitem__("task_plan_sha256", "0" * 64),
    ]
    for edit in edits:
        mutation = copy.deepcopy(saved)
        edit(mutation)
        forged.write_text(json.dumps(mutation), encoding="utf-8")
        _expect_refused(lambda: P1["resolve"](forged, revision_id),
                        "REVISION_MISMATCH")
    # Duplicate keys and symlinked input must not silently resolve.
    forged.write_text('{"body":{},"body":{}}', encoding="utf-8")
    _expect_refused(lambda: P1["resolve"](forged, revision_id), "DUPLICATE_FIELD")
    forged.unlink()
    forged.symlink_to(target)
    _expect_refused(lambda: P1["resolve"](forged, revision_id), "INVALID_RECEIPT")
    assert P1["resolve"](target, revision_id)["status"] == "VERIFIED_CANDIDATE_READBACK"


def test_manifest_drift_rejected_even_if_checksum_recomputed(tmp_path, monkeypatch):
    manifest = tmp_path / "forged-catalog.json"
    altered = P1["_expected_manifest"]()
    altered["entries"][0]["revision_id"] = "od2-" + "0" * 64
    manifest.write_text(json.dumps(altered), encoding="utf-8")
    monkeypatch.setitem(P1["_manifest"].__globals__, "MANIFEST", manifest)
    _expect_refused(lambda: P1["_manifest"](), "CATALOG_DRIFT")
    _expect_refused(lambda: P1["derive"](4, "0.90"), "CATALOG_DRIFT")


def test_no_valid_receipt_without_clean_exact_head(tmp_path, monkeypatch):
    # Does not require creating a dirty checkout on the review branch.
    git_fn = P1["_git_head"]
    def blocked(*args, **kwargs):
        raise OD2["RevisionError"]("DIRTY_CHECKOUT", "simulated dirty state")
    monkeypatch.setitem(P1["derive"].__globals__, "_git_head", blocked)
    _expect_refused(lambda: P1["derive"](4, "1.10"), "DIRTY_CHECKOUT")
    output = tmp_path / "must-not-exist.json"
    _expect_refused(lambda: P1["issue"](4, "1.10", output), "DIRTY_CHECKOUT")
    assert not output.exists()
    monkeypatch.setitem(P1["derive"].__globals__, "_git_head", git_fn)
