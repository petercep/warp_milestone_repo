from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplstereonet


def main() -> None:
    # Provided data
    dip = [30, 45, 60]
    dip_dir = [120, 200, 300]

    # mplstereonet pole() expects strike + dip.
    strike = [((d - 90) % 360) for d in dip_dir]

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="stereonet")
    ax.pole(strike, dip, marker="o", color="tab:blue", linestyle="None")
    ax.grid(True)
    fig.suptitle("Stereonet Pole Plot (Provided Data)", y=0.98)

    output = Path("sample_data/stereonet_example_from_prompt.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
