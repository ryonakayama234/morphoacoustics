"""SMC7 L0 frozen F01–F14; test-only commit must be RED before source exists.

All evidence is synthetic/software. No Japanese G2P/phonetic or physical claim.
"""
import copy
from dataclasses import replace
from fractions import Fraction
import json

from test_smc5_preregistered import valid, encoded
from morphoacoustics_smc.symbolic_bridge import compile_wire
from morphoacoustics_smc.temporal_stn import TemporalScenario, analyze_temporal_wire
from morphoacoustics_smc.reading_paths import (
    ReadingUnit, ReadingPath, propose_kana, make_proposal, compile_selected,
)


def proposal():
    paths = (
        ReadingPath("p1", (
            ReadingUnit("P1", "a", 0, 1),
            ReadingUnit("P2", "i", 1, 2),
        ), "MANUAL_UNVERIFIED"),
        ReadingPath("p2", (
            ReadingUnit("Q1", "ai", 0, 2),
        ), "MANUAL_UNVERIFIED"),
    )
    return make_proposal("甲乙", "r1", paths)


def scenario(horizon=2):
    return TemporalScenario(
        study_id="smc7-compat", lane="COMPATIBILITY",
        horizon_s=Fraction(horizon), minimum_duration_s=Fraction(1, 100),
        constraints=(),
    )


def test_f01_kana_character_baseline_not_phonetic():
    p = propose_kana("ありがとう", "r1")
    assert p.status == "PROPOSED" and len(p.paths) == 1
    assert [(x.symbol, x.start_offset, x.end_offset) for x in p.paths[0].units] == [
        (c, i, i + 1) for i, c in enumerate("ありがとう")
    ]
    assert p.paths[0].evidence_id == "ORTHOGRAPHIC_ONLY"


def test_f02_unknown_kanji_and_mixed_script_abstain():
    for s in ("生物を運ぶ", "ありがとう🙂", "abc", "あ1", "あー"):
        p = propose_kana(s, "r1")
        assert p.status == "REJECTED" and p.code == "UNKNOWN_READING"
        assert not p.paths


def test_f03_multiple_complete_paths_no_implicit_selection():
    p = proposal()
    assert p.status == "PROPOSED" and len(p.paths) == 2
    r = compile_selected(p, None, encoded(valid()), scenario())
    assert r.status == "REFUSED" and r.code == "SELECTION_REQUIRED"
    assert r.smc5 is None and r.smc6 is None


def test_f04_exact_source_coverage_and_silent_positions():
    assert make_proposal("あ、い", "r1", (
        ReadingPath("p", (ReadingUnit("U1", "あ", 0, 1), ReadingUnit("U2", "い", 2, 3)), "manual"),
    )).status == "PROPOSED"
    cases = [
        (ReadingUnit("U1", "あ", 0, 1),),
        (ReadingUnit("U1", "あ", 0, 2), ReadingUnit("U2", "い", 1, 2)),
        (ReadingUnit("U2", "い", 1, 2), ReadingUnit("U1", "あ", 0, 1)),
        (ReadingUnit("U1", "あ", 0, 1), ReadingUnit("U1", "い", 1, 2)),
    ]
    for units in cases:
        p = make_proposal("あい", "r1", (ReadingPath("p", units, "manual"),))
        assert p.status == "REJECTED" and p.paths == ()


def test_f05_unicode_original_identity_and_surrogate_refusal():
    a = propose_kana("が", "r1")
    b = propose_kana("か\u3099", "r1")
    c = propose_kana("が", "r2")
    assert a.status == "PROPOSED" and b.status == "REJECTED"
    assert a.proposal_digest != c.proposal_digest
    assert propose_kana("\ud800", "r1").status == "REJECTED"


def test_f06_bounded_caps_and_wrong_type():
    assert propose_kana("あ" * 257, "r1").code == "SOURCE_LIMIT"
    assert propose_kana(5, "r1").status == "REJECTED"
    assert make_proposal("あ", "r1", tuple(
        ReadingPath(f"p{i}", (ReadingUnit("U1", "あ", 0, 1),), "manual")
        for i in range(9)
    )).code == "PATH_LIMIT"
    assert make_proposal("あ" * 33, "r1", (ReadingPath(
        "p", tuple(ReadingUnit(f"U{i}", "あ", i, i+1) for i in range(33)), "manual"
    ),)).code == "UNIT_LIMIT"


def test_f07_exact_direct_smc5_and_smc6_compatibility():
    raw = encoded(valid())
    p = proposal()
    r = compile_selected(p, "p1", raw, scenario())
    direct5 = compile_wire(raw)
    direct6 = analyze_temporal_wire(raw, scenario())
    assert r.status == "SYMBOLIC_READY" and r.smc5 == direct5 and r.smc6 == direct6
    assert r.smc6 is not None and r.smc6.status == "SAT_UNIQUE"
    assert r.smc5 is not None and r.smc5.receipt.candidate_digest


def test_f08_unsat_retains_valid_upstream_evidence():
    raw = encoded(valid())
    r = compile_selected(proposal(), "p1", raw, scenario(Fraction(1, 10)))
    assert r.status == "TEMPORAL_REFUSED"
    assert r.smc5 is not None and r.smc5.receipt.status == "RESOLVED"
    assert r.smc6 is not None and r.smc6.status == "UNSAT"
    assert r.smc6.events == ()
    assert r.smc6.receipt is not None
    assert r.smc6.receipt.source_candidate_digest == r.smc5.receipt.candidate_digest


def test_f09_wire_must_match_selected_path_and_source_exactly():
    raw = valid()
    mutations = [
        ("segment", "source_revision", "r2"),
        ("segment", "source_text", "甲丙"),
        ("pronunciation", "selected_path_id", "p2"),
    ]
    for key, field, value in mutations:
        d = copy.deepcopy(raw)
        d[key][field] = value
        r = compile_selected(proposal(), "p1", encoded(d), scenario())
        assert r.status == "REFUSED" and r.smc5 is None and r.smc6 is None
    d = copy.deepcopy(raw)
    d["pronunciation"]["paths"][0]["units"][0]["symbol"] = "wrong"
    r = compile_selected(proposal(), "p1", encoded(d), scenario())
    assert r.status == "REFUSED" and r.smc5 is None


def test_f10_smc5_unmapped_preserved_no_temporal():
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"] = []
    r = compile_selected(proposal(), "p1", encoded(d), scenario())
    assert r.status == "REFUSED" and r.stage == "SMC5"
    assert r.smc5 is not None and r.smc5.receipt.code == "UNMAPPED"
    assert r.smc6 is None


def test_f11_noncompatibility_lane_refused():
    sc = replace(scenario(), lane="RESEARCH_OVERRIDE")
    r = compile_selected(proposal(), "p1", encoded(valid()), sc)
    assert r.status == "REFUSED" and r.smc5 is None and r.smc6 is None


def test_f12_determinism_revisions_and_symbols():
    a = proposal()
    b = proposal()
    assert a == b
    assert compile_selected(a, "p1", encoded(valid()), scenario()) == compile_selected(b, "p1", encoded(valid()), scenario())
    alt = make_proposal("甲乙", "r1", (
        ReadingPath("p1", (ReadingUnit("P1", "a", 0, 1), ReadingUnit("P2", "u", 1, 2)), "manual"),
    ))
    assert a.proposal_digest != alt.proposal_digest


def test_f13_no_bodily_claim_or_audio_in_public_research_shape():
    p = proposal()
    r = compile_selected(p, "p1", encoded(valid()), scenario())
    for obj in (p, r):
        for field in ("organ", "f0", "pressure", "waveform", "body", "audio", "physical_state"):
            assert not hasattr(obj, field)


def test_f14_independent_coverage_and_legacy_oracle():
    p = proposal()
    # Independent *test-side* reconstruction, not a library coverage helper.
    for path in p.paths:
        spans = [set(range(u.start_offset, u.end_offset)) for u in path.units]
        assert set.union(*spans) == set(range(len(p.source_text)))
        assert sum(len(s) for s in spans) == len(p.source_text)
    raw = encoded(valid())
    direct = json.loads(raw)
    matched = p.paths[0]
    assert [(u.unit_id, u.symbol, u.start_offset, u.end_offset) for u in matched.units] == [
        (u["unit_id"], u["symbol"], u["start_offset"], u["end_offset"])
        for u in direct["pronunciation"]["paths"][0]["units"]
    ]
    assert compile_selected(p, "p1", raw, scenario()).smc6 == analyze_temporal_wire(raw, scenario())
