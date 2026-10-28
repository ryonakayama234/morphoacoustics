"""Gate-B numerical-only tests: frozen independent WL reference + adversarial controls."""
from __future__ import annotations

from dataclasses import replace
from math import cos, pi, sin
from pathlib import Path
import json
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments" / "044_el_r2_s1_source_load"
sys.path.insert(0, str(STUDY))
from audit import COLUMNS, audit_row, load_oracle, verify_wolfram_source
from listener_port import Fixture, ResearchBoundaryError, solve

ORACLE = load_oracle(verify_pin=False)  # local preflight copy; pinned verification tested separately in CI
ROWS=ORACLE["rows"]


def fixture_from(row):
    return Fixture(area_m2=row[0],length_m=row[1],frequency_hz=row[2],
                   source_pressure_pa=complex(ORACLE["source_pressure_pa"]),
                   source_impedance_pa_s_m3=ORACLE["source_impedance_pa_s_m3"],
                   terminal_impedance_pa_s_m3=ORACLE["terminal_impedance_pa_s_m3"])


@pytest.mark.parametrize("row",ROWS,ids=lambda row:f"A{row[0]}-L{row[1]}-f{row[2]}")
def test_frozen_18_complex_and_power_oracle(row):
    f=fixture_from(row)
    o=solve(f)
    check=audit_row(f,o,row)
    assert check.verdict=="PASS", check.failures
    assert check.max_complex_pressure_error_pa <= 1e-11
    assert check.max_power_error_w <= 1e-13


def test_frozen_oracle_metadata_and_exact_rows():
    assert tuple(ORACLE["columns"])==COLUMNS
    assert len(ROWS)==18
    assert len({tuple(r[:3]) for r in ROWS})==18
    assert load_oracle(verify_pin=False)==ORACLE


def test_real_frozen_blob_pins():
    # Local preflight may use a reconstructed fixture. CI must require original bytes.
    assert load_oracle(verify_pin=True)["schema"]=="el-r2-s1.wolfram.scattering.v0"
    assert verify_wolfram_source()=="fa8c2112f36f2b7119d40e8125e4d979ba091eef"


@pytest.mark.parametrize("freq",[1000,3000,7000])
def test_matched_source_length_null_and_phase(freq):
    observations=[]
    for length in (.02,.025,.03):
        f=Fixture(area_m2=3e-5,length_m=length,frequency_hz=freq)
        o=solve(f)
        assert abs(abs(o.h_total)-2/3)<1e-11
        observations.append((length,o.h_total))
    for (l0,h0),(l1,h1) in zip(observations,observations[1:]):
        delta=2*pi*freq*(l1-l0)/343.0
        expected=complex(cos(-delta),sin(-delta))
        assert abs(h1/h0-expected)<1e-11


def test_absolute_load_area_contrast():
    f1=Fixture(3e-5,.025,3000)
    f2=Fixture(6e-5,.025,3000)
    a,b=solve(f1),solve(f2)
    assert abs(abs(a.pL_pa)-2/3)<1e-11
    assert abs(abs(b.pL_pa)-0.4492470594476995)<1e-11
    assert f1.terminal_impedance_pa_s_m3==f2.terminal_impedance_pa_s_m3
    assert f1.source_impedance_pa_s_m3==f2.source_impedance_pa_s_m3
    assert abs(a.h_drive-b.h_drive)>1e-3
    assert abs(a.h_canal-b.h_canal)>1e-3


def test_area_pairs_are_distinct_complex_counterfactuals():
    for length in (.02,.025,.03):
        for freq in (1000,3000,7000):
            a=solve(Fixture(3e-5,length,freq))
            b=solve(Fixture(6e-5,length,freq))
            assert abs(b.pL_pa-a.pL_pa)>1e-4
            assert abs(a.h_total-a.h_drive*a.h_canal)<1e-11
            assert abs(b.h_total-b.h_drive*b.h_canal)<1e-11


@pytest.mark.parametrize("area",[3e-5,6e-5])
def test_ideal_source_limit(area):
    f=Fixture(area,.025,3000,source_impedance_pa_s_m3=0)
    o=solve(f)
    assert abs(o.p0_pa-f.source_pressure_pa)<1e-11
    assert abs(o.u0_m3_s)>0
    assert abs(o.power_drive_w-o.power_terminal_w)<1e-13


def test_normalized_load_control_is_not_primary_absolute_load():
    # *Separate* total-entrance-pressure fixture, realized via ideal source Zs=0.
    two=[]
    for area in (3e-5,6e-5):
        zc=1.21*343/area
        normalized=Fixture(area,.025,3000,source_impedance_pa_s_m3=0,terminal_impedance_pa_s_m3=2*zc)
        two.append(solve(normalized).h_canal)
    assert abs(two[0]-two[1])<1e-11
    fixed=[solve(Fixture(a,.025,3000,source_impedance_pa_s_m3=0)).h_canal for a in (3e-5,6e-5)]
    assert abs(fixed[0]-fixed[1])>1e-3


def test_zero_source_is_valid_but_ratio_is_undefined():
    f=Fixture(3e-5,.02,1000,source_pressure_pa=0j)
    o=solve(f)
    assert (o.p0_pa,o.u0_m3_s,o.pL_pa,o.uL_m3_s)==(0j,0j,0j,0j)
    assert (o.h_drive,o.h_canal,o.h_total,o.zin_pa_s_m3)==(None,None,None,None)
    assert (o.power_drive_w,o.power_entrance_w,o.power_terminal_w,o.power_source_loss_w)==(0,0,0,0)
    assert abs(o.gamma_in)<1
    assert o.undefined_transfer_reason=="zero_source_drive"


@pytest.mark.parametrize("field,value,category",[
    ("length_m",0.0,"INVALID"),("length_m",-1.0,"INVALID"),
    ("area_m2",0,"INVALID"),("air_density_kg_m3",-1,"INVALID"),
    ("sound_speed_m_s",0,"INVALID"),("source_impedance_pa_s_m3",-2,"INVALID"),
    ("terminal_impedance_pa_s_m3",0,"INVALID"),
    ("source_impedance_pa_s_m3",1j,"UNSUPPORTED"),
    ("terminal_impedance_pa_s_m3",1+2j,"UNSUPPORTED"),
    ("frequency_hz",0,"UNSUPPORTED"),("frequency_hz",9000,"UNSUPPORTED"),
    ("length_m",.051,"UNSUPPORTED"),("area_m2",2e-4,"UNSUPPORTED"),
    ("source_pressure_pa",1e8,"UNSUPPORTED"),
    ("area_m2",True,"INVALID"),("frequency_hz",float('nan'),"INVALID"),
    ("length_m",float('inf'),"INVALID"),("source_pressure_pa",1+complex(0,float('nan')),"INVALID"),
    ("terminal_impedance_pa_s_m3",10**10000,"INVALID"),
    ("source_pressure_pa",[1,0],"INVALID"),
    ("frequency_hz","3000 Hz","INVALID"),
],ids=[f"refusal-{i}" for i in range(21)])
def test_typed_refusals(field,value,category):
    with pytest.raises(ResearchBoundaryError) as e:
        solve(replace(Fixture(3e-5,.02,1000),**{field:value}))
    assert e.value.category==category
    assert e.value.field==field


def test_finite_input_numeric_scale_can_be_unresolved():
    # The input is positive/finite, but rho*c*c exceeds float64 range.
    with pytest.raises(ResearchBoundaryError) as e:
        solve(Fixture(3e-5,.02,1000,air_density_kg_m3=1e308,sound_speed_m_s=1e308))
    assert e.value.category=="NUMERICALLY_UNRESOLVED"


def test_invalid_fixture_is_not_a_motor_infeasibility():
    with pytest.raises(ResearchBoundaryError) as e:
        solve({"area_m2":3e-5})
    assert e.value.category=="INVALID"
    assert "INFEASIBLE" not in str(e.value)


def test_mutations_are_actually_caught_by_named_invariants():
    f=fixture_from(ROWS[4])
    o=solve(f)
    assert audit_row(f,o,ROWS[4]).verdict=="PASS"
    mutants={
        "phasor_flip":replace(o,pL_pa=o.pL_pa.conjugate()),
        "pressure_volume_swap":replace(o,pL_pa=o.uL_m3_s),
        "reverse_flow":replace(o,u0_m3_s=-o.u0_m3_s, source_boundary_residual_pa=f.source_pressure_pa-o.p0_pa+f.source_impedance_pa_s_m3*o.u0_m3_s),
        "p0_equal_ps":replace(o,p0_pa=f.source_pressure_pa),
        "absolute_load_changed":solve(replace(f,terminal_impedance_pa_s_m3=f.terminal_impedance_pa_s_m3/2)),
        "drop_source_loss":replace(o,power_source_loss_w=0),
        "wrong_source_sign":replace(o,source_boundary_residual_pa=f.source_pressure_pa-o.p0_pa+f.source_impedance_pa_s_m3*o.u0_m3_s),
        "gamma_sign":replace(o,gamma_in=o.gamma_in.conjugate()),
        "determinant_broken":replace(o,matrix_determinant_residual=1+0j),
        "incorrect_port_plane":replace(o,entrance_plane="FREE_FIELD"),
        "stale_source_flow":replace(o,u0_m3_s=o.u0_m3_s*1.5),
        "stale_terminal_flow":replace(o,uL_m3_s=o.uL_m3_s*0.5),
    }
    for mutant_id,m in mutants.items():
        check=audit_row(f,m,ROWS[4])
        assert check.verdict=="FAIL",mutant_id
        assert check.failures,mutant_id


def test_oracle_rejects_corrupted_schema_and_column_order(tmp_path):
    bad=dict(ORACLE)
    bad["columns"]=list(reversed(ORACLE["columns"]))
    path=tmp_path/"oracle.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError,match="column"):
        load_oracle(path,verify_pin=False)


def test_research_cli_with_full_outputs(tmp_path):
    path=tmp_path/"results.json"
    proc=subprocess.run([sys.executable,str(STUDY/"run.py"),"--no-pin","--output",str(path)],capture_output=True,text=True,check=False)
    assert proc.returncode==0,proc.stderr+proc.stdout
    output=json.loads(path.read_text())
    assert output["summary"]["frozen_rows"]==18
    assert output["summary"]["passed"]==18
    assert output["summary"]["failed"]==0
    assert len(output["rows"])==18
    assert output["source_calibration"]=="NUMERIC_EQUIVALENT_FIXTURE_NOT_EMPIRICAL"
    assert output["rows"][0]["ports"]["p0_pa"]!=output["rows"][0]["ports"]["pL_pa"]
    assert "uL_m3_s" in output["rows"][0]["ports"]