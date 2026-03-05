
import numpy as np

# Simplified surrogate E-field score model.
# Not a biophysical FEM; suitable for educational optimization demos.


def attenuation_factor(hair_thickness_mm, coil_height_mm, skull_thickness_mm):
    # Simple attenuation from lift and skull; normalized 0..1
    # Larger lift and skull thickness reduce score.
    lift = hair_thickness_mm + coil_height_mm
    # Tunable constants
    a_lift = 0.02  # per mm
    a_skull = 0.05  # per mm
    A = np.exp(-a_lift * max(lift, 0.0)) * np.exp(-a_skull * max(skull_thickness_mm, 0.0))
    return A


def efield_score(xc, yc, xt, yt, coil_angle_deg, params):
    """
    xc, yc: coil center (mm)
    xt, yt: target location (mm)
    coil_angle_deg: orientation angle (deg). 0=+y (anterior) for clinical familiarity.
    params: dict of modeling constants
    """
    # Distance term
    dx = xt - xc
    dy = yt - yc
    d = np.hypot(dx, dy) + 1e-6

    # Convert convention: define 0 deg as anterior (+y), increasing clockwise.
    # Our dx,dy angle from coil to target relative to +y axis:
    angle_to_target = np.degrees(np.arctan2(dx, dy))  # swap to make 0 along +y
    # Alignment term
    alpha = np.deg2rad(((angle_to_target - coil_angle_deg + 180) % 360) - 180)
    alignment = np.cos(alpha)
    alignment = max(alignment, 0.0)  # negative alignment not helpful

    # Distance weighting (inverse-square softened + exponential falloff)
    d0 = params.get('d0', 10.0)
    lam = params.get('lambda_mm', 30.0)
    dist_term = np.exp(-d / lam) / (d + d0)**2

    # Attenuation
    A = attenuation_factor(
        params['hair_thickness_mm'], params['coil_height_mm'], params['skull_thickness_mm']
    )

    K = params.get('K', 1.0)
    score = K * alignment * dist_term * A
    return score
