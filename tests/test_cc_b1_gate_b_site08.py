"""Bounded CC-B1 research-only tests; no production source or Studio changes."""
from __future__ import annotations

import os
import hashlib
from types import SimpleNamespace
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
    assert receipt["status"] == "RESEARCH_MACHINE_PASS_PENDING_INDEPENDENT_AUDIT"
    assert receipt["prespecified_freeze_commit"] == "ca8bf64c8525a9cf59cb1332c4819763a0f9197e"
    assert receipt["section_zero_based"] == 8
    assert receipt["runtime"]["numpy_version"] == "2.4.6"
    assert receipt["runtime"]["python_version"].startswith("3.11")
    assert receipt["ci"]["artifact_name"] == "cc-b1-gate-b-site08-raw-pa-and-provenance"
    assert receipt["negative_controls"]["scope"] == "synthetic_gate_b_acceptance_boundary_only"
    assert len(receipt["negative_controls"]["controls"]) == 8
    assert all(x["status"] == "PASS" for x in receipt["negative_controls"]["controls"])
    assert receipt["negative_controls"]["not_tested"][0]["status"] == "NOT_TESTED"
    for name, digest in receipt["artifact_file_sha256"].items():
        assert hashlib.sha256((out/name).read_bytes()).hexdigest() == digest
    assert receipt["baseline_repeat"]["fresh_physical_execution"]
    assert receipt["baseline_repeat"]["acoustic_calls"] == 102
    assert receipt["baseline_repeat"]["quantized_sha256"] == receipt["conditions"][1]["raw_pressure_quantized_sha256"]
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

def test_frozen_oracle_cannot_be_silently_replaced(tmp_path):
    path=RUNNER["ORACLE"]
    RUNNER["verify_frozen_oracle"](path)
    bad=tmp_path/"modified_oracle.json"
    bad.write_text(path.read_text(encoding="utf-8").replace('"site08-v1"', '"site08-v2"'),
                   encoding="utf-8")
    # Even if a syntactically valid JSON retains the schema, content-hash pin fails.
    bad.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(RuntimeError,match="ORACLE_CONTENT_DRIFT"):
        RUNNER["verify_frozen_oracle"](bad)


def test_frozen_task_digest_and_finite_peak_refusals():
    RUNNER["verify_task_plan_digest"](
        "17148dea27e59abfb626b149beebcc7893d4ff9ba04ce4cf3af9ad408ce8a7bf"
    )
    with pytest.raises(RuntimeError, match="TASK_PLAN_DRIFT"):
        RUNNER["verify_task_plan_digest"]("0" * 64)
    with pytest.raises(RuntimeError, match="NONFINITE_OR_MALFORMED_PEAKS"):
        RUNNER["validated_peak_triplet"](np.array([250., float("nan"), 3100.]))


def test_fault_injected_fallback_and_nonfinite_pressure_cannot_pass():
    from morphoacoustics.domain.result import FeasibilityStatus
    from morphoacoustics.physical import Tract1DGeometry, TubeSection
    geometry = Tract1DGeometry(
        cavity_id="oral", sections=tuple(TubeSection(0.01, 1e-4) for _ in range(16))
    )
    fake = SimpleNamespace(
        feasibility=SimpleNamespace(status=FeasibilityStatus.FEASIBLE),
        endpoint=geometry,
        waveform=np.zeros(24000, dtype=np.float64),
        acoustic_call_count=102,
    )
    assert RUNNER["validated_pressure"](fake).shape == (24000,)
    fake.feasibility.status = FeasibilityStatus.UNSUPPORTED
    with pytest.raises(RuntimeError, match="PHYSICAL_FALLBACK_OR_INCOMPLETE"):
        RUNNER["validated_pressure"](fake)
    fake.feasibility.status = FeasibilityStatus.FEASIBLE
    fake.waveform = np.full(24000, float("inf"))
    with pytest.raises(RuntimeError, match="NONFINITE_OR_MALFORMED_PRESSURE"):
        RUNNER["validated_pressure"](fake)
    fake.waveform = np.zeros(24000, dtype=np.float64)
    fake.acoustic_call_count = 101
    with pytest.raises(RuntimeError, match="PHYSICAL_FALLBACK_OR_INCOMPLETE"):
        RUNNER["validated_pressure"](fake)


def test_prepared_revision_and_provenance_guard():
    from morphoacoustics.physical import Tract1DGeometry, TubeSection
    from morphoacoustics.preparation import TRACT1D_BACKEND_ID, PreparationProvenance
    base = Tract1DGeometry("oral", tuple(TubeSection(0.01, 1e-4) for _ in range(16)))
    prepared = SimpleNamespace(
        backend_id=TRACT1D_BACKEND_ID,
        rest_state=RUNNER["edit_rest_geometry"](base, 1.10),
        provenance=PreparationProvenance(
            source="cc-b1-gate-b-site08-new-core-physical-run",
            model="frozen-one-site-rest-area-section-8/v0",
            notes=("rest_area_ratio=1.10",
                   "gate-a-commit=ca8bf64c8525a9cf59cb1332c4819763a0f9197e"),
        ),
    )
    RUNNER["verify_prepared_binding"](base, prepared, 1.10)
    with pytest.raises(RuntimeError, match="PREPARED_BINDING_MISMATCH"):
        RUNNER["verify_prepared_binding"](base, prepared, 0.90)
    prepared.provenance = PreparationProvenance(source="forged", model="untrusted")
    with pytest.raises(RuntimeError, match="PREPARED_BINDING_MISMATCH"):
        RUNNER["verify_prepared_binding"](base, prepared, 1.10)
