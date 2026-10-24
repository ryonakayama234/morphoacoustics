"""Independent Codex P2 review of SMC-4 Gate B SHA 1be16c5.

Reproduce fail-closed malformed coverage, projected duplicate exact edges,
deterministic unsupported-scope diagnostics and rule-content provenance.
Test code is committed before fixes, retaining RED CI evidence.
"""
from dataclasses import replace
from fractions import Fraction as Q

import pytest

from morphoacoustics_smc.model import Event
from morphoacoustics_smc.smc4_lexicon import (
    Predicate, ShareDecision, TimeRelation,
)
from test_smc4_gate_b_preregistered import run, standard


@pytest.mark.parametrize("required", [(0,), None, ((0, "2"),)])
def test_codex_round2_invalid_runtime_coverage_fails_closed(required):
    p, _ = standard()
    result = run(path=replace(p, required_spans=required))
    assert result.plan is None and result.receipt.code == "INVALID_INPUT"


@pytest.mark.parametrize("complete", ["false", 1, None])
def test_codex_round2_nonboolean_complete_cannot_claim_reading(complete):
    p, _ = standard()
    result = run(path=replace(p, complete=complete))
    assert result.plan is None and result.receipt.code == "INVALID_INPUT"


def test_codex_round2_shared_edge_projection_is_idempotent():
    relation1 = TimeRelation("P1", "source", Event.ONSET,
                             "P1", "source", Event.OFFSET, Q(1))
    relation2 = TimeRelation("P2", "source", Event.ONSET,
                             "P2", "source", Event.OFFSET, Q(1))
    shared = ShareDecision("e", (("P1", "source"), ("P2", "source")))
    a = run(relations=(relation1, relation2), shares=(shared,))
    b = run(relations=(relation2, relation1), shares=(shared,))
    assert a.plan is not None and b.plan is not None
    assert a.receipt.status == b.receipt.status == "MAPPED_SYMBOLIC"
    assert a.receipt.digest == b.receipt.digest
    assert len(a.plan.couplings) == 1


def test_codex_round2_multiple_unsupported_scope_errors_are_canonical():
    p, lex = standard()
    bad1 = replace(lex.bundles[0], bundle_id="B12", target_scope_kind="MULTI_UNIT",
                   target_unit_ids=("P1", "P2"))
    bad2 = replace(lex.bundles[1], bundle_id="B21", target_scope_kind="MULTI_UNIT",
                   target_unit_ids=("P2", "P1"))
    la = replace(lex, bundles=lex.bundles + (bad1, bad2))
    lb = replace(lex, bundles=(bad2,) + lex.bundles + (bad1,))
    a, b = run(lex=la), run(lex=lb)
    assert a.receipt.code == b.receipt.code == "UNSUPPORTED_MAPPING_SCOPE"
    assert a.plan is None and b.plan is None
    assert a.receipt.detail == b.receipt.detail
    assert "B12" in a.receipt.detail and "B21" in a.receipt.detail
    assert a.receipt.digest == b.receipt.digest


def test_codex_round2_context_predicate_content_alters_provenance():
    _, lex = standard()
    original = run(lex=lex, context={"f": "yes"})
    changed_b = replace(lex.bundles[0], context=Predicate("EQ", "f", "yes"))
    modified = run(lex=replace(lex, bundles=(changed_b, lex.bundles[1])),
                   context={"f": "yes"})
    assert original.plan == modified.plan
    assert original.receipt.input_fingerprint != modified.receipt.input_fingerprint
    assert original.receipt.digest != modified.receipt.digest
