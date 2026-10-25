"""SMC-4 Gate B tenth Codex review — intentionally failing REVISE witnesses.

Source+docs candidate audited: f05fda35640a47e868574d367f68cdd81a28da2e.
The current candidate remains intentionally unmodified. These tests preserve
the exact Gate B falsifiers; red CI is a STOP/REVISE finding, not an invitation
to declare GO or merge into main. Synthetic software only.
"""
from dataclasses import replace

from test_smc4_gate_b_preregistered import run, standard


def test_codex10_distinct_malformed_context_mapping_key_types_have_distinct_receipts():
    integer_key = run(context={1: []})
    string_key = run(context={"1": []})
    assert integer_key.plan is None and string_key.plan is None
    assert integer_key.receipt.code == string_key.receipt.code == "INVALID_INPUT"
    assert integer_key.receipt.input_fingerprint != string_key.receipt.input_fingerprint
    assert integer_key.receipt.digest != string_key.receipt.digest


def test_codex10_cyclic_invalid_unordered_definition_permutation_same_receipt():
    a = []
    b = []
    a.append(b)
    b.extend((a, "leaf"))
    _, lex = standard()
    first = run(lex=replace(lex, definitions=(a, b)))
    second = run(lex=replace(lex, definitions=(b, a)))
    assert first.plan is None and second.plan is None
    assert first.receipt.code == second.receipt.code == "INVALID_PLAN"
    assert first.receipt.detail == second.receipt.detail
    assert first.receipt.input_fingerprint == second.receipt.input_fingerprint
    assert first.receipt.digest == second.receipt.digest
