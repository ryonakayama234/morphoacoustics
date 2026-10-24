"""SMC-4 Gate B preregistered synthetic falsifiers; written before implementation.

Scientific phonetic/physical truth is deliberately not tested.
"""
from dataclasses import replace
from fractions import Fraction as Q

from morphoacoustics_smc.model import PronunciationUnit
from morphoacoustics_smc.smc4_lexicon import (
    PronunciationPath, Predicate, TaskDefinition, SlotCandidate,
    GoalSlot, TemplateBundle, TaskLexicon, ShareDecision, compile_lexicon,
)

YES = Predicate("TRUE")
DEVOICE = Predicate("EQ", "devoiced", "yes")


def definition(name: str) -> TaskDefinition:
    return TaskDefinition(name, "r1", "q_" + name, "scalar", "FUNCTIONAL_" + name)


def candidate(name: str, definition_id: str, lo: int = 0, hi: int = 2,
              predicate: Predicate = YES, priority: int | None = None) -> SlotCandidate:
    return SlotCandidate(name, definition_id, "r1", Q(lo), Q(hi),
                         predicate, priority, "synthetic:" + name)


def bundle(name: str, unit: str, symbol: str, *slots: GoalSlot,
           predicate: Predicate = YES, priority: int | None = None,
           scope: str = "EXACT_ONE_SELECTED_UNIT") -> TemplateBundle:
    return TemplateBundle(name, unit, symbol, slots, predicate, priority,
                          "fixture", scope)


def standard():
    units = (PronunciationUnit("P1", "p1", 0, 1),
             PronunciationUnit("P2", "p2", 1, 2))
    path = PronunciationPath("R", units, ((0, 2),), True)
    defs = (definition("tractA"), definition("tractB"), definition("src"))
    b1 = bundle("BA", "P1", "p1",
                GoalSlot("tract", (candidate("TA", "tractA"),)),
                GoalSlot("source", (candidate("TS1", "src"),)))
    b2 = bundle("BI", "P2", "p2",
                GoalSlot("tract", (candidate("TI", "tractB"),)),
                GoalSlot("source", (candidate("TS2", "src"),)))
    lex = TaskLexicon("lex-v1", "rule-v1", defs, (b1, b2))
    return path, lex


def run(path=None, lex=None, selected="R", shares=(), context=None, paths=None,
        source="甲乙", **kwargs):
    default_path, default_lex = standard()
    return compile_lexicon("seg", source, "synthetic", "fixture",
                           (path or default_path,) if paths is None else paths,
                           selected, lex or default_lex, context or {},
                           shares=shares, **kwargs)


def test_f01_required_slots_and_explicit_compatible_share():
    r = run(shares=(ShareDecision("episode", (("P1", "source"), ("P2", "source"))),))
    assert r.receipt.status == "MAPPED_SYMBOLIC"
    assert r.plan is not None
    assert len(r.plan.tasks) == 3
    assert len(r.plan.associations) == 4
    assert "TS1" in r.receipt.evidence and "TS2" in r.receipt.evidence


def test_f02_no_share_keeps_independent_instances():
    r = run()
    assert r.plan is not None
    assert len(r.plan.tasks) == 4
    assert len(r.plan.associations) == 4
    assert len({t.task_id for t in r.plan.tasks}) == 4


def test_f04_missing_bundle_refuses_complete_graph():
    p, lex = standard()
    r = run(lex=replace(lex, bundles=lex.bundles[:1]))
    assert r.receipt.code == "UNMAPPED" and r.plan is None


def test_f05_and_f30_competing_true_bundles_are_exclusive():
    p, lex = standard()
    extra = replace(lex.bundles[0], bundle_id="BA2")
    r = run(lex=replace(lex, bundles=lex.bundles + (extra,)))
    assert r.receipt.code == "AMBIGUOUS" and r.plan is None
    r2 = run(lex=replace(lex, bundles=(extra,) + lex.bundles))
    assert r.receipt.digest == r2.receipt.digest


def test_f16_two_readings_never_combine():
    p, lex = standard()
    alt = PronunciationPath("R2", (PronunciationUnit("Q", "q", 0, 2),),
                            ((0, 2),), True)
    alt_bundle = bundle("BQ", "Q", "q",
                        GoalSlot("tract", (candidate("TQ", "tractA"),)))
    l2 = replace(lex, bundles=lex.bundles + (alt_bundle,))
    result = run(paths=(p, alt), selected=None, lex=l2)
    assert result.receipt.code == "AMBIGUOUS_PRONUNCIATION_PATH"
    assert result.plan is None
    for path_id, expected in (("R", {"P1", "P2"}), ("R2", {"Q"})):
        result = run(paths=(p, alt), selected=path_id, lex=l2)
        assert result.plan is not None
        assert {u.unit_id for u in result.plan.pronunciation_units} == expected


def test_f17_missing_path_coverage_is_unresolved_not_unmapped():
    p, lex = standard()
    partial = replace(p, units=p.units[:1])
    r = run(path=partial)
    assert r.receipt.code == "UNRESOLVED_PRONUNCIATION" and r.plan is None


def test_f18_unknown_specific_context_must_not_fallback():
    p, lex = standard()
    specific = replace(lex.bundles[0], bundle_id="specific",
                       context=DEVOICE, priority=2)
    generic = replace(lex.bundles[0], priority=1)
    lex = replace(lex, bundles=(generic, specific, lex.bundles[1]))
    missing = run(lex=lex)
    assert missing.receipt.code == "INSUFFICIENT_CONTEXT" and missing.plan is None
    known_no = run(lex=lex, context={"devoiced": "no"})
    assert known_no.plan is not None
    known_yes = run(lex=lex, context={"devoiced": "yes"})
    assert known_yes.plan is not None
    assert "specific" in known_yes.receipt.evidence


def test_f21_incompatible_share_refuses_without_splitting():
    p, lex = standard()
    b2 = lex.bundles[1]
    s = b2.slots[1]
    c = replace(s.candidates[0], lower=Q(3), upper=Q(4))
    b2 = replace(b2, slots=(b2.slots[0], replace(s, candidates=(c,))))
    lex = replace(lex, bundles=(lex.bundles[0], b2))
    share = ShareDecision("episode", (("P1", "source"), ("P2", "source")))
    r = run(lex=lex, shares=(share,))
    assert r.receipt.code == "TASK_SHARE_CONFLICT" and r.plan is None


def test_f23_required_additive_slots():
    p, lex = standard()
    p = replace(p, units=p.units[:1], required_spans=((0, 1),))
    r = run(path=p, source="甲")
    assert r.plan is not None and len(r.plan.tasks) == 2


def test_f24_alternative_candidates_need_priority():
    p, lex = standard()
    b = lex.bundles[0]
    sl = b.slots[0]
    second = replace(sl.candidates[0], template_id="TA2")
    bx = replace(b, slots=(replace(sl, candidates=(second,) + sl.candidates),) + b.slots[1:])
    altered = replace(lex, bundles=(bx, lex.bundles[1]))
    r = run(lex=altered)
    assert r.receipt.code == "AMBIGUOUS" and r.plan is None
    c1 = replace(sl.candidates[0], priority=1)
    c2 = replace(second, priority=2)
    prioritized = replace(bx, slots=(replace(sl, candidates=(c1, c2)),) + b.slots[1:])
    r = run(lex=replace(lex, bundles=(prioritized, lex.bundles[1])))
    assert r.plan is not None and "TA2" in r.receipt.evidence


def test_f28_overlap_bundle_scope_is_unsupported():
    p, lex = standard()
    bad = replace(lex.bundles[0], bundle_id="B12",
                  target_scope_kind="MULTI_UNIT", target_unit_ids=("P1", "P2"))
    r = run(lex=replace(lex, bundles=lex.bundles + (bad,)))
    assert r.receipt.code == "UNSUPPORTED_MAPPING_SCOPE" and r.plan is None


def test_f09_reordered_declarations_preserve_receipt():
    p, lex = standard()
    rev = replace(lex, definitions=tuple(reversed(lex.definitions)),
                  bundles=tuple(replace(b, slots=tuple(reversed(b.slots)))
                                for b in reversed(lex.bundles)))
    r1, r2 = run(), run(lex=rev, path=replace(p, units=tuple(reversed(p.units))))
    assert r1.plan is not None and r2.plan is not None
    assert r1.receipt.digest == r2.receipt.digest


def test_f10_lexicon_revision_changes_receipt_not_graph():
    _, lex = standard()
    a = run()
    b = run(lex=replace(lex, revision="lex-v2"))
    assert a.plan == b.plan
    assert a.receipt.digest != b.receipt.digest
