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
    if not _scalar(s):
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


def fingerprint_dictionary(path: Path | str) -> str:
    """Deterministic content fingerprint of an existing local dictionary tree.

    Not a signature of library authenticity or evidence of linguistic accuracy.
    Refuses links, empty directories, excessive size and nonregular entries.
    """
    if not (type(path) is str or isinstance(path, Path)):
        raise ValueError("INVALID_DICTIONARY_PATH")
    root = Path(path)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("INVALID_DICTIONARY_PATH")
    h = sha256(b"SMC7-C0-OPENJTALK-DICTIONARY/v0\x00")
    n = 0
    total = 0
    for item in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if item.is_symlink():
            raise ValueError("DICTIONARY_SYMLINK")
        if item.is_dir():
            continue
        if not item.is_file():
            raise ValueError("DICTIONARY_NOT_REGULAR")
        n += 1
        if n > _MAX_DICT_FILES:
            raise ValueError("DICTIONARY_LIMIT")
        size = item.stat().st_size
        total += size
        if size < 0 or total > _MAX_DICT_TOTAL:
            raise ValueError("DICTIONARY_LIMIT")
        name = item.relative_to(root).as_posix().encode("utf-8")
        h.update(len(name).to_bytes(4, "big"))
        h.update(name)
        h.update(size.to_bytes(8, "big"))
        with item.open("rb") as fh:
            remaining = size
            while remaining:
                block = fh.read(min(1024 * 1024, remaining))
                if not block:
                    raise ValueError("DICTIONARY_CHANGED_DURING_READ")
                remaining -= len(block)
                h.update(block)
            if fh.read(1):
                raise ValueError("DICTIONARY_CHANGED_DURING_READ")
    if n == 0:
        raise ValueError("EMPTY_DICTIONARY")
    return h.hexdigest()


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
    """Real g2p(kana=True) *text only*, with verified local dictionary identity.

    Fixture override is reserved for software tests and unconditionally marked
    FIXTURE_ONLY. No kana-to-source token/character alignment is invented.
    """
    error = _source_valid(source)
    if error:
        return _refuse(error, source)
    assert isinstance(source, str)
    try:
        dictionary_sha = fingerprint_dictionary(dictionary_dir)
    except (ValueError, OSError, UnicodeError):
        return _refuse("DICTIONARY_UNVERIFIED", source)

    if fixture_reader is None:
        try:
            version = metadata.version("pyopenjtalk")
            if version != _B0_VERSION:
                return _refuse("PROVIDER_VERSION_MISMATCH", source)
            module = import_module("pyopenjtalk")
            active = module.OPEN_JTALK_DICT_DIR
            if type(active) not in (bytes, str) or not (type(dictionary_dir) is str or isinstance(dictionary_dir, Path)):
                return _refuse("DICTIONARY_UNVERIFIED", source)
            # samefile enforces the provider's actual dictionary location; the
            # passed folder is never merely a self-claimed SHA label.
            if not os.path.samefile(os.fsdecode(active), dictionary_dir):
                return _refuse("DICTIONARY_UNVERIFIED", source)
        except (metadata.PackageNotFoundError, ImportError, OSError, AttributeError):
            return _refuse("PROVIDER_UNAVAILABLE", source)
        try:
            raw = module.g2p(source, kana=True)
        except Exception:
            return _refuse("PROVIDER_FAILURE", source)
        mode = "PYOPENJTALK_REAL"
    else:
        # Explicitly non-scientific controlled fixture. Never mislabel as B0.
        version = "FIXTURE"
        try:
            raw = fixture_reader(source)
        except Exception:
            return _refuse("PROVIDER_FAILURE", source)
        mode = "FIXTURE_ONLY"
    problem = _kana_valid(raw)
    if problem:
        return _refuse(problem, source)
    assert isinstance(raw, str)
    return BaselineReading(
        "READ", "OK", mode, raw,
        sha256(source.encode("utf-8")).hexdigest(),
        dictionary_sha, version, _source_l1_supported(source),
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
    if file.stat().st_size > _MAX_CORPUS_BYTES:
        raise ValueError("DATASET_LIMIT")
    data = file.read_bytes()
    if len(data) > _MAX_CORPUS_BYTES:
        raise ValueError("DATASET_LIMIT")
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
                or not key.split("_")[0] or len(key.split("_")[0]) != 1):
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
        "AUDITED" if not errors else "INVALID_DATASET",
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
