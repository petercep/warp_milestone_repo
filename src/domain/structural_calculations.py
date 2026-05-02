"""Structural orientation computation helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd

REQUIRED_COLUMNS = ("alpha", "beta", "trend_of_hole")


def compute_orientations(valid_df: pd.DataFrame) -> pd.DataFrame:
    """Compute dip, dip direction, and strike for validated rows."""
    missing = [column for column in REQUIRED_COLUMNS if column not in valid_df.columns]
    if missing:
        raise ValueError(
            "Missing required columns for orientation computation: "
            + ", ".join(sorted(missing))
        )

    output_df = valid_df.copy()
    output_df["dip"] = pd.to_numeric(output_df["alpha"], errors="raise")
    output_df["dip_direction"] = (
        pd.to_numeric(output_df["trend_of_hole"], errors="raise")
        + pd.to_numeric(output_df["beta"], errors="raise")
    ) % 360.0
    output_df["strike"] = (output_df["dip_direction"] - 90.0) % 360.0
    return output_df
