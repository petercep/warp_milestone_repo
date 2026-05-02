import unittest

import pandas as pd

from src.data.validation import validate_dataframe
from src.domain.conventions import get_convention


class TestValidation(unittest.TestCase):
    def test_validation_splits_valid_and_invalid_rows(self):
        df = pd.DataFrame(
            [
                {
                    "hole_id": "A",
                    "depth": 10,
                    "alpha": 20,
                    "beta": 40,
                    "trend_of_hole": 100,
                    "plunge_of_hole": 30,
                    "core_orientation_reference": None,
                },
                {
                    "hole_id": "B",
                    "depth": 13,
                    "alpha": "bad",
                    "beta": 400,
                    "trend_of_hole": 400,
                    "plunge_of_hole": -1,
                    "core_orientation_reference": 180,
                },
            ]
        )

        valid_df, issues_df = validate_dataframe(
            df, get_convention("oriented_core_bottom_ref")
        )

        self.assertEqual(len(valid_df), 1)
        self.assertGreaterEqual(len(issues_df), 4)
        self.assertEqual(valid_df.iloc[0]["core_orientation_reference"], 180.0)

    def test_validation_requires_columns(self):
        df = pd.DataFrame([{"hole_id": "A"}])
        with self.assertRaises(ValueError) as ctx:
            validate_dataframe(df, get_convention("oriented_core_bottom_ref"))
        self.assertIn("Missing required columns", str(ctx.exception))

