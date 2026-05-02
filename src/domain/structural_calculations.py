"""Higher-level structural orientation calculations."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.domain.geometry import pole_from_alpha_beta, pole_to_plane_orientation


@dataclass(frozen=True)
class OrientationResult:
    dip: float
    dip_direction: float
    strike: float
    pole_east: float
    pole_north: float
    pole_up: float


def alpha_beta_to_orientation(
    alpha: float,
    beta: float,
    trend_of_hole: float,
    plunge_of_hole: float,
    reference_line: float,
) -> OrientationResult:
    """
    Compute plane orientation outputs for a single row.
    Alpha: plane/core-axis angle (0-90).
    Beta: clockwise downhole angle from reference line (0-360).
    """
    pole = pole_from_alpha_beta(
        trend_deg=trend_of_hole,
        plunge_deg=plunge_of_hole,
        alpha_deg=alpha,
        beta_deg=beta,
        reference_line_deg=reference_line,
    )
    dip, dip_direction, strike = pole_to_plane_orientation(pole)
    return OrientationResult(
        dip=dip,
        dip_direction=dip_direction,
        strike=strike,
        pole_east=float(pole[0]),
        pole_north=float(pole[1]),
        pole_up=float(pole[2]),
    )


def compute_orientations(valid_df: pd.DataFrame) -> pd.DataFrame:
    """Compute orientation columns for each valid input row."""
    output_df = valid_df.copy()
    dips = []
    dip_dirs = []
    strikes = []
    pole_e = []
    pole_n = []
    pole_u = []

    for _, row in output_df.iterrows():
        result = alpha_beta_to_orientation(
            alpha=float(row["alpha"]),
            beta=float(row["beta"]),
            trend_of_hole=float(row["trend_of_hole"]),
            plunge_of_hole=float(row["plunge_of_hole"]),
            reference_line=float(row["core_orientation_reference"]),
        )
        dips.append(result.dip)
        dip_dirs.append(result.dip_direction)
        strikes.append(result.strike)
        pole_e.append(result.pole_east)
        pole_n.append(result.pole_north)
        pole_u.append(result.pole_up)

    output_df["dip"] = dips
    output_df["dip_direction"] = dip_dirs
    output_df["strike"] = strikes
    output_df["pole_east"] = pole_e
    output_df["pole_north"] = pole_n
    output_df["pole_up"] = pole_u

    return output_df

