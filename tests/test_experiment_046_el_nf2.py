"""EL-NF2 isolated physics/holdout/invalid-path tests — never production adoption."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import h5py
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments" / "046_el_nf2_spatial" / "run.py"
SPEC = importlib.util.spec_from_file_location("el_nf2_run", PATH)
assert SPEC and SPEC.loader
nf2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(nf2)


def artificial_data():
    # Deterministic 49 regular directions, four measured radii; energy in all 4 bands.
    az = np.linspace(-np.pi, np.pi, 49, endpoint=False)
    dirs = np.stack([np.cos(az), np.sin(az), np.zeros_like(az)], axis=1)
    xyz = []
    hrir = []
    times = np.arange(1024)
    for radius in nf2.RADII:
        for unit in dirs:
            xyz.append(radius * unit)
            ear = []
            for side in (-1, 1):
                arrival = 90 + int(round(45 * radius)) + int(round(side * 5 * unit[1]))
                t = times - arrival
                # broadband reproducible finite impulse with a stable dominant arrival
                wave = np.where(t == 0, 1.0, 0.0)
                wave += 0.3 * np.where(t == 2, 1.0, 0.0)
                wave += 0.17 * np.where(t == 5, 1.0, 0.0)
                wave *= (1.0 + side * 0.14 * unit[1])
                ear.append(wave)
            hrir.append(ear)
    return {"xyz": np.asarray(xyz), "ir": np.asarray(hrir), "sr": nf2.FS}


def test_all_groups_and_direction_holdout_are_disjoint():
    d = artificial_data()
    groups = nf2.match_directions(d["xyz"])
    assert len(groups) == 49
    split = nf2.split_coordinates(d["xyz"], groups)
    assert len(split["final"]) == 10
    assert len(split["validation"]) == 10
    assert len(split["training"]) == 29
    assert len(set(split["final"]) & set(split["training"])) == 0
    assert len(set(split["validation"]) & set(split["training"])) == 0
    assert len(set(split["final"]) & set(split["validation"])) == 0
    train_indices = {groups[d][i] for d in split["training"] for i in range(4)}
    final_indices = {groups[d][i] for d in split["final"] for i in range(4)}
    assert train_indices.isdisjoint(final_indices)


def test_training_position_identity_with_fixed_arrival():
    d = artificial_data()
    groups = nf2.match_directions(d["xyz"])
    direction = 10
    observed_idx = groups[direction][0]
    p = nf2.prediction(d["xyz"], d["ir"], groups, [10, 11, 12], d["xyz"][observed_idx], 0, "S1", "C1")
    np.testing.assert_allclose(p, d["ir"][observed_idx], rtol=0, atol=1e-11)


def test_joint_direction_distance_is_train_endpoints_only():
    d = artificial_data()
    groups = nf2.match_directions(d["xyz"])
    split = nf2.split_coordinates(d["xyz"], groups)
    target = groups[split["final"][0]][1]
    a = nf2.prediction(d["xyz"], d["ir"], groups, split["training"], d["xyz"][target], 1, "S2", "C1")
    corrupted = d["ir"].copy()
    # Corrupt *all* hidden 0.30 and 0.40m HRIR; S2 must never read them.
    for group in groups:
        corrupted[group[1]] = 1000.0
        corrupted[group[2]] = 1000.0
    b = nf2.prediction(d["xyz"], corrupted, groups, split["training"], d["xyz"][target], 1, "S2", "C1")
    np.testing.assert_array_equal(a, b)


def test_test_direction_acoustic_data_cannot_affect_prediction():
    d = artificial_data()
    groups = nf2.match_directions(d["xyz"])
    split = nf2.split_coordinates(d["xyz"], groups)
    target = groups[split["final"][0]][0]
    a = nf2.prediction(d["xyz"], d["ir"], groups, split["training"], d["xyz"][target], 0, "S1", "C1")
    corrupted = d["ir"].copy()
    for direction in split["final"]:
        for index in groups[direction]:
            corrupted[index] *= 10000
    b = nf2.prediction(d["xyz"], corrupted, groups, split["training"], d["xyz"][target], 0, "S1", "C1")
    np.testing.assert_array_equal(a, b)


def test_refuse_out_of_domain_and_invalid_xyz():
    d = artificial_data()
    groups = nf2.match_directions(d["xyz"])
    train = list(range(12))
    with pytest.raises(ValueError, match="UNSUPPORTED"):
        nf2.candidate_indices(d["xyz"], groups, train, np.array([0.01, 0, 0]))
    with pytest.raises(ValueError, match="INVALID"):
        nf2.candidate_indices(d["xyz"], groups, train, np.array([float("nan"), 0, 0]))


def test_unsupported_direction_with_insufficient_angular_coverage():
    d = artificial_data()
    groups = nf2.match_directions(d["xyz"])
    with pytest.raises(ValueError, match="UNSUPPORTED"):
        nf2.candidate_indices(d["xyz"], groups, [0, 1, 2], np.array([0.25, 0, 0]))


def test_bilateral_ild_zero_for_identical_ears():
    h = np.zeros((2, 2048))
    h[:, 35] = 1.0
    assert all(abs(v) < 1e-12 for v in nf2.ild(h))
    assert abs(nf2.itd_us(h)) < 0.01


def test_no_silent_nan_or_silent_band():
    h = np.zeros((2, 2048))
    with pytest.raises(ValueError, match="INDETERMINATE"):
        nf2.ild(h)
    h[:, 10] = 1.0
    h[0, 10] = np.nan
    with pytest.raises(ValueError, match="INVALID"):
        nf2.ild(h)


def test_no_overwrite(tmp_path: Path):
    dest = tmp_path / "evidence.json"
    dest.write_text("DO NOT REPLACE")
    with pytest.raises(FileExistsError):
        nf2.run(tmp_path / "nonexistent.sofa", dest)
    assert dest.read_text() == "DO NOT REPLACE"


def test_original_sofa_hash_fail_closed(tmp_path: Path):
    path = tmp_path / "synthetic.sofa"
    with h5py.File(path, "w") as obj:
        obj.attrs["SOFAConventions"] = "SimpleFreeFieldHRIR"
        obj.attrs["DataType"] = "FIR"
        sp = obj.create_dataset("SourcePosition", data=np.ones((1, 3)))
        sp.attrs["Type"] = "cartesian"
        sp.attrs["Units"] = "metre"
        obj.create_dataset("Data.IR", data=np.ones((1, 2, 48)))
        obj.create_dataset("Data.SamplingRate", data=np.array([48000]))
    with pytest.raises(ValueError, match="checksum"):
        nf2.load_sofa(path, require_original=True)


def test_synthetic_full_evaluation_runs_or_reports_coverage():
    d = artificial_data()
    e = nf2.evaluate(d)
    assert e["adoption"] == "NOT_ADOPTED"
    assert len(e["records"]) == 3 * 4 * 20
    assert e["final"]["verdict"] in ("GO_LIMITED_NUMERICAL_CANDIDATE", "REVISE_OR_REJECT", "INDETERMINATE")


def test_coordinate_units_rejection():
    with pytest.raises(ValueError, match="UNSUPPORTED"):
        nf2.source_cartesian(np.ones((2, 3)), "spherical", "degree, degree, second")
