"""Milestone 3 desktop UI scaffold (main window + action wiring)."""

from __future__ import annotations

import sys
from typing import Any

from src.app.controllers import MainWindowController

try:
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QToolBar,
        QVBoxLayout,
        QWidget,
        QHBoxLayout,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
    )
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local UI deps
    raise RuntimeError(
        "PySide6 is required to run the desktop UI scaffold. "
        "Install it before launching src.app.ui_main."
    ) from exc


class MainWindow(QMainWindow):
    """Initial desktop shell for Milestone 3."""
    MAX_PREVIEW_ROWS = 200

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Geology Workstation - Milestone 3 Scaffold")
        self.resize(980, 680)

        self.status_label = QLabel("Ready. Use Import to select input data.")
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)

        self.preview_tabs = QTabWidget()
        self.input_preview_table = QTableWidget()
        self.computed_preview_table = QTableWidget()
        self.issues_preview_table = QTableWidget()
        self.preview_tabs.addTab(self.input_preview_table, "Input Preview")
        self.preview_tabs.addTab(self.computed_preview_table, "Computed Preview")
        self.preview_tabs.addTab(self.issues_preview_table, "Validation Issues")
        self.canvas_placeholder = QLabel(
            "Stereonet canvas placeholder (to be embedded in next task)."
        )

        self.controller = MainWindowController(
            status_sink=self.append_status,
            error_sink=self.show_error,
        )

        self._build_layout()
        self._build_toolbar()
        self._append_log("UI scaffold initialized.")

    def _build_layout(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.status_label)

        button_row = QHBoxLayout()
        self.import_btn = QPushButton("Import")
        self.calculate_btn = QPushButton("Calculate")
        self.plot_btn = QPushButton("Plot")
        self.export_btn = QPushButton("Export")
        for button in (
            self.import_btn,
            self.calculate_btn,
            self.plot_btn,
            self.export_btn,
        ):
            button_row.addWidget(button)
        layout.addLayout(button_row)
        layout.addWidget(self.preview_tabs)

        layout.addWidget(self.canvas_placeholder)
        layout.addWidget(self.log_output)
        self.setCentralWidget(container)

        self.import_btn.clicked.connect(self._on_import_triggered)
        self.calculate_btn.clicked.connect(self._on_calculate_triggered)
        self.plot_btn.clicked.connect(self.controller.handle_plot)
        self.export_btn.clicked.connect(self._on_export_triggered)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Actions")
        self.addToolBar(toolbar)

        import_action = toolbar.addAction("Import")
        calculate_action = toolbar.addAction("Calculate")
        plot_action = toolbar.addAction("Plot")
        export_action = toolbar.addAction("Export")

        import_action.triggered.connect(self._on_import_triggered)
        calculate_action.triggered.connect(self._on_calculate_triggered)
        plot_action.triggered.connect(self.controller.handle_plot)
        export_action.triggered.connect(self._on_export_triggered)

    def _on_import_triggered(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select input file",
            "",
            "Data files (*.csv *.xlsx *.xlsm);;All files (*)",
        )
        self.controller.handle_import(file_path or None)
        self._refresh_previews_after_import()

    def _on_calculate_triggered(self) -> None:
        self.controller.handle_calculate()
        self._refresh_previews_after_calculate()
        summary = self.controller.last_calculation_summary
        if summary is not None:
            self._append_log(
                "Calculation summary: "
                f"input={summary['input_rows']}, "
                f"valid={summary['valid_rows']}, "
                f"invalid={summary['invalid_rows']}, "
                f"issues={summary['issues_count']}"
            )

    def _on_export_triggered(self) -> None:
        self.controller.handle_export()
        if (
            self.controller.last_export_path is not None
            and self.controller.last_issues_export_path is not None
        ):
            self._append_log(
                "Export files:\n"
                f"- {self.controller.last_export_path}\n"
                f"- {self.controller.last_issues_export_path}"
            )

    def _refresh_previews_after_import(self) -> None:
        self._fill_table_from_rows(
            self.input_preview_table,
            self.controller.imported_df,
        )
        self._fill_table_from_rows(
            self.computed_preview_table,
            None,
        )
        self._fill_table_from_rows(
            self.issues_preview_table,
            None,
        )
        if self.controller.imported_df is not None:
            shown = min(len(self.controller.imported_df), self.MAX_PREVIEW_ROWS)
            self._append_log(f"Input preview updated ({shown} rows shown).")

    def _refresh_previews_after_calculate(self) -> None:
        self._fill_table_from_rows(
            self.computed_preview_table,
            self.controller.computed_df,
        )
        self._fill_table_from_rows(
            self.issues_preview_table,
            self.controller.issues_df,
        )
        if self.controller.computed_df is not None:
            shown = min(len(self.controller.computed_df), self.MAX_PREVIEW_ROWS)
            self._append_log(f"Computed preview updated ({shown} rows shown).")
        if self.controller.issues_df is not None:
            shown = min(len(self.controller.issues_df), self.MAX_PREVIEW_ROWS)
            self._append_log(f"Issues preview updated ({shown} rows shown).")

    def _fill_table_from_rows(
        self,
        table: QTableWidget,
        rows_obj: Any | None,
    ) -> None:
        table.clear()
        if rows_obj is None:
            table.setRowCount(0)
            table.setColumnCount(0)
            return

        preview = rows_obj.head(self.MAX_PREVIEW_ROWS)
        table.setRowCount(len(preview))
        table.setColumnCount(len(preview.columns))
        table.setHorizontalHeaderLabels([str(column) for column in preview.columns])

        for row_idx, row in enumerate(preview.itertuples(index=False, name=None)):
            for col_idx, value in enumerate(row):
                display = "" if value is None else str(value)
                table.setItem(row_idx, col_idx, QTableWidgetItem(display))
        table.resizeColumnsToContents()

    def append_status(self, message: str) -> None:
        self.status_label.setText(message)
        self._append_log(message)

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Action Error", message)
        self._append_log(f"ERROR: {message}")

    def _append_log(self, message: str) -> None:
        self.log_output.appendPlainText(message)


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
