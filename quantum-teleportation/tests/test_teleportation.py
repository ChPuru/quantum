# tests/test_teleportation.py

import unittest
from qiskit.quantum_info import Statevector
from src.teleportation import Teleportation

class TestTeleportation(unittest.TestCase):

    def test_protocol_correctness(self):
        """
        Tests the full teleportation protocol by sending a known state
        and verifying the output state.
        """
        # Create a known, non-trivial initial state for the message qubit
        # This state is |+>
        initial_state = Statevector.from_label('+')

        # Initialize the circuit with this state
        teleporter = Teleportation()
        teleporter.circuit.initialize(initial_state, 0)
        teleporter.circuit.barrier()

        # Build the protocol circuit
        teleporter.build_circuit()

        # Run the verification
        results = teleporter.run_and_verify(initial_state)

        # Assert that the protocol was successful
        self.assertTrue(results['success'], "The final state should match the initial state.")
        
        # Optional: Check if the final state is indeed close to |+>
        # final_state_vec = Statevector(results['final_state'])
        # self.assertTrue(final_state_vec.equiv(initial_state))

if __name__ == '__main__':
    unittest.main()