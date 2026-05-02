"""Validation and normalization for input logs."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.domain.conventions import Convention

REQUIRED_COLUMNS = [
    "hole_id",
    "depth",
    "alpha",
    "beta",
    "trend_of_hole",
    "plunge_of_hole",
]

NUMERIC_COLUMNS = [
    "depth",
    "alpha",
    "beta",
    "trend_of_hole",
    "plunge_of_hole",
]

OPTIONAL_COLUMNS = [
    "core_orientation_reference",
    "lithology",
    "structure_type",
    "comments",
]


@dataclass(frozen=True)
class ValidationIssue:
    source_row: int
    column: str
    message: str


def _in_range(value: float, minimum: float, maximum: float) -> bool:
    return minimum <= value <= maximum


def validate_dataframe(
    df: pd.DataFrame,
    convention: Convention,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate and normalize dataframe values.
    Returns (valid_rows_df, validation_issues_df).
    """
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        missing_display = ", ".join(missing_columns)
        raise ValueError(f"Missing required columns: {missing_display}")

    working_df = df.copy()
    for col in OPTIONAL_COLUMNS:
        if col not in working_df.columns:
            working_df[col] = pd.NA

    for col in NUMERIC_COLUMNS + ["core_orientation_reference"]:
        working_df[col] = pd.to_numeric(working_df[col], errors="coerce")

    issues: list[ValidationIssue] = []
    valid_indices: list[int] = []

    for idx, row in working_df.iterrows():
        row_issues = []

        for col in NUMERIC_COLUMNS:
            if pd.isna(row[col]):
                row_issues.append(
                    ValidationIssue(
                        source_row=int(idx),
                        column=col,
                        message=f"'{col}' must be numeric and non-empty.",
                    )
                )

        if not pd.isna(row["alpha"]) and not _in_range(
            float(row["alpha"]), convention.alpha_min, convention.alpha_max
        ):
            row_issues.append(
                ValidationIssue(
                    source_row=int(idx),
                    column="alpha",
                    message=(
                        f"alpha out of range [{convention.alpha_min}, "
                        f"{convention.alpha_max}]"
                    ),
                )
            )

        if not pd.isna(row["beta"]) and not _in_range(
            float(row["beta"]), convention.beta_min, convention.beta_max
        ):
            row_issues.append(
                ValidationIssue(
                    source_row=int(idx),
                    column="beta",
                    message=(
                        f"beta out of range [{convention.beta_min}, "
                        f"{convention.beta_max}]"
                    ),
                )
            )

        if not pd.isna(row["trend_of_hole"]) and not _in_range(
            float(row["trend_of_hole"]), convention.trend_min, convention.trend_max
        ):
            row_issues.append(
                ValidationIssue(
                    source_row=int(idx),
                    column="trend_of_hole",
                    message=(
                        f"trend_of_hole out of range [{convention.trend_min}, "
                        f"{convention.trend_max}]"
                    ),
                )
            )

        if not pd.isna(row["plunge_of_hole"]) and not _in_range(
            float(row["plunge_of_hole"]), convention.plunge_min, convention.plunge_max
        ):
            row_issues.append(
                ValidationIssue(
                    source_row=int(idx),
                    column="plunge_of_hole",
                    message=(
                        f"plunge_of_hole out of range [{convention.plunge_min}, "
                        f"{convention.plunge_max}]"
                    ),
                )
            )


        if row_issues:
            issues.extend(row_issues)
        else:
            valid_indices.append(int(idx))

    valid_df = working_df.loc[valid_indices].copy()
    valid_df["core_orientation_reference"] = valid_df[
        "core_orientation_reference"
    ].fillna(convention.reference_line_default)

    issues_df = pd.DataFrame([issue.__dict__ for issue in issues])
    if issues_df.empty:
        issues_df = pd.DataFrame(columns=["source_row", "column", "message"])

    return valid_df, issues_df

