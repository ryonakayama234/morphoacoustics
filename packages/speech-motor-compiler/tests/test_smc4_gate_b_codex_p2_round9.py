"""Ninth GitHub Codex P2: runtime input trust-boundary preregression.

Audited exact source+docs 15ed2f09c2da008e3d5b8a75e10ed6c204778e69.
Tests precede generalized normalization/validation and preserve negative CI.
No phonetic, body, audio or public TaskScore claims.
"""
from dataclasses import replace
from fractions import Fraction as Q

import pytest

from morphoacoustics_smc.model import Event
from morphoacoustics_smc.smc4_lexicon import (
    TimeAnchor, TimeRelation,
)
from test_smc4_gate_b_preregistered import run, standard


def test_codex9_self_referential_non_predicate_context_rejected_without_crash():
    loop = []
    loop.append(loop)
    result = run(context={"f": loop})
    assert result.plan is None
    assert result.receipt.code == "INVALID_INPUT"
    assert result.receipt.input_fingerprint


def test_codex9_deep_nonpredicate_context_rejected_without_recursion_crash():
    value = ["leaf"]
    for _ in range(1050):
        value = [value]
    result = run(context={"f": value})
    assert result.plan is None
    assert result.receipt.code == "INVALID_INPUT"
    assert result.receipt.input_fingerprint


@pytest.mark.parametrize("bad_paths", [(0,), ("text",), (None,)])
def test_codex9_invalid_pronunciation_path_declaration(bad_paths):
    result = run(paths=bad_paths)
    assert result.plan is None and result.receipt.code == "INVALID_INPUT"


def test_codex9_unhashable_path_identifier_fail_closed():
    p, _ = standard()
    r = run(path=replace(p, path_id=[]))
    assert r.plan is None and r.receipt.code == "INVALID_INPUT"


def test_codex9_unhashable_goal_slot_identifier_fail_closed():
    _, lex = standard()
    b = lex.bundles[0]
    invalid_slot = replace(b.slots[0], slot_id=[])
    r = run(lex=replace(lex, bundles=(
        replace(b, slots=(invalid_slot,) + b.slots[1:]), lex.bundles[1])))
    assert r.plan is None and r.receipt.code == "INVALID_PLAN"


def test_codex9_unhashable_candidate_definition_reference_fail_closed():
    _, lex = standard()
    b = lex.bundles[0]
    bad = replace(b.slots[0].candidates[0], definition_id=[])
    slot = replace(b.slots[0], candidates=(bad,))
    r = run(lex=replace(lex, bundles=(
        replace(b, slots=(slot,) + b.slots[1:]), lex.bundles[1])))
    assert r.plan is None and r.receipt.code == "INVALID_PLAN"


def test_codex9_unhashable_scope_target_reference_fail_closed():
    _, lex = standard()
    b = lex.bundles[0]
    bad = replace(b, target_unit_ids=([],))
    r = run(lex=replace(lex, bundles=(bad, lex.bundles[1])))
    assert r.plan is None and r.receipt.code == "INVALID_PLAN"


def test_codex9_invalid_anchor_reference_diagnostics_order_independent():
    a1 = TimeAnchor("missing1", "source", Event.ONSET, Q(0))
    a2 = TimeAnchor("missing2", "source", Event.ONSET, Q(0))
    a = run(anchors=(a1, a2))
    b = run(anchors=(a2, a1))
    assert a.plan is None and b.plan is None
    assert a.receipt.code == b.receipt.code == "INVALID_PLAN"
    assert a.receipt.detail == b.receipt.detail
    assert a.receipt.digest == b.receipt.digest


def test_codex9_invalid_relation_reference_diagnostics_order_independent():
    q1 = TimeRelation("missing1", "source", Event.ONSET,
                      "P2", "source", Event.OFFSET, Q(0))
    q2 = TimeRelation("missing2", "source", Event.ONSET,
                      "P2", "source", Event.OFFSET, Q(0))
    a = run(relations=(q1, q2))
    b = run(relations=(q2, q1))
    assert a.plan is None and b.plan is None
    assert a.receipt.code == b.receipt.code == "INVALID_PLAN"
    assert a.receipt.detail == b.receipt.detail
    assert a.receipt.digest == b.receipt.digest
