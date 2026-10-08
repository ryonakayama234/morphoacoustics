"""Pure request-policy tests: run under the ordinary Python version matrix."""
from morphoacoustics.integration.limited_live import (
    BODY_ID, PRONUNCIATION_ID, SCHEMA_VERSION, validate,
)


def request():
    return {
        "schema_version": SCHEMA_VERSION,
        "pronunciation_id": PRONUNCIATION_ID,
        "body_id": BODY_ID,
        "segment_id": "s1",
        "text": "あい",
        "seed": 0,
    }


def test_supported_fixture_only():
    assert validate(request()) is None
    other_segment = {**request(), "segment_id": "s2"}
    assert validate(other_segment) is None


def test_rejects_unsupported_text_without_fallback():
    result = validate({**request(), "text": "こんにちは"})
    assert result is not None
    assert result["realization_outcome"] == "UNSUPPORTED"
    assert result["artifacts"] == []
    assert result["diagnostics"][0]["code"] == "PRONUNCIATION"


def test_rejects_unknown_body_and_creative_direction():
    for changed in (
        {"body_id": "some-other-body"},
        {"direction": {"emotion": "angry"}},
        {"seed": 123},
        {"pronunciation_id": "general-japanese/v1"},
    ):
        result = validate({**request(), **changed})
        assert result is not None
        assert result["realization_outcome"] == "UNSUPPORTED"
        assert result["artifacts"] == []


def test_structural_invalidity_distinct_from_unsupported():
    for changed in (
        {"seed": True},
        {"seed": "0"},
        {"segment_id": ""},
        {"arbitrary_solver_pressure": 0.8},
        {"direction": "not-a-dictionary"},
    ):
        result = validate({**request(), **changed})
        assert result is not None
        assert result["realization_outcome"] == "INVALID"
        assert result["artifacts"] == []


def test_rejects_missing_schema_and_arrays():
    for request_value in ({}, ["あい"], None):
        result = validate(request_value)
        assert result is not None
        assert result["realization_outcome"] == "INVALID"


def test_normalized_request_digest_is_independent_of_json_key_order():
    a = validate({**request(), "text": "X"})
    b = validate(dict(reversed(list({**request(), "text": "X"}.items()))))
    assert a is not None and b is not None
    assert a["provenance"]["request_sha256"] == b["provenance"]["request_sha256"]


def test_nonfinite_and_non_json_extensions_are_invalid():
    for bad in (float("nan"), float("inf")):
        result = validate({**request(), "direction": {"energy": bad}})
        assert result is not None
        assert result["realization_outcome"] == "INVALID"
        assert result["diagnostics"][0]["code"] == "REQUEST_ENCODING"
        assert result["provenance"]["request_sha256"] is None
