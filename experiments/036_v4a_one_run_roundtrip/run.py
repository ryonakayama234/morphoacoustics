"""V4-A: one-source, one-timeline, one-render 1s /a/-like→/i/-like→/a/-like.

Research-only experiment stacked upon Draft PR #77 preregistration. It does
NOT implement dynamic tissue, traveling-wave time-domain acoustics, FSI,
coarticulation, arbitrary phonemes, or a production voice capability.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE = HERE / "wolfram" / "schedule_oracle.json"

# Reuse the audited reference and existing realizer, not a recreated voice model.
import importlib.util
import sys
from types import ModuleType


def load_experiment(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import experiment: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP29 = load_experiment("morpho_exp029_for_036", EXPERIMENTS /
                        "029_task_field_embodied_infeasibility" / "run.py")
EXP27 = EXP29.EXP27
EXP26 = EXP29.EXP26
EXP13 = EXP26.EXP13
EXP12 = EXP26.EXP12

RATE = 48000
DURATION = 1.0
SAMPLES = 48000
SEED = 0
PRIMARY_STEP = 0.005
REFERENCE_STEP = 0.0025
PRIMARY_HOP = 256
REFERENCE_HOP = 128
TRACE_STEP = 0.010
REFERENCE_SIGNATURE = EXP29.AUDITED_QUANTIZED_WAVEFORM_SHA256


def analytic_activation(time_s: float) -> float:
    if not math.isfinite(time_s):
        raise ValueError("time must be finite")
    if time_s <= .15 or time_s >= .85:
        return 0.0
    if time_s >= .35 and time_s <= .65:
        return 1.0
    u = (time_s-.15)/.20 if time_s < .35 else (.85-time_s)/.20
    return float(u*u*(3.0-2.0*u))


def activation_at(time_s: float, step_s: float) -> tuple[float, ...]:
    if step_s not in {PRIMARY_STEP, REFERENCE_STEP}:
        raise ValueError("control grid not preregistered")
    sample_times = np.arange(-2, int(round(DURATION/step_s))+3,
                             dtype=np.float64)*step_s
    sampled = np.asarray([analytic_activation(float(t)) for t in sample_times])
    value = float(np.interp(time_s, sample_times, sampled))
    return tuple(value for _ in EXP27.TASKS)


def body():
    a = EXP26.EXP23.primary_geometry("a")
    creature = EXP29.creature_for(cavity_id=a.cavity_id, oral_reachable_end=.75)
    prep = EXP29.prepared_for(creature=creature, geometry=a, condition="M_plus")
    report = EXP29.capability_report(prep)
    if report.status is not EXP29.FeasibilityStatus.FEASIBLE:
        raise RuntimeError(f"Frozen prepared M_plus body not feasible: {report}")
    return prep


def geometry_at(start, time_s: float, step_s: float):
    # Every task remains separate in the frozen task representation.
    # This candidate has deliberately coincident activations, not a new API.
    return EXP27.realize_task_geometry_from_activations(
        start, activation_at(time_s, step_s),
        cavity_id=start.cavity_id
    )


def full_lf_source() -> tuple[np.ndarray, np.ndarray]:
    # Exactly the existing LF Rd=1.0 flow pulse and peak, but globally 1s.
    params = EXP13.lf_parameters()
    phase, flow = EXP13.lf_flow_shape(params)
    f0 = np.full(SAMPLES, 100.0, dtype=np.float64)
    cycles = EXP13.cycles_from_f0(f0)
    envelope = EXP13.common_file_envelope(SAMPLES)
    source = EXP13.normalize_peak(
        np.interp(np.mod(cycles, 1.0), phase, flow) * envelope
    )
    return source, cycles


def render(source: np.ndarray, start, *, step_s: float, hop: int,
           offset_s: float = 0.0) -> tuple[np.ndarray, int]:
    count = 0

    def physical_transfer(center_s: float, frequencies_hz: np.ndarray):
        nonlocal count
        g = geometry_at(start, offset_s + center_s, step_s)
        count += 1
        return EXP26.EXP9.far_field_pressure_transfer(g, frequencies_hz)

    pressure = EXP12.frame_render(
        source, physical_transfer, hop_size=hop, edge_mode="preroll_edge"
    )
    return np.asarray(pressure, dtype=np.float64), count


def sha_f64(arr: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(arr, dtype="<f8").tobytes()).hexdigest()


def source_provenance() -> dict[str, object]:
    """Record the actual read sources, not just an inherited task/oracle ID."""
    root = HERE.parents[1]
    source_paths = [
        "experiments/009_fixed_tract_waveform/run.py",
        "experiments/012_source_renderer_artifacts/run.py",
        "experiments/013_parametric_source_prosody/run.py",
        "experiments/023_static_vowel_calibration/run.py",
        "experiments/026_moving_vowel_transition/run.py",
        "experiments/027_task_field_vowel_transition/run.py",
        "experiments/029_task_field_embodied_infeasibility/run.py",
        "experiments/036_v4a_one_run_roundtrip/run.py",
        "experiments/036_v4a_one_run_roundtrip/wolfram/schedule_oracle.json",
    ]
    hashes = {p: hashlib.sha256((root / p).read_bytes()).hexdigest()
              for p in source_paths}
    git = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True)
    return {"git_head": git.stdout.strip(), "source_sha256": hashes}


def publish_listening_wav(output_dir: Path, pressure: np.ndarray,
                          checks: dict[str, bool]) -> tuple[str | None, float | None]:
    """Only passing research gates may produce a normally named preview WAV.

    Failed numeric experiments keep diagnostic arrays, never a playable artifact
    that a downstream creator could accidentally mistake for accepted physics.
    """
    if not checks or not all(checks.values()):
        return None, None
    wav_path = output_dir / "R1_listen.wav"
    gain = EXP26.EXP9.write_listening_wav(wav_path, pressure)
    return hashlib.sha256(wav_path.read_bytes()).hexdigest(), gain


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("no CSV rows")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def jump_diagnostics(pressure: np.ndarray) -> dict[str, float]:
    differences = np.abs(np.diff(pressure))
    def window_peak(lo: float, hi: float) -> float:
        a, b = round(lo*RATE), round(hi*RATE)
        return float(np.max(differences[max(0, a):min(len(differences), b)]))
    refs = ((.05,.10), (.43,.57), (.90,.95))
    stable = max(window_peak(a,b) for a,b in refs)
    if stable <= 0:
        raise RuntimeError("silent stable-reference pressure")
    return {f"{t:.2f}s": window_peak(t-.015,t+.015)/stable
            for t in (.15,.35,.65,.85)}


def source_cycle_jump(source: np.ndarray) -> float:
    period = round(RATE/100)
    boundaries = np.arange(2*period, len(source)-2*period,
                           period, dtype=np.int64)
    rms = EXP26.rms(source)
    if rms <= 0:
        return math.inf
    return float(np.max(np.abs(source[boundaries]-source[boundaries-1]))/rms)


def run(output_dir: Path) -> dict[str, object]:
    # Exclusive new output: refuse even an empty directory or a dangling symlink.
    # No existing Take/evidence path may be reused or overwritten.
    output_dir.mkdir(parents=True, exist_ok=False)
    if np.__version__ != EXP29.AUDITED_NUMPY_VERSION:
        raise RuntimeError("V4-A must run NumPy==2.4.6 for the frozen baseline")
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    prep = body()
    start = prep.rest_state
    source0 = EXP13.build_sources()[0]["lf_fixed"].source
    baseline = EXP29.evaluate_condition(prep, source0, label="v4a-baseline")
    frozen_hash = (EXP29.quantized_waveform_sha256(baseline.waveform)
                   if baseline.waveform is not None else "MISSING")
    source, cycles = full_lf_source()
    pressure, count = render(source, start, step_s=PRIMARY_STEP, hop=PRIMARY_HOP)
    reference, ref_count = render(source, start, step_s=REFERENCE_STEP,
                                  hop=REFERENCE_HOP)
    # Deliberately invalid two independent half renders: diagnostic C0 only.
    left, count_l = render(source[:SAMPLES//2], start, step_s=PRIMARY_STEP,
                           hop=PRIMARY_HOP)
    right, count_r = render(source[SAMPLES//2:], start, step_s=PRIMARY_STEP,
                            hop=PRIMARY_HOP, offset_s=.5)
    concat_control = np.concatenate([left, right])

    checks: dict[str, bool] = {}
    checks["frozen_B0"] = bool(
        frozen_hash == REFERENCE_SIGNATURE and
        baseline.acoustic_call_count == 102 and
        baseline.feasibility.status is EXP29.FeasibilityStatus.FEASIBLE
    )
    checks["source_identity"] = bool(
        len(source)==SAMPLES and len(cycles)==SAMPLES and
        abs(EXP13.RD-1.0)<1e-15 and EXP13.BASE_F0_HZ==100 and
        abs(float(np.max(source))-EXP13.SOURCE_PEAK_M3_S)<1e-12 and
        np.all(np.isfinite(source))
    )
    anchors = oracle["anchors"]
    checks["analytic_schedule"] = all(
        abs(analytic_activation(t)-value)<=1e-12 for t,value in anchors
    )
    checks["same_three_tasks"] = bool(
        len(EXP27.TASKS)==oracle["task_count"] and
        EXP27.representation_is_clean(EXP27.task_plan_payload()) and
        all(abs(a-b)<1e-12 for t,v in anchors
            for a,b in zip(activation_at(t, PRIMARY_STEP), (v,)*3))
    )
    i_geom = EXP27.realize_task_geometry(
        start, 1.0, cavity_id=start.cavity_id
    )
    endpoint = EXP26.EXP23.primary_geometry("i")
    trace: list[dict[str, object]] = []
    trajectory = []
    all_geometry_valid = True
    endpoints_valid = True
    peak_errors = []
    for n in range(101):
        t = n*TRACE_STEP
        g = geometry_at(start, t, PRIMARY_STEP)
        areas = EXP26.geometry_areas(g)
        all_geometry_valid &= bool(np.all(np.isfinite(areas)) and
                                   np.all(areas>0))
        if n in {0,50,100}:
            target = EXP26.geometry_areas(i_geom if n==50 else start)
            endpoints_valid &= bool(np.allclose(areas,target,
                                                rtol=1e-12,atol=1e-15))
        peaks = EXP26.peak_array(g, count=3)
        trajectory.append(peaks[:2])
        p = {"time_s":t,"task0_activation":activation_at(t,PRIMARY_STEP)[0],
             "task1_activation":activation_at(t,PRIMARY_STEP)[1],
             "task2_activation":activation_at(t,PRIMARY_STEP)[2],
             "p1_hz":float(peaks[0]),"p2_hz":float(peaks[1]),
             "p3_hz":float(peaks[2]),"min_area_m2":float(np.min(areas)),
             "max_area_m2":float(np.max(areas))}
        trace.append(p)
    p0 = EXP26.peak_array(start,count=5)
    pi = EXP26.peak_array(i_geom,count=5)
    observed_target = EXP26.peak_array(endpoint,count=5)
    denominator = float(np.linalg.norm(p0[:2]-observed_target[:2]))
    task_i_error = float(np.linalg.norm(pi[:2]-observed_target[:2])
                          /denominator) if denominator>0 else math.inf
    trajectory_array = np.asarray(trajectory)
    step_ratio = (float(np.max(np.linalg.norm(np.diff(trajectory_array,axis=0),axis=1)))
                  /denominator) if denominator>0 else math.inf
    # Compare inherited immutable Exp027 independently checked peak grid.
    exp27_oracle = json.loads(EXP27.ORACLE_PATH.read_text(encoding="utf-8"))
    expected_peaks = np.asarray(exp27_oracle["peak_frequencies_hz"]["task_endpoint"])
    peak_errors = np.abs(pi-expected_peaks).tolist()

    checks["realized_geometry"] = bool(all_geometry_valid and endpoints_valid
         and task_i_error<=.20 and max(peak_errors)<=.5)
    checks["trajectory_step"] = bool(step_ratio<.20)
    stability_ratio = EXP12.normalized_rms_difference(pressure,reference)
    jumps = jump_diagnostics(pressure)
    checks["pressure_and_hop_stability"] = bool(
        len(pressure)==SAMPLES and np.all(np.isfinite(pressure)) and
        stability_ratio<.20 and max(jumps.values())<3.0
    )
    cycle_jump = source_cycle_jump(source)
    checks["single_phase_source"] = bool(
        cycle_jump<.01 and np.all(np.diff(cycles)>0) and
        abs((cycles[-1]+100/RATE)-100.0)<1e-7
    )
    checks["single_run_counts"] = bool(
        count==oracle["primary_transfer_calls"] and
        ref_count==oracle["reference_transfer_calls"] and
        count_l==102 and count_r==102 and
        concat_control.shape==(SAMPLES,)
    )

    write_rows(output_dir/"activation_and_resonance_trace.csv",trace)
    np.save(output_dir/"R1_raw_pressure_pa.npy",pressure)
    np.save(output_dir/"R1_ref_raw_pressure_pa.npy",reference)
    np.save(output_dir/"C0_naive_concat_DIAGNOSTIC_ONLY.npy",concat_control)
    np.save(output_dir/"source_volume_flow_m3_s.npy",source)
    wav_sha, pcm_gain = publish_listening_wav(output_dir, pressure, checks)
    manifest = {
        "experiment":"V4-A-experiment-036",
        "decision": "SUPPORT_ONE_RUN_ROUNDTRIP" if all(checks.values())
                    else "RESEARCH_GATE_FAILED",
        "claim_limit":"one continuous quasi-static geometry timeline and one "
                      "windowed renderer; no inertial articulator, traveling-wave "
                      "acoustic state, coarticulation or natural Japanese proof",
        "checks":checks,"metrics":{
            "task_i_error_ratio":task_i_error,
            "trajectory_step_ratio":step_ratio,
            "pressure_hop_normalized_rms_difference":stability_ratio,
            "jump_ratios":jumps,"source_cycle_jump_ratio":cycle_jump,
            "accepted_transfer_calls":count,
            "reference_transfer_calls":ref_count,
            "diagnostic_control_transfer_calls":[count_l,count_r],
            "baseline_transfer_calls":baseline.acoustic_call_count,
            "baseline_quantized_sha256":frozen_hash,
            "pressure_sha256":sha_f64(pressure),
            "source_sha256":sha_f64(source),
            "wav_sha256":wav_sha,
            "playback_gain_fullscale_per_pa":pcm_gain,
            "resonance_grid_peak_errors_hz":peak_errors,
        },
        "provenance":{
            "numpy":np.__version__,"python":platform.python_version(),
            "sample_rate_hz":RATE,"samples":SAMPLES,"seed":SEED,
            "source":"Experiment013 lf_fixed Rd=1.0 100Hz continuous phase",
            "prepared_body":"Experiment029 M_plus, oral reach end 0.75",
            "task_plan":EXP27.task_plan_payload(),
            "task_sha256":EXP29.sha256_json(EXP27.task_plan_payload()),
            "renderer":"Experiment012 frame_render preroll_edge",
            "oracle_sha256":hashlib.sha256(ORACLE.read_bytes()).hexdigest(),
            "executed_sources":source_provenance(),
        },
        "adoption_status":"NOT_ADOPTED_REVIEW_AND_HUMAN_GATE_PENDING",
        "preview_available":wav_sha is not None,
    }
    (output_dir/"summary.json").write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False,sort_keys=True)+"\n",
        encoding="utf-8")
    return manifest


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    summary=run(a.output_dir)
    print(json.dumps({"decision":summary["decision"],"checks":summary["checks"],
                      "metrics":summary["metrics"]},indent=2))
    if summary["decision"] != "SUPPORT_ONE_RUN_ROUNDTRIP":
        raise SystemExit(1)


if __name__=="__main__":
    main()
