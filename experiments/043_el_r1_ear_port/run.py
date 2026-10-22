"""Execute research-only EL-R1 synthetic fixture; print structured JSON."""
from __future__ import annotations

import argparse
import json

from listener_port import EntranceDrive, ListenerFixture, evaluate


def main() -> None:
    parser = argparse.ArgumentParser(description="EL-R1 passive listener acoustic port")
    parser.add_argument("--length-m", type=float, default=0.025)
    parser.add_argument("--load-ratio", type=float, default=2.0)
    parser.add_argument("--frequencies-hz", default="0,1000,3000,7000")
    arguments = parser.parse_args()
    data = evaluate(
        ListenerFixture(length_m=arguments.length_m,
                        terminal_resistance_ratio_to_zc=arguments.load_ratio),
        EntranceDrive(frequencies_hz=tuple(float(x) for x in arguments.frequencies_hz.split(","))),
    )
    print(json.dumps(data, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
