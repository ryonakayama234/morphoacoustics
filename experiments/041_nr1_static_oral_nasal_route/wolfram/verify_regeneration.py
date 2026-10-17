"""Verify independent Wolfram global12 *numerical* regeneration of NR-1a goldens.

Offline comparison uses --regenerated JSON; otherwise wolframscript runs the
checked-in .wl source. This is a research audit utility, NOT a scientific
preregistration, and it is NOT silently skipped in GitHub CI.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
from typing import Any

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "global12_oracle.wl"
GOLDEN = HERE / "global12_oracle.json"
START, END = "NR1A_ORACLE_BEGIN", "NR1A_ORACLE_END"
SCALES = {
    "pressure_pa": 1.372,
    "volume_flow_m3_s": 1e-6,
    "mean_power_w": 0.5 * 1.372e-6,
    "input_impedance_pa_s_m3": 1.372e6,
}
TOLERANCE = 1e-12  # engineering *regeneration* comparator; not Gate A acceptance


def _no_nonfinite(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant: {value}")


def read_json(text: str) -> dict[str, Any]:
    result = json.loads(text, parse_constant=_no_nonfinite)
    if not isinstance(result, dict):
        raise ValueError("oracle must be a JSON object")
    return result


def compare_candidate_oracles(golden: dict[str, Any], regenerated: dict[str, Any]) -> float:
    """Reject changed metadata/case ordering/shape/nonfinite data; compare all 24 states.

    Numeric comparison is intentionally normalized, not raw JSON-byte equality.
    """
    if set(golden) != set(regenerated):
        raise AssertionError("oracle top-level fields differ")
    if golden.get("schema") != "nr1a.wolfram.global12.oracle.v0":
        raise AssertionError("unexpected oracle schema")
    if golden.get("status") != "CANDIDATE_NOT_FROZEN":
        raise AssertionError("oracle adoption status changed")
    for key in golden:
        if key != "records" and golden[key] != regenerated[key]:
            raise AssertionError(f"oracle metadata differs: {key}")
    a, b = golden["records"], regenerated["records"]
    if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b) or len(a) != 24:
        raise AssertionError("not exactly 24 records")
    expected = [(case, hz) for case in "NOM" for hz in [80, 250, 400, 733, 997, 1200, 2000, 4000]]
    worst = 0.0
    for i, (x, y) in enumerate(zip(a, b)):
        if set(x) != set(y) or (x["case"], x["frequency_hz"]) != expected[i] or (
            y["case"], y["frequency_hz"]
        ) != expected[i]:
            raise AssertionError(f"case/order/field mismatch at {i}")
        for field, scale in SCALES.items():
            xv, yv = x[field], y[field]
            vector = field in ("input_impedance_pa_s_m3",)
            complex_ports = field in ("pressure_pa", "volume_flow_m3_s")
            n = 2 if vector else 6
            if len(xv) != n or len(yv) != n:
                raise AssertionError(f"{field} size mismatch at {i}")
            for j in range(n):
                xx, yy = xv[j], yv[j]
                if complex_ports:
                    if len(xx) != 2 or len(yy) != 2:
                        raise AssertionError(f"{field} complex shape mismatch at {i}/{j}")
                    parts = zip(xx, yy)
                elif vector:
                    parts = [(xx, yy)]
                else:
                    parts = [(xx, yy)]
                for g, r in parts:
                    if not isinstance(g, (float, int)) or not isinstance(r, (float, int)) or (
                        not math.isfinite(g) or not math.isfinite(r)
                    ):
                        raise AssertionError(f"{field} nonfinite/non-numeric at {i}/{j}")
                    error = abs(g - r) / scale
                    worst = max(worst, error)
                    if error > TOLERANCE:
                        raise AssertionError(f"{field} differs at {i}/{j}: {error:g}")
    return worst


def regenerate(command: str, timeout: int) -> str:
    completed = subprocess.run(
        [command, "-file", str(SOURCE)],
        check=True, capture_output=True, text=True, timeout=timeout,
    )
    output = completed.stdout
    if output.count(START) != 1 or output.count(END) != 1:
        raise AssertionError("missing or duplicate Wolfram oracle markers")
    return output.split(START, 1)[1].split(END, 1)[0].strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regenerated", type=Path, help="independently archived RawJSON")
    parser.add_argument("--wolframscript", default="wolframscript")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    golden = read_json(GOLDEN.read_text(encoding="utf-8"))
    raw = (args.regenerated.read_text(encoding="utf-8") if args.regenerated
           else regenerate(args.wolframscript, args.timeout))
    regenerated = read_json(raw)
    error = compare_candidate_oracles(golden, regenerated)
    print(json.dumps({
        "status": "CANDIDATE_NUMERIC_REGENERATION_MATCH_NOT_ADOPTED",
        "records": len(golden["records"]),
        "max_normalized_component_difference": error,
        "tolerance": TOLERANCE,
        "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
        "golden_sha256": sha256(GOLDEN.read_bytes()).hexdigest(),
        "regenerated_sha256": sha256(raw.encode("utf-8")).hexdigest(),
        "mode": "archived_rawjson" if args.regenerated else "wolframscript",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
