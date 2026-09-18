import argparse

import networkx as nx

from src.annealer import anneal


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulated quantum annealing for MaxCut.")
    parser.add_argument("--time", type=float, default=10.0, help="total anneal time")
    parser.add_argument("--steps", type=int, default=200)
    args = parser.parse_args()

    # A 5-cycle with two chords. The best cut is 6.
    graph = nx.Graph([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 4)])
    result = anneal(graph, total_time=args.time, steps=args.steps)

    sides = result.best_assignment
    left = sorted(n for n, s in sides.items() if s == 0)
    right = sorted(n for n, s in sides.items() if s == 1)
    print(f"most likely cut     {left} | {right}")
    print(f"cut value           {result.best_cut:g} (maximum {result.max_cut:g})")
    print(f"P(maximum cut)      {result.success_probability:.1%}")

    print("\nanneal time vs P(maximum cut)")
    for t in (0.5, 2, 5, 10, 20):
        print(f"  T = {t:<4} {anneal(graph, total_time=t).success_probability:.1%}")


if __name__ == "__main__":
    main()
