"""Synthetic end-to-end CLI smoke: output must never be called measured KEMAR proof."""
from pathlib import Path
import json
import subprocess
import sys

import numpy as np
import pytest

h5py=pytest.importorskip("h5py")
pytest.importorskip("scipy")


def test_full_cli_synthetic_without_scientific_promotion(tmp_path):
    root=Path(__file__).resolve().parents[1]
    script=root/"experiments/047_el_nf3_receiver/run.py"
    auditor=root/"experiments/047_el_nf3_receiver/audit.py"
    path=tmp_path/"unmeasured_synthetic.sofa"
    xyz=[]
    signals=[]
    fs=48000
    for azi in range(0,360,10):
        for elev in (-20,0,20):
            for radius in (.20,.30,.40,.50):
                theta=np.deg2rad(azi);phi=np.deg2rad(elev)
                xyz.append((azi,elev,radius))
                s=np.zeros((2,256),dtype=float)
                base=10+round(radius*fs/343)
                spread=round(np.sin(theta)*4)
                s[0,base-spread]=1/radius
                s[1,base+spread]=.9/radius
                signals.append(s)
    with h5py.File(path,"w") as f:
        f.attrs["SOFAConventions"]="SimpleFreeFieldHRIR"
        ds=f.create_dataset("SourcePosition",data=np.asarray(xyz))
        ds.attrs["Type"]="spherical";ds.attrs["Units"]="degree, degree, metre"
        f.create_dataset("Data.IR",data=np.asarray(signals,dtype=np.float32))
        f.create_dataset("Data.SamplingRate",data=np.asarray([fs]))
        f.create_dataset("Data.Delay",data=np.zeros((1,2)))
    outfile=tmp_path/"synthetic-evidence.json"
    run=subprocess.run([sys.executable,str(script),"evaluate","--sofa",str(path),
                        "--output",str(outfile),"--skip-original-md5"],
                       capture_output=True,text=True,timeout=90)
    assert run.returncode==0,run.stdout+"\n"+run.stderr
    e=json.loads(outfile.read_text())
    assert e["synthetic_or_unverified_source"]
    assert e["experiment"]["science_adoption"]=="NOT_ADOPTED"
    assert e["experiment"]["final_evaluated_queries"]>0
    check=subprocess.run([sys.executable,str(auditor),"--evidence",str(outfile)],
                         capture_output=True,text=True,timeout=30)
    assert check.returncode==0,check.stdout+"\n"+check.stderr
    rerun=subprocess.run([sys.executable,str(script),"evaluate","--sofa",str(path),
                         "--output",str(outfile),"--skip-original-md5"],
                        capture_output=True,text=True,timeout=30)
    assert rerun.returncode!=0 and "exists" in rerun.stderr
