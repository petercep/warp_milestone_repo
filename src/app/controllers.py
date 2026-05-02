"""Milestone 3 UI action controllers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

StatusSink = Callable[[str], None]
ErrorSink = Callable[[str], None]


@dataclass
class MainWindowController:
    """Thin controller for initial UI action wiring."""

    status_sink: StatusSink
    error_sink: ErrorSink
    selected_input_path: Path | None = None
    last_export_path: Path | None = None

    def handle_import(self, selected_path: str | None) -> None:
        """Track imported file selection from UI."""
        if not selected_path:
            self.status_sink("Import cancelled.")
            return

        self.selected_input_path = Path(selected_path)
        self.status_sink(f"Selected input: {self.selected_input_path}")

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
