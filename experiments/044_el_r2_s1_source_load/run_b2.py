"""Reproduce all B2 24 synthetic rows and report independent-reference errors.

This executable is an observation recorder, not a measured-ear simulator.
The frozen oracle's Git blob SHA is checked in the independent pytest gate.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

from listener_port import Fixture, solve

HERE = Path(__file__).resolve().parent
ORACLE = HERE / "holdout_oracle_24.json"
BLOB_SHA = "0c3476899de4d3cdeaad46816895b8318b43cde0"


def _pair(z: complex) -> list[float]:
    return [float(z.real), float(z.imag)]


def main() -> int:
    original = ORACLE.read_bytes()
    actual_sha = hashlib.sha1(b"blob " + str(len(original)).encode() + b"\0" + original).hexdigest()
    if actual_sha != BLOB_SHA:
        raise ValueError("B2 oracle bytes differ from pinned Git blob SHA")
    ref = json.loads(original)
    rows = []
    maxima = {"complex_pressure_component_pa": 0.0,
              "complex_flow_component_times_zc_pa": 0.0,
              "mean_power_w": 0.0,
              "source_energy_residual_w": 0.0,
              "tube_energy_residual_w": 0.0}
    for v in ref["rows"]:
        f = Fixture(area_m2=v[0],length_m=v[1],frequency_hz=v[2],
                    source_impedance_pa_s_m3=ref["source_impedance_pa_s_m3"],
                    terminal_impedance_pa_s_m3=ref["terminal_impedance_pa_s_m3"])
        o = solve(f)
        predictions = [o.pL_pa, o.p0_pa, o.uL_m3_s, o.u0_m3_s]
        expected = [complex(v[3],v[4]),complex(v[5],v[6]),
                    complex(v[7],v[8]),complex(v[9],v[10])]
        for i,(x,y) in enumerate(zip(predictions,expected)):
            k = "complex_pressure_component_pa" if i < 2 else "complex_flow_component_times_zc_pa"
            scale = 1.0 if i < 2 else o.zc_pa_s_m3
            maxima[k] = max(maxima[k],abs((x.real-y.real)*scale),abs((x.imag-y.imag)*scale))
        powers = [o.power_drive_w,o.power_entrance_w,o.power_terminal_w,o.power_source_loss_w]
        maxima["mean_power_w"] = max(maxima["mean_power_w"],*(abs(x-y) for x,y in zip(powers,v[11:15])))
        maxima["source_energy_residual_w"] = max(maxima["source_energy_residual_w"],abs(o.source_residual_w))
        maxima["tube_energy_residual_w"] = max(maxima["tube_energy_residual_w"],abs(o.tube_residual_w))
        rows.append({"A_m2":v[0],"L_m":v[1],"f_hz":v[2],
                     "p0_pa":_pair(o.p0_pa),"u0_m3_s":_pair(o.u0_m3_s),
                     "pL_pa":_pair(o.pL_pa),"uL_m3_s":_pair(o.uL_m3_s),
                     "H_total":_pair(o.h_total),"H_drive":_pair(o.h_drive),
                     "H_canal":_pair(o.h_canal),
                     "Psource_w":o.power_drive_w,"Pentrance_w":o.power_entrance_w,
                     "Pterminal_w":o.power_terminal_w,"Psource_loss_w":o.power_source_loss_w})
    passed = (len(rows)==24
              and maxima["complex_pressure_component_pa"]<=1e-11
              and maxima["complex_flow_component_times_zc_pa"]<=1e-11
              and maxima["mean_power_w"]<=1e-13
              and maxima["source_energy_residual_w"]<=1e-13
              and maxima["tube_energy_residual_w"]<=1e-13)
    result = {"schema":"el-r2-s1.b2.result24.v1",
              "decision":"NUMERICAL_PASS" if passed else "NUMERICAL_FAIL",
              "scientific_scope":"SYNTHETIC_IDEAL_1D_NOT_REAL_EAR_NOT_ASMR",
              "evidence_context":"GITHUB_ACTIONS" if os.environ.get("GITHUB_ACTIONS")=="true" else "LOCAL_RUN_ONLY",
              "head_sha":os.environ.get("GATEB_HEAD_SHA") or None,
              "oracle_git_blob_sha1":BLOB_SHA,
              "oracle_sha256":hashlib.sha256(original).hexdigest(),
              "cases":len(rows),"maximum_discrepancies":maxima,"rows":rows}
    output = Path(sys.argv[1]) if len(sys.argv)>1 else Path("el-r2-s1-b2-24-observations.json")
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"decision":result["decision"],"cases":len(rows),"max":maxima,"artifact":str(output)}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
