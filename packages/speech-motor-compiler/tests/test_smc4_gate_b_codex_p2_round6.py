"""SMC-4 Gate B sixth independent Codex review regression, TEST ONLY.

Reviewed exact source+docs HEAD: 034d4efa479c29732f2d3e1578ebd4105792a2a4.
P2: nested/cyclic predicate fingerprinting; shared DAG predicate node identity;
order-independent invalid-rule diagnostics. Commit tests before modifying code.
Synthetic software claims only.
"""
from dataclasses import replace

from morphoacoustics_smc.smc4_lexicon import Predicate
from test_smc4_gate_b_preregistered import run, standard


def _changed_bundle(predicate):
    _, lex = standard()
    return replace(lex, bundles=(replace(lex.bundles[0], context=predicate),
                                 lex.bundles[1]))


def test_codex6_400_nested_not_returns_a_rejection_receipt_without_recursion_crash():
    p = Predicate("TRUE")
    for _ in range(400):
        p = Predicate("NOT", operands=(p,))
    outcome = run(lex=_changed_bundle(p))
    assert outcome.plan is None
    assert outcome.receipt.code == "INVALID_PLAN"
    assert outcome.receipt.input_fingerprint


def test_codex6_self_cycle_returns_fail_closed_receipt():
    p = Predicate("NOT")
    object.__setattr__(p, "operands", (p,))
    result = run(lex=_changed_bundle(p))
    assert result.plan is None
    assert result.receipt.code == "INVALID_PLAN"
    assert result.receipt.input_fingerprint


def test_codex6_shared_predicate_subtree_is_not_mistaken_for_a_cycle():
    same = Predicate("TRUE")
    shared = Predicate("AND", operands=(same, same))
    distinct = Predicate("AND", operands=(Predicate("TRUE"), Predicate("TRUE")))
    r1 = run(lex=_changed_bundle(shared))
    r2 = run(lex=_changed_bundle(distinct))
    assert r1.plan is not None and r2.plan is not None
    assert r1.receipt.status == r2.receipt.status == "MAPPED_SYMBOLIC"
    assert r1.plan == r2.plan
    assert r1.receipt.digest == r2.receipt.digest


def test_codex6_invalid_bundle_diagnostics_are_declaration_order_independent():
    _, lex = standard()
    a = replace(lex.bundles[0], context=Predicate("BAD"))
    b = replace(lex.bundles[1], context=Predicate("BAD"))
    first = run(lex=replace(lex, bundles=(a, b)))
    second = run(lex=replace(lex, bundles=(b, a)))
    assert first.plan is None and second.plan is None
    assert first.receipt.code == second.receipt.code == "INVALID_PLAN"
    assert first.receipt.detail == second.receipt.detail
    assert first.receipt.digest == second.receipt.digest
    assert "BA" in first.receipt.detail and "BI" in first.receipt.detail


def test_codex6_invalid_candidate_rule_diagnostics_are_order_independent():
    _, lex = standard()
    b0 = lex.bundles[0]
    bad0 = replace(b0.slots[0].candidates[0], context=Predicate("BAD"))
    bad1 = replace(b0.slots[1].candidates[0], context=Predicate("BAD"))
    changed = replace(b0, slots=(
        replace(b0.slots[0], candidates=(bad0,)),
        replace(b0.slots[1], candidates=(bad1,)),
    ))
    ordered = run(lex=replace(lex, bundles=(changed, lex.bundles[1])))
    reversed_slots = replace(changed, slots=tuple(reversed(changed.slots)))
    reversed_result = run(lex=replace(lex, bundles=(lex.bundles[1], reversed_slots)))
    assert ordered.plan is None and reversed_result.plan is None
    assert ordered.receipt.code == reversed_result.receipt.code == "INVALID_PLAN"
    assert ordered.receipt.detail == reversed_result.receipt.detail
    assert ordered.receipt.digest == reversed_result.receipt.digest
