"""Bounded CC-B1 research-only tests; no production source or Studio changes."""
from __future__ import annotations

import os
from pathlib import Path
import runpy
import wave

import numpy as np
import pytest

RUNNER = runpy.run_path(str(Path(__file__).resolve().parents[1] /
   "experiments/cc_b1_gate_b_site08/run.py"), run_name="cc_b1_pilot")

def test_rejects_unsafe_ratios():
    validate = RUNNER["checked_ratio"]
    for illegal in (0.8, 1.2, -1.0, float("nan"), float("inf"), 0, 1, "1.00", None, True):
        with pytest.raises(ValueError, match="UNSUPPORTED"):
            validate(illegal)
    for allowed in (0.90, 1.00, 1.10):
        assert validate(allowed) == allowed

def test_single_section_rest_edit_is_identity_elsewhere():
    from morphoacoustics.physical import Tract1DGeometry, TubeSection
    baseline = Tract1DGeometry(
        cavity_id="oral", sections=tuple(TubeSection(length_m=0.01,area_m2=1e-4)
                                         for _ in range(16)))
    edit = RUNNER["edit_rest_geometry"](baseline,1.10)
    assert edit.sections[8].area_m2 == pytest.approx(1.1e-4)
    assert all(edit.sections[j] == baseline.sections[j] for j in range(16) if j != 8)
    assert baseline.sections[8].area_m2 == pytest.approx(1e-4)
    with pytest.raises(ValueError, match="UNSUPPORTED"):
        RUNNER["edit_rest_geometry"](Tract1DGeometry(
            cavity_id="oral",sections=baseline.sections[:-1]), 1.1)

@pytest.mark.skipif(os.getenv("CC_B1_GATE_B_PHYSICS") != "1",
                    reason="dedicated CI invokes exact frozen physical run")
def test_frozen_site08_fresh_physics_and_exact_repeat(tmp_path):
    out = tmp_path / "new-physical-output"
    receipt = RUNNER["run"](out)
    assert receipt["status"] == "RESEARCH_MACHINE_PASS_PENDING_INDEPENDENT_AUDIT"\n    assert receipt["prespecified_freeze_commit"] == "ca8bf64c8525a9cf59cb1332c4819763a0f9197e"\n    assert receipt["section_zero_based"] == 8\n    assert receipt["baseline_repeat"]["fresh_physical_execution"]\n    assert receipt["baseline_repeat"]["acoustic_calls"] == 102\n    assert receipt["baseline_repeat"]["quantized_sha256"] == receipt["conditions"][1]["raw_pressure_quantized_sha256"]
    assert [x["ratio"] for x in receipt["conditions"]] == [0.9, 1.0, 1.1]
    assert receipt["conditions"][1]["relative_l2_difference_from_baseline"] == 0.0
    assert receipt["conditions"][0]["relative_l2_difference_from_baseline"] > 1e-8
    assert receipt["conditions"][2]["relative_l2_difference_from_baseline"] > 1e-8
    assert (out/"decision.json").exists()
    gains = []
    for ratio in (0.9,1.0,1.1):
        raw = np.load(out/f"pressure_{ratio:.2f}.npy",allow_pickle=False)
        assert raw.shape == (24000,)
        path = out/f"preview_{ratio:.2f}.wav"
        assert path.exists()
        with wave.open(str(path),"rb") as wav:
            assert (wav.getnchannels(),wav.getsampwidth(),wav.getframerate(),wav.getnframes()) == (1,2,48000,24000)
            samples = np.frombuffer(wav.readframes(24000),dtype="<i2")
        assert np.max(np.abs(samples)) <= 29491
        gains.append(receipt["preview_audio"]["comparison_shared_gain"])
        np.testing.assert_allclose(samples/32767.0, raw*gains[-1],rtol=0,atol=1/32767)
    assert len(set(gains)) == 1
    repeat=np.load(out/"pressure_repeat_1.00.npy", allow_pickle=False)
    original=np.load(out/"pressure_1.00.npy", allow_pickle=False)
    assert repeat.shape==original.shape==(24000,)
    assert receipt["baseline_repeat"]["quantized_sha256"]==receipt["conditions"][1]["raw_pressure_quantized_sha256"]
    with pytest.raises(FileExistsError):
        RUNNER["run"](out)

def test_site_and_source_identity_refusals():
    check=RUNNER["checked_section_index"]
    assert check(8)==8
    for site in (0,2,4,-1,7,9,16,8.0,True,"8",None):
        with pytest.raises(ValueError,match="UNSUPPORTED"):
            check(site)
    pressure=np.arange(16,dtype=np.float64)
    digest=RUNNER["sha_array"](pressure)
    RUNNER["verify_source_identity"](digest,pressure.copy())
    tampered=pressure.copy();tampered[2]+=1.0
    with pytest.raises(ValueError,match="SOURCE_CHANGED"):
        RUNNER["verify_source_identity"](digest,tampered)
