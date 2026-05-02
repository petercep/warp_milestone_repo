import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.viz.stereonet import filter_computed_rows, plot_poles


class TestStereonet(unittest.TestCase):
    def test_filter_computed_rows_drops_missing_and_applies_filters(self):
        df = pd.DataFrame(
            [
                {"hole_id": "A", "dip": 35.0, "dip_direction": 120.0, "strike": 30.0},
                {"hole_id": "A", "dip": None, "dip_direction": 100.0, "strike": 10.0},
                {"hole_id": "B", "dip": 25.0, "dip_direction": 200.0, "strike": 110.0},
            ]
        )
        filtered = filter_computed_rows(df, filters={"hole_id": "A"})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["hole_id"], "A")

    def test_plot_poles_exports_png(self):
        df = pd.DataFrame(
            [
                {"hole_id": "A", "dip": 35.0, "dip_direction": 120.0, "strike": 30.0},
                {"hole_id": "B", "dip": 50.0, "dip_direction": 210.0, "strike": 120.0},
            ]
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir) / "stereonet.png"
            plot_poles(df, out, title="Test")
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 0)

    def test_plot_poles_exports_png_with_polar_grid(self):
        df = pd.DataFrame(
            [
                {"hole_id": "A", "dip": 35.0, "dip_direction": 120.0, "strike": 30.0},
                {"hole_id": "B", "dip": 50.0, "dip_direction": 210.0, "strike": 120.0},
            ]
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir) / "stereonet_polar_grid.png"
            plot_poles(df, out, title="Test", polar_grid=True)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 0)

    def test_plot_poles_exports_png_equal_angle_projection(self):
        df = pd.DataFrame(
            [
                {"hole_id": "A", "dip": 35.0, "dip_direction": 120.0, "strike": 30.0},
                {"hole_id": "B", "dip": 50.0, "dip_direction": 210.0, "strike": 120.0},
            ]
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir) / "stereonet_equal_angle.png"
            plot_poles(df, out, title="Test", projection="equal-angle")
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 0)

    def test_plot_poles_rejects_invalid_projection(self):
        df = pd.DataFrame(
            [
                {"hole_id": "A", "dip": 35.0, "dip_direction": 120.0, "strike": 30.0},
                {"hole_id": "B", "dip": 50.0, "dip_direction": 210.0, "strike": 120.0},
            ]
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir) / "stereonet_invalid_projection.png"
            with self.assertRaises(ValueError):
                plot_poles(df, out, title="Test", projection="not-a-projection")
