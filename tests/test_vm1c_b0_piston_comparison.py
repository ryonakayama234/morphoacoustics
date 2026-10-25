"""VM-1C: exact reused SA-2A oracle, B0 physical law, falsifiable body perturbations."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
import math
from pathlib import Path

import numpy as np
import pytest

# SA-2A requires experiment-local SciPy, not a new Core runtime dependency.
# Dedicated VM-1C CI explicitly installs it and runs these tests; the normal
# Core matrix may omit it and must not fail on a research-only dependency.
pytest.importorskip("scipy", reason="research-only SA-2A oracle requires scipy")

SCRIPT = Path(__file__).resolve().parents[1] / "tools/vm1c_b0_piston_comparison.py"
SPEC = spec_from_file_location("vm1c_compare", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
V = module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def test_pinned_unmodified_reference_and_frozen_16_section_body() -> None:
    data, oracle = V.verified_inputs()
    assert V.blob_sha1(V.REFERENCE.read_bytes()) == V.REF_BLOB_SHA1
    assert V.blob_sha1(V.BODY.read_bytes()) == V.BODY_BLOB_SHA1
    assert len(data["M0"]["a_areas_m2"]) == 16
    assert oracle["C"] == V.C and oracle["X_MAX"] == V.KA_MAX
    assert math.sqrt(data["M0"]["a_areas_m2"][-1]/math.pi) == pytest.approx(.016)


def test_analytical_piston_matches_SA2A_independent_rayleigh_overlap() -> None:
    _, oracle = V.verified_inputs()
    ka = np.array([.02, .1, .25, .55, .8])
    ref = oracle["_normalized_nonnegative"](ka)
    direct_overlap = oracle["normalized_overlap_oracle"](ka)
    assert np.max(abs(ref-direct_overlap)) <= 2e-9
    assert np.all(ref.real >= 0)
    assert np.all(ref.imag > 0)


@pytest.mark.parametrize("radius", [.005, .010, .016])
def test_b0_leading_asymptotic_real_and_imag(radius: float) -> None:
    _, oracle = V.verified_inputs()
    x = .001
    f = x * V.C / (2*math.pi*radius)
    zc = V.RHO * V.C / (math.pi*radius**2)
    approximate = V.b0_impedance(radius, f)
    exact = complex(oracle["radiation_impedance"](f, radius))
    assert abs(approximate-exact)/zc < 2e-6
    assert (approximate/zc).real == pytest.approx(x*x/2, rel=.001)
    assert (approximate/zc).imag == pytest.approx(8*x/(3*math.pi), rel=.001)


@pytest.mark.parametrize("frequency", [100., 300., 600., 1000., 1600., 2500.])
def test_b0_discrete_and_continuum_not_conflated(frequency: float) -> None:
    r = .016
    cont = V.b0_impedance(r, frequency)
    disc = V.b0_impedance(r, frequency, dt=.010/(2*V.C))
    assert cont.real >= 0 and disc.real >= 0
    assert abs(cont-disc) > 0
    assert math.isfinite((cont-disc).real) and math.isfinite((cont-disc).imag)


def test_transmission_matrix_matches_uniform_tube_known_analytic() -> None:
    area = math.pi * .01**2
    m = V.port_matrix([area]*16, .01, 600.0)
    characteristic = V.RHO * V.C / area
    result = V.tube_load(m, characteristic)
    expected = np.exp(-1j*2*math.pi*600*.16/V.C)
    assert result["HU"] == pytest.approx(expected, rel=1e-12)
    assert result["HpU"] == pytest.approx(expected*characteristic, rel=1e-12)
    assert result["Zin"] == pytest.approx(characteristic, rel=1e-12)
    assert result["power_balance_relative_error"] < 1e-12


def test_true_body_and_boundary_comparison_preserves_power_and_complex_ports() -> None:
    record = V.run()
    assert record["research_verdict"] == "SA2A_IDEAL_PISTON_COMPARISON_MEASURED"
    assert record["gates_pass"]
    assert len(record["M0_M1_loaded_cases"]) == 2
    assert len(record["M0_M1_loaded_cases"]["M0"]) == 18
    assert len(record["M0_M1_loaded_cases"]["M1"]) == 18
    assert len(record["port_selectivity"]) == 6
    assert len(record["calibrations"]) == 18
    assert all(x["power_balance_relative_error"] < 1e-8
               for cases in record["M0_M1_loaded_cases"].values() for x in cases)
    assert all(set(x["HpU"]) == {"real", "imag"}
               for cases in record["M0_M1_loaded_cases"].values() for x in cases)
    assert record["real_biological_radiation"] == "INDETERMINATE_REAL_RADIATION"
    assert record["voice_quality"] == "VOICE_NO_GO_UNCHANGED"
    assert record["provenance"]["clean_tracked_checkout"]


def test_out_of_range_and_corrupt_reference_never_fake_physical_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ValueError, match="UNSUPPORTED_KA"):
        V.check_frequency(.016, 3000)
    with pytest.raises(ValueError, match="INVALID_APERTURE_OR_FREQUENCY"):
        V.check_frequency(-.010, 600)
    with pytest.raises(ValueError, match="INVALID_APERTURE_OR_FREQUENCY"):
        V.b0_impedance(float("nan"), 100)
    with pytest.raises(ValueError, match="INVALID_NONPASSIVE_BOUNDARY"):
        V.tube_load(np.eye(2), -1+0j)
    with pytest.raises(ValueError, match="INVALID_NATIVE_CLOCK"):
        V.b0_impedance(.01, 600, dt=-.001)
    altered = tmp_path / "source_mismatch.py"
    altered.write_bytes(V.REFERENCE.read_bytes()+b"\n# TAMPER\n")
    monkeypatch.setattr(V, "REFERENCE", altered)
    with pytest.raises(ValueError, match="SA2A_REFERENCE_SHA_MISMATCH"):
        V.verified_inputs()
    monkeypatch.setattr(V, "REFERENCE", SCRIPT.parent.parent /
                        "experiments/049_baffled_piston_sa2a/run.py")
    bad_body = tmp_path / "changed.json"
    bad_body.write_text('{"M0":{"a_areas_m2":[]}}', encoding="utf-8")
    monkeypatch.setattr(V, "BODY", bad_body)
    with pytest.raises(ValueError, match="FROZEN_BODY_SHA_MISMATCH"):
        V.verified_inputs()
