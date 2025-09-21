# tests/test_bit_flip_code.py

import unittest
from qiskit.quantum_info import Statevector
from src.bit_flip_code import BitFlipCode

class TestBitFlipCode(unittest.TestCase):

    def test_correction_from_plus_state(self):
        """
        Tests the full protocol by starting with the |+> state, applying a known
        error, and verifying the final state is recovered.
        """
        initial_state = Statevector.from_label('+')
        
        for error_loc in range(3):
            with self.subTest(error_location=error_loc):
                qec_sim = BitFlipCode(initial_state=initial_state)
                
                # Manually run the steps to control the error location
                qec_sim._encode()
                qec_sim.introduce_error(error_loc)
                qec_sim._detect_and_correct()
                
                # Uncompute encoding
                qec_sim.circuit.cx(0, 2)
                qec_sim.circuit.cx(0, 1)
                
                # Verify
                final_state_circuit = qec_sim.circuit.copy()
                final_state_circuit.save_statevector()
                backend = qec_sim.backend
                result = backend.run(final_state_circuit).result()
                final_full_vector = result.get_statevector()
                final_logical_vector_data = [final_full_vector.data[0], final_full_vector.data[1]]
                final_logical_state = Statevector(final_logical_vector_data)

                self.assertTrue(initial_state.equiv(final_logical_state))

if __name__ == '__main__':
    unittest.main()