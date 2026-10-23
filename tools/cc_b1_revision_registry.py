"""CC-B1 Gate C research: immutable local BodyRevision receipt registry.

Candidate only. Neither production package nor multi-user service. This
registry persists physical body *identity*, not acoustic output or studio Takes.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import runpy
import secrets
import stat
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[1]
VERSION = "cc-b1-body-revision-registry/v0"
PERFORMER_VERSION = "cc-b1-core-limited-performer/v1"
IDENTITY_PATTERN = re.compile(r"cc-b1-[0-9a-f]{64}\Z", re.ASCII)
MAX_RECORD_BYTES = 8192
RATIOS = ("0.90", "1.10")
_DIR_FLAGS = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
_FILE_READ_FLAGS = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)


class StrictParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ValueError("CLI_ARGUMENT_INVALID")


class RegistryError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def response(status: str, code: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {"schema_version": VERSION, "status": status}
    if code is not None:
        result["error"] = {"code": code}
    return result


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def _secure_dir_fd(path: Path, *, create_children: bool) -> tuple[int, int]:
    """Open anchored directory descriptors; require trusted private owner.

    Does NOT authenticate external origins or protect against a privileged
    adversary with write access to the same directory/user account.
    """
    try:
        root = os.open(path, _DIR_FLAGS)
    except OSError as exc:
        raise RegistryError("REGISTRY_DIR_UNSAFE") from exc
    try:
        root_stat = os.fstat(root)
        if (not stat.S_ISDIR(root_stat.st_mode)
            or root_stat.st_uid != os.geteuid()
            or root_stat.st_mode & 0o077):
            raise RegistryError("REGISTRY_DIR_UNSAFE")
        if create_children:
            try:
                os.mkdir("revisions", mode=0o700, dir_fd=root)
            except FileExistsError:
                pass
        try:
            child = os.open("revisions", _DIR_FLAGS, dir_fd=root)
        except OSError as exc:
            raise RegistryError("REGISTRY_DIR_UNSAFE") from exc
        try:
            info = os.fstat(child)
            if (not stat.S_ISDIR(info.st_mode)
                or info.st_uid != os.geteuid()
                or info.st_mode & 0o077):
                raise RegistryError("REGISTRY_DIR_UNSAFE")
        except BaseException:
            os.close(child)
            raise
        return root, child
    except BaseException:
        os.close(root)
        raise


def _read_entry(child_fd: int, name: str) -> bytes:
    try:
        fd = os.open(name, _FILE_READ_FLAGS, dir_fd=child_fd)
    except FileNotFoundError as exc:
        raise RegistryError("REVISION_NOT_FOUND") from exc
    except OSError as exc:
        raise RegistryError("REGISTRY_ENTRY_UNSAFE") from exc
    try:
        s = os.fstat(fd)
        if (not stat.S_ISREG(s.st_mode)
            or s.st_nlink != 1 or s.st_mode & 0o077
            or s.st_size > MAX_RECORD_BYTES):
            raise RegistryError("REGISTRY_ENTRY_UNSAFE")
        with os.fdopen(os.dup(fd), "rb") as stream:
            data = stream.read(MAX_RECORD_BYTES + 1)
        if len(data) > MAX_RECORD_BYTES:
            raise RegistryError("REGISTRY_ENTRY_UNSAFE")
        return data
    finally:
        os.close(fd)


def _derive(ratio: str) -> dict[str, object]:
    """Reconstruct from authoritative Core M0/r1, never from a stored claim."""
    if ratio not in RATIOS:
        raise RegistryError("REVISION_UNSUPPORTED")
    performer = runpy.run_path(str(ROOT / "tools/cc_b1_limited_performer.py"))
    cc_a2 = runpy.run_path(str(ROOT / "tools/cc_a2_live.py"))
    exp = cc_a2["_load_frozen_adapter"]()._load_audited_experiment()
    from morphoacoustics.integration.body_presets import CharacterBodyBinding
    registry = cc_a2["prepared_registry"](exp)
    resolution = registry.resolve(
        CharacterBodyBinding("cc-b1", performer["BASE_ID"], performer["BASE_REVISION"]),
        required_backend_id=exp.TRACT1D_BACKEND_ID,
    )
    if not resolution.is_bound or resolution.preset is None:
        raise RegistryError("TRUSTED_BASE_UNAVAILABLE")
    base = resolution.preset
    valid_parent = performer["inspect_baseline"]()["parent"]
    if base.preparation_digest != valid_parent["preparation_digest"]:
        raise RegistryError("TRUSTED_BASE_UNAVAILABLE")
    proto = runpy.run_path(str(ROOT / "tools/cc_b1_revision.py"))
    edited = proto["RestAreaEditIntent"](
        base_preset_id=base.preset_id,
        base_revision=base.revision,
        base_preparation_digest=base.preparation_digest,
        cavity_id="oral-vowel-a-16x10mm",
        section_index=8,
        area_m2=base.prepared.rest_state.sections[8].area_m2
        * performer["RATIOS"][ratio],
    )
    revision = proto["prepare_rest_area_revision"](base, edited)
    if not revision.accepted or revision.revision is None:
        raise RegistryError("TRUSTED_REVISION_UNAVAILABLE")
    receipt = revision.revision.receipt()
    if not IDENTITY_PATTERN.fullmatch(receipt["revision_id"]):
        raise RegistryError("TRUSTED_REVISION_INVALID")
    return receipt


def _expected_record(ratio: str) -> dict[str, object]:
    receipt = _derive(ratio)
    return {
        "schema_version": VERSION,
        "revision_id": receipt["revision_id"],
        "rest_area_ratio": ratio,
        "body_revision": receipt,
        "body_revision_sha256": "sha256:" + sha256(canonical(receipt)).hexdigest(),
    }


def _match_trusted_entry(payload: bytes, expected: dict[str, object]) -> None:
    # Exact bytes disallow unknown/duplicate keys, altered numeric types, BOM,
    # whitespace ambiguity, nonfinite constants, and rehashed fake claims.
    if payload != canonical(expected):
        raise RegistryError("REGISTRY_COLLISION_OR_TAMPER")


def _install_record(registry_dir: Path, expected: dict[str, object]) -> str:
    revision_id = expected["revision_id"]
    if not isinstance(revision_id, str) or not IDENTITY_PATTERN.fullmatch(revision_id):
        raise RegistryError("TRUSTED_REVISION_INVALID")
    payload = canonical(expected)
    if len(payload) > MAX_RECORD_BYTES:
        raise RegistryError("REGISTRY_RECORD_TOO_LARGE")
    root, child = _secure_dir_fd(registry_dir, create_children=True)
    try:
        name = revision_id + ".json"
        stage_name = ".stage-" + secrets.token_hex(16)
        # Never expose the final ID as a partial record. Write and fsync a
        # private staging inode, then atomically hard-link without replacement.
        flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
                 | getattr(os, "O_NOFOLLOW", 0))
        try:
            stage_fd = os.open(stage_name, flags, 0o600, dir_fd=child)
            try:
                with os.fdopen(stage_fd, "wb") as stream:
                    written = stream.write(payload)
                    if written != len(payload):
                        raise OSError("SHORT_STAGING_WRITE")
                    stream.flush()
                    os.fsync(stream.fileno())
                try:
                    os.link(stage_name, name, src_dir_fd=child,
                            dst_dir_fd=child, follow_symlinks=False)
                    outcome = "REGISTERED"
                except FileExistsError:
                    outcome = "ALREADY_REGISTERED"
            finally:
                # A failed stage/commit may leave garbage on crash; a staged
                # inode is never a valid revision ID and never a success.
                os.unlink(stage_name, dir_fd=child)
            os.fsync(child)
            _match_trusted_entry(_read_entry(child, name), expected)
            return outcome
        except OSError as exc:
            raise RegistryError("REGISTRY_PUBLISH_FAILED") from exc
    finally:
        os.close(child)
        os.close(root)


def register_archive(registry_dir: Path, archive_dir: Path) -> dict[str, object]:
    cli = runpy.run_path(str(ROOT / "tools/cc_b1_candidate_cli.py"))
    report = cli["execute"]([
        "--protocol-version", PERFORMER_VERSION, "--verify",
        "--archive-dir", str(archive_dir),
    ])
    if report.get("status") != "SUCCEEDED":
        raise RegistryError("PHYSICAL_ARCHIVE_UNVERIFIED")
    edit = report.get("edit_intent")
    if not isinstance(edit, dict) or edit.get("rest_area_ratio") not in RATIOS:
        raise RegistryError("REVISION_UNSUPPORTED")
    ratio = edit["rest_area_ratio"]
    expected = _expected_record(ratio)
    if canonical(report.get("body_revision")) != canonical(expected["body_revision"]):
        raise RegistryError("REVISION_MISMATCH")
    outcome = _install_record(registry_dir, expected)
    return {"schema_version": VERSION, "status": outcome,
            "revision_id": expected["revision_id"],
            "body_revision_sha256": expected["body_revision_sha256"]}


def resolve_revision(registry_dir: Path, revision_id: str) -> dict[str, object]:
    if not isinstance(revision_id, str) or not IDENTITY_PATTERN.fullmatch(revision_id):
        raise RegistryError("REVISION_ID_INVALID")
    # Only two legal identities exist in this narrowly validated physical scope.
    accepted: dict[str, object] | None = None
    for ratio in RATIOS:
        entry = _expected_record(ratio)
        if entry["revision_id"] == revision_id:
            accepted = entry
            break
    if accepted is None:
        raise RegistryError("REVISION_UNSUPPORTED")
    root, child = _secure_dir_fd(registry_dir, create_children=False)
    try:
        content = _read_entry(child, revision_id + ".json")
        _match_trusted_entry(content, accepted)
    finally:
        os.close(child)
        os.close(root)
    return {"schema_version": VERSION, "status": "RESOLVED",
            "revision_id": revision_id,
            "body_revision_sha256": accepted["body_revision_sha256"],
            "body_revision": accepted["body_revision"]}


def execute(argv: list[str] | None = None) -> dict[str, object]:
    parser = StrictParser()
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--register", action="store_true")
    operation.add_argument("--resolve", action="store_true")
    parser.add_argument("--registry-dir", type=Path, required=True)
    parser.add_argument("--archive-dir", type=Path)
    parser.add_argument("--revision-id")
    try:
        args = parser.parse_args(argv)
        if args.register:
            if args.archive_dir is None or args.revision_id is not None:
                raise RegistryError("CLI_ARGUMENT_INVALID")
            return register_archive(args.registry_dir, args.archive_dir)
        if args.archive_dir is not None or args.revision_id is None:
            raise RegistryError("CLI_ARGUMENT_INVALID")
        return resolve_revision(args.registry_dir, args.revision_id)
    except RegistryError as exc:
        return response("REFUSED", exc.code)
    except (ValueError, OSError):
        return response("REFUSED", "CLI_ARGUMENT_INVALID")
    except Exception:
        return response("FAILED", "CORE_REGISTRY_RUNTIME_FAILURE")


def main() -> None:
    result = execute()
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False))
    if result["status"] not in ("REGISTERED", "ALREADY_REGISTERED", "RESOLVED"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
