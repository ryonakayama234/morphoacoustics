"""VQ-1 G0-P: deterministic signed SI evidence, including *failed* attempts.

No sound output. A failed physics check retains every earlier fixture and the
last attempted tick's predictor/actual values and snapshots rather than replacing
scientific data with only an exception traceback.
"""
from __future__ import annotations

import argparse
import json
import os
from math import sin
from pathlib import Path
import subprocess
import traceback

from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics_waveguide import PassiveWaveguideConfig, PassiveWaveguideSession
from port import FixedWaveguideInletPort, StalePortSnapshot


CASES = (
    ("single_matched", 0.01, (0.0008,), "matched"),
    ("two_sections_b0", 0.01, (0.0008, 0.0004), "b0"),
    ("m0_surrogate", 0.01, (0.0008,) * 16, "closed"),
    ("m1_surrogate", 0.011, (0.0008,) * 16, "pressure_release"),
)


def run(receipt: dict) -> None:
    """Mutate a retained evidence object; never hide completed/failed tick data."""
    for name, length, areas, termination in CASES:
        case = {
            "fixture": name,
            "status": "IN_PROGRESS",
            "geometry": "uniform-length serial duct",
            "section_count": len(areas),
            "section_length_m": length,
            "areas_m2": list(areas),
            "termination": termination,
            "samples": [],  # complete signed raw trace, one record per attempted tick
            "nonzero_b_ticks": 0,
            "nonzero_energy_ticks": 0,
            "max_pressure_residual_pa": 0.0,
            "max_energy_residual_j": 0.0,
            "max_scaled_pressure_error": 0.0,
            "max_scaled_energy_error": 0.0,
        }
        receipt["fixtures"].append(case)
        geometry = Tract1DGeometry(
            cavity_id="oral",
            sections=tuple(TubeSection(length_m=length, area_m2=a) for a in areas),
        )
        config = PassiveWaveguideConfig(geometry, termination=termination)
        if name == "single_matched":
            # Matched outlet has no returning reflection; seed nonzero incoming
            # first wave to exercise exact nonzero-b behavior at this boundary.
            session = PassiveWaveguideSession(
                config, initial_backward_pa=((0.25, 0.0),)
            )
        else:
            session = PassiveWaveguideSession(config)
        port = FixedWaveguideInletPort(session)
        case["native_dt_s"] = config.timestep_s
        case["native_clock_hz"] = config.physics_clock_hz
        for tick in range(128):
            snap = port.snapshot()
            u = 1e-6 * sin(0.17 * (tick + 1)) if tick < 64 else 0.0
            zin = config.air_density_kg_m3 * config.sound_speed_m_s / areas[0]
            incident = session.backward[0][0]
            p_ref = incident + (incident + zin * u)
            before_e = sum(session.energies_j())
            native_before = (
                tuple(tuple(q) for q in session.forward),
                tuple(tuple(q) for q in session.backward),
                None if session._radiation is None else session._radiation.q,
            )
            attempt = {
                "tick": tick,
                "pre_shift_snapshot_digest": snap.state_digest,
                "incoming_b_pa": incident,
                "flow_m3_s": u,
                "oracle_pressure_pa": p_ref,
                "before_stored_energy_j": before_e,
                "status": "ATTEMPTED",
            }
            case["samples"].append(attempt)  # survives ANY later exception
            case["failed_tick"] = tick
            try:
                pred = port.peek(snap, u)
                attempt["predicted_pressure_pa"] = pred.pressure_pa
                attempt["predicted_source_work_j"] = pred.source_work_j
                assert session.ticks == tick
                assert native_before == (
                    tuple(tuple(q) for q in session.forward),
                    tuple(tuple(q) for q in session.backward),
                    None if session._radiation is None else session._radiation.q,
                ), "peek unexpectedly mutated live Core state"
                obs = port.commit_once(snap, u)
                after_e = sum(session.energies_j())
                attempt.update({
                    "actual_pressure_pa": obs.source_pressure_pa,
                    "source_work_j": obs.source_work_j,
                    "delta_stored_energy_j": after_e - before_e,
                    "after_stored_energy_j": after_e,
                    "duct_energy_j": obs.duct_energy_j,
                    "radiation_energy_j": obs.radiation_energy_j,
                    "outlet_loss_j": obs.outlet_dissipation_j,
                    "post_shift_tick": session.ticks,
                    "post_shift_snapshot_digest": port.snapshot().state_digest,
                })
                assert obs.tick == tick, "wrong source tick"
                try:
                    port.peek(snap, 0.0)
                except StalePortSnapshot:
                    pass
                else:
                    raise AssertionError("old snapshot could be reused")
                error = abs(p_ref - obs.source_pressure_pa)
                scale_p = max(abs(2.0 * incident) + abs(zin * u), 1.0)
                pressure_scaled = error / scale_p
                signed_residual = (
                    (after_e - before_e) - obs.source_work_j
                    + obs.outlet_dissipation_j
                )
                scale_e = max(
                    abs(after_e - before_e) + abs(obs.source_work_j)
                    + abs(obs.outlet_dissipation_j), 1e-12
                )
                energy_scaled = abs(signed_residual) / scale_e
                attempt.update({
                    "pressure_error_pa": error,
                    "scaled_pressure_error": pressure_scaled,
                    "signed_energy_residual_j": signed_residual,
                    "scaled_energy_error": energy_scaled,
                })
                case["max_pressure_residual_pa"] = max(
                    case["max_pressure_residual_pa"], error
                )
                case["max_energy_residual_j"] = max(
                    case["max_energy_residual_j"], abs(signed_residual)
                )
                case["max_scaled_pressure_error"] = max(
                    case["max_scaled_pressure_error"], pressure_scaled
                )
                case["max_scaled_energy_error"] = max(
                    case["max_scaled_energy_error"], energy_scaled
                )
                case["nonzero_b_ticks"] += int(abs(incident) > 1e-9)
                case["nonzero_energy_ticks"] += int(after_e > 1e-14)
                if pressure_scaled > 1e-10 or energy_scaled > 1e-10:
                    raise AssertionError(
                        f"port or energy gate failed: {name}, tick={tick}"
                    )
                attempt["status"] = "NUMERIC_PASS"
            except Exception:
                attempt["status"] = "FAIL"
                attempt["failure"] = traceback.format_exc()
                raise
            finally:
                case["ticks_attempted"] = len(case["samples"])
        if not case["nonzero_b_ticks"] or not case["nonzero_energy_ticks"]:
            case["status"] = "UNINFORMATIVE_FIXTURE"
            raise AssertionError(f"uninformative reflection/energy fixture {name}")
        case["status"] = "NUMERIC_PASS"
        case.pop("failed_tick", None)
    receipt["outcome"] = "GO_NUMERIC_PORT_CANDIDATE"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    # Exact HEAD is part of the scientific receipt, not inferred from a PR URL.
    root = Path(__file__).resolve().parents[2]
    head = subprocess.check_output(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=root, text=True,
    ).strip()
    tests_outcome = os.environ.get("VQ1_TEST_OUTCOME", "not_verified")
    receipt = {
        "scope": "G0 discrete acoustics only; NO tissue, voice or Studio",
        "source_head": head,
        "preregistered_numerical_threshold": 1e-10,
        "test_step_outcome": tests_outcome,
        "outcome": "NUMERICALLY_UNRESOLVED",
        "not_a_claim": [
            "intraglottal measured pressure", "self-excited tissue",
            "physiological naturalness", "creator sound acceptance",
        ],
        "fixtures": [],
    }
    failure = None
    try:
        run(receipt)
        if tests_outcome != "success":
            # The independent runner cannot grant a GO when pytest failed.
            receipt["outcome"] = "NUMERICALLY_UNRESOLVED"
            receipt["reason"] = "test gate not verified"
    except Exception:
        failure = traceback.format_exc()
        receipt["outcome"] = "NUMERICALLY_UNRESOLVED"
        receipt["failure"] = failure
    finally:
        # Write even if a physical inequality/step fails. The complete
        # history and the failing tick remain part of the returned artifact.
        args.out.write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({
            "outcome": receipt["outcome"],
            "fixtures": len(receipt["fixtures"]),
            "path": str(args.out),
        }))
    if failure is not None:
        raise RuntimeError(failure)


if __name__ == "__main__":
    main()
