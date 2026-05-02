"""Milestone 1 CLI pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.config.defaults import DEFAULT_CONVENTION_NAME, DEFAULT_OUTPUT_FILE
from src.data.io import load_table, save_table
from src.data.validation import validate_dataframe
from src.domain.conventions import BUILTIN_CONVENTIONS, get_convention
from src.domain.structural_calculations import compute_orientations


def run_pipeline(
    input_path: str | Path,
    output_path: str | Path,
    convention_name: str,
    errors_path: str | Path | None = None,
) -> dict[str, int]:
    """Run import -> validate -> compute -> export."""
    convention = get_convention(convention_name)

    raw_df = load_table(input_path)
    valid_df, issues_df = validate_dataframe(raw_df, convention)
    computed_df = compute_orientations(valid_df)

    output = Path(output_path)
    save_table(computed_df, output)

    errors_output = (
        Path(errors_path)
        if errors_path is not None
        else output.with_name(f"{output.stem}_validation_errors.csv")
    )
    save_table(issues_df, errors_output)

    invalid_row_count = (
        int(issues_df["source_row"].nunique()) if not issues_df.empty else 0
    )
    return {
        "input_rows": int(len(raw_df)),
        "valid_rows": int(len(computed_df)),
        "invalid_rows": invalid_row_count,
        "issues_count": int(len(issues_df)),
    }


def build_parser() -> argparse.ArgumentParser:
    """Create CLI parser."""
    parser = argparse.ArgumentParser(
        description="Milestone 1 pipeline: import, validate, compute, export."
    )
    parser.add_argument("--input", required=True, help="Input CSV/XLSX path.")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT_FILE}).",
    )
    parser.add_argument(
        "--errors-output",
        default=None,
        help="Validation issue CSV path (default: <output>_validation_errors.csv).",
    )
    parser.add_argument(
        "--convention",
        default=DEFAULT_CONVENTION_NAME,
        choices=sorted(BUILTIN_CONVENTIONS),
        help=f"Measurement convention (default: {DEFAULT_CONVENTION_NAME}).",
    )
    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    summary = run_pipeline(
        input_path=args.input,
        output_path=args.output,
        convention_name=args.convention,
        errors_path=args.errors_output,
    )

    print(
        "Pipeline complete "
        f"(input={summary['input_rows']}, "
        f"valid={summary['valid_rows']}, "
        f"invalid={summary['invalid_rows']}, "
        f"issues={summary['issues_count']})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

