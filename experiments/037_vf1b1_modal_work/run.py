"""VF-1B1 preregistered 0.5s modal work study of *unchanged* VF-1A.

This runs a physically symmetric, generic aperture and measures mechanical
modal budgets. NOT a biological phonator, waveform or sound-quality test.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/"experiments/036_vf1a_two_mass"))
from two_mass import make_pilot
from modal import observe_step, independent_work_identity, coordinates, midpoint_transition, energy

VERSION="vf1b1-modal-phase-work-research/v1"
FILES=(
 "experiments/036_vf1a_two_mass/two_mass.py",
 "experiments/037_vf1b1_modal_work/modal.py",
 "experiments/037_vf1b1_modal_work/run.py",
 "experiments/037_vf1b1_modal_work/test_modal.py",
 ".github/workflows/vf1b1-modal-work.yml",
 "docs/research/vf1b/SYSTEM.md",
 "docs/research/vf1b/DATA.md",
 "docs/research/vf1b/EXPERIMENT.md",
)


def evidence_provenance() -> dict:
    def git(*args):
        return subprocess.check_output(["git",*args],cwd=ROOT,text=True,timeout=10).strip()
    head=git("rev-parse","HEAD")
    return {
        "exact_checkout":head,
        "tracked_clean":git("status","--porcelain=v1","--untracked-files=no")=="",
        "files_sha256":{f:sha256((ROOT/f).read_bytes()).hexdigest() for f in FILES},
        "parent_stacked_vf1a":"2b33bc69835170639fb9127c01dab7b523eff4f3",
    }


def test_status(path: Path|None) -> dict:
    if path is None or not path.is_file():
        return {"eligible":False,"reason":"MISSING_TEST_RECEIPT"}
    raw=path.read_bytes()
    try:
        a=json.loads(raw)
        eligible=(isinstance(a,dict)
                  and a.get("schema")=="vf1b1.independent-pytest.v1"
                  and a.get("passed") is True
                  and type(a.get("exit_code")) is int and a["exit_code"]==0)
    except (ValueError,UnicodeError):
        eligible=False
    return {"eligible":bool(eligible),
            "reason":"PASS" if eligible else "FAILED_OR_MALFORMED_TEST_RECEIPT",
            "sha256":sha256(raw).hexdigest()}


def case(outdir:Path, name:str, drive_pa:float, shape:str, rate:int)->dict:
    sim=make_pilot(pressure_shape=shape,sample_rate_hz=rate)
    duration=0.5
    n=int(round(duration*rate))
    state=np.empty((n,13),dtype=np.float64)
    # columns: time, plus_x, minus_x, plus_v, minus_v,
    # Es, Ea, full source work, full tissue damping, anti analytic
    # position error [m], anti velocity error [m/s], inlet p, valve flow.
    cum_work=np.zeros(2)
    cum_loss=np.zeros(2)
    maxima=np.zeros(5)
    status="SUCCESS"
    error=None
    recorded=0
    initial_energy=float(sum(sim.energy()))
    initial_modal_energy=energy(sim.x,sim.v,sim.tissue)
    predicted_am=np.array((0.5**0.5*(sim.x[0]-sim.x[1]),
                           0.5**0.5*(sim.v[0]-sim.v[1])))
    midpoint=midpoint_transition(sim.tissue,sim.dt)
    max_analytic_position_error_m=0.
    max_analytic_velocity_error_m_s=0.
    try:
        for k in range(n):
            x0=sim.x.copy()
            v0=sim.v.copy()
            out=sim.step(subglottal_pressure_pa=drive_pa)
            o=observe_step(sim.tissue,sim.dt,x0,v0,out)
            w=independent_work_identity(sim.tissue,sim.dt,x0,v0,out)
            predicted_am=midpoint@predicted_am
            max_analytic_position_error_m=max(
                max_analytic_position_error_m,
                abs(predicted_am[0]-o.coordinate_after_m[1]))
            max_analytic_velocity_error_m_s=max(
                max_analytic_velocity_error_m_s,
                abs(predicted_am[1]-o.velocity_after_m_s[1]))
            cum_work+=np.asarray(o.pressure_work_j)
            cum_loss+=np.asarray(o.damping_loss_j)
            maxima=np.maximum(maxima, np.abs((
                o.residual_j[0],o.residual_j[1],
                w["full_identity_residual_j"],
                o.antisym_midpoint_position_error_m,
                o.antisym_midpoint_velocity_error_m_s)))
            state[k]=(
                out.time_s,*o.coordinate_after_m,*o.velocity_after_m_s,
                *o.energy_after_j,w["full_pressure_work_j"],
                w["full_damping_loss_j"],
                o.antisym_midpoint_position_error_m,
                o.antisym_midpoint_velocity_error_m_s,
                out.pressure_mid_pa,out.flow_valve_m3_s)
            recorded=k+1
    except Exception as exc:
        status="NUMERICALLY_UNRESOLVED"
        error={"type":type(exc).__name__,"message":str(exc),"at_tick":recorded}
    # Preserve partial samples even on failure. No success guessed from traces.
    path=outdir/(name+".npz")
    np.savez_compressed(path,trace=state[:recorded],
                        column_names=np.asarray((
                         "t_s","x_plus_m","x_minus_m","v_plus_m_s","v_minus_m_s",
                         "E_plus_j","E_minus_j","full_work_j_step",
                         "full_damping_j_step","oracle_position_error_m",
                         "oracle_velocity_error_m_s",
                         "inlet_pressure_pa","q_valve_m3_s")))
    if recorded:
        full=state[:recorded]
        def rms(a):
            return float(np.sqrt(np.mean((a-np.mean(a))**2)))
        windows=[
            {"start_s":lo,"end_s":hi,
             "plus_rms_deviation_m":rms(full[(full[:,0]>lo)&(full[:,0]<=hi),1]),
             "minus_rms_deviation_m":rms(full[(full[:,0]>lo)&(full[:,0]<=hi),2])}
            for lo,hi in ((0.10,0.20),(0.20,0.30),(0.30,0.40),(0.40,0.50))
            if (full[:,0]>lo).sum() and (full[:,0]<=hi).sum()
        ]
    else:
        windows=[]
    return {"name":name,"status":status,"error":error,
            "n_requested":n,"n_recorded":recorded,"dt_s":sim.dt,
            "drive_pa":drive_pa,"shape":shape,"duration_s":duration,
            "trace_sha256":sha256(path.read_bytes()).hexdigest(),
            "trace_columns":"see NPZ column_names (physical SI units)",
            "initial_energy_all_subsystems_j":initial_energy,
            "modal_work_total_j":cum_work.tolist(),
            "modal_damping_total_j":cum_loss.tolist(),
            "max_modal_energy_residual_j":maxima[:2].tolist(),
            "max_full_tissue_energy_residual_j":float(maxima[2]),
            "max_step_oracle_position_error_m":float(maxima[3]),
            "max_step_oracle_velocity_error_m_s":float(maxima[4]),
            "max_trajectory_oracle_position_error_m":float(max_analytic_position_error_m),
            "max_trajectory_oracle_velocity_error_m_s":float(max_analytic_velocity_error_m_s),
            "initial_modal_energies_j":initial_modal_energy.tolist(),
            "final_modal_energies_j":state[recorded-1,5:7].tolist() if recorded else None,
            "modal_energy_change_j":(state[recorded-1,5:7]-initial_modal_energy).tolist() if recorded else None,
            "modal_work_minus_damping_j":(cum_work-cum_loss).tolist(),
            "windows":windows,
            "self_oscillation_verdict":"NOT_ESTABLISHED_NO_PER_CYCLE_ONSET_TEST"}


def run(outdir:Path,tests:Path|None) -> dict:
    outdir.mkdir(parents=True,exist_ok=True)
    evidence=test_status(tests)
    provenance=evidence_provenance()
    results={}
    for name,drive,shape,rate in (
        ("uniform_800pa_24k",800.,"uniform",24000),
        ("uniform_800pa_48k",800.,"uniform",48000),
        ("uniform_800pa_96k",800.,"uniform",96000),
        ("constricted_800pa_48k",800.,"constricted",48000),
        ("zero_uniform_48k",0.,"uniform",48000),
    ):
        results[name]=case(outdir,name,drive,shape,rate)

    numeric_ok=(evidence["eligible"] and provenance["tracked_clean"]
        and all(v["status"]=="SUCCESS" and v["n_recorded"]==v["n_requested"]
                and max(v["max_modal_energy_residual_j"])<1e-10
                and v["max_full_tissue_energy_residual_j"]<1e-10
                and v["max_trajectory_oracle_position_error_m"]<1e-9
                and v["max_trajectory_oracle_velocity_error_m_s"]<1e-9
                and abs(v["modal_work_total_j"][1])<1e-15
                for v in results.values()))
    # A comparative convergence diagnostic on the SAME physical 0.5s horizon.
    a,b,c=(results[f"uniform_800pa_{rate}k"] for rate in (24,48,96))
    # Observed convergence trend is diagnostic only: no post hoc science
    # threshold added after seeing measurements from the first failed CI.
    diffs=[abs(b["modal_work_total_j"][0]-a["modal_work_total_j"][0]),
           abs(c["modal_work_total_j"][0]-b["modal_work_total_j"][0])]
    convergence_note={
        "quantity":"symmetric cumulative pressure work at identical 0.5s horizon",
        "absolute_diff_24k_48k_j":diffs[0],
        "absolute_diff_48k_96k_j":diffs[1],
        "refinement_ratio_observed":diffs[1]/diffs[0] if diffs[0] else None,
        "gate":"DIAGNOSTIC_ONLY_NO_POSTHOC_PASS_CUTOFF",
    }
    return {"schema":VERSION,"provenance":provenance,
            "independent_tests":evidence,"cases":results,
            "refinement_note":convergence_note,
            "g0_g1":"NUMERICALLY_CONSISTENT_WITH_SYMMETRIC_MODAL_MODEL"
                    if numeric_ok else "NUMERICALLY_UNRESOLVED",
            "g2":"BIOPHYSICAL_MODEL_INDETERMINATE",
            "g3":"SUSTAINED_SELF_OSCILLATION_NOT_ESTABLISHED",
            "g4":"CREATOR_AUDIO_NO_GO_UNCHANGED",
            "excluded":["symmetric-mode stability certified","voice naturalness",
                        "human vocal fold","audible Take","receiver audio",
                        "intraglottal flow separation law","public API"],
            "verdict":"MODAL_WORK_NUMERICAL_PASS_NOT_A_PHONATOR"
                      if numeric_ok else "NUMERICALLY_UNRESOLVED"}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--test-status-file",type=Path)
    cfg=ap.parse_args()
    cfg.output_dir.mkdir(parents=True,exist_ok=True)
    try:
        report=run(cfg.output_dir,cfg.test_status_file)
    except Exception as exc:
        report={"schema":VERSION,"verdict":"NUMERICALLY_UNRESOLVED",
                "failure":{"type":type(exc).__name__,"message":str(exc)},
                "g2":"BIOPHYSICAL_MODEL_INDETERMINATE",
                "g3":"SUSTAINED_SELF_OSCILLATION_NOT_ESTABLISHED",
                "g4":"CREATOR_AUDIO_NO_GO_UNCHANGED"}
    (cfg.output_dir/"vf1b1_receipt.json").write_text(
         json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("VF1B1_VERDICT",report["verdict"])
    if "cases" in report:
        for name,r in report["cases"].items():
            print("VF1B1_CASE",name, json.dumps({
                "status":r["status"],
                "modal_work_j":r["modal_work_total_j"],
                "modal_damping_j":r["modal_damping_total_j"],
                "max_oracle_error_m":r["max_trajectory_oracle_position_error_m"],
                "max_oracle_error_m_s":r["max_trajectory_oracle_velocity_error_m_s"],
                "windows":r["windows"]},sort_keys=True))
    if report["verdict"]!="MODAL_WORK_NUMERICAL_PASS_NOT_A_PHONATOR":
        raise SystemExit(1)


if __name__=="__main__":
    main()
