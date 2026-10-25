"""Fifth GitHub Codex P2 regression suite, committed before source repair.

Reviewed candidate: e321d5b71830aef8a5418496013913569b237333.
Probes reject malformed predicates and share-member coordinates without
uncaught exceptions, preserving a source-bound rejection receipt.
Synthetic compiler integrity tests ONLY; no phonetic/physical claim.
"""
from dataclasses import replace

import pytest

from morphoacoustics_smc.smc4_lexicon import Predicate, ShareDecision
from test_smc4_gate_b_preregistered import run, standard


@pytest.mark.parametrize("bad_predicate", [
    Predicate("EQ", ["f"], "yes"),  # hash-unsafe key
    Predicate("EQ", "f", True),   # bool must not silently match/lose
    Predicate("NOT", operands=None),
    Predicate("NOT", operands=(Predicate("TRUE"), None)),
    Predicate("AND", operands=(Predicate("TRUE"), None)),
    Predicate("OR", operands="not-a-tuple"),
    Predicate("NOT", operands=()),
    Predicate("UNKNOWN_OPERATOR"),
    Predicate("EQ", "", "yes"),
    Predicate("EQ", "f", chr(0xD800)),
])
def test_codex5_bad_bundle_predicates_fail_closed(bad_predicate):
    _, lex = standard()
    changed = replace(lex.bundles[0], context=bad_predicate)
    result = run(lex=replace(lex, bundles=(changed, lex.bundles[1])),
                 context={"f": "yes"})
    assert result.plan is None
    assert result.receipt.code == "INVALID_PLAN"
    assert result.receipt.input_fingerprint


@pytest.mark.parametrize("bad_members", [
    (["P1", "source"], ["P2", "source"]),  # unhashable pair
    (("P1", "source"), ["P2", "source"]),
    (("P1", "source"), ("P2",)),  # incomplete coordinate
    (("P1", "source"), ("P2", 3)),
    (("P1", "source"), ("P2", chr(0xD800))),
    (("P1", "source"), "P2"),
    "P1sourceP2source",
    None,
])
def test_codex5_bad_share_members_fail_closed(bad_members):
    r = run(shares=(ShareDecision("episode", bad_members),))
    assert r.plan is None
    assert r.receipt.code == "INVALID_PLAN"
    assert r.receipt.input_fingerprint


def test_codex5_invalid_predicate_cannot_disappear_as_false_competitor():
    _, lex = standard()
    invalid_high_priority = replace(
        lex.bundles[0], bundle_id="B_BAD",
        context=Predicate("EQ", "f", True), priority=999,
    )
    r = run(lex=replace(lex, bundles=lex.bundles + (invalid_high_priority,)),
            context={"f": "yes"})
    assert r.plan is None and r.receipt.code == "INVALID_PLAN"


def test_codex5_valid_nested_predicate_and_share_are_unchanged():
    _, lex = standard()
    nested = Predicate("AND", operands=(
        Predicate("EQ", "f", "yes"),
        Predicate("NOT", operands=(Predicate("EQ", "g", "no"),)),
    ))
    b = replace(lex.bundles[0], context=nested)
    shared = ShareDecision("episode", (("P1", "source"), ("P2", "source")))
    result = run(lex=replace(lex, bundles=(b, lex.bundles[1])),
                 context={"f": "yes", "g": "yes"}, shares=(shared,))
    assert result.plan is not None and len(result.plan.tasks) == 3
    assert len(result.plan.associations) == 4
