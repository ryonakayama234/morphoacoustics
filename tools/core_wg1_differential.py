"""CORE-WG-1: differential *software* audit against pinned B2-A research source.

Do not confuse exact source equivalence with an independent physical oracle;
the B2-A scientific oracle/energy evidence lives in PR #184. This file
executes both source trees on identical verified prepared M0/M1 fixtures.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from morphoacoustics_waveguide import (
    PassiveWaveguideConfig,
    PassiveWaveguideSession,
)

REFERENCE_SHA = "49d56f581036286e534e14835bede895a06327d6"


def verify_archival_source(reference_root: Path) -> str:
    """Fail closed on wrong revision, local edits and added source files.

    Identity must be checked before importing archival Python code, since
    importing it may legitimately create ignored bytecode caches.
    """
    root = reference_root.resolve()
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("archival B2-A reference is not a verifiable git checkout") from exc
    if head != REFERENCE_SHA:
        raise RuntimeError(f"archival B2-A reference revision mismatch: {head}")
    if dirty:
        raise RuntimeError("archival B2-A reference has modified or untracked files")
    return head


def run(reference_root: Path) -> dict[str, object]:
    verified_reference_sha = verify_archival_source(reference_root)
    src = reference_root / "experiments" / "053_b2a_static_multisection" / "run.py"
    if not src.is_file():
        raise FileNotFoundError("the pinned B2-A source checkout is missing")
    spec = importlib.util.spec_from_file_location("core_wg1_pinned_b2a", src)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load pinned B2-A source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # B2-A resolves authentic fixed CC-A2 prepared M0/M1 through the original
    # registry AND checks their exact frozen Experiment-028 area/length data.
    bodies = module.prepared_bodies()
    counts = {"cases": 0, "ticks": 0, "wave_cells_compared": 0}
    rng = np.random.default_rng(20261025)
    for name in ("M0", "M1"):
        original = bodies[name]
        for n in (2, 4, 8):
            for term in ("closed", "pressure_release", "matched", "b0"):
                for nonzero_initial in (False, True):
                    config = module.config_for(original, n=n, term=term)
                    physical = PassiveWaveguideConfig(
                        geometry=original["geometry"],
                        cells_per_section=n,
                        termination=term,
                        air_density_kg_m3=config.rho,
                        sound_speed_m_s=config.c,
                    )
                    np.testing.assert_allclose(physical.physics_clock_hz, config.fs,
                                               rtol=1e-13, atol=0)
                    shape = (16, n)
                    forward = (
                        rng.normal(0.0, 0.03, shape)
                        if nonzero_initial else np.zeros(shape)
                    )
                    backward = (
                        rng.normal(0.0, 0.03, shape)
                        if nonzero_initial else np.zeros(shape)
                    )
                    q = (1e-10 if nonzero_initial and term == "b0" else 0.0)
                    reference = module.StaticMultisection(
                        config, forward=forward, backward=backward, initial_q=q
                    )
                    subject = PassiveWaveguideSession(
                        physical,
                        initial_forward_pa=tuple(tuple(float(v) for v in row) for row in forward),
                        initial_backward_pa=tuple(tuple(float(v) for v in row) for row in backward),
                        initial_b0_q_m3_s=q,
                    )
                    drive = rng.normal(0, 1e-8, 48)
                    drive[24:] = 0.0
                    for value in drive:
                        ref_step = reference.step(float(value))
                        step = subject.step(float(value))
                        ref_columns = (
                            ref_step.tick, ref_step.inlet_flow, ref_step.p_source,
                            ref_step.p_mouth, ref_step.U_mouth,
                            ref_step.E_duct, ref_step.E_B0, ref_step.W_source,
                            ref_step.D_terminal, ref_step.delta_E,
                            ref_step.residual,
                        )
                        new_columns = (
                            step.tick, step.inlet_flow_m3_s, step.source_pressure_pa,
                            step.mouth_pressure_pa, step.mouth_flow_m3_s,
                            step.duct_energy_j, step.radiation_energy_j,
                            step.source_work_j, step.outlet_dissipation_j,
                            step.delta_stored_energy_j, step.energy_residual_j,
                        )
                        np.testing.assert_allclose(
                            new_columns, ref_columns, rtol=1e-12, atol=1e-18,
                            err_msg=f"body={name}, cells={n}, term={term}"
                        )
                        for lhs, rhs in (
                            (reference.f, subject.forward),
                            (reference.b, subject.backward),
                        ):
                            np.testing.assert_allclose(
                                np.array([list(qx) for qx in lhs]),
                                np.array([list(qx) for qx in rhs]),
                                rtol=1e-12, atol=1e-18,
                                err_msg=f"wave state: {name}, n={n}, term={term}",
                            )
                            counts["wave_cells_compared"] += 16 * n
                        if term == "b0":
                            np.testing.assert_allclose(
                                subject._radiation.q, reference.port.q_m3_s,
                                rtol=1e-12, atol=1e-18,
                            )
                        counts["ticks"] += 1
                    counts["cases"] += 1
    return {
        "reference_exact_sha": verified_reference_sha,
        "subject": "CORE-WG-1 branch under workflow checkout",
        "bodies": ["M0", "M1"],
        "cells_per_section": [2, 4, 8],
        "terminations": ["closed", "pressure_release", "matched", "b0"],
        "initial_state": ["zero", "nonzero signed waves and B0 q"],
        "counts": counts,
        "status": "SOURCE_EQUIVALENCE_PASS",
        "limitations": (
            "Software differential only; independent physical energy/continuum oracle",
            "was previously tested on B2-A source; no B2-B or voice proof.",
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run(args.reference_root)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
