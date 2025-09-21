# src/bit_flip_code.py

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import random_statevector, Statevector
from qiskit_aer import AerSimulator

class BitFlipCode:
    """
    Encapsulates the logic for the 3-qubit bit-flip error correction code.
    """

    def __init__(self, initial_state: Statevector):
        if not isinstance(initial_state, Statevector) or initial_state.dim != 2:
            raise TypeError("Initial state must be a single-qubit Statevector.")
        
        self.initial_state = initial_state
        self.q = QuantumRegister(5, name='q')
        self.syn = ClassicalRegister(2, name='syndrome')
        self.circuit = QuantumCircuit(self.q, self.syn)
        self.circuit.initialize(self.initial_state, 0)
        self.circuit.barrier()

    def _encode(self):
        """Encodes the logical qubit (q0) onto two ancilla qubits (q1, q2)."""
        self.circuit.cx(0, 1)
        self.circuit.cx(0, 2)
        self.circuit.barrier()

    def introduce_error(self, error_qubit_index: int):
        """Applies a single X-gate (bit-flip) error to one of the encoded qubits."""
        if not 0 <= error_qubit_index <= 2:
            raise ValueError("Error can only be applied to the first 3 qubits (0, 1, or 2).")
        
        print(f"INFO: Introducing a bit-flip error on qubit {error_qubit_index}.")
        self.circuit.x(error_qubit_index)
        self.circuit.barrier()

    def _detect_and_correct(self):
        """Builds the syndrome measurement and correction circuit."""
        # Syndrome measurement
        self.circuit.cx(0, 3)
        self.circuit.cx(1, 3)
        self.circuit.cx(1, 4)
        self.circuit.cx(2, 4)
        self.circuit.measure(self.q[3], self.syn[0])
        self.circuit.measure(self.q[4], self.syn[1])
        self.circuit.barrier()

        # Corrected logic from previous step
        with self.circuit.if_test((self.syn, 1)): # Syndrome '01' -> Error on q0
            self.circuit.x(0)
        with self.circuit.if_test((self.syn, 2)): # Syndrome '10' -> Error on q2
            self.circuit.x(2)
        with self.circuit.if_test((self.syn, 3)): # Syndrome '11' -> Error on q1
            self.circuit.x(1)

    def run_and_verify(self):
        """
        Runs the full simulation and verifies if the encoded state was recovered.
        """
        # 1. Encode the state
        self._encode()
        
        # 2. Save the "correct" encoded state for later comparison
        self.circuit.save_statevector(label="correct_encoded_state")
        
        # 3. Introduce a random error
        error_location = np.random.randint(0, 3)
        self.introduce_error(error_location)
        
        # 4. Run the detection and correction protocol
        self._detect_and_correct()
        
        # 5. Save the final "corrected" state
        self.circuit.save_statevector(label="corrected_state")
        
        # Run simulation
        backend = AerSimulator()
        result = backend.run(self.circuit).result()
        
        # 6. Compare the two statevectors
        correct_state = result.data()['correct_encoded_state']
        corrected_state = result.data()['corrected_state']
        
        success = correct_state.equiv(corrected_state)

        return {
            "success": success,
            "initial_state": self.initial_state.data,
            "error_location": error_location
        }