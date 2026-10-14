"""Plot measured evidence only. Plot interpolation is not a new scientific fixture."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot(output: Path) -> None:
    local = json.loads((output / "local_scattering.json").read_text())
    metrics = json.loads((output / "metrics.json").read_text())
    plt.rcParams["svg.hashsalt"] = "og1-exp038"
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), layout="constrained")
    colors = ("#666666", "#3476ad", "#b15a32")
    labels = ("Reflection to A", "Transmission to B", "Transmission to C")
    bottom = [0., 0., 0.]
    for i, (label, color) in enumerate(zip(labels, colors)):
        values = [100 * row["reflection_B_C_power_fractions"][i] for row in local]
        axes[0].bar([0, 1, 2], values, bottom=bottom, color=color, label=label)
        for x, value, base in zip([0, 1, 2], values, bottom):
            axes[0].text(x, base + value/2, f"{value:.1f}%", ha="center", va="center", color="white", fontsize=10)
        bottom = [b+v for b, v in zip(bottom, values)]
    axes[0].set_xticks([0, 1, 2], ["0.5", "1", "2"])
    axes[0].set_xlabel("Branch C area / baseline area")
    axes[0].set_ylabel("Incident power (%)")
    axes[0].set_title("Local junction: no returning waves")
    axes[0].legend(loc="upper center", bbox_to_anchor=(.5, -.19), frameon=False, fontsize=9)
    for ratio, color in zip((.5, 1., 2.), colors):
        selected = [m for m in metrics if m["area_ratio_c"] == ratio and m["load_c"] == "fixed_impedance"
                    and m["source_scale"] == 1]
        selected.sort(key=lambda m: m["frequency_hz"])
        axes[1].plot([m["frequency_hz"] for m in selected],
                     [m["powers_input_B_C_w"][0] * 1e6 for m in selected], "o-", color=color,
                     label=f"C area x {ratio:g}")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("Input mean power (micro W)")
    axes[1].set_title("Whole body: C termination held fixed")
    axes[1].legend(frameon=False, fontsize=9)
    axes[1].grid(alpha=.2)
    fig.suptitle("OG-1 / Exp038: fixed, passive 1D acoustic branch (research only)", fontsize=12)
    for suffix in ("svg", "png"):
        path = output / f"comparison.{suffix}"
        if path.exists():
            raise FileExistsError(path)
        options = {"metadata": {"Date": None, "Creator": "OG-1 Experiment 038"}} if suffix == "svg" else {}
        fig.savefig(path, dpi=150, **options)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    plot(parser.parse_args().output_dir)
