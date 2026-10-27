"""Independent small-network exact grid oracle, added after initial RED witness.

Unlike temporal_stn, this reference enumerates candidate event assignments and
never calls the graph solver or its shortest-path/overlap helpers. Synthetic
closed-grid instances use 1/20 s coefficients, so their attainable extrema
are exactly representable on this grid (difference constraints have integral
grid data and an integral totally unimodular incidence matrix).
"""
from dataclasses import replace
from fractions import Fraction

from morphoacoustics_smc.model import Event
from morphoacoustics_smc.temporal_stn import analyze_temporal_wire
from test_smc6_stn_preregistered import original, c, ep, study, event_map, overlap


def test_independent_enumeration_eight_synthetic_joint_overlap_scenarios():
    wire, _, ids = original()
    g1, g2 = ids[("P1", "tract")], ids[("P2", "tract")]
    tick = Fraction(1, 20)
    # (onset_min_tick, onset_max_tick, duration_min_tick, duration_max_tick).
    # Includes partial overlap, fully nested, boundary touching and variable
    # duration: interval bounds are integer multiples of tick.
    fixtures = (
        (1, 3, 3, 5),
        (3, 5, 3, 5),
        (4, 6, 3, 4),
        (0, 2, 2, 4),
        (5, 8, 1, 3),
        (2, 6, 2, 5),
        (1, 6, 1, 2),
        (6, 8, 1, 4),
    )
    for case_number, (slo, shi, dlo, dhi) in enumerate(fixtures):
        s = study(ids)
        # Preserve Task identities and original request, change ONLY timing.
        scenario = replace(
            s, study_id=f"oracle-case-{case_number}",
            constraints=(
                c("s1", None, ep(g1, Event.ONSET), 0, 0),
                c("e1", ep(g1, Event.ONSET), ep(g1, Event.OFFSET),
                  Fraction(3, 10), Fraction(3, 10)),
                c("s2", None, ep(g2, Event.ONSET), slo*tick, shi*tick),
                c("dur2", ep(g2, Event.ONSET), ep(g2, Event.OFFSET),
                  dlo*tick, dhi*tick),
            ),
        )
        result = analyze_temporal_wire(wire, scenario)
        assert result.status == "SAT_NONUNIQUE"
        admissible = []
        for si in range(13):
            for ei in range(13):
                if (slo <= si <= shi
                        and dlo <= ei-si <= dhi
                        and ei <= 12):
                    start, end = si*tick, ei*tick
                    overlap_s = max(Fraction(0), min(Fraction(3, 10), end)-start)
                    admissible.append((start, end, overlap_s))
        assert admissible
        windows = event_map(result)
        assert windows[(g2, Event.ONSET)][:2] == (
            min(x[0] for x in admissible), max(x[0] for x in admissible))
        assert windows[(g2, Event.OFFSET)][:2] == (
            min(x[1] for x in admissible), max(x[1] for x in admissible))
        lo, hi, w = overlap(result, g1, g2)
        assert (lo, hi) == (
            min(x[2] for x in admissible), max(x[2] for x in admissible))
        assert lo <= w <= hi
