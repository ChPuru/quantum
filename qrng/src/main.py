import argparse

from src.quantum_rng import coin_circuit, random_bits, random_int


def main() -> None:
    parser = argparse.ArgumentParser(description="Random bits from a simulated qubit.")
    parser.add_argument("--bits", type=int, default=16)
    parser.add_argument("--dice", action="store_true", help="also roll a six-sided die")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    print(coin_circuit().draw(output="text"))
    print(f"bits    {random_bits(args.bits, seed=args.seed)}")
    if args.dice:
        print(f"die     {random_int(1, 6, seed=args.seed)}")


if __name__ == "__main__":
    main()
