
import math
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from .fem_backend import fem_run_single_pose, sample_E_at_target
from .visualization import plot_heatmap


def _grid_around_target_mni(target_mni, radius_mm, step_mm):
    xs = np.arange(-radius_mm, radius_mm + 1e-6, step_mm)
    ys = np.arange(-radius_mm, radius_mm + 1e-6, step_mm)
    grid = []
    for dy in ys:
        for dx in xs:
            x = target_mni[0] + dx
            y = target_mni[1] + dy
            z = target_mni[2]
            grid.append(((x,y,z), dx, dy))
    return grid


def _ydir_from_angle(center_mni, angle_deg, handle_len_mm=10.0):
    th = math.radians(angle_deg)
    vx = math.sin(th)
    vy = math.cos(th)
    x = center_mni[0] + handle_len_mm*vx
    y = center_mni[1] + handle_len_mm*vy
    z = center_mni[2]
    return (x,y,z)


def optimize_for_row_fem(row, outdir: Path):
    R = row['head_radius_mm']
    target_mni = row['target_mni']
    search_r = row['search_radius_mm']
    step = row['grid_step_mm']
    angle = row['preferred_orientation_deg']
    standoff = row['coil_height_mm'] + row['hair_thickness_mm']
    didt = row['didt_A_per_s']

    candidates = _grid_around_target_mni(target_mni, search_r, step)

    scores = []
    xs_mm = []
    ys_mm = []
    angles = []
    t0 = time.time()

    for (center_mni, dx, dy) in candidates:
        ydir_mni = _ydir_from_angle(center_mni, angle)
        epath, subj_target_mm = fem_run_single_pose(
            m2m_dir=row['m2m_dir'],
            head_mesh_name=row['head_mesh_name'],
            coil_file=row['coil_file'],
            center_mni=center_mni,
            ydir_mni=ydir_mni,
            distance_mm=standoff,
            didt_A_per_s=didt,
            map_to_vol=row['map_to_vol'],
            work_root=outdir / f"{row['target_name']}_fem"
        )
        e_vpm = sample_E_at_target(epath, subj_target_mm)
        scores.append(e_vpm)
        xs_mm.append(center_mni[0] - target_mni[0])
        ys_mm.append(center_mni[1] - target_mni[1])
        angles.append(angle)

    scores = np.array(scores)
    xs_arr = np.array(xs_mm)
    ys_arr = np.array(ys_mm)

    best_idx = int(np.argmax(scores))
    best_dx = xs_arr[best_idx]
    best_dy = ys_arr[best_idx]
    best_center_mni = (target_mni[0] + best_dx, target_mni[1] + best_dy, target_mni[2])
    best_angle = angles[best_idx]
    best_score = float(scores[best_idx])

    dt = datetime.now().strftime('%Y%m%d_%H%M%S')
    tag = f"{row['target_name']}_{dt}"
    df = pd.DataFrame({
        'dX_mm': xs_arr,
        'dY_mm': ys_arr,
        'E_V_per_m': scores,
        'angle_deg': angles
    })
    results_csv = outdir / f"{tag}_results.csv"
    df.to_csv(results_csv, index=False)

    fig_path = outdir / f"{tag}_heatmap.png"
    plot_heatmap(
        xs_arr, ys_arr, scores,
        head_radius_mm=R,
        target_xy=(0.0, 0.0),
        best_xy=(best_dx, best_dy),
        best_angle_deg=best_angle,
        title=f"Target: {row['target_name']} (best |E|={best_score:.2f} V/m)",
        outpath=fig_path
    )

    report = outdir / f"{tag}_report.txt"
    with open(report, 'w') as f:
        f.write(
            "TMS FEM optimizer (SimNIBS)
"
            f"Target: {row['target_name']}
"
            f"MNI target (mm): ({target_mni[0]:.1f}, {target_mni[1]:.1f}, {target_mni[2]:.1f})
"
            f"Best coil Δ from target (mm): ({best_dx:.1f}, {best_dy:.1f})  [x=+right, y=+anterior]
"
            f"Best orientation (deg; 0=anterior, +CW): {best_angle:.1f}
"
            f"Estimated |E| at target (V/m): {best_score:.2f}
"
            f"Standoff (hair+height) (mm): {standoff:.1f}
"
            f"dI/dt (A/s): {didt:.3e}
"
            f"SimNIBS m2m dir: {row['m2m_dir']}
"
            f"Head mesh: {row['head_mesh_name']}
"
            f"Coil file: {row['coil_file']}
"
        )

    print(f"Saved: {results_csv}")
    print(f"Saved: {fig_path}")
    print(f"Saved: {report}")
    print(f"FEM runs: {len(candidates)}  Elapsed: {time.time()-t0:.1f}s")
