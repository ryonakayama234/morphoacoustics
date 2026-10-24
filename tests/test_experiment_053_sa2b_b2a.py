"""B2-A conservative stationary area-junction physics checks."""
import importlib.util
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"experiments/053_b2a_anatomical_waveguide/run.py"
spec=importlib.util.spec_from_file_location("b2a_experiment",PATH)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

def test_junction_energy_and_reflection():
    for zl,zr in ((2.,2.),(2.,5.),(5.,2.),(1.,100.)):
        for a,b in ((1.,0.),(0.,1.),(1.25,-.4)):
            left,right=mod.junction(a,b,zl,zr)
            assert np.isclose(a*a/zl+b*b/zr,left*left/zl+right*right/zr,rtol=1e-12,atol=1e-12)
        left,right=mod.junction(1.,0.,zl,zr)
        assert np.isclose(left,(zr-zl)/(zr+zl),atol=1e-12)
        assert np.isclose(right,2*zr/(zl+zr),atol=1e-12)

def test_uniform_reduces_to_b1b():
    b1=mod._b1()
    for term in ("closed","pressure_release","matched","b0"):
        cfg=mod.AnatomicalDuct((.01,)*16,(b1.M0_LIP_AREA_M2,)*16,termination=term)
        original=b1.LocalTravelingWaveDuct(b1.PhysicalClockDuct(termination=term))
        new=mod.AnatomicalTravelingWaveDuct(cfg)
        drive=np.zeros(140)
        drive[0]=1e-6
        drive[17]=-2e-7
        for u in drive:
            a=new.step(u)
            b=original.step(u)
            for k,kb in (("p_lip_pa","lip_pressure_pa"),("p_in_pa","inlet_pressure_pa"),("duct_energy_j","duct_energy_j"),("mouth_energy_j","mouth_energy_j"),("source_work_j","source_work_j"),("outlet_dissipation_j","outlet_dissipation_j")):
                assert np.isclose(a[k],getattr(b,kb),rtol=1e-10,atol=1e-22),(term,k)
            assert abs(a["residual_j"])<1e-18

def test_m0_m1_frozen_physical_wavefront():
    import json
    ref=json.loads((ROOT/"experiments/028_task_field_morphology_transfer/frozen_reference.json").read_text())["M0"]
    for vowel in ("a","i"):
        areas=tuple(ref[f"{vowel}_areas_m2"])
        for section_length in ((.01,.011) if vowel=="a" else (.01,)):
            cfg=mod.AnatomicalDuct((section_length,)*16,areas,termination="matched")
            wave=mod.AnatomicalTravelingWaveDuct(cfg)
            result=wave.impulse(45)
            assert np.flatnonzero(result)[0]==32
            assert np.isclose(cfg.one_way_s,16*section_length/343)
            assert np.isclose(cfg.dt*32,cfg.one_way_s)
