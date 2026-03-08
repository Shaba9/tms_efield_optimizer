
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrow

def plot_heatmap(xs, ys, scores, head_radius_mm, target_xy, best_xy, best_angle_deg, title, outpath):
    xs = np.asarray(xs); ys = np.asarray(ys); scores = np.asarray(scores)

    grid_step = max(2.0, np.min(np.diff(np.unique(xs))) if len(np.unique(xs))>1 else 5.0)
    xi = np.arange(-head_radius_mm, head_radius_mm + 1e-6, grid_step)
    yi = np.arange(-head_radius_mm, head_radius_mm + 1e-6, grid_step)
    XI, YI = np.meshgrid(xi, yi)

    Z = np.zeros_like(XI)
    for i in range(XI.shape[0]):
        for j in range(XI.shape[1]):
            x0, y0 = XI[i, j], YI[i, j]
            d2 = (xs - x0)**2 + (ys - y0)**2
            w = 1.0 / (d2 + 1e-6)
            Z[i, j] = np.sum(w * scores) / np.sum(w)

    mask = (XI**2 + YI**2) > head_radius_mm**2
    Z = np.ma.array(Z, mask=mask)

    fig, ax = plt.subplots(figsize=(7, 7))
    im = ax.pcolormesh(XI, YI, Z, cmap=plt.cm.inferno, shading='auto')
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label('|E| at target (V/m)')

    head = Circle((0, 0), radius=head_radius_mm, edgecolor='white', facecolor='none', lw=2)
    ax.add_patch(head)

    tx, ty = target_xy
    ax.plot([tx], [ty], marker='x', color='cyan', markersize=10, label='Target (0,0)')

    bx, by = best_xy
    ax.plot([bx], [by], marker='o', color='lime', markersize=8, label='Best')

    ang = np.deg2rad(best_angle_deg)
    vx, vy = np.sin(ang), np.cos(ang)
    L = max(20.0, head_radius_mm * 0.2)
    ax.add_patch(FancyArrow(bx, by, vx*L, vy*L, width=2.0, head_width=8.0, head_length=8.0,
                            color='lime', length_includes_head=True))

    ax.set_aspect('equal')
    ax.set_title(title)
    ax.set_xlabel('ΔLateral (mm, +right)')
    ax.set_ylabel('ΔAnterior (mm, +anterior)')

    dist = np.hypot(bx - tx, by - ty)
    txt = f"Angle: {best_angle_deg:.0f}°  |  Δx={bx-tx:.1f} mm  Δy={by-ty:.1f} mm  |  d={dist:.1f} mm"
    ax.text(0.02, 0.02, txt, transform=ax.transAxes, fontsize=10, color='white',
            bbox=dict(facecolor='black', alpha=0.4, boxstyle='round'))

    ax.legend(loc='upper right')
    ax.set_xlim(-head_radius_mm*1.05, head_radius_mm*1.05)
    ax.set_ylim(-head_radius_mm*1.05, head_radius_mm*1.05)

    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)
