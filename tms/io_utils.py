
from pathlib import Path
import pandas as pd


def load_patient_rows(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f'CSV not found: {csv_path}')
    df = pd.read_csv(csv_path)

    required = [
        'head_radius_mm', 'skull_thickness_mm', 'hair_thickness_mm',
        'target_name', 'target_offset_lateral_mm', 'target_offset_anterior_mm',
        'search_radius_mm', 'grid_step_mm'
    ]
    for col in required:
        if col not in df.columns:
            raise ValueError(f'Missing required column: {col}')

    # Fill optionals
    if 'coil_height_mm' not in df.columns:
        df['coil_height_mm'] = df['hair_thickness_mm'] + 2.0
    if 'preferred_orientation_deg' not in df.columns:
        df['preferred_orientation_deg'] = 45.0

    # Materialize rows as dicts
    rows = []
    for _, r in df.iterrows():
        rows.append({
            'head_radius_mm': float(r['head_radius_mm']),
            'skull_thickness_mm': float(r['skull_thickness_mm']),
            'hair_thickness_mm': float(r['hair_thickness_mm']),
            'coil_height_mm': float(r.get('coil_height_mm', r['hair_thickness_mm'] + 2.0)),
            'target_name': str(r['target_name']),
            'target_offset_lateral_mm': float(r['target_offset_lateral_mm']),
            'target_offset_anterior_mm': float(r['target_offset_anterior_mm']),
            'search_radius_mm': float(r['search_radius_mm']),
            'grid_step_mm': float(r['grid_step_mm']),
            'preferred_orientation_deg': float(r.get('preferred_orientation_deg', 45.0))
        })
    return rows
