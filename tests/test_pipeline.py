import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.app.cli import run_pipeline


class TestPipeline(unittest.TestCase):
    def test_pipeline_creates_outputs(self):
        input_df = pd.DataFrame(
            [
                {
                    "hole_id": "X",
                    "depth": 1.0,
                    "alpha": 15.0,
                    "beta": 35.0,
                    "trend_of_hole": 45.0,
                    "plunge_of_hole": 10.0,
                    "core_orientation_reference": 180.0,
                },
                {
                    "hole_id": "Y",
                    "depth": 3.0,
                    "alpha": 145.0,
                    "beta": 45.0,
                    "trend_of_hole": 30.0,
                    "plunge_of_hole": 15.0,
                    "core_orientation_reference": 180.0,
                },
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_path = tmp_path / "input.csv"
            output_path = tmp_path / "output.csv"
            errors_path = tmp_path / "errors.csv"
            input_df.to_csv(input_path, index=False)

            summary = run_pipeline(
                input_path=input_path,
                output_path=output_path,
                convention_name="oriented_core_bottom_ref",
                errors_path=errors_path,
            )

            self.assertTrue(output_path.exists())
            self.assertTrue(errors_path.exists())
            self.assertEqual(summary["input_rows"], 2)
            self.assertEqual(summary["valid_rows"], 1)
            self.assertEqual(summary["invalid_rows"], 1)

            out_df = pd.read_csv(output_path)
            self.assertTrue(
                {"dip", "dip_direction", "strike"}.issubset(out_df.columns)
            )
