# src/quantum_penny_flip.py

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

class QuantumPennyFlip:
    """
    Encapsulates the logic for the Quantum Penny Flip game.
    """

    def __init__(self):
        self.circuit = None
        self.backend = AerSimulator()

    def run_game(self, q_strategy: str, picard_strategy: str):
        """
        Runs a single round of the Penny Flip game.

        Args:
            q_strategy (str): Q's strategy ('identity' or 'hadamard').
            picard_strategy (str): Picard's strategy ('identity' or 'flip').

        Returns:
            int: The result of the game (0 for Heads/Picard wins, 1 for Tails/Q wins).
        """
        self.circuit = QuantumCircuit(1, 1)

        # Q's First Move
        if q_strategy.lower() == 'hadamard':
            self.circuit.h(0)
        # If classical, Q does nothing (identity).

        # Picard's Move
        if picard_strategy.lower() == 'flip':
            self.circuit.x(0)
        # If identity, Picard does nothing.

        # Q's Second Move (This is the corrected logic)
        if q_strategy.lower() == 'hadamard':
            # The winning strategy is to apply H and then X.
            self.circuit.h(0)
            self.circuit.x(0)
        # If classical, Q does nothing.

        # Measurement
        self.circuit.measure(0, 0)

        result = self.backend.run(self.circuit, shots=1, memory=True).result()
        measurement = int(result.get_memory()[0])
        
        return measurement

    def simulate_games(self, num_games: int, q_strategy: str, picard_strategy: str):
        """
        Simulates many games to find the win probability for Q.
        """
        q_wins = 0
        for i in range(num_games):
            # Picard randomly chooses to flip or not
            picard_random_move = 'flip' if i % 2 == 0 else 'identity'
            result = self.run_game(q_strategy, picard_random_move)
            if result == 1:
                q_wins += 1
        
        return q_wins / num_games