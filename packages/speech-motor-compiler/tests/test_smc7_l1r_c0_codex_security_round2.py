"""SMC-7 C0 second independent security review S201-S205: tests before fix."""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from morphoacoustics_smc import l1r_real_g2p as c0


def _dictionary(tmp_path: Path) -> Path:
    d = tmp_path / "dic"
    d.mkdir()
    (d / "sys.dic").write_bytes(b"fake-jtalk-dic")
    (d / "matrix.bin").write_bytes(b"matrix")
    return d


def test_r201_nul_input_must_refuse_before_reader(tmp_path: Path):
    d = _dictionary(tmp_path)
    spy = MagicMock(return_value="コウオツ")
    got = c0.read_b0("甲\x00乙", d, fixture_reader=spy)
    assert (got.status, got.code, got.kana) == ("REFUSED", "INVALID_SOURCE", None)
    spy.assert_not_called()


def test_r202_active_external_user_dictionary_directive_rejected(tmp_path: Path):
    d = _dictionary(tmp_path)
    (d / "dicrc").write_text("cost-factor = 800\nuserdic = /outside/untracked.dic\n", encoding="utf-8")
    with pytest.raises(ValueError, match="DICTIONARY_EXTERNAL_USERDIC"):
        c0.fingerprint_dictionary(d)
    reader = MagicMock(return_value="コウ")
    result = c0.read_b0("甲", d, fixture_reader=reader)
    assert (result.status, result.code, result.kana) == ("REFUSED", "DICTIONARY_UNVERIFIED", None)
    reader.assert_not_called()


def test_r202_comment_is_not_active_dictionary_directive(tmp_path: Path):
    d = _dictionary(tmp_path)
    (d / "dicrc").write_text("# userdic = /outside/dic\ncost-factor = 800\n", encoding="utf-8")
    assert len(c0.fingerprint_dictionary(d)) == 64


def test_r203_fifo_substitution_never_blocks_before_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    if not hasattr(os, "mkfifo"):
        pytest.skip("POSIX FIFO only")
    d = _dictionary(tmp_path)
    former_open = os.open
    injected = False

    def swap(path: object, flags: int, *args: object, **kwargs: object) -> int:
        nonlocal injected
        if path == "sys.dic" and kwargs.get("dir_fd") is not None and not injected:
            assert flags & os.O_NONBLOCK, "leaf must be opened nonblocking"
            injected = True
            (d / "sys.dic").unlink()
            os.mkfifo(d / "sys.dic")
        return former_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(c0.os, "open", swap)
    with pytest.raises((ValueError, OSError, AssertionError)):
        c0.fingerprint_dictionary(d)
    assert injected is True or (d / "sys.dic").is_file()


def test_r204_corpus_path_symlink_swap_before_open_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    original = tmp_path / "input.jsonl"
    outside = tmp_path / "outside.jsonl"
    row = json.dumps({
        "key": "甲_コウ_0", "normalized_text": "甲だ。", "normalized_pron": "<コウ>ダ。",
    }, ensure_ascii=False) + "\n"
    original.write_text(row, encoding="utf-8")
    outside.write_text(row, encoding="utf-8")
    former_open = os.open
    swapped = False

    def replace_before_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        nonlocal swapped
        if str(path) == str(original) and not swapped:
            swapped = True
            original.unlink()
            original.symlink_to(outside)
        return former_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(c0.os, "open", replace_before_open)
    with pytest.raises((ValueError, OSError)):
        c0.audit_joyo_jsonl(original)
    assert swapped is True


def test_r205_regular_corpus_still_audits_and_digest_is_bound(tmp_path: Path):
    original = tmp_path / "valid.jsonl"
    original.write_text(json.dumps({
        "key": "甲_コウ_0", "normalized_text": "甲だ。", "normalized_pron": "<コウ>ダ。",
    }, ensure_ascii=False) + "\n", encoding="utf-8")
    first = c0.audit_joyo_jsonl(original)
    assert (first.status, first.rows, first.valid_rows) == ("AUDITED", 1, 1)
    assert c0.audit_joyo_jsonl(original, expected_sha256=first.file_sha256) == first
