import argparse

from src.quantum_penny_flip import PICARD_MOVES, payoff_table, play


def main() -> None:
    parser = argparse.ArgumentParser(description="Meyer's quantum penny flip game.")
    parser.add_argument("--games", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    print("P(Q wins) for each pure Q strategy")
    print("Q moves   " + "   ".join(f"Picard {p}" for p in PICARD_MOVES))
    for (a, b), row in payoff_table().items():
        print(f"{a}, {b}      " + "       ".join(f"{row[p]:.2f}" for p in PICARD_MOVES))

    print(f"\n{args.games} games against a Picard who flips at random")
    print(f"classical Q wins    {play(args.games, 'classical', seed=args.seed):.1%}")
    print(f"quantum Q wins      {play(args.games, 'quantum', seed=args.seed):.1%}")


if __name__ == "__main__":
    main()
