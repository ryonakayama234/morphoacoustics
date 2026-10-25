"""Second GitHub Codex P2 preregression: typed rational sort keys."""
import json
from copy import deepcopy

from morphoacoustics_smc.canonical_ingress import parse_canonical_request
from test_smc4_br_ingress_preregistered import fixture, encoded


def test_codex2_anchor_rationals_sort_numerically_not_lexically():
    d = fixture()
    a = deepcopy(d["coordination"]["anchors"][0])
    b = deepcopy(a)
    a["time_s"] = {"numerator": 10, "denominator": 1}
    b["time_s"] = {"numerator": 2, "denominator": 1}
    d["coordination"]["anchors"] = [a, b]
    r = parse_canonical_request(encoded(d))
    assert r.request is not None
    anchors = json.loads(r.request.canonical_bytes)["coordination"]["anchors"]
    assert [x["time_s"]["numerator"] for x in anchors] == [2, 10]


def test_codex2_relation_lags_sort_numerically_not_lexically():
    d = fixture()
    relation = {
        "from_unit": "P1", "from_slot": "tract", "from_event": "ONSET",
        "to_unit": "P2", "to_slot": "tract", "to_event": "OFFSET",
        "lag_s": {"numerator": 10, "denominator": 1},
    }
    another = deepcopy(relation)
    another["lag_s"]["numerator"] = 2
    d["coordination"]["relations"] = [relation, another]
    r = parse_canonical_request(encoded(d))
    assert r.request is not None
    rel = json.loads(r.request.canonical_bytes)["coordination"]["relations"]
    assert [x["lag_s"]["numerator"] for x in rel] == [2, 10]
