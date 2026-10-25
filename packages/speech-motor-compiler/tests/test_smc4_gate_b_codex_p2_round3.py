"""Third GitHub Codex P2 review of exact SHA 827c66d.

Runtime malformed Unicode/priorities and unordered declaration fingerprint
equivalence must fail before repairs, then pass without changing SMC-3.
"""
from dataclasses import replace
from fractions import Fraction as Q

import pytest

from morphoacoustics_smc.smc4_lexicon import ShareDecision
from test_smc4_gate_b_preregistered import run, standard


def test_codex3_surrogate_in_rejected_share_episode_never_crashes():
    episode = chr(0xD800)
    r = run(shares=(ShareDecision(episode, (("P1", "source"),
                                              ("P2", "source"))),))
    assert r.plan is None
    assert r.receipt.code in ("INVALID_PLAN", "INVALID_INPUT")
    assert r.receipt.input_fingerprint


def test_codex3_surrogate_in_unsupported_bundle_id_never_crashes():
    _, lex = standard()
    bad = replace(lex.bundles[0], bundle_id=chr(0xD800),
                  target_scope_kind="MULTI_UNIT", target_unit_ids=("P1", "P2"))
    r = run(lex=replace(lex, bundles=lex.bundles + (bad,)))
    assert r.plan is None
    assert r.receipt.code in ("UNSUPPORTED_MAPPING_SCOPE", "INVALID_INPUT")
    assert r.receipt.input_fingerprint


@pytest.mark.parametrize("priorities", [(1, "2"), ("9", "10"), (True, 0)])
def test_codex3_malformed_bundle_priorities_refused(priorities):
    _, lex = standard()
    a = replace(lex.bundles[0], priority=priorities[0])
    b = replace(lex.bundles[0], bundle_id="BA2", priority=priorities[1])
    r = run(lex=replace(lex, bundles=(a, b, lex.bundles[1])))
    assert r.plan is None and r.receipt.code == "INVALID_PLAN"


@pytest.mark.parametrize("priority", [True, "1", Q(1, 2)])
def test_codex3_malformed_slot_priorities_refused(priority):
    _, lex = standard()
    first = lex.bundles[0]
    slot = first.slots[0]
    c = replace(slot.candidates[0], priority=priority)
    changed = replace(first, slots=(replace(slot, candidates=(c,)), first.slots[1]))
    r = run(lex=replace(lex, bundles=(changed, lex.bundles[1])))
    assert r.plan is None and r.receipt.code == "INVALID_PLAN"


def test_codex3_capabilities_permutation_does_not_change_receipts():
    _, lex = standard()
    defs = list(lex.definitions)
    defs[0] = replace(defs[0], capabilities=("capA", "capB"))
    a = run(lex=replace(lex, definitions=tuple(defs)))
    defs[0] = replace(defs[0], capabilities=("capB", "capA"))
    b = run(lex=replace(lex, definitions=tuple(defs)))
    assert a.plan == b.plan
    assert a.receipt.digest == b.receipt.digest
    assert a.receipt.input_fingerprint == b.receipt.input_fingerprint


def test_codex3_unsupported_scope_target_order_does_not_change_refusal():
    _, lex = standard()
    bad = replace(lex.bundles[0], bundle_id="B12",
                  target_scope_kind="MULTI_UNIT", target_unit_ids=("P1", "P2"))
    a = run(lex=replace(lex, bundles=lex.bundles + (bad,)))
    b = run(lex=replace(lex, bundles=lex.bundles + (
        replace(bad, target_unit_ids=("P2", "P1")),)))
    assert a.plan is None and b.plan is None
    assert a.receipt.code == b.receipt.code == "UNSUPPORTED_MAPPING_SCOPE"
    assert a.receipt.detail == b.receipt.detail
    assert a.receipt.digest == b.receipt.digest
    assert a.receipt.input_fingerprint == b.receipt.input_fingerprint
