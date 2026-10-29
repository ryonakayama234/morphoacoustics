"""SMC-7 C0 preregistered real-baseline and corpus audit tests.

Fake G2P readers prove software invariants only; never constitute B0 results.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from morphoacoustics_smc.l1r_real_g2p import (
    BaselineReading,
    audit_joyo_jsonl,
    fingerprint_dictionary,
    read_b0,
)


def _dic(tmp_path: Path) -> Path:
    p = tmp_path / "dic"
    p.mkdir()
    (p / "sys.dic").write_bytes(b"fake-openjtalk-dictionary\x00")
    (p / "matrix.bin").write_bytes(b"metadata\x01")
    return p


def test_t01_dictionary_fingerprint_is_deterministic_content_addressed(tmp_path: Path):
    d = _dic(tmp_path)
    first = fingerprint_dictionary(d)
    assert len(first) == 64
    assert fingerprint_dictionary(d) == first
    (d / "matrix.bin").write_bytes(b"metadata\x02")
    assert fingerprint_dictionary(d) != first
    a = fingerprint_dictionary(d)
    (d / "matrix.bin").rename(d / "renamed.bin")
    assert fingerprint_dictionary(d) != a


def test_t02_directory_attack_and_missing_directory_refuse(tmp_path: Path):
    with pytest.raises(ValueError):
        fingerprint_dictionary(tmp_path / "missing")
    d = _dic(tmp_path)
    (d / "symlink").symlink_to(d / "sys.dic")
    with pytest.raises(ValueError):
        fingerprint_dictionary(d)
    with pytest.raises(ValueError):
        fingerprint_dictionary(tmp_path)


def test_t03_fixture_is_explicitly_not_a_real_b0(tmp_path: Path):
    d = _dic(tmp_path)
    reader = MagicMock(return_value="ヒトケノナイバショ")
    a = read_b0("人気のない場所", d, fixture_reader=reader)
    assert (a.status, a.code, a.mode) == ("READ", "OK", "FIXTURE_ONLY")
    assert a.kana == "ヒトケノナイバショ"
    assert a.dictionary_digest == fingerprint_dictionary(d)
    reader.assert_called_once_with("人気のない場所")
    assert a.source_digest is not None
    assert not hasattr(a, "proposal")
    assert not hasattr(a, "smc5")


def test_t04_unsupported_l1_source_still_can_be_text_only_b0(tmp_path: Path):
    d = _dic(tmp_path)
    a = read_b0("ラーメン・A", d, fixture_reader=lambda _: "ラーメンエー")
    assert (a.status, a.mode, a.l1_source_eligible) == ("READ", "FIXTURE_ONLY", False)
    assert a.kana == "ラーメンエー"


def test_t05_bad_output_and_input_fail_closed(tmp_path: Path):
    d = _dic(tmp_path)
    for output in ("", "漢字", "ひらがな", "カ" * 513, MagicMock()):
        z = read_b0("甲", d, fixture_reader=lambda _, x=output: x)
        assert z.status == "REFUSED"
        assert z.kana is None
    z = read_b0("甲" * 257, d, fixture_reader=lambda _: "コウ")
    assert z.code == "SOURCE_LIMIT"
    z = read_b0("\ud800", d, fixture_reader=lambda _: "コウ")
    assert z.status == "REFUSED"
    z = read_b0(["untrusted"], d, fixture_reader=lambda _: "コウ")
    assert z.status == "REFUSED"


def test_t06_provider_failure_or_unverified_dictionary_never_claims_read(tmp_path: Path):
    d = _dic(tmp_path)
    def crash(_: str) -> str:
        raise RuntimeError("provider unavailable")
    x = read_b0("人気", d, fixture_reader=crash)
    assert (x.status, x.code, x.kana) == ("REFUSED", "PROVIDER_FAILURE", None)
    y = read_b0("人気", tmp_path / "no-such-dic", fixture_reader=lambda _: "ニンキ")
    assert (y.status, y.code, y.kana) == ("REFUSED", "DICTIONARY_UNVERIFIED", None)


def test_t07_marked_gold_is_not_original_source_alignment(tmp_path: Path):
    p = tmp_path / "toy.jsonl"
    rows = [
        {"key": "固_かためる_0", "normalized_text": "結束を固める。", "normalized_pron": "ケッソクオ<カタメ>ル。"},
        {"key": "精_セイ_0", "normalized_text": "精密な仕事。", "normalized_pron": "<セー>ミツナシゴト。"},
        {"key": "麺_メン_0", "normalized_text": "ラーメンの麺。", "normalized_pron": "ラーメンノ<メン>。"},
    ]
    p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    q = audit_joyo_jsonl(p)
    assert q.status == "AUDITED"
    assert (q.rows, q.valid_rows, q.invalid_rows) == (3, 3, 0)
    assert q.distinct_target_kanji == 3
    assert q.l1_source_eligible == 2  # source contains ー for the last item
    assert len(q.file_sha256) == 64
    assert not hasattr(q, "target_accuracy")
    assert not hasattr(q, "gold_paths")


def test_t08_duplicate_keys_and_bad_markers_are_not_admitted(tmp_path: Path):
    p = tmp_path / "bad.jsonl"
    p.write_text("\n".join([
        json.dumps({"key": "固_かためる_0", "normalized_text": "固める。", "normalized_pron": "<カタメ>ル。"}, ensure_ascii=False),
        json.dumps({"key": "固_かためる_0", "normalized_text": "固める。", "normalized_pron": "<カタメ>ル。"}, ensure_ascii=False),
        json.dumps({"key": "変_ヘン_0", "normalized_text": "変わる。", "normalized_pron": "<ヘン><カワ>ル。"}, ensure_ascii=False),
        json.dumps({"key": "空_クウ_0", "normalized_text": "空だ。", "normalized_pron": "クウダ。"}, ensure_ascii=False),
    ]) + "\n", encoding="utf-8")
    q = audit_joyo_jsonl(p)
    assert (q.status, q.rows, q.valid_rows, q.invalid_rows) == ("INVALID_DATASET", 4, 1, 3)
    assert q.failure_codes == (("DUPLICATE_KEY", 1), ("INVALID_TARGET_MARKER", 2))


def test_t09_unicode_bytes_and_size_are_bounded(tmp_path: Path):
    p = tmp_path / "huge.jsonl"
    p.write_bytes(b" " * (8 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match="DATASET_LIMIT"):
        audit_joyo_jsonl(p)
    p.write_bytes(b"\xff")
    with pytest.raises(ValueError, match="INVALID_UTF8"):
        audit_joyo_jsonl(p)


def test_t10_real_b0_absent_must_not_fall_back_to_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    d = _dic(tmp_path)
    # An arbitrary nonexistent required distribution cannot be accepted as 0.4.1.
    monkeypatch.setenv("SMC7_C0_REQUIRE_UNAVAILABLE_PROVIDER", "1")
    a = read_b0("人気", d)
    assert a.status == "REFUSED"
    assert a.mode != "FIXTURE_ONLY"
    assert a.kana is None
