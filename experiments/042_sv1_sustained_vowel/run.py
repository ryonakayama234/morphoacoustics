"""SV-1: controlled single-sustain /a/-like duration, not WAV time stretch.

Experiment-local ONLY. This is prescribed LF excitation through an adopted
static, prepared oral tube + quasi-stationary acoustic transfer. It does not
simulate vocal-fold self-oscillation, respiration or mechanical holding force.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
import math
import os
from pathlib import Path
import runpy
import sys
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_RATE = 48_000
F0_HZ = 100.0
DURATIONS = (0.25, 0.50)
PRESET_ID = "v3b-axial-M0"
PRESET_REVISION = 1
STATIC_A_PEAKS_HZ = (720.25, 1288.50)  # Exp028 frozen M0 /a/ REST (not /i/ endpoint)
LISTENING_PEAK = 0.90
OUTCOME = "NUMERIC_GATE_PASS_CANDIDATE_NOT_ADOPTED"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _validated_context() -> tuple[object, object, object]:
    # Reuse exact adopted CC-A2 body preparation and transitive frozen experiment
    # source/NumPy/Wolfram preflight; do NOT copy geometry into an untracked fixture.
    cc = runpy.run_path(str(ROOT / "tools" / "cc_a2_live.py"))
    frozen = cc["_load_frozen_adapter"]()
    exp = frozen._load_audited_experiment()
    registry = cc["prepared_registry"](exp)
    from morphoacoustics.integration.body_presets import CharacterBodyBinding, BindingStatus
    resolution = registry.resolve(
        CharacterBodyBinding("sv1-research", PRESET_ID, PRESET_REVISION),
        required_backend_id=exp.TRACT1D_BACKEND_ID,
    )
    if resolution.status != BindingStatus.BOUND or resolution.preset is None:
        raise RuntimeError("SV-1 exact prepared M0 body unavailable")
    if resolution.snapshot is None:
        raise RuntimeError("SV-1 missing immutable body binding")
    prepared = resolution.preset.prepared
    report = exp.capability_report(prepared)
    if report.status != exp.FeasibilityStatus.FEASIBLE:
        raise RuntimeError("SV-1 body not physically feasible (no audio fallback)")
    geometry = prepared.rest_state
    expected = exp.EXP26.EXP23.primary_geometry("a")
    if (geometry.total_length_m != expected.total_length_m
            or len(geometry.sections) != 16
            or any(x.length_m != y.length_m or x.area_m2 != y.area_m2
                   for x, y in zip(geometry.sections, expected.sections, strict=True))):
        raise RuntimeError("SV-1 chosen body's rest geometry differs from frozen /a/")
    peaks = exp.EXP26.EXP23.peak_frequencies(geometry, count=2)
    if not np.allclose(peaks, STATIC_A_PEAKS_HZ, rtol=0.0, atol=0.25):
        raise RuntimeError("SV-1 static /a/ frozen Wolfram resonance oracle failed")
    return frozen, exp, resolution


def _source_for_duration(exp: object, duration_s: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if type(duration_s) is not float or duration_s not in DURATIONS:
        raise ValueError("SV-1 only supports exact 0.25 and 0.50 second durations")
    count = round(duration_s * SAMPLE_RATE)
    e13 = exp.EXP26.EXP23.EXP13
    if SAMPLE_RATE != e13.SAMPLE_RATE_HZ or F0_HZ != e13.BASE_F0_HZ:
        raise RuntimeError("SV-1 audited source sample rate or F0 changed")
    if e13.RD != 1.0 or e13.EXP12.SOURCE_RAMP_S != 0.01:
        raise RuntimeError("SV-1 audited Rd / envelope changed")
    # Use adopted cumulative phase algorithm, including its floating-point order.
    f0 = np.full(count, F0_HZ, dtype=np.float64)
    cycles = e13.cycles_from_f0(f0)
    phase, lf_flow = e13.lf_flow_shape(e13.lf_parameters())
    envelope = e13.common_file_envelope(count)
    opening = np.interp(np.mod(cycles, 1.0), phase, lf_flow)
    # Fixed normalization reference for BOTH durations. Per-file peak normalization
    # is a nuisance intervention: distinct finite-length samples have tiny
    # peak differences even during acoustically identical steady intervals.
    # Keep the inherited 0.50s LF source EXACT, and apply its scale to fresh
    # 0.25s source excitation. No completed WAV is cut, looped or stretched.
    ref_count = round(DURATIONS[1] * SAMPLE_RATE)
    ref_cycles = e13.cycles_from_f0(np.full(ref_count, F0_HZ, dtype=np.float64))
    ref_opening = np.interp(np.mod(ref_cycles, 1.0), phase, lf_flow)
    ref_unscaled = ref_opening * e13.common_file_envelope(ref_count)
    ref_peak = float(np.max(np.abs(ref_unscaled)))
    if not math.isfinite(ref_peak) or ref_peak <= 0:
        raise RuntimeError("SV-1 fixed LF reference normalization failed")
    source = np.asarray(opening * envelope * (e13.SOURCE_PEAK_M3_S / ref_peak),
                        dtype=np.float64)
    # Exact initial phase, monotonic control, single envelope, no interior restart.
    ramp = round(0.01 * SAMPLE_RATE)
    if (source.shape != (count,) or not np.isfinite(source).all()
            or cycles[0] != 0 or np.any(np.diff(cycles) <= 0)
            or abs(cycles[-1] - (count - 1) * F0_HZ / SAMPLE_RATE) > 1e-8
            or not np.all(envelope[ramp:-ramp] == 1.0)
            or not np.any(np.abs(source[ramp:-ramp]) > 0)):
        raise RuntimeError("SV-1 source continuity / sustain numeric gate failed")
    return source, cycles, envelope


def _render(exp: object, geometry: object, source: np.ndarray) -> np.ndarray:
    # Adopted Experiment023's constant-geometry use of Exp012 frame_render.
    # Fresh acoustic pressure, not a modified WAV or pre-rendered fixture.
    pressure = np.asarray(exp.EXP26.EXP23.render_static(source, geometry), dtype=np.float64)
    if (pressure.shape != source.shape or not np.isfinite(pressure).all()
            or not np.any(np.abs(pressure) > 0)):
        raise RuntimeError("SV-1 raw physical pressure invalid")
    return pressure


def _assert_wav(blob: bytes, frames: int) -> bytes:
    with wave.open(io.BytesIO(blob), "rb") as handle:
        if (handle.getnchannels() != 1 or handle.getsampwidth() != 2
                or handle.getframerate() != SAMPLE_RATE
                or handle.getcomptype() != "NONE"
                or handle.getnframes() != frames):
            raise RuntimeError("SV-1 WAV format / length invalid")
        pcm = handle.readframes(frames)
    if len(pcm) != frames * 2:
        raise RuntimeError("SV-1 WAV payload truncated")
    if np.max(np.abs(np.frombuffer(pcm, dtype="<i2").astype(np.int32))) > 32767:
        raise RuntimeError("SV-1 WAV clipping")
    return pcm


def _diagnostic_concat(first_pcm: bytes, second_pcm: bytes) -> bytes:
    """Splice two separately rendered 0.25s WAV payloads; NOT one physical run."""
    if len(first_pcm) != 24_000 or len(second_pcm) != 24_000:
        raise ValueError("two separately computed 12k-sample PCM payloads required")
    out = io.BytesIO()
    with wave.open(out, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(first_pcm + second_pcm)
    _assert_wav(out.getvalue(), 24_000)
    return out.getvalue()


def _npy(array: np.ndarray) -> bytes:
    stream = io.BytesIO()
    np.save(stream, np.asarray(array, dtype="<f8"), allow_pickle=False)
    return stream.getvalue()


def _trace(cycles: np.ndarray, envelope: np.ndarray, geometry: object) -> bytes:
    """Coarse observational trace; 10ms intervals, final frame endpoint marker."""
    import csv
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["sample_index", "time_s", "phase_cycles", "source_gain",
                     "min_area_m2", "max_area_m2"])
    areas = np.array([s.area_m2 for s in geometry.sections])
    # The 10 ms sampling grid ends at the START of the final 10 ms fade.
    # Always include the actual last audio sample to audit file-off decay.
    indices = list(range(0, len(cycles), 480))
    if not indices or indices[-1] != len(cycles) - 1:
        indices.append(len(cycles) - 1)
    for i in indices:
        writer.writerow([i, format(i / SAMPLE_RATE, ".5f"),
                         format(float(cycles[i]), ".17g"),
                         format(float(envelope[i]), ".17g"),
                         format(float(np.min(areas)), ".17g"),
                         format(float(np.max(areas)), ".17g")])
    return stream.getvalue().encode("utf-8")


def _write_at(root_fd: int, relative_name: str, data: bytes) -> None:
    """Exclusive no-follow file write beneath an already opened directory inode.

    Unlike Path.write_bytes on a name, this is resistant to a parent-directory
    rename-and-symlink swap by another local process after mkdir.
    """
    if not isinstance(data, bytes):
        raise TypeError("SV-1 payload must be bytes")
    components = relative_name.split("/")
    if (not components or any(p in {"", ".", ".."} or "\\" in p
                              for p in components)):
        raise ValueError("SV-1 illegal relative artifact path")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    current = root_fd
    opened: list[int] = []
    try:
        for name in components[:-1]:
            try:
                os.mkdir(name, mode=0o700, dir_fd=current)
            except FileExistsError:
                pass
            child_fd = os.open(name, flags, dir_fd=current)
            opened.append(child_fd)
            current = child_fd
        file_fd = os.open(
            components[-1],
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            mode=0o600, dir_fd=current,
        )
        with os.fdopen(file_fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        for fd in reversed(opened):
            os.close(fd)


def _fsync_evidence_directories(root_fd: int, relative_names: tuple[str, ...]) -> None:
    """Persist nested file directory entries before manifest publication.

    fsync(file) alone guarantees content, not persistence of the directory
    entry naming the file. Every nested parent is fsynced deepest-first,
    followed by the root in _publish_new_bundle. No path follows symlinks.
    """
    parents = {
        tuple(name.split("/")[:depth])
        for name in relative_names
        for depth in range(1, len(name.split("/")))
    }
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    for parts in sorted(parents, key=lambda p: (-len(p), p)):
        directory_fd = os.dup(root_fd)
        try:
            for component in parts:
                next_fd = os.open(component, flags, dir_fd=directory_fd)
                os.close(directory_fd)
                directory_fd = next_fd
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)


def _publish_new_bundle(output_dir: Path, files: dict[str, bytes],
                        manifest: dict) -> None:
    """Reserve new output, anchor ALL writes to fd, publish complete marker last."""
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise RuntimeError("SV-1 requires Linux/POSIX no-follow directory fd")
    output_dir.mkdir(mode=0o700)
    root_fd = os.open(
        output_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    )
    try:
        for name, contents in sorted(files.items()):
            _write_at(root_fd, name, contents)
        # Before exposing a completed bundle, all nested directory entries
        # must be durable too (review P2; file fsync cannot do this).
        _fsync_evidence_directories(root_fd, tuple(sorted(files)))
        os.fsync(root_fd)
        # Refuse a swapped output directory even if its replacement is another
        # real directory (a symlink replacement was refused by O_NOFOLLOW).
        actual = os.stat(output_dir, follow_symlinks=False)
        held = os.fstat(root_fd)
        if (actual.st_dev, actual.st_ino) != (held.st_dev, held.st_ino):
            raise RuntimeError("SV-1 output directory was swapped during generation")
        # Staged manifest file has been fully flushed and fsynced before its
        # hard-link becomes the atomic completion marker; never overwrite it.
        _write_at(root_fd, ".manifest.staged",
                  canonical_bytes(manifest) + b"\n")
        os.link(".manifest.staged", "manifest.json",
                src_dir_fd=root_fd, dst_dir_fd=root_fd,
                follow_symlinks=False)
        os.unlink(".manifest.staged", dir_fd=root_fd)
        os.fsync(root_fd)
    finally:
        os.close(root_fd)


def perform(
    output_dir: Path,
    *,
    vowel: str = "a",
    preset_id: str = PRESET_ID,
    revision: int = PRESET_REVISION,
    durations: tuple[float, float] = DURATIONS,
) -> dict:
    """Build a new, bounded SV-1 evidence bundle; never overwrite any output."""
    if (vowel != "a" or preset_id != PRESET_ID
            or type(revision) is not int or revision != PRESET_REVISION
            or durations != DURATIONS):
        raise ValueError("UNSUPPORTED SV-1 vowel, body, revision, or durations")
    output_dir = Path(output_dir)
    if os.path.lexists(output_dir):
        raise FileExistsError("SV-1 output directory must not already exist")
    if not output_dir.parent.is_dir():
        raise FileNotFoundError("SV-1 output parent must already exist")
    frozen, exp, resolution = _validated_context()
    geometry = resolution.preset.prepared.rest_state
    e13 = exp.EXP26.EXP23.EXP13

    payloads: dict[str, bytes] = {}
    entries: dict[str, dict] = {}
    for letter, duration in (("A", DURATIONS[0]), ("B", DURATIONS[1])):
        source, cycles, envelope = _source_for_duration(exp, duration)
        # The 0.5s LF source must be *exactly* the inherited audited baseline,
        # but the physical pressure is newly computed for frozen static /a/.
        if letter == "B":
            baseline = e13.build_sources()[0]["lf_fixed"].source
            if not np.array_equal(source, baseline):
                raise RuntimeError("SV-1 0.5s source differs from audited LF baseline")
        pressure = _render(exp, geometry, source)
        wav = frozen._wav_bytes(pressure)
        pcm = _assert_wav(wav, len(source))
        payloads[f"{letter}_listen.wav"] = wav
        payloads[f"{letter}_source_flow.npy"] = _npy(source)
        payloads[f"{letter}_raw_pressure_pa.npy"] = _npy(pressure)
        payloads[f"{letter}_trace.csv"] = _trace(cycles, envelope, geometry)
        entries[letter] = {
            "kind": "FRESH_SINGLE_SOURCE_SINGLE_ACOUSTIC_RUN",
            "vowel": "/a/-like", "duration_seconds": duration,
            "frames": int(round(duration * SAMPLE_RATE)),
            "nominal_source_cycles": int(duration * F0_HZ),
            "steady_envelope_interval_seconds": [0.01, duration - 0.01],
            "source_sha256_f64": digest(source.astype("<f8").tobytes()),
            "pressure_sha256_f64": digest(pressure.astype("<f8").tobytes()),
            "raw_pressure_rms_pa": float(np.sqrt(np.mean(pressure * pressure))),
            "wav_pcm_sha256": digest(pcm),
        }

    # Window inside common steady state (no comparison of file-end ramp).
    a_source = np.load(io.BytesIO(payloads["A_source_flow.npy"]), allow_pickle=False)
    b_source = np.load(io.BytesIO(payloads["B_source_flow.npy"]), allow_pickle=False)
    if not np.array_equal(a_source[2400:7200], b_source[2400:7200]):
        raise RuntimeError("SV-1 equal-time, equal-phase source ablation failed")

    # Diagnostic C splices two INDEPENDENT 0.25s physical executions, never
    # a single continuous physical run. Each component is retained for audit.
    # Determinism means component bytes should be identical; check rather than
    # quietly substituting a reused A buffer.
    a_pcm = _assert_wav(payloads["A_listen.wav"], 12_000)
    c2_source, c2_cycles, c2_envelope = _source_for_duration(exp, DURATIONS[0])
    c2_pressure = _render(exp, geometry, c2_source)  # actual second fresh render
    c2_wav = frozen._wav_bytes(c2_pressure)
    c2_pcm = _assert_wav(c2_wav, 12_000)
    if (c2_pcm != a_pcm
            or digest(c2_source.astype("<f8").tobytes()) != entries["A"]["source_sha256_f64"]
            or digest(c2_pressure.astype("<f8").tobytes()) != entries["A"]["pressure_sha256_f64"]):
        raise RuntimeError("SV-1 C component fresh-repeat determinism failed")
    payloads["C_second_source_flow.npy"] = _npy(c2_source)
    payloads["C_second_raw_pressure_pa.npy"] = _npy(c2_pressure)
    payloads["C_second_listen.wav"] = c2_wav
    payloads["C_second_trace.csv"] = _trace(c2_cycles, c2_envelope, geometry)
    diagnostic = _diagnostic_concat(a_pcm, c2_pcm)
    payloads["C_concat_DIAGNOSTIC.wav"] = diagnostic
    payloads["listening/blind/trial_01.wav"] = payloads["B_listen.wav"]
    payloads["listening/blind/trial_02.wav"] = diagnostic
    payloads["listening/blind/trial_03.wav"] = payloads["A_listen.wav"]
    payloads["listening/ANSWER_KEY_OPEN_AFTER_RESPONSE.json"] = canonical_bytes({
        "trial_01": "B; 0.50s fresh physical single sustain",
        "trial_02": "C; 2 separately completed 0.25s files concatenated; DIAGNOSTIC",
        "trial_03": "A; 0.25s fresh physical single sustain",
    }) + b"\n"
    payloads["listening/READ_FIRST.md"] = (
        "Listen only to files in blind/ in order or random order, without reading "
        "ANSWER_KEY_OPEN_AFTER_RESPONSE.json. Before opening the key, write your "
        "free Japanese transcription, whether each sounds like one sustained or "
        "two distinct phonation starts (or unknown), discontinuity/buzziness, "
        "naturalness, and creator usefulness. Single-listener pilot only.\n"
    ).encode()

    manifest = {
        "schema": "sv1-research/v1",
        "status": OUTCOME,
        "claim_limit": "fixed /a/-like 1D tube with imposed LF source; not respiratory/biomechanical sustain, not natural Japanese",
        "body": {
            "preset_id": PRESET_ID, "revision": PRESET_REVISION,
            "preparation_digest": resolution.snapshot.preparation_digest,
            "backend": resolution.snapshot.backend_id,
            "total_length_m": geometry.total_length_m,
            "static_a_rest_peak_hz": list(STATIC_A_PEAKS_HZ),
            "peak_oracle_source": "adopted Experiment028 independent Wolfram static M0 /a/ rest",
        },
        "source": {
            "family": "Experiment013 lf_fixed-duration-generalized",
            "f0_hz": F0_HZ, "rd": 1.0, "seed": 0,
            "ramp_seconds": 0.01, "sample_rate_hz": SAMPLE_RATE,
            "historical_half_second_source_exact": True,
        },
        "renderer": "Experiment023 render_static -> Experiment012 frame_render, hop=256, Hann=1024, preroll_edge",
        "program": "SV1 single static /a/-like hold; source on and off per file; no articulator state integration",
        "stimuli": entries,
        "C": {
            "kind": "DIAGNOSTIC_NOT_SINGLE_PHYSICAL_RUN",
            "frames": 24_000,
            "construction": "PCM concatenation of two independently generated 0.25s physical A-like files (A and C_second), never a joined physical trajectory",
            "component_first_pressure_sha256_f64": entries["A"]["pressure_sha256_f64"],
            "component_second_pressure_sha256_f64": digest(c2_pressure.astype("<f8").tobytes()),
            "separate_acoustic_run_count": 2,
            "is_accepted_physical_take": False,
        },
        "listening_gate": "NOT_RUN_CREATOR_LISTENING_PENDING",
        "independent_review": "PENDING",
        "code_sha256": digest(Path(__file__).read_bytes()),
        "numpy_version": np.__version__,
        "artifact_sha256": {name: digest(data) for name, data in sorted(payloads.items())},
    }

    # The payload and atomic manifest completion marker are always written
    # relative to the directory inode opened with O_NOFOLLOW; never truncate
    # an existing file after a path-based symlink swap.
    _publish_new_bundle(output_dir, payloads, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = perform(args.output_dir)
    print(json.dumps({
        "status": result["status"], "manifest": str(args.output_dir / "manifest.json"),
        "A_frames": result["stimuli"]["A"]["frames"],
        "B_frames": result["stimuli"]["B"]["frames"],
        "listening_gate": result["listening_gate"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
