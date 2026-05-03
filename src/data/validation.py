"""Input dataframe validation for controller workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.domain.conventions import Convention

REQUIRED_COLUMNS = (
    "hole_id",
    "depth",
    "alpha",
    "beta",
    "trend",
    "plunge",
)
NUMERIC_COLUMNS = ("depth", "alpha", "beta", "trend", "plunge")
OPTIONAL_REFERENCE_COLUMNS = ("ref",)
REFERENCE_MIN = 0.0
REFERENCE_MAX = 359.0


@dataclass(frozen=True)
class _Issue:
    source_row: int
    column: str
    message: str


def _as_float(value: Any) -> float | None:
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_dataframe(
    df: pd.DataFrame,
    convention: Convention,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (valid_rows, issues) using row-level validation."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            "Missing required input columns: " + ", ".join(sorted(missing))
        )

    valid_rows: list[dict[str, Any]] = []
    issues: list[_Issue] = []

    for source_row, row in df.iterrows():
        row_data = {column: row[column] for column in df.columns}

        missing_required = next(
            (
                column
                for column in REQUIRED_COLUMNS
                if row_data.get(column) is None or pd.isna(row_data.get(column))
            ),
            None,
        )
        if missing_required is not None:
            issues.append(
                _Issue(
                    source_row=int(source_row),
                    column=missing_required,
                    message=f"Missing required value in '{missing_required}'.",
                )
            )
            continue

        numeric_values: dict[str, float] = {}
        invalid_numeric_column: str | None = None
        for column in NUMERIC_COLUMNS:
            numeric_value = _as_float(row_data[column])
            if numeric_value is None:
                invalid_numeric_column = column
                break
            numeric_values[column] = numeric_value
        if invalid_numeric_column is not None:
            issues.append(
                _Issue(
                    source_row=int(source_row),
                    column=invalid_numeric_column,
                    message=f"Non-numeric value in '{invalid_numeric_column}'.",
                )
            )
            continue

        invalid_reference_column: str | None = None
        invalid_reference_message: str | None = None
        for column in OPTIONAL_REFERENCE_COLUMNS:
            if column not in row_data:
                continue
            if pd.isna(row_data[column]):
                continue
            reference_value = _as_float(row_data[column])
            if reference_value is None:
                invalid_reference_column = column
                invalid_reference_message = (
                    f"Non-numeric value in optional '{column}'."
                )
                break
            if not (REFERENCE_MIN <= reference_value <= REFERENCE_MAX):
                invalid_reference_column = column
                invalid_reference_message = (
                    "Reference line out of range: "
                    f"{reference_value} not in [{REFERENCE_MIN}, {REFERENCE_MAX}]."
                )
                break
            numeric_values[column] = reference_value
        if invalid_reference_column is not None:
            issues.append(
                _Issue(
                    source_row=int(source_row),
                    column=invalid_reference_column,
                    message=invalid_reference_message or "Invalid reference value.",
                )
            )
            continue

        alpha = numeric_values["alpha"]
        if not (convention.alpha_min <= alpha <= convention.alpha_max):
            issues.append(
                _Issue(
                    source_row=int(source_row),
                    column="alpha",
                    message=(
                        "Alpha out of range: "
                        f"{alpha} not in [{convention.alpha_min}, {convention.alpha_max}]."
                    ),
                )
            )
            continue

        beta = numeric_values["beta"]
        if not (convention.beta_min <= beta <= convention.beta_max):
            issues.append(
                _Issue(
                    source_row=int(source_row),
                    column="beta",
                    message=(
                        "Beta out of range: "
                        f"{beta} not in [{convention.beta_min}, {convention.beta_max}]."
                    ),
                )
            )
            continue

        normalized_row = dict(row_data)
        normalized_row.update(numeric_values)
        valid_rows.append(normalized_row)

    valid_df = pd.DataFrame(valid_rows, columns=list(df.columns))
    issues_df = pd.DataFrame(
        [
            {
                "source_row": issue.source_row,
                "column": issue.column,
                "message": issue.message,
            }
            for issue in issues
        ]
    )
    return valid_df, issues_df
