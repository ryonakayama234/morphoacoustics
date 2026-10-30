"""Only external Joyo metadata/strict-format classification; NOT reading-quality scoring.

Download ONLY the exact public original Joyo revision (SHA checked) and reproduce
the old/new C0 admission categories without mutating data, normalizing Japanese,
training, reading any held-out SMC text, or constructing an SMC motor plan.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any
from urllib.request import urlopen

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / "src"))
from morphoacoustics_smc.l1r_real_g2p import _source_valid, _scalar, _kana_valid  # noqa: E402

SOURCE_URL = (
    "https://huggingface.co/datasets/sbintuitions/joyo-kanji-yomi-benchmark/"
    "resolve/2ae383bcdac88dacf89c9ab84f9990eec55fe5c9/common_kanji_source.jsonl"
)
SOURCE_SHA = "32a843f662c55f1876baf64f8dc3475cc7b777c576a8fea6b43a2343ff46e897"
MAX_BYTES = 8 * 1024 * 1024


def classify(line: str, keys: set[str], *, strict_key: bool) -> tuple[str, str]:
    if len(line) > 4096:
        return "ROW_LIMIT", ""
    try:
        row = json.loads(line)
    except (ValueError, TypeError):
        return "INVALID_JSON", ""
    if type(row) is not dict or set(row) != {"key", "normalized_text", "normalized_pron"}:
        return "INVALID_FIELDS", ""
    key, source, marked = row["key"], row["normalized_text"], row["normalized_pron"]
    if type(key) is not str or len(key) > 120:
        return "INVALID_KEY", ""
    parts = key.split("_")
    if len(parts) != 3 or not parts[-1].isdigit() or not parts[0] or len(parts[0]) != 1:
        return "INVALID_KEY", key
    if strict_key and (
        not parts[1] or not 0x4E00 <= ord(parts[0]) <= 0x9FFF
        or not all(0x3041 <= ord(c) <= 0x3096
                   or 0x30A1 <= ord(c) <= 0x30FA
                   or c == "ー" for c in parts[1])
    ):
        return "INVALID_KEY", key
    if key in keys:
        return "DUPLICATE_KEY", key
    keys.add(key)
    if _source_valid(source) is not None or parts[0] not in source:
        return "INVALID_SOURCE", key
    if type(marked) is not str or len(marked) > 512 or not _scalar(marked):
        return "INVALID_TARGET_MARKER", key
    if marked.count("<") != 1 or marked.count(">") != 1:
        return "INVALID_TARGET_MARKER", key
    a, b = marked.index("<"), marked.index(">")
    part = marked[a+1:b] if a < b else ""
    if not part or not all(0x30A1 <= ord(c) <= 0x30FA or c == "ー" for c in part):
        return "INVALID_TARGET_MARKER", key
    if _kana_valid(marked.replace("<", "").replace(">", "")) is not None:
        return "INVALID_TARGET_MARKER", key
    return "ADMITTED", key


def main() -> int:
    with urlopen(SOURCE_URL, timeout=45) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise SystemExit("DATASET_LIMIT")
    digest = sha256(raw).hexdigest()
    if digest != SOURCE_SHA:
        raise SystemExit("DATASET_DIGEST_MISMATCH:" + digest)
    lines = raw.decode("utf-8").splitlines()
    old_keys: set[str] = set()
    new_keys: set[str] = set()
    old: Counter[str] = Counter()
    new: Counter[str] = Counter()
    mismatches: list[dict[str, Any]] = []
    queue: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        old_reason, old_key = classify(line, old_keys, strict_key=False)
        new_reason, new_key = classify(line, new_keys, strict_key=True)
        old[old_reason] += 1
        new[new_reason] += 1
        if old_reason != new_reason:
            mismatches.append({
                "line": number, "key": new_key or old_key,
                "historical": old_reason, "accepted_sha": new_reason,
            })
        if new_reason != "ADMITTED":
            queue.append({"line": number, "key": new_key or old_key,
                          "historical": old_reason, "current": new_reason})
    report = {
        "kind": "C0_PUBLIC_FORMAT_AUDIT_NOT_LINGUISTIC_GOLD",
        "exact_public_data_sha256": digest,
        "rows": len(lines),
        "early_predicate": dict(sorted(old.items())),
        "accepted_code_predicate": dict(sorted(new.items())),
        "changed_classification": mismatches,
        "current_manual_review_queue": queue,
        "no_gold_scoring": True,
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    expected_old = {"ADMITTED": 13056, "INVALID_SOURCE": 8, "INVALID_TARGET_MARKER": 31}
    expected_new = {"ADMITTED": 13050, "INVALID_KEY": 6,
                    "INVALID_SOURCE": 8, "INVALID_TARGET_MARKER": 31}
    if len(lines) != 13095 or dict(old) != expected_old or dict(new) != expected_new:
        raise SystemExit("HISTORICAL_PREDICATE_REPLAY_MISMATCH_NO_ADMISSION")
    if len(queue) != 45 or len(mismatches) != 6:
        raise SystemExit("MANUAL_RECONCILIATION_COUNT_MISMATCH")
    print("REPRODUCED_39_OLD_VS_45_CURRENT; MANUAL_RECONCILIATION_REQUIRED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
