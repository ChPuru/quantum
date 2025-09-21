# src/main.py

import networkx as nx
from src.annealer import QuantumAnnealer

def main():
    # Define a simple graph for demonstration
    graph = nx.Graph()
    graph.add_nodes_from([0, 1, 2, 3])
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    
    try:
        print("--- Quantum Annealing Simulator for Max-Cut ---")
        print(f"Graph nodes: {list(graph.nodes())}")
        print(f"Graph edges: {list(graph.edges())}")

        annealer = QuantumAnnealer(graph)
        solution_str = annealer.anneal(total_time=10, time_steps=200)
        cut_count, partition = annealer.get_max_cut_solution(solution_str)

        print("\n--- Results ---")
        print(f"Optimal solution found (spin config): {solution_str}")
        print(f"Node partition sets: {partition}")
        print(f"Number of edges cut: {cut_count}")
        print("-----------------")

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()