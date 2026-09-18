import argparse

from src.grover import grover_circuit, search


def main() -> None:
    parser = argparse.ArgumentParser(description="Grover search for one or more bitstrings.")
    parser.add_argument("marked", nargs="+", help="bitstrings to find, e.g. 101 or 0110 1001")
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--iterations", type=int, help="override the optimal iteration count")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--draw", action="store_true", help="print the circuit")
    args = parser.parse_args()

    try:
        result = search(args.marked, shots=args.shots, iterations=args.iterations, seed=args.seed)
    except ValueError as err:
        parser.exit(1, f"error: {err}\n")

    print(f"iterations          {result.iterations}")
    print(f"most frequent       {result.most_frequent}")
    print(f"hit rate            {result.success_rate:.1%}")
    print(f"theoretical         {result.expected_success:.1%}")

    if args.draw:
        print(grover_circuit(args.marked, result.iterations).draw(output="text"))


if __name__ == "__main__":
    main()
