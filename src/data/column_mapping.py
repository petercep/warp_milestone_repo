"""Input column alias normalization for import workflows."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "hole_id": ("hole", "hole_id", "drilhole", "drillhole_id", "borehole", "bh_id", "bh"),
    "depth": ("depth", "distance", "depth_to", "depth to"),
    "trend": ("trend", "azimuth", "az", "hole_az", "bearing"),
    "plunge": ("hole_dip", "inclination", "plunge", "hole_plunge"),
    "alpha": ("alfa", "alpha", "angle1"),
    "beta": ("beta", "angle2"),
}
OPTIONAL_REFERENCE_ALIASES: tuple[str, ...] = (
    "ref",
    "reference_line",
    "core_orientation_reference",
)


def _normalize_column_name(column_name: str) -> str:
    return " ".join(column_name.strip().lower().split())


def _column_lookup(columns: pd.Index) -> dict[str, str]:
    return {_normalize_column_name(column): column for column in columns}


def _format_missing_required_columns(missing: list[tuple[str, tuple[str, ...]]]) -> str:
    required = "; ".join(
        f"{canonical} (accepted: {', '.join(aliases)})"
        for canonical, aliases in missing
    )
    return "Missing required column(s): " + required


def normalize_input_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Validate required input aliases and normalize to canonical column names."""
    normalized_df = df.copy()
    lookup = _column_lookup(normalized_df.columns)

    missing_required: list[tuple[str, tuple[str, ...]]] = []
    rename_map: dict[str, str] = {}
    for canonical_name, aliases in REQUIRED_COLUMN_ALIASES.items():
        matched_column = None
        for alias in aliases:
            matched_column = lookup.get(_normalize_column_name(alias))
            if matched_column is not None:
                break
        if matched_column is None:
            missing_required.append((canonical_name, aliases))
            continue
        if matched_column != canonical_name:
            rename_map[matched_column] = canonical_name

    if missing_required:
        raise ValueError(_format_missing_required_columns(missing_required))

    if rename_map:
        normalized_df = normalized_df.rename(columns=rename_map)

    lookup = _column_lookup(normalized_df.columns)
    matched_reference_columns: list[str] = []
    for alias in OPTIONAL_REFERENCE_ALIASES:
        matched = lookup.get(_normalize_column_name(alias))
        if matched is not None and matched not in matched_reference_columns:
            matched_reference_columns.append(matched)

    if matched_reference_columns:
        merged_reference = normalized_df[matched_reference_columns[0]]
        for column in matched_reference_columns[1:]:
            merged_reference = merged_reference.where(
                merged_reference.notna(), normalized_df[column]
            )
        normalized_df["ref"] = merged_reference
        for column in matched_reference_columns:
            if column != "ref":
                normalized_df = normalized_df.drop(columns=[column])

    return normalized_df
