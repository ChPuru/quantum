# tests/test_annealer.py

import unittest
import networkx as nx
from src.annealer import QuantumAnnealer

class TestQuantumAnnealer(unittest.TestCase):

    def test_square_graph_solution(self):
        """
        Tests the annealer on a simple square graph where the max-cut is known to be 4.
        """
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2, 3])
        graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
        
        annealer = QuantumAnnealer(graph)
        solution_str = annealer.anneal(total_time=10, time_steps=200)
        cut_count, _ = annealer.get_max_cut_solution(solution_str)

        self.assertEqual(cut_count, 4)
        # Valid solutions are '0101' or '1010'
        self.assertIn(solution_str, ['0101', '1010'])

if __name__ == '__main__':
    unittest.main()