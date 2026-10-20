"""Evidence must reject stale outputs, dirty sources and self-consistent tampering."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import runpy
import subprocess
import sys

import pytest

from morphoacoustics_graph.tree5 import prepare_tree5

ROOT = Path(__file__).resolve().parents[1]
SCORER = runpy.run_path(str(ROOT / "checks/check_og5_gate_b3.py"))
AUDIT = runpy.run_path(str(ROOT / "checks/check_og5_b3_twin.py"))


def test_stale_output_is_preserved_even_on_cli_failure(tmp_path: Path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    (output / "summary.json").write_text("previous raw evidence")
    result = subprocess.run([
        sys.executable, str(ROOT / "checks/check_og5_gate_b3.py"),
        "--expected-head", "0" * 40, "--output-dir", str(output)], capture_output=True)
    assert result.returncode != 0 and b"STALE_OUTPUT" in result.stderr
    assert list(output.iterdir()) == [output / "summary.json"]
    assert (output / "summary.json").read_text() == "previous raw evidence"


def test_dirty_tracked_sources_refuse_before_solving(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    source = repo / "source.py"
    source.write_text("original\n")
    subprocess.run(["git", "add", "source.py"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=Evidence Test", "-c", "user.email=test@example.invalid",
                    "commit", "-qm", "fixture"], cwd=repo, check=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    source.write_text("uncommitted replacement\n")
    monkeypatch.setitem(SCORER["run"].__globals__, "ROOT", repo)
    output = tmp_path / "dirty"
    with pytest.raises(AssertionError, match="DIRTY_TRACKED_WORKTREE"):
        SCORER["run"](output, head)
    assert not output.exists()


@pytest.fixture
def raw_record() -> dict:
    gold = json.loads((ROOT / "docs/research/og5-contract-goldens.json").read_text())
    prepared = prepare_tree5(copy.deepcopy(gold["blueprint_snapshot_variants"]["baseline"]["input"]))
    frozen = gold["baseline_observation"]
    reference = {key: [[z["real"], z["imag"]] for z in frozen[key][0]]
                 for key in ("pressure_pa", "volume_flow_m3_s")}
    record = {"input_blueprint": prepared.to_snapshot()["blueprint"],
              "core_response": prepared.response([733]),
              "case": {"frequency_hz": 733, "c_area_m2": .00015, "c_load": "matched", "scale": 1.,
                       "global": reference, "recursive": copy.deepcopy(reference)}}
    AUDIT["audit_record"](record)
    return record


def test_audit_recomputes_observation_identity(raw_record: dict) -> None:
    raw_record["core_response"]["observation_digest"] = "sha256:" + "0" * 64
    with pytest.raises(AssertionError, match="wrong observation digest"):
        AUDIT["audit_record"](raw_record)


def test_rehashing_wrong_states_does_not_forge_oracle_agreement(raw_record: dict) -> None:
    observation = raw_record["core_response"]
    observation["pressure_pa"][0][0]["real"] += .01
    observation["observation_digest"] = AUDIT["digest"](
        "observation", {k: v for k, v in observation.items() if k != "observation_digest"})
    raw_record["errors"] = {"global": 0., "recursive": 0.}
    with pytest.raises(AssertionError, match="raw Core/oracle mismatch"):
        AUDIT["audit_record"](raw_record)


def test_raw_oracles_cannot_be_changed_together_with_states() -> None:
    cases = []
    for i in range(8):
        shard = json.loads((ROOT / f"docs/research/og5-b3-oracle-{i:02}.json").read_text())
        cases.extend({"case": value} for value in shard["cases"])
    AUDIT["audit_pinned_oracle"](cases)
    for method in ("global", "recursive"):
        cases[0]["case"][method]["pressure_pa"][0][0] += .01
    with pytest.raises(AssertionError, match="raw oracle values differ from pinned source"):
        AUDIT["audit_pinned_oracle"](cases)
