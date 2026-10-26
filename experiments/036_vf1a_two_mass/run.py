"""VF-1A experiment: explicit science receipt, not a voice renderer."""
from __future__ import annotations
import argparse
import csv
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from two_mass import make_pilot, Tissue

ROOT=Path(__file__).resolve().parents[2]
VERSION="vf1a-two-mass-power-port-research/v1"
FILES=("experiments/032_passive_time_domain_tract/waveguide.py",
       "experiments/033_glottal_tract_coupling/coupled.py",
       "experiments/036_vf1a_two_mass/two_mass.py",
       "experiments/036_vf1a_two_mass/test_two_mass.py",
       "experiments/036_vf1a_two_mass/run.py",
       ".github/workflows/vf1a-two-mass.yml",
       "docs/research/vf1/GATE_A.md",
       "experiments/036_vf1a_two_mass/wolfram/independent_oracle.wl",
       "experiments/036_vf1a_two_mass/wolfram/oracle.json")


def provenance() -> dict:
    paths={x:sha256((ROOT/x).read_bytes()).hexdigest() for x in FILES}
    def git(*args):
        return subprocess.run(["git",*args],cwd=ROOT,check=True,
                              capture_output=True,text=True,timeout=8).stdout.strip()
    head=git("rev-parse","HEAD")
    tree=git("rev-parse","HEAD^{tree}")
    commit=git("cat-file","-p","HEAD")
    parents=[x[7:] for x in commit.splitlines() if x.startswith("parent ")]
    clean=not git("status","--porcelain=v1","--untracked-files=no")
    valid=(len(head)==40 and len(tree)==40 and clean and
           (not os.environ.get("GITHUB_SHA") or os.environ["GITHUB_SHA"]==head)
           and all(len(x)==40 for x in parents))
    return {"checkout":head,"tree":tree,"parents":parents,
            "tracked_clean":clean,"source_hashes_sha256":paths,"verified":valid}


def one_case(outdir: Path, name: str, shape: str, drive: float,
             stiffness_scale:float=1.0)->dict:
    sim=make_pilot(pressure_shape=shape,stiffness_scale=stiffness_scale)
    steps=int(round(0.06/sim.dt))
    path=outdir/(name+".csv")
    x_history=[]
    q_history=[]
    e_history=[]
    max_e=0.
    max_r=0.
    positive_errors=0
    source_total=loss_total=0.
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(("t_s","x1_m","x2_m","v1_m_s","v2_m_s",
                    "A_mid_m2","q_m3_s","Uin_mid_m3_s","p_mid_Pa",
                    "Uout_mid_m3_s","Etissue_J","Eflow_J","Etract_J",
                    "Psub_work_J","Rflow_loss_J","Bflow_loss_J",
                    "damping_loss_J","outlet_loss_J",
                    "tissue_energy_err_J","valve_energy_err_J",
                    "tract_energy_err_J","total_energy_err_J"))
        for k in range(steps):
            r=sim.step(subglottal_pressure_pa=drive)
            w.writerow((r.time_s,*r.x_m,*r.v_m_s,r.area_m2,
                        r.flow_valve_m3_s,r.flow_tract_mid_m3_s,
                        r.pressure_mid_pa,r.outlet_flow_mid_m3_s,
                        r.stored_tissue_j,r.stored_flow_j,r.stored_tract_j,
                        r.source_work_j,r.linear_flow_loss_j,r.nonlinear_flow_loss_j,
                        r.tissue_damping_loss_j,r.outlet_loss_j,
                        r.tissue_energy_residual_j,r.flow_energy_residual_j,
                        r.tract_energy_residual_j,r.total_energy_residual_j))
            x_history.append(r.x_m[0])
            q_history.append(r.flow_valve_m3_s)
            total_e=r.stored_tissue_j+r.stored_flow_j+r.stored_tract_j
            e_history.append(total_e)
            max_e=max(max_e,abs(r.total_energy_residual_j))
            max_r=max(max_r,abs(r.valve_equation_residual_pa))
            if drive==0 and len(e_history)>1 and total_e>e_history[-2]+1e-12:
                positive_errors+=1
            source_total+=r.source_work_j
            loss_total+=(r.linear_flow_loss_j+r.nonlinear_flow_loss_j+
                         r.tissue_damping_loss_j+r.outlet_loss_j)
    x=np.array(x_history,dtype=np.float64)
    q=np.array(q_history,dtype=np.float64)
    last=x[int(0.04/sim.dt):]
    early=x[int(0.02/sim.dt):int(0.04/sim.dt)]
    rms=lambda xs:float(np.sqrt(np.mean((xs-np.mean(xs))**2)))
    tail_rms=rms(last)
    mid_rms=rms(early)
    return {"condition":name,"shape":shape,"Psub_pa":drive,
            "stiffness_scale":stiffness_scale,
            "trace_sha256":sha256(path.read_bytes()).hexdigest(),
            "sample_count":steps,"dt_s":sim.dt,
            "max_total_energy_residual_j":max_e,
            "max_valve_equation_residual_pa":max_r,
            "zero_drive_positive_energy_steps":positive_errors,
            "source_work_total_j":source_total,
            "modeled_losses_total_j":loss_total,
            "final_total_energy_j":e_history[-1],
            "x1_mean_last_20ms_m":float(np.mean(last)),
            "x1_rms_deviation_20_40ms_m":mid_rms,
            "x1_rms_deviation_40_60ms_m":tail_rms,
            "tail_to_middle_rms_ratio":tail_rms/max(mid_rms,1e-30),
            "q_mean_last_20ms_m3_s":float(np.mean(q[int(0.04/sim.dt):])),
            "q_rms_last_20ms_m3_s":rms(q[int(0.04/sim.dt):]),
            "max_absolute_x1_m":float(np.max(np.abs(x))),
            "max_absolute_q_m3_s":float(np.max(np.abs(q))),
            "periodicity_verdict":"INDETERMINATE_60MS_NOT_LONG_ENOUGH_FOR_SUSTAINED_SELF_OSCILLATION_CLAIM"
            }


def run(outdir:Path)->dict:
    outdir.mkdir(parents=True,exist_ok=True)
    prov=provenance()
    results={}
    for name,shape,drive,k in (
        ("zero_uniform","uniform",0.,1.),
        ("zero_constricted","constricted",0.,1.),
        ("drive_uniform","uniform",800.,1.),
        ("drive_constricted","constricted",800.,1.),
        ("drive_stiffness_plus_10pct","uniform",800.,1.1),
    ):
        results[name]=one_case(outdir,name,shape,drive,k)
    a=np.genfromtxt(outdir/"drive_uniform.csv",delimiter=",",names=True)
    b=np.genfromtxt(outdir/"drive_constricted.csv",delimiter=",",names=True)
    dx=float(np.sqrt(np.mean((a["x1_m"]-b["x1_m"])**2)))
    dq=float(np.sqrt(np.mean((a["q_m3_s"]-b["q_m3_s"])**2)))
    # Report observed values; do not manufacture a future loudness/pitch gain.
    numeric_ok=(prov["verified"] and
        all(v["max_total_energy_residual_j"]<=1e-10 for v in results.values())
        and all(v["max_valve_equation_residual_pa"]<1e-4 for v in results.values())
        and all(v["zero_drive_positive_energy_steps"]==0 for v in results.values()
                if v["Psub_pa"]==0))
    return {"schema":VERSION,"research":"VF1_A_GENERIC_COMPLIANT_APERTURE",
            "provenance":prov,"simulator":"pinned SFI-3 / SFI-2 1D tract",
            "model":"two mass + pressure-compliant volume + nonlinear Bernoulli resistance",
            "claims_excluded":["actual human vocal fold model","contact/closure",
                               "receiver audio","sustained self-excitation verified",
                               "voice naturalness","production graph ABI"],
            "causal_body_intervention":{"upstream_x1_rms_difference_m":dx,
                                        "upstream_q_rms_difference_m3_s":dq,
                                        "observed":dx>1e-12 and dq>1e-12},
            "cases":results,
            "g0_g1_research_numerics":"PASS" if numeric_ok else "NUMERICALLY_UNRESOLVED",
            "g2":"INDETERMINATE_PHYSIOLOGY",
            "g3":"SUSTAINED_SELF_OSCILLATION_NOT_ESTABLISHED",
            "g4":"VOICE_NO_GO_UNCHANGED",
            "review":"AWAITING_INDEPENDENT_EXACT_HEAD_AUDIT",
            "verdict":"RESEARCH_NUMERICAL_PASS_NOT_A_PHONATOR" if numeric_ok else
                      "NUMERICALLY_UNRESOLVED"}


def main()->None:
    cli=argparse.ArgumentParser()
    cli.add_argument("--output-dir",type=Path,required=True)
    target=cli.parse_args().output_dir
    try:
        report=run(target)
    except Exception as exc:
        report={"schema":VERSION,"verdict":"NUMERICALLY_UNRESOLVED",
                "failure_type":type(exc).__name__,"failure":str(exc),
                "g2":"INDETERMINATE_PHYSIOLOGY","g4":"VOICE_NO_GO_UNCHANGED"}
    target.mkdir(parents=True,exist_ok=True)
    (target/"vf1a_receipt.json").write_text(
        json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("VF1_A_VERDICT",report["verdict"])
    if "causal_body_intervention" in report:
        print("VF1_A_BODY_INTERVENTION",json.dumps(report["causal_body_intervention"],sort_keys=True))
        print("VF1_A_CASES",json.dumps({
            k:{"tail_ratio":v["tail_to_middle_rms_ratio"],
               "max_Eerr_J":v["max_total_energy_residual_j"],
               "x_rms_tail_m":v["x1_rms_deviation_40_60ms_m"],
               "q_rms_tail_m3_s":v["q_rms_last_20ms_m3_s"]}
            for k,v in report["cases"].items()},sort_keys=True))
    if report["verdict"] != "RESEARCH_NUMERICAL_PASS_NOT_A_PHONATOR":
        raise SystemExit(1)


if __name__=="__main__":
    main()
