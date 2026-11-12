"""No physics calculation: verify frozen protocol and non-execution boundaries."""
import json
from pathlib import Path
import pytest

from experiments.bodymap_b2_passive_loss.prereg_binding import (
    Refusal, validate_lambda, validate_envelope, FREQUENCIES_HZ,
    M0_DIAMETERS_MM, PLAN_CONTENT_SHA256, PREREG_CONTENT_SHA256,
    SCIENTIFIC_CASES_AUTHORIZED,
)
from experiments.bodymap_b2_passive_loss.cli import gate


def _fixtures(name):
    root = Path(__file__).resolve().parents[2]
    return json.loads((root / "experiments" / "bodymap_b2_passive_loss"
                       / "fixtures" / name).read_text(encoding="utf-8"))


def test_prereg_grid_frozen():
    assert len(FREQUENCIES_HZ) == 351
    assert FREQUENCIES_HZ[0] == 100
    assert FREQUENCIES_HZ[-1] == 800
    assert list(FREQUENCIES_HZ) == list(range(100, 801, 2))
    assert len(M0_DIAMETERS_MM) == 16


def test_lambda_gate_and_bool_rejection():
    for valid in (0, 1e-6, .5, 1):
        assert validate_lambda(valid) == float(valid)
    for invalid in (False, True, -1, 1.01, .3, float("nan"), float("inf")):
        with pytest.raises(Refusal) as info:
            validate_lambda(invalid)
        assert info.value.code == "INVALID_LOSS_PARAMETER"


def test_model_envelope_preflight():
    validate_envelope((.006,) * 16, (.010,) * 16)
    validate_envelope((.019,) * 16, (.010,) * 16)
    validate_envelope((.006,), (.160,))
    for radii, lengths in (((.005,) * 16, (.010,) * 16),
                            ((.02,) * 16, (.010,) * 16),
                            ((.006,) * 16, (.011,) * 16)):
        with pytest.raises(Refusal):
            validate_envelope(radii, lengths)


def test_engineering_not_registered_study():
    m = _fixtures("engineering-cases-v1.json")
    assert m["engineering_only"] is True
    assert SCIENTIFIC_CASES_AUTHORIZED is False
    assert m["study_evaluations_authorized"] == 0
    assert len(m["cases"]) == 8
    assert m["max_separate_process_repeats"] == 1
    assert m["plan_content_sha256"] == PLAN_CONTENT_SHA256
    assert m["prereg_content_sha256"] == PREREG_CONTENT_SHA256
    assert len({c["id"] for c in m["cases"]}) == 8


def test_all_nine_refusal_names_registered():
    m = _fixtures("expected-refusals-v1.json")
    assert [f["id"] for f in m["families"]] == [
        "NEG-LAMBDA", "ACTIVE-ZY", "SWAP-COEFF",
        "SWAP-LOAD", "SWAP-GEOM-PORT", "RAW-FORGE",
        "LOSS-IGNORED", "OLD-ATTENUATION", "SHA-SOURCE"]
    assert m["max_invocations_per_family"] == 2
    assert m["oracle_review_required"] is True


def test_unreviewed_gate_fails_closed():
    with pytest.raises(Refusal) as info:
        gate(None)
    assert info.value.code in ("DEPENDENCY_LOCK_UNRESOLVED", "REVIEWER_UNRESOLVED")
