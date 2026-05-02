"""Milestone 2 stereonet plotting CLI."""

from __future__ import annotations

import argparse

from src.config.defaults import (
    DEFAULT_STEREONET_POLAR_GRID,
    DEFAULT_STEREONET_PROJECTION,
    SUPPORTED_STEREONET_PROJECTIONS,
)
from src.data.io import load_table
from src.viz.stereonet import plot_poles


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot computed poles on a stereonet.")
    parser.add_argument("--input", required=True, help="Computed CSV/XLSX input file.")
    parser.add_argument("--output", required=True, help="Output plot file (.png or .svg).")
    parser.add_argument("--title", default=None, help="Optional plot title.")
    parser.add_argument("--hole-id", default=None, help="Optional hole_id filter.")
    parser.add_argument(
        "--projection",
        default=DEFAULT_STEREONET_PROJECTION,
        choices=sorted(SUPPORTED_STEREONET_PROJECTIONS),
        help=(
            "Stereonet projection mode "
            f"(default: {DEFAULT_STEREONET_PROJECTION})."
        ),
    )
    parser.add_argument(
        "--polar-grid",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_STEREONET_POLAR_GRID,
        help=(
            "Enable/disable polar-style grid overlay beneath the stereonet "
            f"(default: {DEFAULT_STEREONET_POLAR_GRID})."
        ),
    )
    parser.add_argument(
        "--structure-type", default=None, help="Optional structure_type filter."
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    filters = {}
    if args.hole_id is not None:
        filters["hole_id"] = args.hole_id
    if args.structure_type is not None:
        filters["structure_type"] = args.structure_type

    df = load_table(args.input)
    out = plot_poles(
        df,
        output_path=args.output,
        filters=filters or None,
        title=args.title,
        projection=args.projection,
        polar_grid=args.polar_grid,
    )
    print(f"Stereonet export complete: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

