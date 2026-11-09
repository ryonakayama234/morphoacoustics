"""VF-1B2a standalone rigid-glottis science traces and adversarial gate.

No dependence on VF-1A/VF-1B1/FSI or acoustic waveguides. All evidence includes
its own research-only SHA. The far-field loss budget is DEFINED, not solved.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from rigid_glottis import RigidGeometry,solve,RigidResult

SCHEMA="vf1b2a.rigid-proxy.v1"
FILES=(
 "experiments/038_vf1b2a_rigid_glottis/rigid_glottis.py",
 "experiments/038_vf1b2a_rigid_glottis/run.py",
 "experiments/038_vf1b2a_rigid_glottis/test_rigid.py",
 ".github/workflows/vf1b2a-rigid-flow.yml",
 "docs/research/vf1b2a/SYSTEM.md",
 "docs/research/vf1b2a/DATA.md",
 "docs/research/vf1b2a/EXPERIMENT.md",
)


def suite_receipt(path:Path|None)->dict:
    if path is None or not path.is_file():
        return {"eligible":False,"reason":"MISSING_TEST_RECEIPT"}
    b=path.read_bytes()
    try:
        a=json.loads(b)
        passed=(type(a) is dict and a.get("schema")=="vf1b2a.unittest.v1"
                and a.get("passed") is True
                and type(a.get("exit_code")) is int and a["exit_code"]==0)
    except (UnicodeDecodeError,ValueError):
        passed=False
    return {"eligible":passed,"reason":"PASS" if passed else "FAILED_OR_INVALID_TEST_RECEIPT",
            "sha256":hashlib.sha256(b).hexdigest()}


def provenance()->dict:
    def git(*args):
        return subprocess.run(["git",*args],cwd=ROOT,check=True,
            capture_output=True,text=True,timeout=10).stdout.strip()
    sha=git("rev-parse","HEAD")
    return {"checkout_sha":sha,"tree_sha":git("rev-parse","HEAD^{tree}"),
            "tracked_clean":not git("status","--porcelain=v1","--untracked-files=no"),
            "expected_base":"e05e3274ad69bfb9202816049f6661a18ba39ec0",
            "source_hashes_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
                                    for p in FILES},
            "github_sha_matches":not os.getenv("GITHUB_SHA") or os.getenv("GITHUB_SHA")==sha}


def audit_independent(r:RigidResult)->dict:
    """Independently recompute exact formulas, instead of trusting source receipts.

    This is an *algebraic reference for the declared toy closure*, NOT an
    independent experimental flow measurement or an FSI-energy audit.
    """
    geom=r.input_geometry
    a0,al=geom.entry_area_m2,geom.exit_area_m2
    # Piecewise oracle deliberately does not invoke geometric_separation or
    # solve from the model.
    if al<=a0 or al<1.2*a0:
        zref=geom.length_m
        aref=al
    else:
        zref=geom.length_m*(0.2*a0)/(al-a0)
        aref=1.2*a0
    dp=r.p_up_pa-r.p_down_pa
    qref=r.discharge_coefficient*aref*(2*dp/r.rho_kg_m3)**0.5
    errors={"flow_m3_s":abs(r.volume_flow_m3_s-qref),
            "separation_z_m":abs(r.geometric_separation_z_m-zref),
            "separation_area_m2":abs(r.separation_area_m2-aref),
            "power_w":abs(r.reservoir_power_w-dp*qref),
            "loss_w":abs(r.declared_farfield_dissipation_w-dp*qref),
            "bookkeeping_w":abs(r.bookkeeping_residual_w),
            "wall_power_w":abs(r.fixed_wall_power_w),
            "profile_pa":0.,"continuity_m3_s":0.,
            "sample_z_m":0.,"sample_area_m2":0.}
    n=len(r.samples)
    for i,s in enumerate(r.samples):
        z=geom.length_m*i/(n-1)
        area=a0+(al-a0)*i/(n-1)
        attached=z<=zref+1e-15
        pressure=(r.p_down_pa+0.5*r.rho_kg_m3*qref*qref*
                  (1/(aref*aref)-1/(area*area)) if attached else r.p_down_pa)
        errors["profile_pa"]=max(errors["profile_pa"],abs(s.pressure_pa-pressure))
        errors["continuity_m3_s"]=max(errors["continuity_m3_s"],abs(s.flow_m3_s-qref))
        errors["sample_z_m"]=max(errors["sample_z_m"],abs(s.z_m-z))
        errors["sample_area_m2"]=max(errors["sample_area_m2"],abs(s.area_m2-area))
        if s.attached!=attached:
            errors["profile_pa"]=math.inf
    thresholds={"flow_m3_s":max(1e-15,abs(qref)*1e-12),
                "separation_z_m":1e-12,"separation_area_m2":1e-15,
                "power_w":1e-10,"loss_w":1e-10,
                "bookkeeping_w":1e-10,"wall_power_w":1e-10,
                "profile_pa":1e-8,"continuity_m3_s":1e-14,
                "sample_z_m":1e-12,"sample_area_m2":1e-15}
    ok=(n>=3 and all(math.isfinite(v) and v<=thresholds[k] for k,v in errors.items())
        and r.separation_active==(dp>0))
    return {"passed":bool(ok),"max_discrepancies":errors,
            "predeclared_thresholds":thresholds,
            "scope":"ALGEBRAIC_MODEL_CONSISTENCY_ONLY_NOT_INDEPENDENT_BIOPHYSICS"}


def one_case(outdir:Path,name:str,a0:float,al:float,p:float,
             cd:float=0.7,n:int=41)->dict:
    r=solve(RigidGeometry(a0,al),p_up_pa=p,discharge_coefficient=cd,sample_count=n)
    path=outdir/(name+".csv")
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(("z_m","area_m2","pressure_pa","attached",
                         "flow_m3_s"))
        for x in r.samples:
            writer.writerow((x.z_m,x.area_m2,x.pressure_pa,int(x.attached),
                             x.flow_m3_s))
    check=audit_independent(r)
    return {"case_id":name,"status":"PASS_ALGEBRAIC" if check["passed"] else "NUMERICALLY_UNRESOLVED",
            "inputs":{"A_entry_m2":a0,"A_exit_m2":al,"length_m":r.input_geometry.length_m,
                      "p_up_pa":p,"p_down_pa":r.p_down_pa,
                      "rho_kg_m3":r.rho_kg_m3,"Cd":cd,"sample_count":n},
            "flow_m3_s":r.volume_flow_m3_s,"separation_z_m":r.geometric_separation_z_m,
            "separation_area_m2":r.separation_area_m2,
            "separation_active":r.separation_active,
            "p_entry_gauge_pa":r.samples[0].pressure_pa-r.p_down_pa,
            "p_exit_gauge_pa":r.samples[-1].pressure_pa-r.p_down_pa,
            "reservoir_power_w":r.reservoir_power_w,
            "declared_farfield_dissipation_w":r.declared_farfield_dissipation_w,
            "fixed_wall_power_w":r.fixed_wall_power_w,
            "audit":check,"trace_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}


def run(outdir:Path,test_status_file:Path|None)->dict:
    outdir.mkdir(parents=True,exist_ok=True)
    cases={}
    for name,a0,al,p,cd,n in (
        ("parallel_800pa_cd07",3e-5,3e-5,800.,0.7,41),
        ("convergent_800pa_cd07",6e-5,3e-5,800.,0.7,41),
        ("divergent_800pa_cd07",3e-5,6e-5,800.,0.7,41),
        ("parallel_0pa_cd07",3e-5,3e-5,0.,0.7,41),
        ("parallel_400pa_cd07",3e-5,3e-5,400.,0.7,41),
        ("parallel_800pa_cd1",3e-5,3e-5,800.,1.,41),
        ("divergent_800pa_cd07_161",3e-5,6e-5,800.,0.7,161),
    ):
        cases[name]=one_case(outdir,name,a0,al,p,cd,n)
    a=cases["parallel_800pa_cd07"]["flow_m3_s"]
    b=cases["parallel_400pa_cd07"]["flow_m3_s"]
    c=cases["parallel_800pa_cd1"]["flow_m3_s"]
    d=cases["divergent_800pa_cd07"]
    e=cases["divergent_800pa_cd07_161"]
    invariants={"pressure_sqrt_law":abs(b/a-1/math.sqrt(2))<1e-12,
                "Cd_linear_flow_law":abs(c/a-1/0.7)<1e-12,
                "divergent_separation_z_m":abs(d["separation_z_m"]-0.0012)<1e-12,
                "divergent_throat_suction":d["p_entry_gauge_pa"]<0,
                "geometry_refinement_flow":abs(d["flow_m3_s"]-e["flow_m3_s"])<=1e-15,
                "geometry_refinement_separation_z":abs(d["separation_z_m"]-e["separation_z_m"])<=1e-12,
                "no_pressure_no_flow":cases["parallel_0pa_cd07"]["flow_m3_s"]==0}
    tests=suite_receipt(test_status_file)
    prov=provenance()
    numeric_ok=(tests["eligible"] and prov["tracked_clean"] and
                prov["github_sha_matches"] and all(x["status"]=="PASS_ALGEBRAIC" for x in cases.values())
                and all(invariants.values()))
    return {"schema":SCHEMA,"provenance":prov,"independent_test_receipt":tests,
            "cases":cases,"controls":invariants,
            "g0_g1":"NUMERICALLY_CONSISTENT_RIGID_FLOW_PROXY" if numeric_ok
                     else "NUMERICALLY_UNRESOLVED",
            "g2":"INDETERMINATE_NO_INDEPENDENT_NUMERIC_PRESSURE_DATA",
            "g3":"NOT_APPLICABLE_RIGID_NO_TISSUE",
            "g4":"VOICE_NO_GO",
            "limitations":["no moving wall","no acoustic waveguide","no contact",
                "zero pressure recovery assumed","Cd and Asep/Amin not calibrated",
                "no measured pressure tap numerical comparison",
                "farfield power loss defined, not independently resolved",
                "no self-excitation or human phonation validation"],
            "verdict":"RESEARCH_ALGEBRAIC_PASS_NOT_AN_FSI_OR_PHONATOR"
                    if numeric_ok else "NUMERICALLY_UNRESOLVED"}


def main()->None:
    cli=argparse.ArgumentParser()
    cli.add_argument("--output-dir",type=Path,required=True)
    cli.add_argument("--test-status-file",type=Path)
    args=cli.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    try:
        result=run(args.output_dir,args.test_status_file)
    except Exception as e:
        result={"schema":SCHEMA,"verdict":"NUMERICALLY_UNRESOLVED",
                "failure":{"type":type(e).__name__,"message":str(e)},
                "g2":"INDETERMINATE_NO_INDEPENDENT_NUMERIC_PRESSURE_DATA",
                "g3":"NOT_APPLICABLE_RIGID_NO_TISSUE","g4":"VOICE_NO_GO"}
    (args.output_dir/"vf1b2a_receipt.json").write_text(
        json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("VF1B2A_VERDICT",result["verdict"])
    if "cases" in result:
        for name,case in result["cases"].items():
            print("VF1B2A_CASE",name,json.dumps({
              "flow_m3_s":case["flow_m3_s"],"separation_z_m":case["separation_z_m"],
              "p_entry_gauge_pa":case["p_entry_gauge_pa"],
              "wall_power_w":case["fixed_wall_power_w"],
              "audit_pass":case["audit"]["passed"]},sort_keys=True))
        print("VF1B2A_CONTROL",json.dumps(result["controls"],sort_keys=True))
    if result["verdict"]!="RESEARCH_ALGEBRAIC_PASS_NOT_AN_FSI_OR_PHONATOR":
        raise SystemExit(1)

if __name__=="__main__":
    main()
