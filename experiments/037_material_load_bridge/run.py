"""EM-1 experiment 037: effective material -> fixed geometry -> acoustic load -> glottal flow.

Research only. Snapshot is frozen per simulation; this is not moving-wall FSI,
anatomical tongue tissue, self-oscillation, voiced output, or a material editor.
Stacked on SFI-3 Draft PR #84; no predecessor sources modified.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from types import ModuleType

import numpy as np

HERE=Path(__file__).resolve().parent
EXP=HERE.parent
MATERIAL_RUN=EXP/"021_material_conditioned_multimode_transient"/"run.py"
MATERIAL_GIT_BLOB="9b19f9e9de9bcc60babc3661a27d14278cccd2d6"
RESEARCH_SFI3_HEAD="7ab18f25f53bc5f81bcdf5e7697fd11981abe6dd"
RATE=48000
STEPS=1440
DURATION_S=STEPS/RATE
SAMPLE_DT=1.0/RATE
DRIVE_PA=800.0
APERTURE_M2=3.0e-5
TSTAR_S=.120
SUBDIVISIONS=4


def git_blob(path: Path) -> str:
    payload=path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\\0".encode("ascii").replace(b"\\0",b"\x00")+payload).hexdigest()


def load_experiment(name: str,path: Path) -> ModuleType:
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Missing pinned experiment")
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


if git_blob(MATERIAL_RUN)!=MATERIAL_GIT_BLOB:
    raise RuntimeError("Experiment021 scientific input changed: frozen git blob mismatch")

EXP21=load_experiment("morpho_exp021_for_em1",MATERIAL_RUN)
COUPLED=load_experiment("morpho_exp033_for_em1",
                        EXP/"033_glottal_tract_coupling"/"coupled.py")


def realized_body(material: str):
    if material not in EXP21.MATERIALS:
        raise ValueError("unpreregistered material")
    k=EXP21._material_stiffness(EXP21.MATERIALS[material])
    equilibrium=EXP21._solve_equilibrium_ratios(k)
    modal=EXP21.ModalCriticallyDampedDynamics(
        EXP21._material_hessian(k),EXP21.OMEGA_PER_S)
    state, command=EXP21._vector_state_at_time(
        modal,equilibrium_ratios=equilibrium,
        duration_s=EXP21.PRIMARY_DURATION_S,time_s=TSTAR_S)
    physical=EXP21._geometry_from_ratios(EXP21._geometry(),state.ratios)
    ratios=np.asarray(state.ratios,dtype=np.float64)
    areas=np.asarray([s.area_m2 for s in physical.sections])
    lengths=np.asarray([s.length_m for s in physical.sections])
    if (ratios.shape!=(10,) or np.any(~np.isfinite(ratios))
        or np.any(ratios<=0) or np.any(areas<=0)
        or np.any(~np.isfinite(areas))
        or not np.allclose(lengths,.017,rtol=0,atol=1e-15)):
        raise RuntimeError("INVALID_PREPARED_GEOMETRY")
    return physical,ratios,command


def simulate(physical, *, feedback: bool) -> list[dict[str,float]]:
    # No material label is passed to the physics solver. It sees only physical
    # geometry resulting from an independently realized material condition.
    geo=COUPLED.Geometry.from_tract1d(physical)
    tract=COUPLED.PassiveTract(
        geometry=geo,subdivisions=SUBDIVISIONS,dt_s=SAMPLE_DT,
        outlet_resistance_pa_s_m3=geo.characteristic_outlet_impedance)
    solver=COUPLED.StrongCoupling(tract,feedback=feedback)
    rows=[]
    for n in range(1,STEPS+1):
        result=solver.step(area_m2=APERTURE_M2,subglottal_pressure_pa=DRIVE_PA)
        rows.append({"time_s":n/RATE,"glottal_aperture_m2":APERTURE_M2,
                     "subglottal_pressure_pa":DRIVE_PA,**asdict(result)})
    return rows


def compare(a: list[dict[str,float]], b: list[dict[str,float]],
            name: str) -> float:
    xa=np.asarray([row[name] for row in a])
    xb=np.asarray([row[name] for row in b])
    reference=float(np.linalg.norm(xa))
    if reference<=0:
        raise RuntimeError("invalid reference")
    return float(np.linalg.norm(xb-xa)/reference)


def field_bytes(rows: list[dict[str,float]], name: str) -> bytes:
    return np.asarray([r[name] for r in rows],dtype="<f8").tobytes()


def energy_gate(rows: list[dict[str,float]]) -> tuple[float,bool]:
    residual=sum(abs(row["energy_residual_j"]) for row in rows)
    supplied=sum(abs(row["pressure_drive_work_j"]) for row in rows)
    ratio=residual/max(supplied,1e-30)
    nonnegative=all(row["glottal_linear_loss_j"]>=-1e-14
                    and row["glottal_nonlinear_loss_j"]>=-1e-14
                    and row["outlet_loss_j"]>=-1e-14 for row in rows)
    return float(ratio),bool(nonnegative and math.isfinite(ratio) and ratio<1e-10)


def write_csv(path: Path, rows: list[dict[str,float]]) -> None:
    with path.open("w",newline="",encoding="utf-8") as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(output_dir: Path) -> dict[str,object]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError("Refuse stale successful evidence in nonempty output")
    output_dir.mkdir(parents=True,exist_ok=True)
    bodies={m:realized_body(m) for m in ("baseline","stiff")}
    original,stiff=bodies["baseline"],bodies["stiff"]
    ratios0,ratios1=original[1],stiff[1]
    material_delta=float(np.linalg.norm(ratios1-ratios0)/
                         np.linalg.norm(ratios0))
    shape0=np.array([s.area_m2 for s in original[0].sections])
    shape1=np.array([s.area_m2 for s in stiff[0].sections])
    conditions={}
    for material, (physical,ratios,_) in bodies.items():
        for feedback in (False,True):
            key=f"{material}_{'C1' if feedback else 'C0'}"
            conditions[key]=simulate(physical,feedback=feedback)
            write_csv(output_dir/f"{key}_trace.csv",conditions[key])
    # Same-geometry/different-label negative control. Material type never
    # enters the acoustic solver after physical geometry is constructed.
    duplicate=simulate(original[0],feedback=True)
    write_csv(output_dir/"label_only_same_geometry_C1_trace.csv",duplicate)
    a0,b0=conditions["baseline_C0"],conditions["stiff_C0"]
    a1,b1=conditions["baseline_C1"],conditions["stiff_C1"]
    feedback_flow=compare(a1,b1,"flow_m3_s")
    feedback_pressure=compare(a1,b1,"inlet_pressure_mid_pa")
    flow_early=max(abs(x["flow_m3_s"]-y["flow_m3_s"])
                   for x,y in zip(a1,b1) if x["time_s"]<=.00025+1e-12)
    baseline_energy,pass0=energy_gate(a1)
    stiff_energy,pass1=energy_gate(b1)
    fields=("flow_m3_s","inlet_pressure_mid_pa","total_energy_j")
    checks={
        "material_provenance":bool(material_delta>1e-6 and
            np.all(shape0>0) and np.all(shape1>0) and
            np.any(shape0!=shape1) and original[2]==stiff[2]),
        "open_loop_flow_null":field_bytes(a0,"flow_m3_s")==field_bytes(b0,"flow_m3_s"),
        "same_geometry_different_label_null":all(
            field_bytes(a1,n)==field_bytes(duplicate,n) for n in fields),
        "feedback_causal_effect":bool(feedback_flow>1e-7 and
            feedback_pressure>1e-7 and flow_early<=1e-7),
        "passive_energy":bool(pass0 and pass1),
        "numeric_stability":all(
            all(math.isfinite(v) for row in rows for v in row.values())
            for rows in conditions.values())
    }
    def digest(rows):
        return hashlib.sha256(
            json.dumps(rows,sort_keys=True,separators=(",",":"),
                       allow_nan=False).encode("utf-8")).hexdigest()
    trace_hashes={n:digest(rows) for n,rows in conditions.items()}
    trace_hashes["same_geometry_null"]=digest(duplicate)
    data={
       "experiment":"EM-1-exp037",
       "decision":"SUPPORT_REDUCED_MATERIAL_TO_LOAD_FEEDBACK"
                 if all(checks.values()) else "NUMERICALLY_UNRESOLVED",
       "checks":checks,
       "metrics":{
           "relative_material_ratio_difference":material_delta,
           "relative_acoustic_inlet_pressure_difference_C1":feedback_pressure,
           "relative_source_flow_difference_C1":feedback_flow,
           "early_source_flow_max_abs_difference_m3_s":float(flow_early),
           "energy_residual_to_abs_input_work_C1":{
                "baseline":baseline_energy,"stiff":stiff_energy},
           "area_vectors_m2":{"baseline":shape0.tolist(),"stiff":shape1.tolist()},
           "ratio_vectors":{"baseline":ratios0.tolist(),"stiff":ratios1.tolist()},
           "trace_sha256":trace_hashes
       },
       "frozen_controls":{
           "relative_stiffness":{"baseline":1,"stiff":4},"stiff_index":5,
           "material_units":"dimensionless reduced model, not anatomical Pa",
           "task_duration_s":.12,"snapshot_s":TSTAR_S,
           "glottal_aperture_m2":APERTURE_M2,"p_sub_pa":DRIVE_PA,
           "sample_rate_hz":RATE,"acoustic_samples":STEPS,
           "subdivisions":SUBDIVISIONS,
           "material_experiment_git_blob":MATERIAL_GIT_BLOB,
           "sfi3_pinned_parent_sha":RESEARCH_SFI3_HEAD,
           "acoustic_tract_policy":"stationary separately per body snapshot",
       },
       "claim_limit":"reduced effective-stiffness effect reaches fixed 1D acoustic "
                     "load and prescribed-open-valve feedback only; no moving "
                     "wall energy, tissue FEM, speech, human/ASMR sound"
    }
    (output_dir/"summary.json").write_text(
        json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return data


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    result=run(a.output_dir)
    print(json.dumps({"decision":result["decision"],"checks":result["checks"],
        "metrics":{k:v for k,v in result["metrics"].items()
                   if k not in ("trace_sha256","area_vectors_m2","ratio_vectors")}},
        indent=2))
    if result["decision"]!="SUPPORT_REDUCED_MATERIAL_TO_LOAD_FEEDBACK":
        raise SystemExit(1)


if __name__=="__main__":
    main()
