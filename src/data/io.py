"""Data loading and saving helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_table(path: str | Path) -> pd.DataFrame:
    """Load tabular data from a supported file type."""
    input_path = Path(path)
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(input_path)
    if suffix in {".xlsx", ".xlsm", ".ods"}:
        return pd.read_excel(input_path)
    raise ValueError(f"Unsupported file type: '{suffix or '<none>'}'.")


def save_table(df: pd.DataFrame, path: str | Path) -> None:
    """Save tabular data to a supported file type."""
    output_path = Path(path)
    suffix = output_path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(output_path, index=False)
        return
    if suffix in {".xlsx", ".xlsm"}:
        df.to_excel(output_path, index=False)
        return
    raise ValueError(f"Unsupported file type: '{suffix or '<none>'}'.")
