"""SMC-7 L1-R C0: REAL optional Open JTalk baseline and *audit-only* corpus parser.

This module never infers source offsets, authorizes a ReadingProposal, trains a
contextual ranker, performs SMC Tasks, or claims language-science correctness.
A fixture reader is always labeled FIXTURE_ONLY and cannot be a real B0 result.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib import import_module, metadata
import json
import os
import stat
import tempfile
from pathlib import Path
import sys
from typing import Callable

_B0_VERSION = "0.4.1"
_MAX_DICT_FILES = 512
_MAX_DICT_TOTAL = 512 * 1024 * 1024
_MAX_CORPUS_BYTES = 8 * 1024 * 1024
_MAX_CORPUS_ROWS = 30000
_SILENT = " \n\t、。！？…"


@dataclass(frozen=True, slots=True)
class BaselineReading:
    status: str
    code: str
    mode: str
    kana: str | None
    source_digest: str | None
    dictionary_digest: str | None
    provider_version: str | None
    l1_source_eligible: bool


@dataclass(frozen=True, slots=True)
class JoyoAudit:
    status: str
    rows: int
    valid_rows: int
    invalid_rows: int
    distinct_target_kanji: int
    l1_source_eligible: int
    file_sha256: str
    failure_codes: tuple[tuple[str, int], ...]


def _scalar(s: str) -> bool:
    return all(not 0xD800 <= ord(ch) <= 0xDFFF for ch in s)


def _source_valid(s: object) -> str | None:
    if type(s) is not str or not s:
        return "INVALID_SOURCE"
    if len(s) > 256:
        return "SOURCE_LIMIT"
    if not _scalar(s) or "\x00" in s:
        return "INVALID_SOURCE"
    if len(s.encode("utf-8")) > 2048:
        return "SOURCE_LIMIT"
    return None


def _source_l1_supported(s: str) -> bool:
    return all(
        c in _SILENT or 0x3041 <= ord(c) <= 0x3096
        or 0x30A1 <= ord(c) <= 0x30FA
        or 0x4E00 <= ord(c) <= 0x9FFF
        for c in s
    )


def _dictionary_tree(path: Path | str, snapshot: Path | None = None) -> str:
    """Bounded POSIX O_NOFOLLOW descriptor-relative enumeration and byte capture.

    If snapshot is provided, the exact bytes hashed are copied to a fresh
    owner-only temporary directory. The engine is constructed from that copy
    with explicit userdic=b"", not from the mutable global cached dictionary.
    """
    if not (type(path) is str or isinstance(path, Path)):
        raise ValueError("INVALID_DICTIONARY_PATH")
    if not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        raise ValueError("UNSAFE_DICTIONARY_PLATFORM")
    root = Path(path)
    if root.is_symlink():
        raise ValueError("DICTIONARY_SYMLINK")
    if not root.is_dir():
        raise ValueError("INVALID_DICTIONARY_PATH")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    rootfd = os.open(root, flags)
    files: list[tuple[tuple[str, ...], os.stat_result]] = []
    entry_count = 0

    def collect(fd: int, prefix: tuple[str, ...], depth: int) -> None:
        nonlocal entry_count
        if depth > 8:
            raise ValueError("DICTIONARY_LIMIT")
        local: list[tuple[str, os.stat_result]] = []
        with os.scandir(fd) as stream:
            for item in stream:
                entry_count += 1  # Count directories as well as files, before sort.
                if entry_count > _MAX_DICT_FILES:
                    raise ValueError("DICTIONARY_LIMIT")
                local.append((item.name, item.stat(follow_symlinks=False)))
        for name, observed in sorted(local, key=lambda x: x[0]):
            if stat.S_ISDIR(observed.st_mode):
                subfd = os.open(name, flags, dir_fd=fd)
                try:
                    opened = os.fstat(subfd)
                    if (opened.st_dev, opened.st_ino) != (observed.st_dev, observed.st_ino):
                        raise ValueError("DICTIONARY_CHANGED_DURING_SCAN")
                    collect(subfd, prefix + (name,), depth + 1)
                finally:
                    os.close(subfd)
            elif stat.S_ISREG(observed.st_mode):
                files.append((prefix + (name,), observed))
            else:
                raise ValueError("DICTIONARY_NOT_REGULAR_OR_LINK")

    try:
        collect(rootfd, (), 0)
        if not files:
            raise ValueError("EMPTY_DICTIONARY")
        total = 0
        h = sha256(b"SMC7-C0-OPENJTALK-DICTIONARY/v0\x00")
        for parts, observed in sorted(files, key=lambda pair: "/".join(pair[0])):
            name = "/".join(parts).encode("utf-8")
            if len(name) > 4096:
                raise ValueError("DICTIONARY_LIMIT")
            size = observed.st_size
            total += size
            if size < 0 or total > _MAX_DICT_TOTAL:
                raise ValueError("DICTIONARY_LIMIT")
            h.update(len(name).to_bytes(4, "big"))
            h.update(name)
            h.update(size.to_bytes(8, "big"))
            # Reopen every parent and file under rootfd using no-follow; a
            # pathname swap cannot escape to external bytes.
            owned: list[int] = []
            fd = rootfd
            try:
                for component in parts[:-1]:
                    fd = os.open(component, flags, dir_fd=fd)
                    owned.append(fd)
                leaf = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
                owned.append(leaf)
                opened = os.fstat(leaf)
                if (not stat.S_ISREG(opened.st_mode)
                        or (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
                        != (observed.st_dev, observed.st_ino, size, observed.st_mtime_ns)):
                    raise ValueError("DICTIONARY_CHANGED_DURING_SCAN")
                if snapshot is not None:
                    target = snapshot.joinpath(*parts)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    dst = target.open("xb")
                else:
                    dst = None
                try:
                    remaining = size
                    dicrc_bytes = bytearray() if parts == ("dicrc",) else None
                    while remaining:
                        block = os.read(leaf, min(1024 * 1024, remaining))
                        if not block:
                            raise ValueError("DICTIONARY_CHANGED_DURING_READ")
                        remaining -= len(block)
                        h.update(block)
                        if dicrc_bytes is not None:
                            if len(dicrc_bytes) + len(block) > 65536:
                                raise ValueError("DICTIONARY_CONFIG_LIMIT")
                            dicrc_bytes.extend(block)
                        if dst is not None:
                            dst.write(block)
                    if os.read(leaf, 1):
                        raise ValueError("DICTIONARY_CHANGED_DURING_READ")
                    if dicrc_bytes is not None:
                        if b"\x00" in dicrc_bytes:
                            raise ValueError("DICTIONARY_CONFIG_INVALID")
                        for rawline in dicrc_bytes.splitlines():
                            unquoted = rawline.split(b"#", 1)[0].strip()
                            key = unquoted.partition(b"=")[0].strip().lower()
                            if key == b"userdic":
                                raise ValueError("DICTIONARY_EXTERNAL_USERDIC")
                    after = os.fstat(leaf)
                    if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
                            opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns):
                        raise ValueError("DICTIONARY_CHANGED_DURING_READ")
                finally:
                    if dst is not None:
                        dst.close()
            finally:
                for owned_fd in reversed(owned):
                    os.close(owned_fd)
        return h.hexdigest()
    finally:
        os.close(rootfd)


def fingerprint_dictionary(path: Path | str) -> str:
    """Fingerprint local dictionary bytes with bounded no-follow traversal."""
    return _dictionary_tree(path)

def _refuse(code: str, source: object = None) -> BaselineReading:
    digest = sha256(source.encode("utf-8")).hexdigest() if (
        type(source) is str and _source_valid(source) is None
    ) else None
    eligible = bool(type(source) is str and _source_valid(source) is None
                    and _source_l1_supported(source))
    return BaselineReading("REFUSED", code, "NOT_RUN", None, digest, None, None, eligible)


def _kana_valid(text: object) -> str | None:
    if type(text) is not str or not text:
        return "INVALID_READING"
    if len(text) > 512:
        return "READING_LIMIT"
    if not _scalar(text):
        return "INVALID_READING"
    if len(text.encode("utf-8")) > 2048:
        return "READING_LIMIT"
    if not all(
        0x30A1 <= ord(x) <= 0x30FA or x == "ー" or x in _SILENT
        for x in text
    ):
        return "INVALID_READING"
    if not any(0x30A1 <= ord(x) <= 0x30FA for x in text):
        return "INVALID_READING"
    return None


def read_b0(
    source: object,
    dictionary_dir: Path | str,
    *,
    fixture_reader: Callable[[str], str] | None = None,
) -> BaselineReading:
    """Text-only G2P with an explicit private dictionary-bound engine.

    A fixture callable never represents genuine Japanese G2P. Actual execution
    always instantiates a NEW OpenJTalk from the exact hashed private snapshot,
    with userdic=b""; it never uses pyopenjtalk's cached global singleton.
    """
    error = _source_valid(source)
    if error:
        return _refuse(error, source)
    assert isinstance(source, str)
    if fixture_reader is not None:
        try:
            digest = fingerprint_dictionary(dictionary_dir)
        except (OSError, ValueError, UnicodeError):
            return _refuse("DICTIONARY_UNVERIFIED", source)
        try:
            raw = fixture_reader(source)
        except Exception:
            return _refuse("PROVIDER_FAILURE", source)
        version = "FIXTURE"
        mode = "FIXTURE_ONLY"
    else:
        try:
            version = metadata.version("pyopenjtalk")
        except (metadata.PackageNotFoundError, ImportError):
            return _refuse("PROVIDER_UNAVAILABLE", source)
        if version != _B0_VERSION:
            return _refuse("PROVIDER_VERSION_MISMATCH", source)
        try:
            module = import_module("pyopenjtalk")
        except (ImportError, OSError):
            return _refuse("PROVIDER_UNAVAILABLE", source)
        try:
            with tempfile.TemporaryDirectory(prefix="smc7-c0-openjtalk-") as temp:
                snapshot = Path(temp) / "dictionary"
                snapshot.mkdir(mode=0o700)
                digest = _dictionary_tree(dictionary_dir, snapshot)
                # Snapshot contents are immutable to external untrusted
                # directory writers, and only these bytes feed this engine.
                engine = module.OpenJTalk(
                    dn_mecab=os.fsencode(snapshot), userdic=b"",
                )
                raw = engine.g2p(source, kana=True)
        except (OSError, ValueError, UnicodeError):
            return _refuse("DICTIONARY_UNVERIFIED", source)
        except Exception:
            return _refuse("PROVIDER_FAILURE", source)
        mode = "PYOPENJTALK_REAL"
    problem = _kana_valid(raw)
    if problem:
        return _refuse(problem, source)
    assert isinstance(raw, str)
    return BaselineReading(
        "READ", "OK", mode, raw,
        sha256(source.encode("utf-8")).hexdigest(),
        digest, version, _source_l1_supported(source),
    )

def audit_joyo_jsonl(path: Path | str, *, expected_sha256: str | None = None) -> JoyoAudit:
    """Format/provenance *audit* of original Joyo kanji-level data, not H1–H4.

    Marked reading is a target **pronunciation span**. It is never a source span,
    nor proof of a unique whole-utterance Japanese reading.
    """
    if not (type(path) is str or isinstance(path, Path)):
        raise ValueError("INVALID_DATASET_PATH")
    file = Path(path)
    if file.is_symlink() or not file.is_file():
        raise ValueError("INVALID_DATASET_PATH")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise ValueError("UNSAFE_DATASET_PLATFORM")
    # No second unbounded pathname read: the no-follow/nonblocking descriptor
    # is checked before the finite read, and rechecked after.
    fd = os.open(file, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("INVALID_DATASET_PATH")
        if before.st_size > _MAX_CORPUS_BYTES:
            raise ValueError("DATASET_LIMIT")
        chunks: list[bytes] = []
        total = 0
        while True:
            block = os.read(fd, min(1024 * 1024, _MAX_CORPUS_BYTES + 1 - total))
            if not block:
                break
            total += len(block)
            if total > _MAX_CORPUS_BYTES:
                raise ValueError("DATASET_LIMIT")
            chunks.append(block)
        after = os.fstat(fd)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError("DATASET_CHANGED_DURING_READ")
        data = b"".join(chunks)
    finally:
        os.close(fd)
    digest = sha256(data).hexdigest()
    if expected_sha256 is not None:
        if (type(expected_sha256) is not str or len(expected_sha256) != 64
                or any(c not in "0123456789abcdef" for c in expected_sha256)
                or digest != expected_sha256):
            raise ValueError("DATASET_DIGEST_MISMATCH")
    try:
        body = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("INVALID_UTF8") from exc
    lines = body.splitlines()
    if not lines or len(lines) > _MAX_CORPUS_ROWS:
        raise ValueError("DATASET_LIMIT")
    errors: Counter[str] = Counter()
    keys: set[str] = set()
    kanji: set[str] = set()
    eligible = 0
    valid = 0
    for line in lines:
        if len(line) > 4096:
            errors["ROW_LIMIT"] += 1
            continue
        try:
            row = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            errors["INVALID_JSON"] += 1
            continue
        if type(row) is not dict or set(row) != {"key", "normalized_text", "normalized_pron"}:
            errors["INVALID_FIELDS"] += 1
            continue
        key = row["key"]
        source = row["normalized_text"]
        marked = row["normalized_pron"]
        if (type(key) is not str or len(key) > 120
                or len(key.split("_")) != 3 or not key.split("_")[-1].isdigit()
                or not key.split("_")[1] or len(key.split("_")[0]) != 1
                or not 0x4E00 <= ord(key.split("_")[0]) <= 0x9FFF
                or not all(0x3041 <= ord(ch) <= 0x3096
                           or 0x30A1 <= ord(ch) <= 0x30FA
                           or ch == "ー" for ch in key.split("_")[1])):
            errors["INVALID_KEY"] += 1
            continue
        if key in keys:
            errors["DUPLICATE_KEY"] += 1
            continue
        keys.add(key)
        if _source_valid(source) is not None or key.split("_")[0] not in source:
            errors["INVALID_SOURCE"] += 1
            continue
        if type(marked) is not str or len(marked) > 512 or not _scalar(marked):
            errors["INVALID_TARGET_MARKER"] += 1
            continue
        if marked.count("<") != 1 or marked.count(">") != 1:
            errors["INVALID_TARGET_MARKER"] += 1
            continue
        start = marked.index("<")
        stop = marked.index(">")
        part = marked[start + 1:stop] if start < stop else ""
        if (not part or not all(
                0x30A1 <= ord(ch) <= 0x30FA or ch == "ー" for ch in part
        ) or not _kana_valid(marked.replace("<", "").replace(">", "")) is None):
            errors["INVALID_TARGET_MARKER"] += 1
            continue
        valid += 1
        kanji.add(key.split("_")[0])
        if _source_l1_supported(source):
            eligible += 1
    return JoyoAudit(
        "AUDITED" if not errors else "RECONCILIATION_REQUIRED",
        len(lines), valid, len(lines) - valid, len(kanji), eligible,
        digest, tuple(sorted(errors.items())),
    )


def _main() -> int:
    parser = argparse.ArgumentParser(description="SMC-7 C0 isolated research-only probe")
    action = parser.add_subparsers(dest="action", required=True)
    b0 = action.add_parser("baseline")
    b0.add_argument("--text", required=True)
    b0.add_argument("--dictionary-dir", required=True)
    audit = action.add_parser("audit")
    audit.add_argument("--jsonl", required=True)
    audit.add_argument("--expected-sha256")
    args = parser.parse_args()
    if args.action == "baseline":
        result = read_b0(args.text, args.dictionary_dir)
        print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))
        return 0 if result.status == "READ" else 2
    report = audit_joyo_jsonl(args.jsonl, expected_sha256=args.expected_sha256)
    print(json.dumps(asdict(report), ensure_ascii=False, sort_keys=True))
    return 0 if report.status == "AUDITED" else 2


if __name__ == "__main__":
    sys.exit(_main())
