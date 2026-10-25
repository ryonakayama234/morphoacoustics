"""VM-1B research: independent transmission matrices, physical port controls."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from hashlib import sha256
from dataclasses import replace
import subprocess
import json
import sys
from math import pi
from pathlib import Path

import numpy as np
import pytest

from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics_waveguide import PassiveWaveguideConfig

SCRIPT = Path(__file__).resolve().parents[1] / "tools/vm1b_loaded_reference.py"
SPEC = spec_from_file_location("vm1b_oracle", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
V = module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def tube(n: int = 1, *, area: float = 8e-4) -> Tract1DGeometry:
    return Tract1DGeometry(
        "analytic-test", tuple(TubeSection(0.010, area) for _ in range(n))
    )


def test_frozen_geometry_has_exact_original_blob_and_body_distinction() -> None:
    bodies, frozen_sha = V.load_bodies()
    assert set(bodies) == {"M0", "M1"} and len(frozen_sha) == 64
    assert len(bodies["M0"].sections) == len(bodies["M1"].sections) == 16
    assert bodies["M0"].total_length_m == pytest.approx(0.160)
    assert bodies["M1"].total_length_m == pytest.approx(0.176)
    assert [s.area_m2 for s in bodies["M0"].sections] == [
        s.area_m2 for s in bodies["M1"].sections
    ]


@pytest.mark.parametrize("n", [1, 2, 16])
@pytest.mark.parametrize("frequency", [100.0, 600.0])
def test_matched_equal_area_independent_phase_reference(n: int, frequency: float) -> None:
    body = tube(n)
    values = V.reference_transfer(body, frequency, termination="matched")
    zc = V.RHO * V.C / body.sections[0].area_m2
    expected_delay = np.exp(-2j * pi * frequency * (0.010 * n) / V.C)
    assert values["HpU"] == pytest.approx(zc * expected_delay, rel=1e-12)
    assert values["HU"] == pytest.approx(expected_delay, rel=1e-12)
    assert values["Zin"] == pytest.approx(zc, rel=1e-12)


@pytest.mark.parametrize("frequency", [100.0, 600.0])
def test_b0_phasor_load_equals_independent_state_equation(frequency: float) -> None:
    area = tube().sections[-1].area_m2
    h = 0.01 / (V.C * 2)
    r, m = V.b0_shunt_parameters(area)
    zinv = np.exp(-2j * pi * frequency * h)
    # Exact steady harmonic solution to the explicit discrete inertance update.
    q = h / m / (1 - zinv)
    y_from_recurrence = 1 / r + 0.5 * (1 + zinv) * q
    assert V.terminal_admittance(area, frequency, h, "b0") == pytest.approx(
        y_from_recurrence, rel=1e-12
    )


def test_matched_native_two_section_complex_all_ports() -> None:
    body = tube(2)
    cfg = PassiveWaveguideConfig(body, termination="matched")
    trace = V.impulse_trace(cfg, 0.01)
    for item in V.observed_transfer(cfg, trace):
        true = V.reference_transfer(body, item["actual_hz"], termination="matched")
        assert max(V.relative_errors(true, item["complex"]).values()) < 1e-9
    assert trace["energy_error_to_tolerance_max"] <= 1


def test_discrete_b0_cell_refinement_against_continuous_equation() -> None:
    bodies, _ = V.load_bodies()
    records = V.refinements("M1", bodies["M1"])
    assert len(records) == 2
    assert all(x["all_ports_complex_converge"] for x in records)
    assert all([a["cells_per_section"] for a in x["levels"]] == [2, 4, 8]
               for x in records)


def test_wrong_termination_is_not_accidentally_accepted_as_b0() -> None:
    bodies, _ = V.load_bodies()
    body = bodies["M0"]
    b0 = V.reference_transfer(body, 100.0, termination="b0")
    wrong = V.reference_transfer(body, 100.0, termination="matched")
    assert V.relative_errors(b0, wrong)["HpU"] > 2e-3


def test_silent_excitation_yields_exact_zero_native_port_traces() -> None:
    cfg = PassiveWaveguideConfig(tube(2), termination="b0")
    trace = V.impulse_trace(cfg, 0.002, amplitude_scale=0.0)
    for port in ("p_in", "p_mouth", "U_mouth"):
        assert np.count_nonzero(trace[port]) == 0
    assert trace["energy_error_to_tolerance_max"] == 0


def test_invalid_inputs_refuse_without_silent_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    altered = tmp_path / "changed.json"
    altered.write_text('{"M0":{"a_areas_m2":[]}}', encoding="utf-8")
    monkeypatch.setattr(V, "FROZEN", altered)
    with pytest.raises(ValueError, match="FROZEN_BODY_BLOB_MISMATCH"):
        V.load_bodies()
    with pytest.raises(ValueError, match="FREQUENCY_OUTSIDE_POSITIVE_RESOLVED_BAND"):
        V.terminal_admittance(8e-4, 0.0, 1/68600, "b0")
    with pytest.raises(ValueError, match="FREQUENCY_OUTSIDE_POSITIVE_RESOLVED_BAND"):
        V.terminal_admittance(8e-4, 34300.0, 1/68600, "b0")
    with pytest.raises(ValueError, match="UNSUPPORTED_TERMINATION"):
        V.terminal_admittance(8e-4, 100.0, 1/68600, "fabricated")
    with pytest.raises(ValueError, match="UNSUPPORTED_CELL_COUNT"):
        V.reference_transfer(tube(), 100.0, termination="matched", cells_per_section=3)
    with pytest.raises(ValueError, match="INVALID_FREQUENCY_OR_GEOMETRY"):
        V.reference_transfer(tube(), float("nan"), termination="b0")
    cfg = PassiveWaveguideConfig(tube(2))
    with pytest.raises(ValueError, match="INVALID_PULSE_SCALE"):
        V.impulse_trace(cfg, 0.002, amplitude_scale=float("nan"))


def test_executed_checkout_and_source_bytes_are_in_report_provenance() -> None:
    provenance = V.execution_provenance()
    assert len(provenance["executed_checkout_git_sha"]) == 40
    assert len(provenance["executed_git_tree_sha"]) == 40
    assert provenance["tracked_tree_clean"] is True
    recorded = provenance["executed_implementation_files_sha256"]
    assert set(recorded) == set(V.IMPLEMENTATION_PATHS)
    for path, digest in recorded.items():
        assert digest == sha256((V.ROOT / path).read_bytes()).hexdigest()


def test_mismatched_github_checkout_and_dirty_worktree_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provenance = V.execution_provenance()
    monkeypatch.setenv("GITHUB_SHA", "0" * 40)
    with pytest.raises(RuntimeError, match="GITHUB_SHA_CHECKOUT_MISMATCH"):
        V.execution_provenance()
    monkeypatch.delenv("GITHUB_SHA")
    real_git = V._git_output
    monkeypatch.setattr(
        V, "_git_output", lambda *args: " M tools/vm1b_loaded_reference.py"
        if args and args[0] == "status" else real_git(*args)
    )
    with pytest.raises(RuntimeError, match="DIRTY_TRACKED_EXECUTED_IMPLEMENTATION"):
        V.execution_provenance()
    assert provenance["tracked_tree_clean"]


def test_failed_gate_main_persists_json_before_refusing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    output = tmp_path / "gate-failed-report.json"
    # Dedicated failure injection: preserve the exact scientific failure
    # verdict and diagnostic values on disk before exiting nonzero.
    negative = {
        "gates_pass": False,
        "scientific_result": "FAIL_NUMERICAL_REFERENCE",
        "scope": "RESEARCH_ONLY",
        "numerical_error": {"HpU": 1.5, "Zin": 0.4},
        "execution_provenance": V.execution_provenance(),
    }
    monkeypatch.setattr(V, "run", lambda: negative)
    monkeypatch.setattr(sys, "argv", ["vm1b", "--out", str(output)])
    with pytest.raises(SystemExit, match="VM1B_GATE_FAILED"):
        V.main()
    assert json.loads(output.read_text(encoding="utf-8")) == negative


def test_shallow_clone_reports_actual_raw_commit_parents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "init", "-q", str(shallow)], check=True)
    subprocess.run(
        ["git", "fetch", "--quiet", "--depth=1", "file://" + str(V.ROOT), "HEAD"],
        cwd=shallow, check=True, capture_output=True, text=True,
    )
    subprocess.run(
        ["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"],
        cwd=shallow, check=True, capture_output=True, text=True,
    )
    def git_in_shallow(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=shallow, check=True, capture_output=True,
            text=True,
        ).stdout.strip()
    assert git_in_shallow("rev-parse", "--is-shallow-repository") == "true"
    raw_parents = [line.split(" ", 1)[1]
                   for line in git_in_shallow("cat-file", "-p", "HEAD").splitlines()
                   if line.startswith("parent ")]
    assert len(raw_parents) > 0
    monkeypatch.setattr(V, "ROOT", shallow)
    monkeypatch.setenv("GITHUB_SHA", git_in_shallow("rev-parse", "HEAD"))
    got = V.execution_provenance()
    assert got["executed_commit_parents"] == raw_parents
    assert got["executed_checkout_git_sha"] == git_in_shallow("rev-parse", "HEAD")


def test_real_energy_gate_failure_serialized_by_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not stub run(): inject a bad *finite native step* and retain its ledger."""
    native = V.PassiveWaveguideSession

    class BadEnergySession:
        def __init__(self, config):
            self.session = native(config)

        def step(self, inlet_flow_m3_s):
            measured = self.session.step(inlet_flow_m3_s)
            # Do not alter p/U traces, only the measured passivity residual.
            return replace(measured, energy_residual_j=measured.energy_residual_j + 1e-8)

    monkeypatch.setattr(V, "PassiveWaveguideSession", BadEnergySession)
    target = tmp_path / "real-energy-gate-failure.json"
    monkeypatch.setattr(sys, "argv", ["vm1b", "--out", str(target)])
    with pytest.raises(SystemExit, match="VM1B_GATE_FAILED"):
        V.main()
    saved = json.loads(target.read_text(encoding="utf-8"))
    assert saved["gates_pass"] is False
    assert saved["scientific_result"] == "FAIL_NUMERICAL_REFERENCE"
    assert saved["execution_provenance"]["tracked_tree_clean"]
    assert all(not case["energy_gate_pass"] and not case["pass"]
               for case in saved["cases"].values())
    assert all(case["energy_failure_samples"][0]["energy_residual_j"] >= 1e-8
               for case in saved["cases"].values())
    assert all(len(case["point_checks"]) == 2 for case in saved["cases"].values())
