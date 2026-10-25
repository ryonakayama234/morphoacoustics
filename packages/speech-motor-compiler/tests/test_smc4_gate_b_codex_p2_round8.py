"""Eighth independent Codex review P2: preregression tests before repairs.

Audited source+docs HEAD: 999a2207148dd675be8ad9da0d6fdcb66286a2a6.
Three bounded symbolic/software falsifiers: cyclic input identity beyond fixed
refinement radius; malformed timing type/coordinate; canonical invalid-Task
definition diagnostics. No phonetic/body/audio evidence.
"""
from dataclasses import replace
from fractions import Fraction as Q

import pytest

from morphoacoustics_smc.model import Event
from morphoacoustics_smc.smc4_lexicon import (
    Predicate, TimeAnchor, TimeRelation,
)
from test_smc4_gate_b_preregistered import run, standard


def test_codex8_cyclic_fingerprint_binds_distant_leaf_beyond_64_edges():
    bad = Predicate("NOT")
    object.__setattr__(bad, "operands", (bad,))
    leaf_a = Predicate("TRUE")
    leaf_b = Predicate("FALSE")
    for _ in range(70):
        leaf_a = Predicate("NOT", operands=(leaf_a,))
        leaf_b = Predicate("NOT", operands=(leaf_b,))
    p_a = Predicate("AND", operands=(bad, leaf_a))
    p_b = Predicate("AND", operands=(bad, leaf_b))
    _, lex = standard()
    a = replace(lex.bundles[0], context=p_a)
    b = replace(lex.bundles[0], context=p_b)
    r1 = run(lex=replace(lex, bundles=(a, lex.bundles[1])))
    r2 = run(lex=replace(lex, bundles=(b, lex.bundles[1])))
    assert r1.plan is None and r2.plan is None
    assert r1.receipt.code == r2.receipt.code == "INVALID_PLAN"
    assert r1.receipt.input_fingerprint != r2.receipt.input_fingerprint
    assert r1.receipt.digest != r2.receipt.digest


@pytest.mark.parametrize("anchors,relations", [
    ((TimeAnchor([], "source", Event.ONSET, Q(0)),), ()),
    ((0,), ()),
    ((TimeAnchor("P1", "source", Event.ONSET, Q(0)),), (None,)),
    ((), (TimeRelation([], "source", Event.ONSET,
                       "P2", "source", Event.OFFSET, Q(0)),)),
    ((), (TimeRelation("P1", "source", Event.ONSET,
                       [], "source", Event.OFFSET, Q(0)),)),
])
def test_codex8_malformed_timing_declarations_fail_closed(anchors, relations):
    result = run(anchors=anchors, relations=relations)
    assert result.plan is None
    assert result.receipt.code == "INVALID_PLAN"
    assert result.receipt.input_fingerprint


def test_codex8_invalid_definitions_are_order_independent():
    _, lex = standard()
    defs = tuple(replace(d, capabilities="bad") for d in lex.definitions)
    a = run(lex=replace(lex, definitions=defs))
    b = run(lex=replace(lex, definitions=tuple(reversed(defs))))
    assert a.plan is None and b.plan is None
    assert a.receipt.code == b.receipt.code == "INVALID_PLAN"
    assert a.receipt.detail == b.receipt.detail
    assert a.receipt.digest == b.receipt.digest
    assert {"tractA", "src", "tractB"}.issubset(set(a.receipt.detail))


def test_codex8_valid_timing_and_definitions_preserved():
    result = run(anchors=(TimeAnchor("P1", "source", Event.ONSET, Q(0)),))
    assert result.plan is not None
    assert result.receipt.status == "MAPPED_SYMBOLIC"
