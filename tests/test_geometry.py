import math
import unittest

from src.domain.structural_calculations import alpha_beta_to_orientation


class TestGeometry(unittest.TestCase):
    def test_matches_workbook_case_row2(self):
        result = alpha_beta_to_orientation(
            alpha=60.0,
            beta=10.0,
            trend_of_hole=180.0,
            plunge_of_hole=60.0,
            reference_line=180.0,
        )
        self.assertEqual(result.dip, 59.0)
        self.assertEqual(result.dip_direction, 5.0)
        self.assertEqual(result.strike, 275.0)

    def test_matches_workbook_case_row6(self):
        result = alpha_beta_to_orientation(
            alpha=35.0,
            beta=186.0,
            trend_of_hole=180.0,
            plunge_of_hole=60.0,
            reference_line=180.0,
        )
        self.assertEqual(result.dip, 25.0)
        self.assertEqual(result.dip_direction, 191.0)
        self.assertEqual(result.strike, 101.0)

    def test_pole_is_normalized(self):
        result = alpha_beta_to_orientation(
            alpha=35.0,
            beta=40.0,
            trend_of_hole=110.0,
            plunge_of_hole=20.0,
            reference_line=180.0,
        )
        magnitude = math.sqrt(
            result.pole_east**2 + result.pole_north**2 + result.pole_up**2
        )
        self.assertAlmostEqual(magnitude, 1.0, places=9)

