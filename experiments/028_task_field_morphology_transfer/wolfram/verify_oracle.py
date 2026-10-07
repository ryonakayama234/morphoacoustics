"""Compare a fresh Wolfram export with the immutable, schema-complete oracle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def oracle_differences(expected: object, actual: object, path: str = "$") -> list[str]:
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or expected.keys() != actual.keys():
            return [f"{path}: object keys differ"]
        return [difference for key in expected
                for difference in oracle_differences(expected[key], actual[key], f"{path}.{key}")]
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            return [f"{path}: array lengths differ"]
        return [difference for index, value in enumerate(expected)
                for difference in oracle_differences(value, actual[index], f"{path}[{index}]")]
    if isinstance(expected, bool) or isinstance(actual, bool):
        equal = type(expected) is type(actual) and expected == actual
    else:
        equal = expected == actual
    return [] if equal else [f"{path}: expected {expected!r}, got {actual!r}"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("regenerated", type=Path)
    args = parser.parse_args()
    frozen = json.loads(Path(__file__).with_name("v3b_oracle.json").read_text())
    regenerated = json.loads(args.regenerated.read_text())
    differences = oracle_differences(frozen, regenerated)
    if differences:
        raise SystemExit("\n".join(differences))
    print("PASS: complete Wolfram oracle matches frozen JSON exactly after parsing")


if __name__ == "__main__":
    main()
