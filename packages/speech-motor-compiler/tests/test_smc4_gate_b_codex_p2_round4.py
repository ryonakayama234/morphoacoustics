"""Fourth Github Codex P2 preregression: invalid capability declarations.

Reviewed prior HEAD: 3249259704aeebac3b845b62da3d3d41457a314d.
Only synthetic runtime input integrity; not a physical capability claim.
"""
from dataclasses import replace

import pytest

from test_smc4_gate_b_preregistered import run, standard


@pytest.mark.parametrize("invalid", [
    "capA", ("capA", 1), (None, "capA"), (True, "capA"),
    ("",), ("capA", chr(0xD800)), ("capA", "capA"),
])
def test_codex4_invalid_task_capability_decl_fails_closed(invalid):
    _, lex = standard()
    defs = list(lex.definitions)
    defs[0] = replace(defs[0], capabilities=invalid)
    r = run(lex=replace(lex, definitions=tuple(defs)))
    assert r.plan is None
    assert r.receipt.code == "INVALID_PLAN"
    assert r.receipt.input_fingerprint


def test_codex4_valid_unordered_capabilities_stay_normalized():
    _, lex = standard()
    defs = list(lex.definitions)
    defs[0] = replace(defs[0], capabilities=("flow", "contact"))
    a = run(lex=replace(lex, definitions=tuple(defs)))
    defs[0] = replace(defs[0], capabilities=("contact", "flow"))
    b = run(lex=replace(lex, definitions=tuple(defs)))
    assert a.plan == b.plan
    assert a.receipt.digest == b.receipt.digest
    assert a.plan is not None
    relevant = [t for t in a.plan.tasks if t.goal_kind == "FUNCTIONAL_tractA"]
    assert len(relevant) == 1
    assert relevant[0].capability_requirements == ("contact", "flow")
