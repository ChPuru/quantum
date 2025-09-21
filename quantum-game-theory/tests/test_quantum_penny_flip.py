# tests/test_quantum_penny_flip.py

import unittest
from src.quantum_penny_flip import QuantumPennyFlip

class TestQuantumPennyFlip(unittest.TestCase):

    def setUp(self):
        self.game = QuantumPennyFlip()

    def test_classical_scenario(self):
        """
        Test the classical vs. classical scenario.
        Q should win approximately 50% of the time.
        """
        win_rate = self.game.simulate_games(
            num_games=200,
            q_strategy='identity',
            picard_strategy='random'
        )
        # We expect the win rate to be close to 0.5
        self.assertAlmostEqual(win_rate, 0.5, delta=0.1)

    def test_quantum_scenario(self):
        """
        Test the quantum vs. classical scenario.
        Q should win 100% of the time.
        """
        win_rate = self.game.simulate_games(
            num_games=200,
            q_strategy='hadamard',
            picard_strategy='random'
        )
        # We expect the win rate to be exactly 1.0
        self.assertEqual(win_rate, 1.0)

if __name__ == '__main__':
    unittest.main()