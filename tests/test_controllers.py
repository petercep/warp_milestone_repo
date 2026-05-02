import unittest
from pathlib import Path
import tempfile

import pandas as pd

from src.app.controllers import MainWindowController


class TestMainWindowController(unittest.TestCase):
    def test_handle_import_sets_selected_input_and_emits_status(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )

        controller.handle_import("sample_data/milestone1_input.csv")

        self.assertTrue(statuses)
        self.assertIn("Import complete:", statuses[-1])
        self.assertEqual(errors, [])
        self.assertIsNotNone(controller.selected_input_path)
        self.assertIsNotNone(controller.imported_df)
        self.assertGreater(len(controller.imported_df), 0)

    def test_handle_import_with_missing_file_emits_error(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )

        controller.handle_import("sample_data/does_not_exist.csv")

        self.assertEqual(statuses, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("Input file not found:", errors[0])
        self.assertIsNone(controller.selected_input_path)
        self.assertIsNone(controller.imported_df)

    def test_handle_import_with_unsupported_type_emits_error(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )

        controller.handle_import("pyproject.toml")

        self.assertEqual(statuses, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("Import failed", errors[0])
        self.assertIsNone(controller.selected_input_path)
        self.assertIsNone(controller.imported_df)

    def test_handle_calculate_without_import_emits_error(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )

        controller.handle_calculate()

        self.assertEqual(statuses, [])
        self.assertEqual(errors, ["No input file selected. Use Import first."])

    def test_handle_calculate_after_import_computes_orientations(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )
        controller.handle_import("sample_data/milestone1_input.csv")

        controller.handle_calculate()

        self.assertEqual(errors, [])
        self.assertIn("Calculate complete:", statuses[-1])
        self.assertIsNotNone(controller.last_calculation_summary)
        self.assertIsNotNone(controller.computed_df)
        self.assertTrue(
            {"dip", "dip_direction", "strike"}.issubset(controller.computed_df.columns)
        )

    def test_handle_calculate_with_invalid_data_emits_error(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )
        controller.handle_import("sample_data/milestone1_input.csv")
        controller.handle_calculate()
        self.assertIsNotNone(controller.last_calculation_summary)
        status_count_before_failure = len(statuses)

        controller.selected_input_path = Path("dummy.csv")
        controller.imported_df = pd.DataFrame([{"bad_col": 1}])

        controller.handle_calculate()

        self.assertEqual(len(statuses), status_count_before_failure)
        self.assertEqual(len(errors), 1)
        self.assertIn("Calculate failed:", errors[0])
        self.assertIsNone(controller.computed_df)
        self.assertIsNone(controller.last_calculation_summary)

    def test_handle_calculate_summary_with_mixed_valid_invalid_rows(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )
        controller.selected_input_path = Path("mixed.csv")
        controller.imported_df = pd.DataFrame(
            [
                {
                    "hole_id": "A",
                    "depth": 1.0,
                    "alpha": 15.0,
                    "beta": 35.0,
                    "trend_of_hole": 45.0,
                    "plunge_of_hole": 10.0,
                    "core_orientation_reference": 180.0,
                },
                {
                    "hole_id": "B",
                    "depth": 2.0,
                    "alpha": 145.0,
                    "beta": 35.0,
                    "trend_of_hole": 45.0,
                    "plunge_of_hole": 10.0,
                    "core_orientation_reference": 180.0,
                },
            ]
        )

        controller.handle_calculate()

        self.assertEqual(errors, [])
        self.assertIsNotNone(controller.last_calculation_summary)
        self.assertEqual(
            controller.last_calculation_summary,
            {"input_rows": 2, "valid_rows": 1, "invalid_rows": 1, "issues_count": 1},
        )
        self.assertIn("Calculate complete:", statuses[-1])

    def test_handle_import_failure_clears_previous_calculation_state(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )
        controller.handle_import("sample_data/milestone1_input.csv")
        controller.handle_calculate()
        self.assertIsNotNone(controller.last_calculation_summary)
        controller.last_export_path = Path("dummy_computed.csv")
        controller.last_issues_export_path = Path("dummy_issues.csv")

        controller.handle_import("sample_data/does_not_exist.csv")

        self.assertEqual(len(errors), 1)
        self.assertIn("Input file not found:", errors[0])
        self.assertIsNone(controller.imported_df)
        self.assertIsNone(controller.computed_df)
        self.assertIsNone(controller.last_calculation_summary)
        self.assertIsNone(controller.last_export_path)
        self.assertIsNone(controller.last_issues_export_path)

    def test_handle_plot_without_calculate_emits_error(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )
        controller.handle_import("sample_data/milestone1_input.csv")

        controller.handle_plot()

        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[-1], "No calculated results available. Use Calculate first."
        )
        self.assertNotIn("Plot action triggered", " ".join(statuses))

    def test_handle_plot_after_calculate_emits_status(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )
        controller.handle_import("sample_data/milestone1_input.csv")
        controller.handle_calculate()

        controller.handle_plot()

        self.assertEqual(errors, [])
        self.assertIn("Plot action triggered for", statuses[-1])

    def test_handle_export_without_calculate_emits_error(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )
        controller.handle_import("sample_data/milestone1_input.csv")

        controller.handle_export()
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[-1], "No calculated results available. Use Calculate first."
        )
        self.assertIsNone(controller.last_export_path)
        self.assertIsNone(controller.last_issues_export_path)

    def test_handle_export_after_calculate_writes_output_files(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "input.csv"
            input_df = pd.DataFrame(
                [
                    {
                        "hole_id": "A",
                        "depth": 1.0,
                        "alpha": 15.0,
                        "beta": 35.0,
                        "trend_of_hole": 45.0,
                        "plunge_of_hole": 10.0,
                        "core_orientation_reference": 180.0,
                    },
                    {
                        "hole_id": "B",
                        "depth": 2.0,
                        "alpha": 145.0,
                        "beta": 35.0,
                        "trend_of_hole": 45.0,
                        "plunge_of_hole": 10.0,
                        "core_orientation_reference": 180.0,
                    },
                ]
            )
            input_df.to_csv(input_path, index=False)

            controller.handle_import(str(input_path))
            controller.handle_calculate()
            controller.handle_export()

            self.assertEqual(errors, [])
            self.assertIn("Export complete:", statuses[-1])
            self.assertIsNotNone(controller.last_export_path)
            self.assertIsNotNone(controller.last_issues_export_path)
            self.assertTrue(controller.last_export_path.exists())
            self.assertTrue(controller.last_issues_export_path.exists())

            exported_computed = pd.read_csv(controller.last_export_path)
            exported_issues = pd.read_csv(controller.last_issues_export_path)
            self.assertTrue(
                {"dip", "dip_direction", "strike"}.issubset(exported_computed.columns)
            )
            self.assertGreaterEqual(len(exported_issues), 1)
