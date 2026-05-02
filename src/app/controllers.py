"""Milestone 3 UI action controllers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd

from src.data.io import load_table

StatusSink = Callable[[str], None]
ErrorSink = Callable[[str], None]


@dataclass
class MainWindowController:
    """Thin controller for initial UI action wiring."""

    status_sink: StatusSink
    error_sink: ErrorSink
    selected_input_path: Path | None = None
    imported_df: pd.DataFrame | None = None
    last_export_path: Path | None = None

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
            return

        try:
            imported_df = load_table(input_path)
        except Exception as exc:
            self.error_sink(f"Import failed for '{input_path}': {exc}")
            self.selected_input_path = None
            self.imported_df = None
            return

        self.selected_input_path = input_path
        self.imported_df = imported_df
        self.status_sink(
            "Import complete: "
            f"{len(imported_df)} rows, {len(imported_df.columns)} columns "
            f"from {input_path.name}"
        )

    def handle_calculate(self) -> None:
        """Placeholder action hook for future computation wiring."""
        if self.selected_input_path is None:
            self.error_sink("No input file selected. Use Import first.")
            return

        self.status_sink(
            "Calculate action triggered (Milestone 3 scaffold; computation wiring pending)."
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