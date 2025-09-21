# src/main.py

import networkx as nx
from src.qaoa_maxcut import QAOAMaxCut

def main():
    # Define a simple graph for demonstration
    # This graph has a clear max-cut solution
    graph = nx.Graph()
    graph.add_nodes_from([0, 1, 2, 3])
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    
    try:
        print("--- Running QAOA for Max-Cut ---")
        print(f"Graph nodes: {list(graph.nodes())}")
        print(f"Graph edges: {list(graph.edges())}")

        qaoa_solver = QAOAMaxCut(graph)
        results = qaoa_solver.solve(reps=2)

        print("\n--- Results ---")
        print(f"Optimal solution found: {results['solution_bitstring']}")
        print(f"Node partition sets: {results['solution_sets']}")
        print(f"Number of edges cut: {results['num_edges_cut']}")
        print("-----------------")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()