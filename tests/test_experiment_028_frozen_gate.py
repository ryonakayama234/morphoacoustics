"""Experiment 028 must reject changes to its audited scientific inputs."""
import functools
import importlib.util
import json
import os
from pathlib import Path
import sys
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "028_task_field_morphology_transfer"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def experiment():
    return load_module("exp028_gate_test", EXPERIMENT / "run.py")


def rejected(experiment, tmp_path, expected):
    result = experiment.run(tmp_path)
    assert result["decision"] == expected
    assert result["preflight"]["pass"] is False
    assert not any(tmp_path.glob("*_raw_pressure_pa.npy"))
    assert json.loads((tmp_path / "decision.json").read_text())["decision"] == expected
    assert (tmp_path / "provenance.json").exists()
    return result


def test_audited_baseline_still_passes(experiment, tmp_path):
    result = experiment.run(tmp_path)
    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert result["decision"] == "SUPPORT_TASK_TRANSFER", json.dumps({
        "preflight": result["preflight"]["checks"], "gates": result["gates"],
        "source": provenance.get("source"),
        "identity": result["preflight"]["implementation"],
    })
    assert all(result["gates"].values())
    assert all(result["preflight"]["checks"].values())
    assert result["endpoint_metrics"]["M1"]["task_to_i_over_a_to_i"] == 0.1868627388125155
    assert result["realizer"]["sha256_M0"] == result["realizer"]["sha256_M1"]
    assert result["realizer"]["sha256_M0"] != result["realizer"]["parameters_sha256"]


@pytest.mark.parametrize("decorated", [False, True])
def test_body_specific_realizer_is_rejected(experiment, monkeypatch, tmp_path, decorated):
    original = experiment.EXP27.task_geometry_for_time

    def body_specific(start, time_s, *, control_step_s, cavity_id):
        activations = experiment.EXP27.task_activations_at_time(
            time_s, control_step_s=control_step_s
        )
        if start.sections[0].length_m == 0.011:
            activations = tuple(value**2 for value in activations)
        return experiment.EXP27.realize_task_geometry_from_activations(
            start, activations, cavity_id=cavity_id
        )

    if decorated:
        body_specific = functools.wraps(original)(body_specific)
    monkeypatch.setattr(experiment.EXP27, "task_geometry_for_time", body_specific)
    result = rejected(experiment, tmp_path, "IMPLEMENTATION_MISMATCH")
    assert not result["preflight"]["checks"]["executed_implementation_matches"]


@pytest.mark.parametrize("vowel", ["a", "i", "both"])
def test_frozen_area_drift_is_rejected(experiment, monkeypatch, tmp_path, vowel):
    original = experiment.EXP26.EXP23.primary_geometry

    def drifted(name):
        geometry = original(name)
        if name != vowel and vowel != "both":
            return geometry
        return experiment.Tract1DGeometry(
            cavity_id=geometry.cavity_id,
            sections=tuple(experiment.TubeSection(
                length_m=section.length_m, area_m2=section.area_m2 * 1.000001
            ) for section in geometry.sections),
        )

    monkeypatch.setattr(experiment.EXP26.EXP23, "primary_geometry", drifted)
    result = rejected(experiment, tmp_path, "MORPHOLOGY_INTERVENTION_INVALID")
    assert not result["preflight"]["checks"]["M0_matches_frozen_body"]


def test_modified_dependency_file_is_rejected(experiment, monkeypatch, tmp_path):
    original = Path.read_bytes
    pinned = Path(experiment.EXP27.__file__).resolve()

    def read_bytes(path):
        data = original(path)
        return data + b"\n# upstream implementation changed\n" if path.resolve() == pinned else data

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    rejected(experiment, tmp_path, "IMPLEMENTATION_MISMATCH")


@pytest.mark.parametrize("name,value", [
    ("TRAJECTORY_STEP_RATIO_LIMIT", 0.30),
    ("ARTIFACT_JUMP_RATIO_LIMIT", 4.0),
    ("TEMPORAL_STABILITY_LIMIT", 0.30),
])
@pytest.mark.parametrize("owner", ["local", "upstream"])
def test_threshold_rescue_is_rejected(experiment, monkeypatch, tmp_path, name, value, owner):
    target = experiment if owner == "local" else experiment.EXP27
    monkeypatch.setattr(target, name, value)
    rejected(experiment, tmp_path, "IMPLEMENTATION_MISMATCH")


def test_changed_oracle_threshold_is_rejected(experiment, monkeypatch, tmp_path):
    oracle = json.loads(experiment.ORACLE_PATH.read_text())
    oracle["frozen_gate"]["trajectory_step_ratio_max"] = 0.30
    path = tmp_path / "changed_oracle.json"
    path.write_text(json.dumps(oracle))
    monkeypatch.setattr(experiment, "ORACLE_PATH", path)
    result = rejected(experiment, tmp_path / "output", "IMPLEMENTATION_MISMATCH")
    assert not result["preflight"]["checks"]["oracle_gate_matches_local_limits"]


def test_source_identity_cannot_change_silently(experiment, monkeypatch, tmp_path):
    original = experiment.EXP26.EXP13.build_sources

    def scaled_source():
        sources, metadata = original()
        sources["lf_fixed"].source[:] *= 1.000001
        return sources, metadata

    monkeypatch.setattr(experiment.EXP26.EXP13, "build_sources", scaled_source)
    rejected(experiment, tmp_path, "IMPLEMENTATION_MISMATCH")


def test_cpu_simd_roundoff_does_not_change_frozen_source_identity(tmp_path):
    # Portable code/parameter identity, not the last floating bit of exp/sin.
    env = dict(os.environ)
    env["NPY_DISABLE_CPU_FEATURES"] = "AVX512F,AVX512_SKX,AVX2,FMA3"
    completed = subprocess.run(
        [sys.executable, str(EXPERIMENT / "run.py"), "--output-dir", str(tmp_path)],
        cwd=ROOT, env=env, capture_output=True, text=True, check=True,
    )
    result = json.loads(completed.stdout)
    assert result["decision"] == "SUPPORT_TASK_TRANSFER", result["gates"]
    provenance = json.loads((tmp_path / "provenance.json").read_text())
    assert provenance["source"]["generator_identity_matches"]
    assert provenance["source"]["byte_digest_is_diagnostic_only"]


def test_oracle_comparison_covers_entire_schema():
    verifier = load_module("exp028_oracle_verify_test", EXPERIMENT / "wolfram" / "verify_oracle.py")
    oracle = json.loads((EXPERIMENT / "wolfram" / "v3b_oracle.json").read_text())
    assert verifier.oracle_differences(oracle, oracle) == []
    for key in oracle:
        incomplete = dict(oracle)
        del incomplete[key]
        assert verifier.oracle_differences(oracle, incomplete)
    for field in ("metrics", "frozen_gate", "peak_frequencies_hz"):
        changed = json.loads(json.dumps(oracle))
        key = next(iter(changed[field]))
        changed[field][key] = -1
        assert verifier.oracle_differences(oracle, changed)
