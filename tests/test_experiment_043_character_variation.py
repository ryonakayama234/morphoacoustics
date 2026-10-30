"""Research-only structural falsifiers for Exp043. No listening-quality claim."""
from __future__ import annotations

import os
from pathlib import Path
import runpy

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PILOT = runpy.run_path(str(
    ROOT / "experiments" / "043_character_voice_variation" / "run.py"
))


def test_body_intervention_is_one_axial_dimension() -> None:
    model = PILOT["load_model"]()
    a = PILOT["make_body"](model, "M0")
    b = PILOT["make_body"](model, "M1")
    assert len(a.sections) == len(b.sections) == 16
    assert a.total_length_m == pytest.approx(0.16)
    assert b.total_length_m == pytest.approx(0.176)
    assert np.array_equal(
        [s.area_m2 for s in a.sections],
        [s.area_m2 for s in b.sections],
    )
    with pytest.raises(ValueError):
        PILOT["make_body"](model, "fake")


def test_timing_changes_motion_not_final_body_target() -> None:
    model = PILOT["load_model"]()
    a = PILOT["make_body"](model, "M0")
    original = PILOT["timing_tasks"](model, "reference")
    delayed = PILOT["timing_tasks"](model, "late_constriction")
    assert original[1].onset_s == 0.15
    assert delayed[1].onset_s == 0.19
    assert original[1].offset_s == delayed[1].offset_s
    assert original[1].degree == delayed[1].degree
    early_a, _ = PILOT["realize"](model, a, "reference", 0.17)
    early_b, _ = PILOT["realize"](model, a, "late_constriction", 0.17)
    end_a, _ = PILOT["realize"](model, a, "reference", 0.50)
    end_b, _ = PILOT["realize"](model, a, "late_constriction", 0.50)
    assert any(x.area_m2 != y.area_m2 for x, y in zip(early_a.sections, early_b.sections))
    assert all(x.area_m2 == y.area_m2 for x, y in zip(end_a.sections, end_b.sections))
    with pytest.raises(ValueError):
        PILOT["timing_tasks"](model, "invented")


def test_frozen_source_drift_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    model = PILOT["load_model"]()
    source, regression, f0_hz = PILOT["audited_fixed_source"](model)
    assert regression["pass"] is True
    assert f0_hz == pytest.approx(100.0)
    assert source.shape == (24_000,)

    # Drift source *and* inherited regression expectation together. Independent
    # frozen-100 check must still reject an internally self-consistent 120 Hz.
    with monkeypatch.context() as patch:
        patch.setattr(model.EXP26.EXP13, "BASE_F0_HZ", 120.0)
        patch.setattr(model.EXP26, "BASE_F0_HZ", 120.0)
        with pytest.raises(RuntimeError, match="frozen 100 Hz regression"):
            PILOT["audited_fixed_source"](model)

    # Keep published 100 Hz metadata but change the *actual generated* phase
    # and LF samples. This was the exact missing negative control identified
    # in the independent review of Exp043 at a74b263.
    with monkeypatch.context() as patch:
        exp13 = model.EXP26.EXP13
        original = exp13.cycles_from_f0

        def drifted_cycles(planned_f0):
            return original(np.asarray(planned_f0) * 1.2)

        patch.setattr(exp13, "cycles_from_f0", drifted_cycles)
        generated, _ = exp13.build_sources()
        assert np.all(generated["lf_fixed"].planned_f0_hz == 100.0)
        assert generated["lf_fixed"].cycles[-1] > 55.0
        with pytest.raises(RuntimeError, match="phase progression"):
            PILOT["audited_fixed_source"](model)

    # Even unchanged phase and metadata must not license a source waveform
    # silently modified after its declared LF opening/gain controls.
    with monkeypatch.context() as patch:
        from dataclasses import replace

        exp13 = model.EXP26.EXP13
        original_build_sources = exp13.build_sources

        def altered_waveform():
            sources, params = original_build_sources()
            base = sources["lf_fixed"]
            changed = np.asarray(base.source, dtype=np.float64).copy()
            changed[5000:6000] *= 0.90
            sources["lf_fixed"] = replace(base, source=changed)
            return sources, params

        patch.setattr(exp13, "build_sources", altered_waveform)
        with pytest.raises(RuntimeError, match="declared physical controls"):
            PILOT["audited_fixed_source"](model)


@pytest.mark.skipif(
    os.getenv("EXP043_REAL_PHYSICS") != "1",
    reason="opt-in full 4-case acoustic render; archive outputs separately",
)
def test_full_research_render(tmp_path: Path) -> None:
    result = PILOT["run"](tmp_path / "evidence")
    assert result["status"] == "NUMERICAL_PILOT_ONLY"
    assert len(result["cases"]) == 4
    assert result["source"]["f0_hz"] == pytest.approx(100.0)
    assert result["source"]["frozen_regression"]["pass"] is True
    assert len(result["execution"]["core_commit_sha"]) == 40
    assert isinstance(result["execution"]["tracked_worktree_dirty"], bool)
    assert result["execution"]["python_version"]
    assert result["execution"]["numpy_version"] == np.__version__
    assert len(list((tmp_path / "evidence").glob("*_pressure_pa.npy"))) == 4
    assert len(list((tmp_path / "evidence").glob("*.wav"))) == 4
