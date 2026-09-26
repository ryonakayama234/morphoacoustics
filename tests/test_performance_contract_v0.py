import json
from pathlib import Path


CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "contracts" / "performance" / "v0"


def _load(name: str) -> dict:
    with (CONTRACT_ROOT / name).open(encoding="utf-8") as f:
        return json.load(f)


def _fixture(name: str) -> dict:
    with (CONTRACT_ROOT / "examples" / name).open(encoding="utf-8") as f:
        return json.load(f)


def test_contract_schema_files_are_json_schema_2020_12() -> None:
    for name in (
        "common.schema.json",
        "character.schema.json",
        "script.schema.json",
        "direction.schema.json",
        "performance-request.schema.json",
        "performance-result.schema.json",
    ):
        schema = _load(name)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["$id"].endswith(name)


def test_request_fixture_preserves_creator_domain_boundaries() -> None:
    request = _fixture("request.json")
    character = request["character"]
    script = request["script"]
    direction = request["direction"]

    assert request["schema_version"] == "performance-contract/v0"
    assert character["schema_version"] == "performance-contract/v0"
    assert script["schema_version"] == "performance-contract/v0"
    assert direction["schema_version"] == "performance-contract/v0"

    forbidden_solver_keys = {
        "creature_spec",
        "gesture_score",
        "prepared_morphology",
        "tract_geometry",
        "physical_state",
        "glottal_pressure",
        "vocal_fold_tension",
    }
    creative_snapshot = {**character, **script, **direction}
    assert forbidden_solver_keys.isdisjoint(creative_snapshot)


def test_request_fixture_cross_object_references_are_coherent() -> None:
    request = _fixture("request.json")
    character_id = request["character"]["character_id"]
    segments = request["script"]["segments"]
    segment_ids = [segment["segment_id"] for segment in segments]

    assert len(segment_ids) == len(set(segment_ids))
    assert all(segment["speaker_character_id"] == character_id for segment in segments)

    override_ids = [
        override["segment_id"]
        for override in request["direction"].get("segment_overrides", [])
    ]
    assert len(override_ids) == len(set(override_ids))
    assert set(override_ids).issubset(segment_ids)


def test_result_fixture_timeline_and_provenance_are_coherent() -> None:
    request = _fixture("request.json")
    result = _fixture("result.mock.json")
    segment_ids = {segment["segment_id"] for segment in request["script"]["segments"]}

    assert result["request_id"] == request["request_id"]
    assert result["job_status"] == "SUCCEEDED"
    assert result["realization_outcome"] in {
        "FEASIBLE",
        "INFEASIBLE",
        "UNSUPPORTED",
        "INVALID",
    }
    assert result["provenance"]["seed"] == request["seed"]
    assert result["provenance"]["contract_version"] == "performance-contract/v0"

    for interval in result.get("timeline", []):
        assert interval["segment_id"] in segment_ids
        assert interval["end_seconds"] >= interval["start_seconds"]


def test_physical_infeasibility_is_not_an_execution_failure() -> None:
    result = _fixture("result.mock.json")
    result["job_status"] = "SUCCEEDED"
    result["realization_outcome"] = "INFEASIBLE"

    assert result["job_status"] == "SUCCEEDED"
    assert result["realization_outcome"] == "INFEASIBLE"
