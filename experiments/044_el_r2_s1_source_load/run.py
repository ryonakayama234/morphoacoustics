"""Reproducible Gate-B 18-row numerical study. No human-ear claims."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

from audit import audit_row, git_blob_digest, load_oracle, verify_wolfram_source
from listener_port import Fixture, ResearchBoundaryError, solve

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent


def _pair(z: complex | None):
    return None if z is None else [z.real,z.imag]


def _record(f: Fixture, o, audit):
    return {
        "fixture": {"area_m2":f.area_m2,"length_m":f.length_m,"frequency_hz":f.frequency_hz,"source_pressure_pa":_pair(f.source_pressure_pa),"source_impedance_pa_s_m3":f.source_impedance_pa_s_m3,"terminal_impedance_pa_s_m3":f.terminal_impedance_pa_s_m3,"air_density_kg_m3":f.air_density_kg_m3,"sound_speed_m_s":f.sound_speed_m_s},
        "reference_planes": [o.source_reference_plane,o.entrance_plane,o.terminal_plane],
        "phasor":o.phasor,"positive_u":o.positive_u,
        "ports":{"p0_pa":_pair(o.p0_pa),"u0_m3_s":_pair(o.u0_m3_s),"pL_pa":_pair(o.pL_pa),"uL_m3_s":_pair(o.uL_m3_s)},
        "derived":{"zc_pa_s_m3":o.zc_pa_s_m3,"zin_pa_s_m3":_pair(o.zin_pa_s_m3),"gamma_in":_pair(o.gamma_in),"h_drive":_pair(o.h_drive),"h_canal":_pair(o.h_canal),"h_total":_pair(o.h_total)},
        "power_w":{"drive":o.power_drive_w,"entrance":o.power_entrance_w,"terminal":o.power_terminal_w,"source_loss":o.power_source_loss_w,"source_residual":o.source_residual_w,"tube_residual":o.tube_residual_w},
        "boundary_residual":{"source_pa":_pair(o.source_boundary_residual_pa),"termination_pa":_pair(o.termination_boundary_residual_pa),"core_pressure_pa":_pair(o.matrix_pressure_residual_pa),"core_flow_m3_s":_pair(o.matrix_flow_residual_m3_s),"determinant":_pair(o.matrix_determinant_residual)},
        "numerical":{"dimensionless_denominator":_pair(o.dimensionless_denominator),"denominator_discrepancy":_pair(o.dimensionless_denominator_residual)},
        "input_status":o.input_status,"science_verdict":audit.verdict,"failures":list(audit.failures),"oracle_pressure_component_error_pa":audit.max_complex_pressure_error_pa,"oracle_power_error_w":audit.max_power_error_w,
    }


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,help="write a complete research observation JSON file")
    parser.add_argument("--no-pin",action="store_true",help="LOCAL RECONSTRUCTION ONLY; never use for CI / scientific gate")
    args=parser.parse_args()
    oracle=load_oracle(verify_pin=not args.no_pin)
    if not args.no_pin:
        verify_wolfram_source()
    rows=[]
    for row in oracle["rows"]:
        f=Fixture(area_m2=row[0],length_m=row[1],frequency_hz=row[2],source_pressure_pa=complex(oracle["source_pressure_pa"]),source_impedance_pa_s_m3=oracle["source_impedance_pa_s_m3"],terminal_impedance_pa_s_m3=oracle["terminal_impedance_pa_s_m3"])
        try:
            o=solve(f)
        except ResearchBoundaryError as e:
            print(f"Gate B refused {f}: {e}",file=sys.stderr)
            return 2
        rows.append(_record(f,o,audit_row(f,o,row)))
    max_p=max(r["oracle_pressure_component_error_pa"] for r in rows)
    max_power=max(r["oracle_power_error_w"] for r in rows)
    failed=[r for r in rows if r["science_verdict"]!="PASS"]
    payload={
        "schema":"el-r2-s1.gateb.research-observation.v1",
        "science_level":"SYNTHETIC_NUMERICAL_ONLY",
        "source_calibration":"NUMERIC_EQUIVALENT_FIXTURE_NOT_EMPIRICAL",
        "model":"linear_passive_lossless_rigid_uniform_1d",
        "gate_a_head_sha":"489111e19ffa18b21c4c4cadba8ef19f84e11bb4",
        "gate_a_oracle_blob":git_blob_digest((HERE/"wolfram_oracle_18.json").read_bytes()),
        "gate_a_wolfram_source_blob":git_blob_digest((HERE/"wolfram_oracle_18.wl").read_bytes()) if (HERE/"wolfram_oracle_18.wl").exists() else None,
        "core_primitive_sha256":hashlib.sha256((ROOT/"src/morphoacoustics/acoustics/uniform_tube.py").read_bytes()).hexdigest(),
        "runtime":{"python":sys.version.split()[0]},
        "summary":{"frozen_rows":len(rows),"passed":len(rows)-len(failed),"failed":len(failed),"max_pressure_component_error_pa":max_p,"max_power_error_w":max_power,"scientific_verdict":"PASS" if not failed else "FAIL"},
        "rows":rows,
    }
    rendered=json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(rendered,encoding="utf-8")
    print(json.dumps(payload["summary"],sort_keys=True))
    return 0 if not failed else 1


if __name__=="__main__":
    raise SystemExit(main())