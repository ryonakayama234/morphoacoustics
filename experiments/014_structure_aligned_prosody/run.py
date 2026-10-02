from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import platform
import sys
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import numpy as np

from morphoacoustics import GestureScore, Task, TaskParameter
from morphoacoustics.integration import (
    AnchorRef,
    CoordinationPlan,
    GestureEvent,
    GestureEventRef,
    GestureTemplate,
    PlanCompileResult,
    PlanCompileStatus,
    ProsodyEvent,
    ProsodyEventKind,
    ProsodyPlan,
    ResolvedAnchor,
    ResolvedTimeline,
    TimingConstraint,
    compile_shared_timeline,
)

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
ORACLE_PATH = HERE / "wolfram" / "prosody_oracle.json"

SAMPLE_RATE_HZ = 48_000
DURATION_S = 0.50
ACTIVE_START_S = 0.05
ACTIVE_END_S = 0.45
ACTIVE_DURATION_S = ACTIVE_END_S - ACTIVE_START_S
UNIT_COUNT = 8
NOMINAL_UNIT_S = ACTIVE_DURATION_S / UNIT_COUNT
BASE_F0_HZ = 100.0
F0_SEMITONE_EXCURSION = 0.6
DURATION_SCALE = 1.20
TARGET_AREA_M2 = 5.0e-5
LOCATION_A = 0.25
LOCATION_B = 0.75
ORAL_RAMP_S = 0.012
CONTROL_STEP_S = 0.005
REFERENCE_CONTROL_STEP_S = 0.0025
DEFAULT_HOP_SIZE = 256
REFERENCE_HOP_SIZE = 128
RNG_SEED = 14014
PRIMARY_TRIALS = 8


def load_experiment_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load experiment module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXP13 = load_experiment_module(
    "morpho_exp013_for_014",
    EXPERIMENTS / "013_parametric_source_prosody" / "run.py",
)
EXP12 = EXP13.EXP12
EXP11 = EXP12.EXP11


@dataclass(frozen=True, slots=True)
class Condition:
    name: str
    target_unit: int | None = None
    structured_pitch: bool = False
    duration_cue: bool = False
    diagnostic: bool = False


@dataclass(frozen=True, slots=True)
class CompiledFixture:
    condition: Condition
    prosody: ProsodyPlan
    timeline: ResolvedTimeline
    compiled: PlanCompileResult
    unit_durations_s: tuple[float, ...]
    unit_bounds_s: tuple[tuple[float, float], ...]
    boundary_anchor: str | None
    boundary_time_s: float | None


CONDITIONS = (
    Condition("flat"),
    Condition("diagnostic", diagnostic=True),
    Condition("pitch_early", target_unit=3, structured_pitch=True),
    Condition("pitch_late", target_unit=5, structured_pitch=True),
    Condition("duration_early", target_unit=3, duration_cue=True),
    Condition("duration_late", target_unit=5, duration_cue=True),
    Condition(
        "combined_early",
        target_unit=3,
        structured_pitch=True,
        duration_cue=True,
    ),
    Condition(
        "combined_late",
        target_unit=5,
        structured_pitch=True,
        duration_cue=True,
    ),
)


def target_anchor(condition: Condition) -> str | None:
    if condition.target_unit is None:
        return None
    return f"m{condition.target_unit}.end"


def make_prosody_plan(condition: Condition) -> ProsodyPlan:
    events: list[ProsodyEvent] = [
        ProsodyEvent("m2.onset", ProsodyEventKind.PROMINENCE, 0.5)
    ]
    anchor = target_anchor(condition)
    if anchor is not None:
        events.append(ProsodyEvent(anchor, ProsodyEventKind.BOUNDARY, 1.0))
        if condition.duration_cue:
            events.append(
                ProsodyEvent(anchor, ProsodyEventKind.DURATION_SCALE, DURATION_SCALE)
            )
    return ProsodyPlan(tuple(events))


def duration_scale_for_anchor(plan: ProsodyPlan, anchor_id: str | None) -> float:
    if anchor_id is None:
        return 1.0
    matches = [
        event.value
        for event in plan.events
        if event.anchor_id == anchor_id
        and event.kind is ProsodyEventKind.DURATION_SCALE
    ]
    if not matches:
        return 1.0
    if len(matches) != 1:
        raise RuntimeError(f"multiple duration modifiers for {anchor_id}")
    return float(matches[0])


def unit_durations_from_plan(
    condition: Condition, plan: ProsodyPlan
) -> tuple[float, ...]:
    durations = [NOMINAL_UNIT_S] * UNIT_COUNT
    anchor = target_anchor(condition)
    scale = duration_scale_for_anchor(plan, anchor)
    if scale == 1.0:
        return tuple(durations)
    if condition.target_unit is None:
        raise RuntimeError("duration scale requires target unit")

    target_index = condition.target_unit - 1
    extra = durations[target_index] * (scale - 1.0)
    durations[target_index] *= scale
    following = list(range(target_index + 1, UNIT_COUNT))
    if not following:
        raise RuntimeError("duration compensation requires following units")
    compensation = extra / len(following)
    for index in following:
        durations[index] -= compensation
        if durations[index] <= 2.0 * ORAL_RAMP_S:
            raise RuntimeError("duration compensation made a unit too short")

    if abs(sum(durations) - ACTIVE_DURATION_S) > 1e-12:
        raise RuntimeError("duration redistribution changed active duration")
    return tuple(durations)


def unit_bounds(
    durations_s: tuple[float, ...]
) -> tuple[tuple[float, float], ...]:
    cursor = ACTIVE_START_S
    result: list[tuple[float, float]] = []
    for duration_s in durations_s:
        start = cursor
        cursor = start + duration_s
        result.append((start, cursor))
    if abs(cursor - ACTIVE_END_S) > 1e-12:
        raise RuntimeError("unit timeline does not end at active-end")
    return tuple(result)


def resolved_timeline(
    durations_s: tuple[float, ...]
) -> tuple[ResolvedTimeline, tuple[tuple[float, float], ...]]:
    bounds = unit_bounds(durations_s)
    anchors: list[ResolvedAnchor] = [
        ResolvedAnchor("utterance.start", 0.0, "experiment014:utterance"),
        ResolvedAnchor("active.start", ACTIVE_START_S, "experiment014:active"),
    ]
    for index, (start_s, end_s) in enumerate(bounds, start=1):
        anchors.extend(
            (
                ResolvedAnchor(
                    f"m{index}.onset",
                    start_s,
                    f"experiment014:m{index}",
                ),
                ResolvedAnchor(
                    f"m{index}.end",
                    end_s,
                    f"experiment014:m{index}",
                ),
            )
        )
    anchors.extend(
        (
            ResolvedAnchor("active.end", ACTIVE_END_S, "experiment014:active"),
            ResolvedAnchor("utterance.end", DURATION_S, "experiment014:utterance"),
        )
    )
    return ResolvedTimeline(tuple(anchors)), bounds


def gesture_templates() -> tuple[GestureTemplate, ...]:
    templates: list[GestureTemplate] = []
    for index in range(1, UNIT_COUNT + 1):
        templates.append(
            GestureTemplate(
                id=f"g{index}",
                task=Task.CONSTRICT,
                target="oral",
                location=LOCATION_A if index % 2 == 1 else LOCATION_B,
                parameters=(
                    TaskParameter("target_area", TARGET_AREA_M2, "m2"),
                ),
            )
        )
    return tuple(templates)


def coordination_plan() -> CoordinationPlan:
    constraints: list[TimingConstraint] = []
    for index in range(1, UNIT_COUNT + 1):
        constraints.extend(
            (
                TimingConstraint(
                    GestureEventRef(f"g{index}", GestureEvent.ONSET),
                    AnchorRef(f"m{index}.onset"),
                ),
                TimingConstraint(
                    GestureEventRef(f"g{index}", GestureEvent.OFFSET),
                    AnchorRef(f"m{index}.end"),
                ),
            )
        )
    return CoordinationPlan(tuple(constraints))


def compile_fixture(condition: Condition) -> CompiledFixture:
    plan = make_prosody_plan(condition)
    durations = unit_durations_from_plan(condition, plan)
    timeline, bounds = resolved_timeline(durations)
    compiled = compile_shared_timeline(
        gestures=gesture_templates(),
        coordination=coordination_plan(),
        prosody=plan,
        timeline=timeline,
    )
    anchor = target_anchor(condition)
    boundary_time = None if anchor is None else timeline.time_for(anchor)
    return CompiledFixture(
        condition=condition,
        prosody=plan,
        timeline=timeline,
        compiled=compiled,
        unit_durations_s=durations,
        unit_bounds_s=bounds,
        boundary_anchor=anchor,
        boundary_time_s=boundary_time,
    )


def diagnostic_semitones(times_s: np.ndarray) -> np.ndarray:
    raw = EXP13.smooth_anchor_values(times_s, EXP13.F0_ANCHORS)
    y_values = np.asarray([value for _, value in EXP13.F0_ANCHORS], dtype=np.float64)
    lo = float(np.min(y_values))
    hi = float(np.max(y_values))
    midpoint = 0.5 * (lo + hi)
    half_range = 0.5 * (hi - lo)
    if half_range <= 0.0:
        raise RuntimeError("diagnostic contour has zero range")
    return np.asarray(
        (raw - midpoint) * (F0_SEMITONE_EXCURSION / half_range),
        dtype=np.float64,
    )


def structured_semitones(
    times_s: np.ndarray, boundary_time_s: float
) -> np.ndarray:
    b = boundary_time_s
    anchors = (
        (0.0, 0.0),
        (b - 0.070, 0.0),
        (b - 0.040, -0.2),
        (b - 0.025, -F0_SEMITONE_EXCURSION),
        (b - 0.015, -F0_SEMITONE_EXCURSION),
        (b + 0.015, +F0_SEMITONE_EXCURSION),
        (b + 0.030, +F0_SEMITONE_EXCURSION),
        (b + 0.080, +0.15),
        (b + 0.120, 0.0),
        (DURATION_S, 0.0),
    )
    if any(x1 <= x0 for (x0, _), (x1, _) in zip(anchors[:-1], anchors[1:], strict=True)):
        raise RuntimeError("structured F0 anchors are not strictly increasing")
    return EXP13.smooth_anchor_values(times_s, anchors)


def f0_for_condition(
    condition: Condition,
    fixture: CompiledFixture,
    times_s: np.ndarray,
) -> np.ndarray:
    if condition.diagnostic:
        semitones = diagnostic_semitones(times_s)
    elif condition.structured_pitch:
        if fixture.boundary_time_s is None:
            raise RuntimeError("structured pitch requires boundary time")
        semitones = structured_semitones(times_s, fixture.boundary_time_s)
    else:
        semitones = np.zeros_like(times_s)
    return np.asarray(
        BASE_F0_HZ * np.power(2.0, semitones / 12.0),
        dtype=np.float64,
    )


def build_source(
    condition: Condition,
    fixture: CompiledFixture,
    lf_phase: np.ndarray,
    lf_flow: np.ndarray,
) -> object:
    sample_count = int(round(DURATION_S * SAMPLE_RATE_HZ))
    times_s = np.arange(sample_count, dtype=np.float64) / SAMPLE_RATE_HZ
    planned_f0 = f0_for_condition(condition, fixture, times_s)
    cycles = EXP13.cycles_from_f0(planned_f0)
    opening = np.interp(np.mod(cycles, 1.0), lf_phase, lf_flow)
    gain = EXP13.common_file_envelope(sample_count)
    deterministic = EXP13.normalize_peak(opening * gain)
    zeros = np.zeros_like(deterministic)
    return EXP13.SourceResult(
        condition.name,
        deterministic,
        deterministic.copy(),
        zeros,
        cycles,
        planned_f0,
        gain,
        opening,
    )


def smoothstep01(value: float) -> float:
    u = min(1.0, max(0.0, value))
    return u * u * (3.0 - 2.0 * u)


def analytic_activation(time_s: float, onset_s: float, offset_s: float) -> float:
    if time_s < onset_s or time_s >= offset_s:
        return 0.0
    duration = offset_s - onset_s
    ramp = min(ORAL_RAMP_S, 0.4 * duration)
    return smoothstep01((time_s - onset_s) / ramp) * smoothstep01(
        (offset_s - time_s) / ramp
    )


def reconstructed_activation(
    time_s: float,
    onset_s: float,
    offset_s: float,
    *,
    step_s: float,
) -> float:
    if time_s < onset_s or time_s >= offset_s:
        return 0.0
    left = math.floor(time_s / step_s) * step_s
    right = left + step_s
    a = analytic_activation(left, onset_s, offset_s)
    b = analytic_activation(right, onset_s, offset_s)
    if right == left:
        return a
    u = (time_s - left) / (right - left)
    return float(a + (b - a) * u)


def oral_activations(
    score: GestureScore,
    time_s: float,
    *,
    control_step_s: float,
) -> tuple[float, float]:
    activation_a = 0.0
    activation_b = 0.0
    for gesture in score.gestures:
        if gesture.location is None:
            continue
        activation = reconstructed_activation(
            time_s,
            gesture.onset_s,
            gesture.offset_s,
            step_s=control_step_s,
        )
        if abs(gesture.location - LOCATION_A) <= 1e-12:
            activation_a = max(activation_a, activation)
        elif abs(gesture.location - LOCATION_B) <= 1e-12:
            activation_b = max(activation_b, activation)
        else:
            raise RuntimeError(f"unexpected gesture location: {gesture.location}")
    return activation_a, activation_b


def render_fixture(
    source: np.ndarray,
    score: GestureScore,
    *,
    control_step_s: float,
    hop_size: int,
) -> np.ndarray:
    morphology = EXP11.EXP8.prepared(EXP11.EXP8.BODIES[0])

    def transfer_for_time(center_s: float, frequencies_hz: np.ndarray) -> np.ndarray:
        safe_time = max(0.0, center_s)
        a, b = oral_activations(
            score,
            safe_time,
            control_step_s=control_step_s,
        )
        state = EXP11.state_for_activations(
            morphology,
            a,
            b,
            safe_time,
        )
        return EXP12.EXP9.far_field_pressure_transfer(state, frequencies_hz)

    return EXP12.frame_render(
        source,
        transfer_for_time,
        hop_size=hop_size,
        edge_mode="preroll_edge",
    )


def window_mean(values: np.ndarray, start_s: float, end_s: float) -> float:
    start = max(0, int(round(start_s * SAMPLE_RATE_HZ)))
    end = min(values.size, int(round(end_s * SAMPLE_RATE_HZ)))
    if end <= start:
        return math.nan
    return float(np.mean(values[start:end]))


def pitch_cue_metrics(
    source_result: object,
    boundary_time_s: float | None,
) -> dict[str, float]:
    if boundary_time_s is None:
        return {
            "pre_f0_hz": math.nan,
            "post_f0_hz": math.nan,
            "f0_reset_hz": math.nan,
            "f0_event_time_s": math.nan,
            "f0_event_timing_error_s": math.nan,
        }
    planned = np.asarray(source_result.planned_f0_hz, dtype=np.float64)
    pre = window_mean(planned, boundary_time_s - 0.024, boundary_time_s - 0.016)
    post = window_mean(planned, boundary_time_s + 0.016, boundary_time_s + 0.029)
    derivative = np.abs(np.gradient(planned) * SAMPLE_RATE_HZ)
    times = np.arange(planned.size, dtype=np.float64) / SAMPLE_RATE_HZ
    mask = (times >= boundary_time_s - 0.04) & (times <= boundary_time_s + 0.04)
    indices = np.flatnonzero(mask)
    event_index = int(indices[np.argmax(derivative[mask])])
    event_time = event_index / SAMPLE_RATE_HZ
    return {
        "pre_f0_hz": pre,
        "post_f0_hz": post,
        "f0_reset_hz": post - pre,
        "f0_event_time_s": event_time,
        "f0_event_timing_error_s": abs(event_time - boundary_time_s),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_wav(path: Path, values: np.ndarray, gain: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    listening = np.clip(np.asarray(values, dtype=np.float64) * gain, -1.0, 1.0)
    pcm = np.round(listening * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE_HZ)
        wav.writeframes(pcm.tobytes())


def plan_payload(fixture: CompiledFixture) -> dict[str, object]:
    return {
        "condition": fixture.condition.name,
        "boundary_anchor": fixture.boundary_anchor,
        "boundary_time_s": fixture.boundary_time_s,
        "prosody_events": [
            {
                "anchor_id": event.anchor_id,
                "kind": event.kind.value,
                "value": event.value,
            }
            for event in fixture.prosody.events
        ],
        "anchors": [
            {
                "id": anchor.id,
                "time_s": anchor.time_s,
                "provenance": anchor.provenance,
            }
            for anchor in fixture.timeline.anchors
        ],
        "compiled_status": fixture.compiled.status.value,
        "compiler_version": fixture.compiled.compiler_version,
        "resolved_prosody": [
            {
                "anchor_id": event.anchor_id,
                "kind": event.kind.value,
                "value": event.value,
                "time_s": event.time_s,
            }
            for event in fixture.compiled.resolved_prosody
        ],
        "gesture_windows": [
            {
                "task": gesture.task.value,
                "onset_s": gesture.onset_s,
                "offset_s": gesture.offset_s,
                "location": gesture.location,
            }
            for gesture in (
                fixture.compiled.score.gestures
                if fixture.compiled.score is not None
                else ()
            )
        ],
        "diagnostics": [
            {"code": diagnostic.code, "message": diagnostic.message}
            for diagnostic in fixture.compiled.diagnostics
        ],
    }


def load_oracle() -> dict[str, object]:
    return json.loads(ORACLE_PATH.read_text(encoding="utf-8"))


def verify_oracle(
    fixtures: dict[str, CompiledFixture],
) -> dict[str, float]:
    oracle = load_oracle()
    tolerance = float(oracle["absolute_tolerance"])
    early = fixtures["combined_early"]
    late = fixtures["combined_late"]
    low_f0 = BASE_F0_HZ * 2.0 ** (-F0_SEMITONE_EXCURSION / 12.0)
    high_f0 = BASE_F0_HZ * 2.0 ** (+F0_SEMITONE_EXCURSION / 12.0)
    actual = {
        "nominal_unit_s": NOMINAL_UNIT_S,
        "early_nominal_boundary_s": fixtures["pitch_early"].boundary_time_s,
        "late_nominal_boundary_s": fixtures["pitch_late"].boundary_time_s,
        "duration_scale": DURATION_SCALE,
        "target_unit_s": early.unit_durations_s[2],
        "early_post_boundary_unit_s": early.unit_durations_s[3],
        "late_post_boundary_unit_s": late.unit_durations_s[5],
        "early_realized_boundary_s": early.boundary_time_s,
        "late_realized_boundary_s": late.boundary_time_s,
        "active_duration_s": sum(early.unit_durations_s),
        "low_f0_hz": low_f0,
        "high_f0_hz": high_f0,
        "reset_hz": high_f0 - low_f0,
        "binomial_ge_7_of_8": sum(math.comb(8, k) for k in (7, 8)) / 2**8,
    }
    errors: dict[str, float] = {}
    for key, value in actual.items():
        expected = float(oracle[key])
        if value is None:
            raise RuntimeError(f"oracle value unresolved: {key}")
        error = abs(float(value) - expected)
        errors[key] = error
        if error > tolerance:
            raise RuntimeError(
                f"Python value disagrees with Wolfram oracle for {key}: "
                f"{value} vs {expected}"
            )
    return errors


def write_control_trace(
    path: Path,
    fixtures: dict[str, CompiledFixture],
    sources: dict[str, object],
) -> None:
    rows: list[dict[str, object]] = []
    step = int(round(0.001 * SAMPLE_RATE_HZ))
    for condition in CONDITIONS:
        fixture = fixtures[condition.name]
        source = sources[condition.name]
        if fixture.compiled.score is None:
            raise RuntimeError("cannot trace invalid compiled fixture")
        realized_f0 = EXP13.realized_f0(source)
        for index in range(0, source.source.size, step):
            t = index / SAMPLE_RATE_HZ
            a, b = oral_activations(
                fixture.compiled.score,
                t,
                control_step_s=CONTROL_STEP_S,
            )
            rows.append(
                {
                    "condition": condition.name,
                    "time_s": t,
                    "planned_f0_hz": source.planned_f0_hz[index],
                    "realized_f0_hz": realized_f0[index],
                    "planned_gain": source.planned_gain[index],
                    "oral_activation_a": a,
                    "oral_activation_b": b,
                }
            )
    write_csv(path, rows)


def make_blind_trials(
    output_dir: Path,
    candidate_waveforms: dict[str, np.ndarray],
    common_gain: float,
) -> None:
    listening_dir = output_dir / "listening" / "primary_pitch_blind"
    listening_dir.mkdir(parents=True, exist_ok=True)
    targets = ["pitch_early"] * 4 + ["pitch_late"] * 4
    rng = np.random.default_rng(RNG_SEED)
    order = list(rng.permutation(targets))
    public_rows: list[dict[str, object]] = []
    key_rows: list[dict[str, object]] = []
    for index, condition_name in enumerate(order, start=1):
        trial_id = f"T{index:02d}"
        filename = f"{trial_id}.wav"
        write_wav(
            listening_dir / filename,
            candidate_waveforms[condition_name],
            common_gain,
        )
        public_rows.append({"trial_id": trial_id, "file": filename})
        key_rows.append(
            {
                "trial_id": trial_id,
                "condition": condition_name,
                "target": "early" if condition_name.endswith("early") else "late",
            }
        )
    write_csv(listening_dir / "manifest.csv", public_rows)
    write_csv(output_dir / "blind_key.csv", key_rows)
    (listening_dir / "README.txt").write_text(
        "Experiment 014 primary blind listening\\n"
        "For each T01..T08, answer EARLY or LATE for the perceived boundary.\\n"
        "Also record boundary-not-felt, confidence, artifact, and voice-like notes separately.\\n"
        "Do not inspect blind_key.csv before completing the trials.\\n",
        encoding="utf-8",
    )


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    fixtures = {condition.name: compile_fixture(condition) for condition in CONDITIONS}
    oracle_errors = verify_oracle(fixtures)

    for fixture in fixtures.values():
        if fixture.compiled.status is not PlanCompileStatus.VALID:
            raise RuntimeError(
                f"{fixture.condition.name}: shared timeline compile failed"
            )
        if fixture.compiled.score is None:
            raise RuntimeError(f"{fixture.condition.name}: missing GestureScore")

    params = EXP13.lf_parameters(EXP13.RD)
    lf_phase, lf_flow = EXP13.lf_flow_shape(params)
    sources = {
        condition.name: build_source(
            condition,
            fixtures[condition.name],
            lf_phase,
            lf_flow,
        )
        for condition in CONDITIONS
    }

    candidate_waveforms: dict[str, np.ndarray] = {}
    reference_waveforms: dict[str, np.ndarray] = {}
    sensitivities: dict[str, float] = {}
    rows: list[dict[str, object]] = []

    for condition in CONDITIONS:
        fixture = fixtures[condition.name]
        score = fixture.compiled.score
        if score is None:
            raise RuntimeError("missing compiled score")
        source = sources[condition.name]
        candidate = render_fixture(
            source.source,
            score,
            control_step_s=CONTROL_STEP_S,
            hop_size=DEFAULT_HOP_SIZE,
        )
        reference = render_fixture(
            source.source,
            score,
            control_step_s=REFERENCE_CONTROL_STEP_S,
            hop_size=REFERENCE_HOP_SIZE,
        )
        candidate_waveforms[condition.name] = candidate
        reference_waveforms[condition.name] = reference
        sensitivity = EXP12.normalized_rms_difference(reference, candidate)
        sensitivities[condition.name] = sensitivity

        source_metrics = EXP13.source_metrics(source)
        cue = pitch_cue_metrics(
            source,
            fixture.boundary_time_s if condition.structured_pitch else None,
        )
        target_duration = (
            fixture.unit_durations_s[condition.target_unit - 1]
            if condition.target_unit is not None
            else math.nan
        )
        target_duration_error = (
            abs(target_duration - NOMINAL_UNIT_S * DURATION_SCALE)
            if condition.duration_cue
            else 0.0
        )
        active_duration_error = abs(
            sum(fixture.unit_durations_s) - ACTIVE_DURATION_S
        )
        rendered_basic = EXP12.basic_signal_metrics(candidate)
        rows.append(
            {
                "condition": condition.name,
                "target_anchor": fixture.boundary_anchor or "",
                "boundary_time_s": (
                    fixture.boundary_time_s
                    if fixture.boundary_time_s is not None
                    else math.nan
                ),
                "target_unit_duration_s": target_duration,
                "target_duration_error_s": target_duration_error,
                "active_duration_error_s": active_duration_error,
                "planned_f0_min_hz": float(np.min(source.planned_f0_hz)),
                "planned_f0_max_hz": float(np.max(source.planned_f0_hz)),
                "planned_f0_range_hz": float(np.ptp(source.planned_f0_hz)),
                "f0_rmse_hz": source_metrics["f0_rmse_hz"],
                "pre_f0_hz": cue["pre_f0_hz"],
                "post_f0_hz": cue["post_f0_hz"],
                "f0_reset_hz": cue["f0_reset_hz"],
                "f0_event_time_s": cue["f0_event_time_s"],
                "f0_event_timing_error_s": cue["f0_event_timing_error_s"],
                "cycle_boundary_jump_per_rms": source_metrics[
                    "cycle_boundary_jump_per_rms"
                ],
                "fixed_10ms_lag_correlation": source_metrics[
                    "fixed_10ms_lag_correlation"
                ],
                "startup_peak_over_steady_rms": EXP12.startup_peak_over_steady_rms(
                    candidate
                ),
                "rendered_rms_pa": rendered_basic["rms"],
                "rendered_max_abs_derivative_per_rms": rendered_basic[
                    "max_abs_derivative_per_rms"
                ],
                "discretization_normalized_rms_difference": sensitivity,
                "finite": bool(np.all(np.isfinite(candidate))),
            }
        )

        np.save(
            output_dir / f"{condition.name}_raw_pressure_pa.npy",
            candidate,
        )

    row_map = {str(row["condition"]): row for row in rows}
    pair_rows: list[dict[str, object]] = []
    for family in ("pitch", "duration", "combined"):
        early = candidate_waveforms[f"{family}_early"]
        late = candidate_waveforms[f"{family}_late"]
        effect = EXP12.normalized_rms_difference(early, late)
        max_sensitivity = max(
            sensitivities[f"{family}_early"],
            sensitivities[f"{family}_late"],
        )
        pair_rows.append(
            {
                "family": family,
                "early_vs_late_normalized_rms_difference": effect,
                "max_discretization_normalized_rms_difference": max_sensitivity,
                "effect_over_discretization": effect
                / max(max_sensitivity, 1e-30),
            }
        )
    write_csv(output_dir / "boundary_pair_metrics.csv", pair_rows)

    flat_source = sources["flat"].source
    flat_fixed = EXP12.render_fixed_tract(
        flat_source,
        hop_size=DEFAULT_HOP_SIZE,
        edge_mode="preroll_edge",
    )
    oral_effect = EXP12.normalized_rms_difference(
        flat_fixed,
        candidate_waveforms["flat"],
    )
    oral_effect_retained = bool(
        oral_effect > 0.01
        and oral_effect > 5.0 * sensitivities["flat"]
    )

    write_csv(output_dir / "condition_metrics.csv", rows)
    write_control_trace(
        output_dir / "control_trajectories.csv",
        fixtures,
        sources,
    )
    (output_dir / "plan_provenance.json").write_text(
        json.dumps(
            {
                name: plan_payload(fixture)
                for name, fixture in fixtures.items()
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    common_peak = max(
        float(np.max(np.abs(values)))
        for values in candidate_waveforms.values()
    )
    if not math.isfinite(common_peak) or common_peak <= 0.0:
        raise RuntimeError("invalid common listening peak")
    common_gain = 0.90 / common_peak

    named_dir = output_dir / "listening" / "named_secondary"
    for condition in CONDITIONS:
        write_wav(
            named_dir / f"{condition.name}.wav",
            candidate_waveforms[condition.name],
            common_gain,
        )
    make_blind_trials(output_dir, candidate_waveforms, common_gain)

    plan_valid = all(
        fixture.compiled.status is PlanCompileStatus.VALID
        for fixture in fixtures.values()
    )
    semantic_boundary_valid = True
    for condition in CONDITIONS:
        fixture = fixtures[condition.name]
        if fixture.boundary_anchor is None:
            continue
        matches = [
            event
            for event in fixture.compiled.resolved_prosody
            if event.kind is ProsodyEventKind.BOUNDARY
        ]
        semantic_boundary_valid = semantic_boundary_valid and bool(
            len(matches) == 1
            and matches[0].anchor_id == fixture.boundary_anchor
            and fixture.boundary_time_s is not None
            and abs(matches[0].time_s - fixture.boundary_time_s) <= 1e-12
        )

    pitch_names = (
        "pitch_early",
        "pitch_late",
        "combined_early",
        "combined_late",
    )
    duration_names = (
        "duration_early",
        "duration_late",
        "combined_early",
        "combined_late",
    )

    pitch_reset_pass = all(
        float(row_map[name]["f0_reset_hz"]) >= 5.0
        for name in pitch_names
    )
    pitch_timing_pass = all(
        float(row_map[name]["f0_event_timing_error_s"]) <= 0.001
        for name in pitch_names
    )
    f0_tracking_pass = all(
        float(row["f0_rmse_hz"]) <= 0.1 for row in rows
    )
    duration_pass = all(
        float(row_map[name]["target_duration_error_s"]) <= 0.0001
        for name in duration_names
    )
    active_duration_pass = all(
        float(row["active_duration_error_s"]) <= 0.0001
        for row in rows
    )
    cycle_artifact_pass = all(
        float(row["cycle_boundary_jump_per_rms"]) < 0.01
        for row in rows
    )
    startup_pass = all(
        float(row["startup_peak_over_steady_rms"]) < 20.0
        for row in rows
    )
    finite_pass = all(bool(row["finite"]) for row in rows)

    pitch_only_range_difference = abs(
        float(row_map["pitch_early"]["planned_f0_range_hz"])
        - float(row_map["pitch_late"]["planned_f0_range_hz"])
    )
    combined_range_difference = abs(
        float(row_map["combined_early"]["planned_f0_range_hz"])
        - float(row_map["combined_late"]["planned_f0_range_hz"])
    )
    structured_range_reference = float(
        row_map["pitch_early"]["planned_f0_range_hz"]
    )
    diagnostic_range_difference = abs(
        float(row_map["diagnostic"]["planned_f0_range_hz"])
        - structured_range_reference
    )
    range_match_pass = bool(
        pitch_only_range_difference <= 0.1
        and combined_range_difference <= 0.1
        and diagnostic_range_difference <= 0.1
    )

    objective_pass = all(
        (
            plan_valid,
            semantic_boundary_valid,
            pitch_reset_pass,
            pitch_timing_pass,
            f0_tracking_pass,
            duration_pass,
            active_duration_pass,
            cycle_artifact_pass,
            startup_pass,
            finite_pass,
            range_match_pass,
            oral_effect_retained,
        )
    )
    decision = (
        "CONTROL_REALIZATION_VALIDATED_AWAITING_LISTENING"
        if objective_pass
        else "CONTROL_REALIZATION_FAILED"
    )

    result = {
        "decision": decision,
        "objective_gate_pass": objective_pass,
        "shared_timeline_valid": plan_valid,
        "semantic_boundary_provenance_valid": semantic_boundary_valid,
        "pitch_reset_ge_5hz": pitch_reset_pass,
        "pitch_event_timing_error_le_1ms": pitch_timing_pass,
        "f0_rmse_le_0_1hz": f0_tracking_pass,
        "duration_target_error_le_0_1ms": duration_pass,
        "active_duration_error_le_0_1ms": active_duration_pass,
        "cycle_boundary_jump_lt_0_01": cycle_artifact_pass,
        "startup_peak_over_steady_rms_lt_20": startup_pass,
        "f0_range_match_le_0_1hz": range_match_pass,
        "all_outputs_finite": finite_pass,
        "oral_effect_retained": oral_effect_retained,
        "oral_vs_fixed_normalized_rms_difference": oral_effect,
        "flat_discretization_normalized_rms_difference": sensitivities["flat"],
        "pitch_only_range_difference_hz": pitch_only_range_difference,
        "combined_range_difference_hz": combined_range_difference,
        "diagnostic_vs_structured_range_difference_hz": diagnostic_range_difference,
        "wolfram_oracle_absolute_errors": oracle_errors,
        "common_listening_gain_fullscale_per_pa": common_gain,
        "primary_human_gate": {
            "trials": PRIMARY_TRIALS,
            "target_balance": {"early": 4, "late": 4},
            "repeatability_threshold": ">=7/8 target-consistent choices",
            "chance_reference_under_independent_unbiased_binary_choice": 0.03515625,
            "interpretation": "within-listener engineering repeatability only; not a population-level p-value",
        },
        "limitations": [
            "mora-like oral sequence is a diagnostic alternating-constriction fixture, not calibrated Japanese phonemes",
            "duration-only condition depends on this uncalibrated oral timing fixture and is secondary",
            "20% phrase-final lengthening is an engineering diagnostic magnitude, not a claimed Tokyo Japanese population mean",
            "structured pitch cue is experiment-local and not a production intonation model",
            "gain/effort is intentionally held fixed in rev1 to avoid adding a third boundary cue",
            "quasi-stationary short-time tract filtering has no carried acoustic state",
            "objective success does not establish meaningful boundary perception until blinded listening is completed",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-014-output"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
