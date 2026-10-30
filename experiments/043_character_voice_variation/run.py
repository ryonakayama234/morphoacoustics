"""Experiment 043: 2 x 2 causal body / timing pilot, research-only.

No new physical laws, source spectral painting, phonetic claim or Studio API.
Reuses the existing Experiment 027 task-field physical realizer and acoustic
transfer; varies only section length and the onset of one canonical task.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
from pathlib import Path
import subprocess
import sys

import numpy as np

from morphoacoustics.physical import Tract1DGeometry, TubeSection

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SAMPLE_RATE = 48_000
DURATION_S = 0.5
PROFILES = ("reference", "late_constriction")
BODIES = ("M0", "M1")
DELAYED_ONSET_S = 0.19
VERSION = "exp043-research-only/v0"
FROZEN_SOURCE_F0_HZ = 100.0


def load_model():
    source = ROOT / "experiments" / "027_task_field_vowel_transition" / "run.py"
    spec = importlib.util.spec_from_file_location("exp043_reference_task_model", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load existing task model")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_body(model, body_id: str) -> Tract1DGeometry:
    if body_id not in BODIES:
        raise ValueError("unknown exact research body")
    base = model.EXP26.EXP23.primary_geometry("a")
    section_length = 0.010 if body_id == "M0" else 0.011
    return Tract1DGeometry(
        cavity_id="exp043-" + body_id,
        sections=tuple(
            TubeSection(length_m=section_length, area_m2=s.area_m2)
            for s in base.sections
        ),
    )


def timing_tasks(model, profile: str):
    if profile not in PROFILES:
        raise ValueError("unknown research timing profile")
    tasks = list(model.TASKS)
    if profile == "late_constriction":
        old = tasks[1]
        tasks[1] = model.CandidateTask(
            task=old.task, location=old.location, degree=old.degree,
            onset_s=DELAYED_ONSET_S, offset_s=old.offset_s,
        )
    return tuple(tasks)


def realize(model, body: Tract1DGeometry, profile: str, time_s: float):
    # Reuse the original physical realization law unchanged. Only the temporal
    # activation of the second gesture changes, never its anatomical target.
    tasks = timing_tasks(model, profile)
    activation = tuple(
        model.task_activation_at_time(
            task, time_s, control_step_s=model.PRIMARY_CONTROL_STEP_S
        )
        for task in tasks
    )
    geometry = model.realize_task_geometry_from_activations(
        body, activation, cavity_id=body.cavity_id + "-" + profile
    )
    return geometry, activation


def physical_render(model, source: np.ndarray, body: Tract1DGeometry, profile: str):
    def transfer_at_time(center_s: float, frequency_hz: np.ndarray):
        geometry, _ = realize(model, body, profile, center_s)
        return model.EXP26.EXP9.far_field_pressure_transfer(geometry, frequency_hz)

    return np.asarray(
        model.EXP26.EXP12.frame_render(
            source, transfer_at_time,
            hop_size=model.PRIMARY_HOP_SIZE, edge_mode="preroll_edge",
        ), dtype=np.float64
    )


def sha256_array(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<f8").tobytes()).hexdigest()


def audited_fixed_source(model):
    """Require the declared, inherited LF source rather than trusting its label."""
    sources, _ = model.EXP26.EXP13.build_sources()
    source_result = sources.get("lf_fixed")
    if source_result is None:
        raise RuntimeError("frozen lf_fixed source is missing")
    regression = model.EXP26.source_regression(source_result)
    planned = np.asarray(source_result.planned_f0_hz, dtype=np.float64)
    if (
        not regression["pass"]
        or planned.shape != (round(DURATION_S * SAMPLE_RATE),)
        or not np.isfinite(planned).all()
        or not np.allclose(
            planned, FROZEN_SOURCE_F0_HZ, atol=1e-12, rtol=0.0
        )
    ):
        raise RuntimeError("inherited LF source failed frozen 100 Hz regression")
    source = np.asarray(source_result.source, dtype=np.float64)
    if source.shape != planned.shape or not np.isfinite(source).all():
        raise RuntimeError("frozen LF source has invalid samples")

    # The inherited Exp026 regression checks nominal F0 metadata, zero noise,
    # and cycle-boundary jumps, but cannot by itself detect a generator which
    # changes actual phase progression while retaining 100 Hz metadata.
    # Derive the expected phase independently from the frozen sampling clock.
    cycles = np.asarray(source_result.cycles, dtype=np.float64)
    expected_cycles = (
        np.arange(source.size, dtype=np.float64)
        * (FROZEN_SOURCE_F0_HZ / SAMPLE_RATE)
    )
    if (
        cycles.shape != source.shape
        or not np.isfinite(cycles).all()
        or not np.allclose(cycles, expected_cycles, atol=1e-8, rtol=0.0)
    ):
        raise RuntimeError("frozen LF source phase progression differs from 100 Hz")

    # Confirm that the emitted waveform is the declared deterministic LF
    # opening times its physical gain envelope, not an altered source with
    # unchanged planned-F0/cycle metadata. No post-render signal replacement.
    opening = np.asarray(source_result.opening, dtype=np.float64)
    gain = np.asarray(source_result.planned_gain, dtype=np.float64)
    if (
        opening.shape != source.shape or gain.shape != source.shape
        or not np.isfinite(opening).all() or not np.isfinite(gain).all()
    ):
        raise RuntimeError("frozen LF source has invalid opening/gain controls")
    expected_source = model.EXP26.EXP13.normalize_peak(opening * gain)
    if not np.allclose(source, expected_source, atol=1e-15, rtol=1e-11):
        raise RuntimeError("frozen LF source differs from declared physical controls")
    return source, regression, float(planned[0])


def execution_provenance() -> dict:
    """Attach the executing checkout and runtime to EACH generated receipt."""
    def git(*arguments: str) -> str:
        try:
            return subprocess.check_output(
                ["git", *arguments], cwd=ROOT, text=True,
                stderr=subprocess.PIPE,
            ).strip()
        except (OSError, subprocess.CalledProcessError) as error:
            raise RuntimeError("cannot establish execution checkout provenance") from error

    revision = git("rev-parse", "--verify", "HEAD")
    if len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise RuntimeError("invalid Git HEAD revision")
    return {
        "core_commit_sha": revision,
        "tracked_worktree_dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
    }


def run(out: Path) -> dict:
    if out.exists():
        raise FileExistsError("research output must be a new directory")
    provenance = execution_provenance()
    model = load_model()
    base0, base1 = (make_body(model, body_id) for body_id in BODIES)
    if len(base0.sections) != 16 or len(base1.sections) != 16:
        raise RuntimeError("expected the existing 16-section body")
    if not np.array_equal(
        [s.area_m2 for s in base0.sections],
        [s.area_m2 for s in base1.sections],
    ):
        raise RuntimeError("body intervention changed area")
    if not np.isclose(base1.total_length_m / base0.total_length_m, 1.10, atol=1e-12):
        raise RuntimeError("incorrect axial intervention")

    source, source_regression, observed_f0_hz = audited_fixed_source(model)

    # Causal negative and positive controls, evaluated before audio synthesis.
    for body in (base0, base1):
        initial, _ = realize(model, body, "reference", 0.0)
        if not np.array_equal(
            [s.area_m2 for s in initial.sections],
            [s.area_m2 for s in body.sections],
        ):
            raise RuntimeError("zero-activation geometry changed")
        early_a, _ = realize(model, body, "reference", 0.17)
        early_b, _ = realize(model, body, "late_constriction", 0.17)
        end_a, _ = realize(model, body, "reference", 0.50)
        end_b, _ = realize(model, body, "late_constriction", 0.50)
        if np.array_equal(
            [s.area_m2 for s in early_a.sections],
            [s.area_m2 for s in early_b.sections],
        ):
            raise RuntimeError("timing intervention had no physical effect")
        if not np.array_equal(
            [s.area_m2 for s in end_a.sections],
            [s.area_m2 for s in end_b.sections],
        ):
            raise RuntimeError("timing intervention changed final target")

    cases = {}
    for body_id, body in zip(BODIES, (base0, base1), strict=True):
        for profile in PROFILES:
            pressure = physical_render(model, source, body, profile)
            if pressure.shape != source.shape or not np.isfinite(pressure).all():
                raise RuntimeError("invalid pressure observation")
            cases[body_id + "_" + profile] = (body, profile, pressure)

    # Detect a missing intervention. This is not a listening-quality gate.
    for profile in PROFILES:
        if np.array_equal(cases["M0_" + profile][2], cases["M1_" + profile][2]):
            raise RuntimeError("body change yielded identical pressure")
    for body_id in BODIES:
        if np.array_equal(cases[body_id + "_reference"][2],
                          cases[body_id + "_late_constriction"][2]):
            raise RuntimeError("timing change yielded identical pressure")

    shared_peak = max(float(np.max(np.abs(item[2]))) for item in cases.values())
    if shared_peak <= 0 or not np.isfinite(shared_peak):
        raise RuntimeError("invalid common listening reference")
    listening_scale = 0.9 / shared_peak

    # All four samples use one fixed listening scale: never per-case normalize.
    from wave import open as wave_open
    out.mkdir(parents=True)
    info = {
        "schema": VERSION, "status": "NUMERICAL_PILOT_ONLY",
        "reference_model": "Experiment027 task-field; Experiment023 Arai vowel tube",
        "execution": provenance,
        "source": {"kind": "lf_fixed", "sha256_float64": sha256_array(source),
                   "f0_hz": observed_f0_hz, "sample_rate_hz": SAMPLE_RATE,
                   "frozen_regression": source_regression},
        "interventions": {
            "body": "M1 sections 0.011m vs M0 0.010m, all areas identical",
            "timing": "second constriction onset 0.19s vs 0.15s; same 0.35s offset and final target",
        },
        "listening": {"shared_pcm_scale_per_pa": listening_scale,
                      "per_case_normalization": False},
        "cases": {},
        "claims_excluded": [
            "natural_voice", "speaker_identity", "phoneme_correctness",
            "perceptual_discriminability", "physiological_motor_persona",
            "general_character_creator", "Studio_API",
        ],
    }
    for case_id, (body, profile, pressure) in cases.items():
        np.save(out / (case_id + "_pressure_pa.npy"), pressure, allow_pickle=False)
        pcm = np.rint(pressure * listening_scale * 32767.0).astype("<i2")
        with wave_open(str(out / (case_id + ".wav")), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(SAMPLE_RATE)
            audio.writeframes(pcm.tobytes())
        info["cases"][case_id] = {
            "body_id": body.cavity_id, "profile": profile,
            "length_m": body.total_length_m,
            "pressure_sha256_float64": sha256_array(pressure),
            "rms_pa": float(np.sqrt(np.mean(pressure ** 2))),
            "peak_pa": float(np.max(np.abs(pressure))),
            "pcm_sha256": hashlib.sha256(pcm.tobytes()).hexdigest(),
        }
    (out / "receipt.json").write_text(
        json.dumps(info, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.out), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
