"""R0 operations wrapper for the unchanged NV1 W0/W1 research fixture.

No synthesis law, preset, normalization, or scientific decision is added here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import zipfile


PIN = "0cffbc29cec4a07c93f60e45084c0e45bde4c058"
EXPERIMENT = "experiments/042_nv1_breath_ear"
SOURCE_HASHES = {
    f"{EXPERIMENT}/run.py": "a3378b011da60a0a6ea3fb988059843938c4d6e6ace9b7229ef982688e437bf7",
    f"{EXPERIMENT}/source.py": "7fe3cd406f132259d739878e32458d900b5a4599da81f5e9fa54a37a1b51571a",
}
VERSIONS = {"numpy": "2.3.5", "scipy": "1.17.0", "soundfile": "0.13.1"}
PRESETS = {"P0": (120.0, 30e-6), "P2": (240.0, 30e-6),
           "A2": (120.0, 60e-6), "Z0": (0.0, 30e-6)}
SCHEMA = "morpho-r0-breath-replay/1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                               sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def environment(destination: Path) -> dict:
    versions = {}
    for name in VERSIONS:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    memory = None
    if hasattr(os, "sysconf"):
        try:
            memory = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        except (OSError, ValueError):
            pass
    # Capacity figures are observations, not a claim about an allocated VM quota.
    return {"python": platform.python_version(), "platform": platform.system(),
            "machine": platform.machine(), "logical_cpu_count": os.cpu_count(),
            "host_memory_bytes": memory,
            "destination_disk_free_bytes": shutil.disk_usage(destination).free,
            "packages": versions, "gpu": "NOT_PROBED_CPU_ONLY_JOB",
            "vm_quota_and_lifetime": "OWNER_OR_MUSE_TO_CONFIRM"}


def qualified_source(root: Path) -> dict:
    for name, expected in SOURCE_HASHES.items():
        path = root / name
        if not path.is_file() or path.is_symlink() or digest(path) != expected:
            raise ValueError(f"Pinned source bytes differ: {name}")
    def git(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(root), *args],
                                       text=True, stderr=subprocess.PIPE).strip()
    if Path(git("rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("source-root must be the checkout root")
    head = git("rev-parse", "HEAD")
    dirty = git("status", "--porcelain", "--untracked-files=normal")
    if head != PIN or dirty:
        raise ValueError("Source checkout must be clean at the documented pin")
    return {"expected_pin": PIN, "observed_git_head": head, "git_dirty": False,
            "source_sha256": SOURCE_HASHES}


def safe_file(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Artifact path must remain within its output directory")
    full = root / path
    if full.is_symlink() or not full.is_file() or not full.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Missing or unsafe artifact: {relative}")
    return full


def inspect_render(render: Path) -> tuple[list[dict], dict]:
    import numpy as np
    import soundfile as sf

    evidence = json.loads(safe_file(render, "evidence.json").read_text(encoding="utf-8"))
    expected = {"schema": "nv1-breath-ear.evidence.v0", "claim": "EXPERIMENTAL_NOT_ADOPTED",
                "scope": "W0_W1_IDEAL_A_ONLY", "rate_hz": 48000, "seed": 133041,
                "playback_gain": 70.0, "receiver_units": "modeled_Pa"}
    for key, value in expected.items():
        if evidence.get(key) != value:
            raise ValueError(f"Unexpected upstream evidence field: {key}")
    if set(evidence["cases"]) != set(PRESETS):
        raise ValueError("Expected the existing four cases only")
    rows, traces = [], {}
    for name, (pressure, area) in PRESETS.items():
        item = evidence["cases"][name]
        if item["pressure_peak_pa"] != pressure or item["effective_aperture_m2"] != area:
            raise ValueError(f"Preset changed: {name}")
        for kind in ("wav", "trace"):
            path = safe_file(render, item[kind])
            if digest(path) != item[kind + "_sha256"]:
                raise ValueError(f"Artifact digest differs: {name} {kind}")
        with np.load(render / item["trace"], allow_pickle=False) as data:
            arrays = {key: data[key] for key in data.files}
        needed = ("pressure_pa", "aperture_m2", "q_mean_m3_s", "q_ac_m3_s",
                  "receiver_raw_A_pa")
        if any(key not in arrays for key in needed):
            raise ValueError(f"Missing physical arrays: {name}")
        if any(not np.isfinite(x).all() for x in arrays.values()):
            raise ValueError(f"Nonfinite physical trace: {name}")
        if any(arrays[key].shape != (115200,) for key in needed[:-1]):
            raise ValueError(f"Unexpected source length: {name}")
        if not np.all(arrays["aperture_m2"] == area):
            raise ValueError(f"Aperture trace differs: {name}")
        source_hash = hashlib.sha256(arrays["q_ac_m3_s"].astype("<f8").tobytes()).hexdigest()
        if source_hash != item["source_sha256"]:
            raise ValueError(f"Source digest differs: {name}")
        info = sf.info(render / item["wav"])
        wave, rate = sf.read(render / item["wav"], always_2d=True)
        raw = arrays["receiver_raw_A_pa"]
        if (rate != 48000 or info.subtype != "PCM_24" or wave.shape[1] != 2
                or wave.shape != raw.shape or not np.isfinite(wave).all()
                or np.max(np.abs(wave)) > .95):
            raise ValueError(f"Invalid stereo PCM24 output: {name}")
        if not np.allclose(wave, 70.0 * raw, atol=2**-23 + 1e-12, rtol=0):
            raise ValueError(f"WAV no longer represents the disclosed fixed gain: {name}")
        if name == "Z0":
            if any(np.any(arrays[key]) for key in ("pressure_pa", "q_mean_m3_s", "q_ac_m3_s", "receiver_raw_A_pa")) or np.any(wave):
                raise ValueError("Zero drive is not silent")
        elif not np.any(wave):
            raise ValueError(f"Unexpected silent driven condition: {name}")
        efficiency = item["ideal_monopole_efficiency"]
        if not np.isfinite(efficiency) or not 0 <= efficiency <= .01:
            raise ValueError(f"Invalid reported power ratio: {name}")
        rows.append({"case": name, "pressure_peak_pa": pressure, "aperture_m2": area,
                     "flow_peak_l_s": float(np.max(arrays["q_mean_m3_s"])) * 1000,
                     "source_sha256": source_hash, "wav": "render/" + item["wav"],
                     "duration_s": len(wave) / rate, "wav_peak": float(np.max(np.abs(wave))),
                     "power_ratio_reported": efficiency})
        traces[name] = arrays
    return rows, traces


def plot_svg(traces: dict) -> str:
    import numpy as np

    colors = {"P0": "#2563eb", "P2": "#dc2626", "A2": "#059669", "Z0": "#64748b"}
    panels = [("q_mean_m3_s", 1000, "Mean flow (L/s)"),
              ("q_ac_m3_s", 1e6, "Equivalent acoustic source (mL/s)"),
              ("receiver_raw_A_pa", 1, "Ideal receiver L (modeled Pa)")]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="790" viewBox="0 0 1000 790">',
             '<rect width="1000" height="790" fill="white"/>',
             '<g font-family="sans-serif" font-size="14" fill="#172033">',
             '<text x="45" y="30">R0 / existing W0-W1 fixture / uncalibrated research model</text>',
             '<text x="45" y="55">P0 blue / P2 red / A2 green / Z0 gray; sampled traces, no smoothing</text>']
    for panel, (key, scale, title) in enumerate(panels):
        y0 = 105 + panel * 220
        values = {}
        for case, trace in traces.items():
            x = trace[key]
            values[case] = (x[:, 0] if x.ndim == 2 else x) * scale
        low = min(float(x.min()) for x in values.values())
        high = max(float(x.max()) for x in values.values())
        span = high - low or 1
        parts += [f'<text x="45" y="{y0-12}">{title}; range [{low:.5g}, {high:.5g}]</text>',
                  f'<path d="M 65 {y0} V {y0+160} H 955" fill="none" stroke="#94a3b8"/>']
        duration = 0.0
        for case, vals in values.items():
            idx = np.unique(np.linspace(0, len(vals)-1, min(600, len(vals))).astype(int))
            duration = max(duration, (len(vals)-1)/48000)
            points = " ".join(f"{65+890*i/(len(vals)-1):.2f},{y0+160-160*(vals[i]-low)/span:.2f}" for i in idx)
            parts.append(f'<polyline points="{points}" fill="none" stroke="{colors[case]}" stroke-width="1"/>')
        parts += [f'<text x="65" y="{y0+185}">0 s</text>',
                  f'<text x="875" y="{y0+185}">{duration:.4f} s</text>']
    parts.append('<text x="45" y="770">Not calibrated SPL, human-breath validation, or a naturalness score.</text></g></svg>')
    return "\n".join(parts) + "\n"


def verify(output: Path) -> dict:
    completed = json.loads(safe_file(output, "complete.json").read_text(encoding="utf-8"))
    if (completed.get("schema") != SCHEMA or completed.get("expected_source_pin") != PIN
            or not completed.get("files")):
        raise ValueError("Completion record does not identify this replay")
    for relative, expected in completed["files"].items():
        if digest(safe_file(output, relative)) != expected:
            raise ValueError(f"Saved replay file changed: {relative}")
    receipt = json.loads(safe_file(output, "operation.json").read_text(encoding="utf-8"))
    source = receipt["source"]
    if (source["expected_pin"] != PIN or source["observed_git_head"] != PIN
            or source["git_dirty"] is not False or source["source_sha256"] != SOURCE_HASHES):
        raise ValueError("Recorded source provenance differs")
    rows, _ = inspect_render(output / "render")
    upstream = json.loads((output / "render/evidence.json").read_text(encoding="utf-8"))
    if upstream["core_commit_sha"] != PIN or upstream["git_dirty"] is not False:
        raise ValueError("Upstream did not record the clean pinned source")
    return {"status": "ARTIFACT_CHECKS_PASSED", "cases": [x["case"] for x in rows],
            "scientific_adoption": "NOT_ASSESSED", "naturalness": "NOT_ASSESSED"}


def run(source_root: Path, output: Path, timeout: float = 120) -> dict:
    source_root, output = source_root.resolve(), output.resolve()
    if timeout <= 0:
        raise ValueError("Timeout must be positive")
    if output.exists() or not output.parent.is_dir() or output.is_relative_to(source_root):
        raise ValueError("Use a new output directory outside the source checkout, with an existing parent")
    provenance = qualified_source(source_root)
    env = environment(output.parent)
    if env["packages"] != VERSIONS:
        raise ValueError(f"Install the documented dependency versions first: {env['packages']}")
    output.mkdir()
    dump(output / "environment.json", env)
    command = [sys.executable, str(source_root / EXPERIMENT / "run.py"), "--output", str(output / "render")]
    started = time.perf_counter()
    try:
        with (output / "stdout.txt").open("wb") as stdout, (output / "stderr.txt").open("wb") as stderr:
            subprocess.run(command, cwd=source_root, stdout=stdout, stderr=stderr,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                           check=True, timeout=timeout)
        if qualified_source(source_root) != provenance:
            raise ValueError("Source changed during execution")
        rows, traces = inspect_render(output / "render")
        dump(output / "operation.json", {"schema": SCHEMA, "source": provenance,
             "driver_sha256": digest(Path(__file__)), "command": command,
             "wall_time_seconds": time.perf_counter() - started,
             "memory_peak": "NOT_MEASURED", "claim": "REPLAY_ONLY_NOT_ADOPTED"})
        dump(output / "summary.json", rows)
        csv_out = io.StringIO(newline="")
        writer = csv.DictWriter(csv_out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        (output / "summary.csv").write_text(csv_out.getvalue(), encoding="utf-8")
        (output / "traces.svg").write_text(plot_svg(traces), encoding="utf-8")
        files = {str(p.relative_to(output)): digest(p) for p in sorted(output.rglob("*")) if p.is_file()}
        dump(output / "complete.json", {"schema": SCHEMA, "expected_source_pin": PIN,
                                       "files": files, "output_bytes_before_completion": sum(p.stat().st_size for p in output.rglob("*") if p.is_file())})
        result = verify(output)
        with zipfile.ZipFile(output / "bundle.zip", "x", compression=zipfile.ZIP_DEFLATED) as bundle:
            for name in [*files, "complete.json"]:
                bundle.write(output / name, arcname=name)
        return {**result, "output": str(output), "bundle": str(output / "bundle.zip")}
    except Exception as exc:
        # Keep all partial files for diagnosis. Never resume or overwrite them.
        (output / "complete.json").unlink(missing_ok=True)
        dump(output / "failed.json", {"schema": SCHEMA, "error_type": type(exc).__name__,
              "message": str(exc), "wall_time_seconds": time.perf_counter() - started})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    probe = sub.add_parser("probe", help="Capacity observations, no synthesis or file writes")
    probe.add_argument("--destination", type=Path, default=Path.cwd())
    replay = sub.add_parser("run", help="Run the unchanged existing four-condition fixture")
    replay.add_argument("--source-root", required=True, type=Path)
    replay.add_argument("--output", required=True, type=Path)
    replay.add_argument("--timeout-seconds", type=float, default=120)
    check = sub.add_parser("verify", help="Check a returned, unzipped result bundle")
    check.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.action == "probe":
            result = environment(args.destination)
        elif args.action == "run":
            result = run(args.source_root, args.output, args.timeout_seconds)
        else:
            result = verify(args.output.resolve())
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "error_type": type(exc).__name__, "message": str(exc)},
                         ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
