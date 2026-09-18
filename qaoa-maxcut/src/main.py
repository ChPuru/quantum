import argparse

import networkx as nx

from src.qaoa_maxcut import brute_force_maxcut, solve


def main() -> None:
    parser = argparse.ArgumentParser(description="MaxCut with QAOA on a small example graph.")
    parser.add_argument("--reps", type=int, default=2, help="QAOA layers p")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    # A 4-cycle with one diagonal. The best cut is 4.
    graph = nx.Graph([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    result = solve(graph, reps=args.reps, seed=args.seed)

    left, right = result.partition
    print(f"edges               {sorted(graph.edges)}")
    print(f"partition           {sorted(left)} | {sorted(right)}")
    print(f"cut value           {result.cut_value:g} (brute force: {brute_force_maxcut(graph):g})")
    print(f"expected cut <C>    {result.expected_cut:.3f}")
    print(f"P(best cut)         {result.best_probability:.1%}")


if __name__ == "__main__":
    main()
