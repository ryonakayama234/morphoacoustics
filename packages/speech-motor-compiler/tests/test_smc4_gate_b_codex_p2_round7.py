"""Seventh GitHub Codex P2 adversarial regression; TEST-FIRST RED.

Reviewed source+docs 7e93f9c66a7f69ed3f84a2f9cf37caece6d01839.
Tests bounded by subprocess timeout where the original DAG evaluator expands
2**40 references. No phonetic/physical claims.
"""
from dataclasses import replace
from multiprocessing import get_context

from morphoacoustics_smc.smc4_lexicon import Predicate
from test_smc4_gate_b_preregistered import run, standard


def _lex_with(predicate):
    _, lex = standard()
    return replace(lex, bundles=(replace(lex.bundles[0], context=predicate),
                                 lex.bundles[1]))


def _compile_large_dag(queue):
    sub = Predicate("TRUE")
    for _ in range(40):
        sub = Predicate("AND", operands=(sub, sub))
    result = run(lex=_lex_with(sub))
    queue.put((result.receipt.code, result.plan is not None))


def test_codex7_shared_predicate_dag_evaluation_must_be_linear_not_exponential():
    ctx = get_context("fork")  # project isolated CI is Linux
    queue = ctx.Queue()
    child = ctx.Process(target=_compile_large_dag, args=(queue,))
    child.start()
    child.join(timeout=2.5)
    if child.is_alive():
        child.terminate()
        child.join(timeout=3)
        assert False, "unmemoized immutable DAG evaluation exceeded bounded runtime"
    assert child.exitcode == 0
    code, mapped = queue.get(timeout=2)
    assert code == "MAPPED_SYMBOLIC" and mapped


def test_codex7_reused_height_cannot_bypass_full_root_to_leaf_bound():
    p = Predicate("TRUE")
    retained = []
    for i in range(1, 1001):
        p = Predicate("NOT", operands=(p,))
        if i % 100 == 0:
            retained.append(p)
    asc = Predicate("AND", operands=tuple(retained))
    desc = Predicate("AND", operands=tuple(reversed(retained)))
    a = run(lex=_lex_with(asc))
    b = run(lex=_lex_with(desc))
    assert a.plan is None and b.plan is None
    assert a.receipt.code == b.receipt.code == "INVALID_PLAN"
    assert a.receipt.digest == b.receipt.digest


def test_codex7_small_height_dag_still_accepts_shared_subexpression():
    p = Predicate("TRUE")
    for _ in range(8):
        p = Predicate("AND", operands=(p, p))
    result = run(lex=_lex_with(p))
    assert result.plan is not None and result.receipt.code == "MAPPED_SYMBOLIC"


def test_codex7_cyclic_and_operand_permutation_have_same_rejected_fingerprint():
    x = Predicate("NOT")
    y = Predicate("AND")
    object.__setattr__(x, "operands", (y,))
    object.__setattr__(y, "operands", (x, Predicate("TRUE")))
    a = Predicate("AND", operands=(x, y))
    b = Predicate("AND", operands=(y, x))
    ra = run(lex=_lex_with(a))
    rb = run(lex=_lex_with(b))
    assert ra.plan is None and rb.plan is None
    assert ra.receipt.code == rb.receipt.code == "INVALID_PLAN"
    assert ra.receipt.input_fingerprint == rb.receipt.input_fingerprint
    assert ra.receipt.digest == rb.receipt.digest
