"""Independent Codex review P2 repros; committed before source repair."""
from __future__ import annotations

import pytest

from morphoacoustics_smc.reading_paths import ReadingPath, ReadingUnit
from morphoacoustics_smc.l1r_evidence import (
    EvidenceManifest, context_hash, manifest_id, make_l1_envelope,
)


@pytest.mark.parametrize("source", ["😀", "甲A", "ー", "・"])
def test_r01_r04_unsupported_source_must_refuse_even_when_spans_complete(source: str):
    context = "文脈A"
    m = EvidenceManifest(
        "manual-research", "2026.10", "a" * 64, "policy-1",
        "internal-fixture", context_hash(context, "r1"),
    )
    # Adversarial claimant provides legitimate structure/provenance *claims*.
    # This is the exact old bypass: L0 checks spans, not L1 script support.
    p = ReadingPath(
        "p1", (ReadingUnit("u1", "ア", 0, len(source)),), manifest_id(m),
    )
    result = make_l1_envelope(source, "r1", context, m, (p,))
    assert (result.status, result.code, result.proposal) == (
        "REJECTED", "UNSUPPORTED_SOURCE", None,
    )


def test_r05_restricted_japanese_source_and_silent_spans_still_valid():
    context = "文脈A"
    m = EvidenceManifest(
        "manual-research", "2026.10", "a" * 64, "policy-1",
        "internal-fixture", context_hash(context, "r1"),
    )
    p = ReadingPath("p1", (
        ReadingUnit("u1", "ア", 0, 1),
        ReadingUnit("u2", "コウ", 1, 2),
        ReadingUnit("u3", "カ", 3, 4),
    ), manifest_id(m))
    result = make_l1_envelope("あ甲、カ！", "r1", context, m, (p,))
    assert (result.status, result.code) == ("PROPOSED", "OK")


def test_r06_hostile_profile_comparison_is_not_called():
    class HostileProfile:
        def __ne__(self, other: object) -> bool:
            raise AssertionError("must reject by type before invoking __ne__")

    with pytest.raises(ValueError, match="INVALID_PROFILE_OR_REVISION"):
        context_hash("文脈A", "r1", HostileProfile())
    with pytest.raises(ValueError, match="INVALID_PROFILE_OR_REVISION"):
        context_hash("文脈A", "r1", "en-US")
