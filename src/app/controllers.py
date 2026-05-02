"""Milestone 3 UI action controllers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd

from src.config.defaults import DEFAULT_CONVENTION_NAME
from src.data.io import load_table
from src.data.validation import validate_dataframe
from src.domain.conventions import get_convention
from src.domain.structural_calculations import compute_orientations

StatusSink = Callable[[str], None]
ErrorSink = Callable[[str], None]


@dataclass
class MainWindowController:
    """Thin controller for initial UI action wiring."""

    status_sink: StatusSink
    error_sink: ErrorSink
    selected_input_path: Path | None = None
    imported_df: pd.DataFrame | None = None
    valid_df: pd.DataFrame | None = None
    issues_df: pd.DataFrame | None = None
    computed_df: pd.DataFrame | None = None
    last_calculation_summary: dict[str, int] | None = None
    last_export_path: Path | None = None

    def _clear_calculation_state(self) -> None:
        self.valid_df = None
        self.issues_df = None
        self.computed_df = None
        self.last_calculation_summary = None

    def handle_import(self, selected_path: str | None) -> None:
        """Load selected file and cache imported table for follow-up actions."""
        if not selected_path:
            self.status_sink("Import cancelled.")
            return

        input_path = Path(selected_path)
        if not input_path.exists() or not input_path.is_file():
            self.error_sink(f"Input file not found: {input_path}")
            self.selected_input_path = None
            self.imported_df = None
            self._clear_calculation_state()
            return

        try:
            imported_df = load_table(input_path)
        except Exception as exc:
            self.error_sink(f"Import failed for '{input_path}': {exc}")
            self.selected_input_path = None
            self.imported_df = None
            self._clear_calculation_state()
            return

        self.selected_input_path = input_path
        self.imported_df = imported_df
        self._clear_calculation_state()
        self.status_sink(
            "Import complete: "
            f"{len(imported_df)} rows, {len(imported_df.columns)} columns "
            f"from {input_path.name}"
        )

    def handle_calculate(self) -> None:
        """Validate imported rows and compute structural orientations."""
        if self.imported_df is None:
            self.error_sink("No input file selected. Use Import first.")
            return

        try:
            convention = get_convention(DEFAULT_CONVENTION_NAME)
            valid_df, issues_df = validate_dataframe(self.imported_df, convention)
            computed_df = compute_orientations(valid_df)
        except Exception as exc:
            self.error_sink(f"Calculate failed: {exc}")
            self._clear_calculation_state()
            return

        invalid_row_count = (
            int(issues_df["source_row"].nunique()) if not issues_df.empty else 0
        )
        summary = {
            "input_rows": int(len(self.imported_df)),
            "valid_rows": int(len(computed_df)),
            "invalid_rows": invalid_row_count,
            "issues_count": int(len(issues_df)),
        }
        self.valid_df = valid_df
        self.issues_df = issues_df
        self.computed_df = computed_df
        self.last_calculation_summary = summary
        self.status_sink(
            "Calculate complete: "
            f"input={summary['input_rows']}, "
            f"valid={summary['valid_rows']}, "
            f"invalid={summary['invalid_rows']}, "
            f"issues={summary['issues_count']}"
        )

    def handle_plot(self) -> None:
        """Placeholder action hook for future plotting wiring."""
        if self.selected_input_path is None:
            self.error_sink("No input file selected. Use Import first.")
            return

        self.status_sink(
            "Plot action triggered (Milestone 3 scaffold; plotting wiring pending)."
        )

    def handle_export(self) -> None:
        """Placeholder action hook for future export wiring."""
        if self.selected_input_path is None:
            self.error_sink("No input file selected. Use Import first.")
            return

        self.last_export_path = Path("export_placeholder.csv")
        self.status_sink(
            "Export action triggered (Milestone 3 scaffold; export wiring pending)."
        )