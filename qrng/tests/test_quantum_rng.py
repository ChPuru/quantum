# tests/test_quantum_rng.py

import unittest
from src.quantum_rng import QuantumRNG

class TestQuantumRNG(unittest.TestCase):
    """
    Unit tests for the QuantumRNG class.
    """

    def setUp(self):
        """Set up a QuantumRNG instance for each test."""
        self.rng = QuantumRNG()

    def test_generate_bits_returns_string(self):
        """Test that generate_bits returns a string."""
        bits = self.rng.generate_bits(8)
        self.assertIsInstance(bits, str)

    def test_generate_bits_correct_length(self):
        """Test that the generated bit string has the correct length."""
        num_bits = 10
        bits = self.rng.generate_bits(num_bits)
        self.assertEqual(len(bits), num_bits)

    def test_generate_bits_contains_only_0_and_1(self):
        """Test that the generated bit string contains only '0' and '1'."""
        bits = self.rng.generate_bits(16)
        self.assertTrue(all(c in '01' for c in bits))

    def test_invalid_input(self):
        """Test that a non-positive integer for num_bits raises a ValueError."""
        with self.assertRaises(ValueError):
            self.rng.generate_bits(0)
        with self.assertRaises(ValueError):
            self.rng.generate_bits(-5)

if __name__ == '__main__':
    unittest.main()