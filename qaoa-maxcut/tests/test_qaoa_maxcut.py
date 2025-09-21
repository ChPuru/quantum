# tests/test_qaoa_maxcut.py

import unittest
import networkx as nx
from src.qaoa_maxcut import QAOAMaxCut

class TestQAOAMaxCut(unittest.TestCase):

    def test_simple_graph_solution(self):
        """
        Tests QAOA on a simple 4-node graph where the max-cut is known to be 4.
        The optimal partitions are ({0, 1}, {2, 3}) or ({0, 3}, {1, 2}).
        """
        graph = nx.Graph()
        graph.add_nodes_from([0, 1, 2, 3])
        graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)]) # A square
        
        qaoa_solver = QAOAMaxCut(graph)
        results = qaoa_solver.solve(reps=2)

        # The maximum number of cuts for a square is 4
        self.assertEqual(results['num_edges_cut'], 4)

        # Check if the solution is one of the two valid partitions
        solution = results['solution_sets']
        valid_solutions = [([0, 2], [1, 3]), ([1, 3], [0, 2])]
        self.assertIn(sorted(map(sorted, solution)), valid_solutions)

if __name__ == '__main__':
    unittest.main()