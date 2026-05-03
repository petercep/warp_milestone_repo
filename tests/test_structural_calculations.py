import unittest
from pathlib import Path

import pandas as pd

from src.domain.structural_calculations import compute_orientations


class TestStructuralCalculations(unittest.TestCase):
    def test_compute_orientations_matches_workbook_conv_alpha_beta_cases(self):
        repo_root = Path(__file__).resolve().parents[1]
        workbook_reference = pd.read_csv(
            repo_root
            / "sample_data"
            / "alfabeta_stereonet_review_equal_area_polar_labeled.csv"
        )
        input_df = workbook_reference[["trend", "plunge", "alpha", "beta", "ref"]].copy()

        computed = compute_orientations(input_df)

        self.assertEqual(
            computed["dip"].tolist(),
            workbook_reference["excel_dip"].astype(float).tolist(),
        )
        self.assertEqual(
            computed["dip_direction"].tolist(),
            workbook_reference["excel_dirn"].astype(float).tolist(),
        )
        self.assertIn("reference_line", computed.columns)
        self.assertNotIn("ref", computed.columns)
