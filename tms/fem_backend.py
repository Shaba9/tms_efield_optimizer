
import os
import json
import hashlib
import numpy as np
from pathlib import Path
import nibabel as nib

# Run inside SimNIBS Python environment
from simnibs import sim_struct, run_simnibs, mni2subject_coords


def _hash_pose(center_mni, ydir_mni, distance_mm, didt, coil_file):
    h = hashlib.md5()
    arr = np.array(list(center_mni)+list(ydir_mni)+[distance_mm, didt], dtype=float)
    h.update(arr.tobytes())
    h.update(str(coil_file).encode('utf-8'))
    return h.hexdigest()


def _find_e_field_nifti(output_dir: Path):
    cands = list(output_dir.rglob('*E_*nii*')) + list(output_dir.rglob('*E*norm*nii*')) + list(output_dir.rglob('*E*mag*nii*'))
    if not cands:
        cands = list(output_dir.rglob('*.nii*'))
    if not cands:
        raise FileNotFoundError(f'No NIfTI E-field volume found in {output_dir}')
    cands_sorted = sorted(cands, key=lambda p: (('E_' not in p.name), p.name))
    return cands_sorted[0]


def _sample_nifti_at_mm(nifti_path: Path, mm_coords):
    img = nib.load(str(nifti_path))
    aff = img.affine
    data = img.get_fdata()
    ijk = nib.affines.apply_affine(np.linalg.inv(aff), np.array(mm_coords))
    ijk_rounded = np.round(ijk).astype(int)
    i,j,k = ijk_rounded
    i = np.clip(i, 0, data.shape[0]-1)
    j = np.clip(j, 0, data.shape[1]-1)
    k = np.clip(k, 0, data.shape[2]-1)
    return float(data[i,j,k])


def fem_run_single_pose(
    m2m_dir: str,
    head_mesh_name: str,
    coil_file: str,
    center_mni: tuple,
    ydir_mni: tuple,
    distance_mm: float,
    didt_A_per_s: float,
    map_to_vol: bool,
    work_root: Path
):
    pose_hash = _hash_pose(center_mni, ydir_mni, distance_mm, didt_A_per_s, coil_file)
    outdir = work_root / f"TMS_{pose_hash}"
    done_file = outdir / 'done.json'
    if done_file.exists():
        epath = _find_e_field_nifti(outdir)
        with open(done_file, 'r') as f:
            meta = json.load(f)
        return epath, tuple(meta['subject_target_mm'])

    outdir.mkdir(parents=True, exist_ok=True)

    subj_center = mni2subject_coords(list(center_mni), m2m_dir)
    subj_ydir   = mni2subject_coords(list(ydir_mni),   m2m_dir)

    S = sim_struct.SESSION()
    S.subpath   = m2m_dir
    S.fnamehead = head_mesh_name
    S.pathfem   = str(outdir)
    S.fields    = 'eE'
    S.map_to_vol = bool(map_to_vol)
    S.tissues_in_niftis = 'all'

    tms = S.add_tmslist()
    tms.fnamecoil = coil_file

    pos = tms.add_position()
    pos.centre   = list(subj_center)
    pos.pos_ydir = list(subj_ydir)
    pos.distance = float(distance_mm)
    pos.didt     = float(didt_A_per_s)

    run_simnibs(S)

    epath = _find_e_field_nifti(outdir)
    with open(done_file, 'w') as f:
        json.dump({'subject_target_mm': list(subj_center)}, f)
    return epath, tuple(subj_center)


def sample_E_at_target(nifti_path: Path, subject_target_mm: tuple):
    return _sample_nifti_at_mm(nifti_path, subject_target_mm)
