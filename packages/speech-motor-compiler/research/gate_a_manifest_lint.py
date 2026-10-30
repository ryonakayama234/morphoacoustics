"""Research-only Gate A *structural* accession lint. No gold/model validation.

This tool never certifies licensing, independent humans, source rights, reading truth,
source-offset accuracy, or availability of a scientific frozen corpus.
Run: python packages/speech-motor-compiler/research/gate_a_manifest_lint.py manifest.json
     python packages/speech-motor-compiler/research/gate_a_manifest_lint.py --self-test
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import os
import stat
import tempfile
from pathlib import Path
import re
import sys
from typing import Any

HASH = re.compile(r"[0-9a-f]{64}\Z")
EXPECTED = {"C": 400, "O": 240, "U": 160, "A": 80}
MAX_BYTES = 4 * 1024 * 1024
LIMIT_ERRORS = 30


def _hash(x: str) -> str:
    return sha256(x.encode("utf-8")).hexdigest()


def _valid_hash(x: object) -> bool:
    return type(x) is str and HASH.fullmatch(x) is not None


def lint(doc: object) -> dict[str, Any]:
    errors: list[str] = []
    def fail(code: str) -> None:
        if len(errors) < LIMIT_ERRORS:
            errors.append(code)
    if type(doc) is not dict or doc.get("schema") != "SMC7_GATE_A_STRUCTURAL_V0":
        return {"status": "REFUSED", "errors": ["INVALID_SCHEMA"], "verified": []}
    cases = doc.get("cases")
    if type(cases) is not list or len(cases) != 1000:
        return {"status": "REFUSED", "errors": ["EXPECTED_1000_CASES"], "verified": []}

    ids: set[str] = set()
    content_split: dict[str, str] = {}
    source_context_pairs: set[tuple[str, str]] = set()
    family_split: dict[str, str] = {}
    document_split: dict[str, str] = {}
    group: dict[str, list[tuple[str, str]]] = defaultdict(list)
    tallies: Counter[tuple[str, str]] = Counter()
    for i, case in enumerate(cases):
        n = f"case[{i}]"
        if type(case) is not dict:
            fail(n + ":INVALID_CASE")
            continue
        cid = case.get("case_id")
        split = case.get("split")
        stratum = case.get("stratum")
        family = case.get("family_id")
        document = case.get("document_id")
        source = case.get("source_sha256")
        context = case.get("context_sha256")
        rights = case.get("rights_id")
        if type(cid) is not str or not cid or len(cid) > 120 or cid in ids:
            fail(n + ":DUPLICATE_OR_INVALID_ID")
        else:
            ids.add(cid)
        if split not in ("pilot", "holdout"):
            fail(n + ":INVALID_SPLIT")
            continue
        if stratum not in ("C", "O", "U", "A"):
            fail(n + ":INVALID_STRATUM")
            continue
        tallies[(split, stratum)] += 1
        if (type(family) is not str or not family or len(family) > 120 or
                type(document) is not str or not document or len(document) > 120):
            fail(n + ":INVALID_GROUP")
            continue
        if not _valid_hash(source) or not _valid_hash(context):
            fail(n + ":INVALID_SOURCE_OR_CONTEXT_HASH")
            continue
        pair = (source, context)
        if pair in source_context_pairs:
            fail(n + ":DUPLICATE_SOURCE_CONTEXT")
        source_context_pairs.add(pair)
        for value, seen, tag in ((source, content_split, "SOURCE"),
                                 (family, family_split, "FAMILY"),
                                 (document, document_split, "DOCUMENT")):
            old = seen.setdefault(value, split)
            if old != split:
                fail(n + ":PILOT_HOLDOUT_" + tag + "_LEAK")
        if type(rights) is not str or not rights or case.get("rights_status") != "CLEARED":
            fail(n + ":RIGHTS_DECLARATION_MISSING")
        refs = case.get("annotators")
        if type(refs) is not dict or set(refs) != {"A", "B", "C"}:
            fail(n + ":ANNOTATOR_ROLES_MISSING")
        elif any(type(refs[r]) is not str or not refs[r] for r in ("A", "B", "C")):
            fail(n + ":ANNOTATOR_ID_INVALID")
        elif len(set(refs.values())) != 3:
            fail(n + ":ANNOTATORS_NOT_DISTINCT")
        gold = case.get("gold_paths_sha256")
        if type(gold) is not list or not gold or len(gold) > 8 or any(
                not _valid_hash(x) for x in gold):
            fail(n + ":GOLD_PATH_DIGESTS_INVALID")
        if case.get("blind_a_b") is not True or case.get("adjudicated") is not True:
            fail(n + ":BLIND_OR_ADJUDICATION_NOT_ATTESTED")
        if stratum == "A":
            if case.get("gold_status") not in ("MULTI", "CONTEXT_INSUFFICIENT"):
                fail(n + ":AMBIGUOUS_CASE_NOT_ATTESTED")
            elif case.get("gold_status") == "MULTI" and (
                    type(gold) is not list or len(set(gold)) < 2):
                fail(n + ":MULTI_NEEDS_TWO_DISTINCT_PATHS")
        if stratum == "C":
            reading = case.get("target_reading_sha256")
            if not _valid_hash(reading):
                fail(n + ":TARGET_READING_HASH_MISSING")
            else:
                group[family].append((split, reading))

    if sum(v for (split, _), v in tallies.items() if split == "pilot") != 120:
        fail("PILOT_COUNT_NOT_120")
    for stratum, count in EXPECTED.items():
        if tallies[("holdout", stratum)] != count:
            fail("HOLDOUT_" + stratum + "_COUNT_NOT_" + str(count))
    c_families = {
        k: records for k, records in group.items()
        if all(split == "holdout" for split, _ in records)
    }
    if len(c_families) != 100:
        fail("C_FAMILY_COUNT_NOT_100")
    for family, records in c_families.items():
        if len(records) != 4 or len({reading for _, reading in records}) < 2:
            fail("C_FAMILY_NOT_FOUR_CONTRASTIVE_READINGS:" + family)
    result = {
        "status": "STRUCTURAL_CHECKS_PASSED_NOT_SCIENTIFICALLY_FROZEN" if not errors
                  else "REFUSED",
        "errors": errors,
        "holdout_counts": {k: tallies[("holdout", k)] for k in EXPECTED},
        "pilot_count": sum(v for (split, _), v in tallies.items() if split == "pilot"),
        "c_orthographic_families": len(c_families),
        "verified": (["counts", "digest_shapes", "declared_blinded_roles",
                      "pilot_holdout_id_nonoverlap", "c_family_structure"]
                     if not errors else []),
        "not_verified": ["genuine_human_independence", "annotation_truth",
                         "source_legal_rights", "text_accessibility",
                         "original_text_offsets", "training_contamination",
                         "model_dictionary_integrity", "gold_snapshot_immutability"],
    }
    return result


def _synthetic_case(i: int, split: str, stratum: str, family: str,
                    reading: str) -> dict[str, object]:
    return {
        "case_id": "SYNTHETIC_" + str(i), "split": split, "stratum": stratum,
        "family_id": family, "document_id": "SYNTHETIC_DOC_" + str(i),
        "source_sha256": _hash("SYNTHETIC_SOURCE_" + str(i)),
        "context_sha256": _hash("SYNTHETIC_CONTEXT_" + str(i)),
        "rights_id": "SYNTHETIC_ONLY", "rights_status": "CLEARED",
        "annotators": {"A": "SYNTHETIC_A", "B": "SYNTHETIC_B",
                       "C": "SYNTHETIC_C"},
        "blind_a_b": True, "adjudicated": True,
        "gold_paths_sha256": [_hash("SYNTHETIC_PATH_" + str(i))] + (
            [_hash("SYNTHETIC_ALT_" + str(i))] if stratum == "A" else []),
        "gold_status": "MULTI" if stratum == "A" else "SINGLE",
        "target_reading_sha256": _hash(reading),
    }


def self_test() -> None:
    cases: list[dict[str, object]] = []
    i = 0
    for family in range(100):
        for j in range(4):
            cases.append(_synthetic_case(i, "holdout", "C",
                        "HETERO_" + str(family), "VARIANT_" + str(j % 2)))
            i += 1
    for stratum, count in (("O", 240), ("U", 160), ("A", 80)):
        for _ in range(count):
            cases.append(_synthetic_case(i, "holdout", stratum,
                        "FAMILY_" + str(i), "R"))
            i += 1
    for _ in range(120):
        cases.append(_synthetic_case(i, "pilot", "O",
                    "PILOT_FAMILY_" + str(i), "R"))
        i += 1
    doc = {"schema": "SMC7_GATE_A_STRUCTURAL_V0", "cases": cases}
    assert lint(doc)["status"].startswith("STRUCTURAL_CHECKS_PASSED")
    cases[0]["annotators"] = {"A": "same", "B": "same", "C": "third"}
    assert lint(doc)["status"] == "REFUSED"
    cases[0]["annotators"] = {"A": "x", "B": "y", "C": "z"}
    cases[0]["family_id"] = "PILOT_FAMILY_880"
    assert lint(doc)["status"] == "REFUSED"
    cases[0]["family_id"] = "HETERO_0"
    cases[1]["target_reading_sha256"] = _hash("VARIANT_0")
    cases[3]["target_reading_sha256"] = _hash("VARIANT_0")
    assert lint(doc)["status"] == "REFUSED"
    cases[1]["target_reading_sha256"] = _hash("VARIANT_1")
    cases[3]["target_reading_sha256"] = _hash("VARIANT_1")
    cases[0]["source_sha256"] = cases[1]["source_sha256"]
    cases[0]["context_sha256"] = cases[1]["context_sha256"]
    assert lint(doc)["status"] == "REFUSED"
    with tempfile.TemporaryDirectory() as d:
        good = Path(d) / "good.json"
        good.write_bytes(b"{}")
        assert _read_bounded(good) == b"{}"
        alias = Path(d) / "symlink.json"
        alias.symlink_to(good)
        try:
            _read_bounded(alias)
        except (OSError, ValueError):
            pass
        else:
            raise AssertionError("symlink was accepted")
    print("SELF_TEST_PASSED: admission, reviewers, split, contrast, duplicates, no-follow file")


def _read_bounded(path: Path) -> bytes:
    """No-follow, regular-file only, bounded descriptor read; no stat/read race."""
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise ValueError("UNSAFE_PLATFORM")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
            raise ValueError("INVALID_INPUT")
        parts: list[bytes] = []
        total = 0
        while True:
            part = os.read(fd, min(65536, MAX_BYTES + 1 - total))
            if not part:
                break
            total += len(part)
            if total > MAX_BYTES:
                raise ValueError("INVALID_INPUT")
            parts.append(part)
        after = os.fstat(fd)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError("CHANGED_DURING_READ")
        return b"".join(parts)
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Untrusted metadata lint only; NOT gold freeze")
    parser.add_argument("manifest", nargs="?", help="private rights-cleared metadata JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.manifest:
        parser.error("manifest required unless --self-test")
    f = Path(args.manifest)
    try:
        doc = json.loads(_read_bounded(f).decode("utf-8"))
    except (UnicodeError, ValueError, OSError, RecursionError):
        print(json.dumps({"status": "REFUSED", "errors": ["INVALID_INPUT_OR_JSON"]}))
        return 2
    result = lint(doc)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"].startswith("STRUCTURAL_CHECKS_PASSED") else 2


if __name__ == "__main__":
    sys.exit(main())
