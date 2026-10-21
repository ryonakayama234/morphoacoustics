"""Independent W0 oracles + W1 numerical and audible artifact gates, no realism claim."""
from __future__ import annotations
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest

pytest.importorskip('scipy')
sf = pytest.importorskip('soundfile')
EXPERIMENT = Path(__file__).resolve().parents[1] / 'experiments' / '042_nv1_breath_ear'
sys.path.insert(0, str(EXPERIMENT))
from source import (N, FS, PRESETS, SEED, steady_orifice, realize_exhale,
                    source_from_flow, describe_spectrum)


@pytest.mark.parametrize('preset,expected', [
    ('P0', (0.0002757716446627536, 9.19238815542512, 3787.501226052541, 0.03309259735953043)),
    ('P2', (0.00039, 13.0, 5356.335601388229, 0.0936)),
    ('A2', (0.0005515432893255072, 9.19238815542512, 5356.33560138823, 0.06618519471906086)),
    ('Z0', (0., 0., 0., 0.)),
])
def test_wolfram_steady_oracles(preset, expected):
    np.testing.assert_allclose(steady_orifice(*PRESETS[preset]), expected, rtol=1e-8, atol=1e-12)


def test_physical_timelines_and_zero_drive():
    for case in ('P0', 'P2', 'A2'):
        f = realize_exhale(*PRESETS[case])
        assert len(f.q_mean_m3_s) == N
        assert f.q_mean_m3_s[0] == 0.0
        np.testing.assert_allclose(f.q_mean_m3_s.max(), steady_orifice(*PRESETS[case])[0], rtol=1e-8)
        assert np.isfinite(f.pneumatic_power_w).all()
        assert np.all(f.pneumatic_power_w >= 0)
    f0 = realize_exhale(*PRESETS['Z0'])
    source0 = source_from_flow(f0)
    assert not np.any(f0.q_mean_m3_s)
    assert not np.any(source0.q_ac_m3_s)
    assert not np.any(source0.dq_dt_m3_s2)
    assert source0.efficiency == 0.0


def test_determinism_distinguishes_source_and_gain():
    a = source_from_flow(realize_exhale(*PRESETS['P0']))
    a2 = source_from_flow(realize_exhale(*PRESETS['P0']))
    p = source_from_flow(realize_exhale(*PRESETS['P2']))
    v = source_from_flow(realize_exhale(*PRESETS['A2']))
    assert a.source_sha256 == a2.source_sha256
    np.testing.assert_array_equal(a.q_ac_m3_s, a2.q_ac_m3_s)
    assert len({a.source_sha256, p.source_sha256, v.source_sha256}) == 3
    for src in (a, p, v):
        assert np.isfinite(src.q_ac_m3_s).all()
        assert 0 < src.efficiency < 0.01
        assert src.q_ac_m3_s[0] == src.q_ac_m3_s[-1] == 0.0
    for other in (p, v):
        fitted_gain = float(np.dot(a.q_ac_m3_s, other.q_ac_m3_s) /
                            np.dot(a.q_ac_m3_s, a.q_ac_m3_s))
        residual = np.linalg.norm(other.q_ac_m3_s - fitted_gain * a.q_ac_m3_s)
        assert residual / np.linalg.norm(other.q_ac_m3_s) > 0.01, 'must not be gain-only'
    assert source_from_flow(realize_exhale(*PRESETS['P0']), seed=SEED+1).source_sha256 != a.source_sha256


@pytest.mark.parametrize('p,a', [(-1, 30e-6), (float('nan'), 30e-6), (float('inf'), 30e-6),
                              (120, -1), (120, 0), (120, float('nan')), (1000, 30e-6)])
def test_refuses_invalid_and_unsupported(p,a):
    with pytest.raises(ValueError, match='INVALID|UNSUPPORTED'):
        realize_exhale(p,a)


def test_bad_seed_refusal():
    with pytest.raises(ValueError, match='INVALID'):
        source_from_flow(realize_exhale(*PRESETS['P0']), seed=-1)


def test_actual_wav_manifest_and_no_overwrite(tmp_path):
    spec=importlib.util.spec_from_file_location('nv1_runner', EXPERIMENT / 'run.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    folder=tmp_path/'w1'
    result=mod.run(folder)
    assert result['scope']=='W0_W1_IDEAL_A_ONLY'
    assert set(result['cases'])==set(PRESETS)
    assert (folder/'evidence.json').exists()
    for name,receipt in result['cases'].items():
        wave,sr=sf.read(folder/receipt['wav'],always_2d=True)
        assert sr==FS and wave.shape[1]==2
        assert np.isfinite(wave).all() and abs(wave).max()<0.95
        if name=='Z0':
            assert not wave.any()
        else:
            assert abs(wave).max()>0.00001
        with np.load(folder/receipt['trace']) as data:
            assert 'q_ac_m3_s' in data.files
            assert 'receiver_raw_A_pa' in data.files
    with pytest.raises(FileExistsError):mod.run(folder)
    assert json.loads((folder/'evidence.json').read_text())['claim']=='EXPERIMENTAL_NOT_ADOPTED'
