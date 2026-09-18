import argparse

from src.shors import factor


def main() -> None:
    parser = argparse.ArgumentParser(description="Factor a small integer with Shor's algorithm.")
    parser.add_argument("number", type=int, nargs="?", default=15, help="odd composite, < 128")
    parser.add_argument("-a", type=int, help="fix the base a instead of picking it at random")
    parser.add_argument("--shots", type=int, default=16)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    try:
        result = factor(args.number, a=args.a, shots=args.shots, seed=args.seed)
    except (ValueError, RuntimeError) as err:
        parser.exit(1, f"error: {err}\n")

    p, q = result.factors
    print(f"{result.n} = {p} x {q}  (method: {result.method})")
    if result.method == "order finding":
        print(f"a = {result.a}, order r = {result.order}, attempts = {result.attempts}")


if __name__ == "__main__":
    main()
