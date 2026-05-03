"""Milestone 3 UI action controllers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd

from src.config.defaults import DEFAULT_CONVENTION_NAME
from src.data.column_mapping import normalize_input_columns
from src.data.io import load_table, save_table
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
    last_issues_export_path: Path | None = None

    def _clear_calculation_state(self) -> None:
        self.valid_df = None
        self.issues_df = None
        self.computed_df = None
        self.last_calculation_summary = None

    def _clear_export_state(self) -> None:
        self.last_export_path = None
        self.last_issues_export_path = None

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
            self._clear_export_state()
            return

        try:
            imported_df = load_table(input_path)
            imported_df = normalize_input_columns(imported_df)
        except Exception as exc:
            self.error_sink(f"Import failed for '{input_path}': {exc}")
            self.selected_input_path = None
            self.imported_df = None
            self._clear_calculation_state()
            self._clear_export_state()
            return

        self.selected_input_path = input_path
        self.imported_df = imported_df
        self._clear_calculation_state()
        self._clear_export_state()
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
            self._clear_export_state()
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
        self._clear_export_state()
        self.status_sink(
            "Calculate complete: "
            f"input={summary['input_rows']}, "
            f"valid={summary['valid_rows']}, "
            f"invalid={summary['invalid_rows']}, "
            f"issues={summary['issues_count']}"
        )

    def handle_plot(self) -> None:
        """Validate plot prerequisites and emit plot-action status."""
        if self.computed_df is None:
            self.error_sink("No calculated results available. Use Calculate first.")
            return
        self.status_sink(f"Plot action triggered for {len(self.computed_df)} row(s).")

    def handle_export(self) -> None:
        """Export computed orientations and validation issues to CSV files."""
        if (
            self.selected_input_path is None
            or self.computed_df is None
            or self.issues_df is None
        ):
            self.error_sink("No calculated results available. Use Calculate first.")
            return

        computed_output = self.selected_input_path.with_name(
            f"{self.selected_input_path.stem}_ui_computed.csv"
        )
        issues_output = self.selected_input_path.with_name(
            f"{self.selected_input_path.stem}_ui_validation_issues.csv"
        )

        try:
            save_table(self.computed_df, computed_output)
            save_table(self.issues_df, issues_output)
        except Exception as exc:
            self.error_sink(f"Export failed: {exc}")
            self._clear_export_state()
            return

        self.last_export_path = computed_output
        self.last_issues_export_path = issues_output
        self.status_sink(
            "Export complete: "
            f"computed={computed_output}, "
            f"issues={issues_output}"
        )
