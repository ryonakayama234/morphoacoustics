"""Deterministic VQ-1 G0-P research receipt. Does not generate sound.

Run under checkout with package installed:
  python experiments/054_vq1_g0_port/run.py --out vq1-g0-evidence.json
"""
from __future__ import annotations

import argparse
import json
from math import sin
from pathlib import Path
import traceback

from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics_waveguide import PassiveWaveguideConfig, PassiveWaveguideSession
from port import FixedWaveguideInletPort, StalePortSnapshot


def run() -> dict:
    results = []
    for name, lengths, areas, termination in (
        ("single_matched", 0.01, (0.0008,), "matched"),
        ("two_sections_b0", 0.01, (0.0008, 0.0004), "b0"),
        ("m0_surrogate", 0.01, (0.0008,) * 16, "closed"),
        ("m1_surrogate", 0.011, (0.0008,) * 16, "pressure_release"),
    ):
        geometry = Tract1DGeometry(
            cavity_id="oral",
            sections=tuple(TubeSection(length_m=lengths, area_m2=a) for a in areas),
        )
        config = PassiveWaveguideConfig(geometry, termination=termination)
        session = PassiveWaveguideSession(config)
        port = FixedWaveguideInletPort(session)
        observations = []
        max_pressure_residual_pa = 0.0
        max_energy_residual_j = 0.0
        max_scaled_pressure_error = 0.0
        max_scaled_energy_error = 0.0
        nonzero_b_ticks = 0
        nonzero_energy_ticks = 0
        for tick in range(128):
            snapshot = port.snapshot()
            u = 1e-6 * sin(0.17 * (tick + 1)) if tick < 64 else 0.0
            # Oracle reconstructs source boundary directly from physical
            # incident wave, geometry and signed volume flow.
            zin = config.air_density_kg_m3 * config.sound_speed_m_s / areas[0]
            incident = session.backward[0][0]
            p_ref = incident + (incident + zin * u)
            before = sum(session.energies_j())
            before_tick = session.ticks
            before_state = (
                tuple(tuple(q) for q in session.forward),
                tuple(tuple(q) for q in session.backward),
                None if session._radiation is None else session._radiation.q,
            )
            pred = port.peek(snapshot, u)
            assert session.ticks == before_tick
            assert before_state == (
                tuple(tuple(q) for q in session.forward),
                tuple(tuple(q) for q in session.backward),
                None if session._radiation is None else session._radiation.q,
            )
            obs = port.commit_once(snapshot, u)
            after = sum(session.energies_j())
            if obs.tick != tick:
                raise AssertionError("clock / commit mismatch")
            try:
                port.peek(snapshot, 0.0)
            except StalePortSnapshot:
                pass
            else:
                raise AssertionError("duplicate snapshot reused after commit")
            pressure_error = abs(p_ref - obs.source_pressure_pa)
            pressure_scaled = pressure_error / max(
                abs(2.0 * incident) + abs(zin * u), 1.0
            )
            residual = (after - before) - obs.source_work_j + obs.outlet_dissipation_j
            energy_scaled = abs(residual) / max(
                abs(after - before) + abs(obs.source_work_j)
                + abs(obs.outlet_dissipation_j), 1e-12
            )
            max_pressure_residual_pa = max(max_pressure_residual_pa, pressure_error)
            max_energy_residual_j = max(max_energy_residual_j, abs(residual))
            max_scaled_pressure_error = max(max_scaled_pressure_error, pressure_scaled)
            max_scaled_energy_error = max(max_scaled_energy_error, energy_scaled)
            nonzero_b_ticks += int(abs(incident) > 1e-9)
            nonzero_energy_ticks += int(after > 1e-14)
            if pressure_scaled > 1e-10 or energy_scaled > 1e-10:
                raise AssertionError(f"port oracle or energy failure {name} at tick={tick}")
            if tick in (0, 1, 2, 32, 64, 127):
                observations.append({
                    "tick": tick,
                    "incoming_b_pa": incident,
                    "flow_m3_s": u,
                    "predicted_pressure_pa": pred.pressure_pa,
                    "actual_pressure_pa": obs.source_pressure_pa,
                    "source_work_j": obs.source_work_j,
                    "signed_energy_residual_j": residual,
                    "duct_energy_j": obs.duct_energy_j,
                    "radiation_energy_j": obs.radiation_energy_j,
                    "outlet_loss_j": obs.outlet_dissipation_j,
                })
        if not nonzero_b_ticks or not nonzero_energy_ticks:
            raise AssertionError(f"UNINFORMATIVE_FIXTURE {name}: no reflected wave or energy")
        results.append({
            "fixture": name,
            "geometry": "uniform-length serial duct",
            "section_count": len(areas),
            "section_length_m": lengths,
            "areas_m2": list(areas),
            "termination": termination,
            "native_dt_s": config.timestep_s,
            "native_clock_hz": config.physics_clock_hz,
            "ticks": session.ticks,
            "nonzero_b_ticks": nonzero_b_ticks,
            "nonzero_energy_ticks": nonzero_energy_ticks,
            "max_pressure_residual_pa": max_pressure_residual_pa,
            "max_energy_residual_j": max_energy_residual_j,
            "max_scaled_pressure_error": max_scaled_pressure_error,
            "max_scaled_energy_error": max_scaled_energy_error,
            "samples": observations,
        })
    return {
        "scope": "VQ-1 G0-P only; exact Core native tick; NO tissue or voice",
        "outcome": "GO_NUMERIC_PORT_CANDIDATE",
        "not_a_claim": ["independent physiological reference", "phonation", "voice quality", "Studio GO"],
        "fixtures": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    receipt = {"outcome": "NUMERICALLY_UNRESOLVED"}
    failure = None
    try:
        receipt = run()
    except Exception:
        failure = traceback.format_exc()
        receipt = {"outcome": "NUMERICALLY_UNRESOLVED", "failure": failure}
    finally:
        arguments.out.write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"outcome": receipt["outcome"], "path": str(arguments.out)}))
    if failure is not None:
        raise RuntimeError(failure)
