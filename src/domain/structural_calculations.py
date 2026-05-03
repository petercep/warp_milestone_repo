"""Structural orientation computation helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config.defaults import DEFAULT_REFERENCE_LINE

REQUIRED_COLUMNS = ("alpha", "beta", "trend", "plunge")
REFERENCE_COLUMNS = ("ref", "reference_line", "core_orientation_reference")
REFERENCE_INPUT_ALIAS_COLUMNS = ("ref", "core_orientation_reference")
DERIVED_COLUMN_ORDER = ("dip", "dip_direction", "strike", "reference_line")


def _resolve_reference_line(df: pd.DataFrame) -> pd.Series:
    reference_line = pd.Series(pd.NA, index=df.index, dtype="Float64")
    for column in REFERENCE_COLUMNS:
        if column not in df.columns:
            continue
        candidate = pd.to_numeric(df[column], errors="raise")
        reference_line = reference_line.where(reference_line.notna(), candidate)
    return reference_line.fillna(DEFAULT_REFERENCE_LINE).astype(float)


def _finalize_output_columns(output_df: pd.DataFrame) -> pd.DataFrame:
    columns_to_drop = [
        column for column in REFERENCE_INPUT_ALIAS_COLUMNS if column in output_df.columns
    ]
    if columns_to_drop:
        output_df = output_df.drop(columns=columns_to_drop)

    leading_columns = [
        column for column in output_df.columns if column not in DERIVED_COLUMN_ORDER
    ]
    derived_columns = [
        column for column in DERIVED_COLUMN_ORDER if column in output_df.columns
    ]
    return output_df.loc[:, leading_columns + derived_columns]


def _compute_conv_alpha_beta(
    trend: pd.Series,
    plunge: pd.Series,
    alpha: pd.Series,
    beta: pd.Series,
    reference_line: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """Vectorized equivalent of workbook ConvAlphaBeta(trend, plunge, alpha, beta, ref)."""
    g = np.deg2rad(reference_line.to_numpy(copy=False))
    a_ = np.deg2rad(90.0 - alpha.to_numpy(copy=False))
    b_ = np.deg2rad(beta.to_numpy(copy=False))
    an = np.deg2rad(plunge.to_numpy(copy=False))
    bn = np.deg2rad(trend.to_numpy(copy=False))

    xd = np.cos(a_)
    yd = -np.sin(a_) * np.cos(b_)
    zd = -np.sin(a_) * np.sin(b_)

    x = xd
    y = np.cos(g) * yd - np.sin(g) * zd
    z = np.sin(g) * yd + np.cos(g) * zd

    xn = np.cos(an) * np.cos(bn) * x + np.sin(an) * np.cos(bn) * y - np.sin(bn) * z
    yn = np.cos(an) * np.sin(bn) * x + np.sin(an) * np.sin(bn) * y + np.cos(bn) * z
    zn = -np.sin(an) * x + np.cos(an) * y

    q = np.select(
        [
            (xn >= 0.0) & (yn >= 0.0),
            (xn <= 0.0) & (yn >= 0.0),
            (xn >= 0.0) & (yn <= 0.0),
        ],
        [0.0, 180.0, 360.0],
        default=180.0,
    )
    horizontal = np.sqrt((xn ** 2) + (yn ** 2))

    with np.errstate(divide="ignore", invalid="ignore"):
        dip_temp = 90.0 - np.rad2deg(np.arctan(np.divide(zn, horizontal)))
        dip_n = np.where(dip_temp > 90.0, 180.0 - dip_temp, dip_temp)
        q2 = np.where((dip_temp > 90.0) | (dip_temp < 0.0), 180.0, 0.0)
        dirn_temp = q + q2 + np.rad2deg(np.arctan(np.divide(yn, xn)))

    dirn_n = np.where(dirn_temp > 360.0, dirn_temp - 360.0, dirn_temp)
    dip = np.floor(dip_n)
    dip_direction = np.floor(dirn_n)
    return (
        pd.Series(dip, index=alpha.index, dtype=float),
        pd.Series(dip_direction, index=alpha.index, dtype=float),
    )


def compute_orientations(valid_df: pd.DataFrame) -> pd.DataFrame:
    """Compute dip, dip direction, and strike for validated rows."""
    missing = [column for column in REQUIRED_COLUMNS if column not in valid_df.columns]
    if missing:
        raise ValueError(
            "Missing required columns for orientation computation: "
            + ", ".join(sorted(missing))
        )

    output_df = valid_df.copy()
    reference_line = _resolve_reference_line(output_df)
    trend = pd.to_numeric(output_df["trend"], errors="raise")
    plunge = pd.to_numeric(output_df["plunge"], errors="raise")
    alpha = pd.to_numeric(output_df["alpha"], errors="raise")
    beta = pd.to_numeric(output_df["beta"], errors="raise")
    dip, dip_direction = _compute_conv_alpha_beta(
        trend=trend,
        plunge=plunge,
        alpha=alpha,
        beta=beta,
        reference_line=reference_line,
    )
    output_df["dip"] = dip
    output_df["dip_direction"] = dip_direction
    output_df["strike"] = (output_df["dip_direction"] - 90.0) % 360.0
    output_df["reference_line"] = reference_line
    return _finalize_output_columns(output_df)