import argparse

from qiskit.quantum_info import random_statevector

from src.bit_flip_code import logical_error_rate, run


def main() -> None:
    parser = argparse.ArgumentParser(description="Three-qubit bit-flip code demo.")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("-p", type=float, default=0.1, help="per-qubit flip probability")
    args = parser.parse_args()

    state = random_statevector(2, seed=args.seed)
    print("error on   syndrome   corrected   fidelity")
    for errors in [(), (0,), (1,), (2,), (0, 1)]:
        r = run(state, errors, seed=args.seed)
        label = ",".join(f"q{q}" for q in errors) or "none"
        fixed = "-" if r.corrected_qubit is None else f"q{r.corrected_qubit}"
        print(f"{label:<10} {r.syndrome:02b}         {fixed:<11} {r.fidelity:.4f}")

    p = args.p
    rate = logical_error_rate(p, seed=args.seed)
    print(f"\nflip probability p = {p}")
    print(f"logical error rate   {rate:.4f}  (theory {3 * p**2 - 2 * p**3:.4f}, bare qubit {p})")


if __name__ == "__main__":
    main()
