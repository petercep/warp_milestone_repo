"""Stereonet plotting utilities (Milestone 2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplstereonet  # noqa: F401
import pandas as pd


def _add_polar_grid_overlay(fig: plt.Figure, reference_ax: plt.Axes) -> None:
    """Overlay a simple polar-style grid beneath a stereonet axis."""
    left, bottom, width, height = reference_ax.get_position().bounds
    polar_ax = fig.add_axes([left, bottom, width, height], projection="polar")
    polar_ax.set_theta_zero_location("N")
    polar_ax.set_theta_direction(-1)
    polar_ax.set_rlim(0.0, 90.0)
    polar_ax.set_thetagrids(list(range(0, 360, 30)))
    polar_ax.set_rticks(list(range(10, 91, 10)))
    polar_ax.set_xticklabels([])
    polar_ax.set_yticklabels([])
    polar_ax.grid(True, linestyle=":", linewidth=0.6, color="0.75")
    polar_ax.patch.set_alpha(0.0)
    for spine in polar_ax.spines.values():
        spine.set_visible(False)
    polar_ax.set_zorder(0)
    reference_ax.set_zorder(1)
    reference_ax.set_facecolor("none")


def filter_computed_rows(
    df: pd.DataFrame,
    filters: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Filter computed orientation rows.
    - Drops rows with missing dip/dip_direction/strike.
    - Applies equality filters for provided columns.
    """
    working = df.copy()

    for col in ("dip", "dip_direction", "strike"):
        if col not in working.columns:
            raise ValueError(
                f"Missing required computed column '{col}' for stereonet plotting."
            )
        working = working[working[col].notna()]

    if filters:
        for col, value in filters.items():
            if col not in working.columns:
                raise ValueError(f"Cannot filter by missing column '{col}'.")
            working = working[working[col] == value]

    return working


def plot_poles(
    df: pd.DataFrame,
    output_path: str | Path,
    filters: Mapping[str, Any] | None = None,
    title: str | None = None,
    polar_grid: bool = False,
) -> Path:
    """Plot poles on stereonet and export PNG/SVG."""
    filtered = filter_computed_rows(df, filters=filters)
    if filtered.empty:
        raise ValueError("No rows available for plotting after filtering.")

    output = Path(output_path)
    suffix = output.suffix.lower()
    if suffix not in {".png", ".svg"}:
        raise ValueError("Unsupported plot format. Use .png or .svg output.")

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="stereonet")
    fig.subplots_adjust(top=0.78)
    if polar_grid:
        _add_polar_grid_overlay(fig, ax)
    ax.grid(True)
    strikes = filtered["strike"].astype(float).to_numpy(copy=True)
    dips = filtered["dip"].astype(float).to_numpy(copy=True)

    ax.pole(
        strikes,
        dips,
        marker="o",
        linestyle="None",
        color="tab:blue",
        markersize=4,
    )
    fig.suptitle(title or "Stereonet Pole Plot", y=0.98)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output

