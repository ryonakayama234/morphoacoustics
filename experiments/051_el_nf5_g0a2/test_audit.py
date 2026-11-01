"""Synthetic-only safety and structure tests; no publisher signals included."""
from __future__ import annotations
import hashlib
import importlib.util
import io
from pathlib import Path
import zipfile

import h5py
import numpy as np
import pytest

MOD = Path(__file__).with_name("audit.py")
spec = importlib.util.spec_from_file_location("g0a2_audit", MOD)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def make_sofa(missing: str | None = None) -> bytes:
    buf = io.BytesIO()
    with h5py.File(buf,"w") as f:
        f.attrs["SOFAConventions"] = "SimpleFreeFieldHRIR"
        f.attrs["License"] = "CC 3.0 BY-SA"
        for name, shape, fill in [
            ("Data.IR",(4,2,128),912345.0), ("Data.Delay",(4,2),777777.0),
            ("Data.SamplingRate",(1,),48000.0), ("SourcePosition",(4,3),123456.0),
            ("ReceiverPosition",(2,3),345678.0)
        ]:
            if name != missing:
                d = f.create_dataset(name, data=np.full(shape,fill))
                if name.endswith("Position"):
                    d.attrs["Units"] = "degree, degree, metre" if name=="SourcePosition" else "metre"
                    d.attrs["Type"] = "spherical" if name=="SourcePosition" else "cartesian"
    return buf.getvalue()


def make_zip(tmp_path, missing=None):
    p = tmp_path/"fixture.zip"
    with zipfile.ZipFile(p, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("safe.sofa",make_sofa(missing))
    return p,hashlib.md5(p.read_bytes()).hexdigest()


def test_synthetic_metadata_without_signal_leak(tmp_path):
    p,md5=make_zip(tmp_path)
    result=audit.audit_archive(p,md5)
    text=str(result)
    assert result["files"][0]["datasets"]["Data.IR"]["shape"]==[4,2,128]
    assert result["files"][0]["datasets"]["Data.Delay"]["shape"]==[4,2]
    assert result["files"][0]["datasets"]["Data.SamplingRate"]["hz"]==48000
    for forbidden in ("912345","777777","123456","345678"):
        assert forbidden not in text
    assert result["original_data_ir_values_read"] is False


def test_corrupt_expected_md5_is_hard_stop(tmp_path):
    p,_=make_zip(tmp_path)
    with pytest.raises(audit.QualificationError,match="MD5 mismatch"):
        audit.audit_archive(p,"0"*32)


@pytest.mark.parametrize("missing",["Data.IR","Data.Delay","SourcePosition","ReceiverPosition","Data.SamplingRate"])
def test_missing_structural_field_is_hard_stop(tmp_path,missing):
    p,md5=make_zip(tmp_path,missing)
    with pytest.raises(audit.QualificationError):
        audit.audit_archive(p,md5)


def test_invalid_not_hdf5():
    with pytest.raises(audit.QualificationError):
        audit.inspect_sofa_bytes(b"not SOFA")


def test_path_traversal_blocked(tmp_path):
    p=tmp_path/"unsafe.zip"
    with zipfile.ZipFile(p,"w") as z:
        z.writestr("../escape.sofa",make_sofa())
    with pytest.raises(audit.QualificationError,match="Unsafe"):
        audit.audit_archive(p,hashlib.md5(p.read_bytes()).hexdigest())

def test_embedded_license_version_conflict_is_explicit(tmp_path):
    p,md5=make_zip(tmp_path)
    result=audit.audit_archive(p,md5)
    assert result["embedded_file_licenses"] == ["CC 3.0 BY-SA"]
    assert result["rights_status"] == "FILE_NOTICE_AND_PAPER_VERSION_CONFLICT_REVIEW_REQUIRED"
    assert result["physical_measurand_status"] == "NOT_QUALIFIED_BY_METADATA"
