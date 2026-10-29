"""Preregistered SMC-7 L1-R software-slice falsifiers (not Japanese G2P)."""
from __future__ import annotations

from dataclasses import fields
from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import ANY

import pytest

from morphoacoustics_smc.reading_paths import ReadingPath, ReadingUnit
from morphoacoustics_smc.l1r_evidence import (
    EvidenceManifest,
    context_hash,
    evaluate_paths,
    make_l1_envelope,
    manifest_id,
    select_l1_path,
)


def fixture(context: str = "文脈A", version: str = "2026.10"):
    digest = context_hash(context, "r1")
    m = EvidenceManifest("manual-research", version, "a" * 64, "policy-1", "internal-fixture", digest)
    e = manifest_id(m)
    p = ReadingPath("p1", (ReadingUnit("u1", "コウオツ", 0, 2),), e)
    q = ReadingPath("p2", (ReadingUnit("u1", "カンオツ", 0, 2),), e)
    return m, p, q


def test_t01_proposal_only_and_selection_is_separate():
    m, p, _ = fixture()
    env = make_l1_envelope("甲乙", "r1", "文脈A", m, (p,))
    assert env.status == "PROPOSED"
    assert env.code == "OK"
    assert env.proposal is not None
    assert env.proposal.paths == (p,)
    assert "smc5" not in {f.name for f in fields(env)}
    assert "smc6" not in {f.name for f in fields(env)}
    assert "audio" not in {f.name for f in fields(env)}
    missing = select_l1_path(env, "甲乙", "r1", "文脈A", m, (p,), "", "human")
    assert (missing.status, missing.code) == ("REJECTED", "SELECTION_REQUIRED")
    decision = select_l1_path(env, "甲乙", "r1", "文脈A", m, (p,), "p1", "human")
    assert (decision.status, decision.code, decision.selected_path_id) == ("SELECTED", "OK", "p1")


def test_t02_ordered_paths_not_cross_spliced():
    m, p, q = fixture()
    a = make_l1_envelope("甲乙", "r1", "文脈A", m, (p, q))
    b = make_l1_envelope("甲乙", "r1", "文脈A", m, (q, p))
    assert a.status == b.status == "PROPOSED"
    assert a.proposal and a.proposal.paths == (p, q)
    assert a.envelope_id != b.envelope_id
    assert make_l1_envelope("甲乙", "r1", "文脈A", m, (p, p)).status == "REJECTED"


def test_t03_empty_abstains_four_candidates_refuse_without_clipping():
    m, p, _ = fixture()
    empty = make_l1_envelope("甲乙", "r1", "文脈A", m, ())
    assert (empty.status, empty.code, empty.proposal) == ("ABSTAIN", "NO_CANDIDATES", None)
    many = tuple(replace(p, path_id=f"p{i}") for i in range(4))
    overflow = make_l1_envelope("甲乙", "r1", "文脈A", m, many)
    assert (overflow.status, overflow.code, overflow.proposal) == ("REJECTED", "CANDIDATE_LIMIT", None)


def test_t04_stale_selection_wrong_actor_and_unknown_path():
    m, p, _ = fixture()
    env = make_l1_envelope("甲乙", "r1", "文脈A", m, (p,))
    for overrides in [
        ("r2", "文脈A", m, (p,), "p1", "human"),
        ("r1", "文脈B", m, (p,), "p1", "human"),
        ("r1", "文脈A", m, (p,), "p9", "human"),
        ("r1", "文脈A", m, (p,), "p1", ""),
    ]:
        revision, context, evidence, paths, selected, actor = overrides
        got = select_l1_path(env, "甲乙", revision, context, evidence, paths, selected, actor)
        assert got.status == "REJECTED"
        assert got.selected_path_id is None


def test_t05_context_and_provider_are_part_of_l1_identity():
    m1, p1, _ = fixture()
    a = make_l1_envelope("甲乙", "r1", "文脈A", m1, (p1,))
    m2, p2, _ = fixture(context="文脈B")
    b = make_l1_envelope("甲乙", "r1", "文脈B", m2, (p2,))
    m3, p3, _ = fixture(version="2026.11")
    c = make_l1_envelope("甲乙", "r1", "文脈A", m3, (p3,))
    assert len({a.envelope_id, b.envelope_id, c.envelope_id}) == 3


def test_t06_span_and_manifest_forgeries_are_rejected():
    m, p, _ = fixture()
    bad = ReadingPath("p1", (ReadingUnit("u1", "コウ", 0, 1),), manifest_id(m))
    assert make_l1_envelope("甲乙", "r1", "文脈A", m, (bad,)).status == "REJECTED"
    no_evidence = replace(p, evidence_id="synthetic-not-this-manifest")
    assert make_l1_envelope("甲乙", "r1", "文脈A", m, (no_evidence,)).code == "EVIDENCE_MISMATCH"
    env = make_l1_envelope("甲乙", "r1", "文脈A", m, (p,))
    forged = replace(env, envelope_id=ANY)
    assert select_l1_path(forged, "甲乙", "r1", "文脈A", m, (p,), "p1", "human").status == "REJECTED"
    forged_manifest = replace(m, provider_version=ANY)
    assert make_l1_envelope("甲乙", "r1", "文脈A", forged_manifest, (p,)).status == "REJECTED"


def test_t07_length_before_scan_bad_types_and_surrogates():
    m, p, _ = fixture()
    assert make_l1_envelope("甲乙", "r1", "x" * 1000000, m, (p,)).code == "CONTEXT_LIMIT"
    assert make_l1_envelope("甲乙", "r1", "\ud800", m, (p,)).status == "REJECTED"
    assert make_l1_envelope("甲乙", "r1", ["context"], m, (p,)).status == "REJECTED"
    assert make_l1_envelope("甲乙", "r1", "文脈A", m, [p]).status == "REJECTED"
    assert make_l1_envelope("甲乙", "r1", "文脈A", m, (p, dict())).status == "REJECTED"
    assert make_l1_envelope("甲乙" * 200, "r1", "文脈A", m, (p,)).status == "REJECTED"


def test_t08_no_inferred_linguistic_or_body_outputs():
    m, p, _ = fixture()
    env = make_l1_envelope("甲乙", "r1", "文脈A", m, (p,))
    names = {f.name for f in fields(env)}
    forbidden = {"f0", "waveform", "audio", "muscle", "body", "confidence", "natural_timing", "smc5", "smc6"}
    assert not (names & forbidden)


def test_t09_repeated_processes_are_deterministic():
    script = """
import json
from morphoacoustics_smc.reading_paths import ReadingPath, ReadingUnit
from morphoacoustics_smc.l1r_evidence import EvidenceManifest, context_hash, manifest_id, make_l1_envelope
m = EvidenceManifest("manual-research","2026.10","a"*64,"policy-1","internal-fixture",context_hash("文脈A","r1"))
p = ReadingPath("p1", (ReadingUnit("u1","コウオツ",0,2),), manifest_id(m))
x = make_l1_envelope("甲乙","r1","文脈A",m,(p,))
print(json.dumps([x.status,x.envelope_id]))
"""
    a = subprocess.check_output([sys.executable, "-c", script], text=True)
    b = subprocess.check_output([sys.executable, "-c", script], text=True)
    assert a == b
    assert json.loads(a)[0] == "PROPOSED"


def test_t11_evaluator_uses_full_path_and_preserves_denominators():
    gold = (("カキ",), ("コウ", "カン"), ("シオ",))
    candidates = (("カキ",), ("カン", "コウ"), ())
    m = evaluate_paths(gold, candidates)
    assert m.n == 3
    assert (m.hits_at_1, m.hits_at_2, m.hits_at_3) == (2, 2, 2)
    assert m.recall_at_1 == Fraction(2, 3)
    assert m.burden == Fraction(3, 3)
    assert evaluate_paths((("ア",),), ((),)).recall_at_3 == Fraction(0)
    with pytest.raises(ValueError):
        evaluate_paths((("ア",),), (("ア", "ア"),))
    with pytest.raises(ValueError):
        evaluate_paths((("ア",),), (("ア", "イ", "ウ", "エ"),))
    with pytest.raises(ValueError):
        evaluate_paths((("ア",),), (("ア",), ("イ",)))
