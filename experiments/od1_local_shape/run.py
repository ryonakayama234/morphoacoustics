"""OD-1 real physics research, not an Organ API or Studio Take."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import runpy
import tempfile
import wave

import numpy as np
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ORACLE = runpy.run_path(str(HERE / "oracle.py"))
CENTERS = (4, 8)
RATIOS = (.90, 1.00, 1.10)
EXPECTED_VOLUMES = {
    (4,.9):8.71040561670529e-5,(4,1.):8.76190191086193e-5,(4,1.1):8.81091698354470e-5,
    (8,.9):8.57972936483764e-5,(8,1.):8.76190191086193e-5,(8,1.1):8.93773956328578e-5,
}
EXPECTED_HARMONICS = {(4,.9):.26896411,(4,1.1):.30760229,(8,.9):.17701535,(8,1.1):.13874321}
FREQ = np.arange(100.,3500.1,25.)
HARMONICS = np.arange(100.,3500.1,100.)
TIMES = (0.,.20,.35,.50)
SAMPLES = 24000
FREEZE = ROOT/"docs/research/od1-organ-shape-assembly-20261101/A0_A3_FREEZE_20261101.md"


def validate(center: object, ratio: object) -> tuple[int,float]:
    if type(center) is not int or center not in CENTERS:
        raise ValueError("UNSUPPORTED center (allowed 4 or 8)")
    if type(ratio) is not float or not math.isfinite(ratio) or ratio not in RATIOS:
        raise ValueError("UNSUPPORTED numeric rest-area ratio")
    return center,ratio


def weights(center: int) -> tuple[float,...]:
    return tuple(1. if i==center else .5 if abs(i-center)==1
                 else .25 if abs(i-center)==2 else 0. for i in range(16))


def edit_geometry(base: Tract1DGeometry, center: int, ratio: float) -> Tract1DGeometry:
    validate(center,ratio)
    if len(base.sections)!=16 or any(s.length_m!=.01 or not math.isfinite(s.area_m2)
                                    or s.area_m2<=0. for s in base.sections):
        raise ValueError("UNSUPPORTED: canonical 16x10mm positive rest tract required")
    if ratio==1.:
        return base
    theta=math.log(ratio)
    return Tract1DGeometry(cavity_id=base.cavity_id,
        sections=tuple(TubeSection(length_m=s.length_m,area_m2=s.area_m2*math.exp(theta*w))
                       for s,w in zip(base.sections,weights(center),strict=True)))


def areas(geometry: Tract1DGeometry) -> np.ndarray:
    return np.asarray([s.area_m2 for s in geometry.sections],dtype=np.float64)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_f64(data: np.ndarray) -> str:
    return sha_bytes(np.asarray(data,dtype="<f8").tobytes())


def wav_bytes(raw: np.ndarray, gain: float) -> bytes:
    if raw.shape!=(SAMPLES,) or not np.isfinite(raw).all():
        raise ValueError("INVALID physical raw pressure")
    scaled=raw*gain
    if not np.isfinite(scaled).all() or float(np.max(np.abs(scaled)))>.90000001:
        raise ValueError("INVALID shared WAV gain; clipping")
    pcm=np.rint(scaled*32767).astype("<i2")
    stream=io.BytesIO()
    with wave.open(stream,"wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(48000)
        output.writeframes(pcm.tobytes())
    return stream.getvalue()


def check_transfer(exp: object, geometry: Tract1DGeometry) -> dict[str,float]:
    a=areas(geometry)
    out={}
    for name,f in (("grid",FREQ),("harmonics",HARMONICS)):
        matrix=ORACLE["direct_uout_uin"](a,f)
        recurrence=ORACLE["recursive_uout_uin"](a,f)
        actual=exp.EXP26.EXP9.outlet_volume_velocity_transfer(geometry,f)
        observed=exp.EXP26.EXP9.far_field_pressure_transfer(geometry,f)
        expected_observer=ORACLE["radiated_pressure_proxy"](recurrence,f)
        def relative(x: np.ndarray,y: np.ndarray) -> float:
            return float(np.max(np.abs(x-y)/np.maximum(np.abs(y),1e-12)))
        error=max(relative(matrix,recurrence),relative(actual,recurrence),
                  relative(observed,expected_observer))
        if not math.isfinite(error) or error>1e-9:
            raise RuntimeError("G2 FAIL: model-matched independent transfer disagreement")
        out[name+"_relative_complex_error"]=error
        out[name+"_phase_error_rad"]=float(np.max(np.abs(np.angle(actual/recurrence))))
    return out


def run(output_dir: Path) -> dict[str,object]:
    if output_dir.exists():
        raise FileExistsError("never overwrite scientific evidence")
    if not FREEZE.is_file():
        raise RuntimeError("A3 preregistration missing")
    adapter=runpy.run_path(str(ROOT/"tools/cc_a2_live.py"))
    frozen=adapter["_load_frozen_adapter"]()
    exp=frozen._load_audited_experiment()
    if np.__version__!=exp.AUDITED_NUMPY_VERSION:
        raise RuntimeError("G0 FAIL: wrong pinned NumPy")
    base=exp.EXP26.EXP23.primary_geometry("a")
    base_areas=areas(base)
    oracle_base=ORACLE["published_areas"]()
    if base_areas.shape!=(16,) or np.max(np.abs(base_areas-oracle_base))>1e-15:
        raise RuntimeError("G0 FAIL: wrong original published anatomy/order")
    sources,_=exp.EXP26.EXP13.build_sources()
    source=np.asarray(sources[frozen.SOURCE_ID].source,dtype=np.float64)
    if source.shape!=(SAMPLES,) or not np.isfinite(source).all():
        raise RuntimeError("G0 FAIL: original prescribed source changed")
    task_sha=exp.sha256_json(exp.task_plan_payload())
    rows=[]
    for center in CENTERS:
        for ratio in RATIOS:
            geom=edit_geometry(base,center,ratio)
            measured_area=areas(geom)
            predicted_area=ORACLE["reference_areas"](center,ratio)
            log_error=float(np.max(np.abs(np.log(measured_area/oracle_base)-
                             math.log(ratio)*ORACLE["reference_weights"](center))))
            if log_error>1e-12:
                raise RuntimeError("G1 FAIL: wrong 5-cell shape equation")
            volume=math.fsum(s.area_m2*s.length_m for s in geom.sections)
            volume_ref=ORACLE["static_volume"](predicted_area)
            if abs(volume-volume_ref)/volume_ref>1e-12 or abs(volume-EXPECTED_VOLUMES[(center,ratio)])/volume_ref>1e-12:
                raise RuntimeError("G1 FAIL: independent rest volume")
            for t in TIMES:
                altered=exp.EXP27.task_geometry_for_time(geom,t,
                    control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,cavity_id="od1-altered")
                control=exp.EXP27.task_geometry_for_time(base,t,
                    control_step_s=exp.EXP27.PRIMARY_CONTROL_STEP_S,cavity_id="od1-control")
                residual=float(np.max(np.abs(np.log(areas(altered)/areas(control))-
                           math.log(ratio)*ORACLE["reference_weights"](center))))
                if residual>1e-10:
                    raise RuntimeError("H2 FAIL: nonseparable task geometry")
            rest_observer=check_transfer(exp,geom)
            endpoint=exp.EXP27.realize_task_geometry(geom,1.0,cavity_id="od1-end")
            end_observer=check_transfer(exp,endpoint)
            h_l2=0.
            if ratio!=1.:
                h=ORACLE["recursive_uout_uin"](predicted_area,HARMONICS)
                h0=ORACLE["recursive_uout_uin"](oracle_base,HARMONICS)
                h_l2=float(np.linalg.norm(h-h0)/np.linalg.norm(h0))
                if abs(h_l2-EXPECTED_HARMONICS[(center,ratio)])>2e-7 or h_l2<=1e-3:
                    raise RuntimeError("A3 FAIL: frozen model harmonic prediction")
            creature=exp.creature_for(cavity_id=geom.cavity_id,oral_reachable_end=.75)
            prepared=prepare_tract1d(creature,geom,provenance=PreparationProvenance(
                source="od1-research-only",model="tract1d.local-log-area-5.v1",
                notes=(f"center={center}",f"ratio={ratio:.2f}","no-public-api")))
            if exp.capability_report(prepared).status is not exp.FeasibilityStatus.FEASIBLE:
                raise RuntimeError("H2 FAIL: body cannot execute requested task")
            result=exp.evaluate_condition(prepared,source,label=f"od1-c{center}-r{ratio:.2f}")
            if result.feasibility.status is not exp.FeasibilityStatus.FEASIBLE or result.waveform is None or result.acoustic_call_count!=102:
                raise RuntimeError("H3 FAIL: no genuine physical execution")
            raw=np.asarray(result.waveform,dtype=np.float64)
            if raw.shape!=(SAMPLES,) or not np.isfinite(raw).all():
                raise RuntimeError("H3 FAIL: invalid Pa observation")
            if ratio==1. and exp.quantized_waveform_sha256(raw)!=exp.AUDITED_QUANTIZED_WAVEFORM_SHA256:
                raise RuntimeError("H0 FAIL: inherited CC-A2 M0 raw pressure drift")
            record={"center":center,"ratio":ratio,"shape_log_residual":log_error,
                "rest_volume_m3":volume,"volume_derivative_per_log_ratio_m3":ORACLE["volume_derivative"](predicted_area,center),
                "rest_areas_m2":measured_area.tolist(),
                "loaded_oracle_rest":rest_observer,"loaded_oracle_endpoint":end_observer,
                "rest_harmonic_transfer_l2":h_l2,
                "acoustic_calls":result.acoustic_call_count,
                "raw_pa_sha256_le_f64":sha_f64(raw),
                "raw_pa_quantized_sha256":exp.quantized_waveform_sha256(raw)}
            rows.append((center,ratio,raw,record))
    nulls=[row[2] for row in rows if row[1]==1.]
    if len(nulls)!=2 or exp.quantized_waveform_sha256(nulls[0])!=exp.quantized_waveform_sha256(nulls[1]):
        raise RuntimeError("H0 FAIL: independent repeated null mismatch")
    floor=float(np.linalg.norm(nulls[0]-nulls[1])/np.linalg.norm(nulls[0]))
    for center,ratio,raw,record in rows:
        diff=float(np.linalg.norm(raw-nulls[0])/np.linalg.norm(nulls[0]))
        if ratio!=1. and not diff>max(1e-4,10*floor):
            raise RuntimeError("G2 HOLD: physical difference below frozen floor")
        record["raw_pa_relative_l2"]=diff
        record["null_numerical_floor"]=floor
    shared_peak=max(float(np.max(np.abs(row[2]))) for row in rows)
    if not math.isfinite(shared_peak) or shared_peak<=0:
        raise RuntimeError("G2 HOLD: empty source-derived observation")
    gain=.90/shared_peak
    for center,ratio,raw,record in rows:
        key=f"c{center:02d}_r{int(round(ratio*100)):03d}"
        record["raw_file"]=key+".npy"
        record["preview_file"]=key+".wav"
        record["preview_sha256"]=sha_bytes(wav_bytes(raw,gain))
    result={
        "status":"GO_LIMITED_RESEARCH_SHAPE_AND_INHERITED_1D_ACOUSTICS",
        "baseline_core_main":"727b11ecf103f5c087cfcb820bdec11f883e7c03",
        "source_id":frozen.SOURCE_ID,"source_sha256_le_f64":sha_f64(source),
        "gesture_plan_sha256":task_sha,"sample_rate_hz":48000,"samples":SAMPLES,
        "preview_common_gain":gain,
        "observation":"Exp009 1D resistive outlet and 0.20m monopole pressure proxy (Pa)",
        "conditions":[row[3] for row in rows],
        "limitations":["not a self-oscillating vocal fold","not calibrated listener SPL",
                       "not human tissue physics","not natural Japanese",
                       "not audited human audibility","not a public body API or Studio Take"],
    }
    output_dir.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="od1-stage-",dir=output_dir.parent) as tmp:
        stage=Path(tmp)
        for center,ratio,raw,record in rows:
            with (stage/str(record["raw_file"])).open("wb") as dest:
                np.save(dest,raw,allow_pickle=False)
            (stage/str(record["preview_file"])).write_bytes(wav_bytes(raw,gain))
        (stage/"decision.json").write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n","utf-8")
        os.rename(stage,output_dir)
    return result


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    result=run(args.output_dir)
    print(json.dumps({"status":result["status"],
          "relative_raw_l2":[x["raw_pa_relative_l2"] for x in result["conditions"]]}))


if __name__=="__main__":
    main()
