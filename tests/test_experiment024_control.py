"""Regression checks for the frozen control and finite improvement gate."""
import importlib.util
import json
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "experiment024_control_test",
    ROOT / "experiments/024_source_spectrum_vowel_cue/run.py",
)
assert SPEC is not None and SPEC.loader is not None
EXP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXP)


def frozen_ratios():
    frozen = json.loads(EXP.BASELINE_PATH.read_text())
    return frozen['s0_source_p2_over_p1_db'], frozen['s0_rendered_p2_over_p1_db']


def test_frozen_control_matches():
    source, rendered = frozen_ratios()
    assert EXP.baseline_reproduction(source, rendered)['pass'] is True


@pytest.mark.parametrize('domain', ['source', 'rendered'])
@pytest.mark.parametrize('vowel', ['a', 'i', 'u'])
@pytest.mark.parametrize('replacement', [None, -math.inf, math.inf, math.nan])
def test_control_drift_or_missing_harmonics_fail(domain, vowel, replacement):
    source, rendered = frozen_ratios()
    ratios = source if domain == 'source' else rendered
    ratios[vowel] = ratios[vowel] + 0.1 if replacement is None else replacement
    assert EXP.baseline_reproduction(source, rendered)['pass'] is False


@pytest.mark.parametrize('invalid', [-math.inf, math.inf, math.nan])
def test_invalid_improvement_cannot_pass(invalid):
    assert EXP.i_cue_improvement(invalid, 3.0) == (None, False)
    assert EXP.i_cue_improvement(-28.8, invalid) == (None, False)


def test_baseline_is_required_by_complete_objective_gate(tmp_path, monkeypatch):
    # Isolate the control gate: substitute passing artifact metrics and widen
    # the S1 oracle tolerance ONLY in this test (024 really fails these gates).
    monkeypatch.setattr(EXP.EXP13, 'source_metrics', lambda _: {'cycle_boundary_jump_per_rms': 0.0})
    monkeypatch.setattr(EXP, 'RENDERED_RATIO_TOLERANCE_DB', 3.0)
    result = EXP.run(tmp_path / 'matching')
    assert result['objective_gate_pass'] is True
    original = EXP.baseline_reproduction

    def drifted(source, rendered):
        altered = dict(source)
        altered['i'] += 0.1
        return original(altered, rendered)

    monkeypatch.setattr(EXP, 'baseline_reproduction', drifted)
    result = EXP.run(tmp_path / 'drifted')
    assert result['i_improvement_pass'] is True
    assert result['s0_baseline_reproduction_pass'] is False
    assert result['objective_gate_pass'] is False
