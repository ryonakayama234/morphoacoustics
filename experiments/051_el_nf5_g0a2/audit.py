"""Metadata-only KU100 SOFA integrity auditor. Never access response/delay values."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import zipfile

MAX_ARCHIVE_BYTES = 50_000_000
MAX_MEMBER_BYTES = 30_000_000
ALLOWED_ROOT_ATTRS = ("SOFAConventions", "SOFAConventionsVersion", "DataType", "License", "RoomType", "DatabaseName", "ListenerShortName")
ALLOWED_DATASETS = ("Data.IR", "Data.Delay", "Data.SamplingRate", "SourcePosition", "ReceiverPosition", "ListenerPosition", "ListenerView", "ListenerUp")


class QualificationError(Exception):
    pass


def digest(data: bytes, algorithm: str) -> str:
    return hashlib.new(algorithm, data).hexdigest()


def _safe_attr(value) -> str | None:
    """Only short scalar convention strings; no arbitrary dataset values."""
    import numpy as np
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    if isinstance(value, np.ndarray):
        if value.ndim != 0:
            return None
        value = value.item()
    if not isinstance(value, (str, int, float)):
        return None
    return str(value)[:200]


def inspect_sofa_bytes(data: bytes) -> dict:
    import h5py
    try:
        with h5py.File(io.BytesIO(data), "r") as root:
            attributes = {k: _safe_attr(root.attrs[k]) for k in ALLOWED_ROOT_ATTRS if k in root.attrs}
            datasets = {}
            for k in ALLOWED_DATASETS:
                obj = root.get(k)
                if isinstance(obj, h5py.Dataset):
                    info = {"shape": list(obj.shape), "dtype": str(obj.dtype)}
                    if k in ("SourcePosition", "ReceiverPosition", "ListenerPosition"):
                        info["units"] = _safe_attr(obj.attrs.get("Units")) if "Units" in obj.attrs else None
                        info["type"] = _safe_attr(obj.attrs.get("Type")) if "Type" in obj.attrs else None
                    if k == "Data.SamplingRate":
                        if obj.size <= 1 and obj.dtype.kind in "if":
                            info["hz"] = float(obj[()].reshape(-1)[0]) if hasattr(obj[()], "reshape") else float(obj[()])
                    datasets[k] = info
            if not all(k in datasets for k in ("Data.IR", "Data.Delay", "SourcePosition", "ReceiverPosition")):
                raise QualificationError("Missing essential SOFA datasets")
            irshape = datasets["Data.IR"]["shape"]
            if len(irshape) != 3 or irshape[1] != 2:
                raise QualificationError("Data.IR is not two-channel [M,R,N]")
            if "Data.SamplingRate" not in datasets:
                raise QualificationError("Missing sampling-rate metadata")
            # No [()] or [:] access to Data.IR, Data.Delay, or position arrays.
            return {"attributes": attributes, "datasets": datasets, "structure": "PASS_SHAPE_ONLY"}
    except OSError as exc:
        raise QualificationError("SOFA is not a readable HDF5 file") from exc


def audit_archive(path: Path, expected_md5: str) -> dict:
    size = path.stat().st_size
    if size <= 0 or size > MAX_ARCHIVE_BYTES:
        raise QualificationError("Archive size out of bounds")
    data = path.read_bytes()
    actual_md5 = digest(data, "md5")
    if actual_md5.lower() != expected_md5.lower():
        raise QualificationError("Publisher MD5 mismatch")
    output = {"schema": "el_nf5_g0a2_integrity_v1", "archive_name": path.name,
              "archive_size_bytes": size, "archive_md5": actual_md5, "archive_sha256": digest(data,"sha256"),
              "original_data_ir_values_read": False, "original_data_delay_values_read": False, "files": []}
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        infos = [x for x in zf.infolist() if not x.is_dir()]
        if not infos or len(infos) > 30:
            raise QualificationError("Unexpected member count")
        for info in infos:
            parts = Path(info.filename).parts
            if info.filename.startswith("/") or ".." in parts or "\\" in info.filename or info.flag_bits & 1:
                raise QualificationError("Unsafe ZIP member")
            if info.file_size > MAX_MEMBER_BYTES or info.compress_size == 0:
                raise QualificationError("ZIP member invalid or oversized")
            if not info.filename.lower().endswith(".sofa"):
                # No unexpected archive contents loaded or redistributed.
                output["files"].append({"name":info.filename, "size":info.file_size, "type":"NON_SOFA_UNINSPECTED"})
                continue
            member = zf.read(info)
            result = inspect_sofa_bytes(member)
            output["files"].append({"name":info.filename, "size":info.file_size,
                                    "sha256":digest(member,"sha256"), **result})
    if not any(f.get("structure") == "PASS_SHAPE_ONLY" for f in output["files"]):
        raise QualificationError("No qualifying SOFA entries")
    file_licenses = sorted(set(str(f.get("attributes", {}).get("License", "")) for f in output["files"] if f.get("structure") == "PASS_SHAPE_ONLY"))
    output["embedded_file_licenses"] = file_licenses
    output["publisher_paper_license"] = "CC BY-SA 4.0"
    output["rights_status"] = ("FILE_NOTICE_AND_PAPER_VERSION_CONFLICT_REVIEW_REQUIRED"
                                if file_licenses != ["CC BY-SA 4.0"] else "LICENSE_STRING_MATCH_ONLY_RIGHTS_REVIEW_PENDING")
    output["physical_measurand_status"] = "NOT_QUALIFIED_BY_METADATA"
    output["conclusion"] = "INTEGRITY_AND_STRUCTURE_ONLY_NOT_PHYSICAL_QUALIFICATION"
    return output


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--expected-md5", required=True)
    args = p.parse_args()
    if len(args.expected_md5) != 32 or any(c not in "0123456789abcdefABCDEF" for c in args.expected_md5):
        raise SystemExit("Invalid expected MD5")
    try:
        print(json.dumps(audit_archive(args.archive, args.expected_md5), sort_keys=True, indent=2))
    except (QualificationError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"G0-A2 BLOCKED: {exc}") from exc


if __name__ == "__main__":
    main()
