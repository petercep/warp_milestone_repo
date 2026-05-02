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


def _safe_atan_ratio(numerator: float, denominator: float) -> float:
    """Return atan(numerator / denominator) with division-by-zero guards."""
    if abs(denominator) < 1e-12:
        if numerator > 0:
            return math.pi / 2
        if numerator < 0:
            return -math.pi / 2
        return 0.0
    return math.atan(numerator / denominator)


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
    Compute a plane pole vector using the same transform sequence as
    workbook VBA function ConvAlphaBeta.

    Returned vector is ENU (east, north, up).
    """
    pi = math.pi
    g = reference_line_deg * pi / 180.0
    a_ = (90.0 - alpha_deg) * pi / 180.0
    b_ = beta_deg * pi / 180.0
    an = plunge_deg * pi / 180.0
    bn = trend_deg * pi / 180.0

    xd = math.cos(a_)
    yd = -math.sin(a_) * math.cos(b_)
    zd = -math.sin(a_) * math.sin(b_)

    x = xd
    y = math.cos(g) * yd - math.sin(g) * zd
    z = math.sin(g) * yd + math.cos(g) * zd

    north = (
        math.cos(an) * math.cos(bn) * x
        + math.sin(an) * math.cos(bn) * y
        - math.sin(bn) * z
    )
    east = (
        math.cos(an) * math.sin(bn) * x
        + math.sin(an) * math.sin(bn) * y
        + math.cos(bn) * z
    )
    up = -math.sin(an) * x + math.cos(an) * y

    return normalize(np.array([east, north, up], dtype=float))


def azimuth_from_en(east: float, north: float) -> float:
    """Return azimuth in degrees [0, 360)."""
    return (math.degrees(math.atan2(east, north)) + 360.0) % 360.0


def pole_to_plane_orientation(pole: np.ndarray) -> tuple[float, float, float]:
    """
    Convert pole vector to dip, dip direction, and strike using
    VBA ConvAlphaBeta dip/direction correction logic.
    """
    pole = normalize(pole)
    east, north, up = float(pole[0]), float(pole[1]), float(pole[2])

    if north >= 0 and east >= 0:
        q = 0.0
    elif north <= 0 and east >= 0:
        q = 180.0
    elif north >= 0 and east <= 0:
        q = 360.0
    else:
        q = 180.0

    horizontal = math.sqrt(north**2 + east**2)
    dip_temp = 90.0 - math.degrees(_safe_atan_ratio(up, horizontal))
    if dip_temp > 90.0:
        dip = 180.0 - dip_temp
    else:
        dip = dip_temp

    q2 = 180.0 if (dip_temp > 90.0 or dip_temp < 0.0) else 0.0
    dirn_temp = q + q2 + math.degrees(_safe_atan_ratio(east, north))
    if dirn_temp > 360.0:
        dip_direction = dirn_temp - 360.0
    elif dirn_temp < 0.0:
        dip_direction = dirn_temp + 360.0
    else:
        dip_direction = dirn_temp

    dip = float(int(dip))
    dip_direction = float(int(dip_direction))
    strike = (dip_direction - 90.0) % 360.0
    return dip, dip_direction, strike

