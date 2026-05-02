"""Low-level geometric helpers."""

from __future__ import annotations

import math

import numpy as np


def normalize(vector: np.ndarray) -> np.ndarray:
    """Return a unit vector."""
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("Cannot normalize a zero-length vector.")
    return vector / norm


def trend_plunge_to_vector(trend_deg: float, plunge_deg: float) -> np.ndarray:
    """
    Convert trend/plunge to an ENU vector.
    Trend is azimuth from north, clockwise.
    Plunge is positive downward.
    """
    trend = math.radians(trend_deg)
    plunge = math.radians(plunge_deg)

    horizontal = math.cos(plunge)
    east = horizontal * math.sin(trend)
    north = horizontal * math.cos(trend)
    up = -math.sin(plunge)

    return normalize(np.array([east, north, up], dtype=float))


def build_core_frame(core_axis: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Build orthonormal vectors perpendicular to core_axis.
    Returns (e1, e2) where e2 = core_axis x e1.
    """
    up = np.array([0.0, 0.0, 1.0], dtype=float)
    if abs(np.dot(core_axis, up)) > 0.98:
        up = np.array([0.0, 1.0, 0.0], dtype=float)

    e1 = normalize(np.cross(up, core_axis))
    e2 = normalize(np.cross(core_axis, e1))
    return e1, e2


def pole_from_alpha_beta(
    trend_deg: float,
    plunge_deg: float,
    alpha_deg: float,
    beta_deg: float,
    reference_line_deg: float,
) -> np.ndarray:
    """
    Compute a plane pole vector from alpha/beta and core orientation.
    Alpha is the angle between plane and core axis (0-90).
    Beta is clockwise downhole angle from reference line (0-360).
    """
    axis = trend_plunge_to_vector(trend_deg, plunge_deg)
    e1, e2 = build_core_frame(axis)
    alpha = math.radians(alpha_deg)
    beta = math.radians((reference_line_deg - beta_deg) % 360.0)

    radial = math.cos(beta) * e1 + math.sin(beta) * e2
    pole = math.sin(alpha) * axis + math.cos(alpha) * radial
    return normalize(pole)


def azimuth_from_en(east: float, north: float) -> float:
    """Return azimuth in degrees [0, 360)."""
    return (math.degrees(math.atan2(east, north)) + 360.0) % 360.0


def pole_to_plane_orientation(pole: np.ndarray) -> tuple[float, float, float]:
    """Convert a pole vector to dip, dip direction, and strike."""
    pole = normalize(pole)
    if pole[2] < 0:
        pole = -pole

    horizontal = math.hypot(pole[0], pole[1])
    dip = math.degrees(math.atan2(horizontal, pole[2]))
    pole_azimuth = azimuth_from_en(pole[0], pole[1])
    dip_direction = (pole_azimuth + 180.0) % 360.0
    strike = (dip_direction - 90.0) % 360.0
    return dip, dip_direction, strike

