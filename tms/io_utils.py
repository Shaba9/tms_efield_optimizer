
from pathlib import Path
import pandas as pd

def load_patient_rows_fem(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f'CSV not found: {csv_path}')
    df = pd.read_csv(csv_path)

    required = [
        'head_radius_mm','skull_thickness_mm','hair_thickness_mm',
        'target_name','target_mni_x','target_mni_y','target_mni_z',
        'search_radius_mm','grid_step_mm','coil_height_mm','preferred_orientation_deg',
        'm2m_subj_dir','head_mesh_name','coil_file','didt_A_per_s','map_to_vol'
    ]
    for col in required:
        if col not in df.columns:
            raise ValueError(f'Missing required column: {col}')

    rows = []
    for _, r in df.iterrows():
        rows.append({
            'head_radius_mm': float(r['head_radius_mm']),
            'skull_thickness_mm': float(r['skull_thickness_mm']),
            'hair_thickness_mm': float(r['hair_thickness_mm']),
            'target_name': str(r['target_name']),
            'target_mni': (float(r['target_mni_x']), float(r['target_mni_y']), float(r['target_mni_z'])),
            'search_radius_mm': float(r['search_radius_mm']),
            'grid_step_mm': float(r['grid_step_mm']),
            'coil_height_mm': float(r['coil_height_mm']),
            'preferred_orientation_deg': float(r['preferred_orientation_deg']),
            'm2m_dir': str(r['m2m_subj_dir']),
            'head_mesh_name': str(r['head_mesh_name']),
            'coil_file': str(r['coil_file']),
            'didt_A_per_s': float(r['didt_A_per_s']),
            'map_to_vol': bool(r['map_to_vol'])
        })
    return rows
