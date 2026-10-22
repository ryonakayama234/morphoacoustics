"""Narrow Gate C candidate validation; expensive physical roundtrip in dedicated CI."""
from __future__ import annotations

from pathlib import Path
import json
import os
import runpy
import wave

import numpy as np
import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = runpy.run_path(str(ROOT / "tools/cc_b1_limited_performer.py"))
SCHEMA = json.loads((ROOT / "contracts/cc-b1/v1/core-limited-performer-request.schema.json").read_text("utf-8"))


def request(digest: str, ratio: str = "0.90") -> dict[str, object]:
    return {"schema_version": ADAPTER["VERSION"],
            "parent": {"preset_id":"v3b-axial-M0", "revision":1,
                       "preparation_digest":digest},
            "edit":{"cavity_id":"oral-vowel-a-16x10mm", "section_index":8,
                    "rest_area_ratio":ratio}}


def test_versioned_schema_is_valid_and_rejects_capability_broadening():
    Draft202012Validator.check_schema(SCHEMA)
    digest = "sha256:"+"a"*64
    valid = request(digest)
    Draft202012Validator(SCHEMA).validate(valid)
    assert ADAPTER["check_request"](valid) is None
    bad = [
        {**valid, "unrecognized_gain": 2},
        {**valid, "schema_version":"performance-contract/v1"},
        {**valid, "edit":{**valid["edit"],"section_index":4}},
        {**valid, "edit":{**valid["edit"],"rest_area_ratio":"1.00"}},
        {**valid, "edit":{**valid["edit"],"rest_area_ratio":"1.05"}},
        {**valid, "edit":{**valid["edit"],"rest_area_ratio":1.10}},
        {**valid, "edit":{**valid["edit"],"section_index":True}},
        {**valid, "parent":{**valid["parent"],"revision":True}},
        {**valid, "parent":{**valid["parent"],"preparation_digest":"forged"}},
    ]
    for item in bad:
        assert ADAPTER["check_request"](item) is not None


def test_refusal_does_not_create_fake_take(tmp_path):
    invalid=request("sha256:"+"a"*64,ratio="0.01")
    target=tmp_path/"no-take"
    result=ADAPTER["perform"](invalid,target)
    assert result["status"]=="UNSUPPORTED"
    assert not target.exists()
    target.mkdir()
    with pytest.raises(FileExistsError):
        ADAPTER["perform"](invalid,target)


def test_reject_nonfinite_and_clipping_preview():
    with pytest.raises(ValueError,match="INVALID_PHYSICAL_AUDIO"):
        ADAPTER["common_gain_wav"](np.full(24000,float("nan")),1.0)
    with pytest.raises(ValueError,match="WAV_CLIPPING"):
        ADAPTER["common_gain_wav"](np.ones(24000),2.0)


@pytest.mark.skipif(os.getenv("CC_B1_GATE_C_PHYSICAL") != "1",
                    reason="Dedicated CI runs new source-pinned physical render")
@pytest.mark.parametrize("ratio", ["0.90", "1.10"])
def test_actual_new_physical_revision_roundtrip(tmp_path,ratio):
    base=ADAPTER["inspect_baseline"]()
    d=base["parent"]["preparation_digest"]
    assert base["editable"]["section_index"]==8
    assert base["editable"]["allowed_ratios"]==["0.90","1.10"]
    wrong=request("sha256:"+"0"*64,ratio)
    assert ADAPTER["perform"](wrong,tmp_path/"reject")["status"]=="REVISION_MISMATCH"
    assert not (tmp_path/"reject").exists()
    output=tmp_path/(ratio.replace(".","_"))
    ret=ADAPTER["perform"](request(d,ratio),output)
    assert ret["status"]=="SUCCEEDED", json.dumps({"refusal": ret, "base": base}, ensure_ascii=False)
    assert ret["acoustic_calls_per_body"]==102
    assert ret["relative_raw_pa_l2"]>1e-8
    assert ret["body_revision"]["edit"]["section_index"]==8
    assert ret["body_revision"]["parent"]["preparation_digest"]==d
    assert ret["baseline_quantized_sha256"] != ret["edited_quantized_sha256"]
    assert ret["edited_quantized_sha256"]==ADAPTER["EXPECTED_EDIT_QUANTIZED"][ratio]
    assert json.loads((output/"result.json").read_text("utf-8"))==ret
    assert ADAPTER["verify_output_archive"](output)==ret
    for artifact in ret["artifacts"]:
        payload=(output/artifact["path"]).read_bytes()
        assert len(payload)==artifact["size_bytes"]
        assert ADAPTER["sha256_bytes"](payload)==artifact["sha256"]
    b=np.load(output/"baseline_pa.npy",allow_pickle=False)
    e=np.load(output/"edited_pa.npy",allow_pickle=False)
    assert b.shape==e.shape==(24000,)
    assert np.isfinite(b).all() and np.isfinite(e).all()
    with wave.open(str(output/"edited.wav"),"rb") as wav:
        assert (wav.getnchannels(),wav.getsampwidth(),wav.getframerate(),
                wav.getnframes())==(1,2,48000,24000)
    with pytest.raises(FileExistsError):
        ADAPTER["perform"](request(d,ratio),output)
    # Adversarial manifest tampering: hashes alone never confer body identity.
    original_manifest = (output/"result.json").read_text("utf-8")
    for kind, expected_error in [
        ("revision_id", "REVISION_MISMATCH"),
        ("prepared_digest", "REVISION_MISMATCH"),
        ("source", "PHYSICAL_PROVENANCE_MISMATCH"),
        ("task_plan", "PHYSICAL_PROVENANCE_MISMATCH"),
        ("artifact_kind", "INVALID_ARTIFACT_REFERENCE"),
        ("acoustic_call_count", "PHYSICAL_PROVENANCE_MISMATCH"),
    ]:
        forged = json.loads(original_manifest)
        if kind == "revision_id":
            forged["body_revision"]["revision_id"] = "cc-b1-" + "0"*64
        elif kind == "prepared_digest":
            forged["body_revision"]["preparation_digest"] = "sha256:" + "0"*64
        elif kind == "source":
            forged["source"]["sha256_le_f64"] = "0"*64
        elif kind == "task_plan":
            forged["task_plan_sha256"] = "0"*64
        elif kind == "artifact_kind":
            forged["artifacts"][0]["kind"] = "fabricated-voice"
        else:
            forged["acoustic_calls_per_body"] = 0
        (output/"result.json").write_text(json.dumps(forged), "utf-8")
        with pytest.raises(ValueError, match=expected_error):
            ADAPTER["verify_output_archive"](output)
        (output/"result.json").write_text(original_manifest, "utf-8")

    # A forged trace hash and rewritten CSV must not bypass Core geometry.
    manifest=json.loads(original_manifest)
    trace=output/"edited_trace.csv"
    original_trace=trace.read_bytes()
    fake_trace=b"fabricated,geometry\\n"
    trace.write_bytes(fake_trace)
    for rec in manifest["artifacts"]:
        if rec["path"]=="edited_trace.csv":
            rec["size_bytes"]=len(fake_trace)
            rec["sha256"]=ADAPTER["sha256_bytes"](fake_trace)
    (output/"result.json").write_text(json.dumps(manifest), "utf-8")
    with pytest.raises(ValueError, match="PHYSICAL_TRACE_MISMATCH"):
        ADAPTER["verify_output_archive"](output)
    trace.write_bytes(original_trace)
    (output/"result.json").write_text(original_manifest, "utf-8")
    assert ADAPTER["verify_output_archive"](output)["status"]=="SUCCEEDED"
    # Byte-level tampering must be rejected even when the manifest remains present.
    wav=output/"edited.wav"
    wav.write_bytes(wav.read_bytes()+b"TAMPER")
    with pytest.raises(ValueError,match="ARTIFACT_HASH_MISMATCH"):
        ADAPTER["verify_output_archive"](output)

def test_partial_archive_without_completion_marker_is_not_a_take(tmp_path):
    partial=tmp_path/"partial"
    partial.mkdir()
    (partial/"edited.wav").write_bytes(b"not a finished physical result")
    with pytest.raises(ValueError,match="INCOMPLETE_RESULT"):
        ADAPTER["verify_output_archive"](partial)


def test_strict_json_rejects_duplicate_keys_and_nonfinite():
    loader=ADAPTER["strict_json_loads"]
    with pytest.raises(ValueError,match="DUPLICATE_JSON_KEY"):
        loader('{"schema_version":"v1","schema_version":"v2"}')
    with pytest.raises(ValueError,match="NONFINITE_JSON_NUMBER"):
        loader('{"edit":NaN}')


def test_linked_archive_path_is_refused(tmp_path):
    target=tmp_path/"actual"
    target.mkdir()
    alias=tmp_path/"link"
    alias.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError,match="UNTRUSTED_SYMLINK_PATH"):
        ADAPTER["verify_output_archive"](alias)
    with pytest.raises(ValueError,match="UNTRUSTED_SYMLINK_PATH"):
        ADAPTER["perform"](request("sha256:"+"a"*64), alias/"new")
