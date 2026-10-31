"""Generate immutable-in-workflow research trace records; no audio synthesis."""
from __future__ import annotations
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import sys
from rigid_reference import RigidChannel, Fluid, solve_fixed_wall


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python run.py OUTPUT_DIRECTORY")
    target = Path(sys.argv[1])
    if target.exists():
        raise FileExistsError("refuse overwrite of previous experimental output")
    target.mkdir(parents=True, exist_ok=False)
    geom, fluid = RigidChannel(), Fluid()
    records = []
    for slope in (-.2, 0., .2):
        for pressure in (0., .1, .2, .4):
            for cells in (4, 8, 16, 32):
                cfg = replace(geom, taper_slope=slope)
                obs = solve_fixed_wall(cfg, fluid, pressure, cells)
                exact = (2 * cfg.width_m * cfg.half_gap_m**3 *
                         (1-slope**2)**2 * pressure /
                         (3 * fluid.viscosity_pa_s * cfg.length_m))
                records.append({"slope": slope, "pressure_pa": pressure,
                                "cells": cells, "geometry": asdict(cfg),
                                "fluid": asdict(fluid), "observation": asdict(obs),
                                "analytic_flow_m3_s": exact,
                                "relative_flow_error": None if pressure == 0
                                else abs(obs.volume_flow_m3_s/exact - 1)})
    payload = {"schema": "vf1b2-rigid-b0/v1", "claim": "low-Re rigid reference only",
               "code_sha": os.environ.get("GITHUB_SHA", "LOCAL_NOT_GITHUB_VERIFIED"),
               "g2_biophysics": "INDETERMINATE_NOT_VALIDATED",
               "g3_phonation": "NOT_APPLICABLE", "g4_creator": "NO_GO",
               "records": records}
    raw = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    path = target / "records.json"
    path.write_bytes(raw)
    (target / "sha256.txt").write_text(hashlib.sha256(raw).hexdigest() + "  records.json\n")
    print(json.dumps({"cases": len(records), "sha256": hashlib.sha256(raw).hexdigest(),
                      "max_taper_n32_relative_error": max(
                          r["relative_flow_error"] for r in records
                          if r["cells"] == 32 and r["slope"] != 0 and r["pressure_pa"] > 0
                      )}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
