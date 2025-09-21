# tests/test_grover.py

import unittest
from src.grover import GroverSearch

class TestGroverSearch(unittest.TestCase):

    def test_init_valid(self):
        """Test successful initialization."""
        search = GroverSearch(num_qubits=3, marked_item="101")
        self.assertEqual(search.num_qubits, 3)
        self.assertEqual(search.marked_item, "101")

    def test_init_invalid(self):
        """Test that initialization fails with invalid marked_item."""
        with self.assertRaises(ValueError):
            GroverSearch(num_qubits=3, marked_item="10") # Wrong length
        with self.assertRaises(ValueError):
            GroverSearch(num_qubits=4, marked_item="101a") # Not binary

    def test_simulation_success_3_qubits(self):
        """Test that the simulation successfully finds the marked item for 3 qubits."""
        marked_item = "110"
        search = GroverSearch(num_qubits=3, marked_item=marked_item)
        search.build_circuit()
        results = search.run(shots=1024)
        self.assertEqual(results['most_frequent_result'], marked_item)

    def test_simulation_success_4_qubits(self):
        """Test that the simulation successfully finds the marked item for 4 qubits."""
        marked_item = "0110"
        search = GroverSearch(num_qubits=4, marked_item=marked_item)
        search.build_circuit()
        results = search.run(shots=2048) # More shots for larger space
        self.assertEqual(results['most_frequent_result'], marked_item)

if __name__ == '__main__':
    unittest.main()