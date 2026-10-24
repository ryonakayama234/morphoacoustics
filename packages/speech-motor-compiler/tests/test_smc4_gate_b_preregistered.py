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

# The following additional oracles implement cases frozen in Gate A/Gate B
# protocol, added as a separate source commit for auditable test provenance.
from morphoacoustics_smc.model import Event
from morphoacoustics_smc.smc4_lexicon import TimeAnchor


def _all_anchors(p2_start=Q(0), p2_stop=Q(1)):
    return tuple(TimeAnchor(unit, slot, event, time)
                 for unit, start, stop in (("P1", Q(0), Q(1)),
                                           ("P2", p2_start, p2_stop))
                 for slot in ("tract", "source")
                 for event, time in ((Event.ONSET, start), (Event.OFFSET, stop)))


def _source_targets(a: tuple[int, int], b: tuple[int, int]):
    _, lex = standard()
    new_bundles = []
    for index, original in enumerate(lex.bundles):
        slot = original.slots[1]
        low, high = (a, b)[index]
        changed = replace(slot.candidates[0], lower=Q(low), upper=Q(high))
        new_bundles.append(replace(original, slots=(
            original.slots[0], replace(slot, candidates=(changed,)))))
    return replace(lex, bundles=tuple(new_bundles))


def test_f03_repeated_symbol_is_not_automatically_shared():
    p, lex = standard()
    p = replace(p, units=(p.units[0], replace(p.units[1], symbol="p1")))
    b2 = replace(lex.bundles[1], symbol="p1")
    r = run(path=p, lex=replace(lex, bundles=(lex.bundles[0], b2)))
    assert r.plan is not None
    assert len(r.plan.tasks) == 4


def test_f06_invalid_unicode_and_invalid_codepoint_span():
    bad_unicode = run(source="甲" + chr(0xD800))
    assert bad_unicode.receipt.code == "INVALID_INPUT" and bad_unicode.plan is None
    p, _ = standard()
    malformed = replace(p, units=(replace(p.units[0], start_offset=-1), p.units[1]))
    r = run(path=malformed)
    assert r.receipt.code == "INVALID_INPUT" and r.plan is None


def test_f07_dangling_definition_is_invalid_not_silent():
    p, lex = standard()
    slot = lex.bundles[0].slots[0]
    wrong = replace(slot.candidates[0], definition_id="missing")
    b = replace(lex.bundles[0],
                slots=(replace(slot, candidates=(wrong,)), lex.bundles[0].slots[1]))
    r = run(lex=replace(lex, bundles=(b, lex.bundles[1])))
    assert r.receipt.code == "INVALID_PLAN" and r.plan is None


def test_f08_contradictory_exact_anchors_are_not_solved():
    anchors = (TimeAnchor("P1", "source", Event.ONSET, Q(0)),
               TimeAnchor("P1", "source", Event.ONSET, Q(1)))
    r = run(anchors=anchors)
    assert r.receipt.code == "INVALID_PLAN" and r.plan is None
    assert any("CONTRADICTORY_TIMING" in x for x in r.receipt.detail)


def test_f12a_overlapping_disjoint_same_variable_is_conflict():
    lex = _source_targets((0, 1), (2, 3))
    r = run(lex=lex, anchors=_all_anchors(Q(1, 2), Q(3, 2)))
    assert r.receipt.code == "TASK_GOAL_CONFLICT" and r.plan is None


def test_f12b_different_variables_stay_unverified_not_infeasible():
    r = run(anchors=_all_anchors(Q(1, 2), Q(3, 2)))
    assert r.plan is not None and r.receipt.status == "MAPPED_SYMBOLIC"
    assert r.receipt.body_status == "UNVERIFIED"


def test_f12c_same_variable_disjoint_time_can_succeed():
    r = run(lex=_source_targets((0, 1), (2, 3)),
            anchors=_all_anchors(Q(2), Q(3)))
    assert r.plan is not None and r.receipt.status == "MAPPED_SYMBOLIC"


def test_f13_unanchored_cannot_invent_absolute_times():
    r = run()
    assert r.plan is not None and r.receipt.timing_status == "UNRESOLVED"


def test_f14_phase_oscillator_is_unsupported():
    r = run(coordination_kind="OSCILLATOR_PHASE")
    assert r.plan is None and r.receipt.code == "UNSUPPORTED_COORDINATION"


def test_f19_unknown_vs_known_mismatching_context():
    p, lex = standard()
    b = replace(lex.bundles[0], context=Predicate("EQ", "position", "X"))
    l2 = replace(lex, bundles=(b, lex.bundles[1]))
    assert run(lex=l2).receipt.code == "INSUFFICIENT_CONTEXT"
    assert run(lex=l2, context={"position": "Y"}).receipt.code == "UNMAPPED"


def test_f20_shared_scalar_target_intersection_is_preserved():
    lex = _source_targets((0, 2), (1, 3))
    decision = ShareDecision("e", (("P2", "source"), ("P1", "source")))
    r = run(lex=lex, shares=(decision,))
    assert r.plan is not None
    assert len(r.plan.tasks) == 3
    targets = [(lo, hi) for _, lo, hi in r.receipt.task_targets]
    assert (Q(1), Q(2)) in targets
    assert {"TS1", "TS2"}.issubset(r.receipt.evidence)
    assert len(r.receipt.mapping_provenance) == 4


def test_f22_share_mismatched_semantic_domain_is_unverified():
    p, lex = standard()
    alt = TaskDefinition("src_alt", "r1", "q_src", "categorical",
                         "FUNCTIONAL_src")
    b2 = lex.bundles[1]
    source = b2.slots[1]
    c = replace(source.candidates[0], definition_id="src_alt")
    b2 = replace(b2, slots=(b2.slots[0], replace(source, candidates=(c,))))
    newlex = replace(lex, definitions=lex.definitions + (alt,),
                     bundles=(lex.bundles[0], b2))
    r = run(lex=newlex, shares=(
        ShareDecision("e", (("P1", "source"), ("P2", "source"))),))
    assert r.receipt.code == "UNVERIFIED_SHARE_COMPATIBILITY"
    assert r.plan is None


def test_f25_false_alternative_does_not_add_third_slot_task():
    p, lex = standard()
    b = lex.bundles[0]
    slot = b.slots[0]
    false_candidate = replace(slot.candidates[0], template_id="NO",
                              context=Predicate("FALSE"))
    b = replace(b, slots=(replace(slot, candidates=slot.candidates +
                                 (false_candidate,)), b.slots[1]))
    r = run(lex=replace(lex, bundles=(b, lex.bundles[1])))
    assert r.plan is not None and len(r.plan.tasks) == 4
    assert "NO" not in r.receipt.evidence


def test_f26_unmatched_required_slot_never_partial_mapping():
    p, lex = standard()
    b = lex.bundles[0]
    source = b.slots[1]
    bad = replace(source.candidates[0], context=Predicate("FALSE"))
    b = replace(b, slots=(b.slots[0], replace(source, candidates=(bad,))))
    r = run(lex=replace(lex, bundles=(b, lex.bundles[1])))
    assert r.receipt.code == "UNMAPPED" and r.plan is None


def test_f27_unknown_competing_bundle_blocks_fallback():
    p, lex = standard()
    specific = replace(lex.bundles[0], bundle_id="B_specific", context=DEVOICE)
    r = run(lex=replace(lex, bundles=lex.bundles + (specific,)))
    assert r.receipt.code == "INSUFFICIENT_CONTEXT" and r.plan is None


def test_f29_f32_complete_per_unit_coverage_and_missing_case():
    p, lex = standard()
    assert {a.unit_id for a in run().plan.associations} == {"P1", "P2"}
    r = run(lex=replace(lex, bundles=lex.bundles[:1]))
    assert r.receipt.code == "UNMAPPED" and r.plan is None


def test_f31_neighbor_fact_is_read_only():
    p, lex = standard()
    b = replace(lex.bundles[0], context=Predicate("EQ", "neighbor_P2", "p2"))
    l2 = replace(lex, bundles=(b, lex.bundles[1]))
    assert run(lex=l2).receipt.code == "INSUFFICIENT_CONTEXT"
    r = run(lex=l2, context={"neighbor_P2": "p2"})
    assert r.plan is not None
    assert {a.unit_id for a in r.plan.associations} == {"P1", "P2"}


def test_f10_rule_revision_changes_receipt():
    _, lex = standard()
    assert run().receipt.digest != run(
        lex=replace(lex, rule_revision="rule-v2")).receipt.digest


def test_f09_reordering_share_members_preserves_digest():
    a = run(shares=(ShareDecision("e", (("P1", "source"),
                                       ("P2", "source"))),))
    b = run(shares=(ShareDecision("e", (("P2", "source"),
                                       ("P1", "source"))),))
    assert a.plan == b.plan and a.receipt.digest == b.receipt.digest


def test_f15_gateb_does_not_accept_unreviewed_project_phonetics():
    p, lex = standard()
    b = lex.bundles[0]
    source = b.slots[1]
    candidate = replace(source.candidates[0], status="PROJECT_MEASURED")
    b = replace(b, slots=(b.slots[0],
                         replace(source, candidates=(candidate,))))
    r = run(lex=replace(lex, bundles=(b, lex.bundles[1])))
    assert r.receipt.code == "UNVERIFIED" and r.plan is None


def test_f12a_partial_time_proof_with_unrelated_unanchored_tasks():
    # P1/P2 source occurrences have complete exact windows, while tract
    # occurrences remain unanchored. Their absence must not mask contradiction.
    src_anchors = tuple(a for a in _all_anchors(Q(1, 2), Q(3, 2))
                        if a.slot_id == "source")
    r = run(lex=_source_targets((0, 1), (2, 3)), anchors=src_anchors)
    assert r.receipt.code == "TASK_GOAL_CONFLICT" and r.plan is None


def test_strong_kleene_negation_and_unknown_explicit_semantics():
    from morphoacoustics_smc.smc4_types import evaluate
    eq = Predicate("EQ", "specified", "yes")
    assert evaluate(Predicate("NOT", operands=(eq,)), {}) == "UNKNOWN"
    assert evaluate(Predicate("AND", operands=(Predicate("FALSE"), eq)), {}) == "FALSE"
    assert evaluate(Predicate("OR", operands=(Predicate("TRUE"), eq)), {}) == "TRUE"
    assert evaluate(eq, {"specified": "no"}) == "FALSE"
