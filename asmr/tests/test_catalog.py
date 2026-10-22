import pytest

from morphoacoustics_asmr import ResearchUnavailable, list_research, require_adopted


def test_catalog_is_stable_and_research_only() -> None:
    items = list_research()
    assert len(items) == 5
    assert {item.id for item in items} == {"EL-HYPOTHESES", "EL-G0", "EL-G0A", "NV1-EAR", "EL-R1"}
    assert all(item.state == "RESEARCH_ONLY" for item in items)
    assert {x.core_pr for x in items} == {83, 114, 129, 138, 153}


@pytest.mark.parametrize("feature_id", ["EL-R1", "NV1-EAR", "EL-G0A", "unknown"])
def test_no_draft_feature_can_execute(feature_id: str) -> None:
    with pytest.raises(ResearchUnavailable):
        require_adopted(feature_id)
