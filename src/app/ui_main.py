"""Milestone 3 desktop UI scaffold (main window + action wiring)."""

from __future__ import annotations

import sys

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
    )
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local UI deps
    raise RuntimeError(
        "PySide6 is required to run the desktop UI scaffold. "
        "Install it before launching src.app.ui_main."
    ) from exc


class MainWindow(QMainWindow):
    """Initial desktop shell for Milestone 3."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Geology Workstation - Milestone 3 Scaffold")
        self.resize(980, 680)

        self.status_label = QLabel("Ready. Use Import to select input data.")
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
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

        layout.addWidget(self.canvas_placeholder)
        layout.addWidget(self.log_output)
        self.setCentralWidget(container)

        self.import_btn.clicked.connect(self._on_import_triggered)
        self.calculate_btn.clicked.connect(self.controller.handle_calculate)
        self.plot_btn.clicked.connect(self.controller.handle_plot)
        self.export_btn.clicked.connect(self.controller.handle_export)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Actions")
        self.addToolBar(toolbar)

        import_action = toolbar.addAction("Import")
        calculate_action = toolbar.addAction("Calculate")
        plot_action = toolbar.addAction("Plot")
        export_action = toolbar.addAction("Export")

        import_action.triggered.connect(self._on_import_triggered)
        calculate_action.triggered.connect(self.controller.handle_calculate)
        plot_action.triggered.connect(self.controller.handle_plot)
        export_action.triggered.connect(self.controller.handle_export)

    def _on_import_triggered(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select input file",
            "",
            "Data files (*.csv *.xlsx *.xlsm);;All files (*)",
        )
        self.controller.handle_import(file_path or None)

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
