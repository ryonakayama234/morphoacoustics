"""Post-review tests for Codex P2: rejection receipt must bind full input.

Test-only RED must precede source repair, preserving the reviewer failure.
"""
from dataclasses import replace
from fractions import Fraction as Q

from morphoacoustics_smc.model import Event
from morphoacoustics_smc.smc4_lexicon import TimeAnchor

from test_smc4_gate_b_preregistered import run, standard


def test_codex_p2_different_context_same_rejection_is_distinguishable():
    _, lex = standard()
    missing = replace(lex, bundles=lex.bundles[:1])
    a = run(lex=missing)
    b = run(lex=missing, context={"devoiced": "yes"})
    assert a.receipt.code == b.receipt.code == "UNMAPPED"
    assert a.plan is None and b.plan is None
    assert a.receipt.input_fingerprint != b.receipt.input_fingerprint
    assert a.receipt.digest != b.receipt.digest


def test_codex_p2_distinct_failed_timing_inputs_distinguishable():
    a = (TimeAnchor("P1", "source", Event.ONSET, Q(0)),
         TimeAnchor("P1", "source", Event.ONSET, Q(1)))
    b = (TimeAnchor("P1", "source", Event.ONSET, Q(0)),
         TimeAnchor("P1", "source", Event.ONSET, Q(2)))
    ra = run(anchors=a)
    rb = run(anchors=b)
    assert ra.receipt.code == rb.receipt.code == "INVALID_PLAN"
    assert ra.receipt.input_fingerprint != rb.receipt.input_fingerprint
    assert ra.receipt.digest != rb.receipt.digest


def test_codex_p2_rejection_hash_invariant_under_bundle_permutation():
    _, lex = standard()
    extra = replace(lex.bundles[0], bundle_id="another")
    first = replace(lex, bundles=lex.bundles + (extra,))
    second = replace(lex, bundles=(extra,) + lex.bundles)
    a, b = run(lex=first), run(lex=second)
    assert a.receipt.code == b.receipt.code == "AMBIGUOUS"
    assert a.receipt.input_fingerprint == b.receipt.input_fingerprint
    assert a.receipt.digest == b.receipt.digest


def test_success_receipt_input_fingerprint_changes_with_unused_alternative_path():
    p, lex = standard()
    from morphoacoustics_smc.smc4_lexicon import PronunciationPath
    from morphoacoustics_smc.model import PronunciationUnit
    extra = PronunciationPath("other",
                              (PronunciationUnit("Q", "q", 0, 2),),
                              ((0, 2),), True)
    first = run(paths=(p,), selected="R")
    second = run(paths=(p, extra), selected="R")
    assert first.plan == second.plan
    assert first.receipt.input_fingerprint != second.receipt.input_fingerprint
    assert first.receipt.digest != second.receipt.digest
