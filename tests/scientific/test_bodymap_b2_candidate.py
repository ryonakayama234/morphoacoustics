"""Small component-only checks, not full-grid FZ acceptance evaluations."""
import math
import pytest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
pytest.importorskip("scipy")
from experiments.bodymap_b2_passive_loss.prereg_binding import (
    Refusal,FREQUENCIES_HZ,validate_lambda,validate_envelope)
from experiments.bodymap_b2_passive_loss.candidate.coefficients import coefficients
from experiments.bodymap_b2_passive_loss.candidate.transfer import one_frequency

def test_grid_and_invalid_loss():
    assert len(FREQUENCIES_HZ)==351
    for invalid in (-1,1.1,True,float("nan"),float("inf")):
        with pytest.raises(Refusal) as err:
            validate_lambda(invalid)
        assert err.value.code=="INVALID_LOSS_PARAMETER"

def test_lossless_uniform_single_bin():
    result=one_frequency(200,(.006,),(.160,),0.0)
    angle=2*math.pi*200*.16/343
    zstar=1.21*343/(math.pi*.006**2)
    assert abs(result["T"][0,0]-math.cos(angle))<1e-12
    assert abs(result["T"][0,1]-1j*zstar*math.sin(angle))<1e-8
    assert abs(result["detT"]-1)<1e-12

def test_lrf_passive_coefficient_single_bin():
    z,y,g,zc,_,_=coefficients(200,.006,1.0)
    assert z.real>0 and y.real>0 and g.real>0 and zc.real>0

def test_geometry_envelope():
    validate_envelope((.006,)*16,(.010,)*16)
    with pytest.raises(Refusal):
        validate_envelope((.006,)*16,(.020,)*16)
