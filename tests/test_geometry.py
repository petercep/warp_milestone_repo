import math
import unittest

from src.domain.structural_calculations import alpha_beta_to_orientation


class TestGeometry(unittest.TestCase):
    def test_alpha_beta_vertical_plane_from_horizontal_core(self):
        result = alpha_beta_to_orientation(
            alpha=90.0,
            beta=0.0,
            trend_of_hole=0.0,
            plunge_of_hole=0.0,
            reference_line=0.0,
        )
        self.assertAlmostEqual(result.dip, 90.0, places=6)
        self.assertAlmostEqual(result.dip_direction, 180.0, places=6)
        self.assertAlmostEqual(result.strike, 90.0, places=6)

    def test_alpha_beta_parallel_plane_from_horizontal_core(self):
        result = alpha_beta_to_orientation(
            alpha=0.0,
            beta=0.0,
            trend_of_hole=0.0,
            plunge_of_hole=0.0,
            reference_line=0.0,
        )
        self.assertAlmostEqual(result.dip, 90.0, places=6)
        self.assertAlmostEqual(result.dip_direction, 90.0, places=6)
        self.assertAlmostEqual(result.strike, 0.0, places=6)

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

