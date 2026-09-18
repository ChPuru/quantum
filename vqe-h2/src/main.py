import argparse

import numpy as np

from src.vqe import dissociation_curve


def main() -> None:
    parser = argparse.ArgumentParser(description="VQE ground-state energy of H2 (STO-3G).")
    parser.add_argument("--start", type=float, default=0.3, help="shortest bond length, angstrom")
    parser.add_argument("--stop", type=float, default=2.5, help="longest bond length, angstrom")
    parser.add_argument("--points", type=int, default=12)
    args = parser.parse_args()

    results = dissociation_curve(list(np.linspace(args.start, args.stop, args.points)))

    print(" R (A)    HF (Ha)      VQE (Ha)     exact (Ha)   VQE error")
    for r in results:
        print(
            f"{r.bond_length:5.2f}  {r.hf_energy:11.6f}  {r.energy:11.6f}  "
            f"{r.fci_energy:11.6f}  {abs(r.energy - r.fci_energy):.1e}"
        )
    best = min(results, key=lambda r: r.energy)
    print(f"\nlowest VQE energy {best.energy:.6f} Ha at R = {best.bond_length:.2f} A")


if __name__ == "__main__":
    main()
