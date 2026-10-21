"""Additional source-pinned physical sensitivity-site exploration tests."""
from __future__ import annotations
import os
import runpy
import wave
from pathlib import Path
import numpy as np
import pytest

RUN = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                      "experiments/cc_b1_spatial_probe/run.py"),
                     run_name="cc_b1_spatial_suite")

def test_site_restriction_and_exact_single_area():
    from morphoacoustics.physical import Tract1DGeometry, TubeSection
    reference=Tract1DGeometry("oral",tuple(TubeSection(.01,2e-4) for _ in range(16)))
    for i in (0,2,4):
        a=RUN["edit"](reference,i,.9)
        assert a.sections[i].area_m2==pytest.approx(1.8e-4)
        assert all(a.sections[j]==reference.sections[j] for j in range(16) if j!=i)
    assert reference.sections[4].area_m2==2e-4
    for i,ratio in ((3,.9),(-1,.9),(16,.9),(2,1.),(2,0.),(2,1.2),(2,float("nan")),(2,True),(2,"1.1")):
        with pytest.raises(ValueError,match="UNSUPPORTED"):
            RUN["edit"](reference,i,ratio)
    with pytest.raises(ValueError,match="UNSUPPORTED"):
        RUN["edit"](Tract1DGeometry("oral",reference.sections[:15]),2,.9)

@pytest.mark.skipif(os.getenv("SPATIAL_PHYSICS")!="1",
                    reason="expensive physical source-pinned CI only")
def test_actual_unedited_source_with_spatially_edited_body(tmp_path):
    out=tmp_path/"new-research-output"
    r=RUN["run"](out)
    assert r["decision"]=="POSTHOC_SPATIAL_EXPLORATION_NOT_AUDIBILITY"
    assert len(r["conditions"])==7
    assert r["conditions"][0]["condition"]=="base"
    assert r["conditions"][0]["relative_raw_pressure_l2_vs_base"]==0.
    for item in r["conditions"]:
        lab=item["condition"]
        assert item["acoustic_calls"]==102
        with (out/(lab+".npy")).open("rb") as h:
            pressure=np.load(h,allow_pickle=False)
        assert pressure.shape==(24000,)
        with wave.open(str(out/(lab+".wav")),"rb") as h:
            assert (h.getframerate(),h.getnframes(),h.getnchannels(),h.getsampwidth())==(48000,24000,1,2)
            pcm=np.frombuffer(h.readframes(24000),dtype="<i2")
        gain=r["preview_gain_common_for_all_conditions"]
        np.testing.assert_allclose(pcm/32767.0,pressure*gain,atol=1./32767.,rtol=0)
        assert np.max(np.abs(pcm))<=29491
    with pytest.raises(FileExistsError):
        RUN["run"](out)
