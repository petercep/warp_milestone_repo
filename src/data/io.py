"""Input/output helpers for tabular logs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_table(path: str | Path) -> pd.DataFrame:
    """Load CSV or XLSX into a DataFrame."""
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(file_path)

    raise ValueError(f"Unsupported file type '{suffix}'. Use CSV or Excel.")


def save_table(df: pd.DataFrame, path: str | Path) -> None:
    """Save DataFrame as CSV."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)

