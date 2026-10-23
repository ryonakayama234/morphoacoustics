"""Source-domain tests only; acoustic/creator gates are separate."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location(
    "jet_source_p0", Path(__file__).resolve().parents[1] / "experiments/047_glottal_jet_closure/run.py")
assert spec is not None and spec.loader is not None
p0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p0)


def test_no_pressure_means_no_sound():
    s = p0.make_source(0.0, 1e-6, 0.02)
    assert np.array_equal(s["source_m3_s"], np.zeros(p0.SAMPLES))
    assert s["reynolds"] == 0


def test_closed_phase_has_no_flux_for_zero_leak():
    s = p0.make_source(800., 0., 0., samples=4800)
    assert np.count_nonzero(s["source_m3_s"]) > 0
    assert np.all(s["source_m3_s"][s["glottal_area_m2"] == 0] == 0)


def test_pressure_squared_root_law_without_noise():
    a = p0.make_source(800., 0., 0.)["flow_m3_s"]
    b = p0.make_source(1600., 0., 0.)["flow_m3_s"]
    assert np.allclose(b, a * np.sqrt(2), rtol=2e-15, atol=0.)


def test_closure_is_reproducible_seeded_and_source_gated():
    a = p0.make_source(800., 0., 0.02)
    b = p0.make_source(800., 0., 0.02)
    c = p0.make_source(800., 0., 0.02, seed=p0.SEED + 1)
    assert np.array_equal(a["source_m3_s"], b["source_m3_s"])
    assert not np.array_equal(a["source_m3_s"], c["source_m3_s"])
    assert np.all(a["aspiration_m3_s"][a["glottal_area_m2"] == 0] == 0)


def test_no_noise_is_exact_baseline_and_leak_changes_closed_phase():
    modal = p0.make_source(800., 0., 0.)
    leak = p0.make_source(800., 0.15e-6, 0.)
    assert np.array_equal(modal["aspiration_m3_s"], np.zeros(p0.SAMPLES))
    closed = modal["glottal_area_m2"] == 0
    assert np.all(modal["source_m3_s"][closed] == 0)
    assert np.any(leak["source_m3_s"][closed] > 0)


def test_bad_controls_are_rejected():
    for args in [(-1., 0., 0.), (800., -1., 0.), (800., 0., float("nan"))]:
        with pytest.raises(ValueError):
            p0.make_source(*args)


def test_source_high_band_screen():
    for params in p0.CASES.values():
        source = p0.make_source(*params)["source_m3_s"]
        assert p0._high_band_energy(source) < 0.10
