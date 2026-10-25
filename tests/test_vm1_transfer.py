"""VM-1A: physics and falsification controls; not a voice-quality certification."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pytest

from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics_waveguide import PassiveWaveguideConfig

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "vm1_transfer.py"
SPEC = spec_from_file_location("vm1a_science", SCRIPT)
assert SPEC and SPEC.loader
VM = module_from_spec(SPEC)
SPEC.loader.exec_module(VM)


def uniform(termination: str = "matched") -> PassiveWaveguideConfig:
    geometry = Tract1DGeometry(
        "control", tuple(TubeSection(0.010, 8e-4) for _ in range(16))
    )
    return PassiveWaveguideConfig(geometry, termination=termination)


def test_uniform_matched_analytic_delay_and_complex_phase() -> None:
    result = VM.uniform_matched_oracle()
    assert result["status"] == "MATCHED_UNIFORM_ANALYTIC_PASS"
    assert result["first_nonzero_outlet_tick"] == 32
    assert result["expected_delay_s"] == pytest.approx(0.16 / 343.0, rel=1e-13)
    assert result["max_relative_complex_transfer_error"] < 1e-9


def test_frozen_exp028_body_contract_is_exact() -> None:
    bodies, digest = VM.frozen_bodies()
    assert len(digest) == 64
    assert set(bodies) == {"M0", "M1"}
    assert len(bodies["M0"].sections) == len(bodies["M1"].sections) == 16
    assert bodies["M0"].total_length_m == pytest.approx(0.16)
    assert bodies["M1"].total_length_m == pytest.approx(0.176)
    assert [s.area_m2 for s in bodies["M0"].sections] == [
        s.area_m2 for s in bodies["M1"].sections
    ]


def test_zero_pulse_has_zero_physical_output() -> None:
    cfg = uniform("b0")
    trace = VM.native_trace(cfg, np.zeros(96, dtype=np.float64))
    for label in ("p_in_pa", "p_mouth_pa", "U_mouth_m3_s"):
        assert np.count_nonzero(trace[label]) == 0
    assert trace["max_energy_residual_fraction_of_tolerance"] == 0


def test_amplitude_linearity_and_b0_no_fake_sound() -> None:
    cfg = uniform("b0")
    inp = VM.make_pulse(cfg, 128, VM.VOLUME_M3)
    out = VM.native_trace(cfg, inp)
    twice = VM.native_trace(cfg, 2 * inp)
    for name in ("p_in_pa", "p_mouth_pa", "U_mouth_m3_s"):
        np.testing.assert_allclose(twice[name], 2 * out[name], rtol=1e-10, atol=1e-14)
    assert out["max_energy_residual_fraction_of_tolerance"] <= 1.0
    assert twice["max_energy_residual_fraction_of_tolerance"] <= 1.0


def test_boundary_intervention_does_not_mask_physical_port() -> None:
    matched, b0 = uniform("matched"), uniform("b0")
    flow = VM.make_pulse(matched, 512, VM.VOLUME_M3)
    a = VM.native_trace(matched, flow)
    b = VM.native_trace(b0, flow)
    assert np.max(np.abs(a["p_mouth_pa"] - b["p_mouth_pa"])) > 1e-10
    assert VM.transfer(matched, a)["H600_to_H100_db"] == pytest.approx(0.0, abs=1e-8)


def test_reject_corrupt_frozen_body_and_bad_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rogue = tmp_path / "untrusted.json"
    rogue.write_text('{"M0":{"a_areas_m2":[]}}', encoding="utf-8")
    monkeypatch.setattr(VM, "FROZEN", rogue)
    with pytest.raises(ValueError, match="FROZEN_BODY_BLOB_MISMATCH"):
        VM.frozen_bodies()
    cfg = uniform()
    with pytest.raises(ValueError, match="INVALID_INJECTED_VOLUME"):
        VM.make_pulse(cfg, 128, float("nan"))
    with pytest.raises(ValueError, match="INVALID_FLOW_TRACE"):
        VM.native_trace(cfg, np.array([1.0, np.nan] + [0.0] * 126))


def test_short_record_is_explicitly_unsupported() -> None:
    with pytest.raises(ValueError, match="INSUFFICIENT_IMPULSE_OBSERVATION"):
        VM.make_pulse(uniform(), 32, VM.VOLUME_M3)
