"""OD-1 structural and negative tests. Real physics runs in dedicated CI job."""
from __future__ import annotations
from pathlib import Path
import math
import runpy
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
RUN=runpy.run_path(str(ROOT/"experiments/od1_local_shape/run.py"))
OBS=runpy.run_path(str(ROOT/"experiments/od1_local_shape/oracle.py"))
validate=RUN["validate"]
edit_geometry=RUN["edit_geometry"]


def test_exact_edit_envelope_rejects_ambiguous_and_invalid_values() -> None:
    for center,ratio in ((True,1.1),(4,1),(4,True),(0,1.1),(9,1.1),
                         (4,float("nan")),(4,float("inf")),(4,.95),("4",1.1)):
        with pytest.raises(ValueError):
            validate(center,ratio)
    for center in (4,8):
        for ratio in (.9,1.,1.1):
            assert validate(center,ratio)==(center,ratio)


def test_independent_published_geometry_oracle_and_static_predictions() -> None:
    base=OBS["published_areas"]()
    assert base.shape==(16,)
    assert np.all(base>0)
    f=np.arange(100.,3500.1,25.)
    hf=np.arange(100.,3500.1,100.)
    hb=OBS["recursive_uout_uin"](base,hf)
    for center in (4,8):
        for r in (.9,1.,1.1):
            area=OBS["reference_areas"](center,r)
            h1=OBS["direct_uout_uin"](area,f)
            h2=OBS["recursive_uout_uin"](area,f)
            assert np.max(np.abs(h1-h2)/np.maximum(np.abs(h1),1e-12))<1e-9
            vol=OBS["static_volume"](area)
            assert vol==pytest.approx(RUN["EXPECTED_VOLUMES"][(center,r)],rel=1e-12)
            assert np.isfinite(OBS["volume_derivative"](area,center))
            if r!=1.:
                actual=float(np.linalg.norm(OBS["recursive_uout_uin"](area,hf)-hb)/np.linalg.norm(hb))
                assert actual==pytest.approx(RUN["EXPECTED_HARMONICS"][(center,r)],abs=2e-7)


def test_candidate_vs_independent_cells_and_frozen_null() -> None:
    from morphoacoustics.physical import Tract1DGeometry, TubeSection
    base=Tract1DGeometry("oral",tuple(TubeSection(.01,float(a)) for a in OBS["published_areas"]()))
    assert edit_geometry(base,4,1.) is base
    for center in (4,8):
        for r in (.9,1.1):
            g=edit_geometry(base,center,r)
            arr=RUN["areas"](g)
            expect=OBS["reference_areas"](center,r)
            assert np.max(np.abs(np.log(arr/expect)))<1e-12
            assert np.array_equal(arr[np.abs(np.arange(16)-center)>2],
                                  OBS["published_areas"]()[np.abs(np.arange(16)-center)>2])
    bad=Tract1DGeometry("oral", (TubeSection(.01,.001),))
    with pytest.raises(ValueError):
        edit_geometry(bad,4,1.1)


def test_aggregate_volume_is_not_a_sufficient_anatomical_oracle() -> None:
    ref=OBS["reference_areas"](4,1.1)
    altered=ref.copy()
    delta=float(ref[3])*.01
    altered[3]+=delta
    altered[7]-=delta
    assert math.isclose(OBS["static_volume"](altered),OBS["static_volume"](ref),
                        rel_tol=0,abs_tol=1e-19)
    assert float(np.max(np.abs(np.log(altered/ref))))>.001
