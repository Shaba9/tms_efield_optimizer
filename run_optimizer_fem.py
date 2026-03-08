
import argparse
from pathlib import Path
from tms.io_utils import load_patient_rows_fem
from tms.optimizer_fem import optimize_for_row_fem

def main():
    p = argparse.ArgumentParser(description='TMS FEM optimizer (SimNIBS backend)')
    p.add_argument('--input', required=True, help='Path to patient CSV.')
    p.add_argument('--outdir', default='outputs', help='Directory to save outputs.')
    p.add_argument('--backend', default='simnibs', choices=['simnibs'], help='FEM backend (SimNIBS only).')
    p.add_argument('--seed', type=int, default=42)
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = load_patient_rows_fem(args.input)
    for row in rows:
        optimize_for_row_fem(row, outdir)

if __name__ == '__main__':
    main()
