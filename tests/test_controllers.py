import unittest

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

    def test_handle_export_after_import_sets_placeholder_path(self):
        statuses: list[str] = []
        errors: list[str] = []
        controller = MainWindowController(
            status_sink=statuses.append,
            error_sink=errors.append,
        )
        controller.handle_import("sample_data/milestone1_input.csv")

        controller.handle_export()

        self.assertEqual(errors, [])
        self.assertIsNotNone(controller.last_export_path)
        self.assertEqual(controller.last_export_path.name, "export_placeholder.csv")
        self.assertIn("Export action triggered", statuses[-1])
