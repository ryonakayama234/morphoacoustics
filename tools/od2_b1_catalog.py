"""B1 P1 Core-only closed OD-2 catalog. No Studio, Take, or v1 wire change.

A candidate *reviewable* Core interface, not an adopted production pin.
The existing OD-2 research CLI remains the single derivation/physics authority;
this module only freezes product authorization and adds durable exact readback.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OD2 = runpy.run_path(str(ROOT / "tools" / "od2_body_cli.py"))
PROTOCOL = "od2.b1.core-catalog-receipt/1"
MANIFEST_PROTOCOL = "od2.b1.closed-catalog-manifest/1"
VERSION = "od2-b1-core-closed-catalog/1"
MANIFEST = ROOT / "contracts" / "body" / "od2-b1" / "catalog-v1.json"
PARENT_DIGEST = "sha256:a98d484f8740bf40a419ac117a2deb41ab659dea095577874455aec0713258de"

# Owner-authorized *finite* case IDs. The two short digest anchors were the
# only digest bytes published in the independent P0 acceptance comment.
# Full digests are always returned by physical Core re-derivation and checked
# against the available P0 anchor, never fabricated from an abbreviated hash.
LEDGER = (
    (4, "0.90", "od2-bfb4199f5d3a38ded992d42cbd7858ad5b4ebc34b297c9f1a8411dde88bdbf0b", "sha256:129bf045"),
    (4, "1.00", "v3b-axial-M0@1", PARENT_DIGEST),
    (4, "1.10", "od2-7c2663189d907111665544c67def56c885576f5394e4220ec12251e0ca5ebf67", "sha256:f2778205243970d43ca3ea0151b91286fd9c46fb85b8867a8efbb7b811e6da0a"),
    (8, "0.90", "od2-d722dfb9595672f0d19c46a8780c610c9d41fc3a8935b93d3d01a5d68aab4084", "sha256:4b4300f05d0ea98d2edc3e6c17d8075fd29a51c8de91af599a94fa663b602375"),
    (8, "1.00", "v3b-axial-M0@1", PARENT_DIGEST),
    (8, "1.10", "od2-b04351e9865aef8af2953ed8b585eefa7bf40ec0887214daf4c0e32590478716", "sha256:649c0b17"),
)


def refuse(code: str, message: str) -> None:
    raise OD2["RevisionError"](code, message)


def _strict_file(path: Path) -> object:
    if path.is_symlink() or not path.is_file():
        refuse("INVALID_RECEIPT", "missing or symlinked JSON file")
    return OD2["_strict_parse"](path)


def _expected_manifest() -> dict[str, Any]:
    return {
        "schema": MANIFEST_PROTOCOL,
        "catalog_version": VERSION,
        "family": OD2["FAMILY"],
        "parent_id": OD2["PARENT_ID"],
        "parent_revision": OD2["PARENT_REVISION"],
        "parent_preparation_digest": PARENT_DIGEST,
        "status": "CANDIDATE_UNADOPTED_CORE_PIN",
        "entries": [
            {"center_index": c, "rest_area_ratio": r,
             "revision_id": revision, "preparation_digest_anchor": anchor}
            for c, r, revision, anchor in LEDGER
        ],
    }


def _manifest() -> dict[str, Any]:
    obj = _strict_file(MANIFEST)
    # Unkeyed checksums are *not* authority: the manifest's entire content
    # must match the independent source-controlled finite whitelist.
    if obj != _expected_manifest():
        refuse("CATALOG_DRIFT", "catalog changed from the reviewed finite P0 ledger")
    return _expected_manifest()


def _git_head() -> str:
    def cmd(*args: str) -> str:
        result = subprocess.run(
            ("git", "-C", str(ROOT), *args), text=True, capture_output=True,
            check=False, timeout=10,
        )
        if result.returncode:
            refuse("UNTRUSTED_CHECKOUT", "Git checkout unavailable")
        return result.stdout.strip()
    head = cmd("rev-parse", "--verify", "HEAD")
    if len(head) != 40 or any(c not in "0123456789abcdef" for c in head):
        refuse("UNTRUSTED_CHECKOUT", "no exact 40-hex Core HEAD")
    if cmd("status", "--porcelain", "--untracked-files=normal"):
        refuse("DIRTY_CHECKOUT", "Core worktree must be clean for issuance/readback")
    return head


def _trusted_cases() -> tuple[Any, dict[tuple[int, str], dict[str, Any]]]:
    _manifest()
    runner, exp, parent, _ = OD2["_load_context"]()  # exact research source pins
    if parent.preparation_digest != PARENT_DIGEST:
        refuse("PARENT_DRIFT", "M0 preparation is not the independently audited parent")
    derived: dict[tuple[int, str], dict[str, Any]] = {}
    base = parent.prepared.rest_state
    if len(base.sections) != 16 or any(s.length_m != .01 for s in base.sections):
        refuse("PARENT_DRIFT", "not the frozen 16 x 0.010m M0 tract")
    for c, r, expected_id, digest_anchor in LEDGER:
        body = OD2["_receipt"](runner, exp, parent, c, r)
        if (body["revision_id"] != expected_id
            or not body["preparation_digest"].startswith(digest_anchor)
            or body["parent_preparation_digest"] != PARENT_DIGEST
            or body["family"] != OD2["FAMILY"]
            or body["backend_id"] != parent.prepared.backend_id
            or body["null_alias"] != (r == "1.00")):
            refuse("CATALOG_DRIFT", f"Core-derived identity/preparation mismatch c{c} r{r}")
        if len(body["rest_areas_hex"]) != 16 or len(body["lengths_hex"]) != 16:
            refuse("GEOMETRY_MISMATCH", "invalid section count")
        for i, (a_hex, length_hex, section) in enumerate(
            zip(body["rest_areas_hex"], body["lengths_hex"], base.sections, strict=True)
        ):
            a, length = float.fromhex(a_hex), float.fromhex(length_hex)
            if (not math.isfinite(a) or a <= 0 or length != section.length_m
                or (i not in range(c-2, c+3) and a != section.area_m2)):
                refuse("GEOMETRY_MISMATCH", "nonlocal edit, nonpositive area or changed length")
        if r == "1.00" and (body["rest_areas_hex"] !=
                            [s.area_m2.hex() for s in base.sections]):
            refuse("NULL_MISMATCH", "null alias not bitwise M0 geometry")
        derived[(c, r)] = body
    if (len(derived) != 6
        or len({b["revision_id"] for b in derived.values() if not b["null_alias"]}) != 4
        or {b["revision_id"] for b in derived.values() if b["null_alias"]} !=
            {"v3b-axial-M0@1"}):
        refuse("CATALOG_DRIFT", "non-closed catalog or new null identity")
    return exp, derived


def _case(center: object, ratio: object) -> tuple[int, str]:
    c, r = OD2["_require_case"](center, ratio)
    if (c, r) not in {(x, y) for x, y, _, _ in LEDGER}:
        refuse("UNAUTHORIZED_BODY", "case not in P0-accepted catalog")
    return c, r


def _receipt(exp: Any, body: dict[str, Any], head: str) -> dict[str, Any]:
    manifest = _manifest()
    # This is a newly computed source-buffer digest on *this* numerical host.
    # It is not the missing actual-performer source attestation for Studio Takes;
    # raw f64 bytes need not be portable across NumPy CPU math backends.
    sources, _ = exp.EXP26.EXP13.build_sources()
    source = np.asarray(sources["lf_fixed"].source, dtype="<f8")
    source_digest = OD2["digest"](source.tobytes(order="C"))
    return {
        "schema": PROTOCOL,
        "catalog_version": VERSION,
        "catalog_manifest_sha256": "sha256:" + OD2["digest"](OD2["canonical"](manifest)),
        "candidate_core_head": head,
        "core_pin_status": "CANDIDATE_UNADOPTED",
        "source_pins": dict(OD2["PINS"]),
        "numerical_environment": {
            "python": ".".join(map(str, sys.version_info[:3])),
            "numpy": __import__("numpy").__version__,
        },
        "source_id": "lf_fixed",
        "recomputed_source_sha256_le_f64": source_digest,
        "source_digest_status": "RECOMPUTED_ON_THIS_HOST_NOT_ACTUAL_PERFORMER_ATTESTATION",
        "task_plan_sha256": exp.sha256_json(exp.task_plan_payload()),
        "body": body,
    }


def catalog() -> dict[str, Any]:
    head = _git_head()
    exp, bodies = _trusted_cases()
    entries = [_receipt(exp, bodies[(c, r)], head) for c, r, _, _ in LEDGER]
    return {
        "schema": PROTOCOL, "catalog_version": VERSION,
        "status": "CORE_P1_CANDIDATE_NOT_ADOPTED",
        "candidate_core_head": head,
        "authorized_revisions": 4, "null_alias_cases": 2,
        "entries": entries,
    }


def derive(center: object, ratio: object) -> dict[str, Any]:
    c, r = _case(center, ratio)
    head = _git_head()
    exp, bodies = _trusted_cases()
    return _receipt(exp, bodies[(c, r)], head)


def issue(center: object, ratio: object, output: Path) -> dict[str, Any]:
    payload = derive(center, ratio)
    if not output.parent.is_dir() or output.parent.is_symlink():
        refuse("INVALID_OUTPUT", "existing nonsymlink parent directory required")
    # No overwrite or retargeting: readback is tied to this receipt's exact HEAD.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(output, flags, 0o600)
    except FileExistsError:
        refuse("OUTPUT_EXISTS", "immutable receipt path already exists")
    with os.fdopen(fd, "wb") as stream:
        stream.write(OD2["canonical"](payload) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    return payload


def resolve(receipt_path: Path, revision_id: str) -> dict[str, Any]:
    saved = _strict_file(receipt_path)
    if not isinstance(saved, dict) or not isinstance(saved.get("body"), dict):
        refuse("INVALID_RECEIPT", "receipt must contain a physical body object")
    saved_body = saved["body"]
    c, r = _case(saved_body.get("center_index"), saved_body.get("rest_area_ratio"))
    # Alias is uniquely selected by (center, ratio, revision_id), NOT merely
    # by the common parent revision_id.
    fresh = derive(c, r)
    if revision_id != fresh["body"]["revision_id"] or saved != fresh:
        refuse("REVISION_MISMATCH", "receipt, exact Core HEAD or chosen revision changed")
    return {"schema": PROTOCOL, "status": "VERIFIED_CANDIDATE_READBACK",
            "receipt": fresh}


def verify_archive(directory: Path) -> dict[str, Any]:
    # Inherits real raw-Pa re-execution and independent acoustic observer checks.
    _git_head()
    _trusted_cases()
    result = OD2["verify_archive"](directory)
    return {"schema": PROTOCOL, "status": "RESEARCH_ARCHIVE_PHYSICS_VERIFIED",
            "catalog_version": VERSION, "candidate_core_head": _git_head(),
            "research_verification": result}


def main() -> None:
    p = argparse.ArgumentParser(description="Core-only OD-2 B1 P1 candidate catalog")
    p.add_argument("operation", choices=("catalog", "derive", "issue", "resolve", "verify-archive"))
    p.add_argument("--center", type=int)
    p.add_argument("--ratio")
    p.add_argument("--output", type=Path)
    p.add_argument("--receipt", type=Path)
    p.add_argument("--revision-id")
    p.add_argument("--archive", type=Path)
    a = p.parse_args()
    try:
        if a.operation == "catalog":
            result = catalog()
        elif a.operation == "derive":
            result = derive(a.center, a.ratio)
        elif a.operation == "issue":
            if a.output is None:
                refuse("INVALID_INPUT", "issue requires --output")
            result = issue(a.center, a.ratio, a.output)
        elif a.operation == "resolve":
            if a.receipt is None or a.revision_id is None:
                refuse("INVALID_INPUT", "resolve requires --receipt and --revision-id")
            result = resolve(a.receipt, a.revision_id)
        else:
            if a.archive is None:
                refuse("INVALID_INPUT", "verify-archive requires --archive")
            result = verify_archive(a.archive)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    except (OD2["RevisionError"], ValueError, OSError, subprocess.TimeoutExpired) as exc:
        code = exc.code if isinstance(exc, OD2["RevisionError"]) else "CORE_REFUSED"
        print(json.dumps({"schema": PROTOCOL, "status": "REFUSED",
                          "code": code, "message": str(exc)}, ensure_ascii=False))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
