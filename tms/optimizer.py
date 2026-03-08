
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from .geometry import within_head
from .models import efield_score
from .visualization import plot_heatmap


def optimize_for_row(row, outdir: Path):
    # Unpack
    R = row['head_radius_mm']
    xt = row['target_offset_lateral_mm']
    yt = row['target_offset_anterior_mm']
    search_r = row['search_radius_mm']
    step = row['grid_step_mm']
    preferred_angle = row['preferred_orientation_deg']  # deg, 0 = +y

    # Build grid of candidate coil centers around the target
    xs = np.arange(xt - search_r, xt + search_r + 1e-6, step)
    ys = np.arange(yt - search_r, yt + search_r + 1e-6, step)

    # Parameter bundle
    params = {
        'hair_thickness_mm': row['hair_thickness_mm'],
        'coil_height_mm': row['coil_height_mm'],
        'skull_thickness_mm': row['skull_thickness_mm'],
        'd0': 10.0,
        'lambda_mm': 30.0,
        'K': 1.0,
    }

    coords = []
    scores = []
    angles = []

    for y in ys:
        for x in xs:
            # Candidate must lie on scalp (within head outline)
            if not within_head(x, y, R):
                continue
            # Use preferred angle for now; could also scan small angle neighborhood
            angle = preferred_angle
            s = efield_score(x, y, xt, yt, angle, params)
            coords.append((x, y))
            scores.append(s)
            angles.append(angle)

    if not coords:
        raise ValueError('No valid candidate positions fell within the head outline. Check search radius and target offsets.')

    scores = np.array(scores)
    xs_list = np.array([c[0] for c in coords])
    ys_list = np.array([c[1] for c in coords])

    # Best
    best_idx = int(np.argmax(scores))
    best_x = float(xs_list[best_idx])
    best_y = float(ys_list[best_idx])
    best_angle = float(angles[best_idx])
    best_score = float(scores[best_idx])

    # Save results table
    dt = datetime.now().strftime('%Y%m%d_%H%M%S')
    tag = f"{row['target_name']}_{dt}"
    df = pd.DataFrame({
        'x_mm': xs_list,
        'y_mm': ys_list,
        'score': scores,
        'angle_deg': angles
    })

    results_csv = outdir / f"{tag}_results.csv"
    df.to_csv(results_csv, index=False)

    # Plot heatmap
    fig_path = outdir / f"{tag}_heatmap.png"
    plot_heatmap(
        xs_list, ys_list, scores,
        head_radius_mm=R,
        target_xy=(xt, yt),
        best_xy=(best_x, best_y),
        best_angle_deg=best_angle,
        title=f"Target: {row['target_name']} (best score={best_score:.3e})",
        outpath=fig_path
    )

    # Brief text report
    dx = best_x - xt
    dy = best_y - yt
    dist = np.hypot(dx, dy)
    report = outdir / f"{tag}_report.txt"
    with open(report, 'w') as f:
        f.write(
            f"TMS E-field optimizer (educational)"
            f"Target: {row['target_name']}"
            f"Head radius (mm): {R}"
            f"Best coil center (x_mm=+right, y_mm=+anterior): ({best_x:.1f}, {best_y:.1f})"
            f"Best orientation (deg; 0=anterior, +CW): {best_angle:.1f}"
            f"Distance from target (mm): {dist:.1f}"
            f"Estimated score (a.u.): {best_score:.3e}"
        )

    print(f"Saved: {results_csv}")
    print(f"Saved: {fig_path}")
    print(f"Saved: {report}")
