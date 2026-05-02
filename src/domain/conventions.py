"""Convention definitions for alpha/beta interpretation and validation ranges."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Convention:
    """Validation ranges for alpha/beta measurements."""

    name: str
    alpha_min: float = 0.0
    alpha_max: float = 90.0
    beta_min: float = 0.0
    beta_max: float = 360.0


_CONVENTIONS: dict[str, Convention] = {
    "core_alpha_beta_v1": Convention(name="core_alpha_beta_v1")
}


def get_convention(name: str) -> Convention:
    """Resolve a convention profile by name."""
    try:
        return _CONVENTIONS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown convention '{name}'.") from exc
