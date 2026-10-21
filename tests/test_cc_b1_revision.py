"""Non-adopting contract tests for experimental CC-B1 BodyRevision preparation."""
from __future__ import annotations

from dataclasses import replace
import json
import math

import pytest

from morphoacoustics import CavityConnection, CavityKind, CavitySpec, CreatureSpec
from morphoacoustics.integration.body_presets import make_body_preset, preparation_digest
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d
from tools.cc_b1_revision import (
    RestAreaEditIntent, RevisionStatus, prepare_rest_area_revision,
)


def baseline(*, branched: bool = False, count: int = 16):
    cavities = (CavitySpec(id="oral", kind=CavityKind.ORAL),)
    connections = ()
    if branched:
        cavities += (CavitySpec(id="nasal", kind=CavityKind.NASAL),)
        connections = (CavityConnection(source_id="oral", target_id="nasal"),)
    creature = CreatureSpec(name="prototype", cavities=cavities, connections=connections)
    geometry = Tract1DGeometry("oral", tuple(
        TubeSection(0.01, 2e-4 + i * 1e-6) for i in range(count)
    ))
    prepared = prepare_tract1d(
        creature, geometry, provenance=PreparationProvenance(source="cc-b1-test")
    )
    return make_body_preset(preset_id="frozen-reference", revision=1, prepared=prepared)


def intent_for(base, site: int = 2, ratio: float = 1.05):
    return RestAreaEditIntent(
        base_preset_id=base.preset_id,
        base_revision=base.revision,
        base_preparation_digest=base.preparation_digest,
        cavity_id="oral",
        section_index=site,
        area_m2=base.prepared.rest_state.sections[site].area_m2 * ratio,
    )


def test_one_and_only_one_si_rest_area_diff_and_immutable_revisions():
    base = baseline()
    prior_digest = preparation_digest(base.prepared)
    intent = intent_for(base)
    result = prepare_rest_area_revision(base, intent)
    assert result.status is RevisionStatus.ACCEPTED and result.revision is not None
    rev = result.revision
    assert rev.parent_preparation_digest == prior_digest
    assert rev.preparation_digest == preparation_digest(rev.prepared)
    assert rev.preparation_digest != prior_digest
    assert rev.prepared.creature is base.prepared.creature
    assert rev.prepared.rest_state.cavity_id == "oral"
    before = base.prepared.rest_state.sections
    after = rev.prepared.rest_state.sections
    assert [i for i in range(16) if before[i] != after[i]] == [2]
    assert all(before[i].length_m == after[i].length_m for i in range(16))
    assert before[2].area_m2 == pytest.approx(2.02e-4)
    assert after[2].area_m2 == pytest.approx(intent.area_m2)
    with pytest.raises(AttributeError):
        rev.edited_area_m2 = 1  # type: ignore[misc]


def test_same_exact_input_replays_same_identity_and_cross_site_distinguishes():
    base = baseline()
    a = prepare_rest_area_revision(base, intent_for(base))
    b = prepare_rest_area_revision(base, intent_for(base))
    c = prepare_rest_area_revision(base, intent_for(base, site=4))
    assert a.revision is not None and b.revision is not None and c.revision is not None
    assert a.revision == b.revision
    assert a.revision.revision_id != c.revision.revision_id
    assert a.revision.preparation_digest != c.revision.preparation_digest
    assert json.loads(json.dumps(a.revision.receipt())) == a.revision.receipt()
    assert "gain" not in json.dumps(a.revision.receipt())
    assert "waveform" not in json.dumps(a.revision.receipt())


@pytest.mark.parametrize("area", [0.0, -1e-4, float("nan"), float("inf"), float("-inf"), True, "2e-4"])
def test_invalid_nonphysical_area_no_accepted_revision(area):
    base = baseline()
    request = replace(intent_for(base), area_m2=area)
    out = prepare_rest_area_revision(base, request)
    assert out.status is RevisionStatus.INVALID
    assert out.revision is None


@pytest.mark.parametrize("site", [-1, 16, True, 1.5])
def test_bad_section_index_is_refused(site):
    base = baseline()
    out = prepare_rest_area_revision(base, replace(intent_for(base), section_index=site))
    assert out.status is RevisionStatus.INVALID
    assert out.revision is None


def test_exact_reference_and_tamper_cannot_forge_a_new_body():
    base = baseline()
    request = intent_for(base)
    assert prepare_rest_area_revision(base, replace(request, base_revision=2)).status is RevisionStatus.REVISION_MISMATCH
    assert prepare_rest_area_revision(base, replace(request, base_preparation_digest="sha256:" + "0" * 64)).status is RevisionStatus.REVISION_MISMATCH
    another = replace(base, preparation_digest="sha256:" + "0" * 64)
    altered = replace(request, base_preparation_digest=another.preparation_digest)
    result = prepare_rest_area_revision(another, altered)
    assert result.status is RevisionStatus.INVALID and result.code == "BASE_TAMPERED"


@pytest.mark.parametrize("ratio", [0.5, 0.899, 1.101, 2.0])
def test_outside_exploratory_physical_envelope_is_unsupported(ratio):
    base = baseline()
    result = prepare_rest_area_revision(base, intent_for(base, ratio=ratio))
    assert result.status is RevisionStatus.UNSUPPORTED and result.revision is None


def test_noop_and_unsupported_geometry_or_graph_never_create_a_body():
    base = baseline()
    assert prepare_rest_area_revision(base, intent_for(base, ratio=1)).code == "NO_OP"
    short = baseline(count=15)
    i = intent_for(short)
    assert prepare_rest_area_revision(short, i).status is RevisionStatus.UNSUPPORTED
    graph = baseline(branched=True)
    j = intent_for(graph)
    assert prepare_rest_area_revision(graph, j).status is RevisionStatus.UNSUPPORTED


def test_old_preparation_and_body_preset_are_never_mutated():
    base = baseline()
    original = base.prepared.rest_state
    original_digest = base.preparation_digest
    for site in (0, 2, 4, 15):
        result = prepare_rest_area_revision(base, intent_for(base, site=site, ratio=0.95))
        assert result.accepted
    assert base.prepared.rest_state is original
    assert base.preparation_digest == original_digest
    assert preparation_digest(base.prepared) == original_digest
