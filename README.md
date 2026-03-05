
# TMS E-field Optimizer (Educational)

**Purpose:**
A lightweight, educational Python tool that simulates a simplified Transcranial Magnetic Stimulation (TMS) electric field (E-field) score at a target region while scanning multiple coil positions on the scalp. It produces a scalp heatmap that highlights a "hot spot" (best position) and overlays a head outline, a placement dot, an orientation arrow, and angle/distance labels.

> ⚠️ **Important**: This tool uses an **analytic, simplified surrogate model** for E-field scoring. It is **not a replacement** for high-fidelity FEM tools (e.g., SimNIBS/COMSOL) and **not intended for clinical use**. It is for learning, prototyping, and demonstrating optimization logic.

---

## Features
- Read **patient/config inputs from CSV** (head size, hair/skull thickness, target offsets, search grid, etc.)
- Simulate a **coarse E-field score** over a 2D scalp map around a target
- **Optimize coil placement** via grid search
- Visualize a **heatmap with head outline**, best position dot, **orientation arrow**, and **angle/distance** annotations
- Export **CSV of all positions** and **PNG figure**

---

## Quick Start

### 1) Environment
This project uses common scientific Python libs:
- `python >= 3.9`
- `numpy`
- `pandas`
- `matplotlib`

These are commonly preinstalled in most scientific stacks. If needed:
```bash
pip install -r requirements.txt
```

### 2) Inputs
Edit or provide your own CSV. A sample is in `data/sample_patient.csv`.

**Required columns** (units in millimeters unless noted):
- `head_radius_mm`: approximate head radius for top view (e.g., 90)
- `skull_thickness_mm`: average skull thickness (e.g., 7)
- `hair_thickness_mm`: average hair thickness/coil lift (e.g., 2)
- `target_name`: free text label (e.g., left_DLPFC)
- `target_offset_lateral_mm`: +right / –left from vertex (Cz)
- `target_offset_anterior_mm`: +anterior / –posterior from vertex (Cz)
- `search_radius_mm`: radius around target to scan coil center positions
- `grid_step_mm`: grid spacing for the scan (e.g., 5)
- `coil_height_mm` (optional): additional coil lift above scalp (defaults to hair_thickness + 2)
- `preferred_orientation_deg` (optional): nominal coil handle angle vs. midline (0° = anterior, +CW)

You may put multiple rows in one CSV; each row will trigger one optimization/plot.

### 3) Run
```bash
python run_optimizer.py --input data/sample_patient.csv --outdir outputs
```

Outputs:
- `*_heatmap.png`: scalp heatmap w/ best position & annotations
- `*_results.csv`: table of all tested positions with scores

### 4) Interpreting the Plot
- **Circle**: head outline (top view).
- **Heatmap**: E-field score at the *target* for each coil position.
- **Green dot**: recommended coil center.
- **Arrow**: recommended coil orientation.
- **Text box**: angle (deg) and distance from target (mm).

---

## Modeling Notes (Simplified Surrogate)
We approximate the induced E-field at a target as a score depending on:
- Distance from coil center to the target projection (stronger when closer, with softening via exponential decay and inverse-square)
- Orientation alignment (stronger when coil's induced current direction is aligned to a desired target tangential direction)
- Attenuation from **coil lift** (hair + coil height) and **skull thickness**

Mathematically (heuristic):

```
E_score = K * cos(alpha) * exp(-d / lambda) / (d + d0)^2 * A
```
where
- `alpha` is the angle between coil orientation and desired direction to target,
- `d` is the in-plane distance from coil to target (mm),
- `lambda`, `d0` are length-scale softeners,
- `A` is attenuation due to lift and skull thickness.

This is deliberately simple, transparent, and fast for didactic purposes.

---

## Disclaimer
This software is provided for educational purposes only, without any warranty. **Not for clinical decision-making.**

---

## Citation / Credit
If you use this in a class or demo, cite as: *"TMS E-field Optimizer (Educational), v1.0"*.
