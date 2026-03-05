
import argparse
from pathlib import Path
from tms.io_utils import load_patient_rows
from tms.optimizer import optimize_for_row


def main():
    parser = argparse.ArgumentParser(description='TMS E-field optimizer (educational).')
    parser.add_argument('--input', required=True, help='Path to patient CSV.')
    parser.add_argument('--outdir', default='outputs', help='Directory to save outputs.')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (reserved).')
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = load_patient_rows(args.input)

    for idx, row in enumerate(rows):
        optimize_for_row(row, outdir)


if __name__ == '__main__':
    main()
