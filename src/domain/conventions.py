"""Measurement convention definitions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Convention:
    name: str
    alpha_min: float
    alpha_max: float
    beta_min: float
    beta_max: float
    trend_min: float
    trend_max: float
    plunge_min: float
    plunge_max: float
    reference_line_default: float
    notes: str


BUILTIN_CONVENTIONS = {
    "oriented_core_bottom_ref": Convention(
        name="oriented_core_bottom_ref",
        alpha_min=0.0,
        alpha_max=90.0,
        beta_min=0.0,
        beta_max=360.0,

        trend_min=0.0,
        trend_max=360.0,
        plunge_min=0.0,
        plunge_max=90.0,
        reference_line_default=180.0,
        notes=(
            "Assumes plunge is positive downward. Alpha is the angle between plane and "
            "core axis (0-90). Beta is the clockwise downhole angle from the reference "
            "line to the lower-ellipse long axis (0-360). Core reference line defaults "
            "to bottom-of-core (180°)."
        ),
    ),
    "oriented_core_top_ref": Convention(
        name="oriented_core_top_ref",
        alpha_min=0.0,
        alpha_max=90.0,
        beta_min=0.0,
        beta_max=360.0,
        trend_min=0.0,
        trend_max=360.0,
        plunge_min=0.0,
        plunge_max=90.0,
        reference_line_default=0.0,
        notes=(
            "Same convention as oriented_core_bottom_ref, but defaults core reference "
            "line to top-of-core (0°)."
        ),
    ),
}


def get_convention(convention_name: str) -> Convention:
    """Return a built-in convention by name."""
    if convention_name not in BUILTIN_CONVENTIONS:
        available = ", ".join(sorted(BUILTIN_CONVENTIONS))
        raise ValueError(
            f"Unknown convention '{convention_name}'. Available conventions: {available}"
        )
    return BUILTIN_CONVENTIONS[convention_name]

