"""Generate genuine sealed-control traces and derived, separately audited receipts."""
from __future__ import annotations
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from solver import Fixture, midpoint_linear_force, save_trace, simulate
from audit import audit


def produce(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    cases = (
        ("damped_4us", Fixture(), 4e-6),
        ("damped_2us", Fixture(), 2e-6),
        ("damped_1us", Fixture(), 1e-6),
        ("lossless_1us", replace(Fixture(), d_L_Ns_m=0, d_U_Ns_m=0), 1e-6),
        ("static_4us", replace(Fixture(), x_L0_m=0, x_U0_m=0), 4e-6),
    )
    report = {"schema": "vf1b2.c1r0.receipt.v0-research", "cases": {}, "quadrature": {}}
    for name, fixture, dt in cases:
        trace = simulate(fixture, dt)
        path = out / f"{name}.json"
        save_trace(path, trace)  # Preserve even if the independent audit refuses.
        try:
            receipt = audit(trace)
        except Exception as exc:
            failure = {"status": "AUDIT_FAILED", "case": name, "error_type": type(exc).__name__,
                       "error": str(exc), "raw_trace": path.name,
                       "raw_sha256": sha256(path.read_bytes()).hexdigest()}
            (out / f"{name}.failure.json").write_text(
                json.dumps(failure, indent=2, sort_keys=True), encoding="utf-8")
            report["cases"][name] = failure
            (out / "receipt.json").write_text(
                json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
            raise
        receipt.update({"trace_filename": path.name,
                        "sha256": sha256(path.read_bytes()).hexdigest(),
                        "sample_count": len(trace["samples"]),
                        "x_final_m": trace["samples"][-1]["x_m"],
                        "v_final_m_s": trace["samples"][-1]["v_m_s"]})
        report["cases"][name] = receipt
    fixture = Fixture()
    exact_lower = fixture.ell_m * fixture.L_g_m * (100.0 + 120.0 / 3)
    exact_upper = fixture.ell_m * fixture.L_g_m * (100.0 + 2 * 120.0 / 3)
    for n in (8, 16, 32):
        lower, upper = midpoint_linear_force(n, 100.0, 120.0, fixture.L_g_m, fixture.ell_m)
        report["quadrature"][str(n)] = {"F_lower_N": lower, "F_upper_N": upper,
                                         "max_force_error_N": max(abs(lower - exact_lower), abs(upper - exact_upper))}
    (out / "receipt.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "vf1b2-c1r0-artifacts")
    results = produce(target)
    for name, case in results["cases"].items():
        print(f"{name}: energy_residual={case['energy_residual_J']:.6e} J, "
              f"relative={case['energy_residual_relative']:.6e}, sha256={case['sha256']}")
