"""Gate A deterministic synthetic receipt; no physical-ear or product capability."""
import json
from fractions import Fraction
from qualifier import (MeasuredPressureTransfer, SyntheticReferencePort,
                       normalized_one_port_pressure, qualify)

def main():
    values = {
        "baseline_a": normalized_one_port_pressure(1, 0, 1),
        "baseline_b": normalized_one_port_pressure(2, 1, 1),
        "counterfactual_a": normalized_one_port_pressure(1, 0, 2),
        "counterfactual_b": normalized_one_port_pressure(2, 1, 2),
    }
    print(json.dumps({
        "schema": "el-rp1.gatea.receipt.v1",
        "preregistration_sha": "a33c8c68879f732cd830b2caab6b8024b5322297",
        "status": "COMPUTED_SYNTHETIC_GATE_A_ONLY",
        "analytic_expected": {"baseline_a": "1", "baseline_b": "1",
                              "counterfactual_a": "1", "counterfactual_b": str(Fraction(4,3))},
        "computed": values,
        "pressure_only_changed_load": qualify(
            MeasuredPressureTransfer("a"*64), "PREDICT_CHANGED_LOAD").code,
        "synthetic_eligibility": qualify(SyntheticReferencePort(
            1+0j, 13834333.333333334, 27668666.666666668, 4e-5, .025, 2200),
            "PREDICT_CHANGED_LOAD").status,
        "human_ear_validation": "NOT_TESTED",
        "studio_api": "NOT_ADOPTED",
    }, sort_keys=True, indent=2, allow_nan=False))

if __name__ == "__main__":
    main()
