"""Frozen independent-Codex S01-S05 regressions BEFORE implementation repair."""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from morphoacoustics_smc import l1r_real_g2p as c0


def _dictionary(tmp_path: Path) -> Path:
    d = tmp_path / "dic"
    d.mkdir()
    (d / "sys.dic").write_bytes(b"test-sys-dictionary")
    (d / "matrix.bin").write_bytes(b"test-matrix")
    return d


def test_s01_real_path_uses_private_path_bound_engine_no_global_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    d = _dictionary(tmp_path)
    constructions: list[tuple[bytes, bytes, str]] = []

    class PrivateEngine:
        def __init__(self, dn_mecab: bytes, userdic: bytes = b""):
            p = Path(os.fsdecode(dn_mecab))
            assert p.is_dir()
            assert p != d
            assert (p / "sys.dic").read_bytes() == (d / "sys.dic").read_bytes()
            constructions.append((dn_mecab, userdic, c0.fingerprint_dictionary(p)))

        def g2p(self, text: str, kana: bool = False) -> str:
            assert text == "人気"
            assert kana is True
            return "ニンキ"

    def forbidden_global(*args: object, **kwargs: object) -> str:
        raise AssertionError("cached pyopenjtalk.g2p MUST NOT be used")

    fake_module = SimpleNamespace(
        g2p=forbidden_global, OpenJTalk=PrivateEngine,
        OPEN_JTALK_DICT_DIR=b"/forged/unrelated/global/dictionary",
    )
    monkeypatch.setattr(c0.metadata, "version", lambda _: "0.4.1")
    monkeypatch.setattr(c0, "import_module", lambda _: fake_module)
    got = c0.read_b0("人気", d)
    assert (got.status, got.mode, got.kana) == ("READ", "PYOPENJTALK_REAL", "ニンキ")
    assert len(constructions) == 1
    assert constructions[0][1] == b""
    assert constructions[0][2] == got.dictionary_digest


def test_s02_link_swap_after_inventory_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    d = _dictionary(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"test-sys-dictionary")
    previous_open = os.open
    swapped = False

    def swap_during_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        nonlocal swapped
        if path == "sys.dic" and "dir_fd" in kwargs and not swapped:
            swapped = True
            (d / "sys.dic").unlink()
            (d / "sys.dic").symlink_to(outside)
        return previous_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(c0.os, "open", swap_during_open)
    with pytest.raises((OSError, ValueError)):
        c0.fingerprint_dictionary(d)
    assert swapped is True


def test_s03_directory_entry_and_depth_budgets(tmp_path: Path):
    d = _dictionary(tmp_path)
    for i in range(513):
        (d / f"empty-{i:04d}").mkdir()
    with pytest.raises(ValueError, match="DICTIONARY_LIMIT"):
        c0.fingerprint_dictionary(d)

    deep = _dictionary(tmp_path / "different") if False else tmp_path / "deep"
    deep.mkdir()
    (deep / "sys.dic").write_bytes(b"a")
    child = deep
    for i in range(10):
        child = child / f"level-{i}"
        child.mkdir()
    with pytest.raises(ValueError, match="DICTIONARY_LIMIT"):
        c0.fingerprint_dictionary(deep)


@pytest.mark.parametrize("key", ["あ__0", "甲__0", "A_エー_0"])
def test_s05_invalid_target_or_empty_key_reading_never_admitted(tmp_path: Path, key: str):
    import json
    p = tmp_path / "rows.jsonl"
    p.write_text(json.dumps({
        "key": key,
        "normalized_text": "甲だ。" if key.startswith("甲") else "あだ。",
        "normalized_pron": "<ア>ダ。",
    }, ensure_ascii=False) + "\n", encoding="utf-8")
    got = c0.audit_joyo_jsonl(p)
    assert (got.status, got.valid_rows, got.invalid_rows) == (
        "RECONCILIATION_REQUIRED", 0, 1,
    )
    assert got.distinct_target_kanji == 0
    assert ("INVALID_KEY", 1) in got.failure_codes
