
import numpy as np

# Coordinate system (top view):
# x: +right, -left ; y: +anterior, -posterior ; origin at vertex (Cz)


def within_head(x, y, head_radius_mm):
    r = np.sqrt(x**2 + y**2)
    return r <= head_radius_mm


def polar_from_xy(x, y):
    r = np.hypot(x, y)
    theta = np.degrees(np.arctan2(y, x))  # deg, 0 along +x
    return r, theta


def angle_diff_deg(a, b):
    # smallest signed difference a-b in [-180, 180]
    d = (a - b + 180) % 360 - 180
    return d
