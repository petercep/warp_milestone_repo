"""Milestone 3 desktop UI scaffold (main window + action wiring)."""

from __future__ import annotations

import sys
from typing import Any

from src.app.controllers import MainWindowController
from src.config.defaults import (
    DEFAULT_STEREONET_POLAR_GRID,
    DEFAULT_STEREONET_PROJECTION,
    SUPPORTED_STEREONET_PROJECTIONS,
)
from src.data.column_mapping import (
    OPTIONAL_REFERENCE_ALIASES,
    REQUIRED_COLUMN_ALIASES,
)

try:
    import mplstereonet  # noqa: F401
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QToolBar,
        QVBoxLayout,
        QWidget,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
    )
except ImportError as exc:  # pragma: no cover - depends on local UI deps
    raise RuntimeError(
        "UI dependencies (PySide6, matplotlib Qt backend, mplstereonet) "
        "are required to run the desktop UI scaffold."
    ) from exc

_MPL_PROJECTION_BY_CONFIG_NAME = {
    "equal-area": "equal_area_stereonet",
    "equal-angle": "equal_angle_stereonet",
}


class MainWindow(QMainWindow):
    """Initial desktop shell for Milestone 3."""
    MAX_PREVIEW_ROWS = 200

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Convert Alpha Beta")
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

        self.projection_label = QLabel("Projection:")
        self.projection_combo = QComboBox()
        self.projection_combo.addItems(list(SUPPORTED_STEREONET_PROJECTIONS))
        self.projection_combo.setCurrentText(DEFAULT_STEREONET_PROJECTION)
        self.polar_grid_checkbox = QCheckBox("Polar grid")
        self.polar_grid_checkbox.setChecked(DEFAULT_STEREONET_POLAR_GRID)

        self.stereonet_figure = Figure(figsize=(6, 6))
        self.stereonet_canvas = FigureCanvas(self.stereonet_figure)

        self.controller = MainWindowController(
            status_sink=self.append_status,
            error_sink=self.show_error,
        )

        self._build_layout()
        self._build_toolbar()
        self._build_menu()
        self._append_log("UI scaffold initialized.")
        self._render_empty_canvas()

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
        plot_options_row = QHBoxLayout()
        plot_options_row.addWidget(self.projection_label)
        plot_options_row.addWidget(self.projection_combo)
        plot_options_row.addWidget(self.polar_grid_checkbox)
        plot_options_row.addStretch(1)
        layout.addLayout(plot_options_row)
        layout.addWidget(self.stereonet_canvas)
        layout.addWidget(self.log_output)
        self.setCentralWidget(container)

        self.import_btn.clicked.connect(self._on_import_triggered)
        self.calculate_btn.clicked.connect(self._on_calculate_triggered)
        self.plot_btn.clicked.connect(self._on_plot_triggered)
        self.export_btn.clicked.connect(self._on_export_triggered)

        self.projection_combo.currentTextChanged.connect(
            self._on_plot_options_changed
        )
        self.polar_grid_checkbox.toggled.connect(self._on_plot_options_changed)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Actions")
        self.addToolBar(toolbar)

        import_action = toolbar.addAction("Import")
        calculate_action = toolbar.addAction("Calculate")
        plot_action = toolbar.addAction("Plot")
        export_action = toolbar.addAction("Export")

        import_action.triggered.connect(self._on_import_triggered)
        calculate_action.triggered.connect(self._on_calculate_triggered)
        plot_action.triggered.connect(self._on_plot_triggered)
        export_action.triggered.connect(self._on_export_triggered)

    def _build_menu(self) -> None:
        help_menu = self.menuBar().addMenu("Help")
        accepted_names_action = help_menu.addAction("Accepted column names")
        accepted_names_action.triggered.connect(self._show_accepted_column_names)

    def _show_accepted_column_names(self) -> None:
        required_lines = [
            f"- {canonical}: {', '.join(aliases)}"
            for canonical, aliases in REQUIRED_COLUMN_ALIASES.items()
        ]
        optional_reference = ", ".join(OPTIONAL_REFERENCE_ALIASES)
        message = (
            "Required input columns (accepted aliases):\n"
            + "\n".join(required_lines)
            + "\n\nOptional reference column aliases:\n"
            + f"- reference line: {optional_reference}"
        )
        QMessageBox.information(self, "Accepted column names", message)

    def _on_import_triggered(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select input file",
            "",
            "Data files (*.csv *.ods *.xlsx *.xlsm);;All files (*)",
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
    def _on_plot_triggered(self) -> None:
        self.controller.handle_plot()
        if self.controller.computed_df is None:
            return
        self._render_stereonet_canvas()

    def _on_plot_options_changed(self) -> None:
        if self.controller.computed_df is not None:
            self._render_stereonet_canvas()

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
        self._render_empty_canvas()
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
        else:
            self._render_empty_canvas()
        if self.controller.issues_df is not None:
            shown = min(len(self.controller.issues_df), self.MAX_PREVIEW_ROWS)
            self._append_log(f"Issues preview updated ({shown} rows shown).")
    def _render_empty_canvas(self) -> None:
        self.stereonet_figure.clear()
        placeholder_ax = self.stereonet_figure.add_subplot(111)
        placeholder_ax.axis("off")
        placeholder_ax.text(
            0.5,
            0.5,
            "Run Calculate, then Plot to render stereonet.",
            ha="center",
            va="center",
            fontsize=11,
        )
        self.stereonet_canvas.draw_idle()

    def _render_stereonet_canvas(self) -> None:
        if self.controller.computed_df is None:
            return

        projection_name = _MPL_PROJECTION_BY_CONFIG_NAME[
            self.projection_combo.currentText()
        ]
        polar_grid_enabled = self.polar_grid_checkbox.isChecked()
        plotted_df = self.controller.computed_df[
            self.controller.computed_df["dip"].notna()
            & self.controller.computed_df["strike"].notna()
        ]
        self.stereonet_figure.clear()
        ax = self.stereonet_figure.add_subplot(111, projection=projection_name)
        self.stereonet_figure.subplots_adjust(top=0.86)
        if polar_grid_enabled:
            self._add_polar_grid_overlay(ax)
        ax.pole(
            plotted_df["strike"].astype(float).to_numpy(copy=True),
            plotted_df["dip"].astype(float).to_numpy(copy=True),
            marker="o",
            linestyle="None",
            color="tab:blue",
            markersize=4,
        )
        self.stereonet_figure.suptitle(
            f"Stereonet ({self.projection_combo.currentText()})",
            y=0.98,
        )
        self.stereonet_canvas.draw_idle()
        self._append_log(
            "Plot updated: "
            f"{len(plotted_df)} row(s), "
            f"projection={self.projection_combo.currentText()}, "
            f"polar_grid={polar_grid_enabled}"
        )

    def _add_polar_grid_overlay(self, reference_ax: Any) -> None:
        left, bottom, width, height = reference_ax.get_position().bounds
        polar_ax = self.stereonet_figure.add_axes(
            [left, bottom, width, height], projection="polar"
        )
        polar_ax.set_theta_zero_location("N")
        polar_ax.set_theta_direction(-1)
        polar_ax.set_rlim(0.0, 90.0)
        polar_ax.set_thetagrids(list(range(0, 360, 30)))
        polar_ax.set_rticks(list(range(10, 91, 10)))
        polar_ax.set_xticklabels([])
        polar_ax.set_yticklabels([])
        polar_ax.grid(True, linestyle=":", linewidth=0.6, color="0.75")
        polar_ax.patch.set_alpha(0.0)
        for spine in polar_ax.spines.values():
            spine.set_visible(False)
        polar_ax.set_zorder(0)
        reference_ax.set_zorder(1)
        reference_ax.set_facecolor("none")

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
