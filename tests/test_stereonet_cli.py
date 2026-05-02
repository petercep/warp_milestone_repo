import unittest

from src.app.stereonet_cli import build_parser
from src.config.defaults import (
    DEFAULT_STEREONET_POLAR_GRID,
    DEFAULT_STEREONET_PROJECTION,
)


class TestStereonetCli(unittest.TestCase):
    def test_parser_defaults_projection_and_polar_grid_from_config(self):
        parser = build_parser()
        args = parser.parse_args(["--input", "in.csv", "--output", "out.png"])
        self.assertEqual(args.projection, DEFAULT_STEREONET_PROJECTION)
        self.assertEqual(args.polar_grid, DEFAULT_STEREONET_POLAR_GRID)

    def test_parser_supports_projection_and_polar_grid_overrides(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "--input",
                "in.csv",
                "--output",
                "out.png",
                "--projection",
                "equal-angle",
                "--polar-grid",
            ]
        )
        self.assertEqual(args.projection, "equal-angle")
        self.assertTrue(args.polar_grid)
